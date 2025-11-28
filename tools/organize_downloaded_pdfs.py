#!/usr/bin/env python3
"""
Organize Downloaded PDFs from Santa Ana
Takes PDFs downloaded manually from browser and organizes them into proper structure

Usage:
    # Organize files from Downloads folder
    python3 organize_downloaded_pdfs.py --source ~/Downloads --output "/Volumes/Samsung USB/City_extraction/Santa_Ana"

    # Dry run first
    python3 organize_downloaded_pdfs.py --source ~/Downloads --output "/Volumes/Samsung USB/City_extraction/Santa_Ana" --dry-run
"""

import argparse
import re
import shutil
from datetime import datetime
from pathlib import Path


class PDFOrganizer:
    """Organize downloaded Santa Ana meeting PDFs"""

    # Meeting type patterns
    MEETING_PATTERNS = {
        'regular_city_council': r'regular.*city.*council(?!.*housing)',
        'regular_housing': r'regular.*city.*council.*housing',
        'special_city_council': r'special.*city.*council',
    }

    # Document type patterns
    DOC_PATTERNS = {
        'agenda': r'agenda',
        'minutes': r'minutes'
    }

    def __init__(self, source_dir, output_dir, dry_run=False):
        """
        Initialize organizer

        Args:
            source_dir: Directory with downloaded PDFs
            output_dir: Base directory for organized files
            dry_run: If True, show what would be done without doing it
        """
        self.source_dir = Path(source_dir).expanduser()
        self.output_dir = Path(output_dir)
        self.dry_run = dry_run

        self.stats = {
            'found': 0,
            'organized': 0,
            'skipped': 0,
            'errors': 0
        }

    def extract_date_from_filename(self, filename):
        """
        Extract date from filename

        Tries multiple patterns:
        - YYYYMMDD
        - YYYY-MM-DD
        - MM/DD/YYYY
        - Meeting ID with timestamp (MeetingsXXXXMinutes_YYYYMMDDHHMMSS)

        Returns:
            datetime object or None
        """
        # Pattern 1: YYYYMMDD
        match = re.search(r'(\d{4})(\d{2})(\d{2})', filename)
        if match:
            year, month, day = match.groups()
            try:
                return datetime(int(year), int(month), int(day))
            except ValueError:
                pass

        # Pattern 2: YYYY-MM-DD
        match = re.search(r'(\d{4})-(\d{2})-(\d{2})', filename)
        if match:
            year, month, day = match.groups()
            try:
                return datetime(int(year), int(month), int(day))
            except ValueError:
                pass

        # Pattern 3: Meetings4660Minutes_20250624175240859
        match = re.search(r'Meetings\d+(?:Agenda|Minutes)_(\d{4})(\d{2})(\d{2})', filename)
        if match:
            year, month, day = match.groups()
            try:
                return datetime(int(year), int(month), int(day))
            except ValueError:
                pass

        return None

    def classify_document(self, filename):
        """
        Classify document type and meeting type

        Returns:
            tuple: (doc_type, meeting_type) or (None, None)
        """
        filename_lower = filename.lower()

        # Determine document type
        doc_type = None
        for dtype, pattern in self.DOC_PATTERNS.items():
            if re.search(pattern, filename_lower):
                doc_type = dtype
                break

        # Determine meeting type
        meeting_type = None
        for mtype, pattern in self.MEETING_PATTERNS.items():
            if re.search(pattern, filename_lower):
                meeting_type = mtype
                break

        return doc_type, meeting_type

    def generate_clean_filename(self, pdf_file, date_obj, doc_type, meeting_type):
        """
        Generate clean filename in format: YYYYMMDD_type_meeting-name.pdf

        Args:
            pdf_file: Original PDF file path
            date_obj: datetime object
            doc_type: 'agenda' or 'minutes'
            meeting_type: meeting type key

        Returns:
            str: New filename
        """
        # Date prefix
        date_prefix = date_obj.strftime('%Y%m%d')

        # Meeting name
        meeting_names = {
            'regular_city_council': 'regular_city_council_meeting',
            'regular_housing': 'regular_city_council_and_special_housing_authority',
            'special_city_council': 'special_city_council_meeting'
        }
        meeting_name = meeting_names.get(meeting_type, 'city_council_meeting')

        # Format: YYYYMMDD_type_meeting-name.pdf
        filename = f"{date_prefix}_{doc_type}_{meeting_name}.pdf"

        return filename

    def process_file(self, pdf_file):
        """
        Process a single PDF file

        Args:
            pdf_file: Path to PDF file

        Returns:
            dict: Processing result
        """
        result = {
            'original_file': str(pdf_file),
            'status': 'unknown',
            'message': ''
        }

        try:
            # Extract date
            date_obj = self.extract_date_from_filename(pdf_file.name)
            if not date_obj:
                result['status'] = 'skipped'
                result['message'] = 'Could not extract date from filename'
                return result

            year = date_obj.year

            # Classify document
            doc_type, meeting_type = self.classify_document(pdf_file.name)

            if not doc_type:
                result['status'] = 'skipped'
                result['message'] = 'Could not determine document type (agenda/minutes)'
                return result

            if not meeting_type:
                result['status'] = 'skipped'
                result['message'] = 'Could not determine meeting type'
                return result

            # Generate new filename
            new_filename = self.generate_clean_filename(pdf_file, date_obj, doc_type, meeting_type)

            # Determine target path
            target_path = self.output_dir / str(year) / "PDFs" / doc_type / new_filename

            # Check if already exists
            if target_path.exists():
                result['status'] = 'skipped'
                result['message'] = 'File already exists at destination'
                result['target_path'] = str(target_path)
                return result

            # Copy or show what would be done
            if self.dry_run:
                result['status'] = 'dry_run'
                result['message'] = f'Would copy to: {target_path}'
                result['target_path'] = str(target_path)
            else:
                # Create target directory
                target_path.parent.mkdir(parents=True, exist_ok=True)

                # Copy file
                shutil.copy2(pdf_file, target_path)

                result['status'] = 'success'
                result['message'] = f'Organized to: {target_path}'
                result['target_path'] = str(target_path)

        except Exception as e:
            result['status'] = 'error'
            result['message'] = str(e)

        return result

    def organize_all(self):
        """Organize all PDFs in source directory"""
        print(f"\n📁 PDF Organizer")
        print(f"{'='*60}")
        print(f"Source directory: {self.source_dir}")
        print(f"Output directory: {self.output_dir}")
        print(f"Dry run: {self.dry_run}\n")

        # Find all PDFs
        pdf_files = list(self.source_dir.glob("*.pdf"))
        self.stats['found'] = len(pdf_files)

        if not pdf_files:
            print(f"⚠️  No PDF files found in {self.source_dir}")
            return

        print(f"✅ Found {len(pdf_files)} PDF files\n")

        # Process each file
        for i, pdf_file in enumerate(pdf_files, 1):
            print(f"[{i}/{len(pdf_files)}] {pdf_file.name}")

            result = self.process_file(pdf_file)

            if result['status'] == 'success':
                print(f"   ✅ {result['message']}")
                self.stats['organized'] += 1
            elif result['status'] == 'dry_run':
                print(f"   📋 {result['message']}")
                self.stats['organized'] += 1
            elif result['status'] == 'skipped':
                print(f"   ⏭️  {result['message']}")
                self.stats['skipped'] += 1
            elif result['status'] == 'error':
                print(f"   ❌ Error: {result['message']}")
                self.stats['errors'] += 1

            print()

        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print organization statistics"""
        print(f"{'='*60}")
        print(f"📊 Organization Summary")
        print(f"{'='*60}")
        print(f"PDFs found: {self.stats['found']}")
        print(f"Organized: {self.stats['organized']}")
        print(f"Skipped: {self.stats['skipped']}")
        print(f"Errors: {self.stats['errors']}")
        print(f"\n✅ Complete!\n")


def main():
    """Command-line interface"""
    parser = argparse.ArgumentParser(
        description='Organize downloaded Santa Ana meeting PDFs'
    )

    parser.add_argument(
        '--source',
        required=True,
        help='Source directory with downloaded PDFs (e.g., ~/Downloads)'
    )

    parser.add_argument(
        '--output',
        default='/Volumes/Samsung USB/City_extraction/Santa_Ana',
        help='Base directory for organized files'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without actually doing it'
    )

    args = parser.parse_args()

    # Verify source exists
    source_path = Path(args.source).expanduser()
    if not source_path.exists():
        print(f"❌ Error: Source directory not found: {source_path}")
        return

    # Create organizer and run
    organizer = PDFOrganizer(
        source_dir=args.source,
        output_dir=args.output,
        dry_run=args.dry_run
    )

    organizer.organize_all()


if __name__ == '__main__':
    main()
