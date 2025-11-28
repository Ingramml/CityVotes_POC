#!/usr/bin/env python3
"""
Rename Santa Ana PDF files to reflect their actual meeting dates and types

This script:
1. Extracts meeting date and type from PDF content
2. Renames files to format: YYYYMMDD_Meeting_Type_Document_Type.pdf
   Example: 20240116_City_Council_Special_Housing_Authority_Meeting_Agenda.pdf

Usage:
    python3 rename_santa_ana_pdfs.py --directory "/Volumes/Samsung USB/City_extraction/Santa_Ana"
    python3 rename_santa_ana_pdfs.py --directory "/Volumes/Samsung USB/City_extraction/Santa_Ana" --dry-run
"""

import argparse
import re
from datetime import datetime
from pathlib import Path
import PyPDF2


class SantaAnaPDFRenamer:
    """Rename Santa Ana PDFs based on their actual content"""

    # Common meeting type patterns to look for
    MEETING_TYPE_PATTERNS = [
        (r'regular\s+city\s+council\s+(?:and\s+)?special\s+housing\s+authority\s+(?:and\s+)?(?:special\s+)?successor\s+agency\s+meeting',
         'City_Council_Special_Housing_Authority_and_Special_Successor_Agency_Meeting'),
        (r'regular\s+city\s+council\s+(?:and\s+)?special\s+housing\s+authority\s+meeting',
         'City_Council_and_Special_Housing_Authority_Meeting'),
        (r'special\s+city\s+council\s+meeting',
         'Special_City_Council_Meeting'),
        (r'regular\s+city\s+council\s+meeting',
         'Regular_City_Council_Meeting'),
        (r'city\s+council\s+meeting',
         'City_Council_Meeting'),
    ]

    # Date patterns to look for in PDF text
    DATE_PATTERNS = [
        r'(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},?\s+\d{4}',
        r'\d{1,2}/\d{1,2}/\d{4}',
        r'\d{4}-\d{2}-\d{2}',
    ]

    def __init__(self, directory, dry_run=False, verbose=False):
        """
        Initialize renamer

        Args:
            directory: Directory containing PDFs to rename
            dry_run: If True, show what would be renamed without actually renaming
            verbose: If True, print detailed information
        """
        self.directory = Path(directory)
        self.dry_run = dry_run
        self.verbose = verbose

        self.stats = {
            'total_files': 0,
            'renamed': 0,
            'skipped': 0,
            'errors': 0,
        }

    def extract_text_from_pdf(self, pdf_path, max_pages=3):
        """
        Extract text from first few pages of PDF

        Args:
            pdf_path: Path to PDF file
            max_pages: Maximum number of pages to extract (default: 3)

        Returns:
            str: Extracted text
        """
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ''

                # Extract text from first few pages
                for page_num in range(min(max_pages, len(reader.pages))):
                    page = reader.pages[page_num]
                    text += page.extract_text() + '\n'

                return text

        except Exception as e:
            if self.verbose:
                print(f"    ⚠️  Error extracting text: {e}")
            return ''

    def extract_meeting_date(self, text):
        """
        Extract meeting date from PDF text

        Args:
            text: PDF text content

        Returns:
            str: Date in YYYYMMDD format, or None if not found
        """
        text_lower = text.lower()

        # Try different date patterns
        for pattern in self.DATE_PATTERNS:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)

            for match in matches:
                date_str = match.group(0)

                # Try to parse the date
                date_obj = None

                # Try different date formats
                for fmt in ['%B %d, %Y', '%B %d %Y', '%m/%d/%Y', '%Y-%m-%d']:
                    try:
                        date_obj = datetime.strptime(date_str, fmt)
                        break
                    except ValueError:
                        continue

                if date_obj:
                    return date_obj.strftime('%Y%m%d')

        return None

    def extract_meeting_type(self, text):
        """
        Extract meeting type from PDF text

        Args:
            text: PDF text content

        Returns:
            str: Meeting type slug, or None if not found
        """
        text_lower = text.lower()

        # Try to match meeting type patterns
        for pattern, slug in self.MEETING_TYPE_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return slug

        return None

    def extract_document_type(self, text, filename):
        """
        Extract document type (agenda or minutes)

        Args:
            text: PDF text content
            filename: Original filename

        Returns:
            str: 'Agenda' or 'Minutes'
        """
        text_lower = text.lower()
        filename_lower = filename.lower()

        # Check filename first
        if 'minute' in filename_lower:
            return 'Minutes'
        elif 'agenda' in filename_lower:
            return 'Agenda'

        # Check PDF content
        # Look at first 500 characters for document type
        first_text = text_lower[:500]

        if 'minutes' in first_text:
            return 'Minutes'
        elif 'agenda' in first_text:
            return 'Agenda'

        # Default to Agenda if unclear
        return 'Agenda'

    def generate_new_filename(self, pdf_path):
        """
        Generate new filename based on PDF content

        Args:
            pdf_path: Path to PDF file

        Returns:
            tuple: (new_filename, metadata_dict) or (None, None) if unable to generate
        """
        try:
            # Extract text from PDF
            text = self.extract_text_from_pdf(pdf_path)

            if not text:
                if self.verbose:
                    print(f"    ⚠️  No text extracted from PDF")
                return None, None

            # Extract metadata
            meeting_date = self.extract_meeting_date(text)
            meeting_type = self.extract_meeting_type(text)
            doc_type = self.extract_document_type(text, pdf_path.name)

            if not meeting_date:
                if self.verbose:
                    print(f"    ⚠️  Could not extract meeting date")
                return None, None

            if not meeting_type:
                if self.verbose:
                    print(f"    ⚠️  Could not extract meeting type")
                return None, None

            # Generate new filename
            new_filename = f"{meeting_date}_{meeting_type}_{doc_type}.pdf"

            metadata = {
                'date': meeting_date,
                'meeting_type': meeting_type,
                'doc_type': doc_type,
            }

            return new_filename, metadata

        except Exception as e:
            if self.verbose:
                print(f"    ❌ Error generating filename: {e}")
            return None, None

    def rename_file(self, old_path, new_filename):
        """
        Rename a file

        Args:
            old_path: Current file path
            new_filename: New filename

        Returns:
            bool: Success status
        """
        try:
            new_path = old_path.parent / new_filename

            # Check if target already exists
            if new_path.exists() and new_path != old_path:
                print(f"    ⚠️  Target file already exists: {new_filename}")
                self.stats['skipped'] += 1
                return False

            if self.dry_run:
                print(f"    [DRY RUN] Would rename to: {new_filename}")
                self.stats['renamed'] += 1
                return True

            # Rename file
            old_path.rename(new_path)
            print(f"    ✅ Renamed to: {new_filename}")
            self.stats['renamed'] += 1
            return True

        except Exception as e:
            print(f"    ❌ Error renaming file: {e}")
            self.stats['errors'] += 1
            return False

    def process_directory(self):
        """Process all PDFs in directory"""
        print(f"\n📄 Santa Ana PDF Renamer")
        print(f"{'='*60}")
        print(f"Directory: {self.directory}")
        print(f"Dry run: {self.dry_run}")
        print(f"Verbose: {self.verbose}\n")

        # Find all PDF files
        pdf_files = list(self.directory.glob("*.pdf"))

        # Filter out metadata files (._*)
        pdf_files = [f for f in pdf_files if not f.name.startswith('._')]

        self.stats['total_files'] = len(pdf_files)

        print(f"Found {len(pdf_files)} PDF files\n")

        # Process each file
        for i, pdf_path in enumerate(pdf_files, 1):
            print(f"[{i}/{len(pdf_files)}] {pdf_path.name}")

            # Check if already in correct format
            if re.match(r'\d{8}_.*_(Agenda|Minutes)\.pdf', pdf_path.name):
                print(f"    ⏭️  Already in correct format")
                self.stats['skipped'] += 1
                continue

            # Generate new filename
            new_filename, metadata = self.generate_new_filename(pdf_path)

            if not new_filename:
                print(f"    ⚠️  Could not generate new filename")
                self.stats['errors'] += 1
                continue

            if self.verbose:
                print(f"    📅 Date: {metadata['date']}")
                print(f"    🏛️  Type: {metadata['meeting_type']}")
                print(f"    📄 Doc: {metadata['doc_type']}")

            # Rename file
            self.rename_file(pdf_path, new_filename)

        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print processing statistics"""
        print(f"\n{'='*60}")
        print(f"📊 Processing Summary")
        print(f"{'='*60}")
        print(f"Total files: {self.stats['total_files']}")
        print(f"Renamed: {self.stats['renamed']}")
        print(f"Skipped: {self.stats['skipped']}")
        print(f"Errors: {self.stats['errors']}")
        print(f"\n✅ Complete!\n")


def main():
    """Command-line interface"""
    parser = argparse.ArgumentParser(
        description='Rename Santa Ana PDFs based on their actual content'
    )

    parser.add_argument(
        '--directory',
        required=True,
        help='Directory containing PDFs to rename'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be renamed without actually renaming'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Print detailed information'
    )

    args = parser.parse_args()

    # Check if directory exists
    directory = Path(args.directory)
    if not directory.exists():
        print(f"❌ Directory does not exist: {directory}")
        return

    if not directory.is_dir():
        print(f"❌ Not a directory: {directory}")
        return

    # Create renamer and run
    renamer = SantaAnaPDFRenamer(
        directory=args.directory,
        dry_run=args.dry_run,
        verbose=args.verbose
    )

    renamer.process_directory()


if __name__ == '__main__':
    main()
