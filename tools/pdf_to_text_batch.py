#!/usr/bin/env python3
"""
PDF to Text Batch Converter
Extracts text from PDFs and organizes in parallel directory structure
"""

import subprocess
import shutil
from pathlib import Path
from datetime import datetime
import json

class PDFToTextConverter:
    def __init__(self, base_path, log_path=None):
        """
        Initialize converter

        Args:
            base_path: Root directory with YYYY/PDFs/ structure
            log_path: Optional path for conversion log
        """
        self.base_path = Path(base_path)
        self.log_path = Path(log_path) if log_path else self.base_path / "conversion_log.json"
        self.log = []

    def check_pdftotext(self):
        """Check if pdftotext is available"""
        return shutil.which('pdftotext') is not None

    def get_available_method(self):
        """Auto-detect available extraction method"""
        if self.check_pdftotext():
            return 'pdftotext'

        try:
            import PyPDF2
            return 'pypdf2'
        except ImportError:
            pass

        try:
            import pdfplumber
            return 'pdfplumber'
        except ImportError:
            pass

        return None

    def extract_text(self, pdf_path, txt_path, method='pdftotext'):
        """
        Extract text from single PDF

        Args:
            pdf_path: Path to PDF file
            txt_path: Path for output text file
            method: 'pdftotext', 'pypdf2', or 'pdfplumber'

        Returns:
            dict: Conversion result with status and metadata
        """
        start_time = datetime.now()
        result = {
            'pdf_file': str(pdf_path),
            'txt_file': str(txt_path),
            'method': method,
            'timestamp': start_time.isoformat(),
            'success': False
        }

        try:
            # Create output directory
            txt_path.parent.mkdir(parents=True, exist_ok=True)

            if method == 'pdftotext':
                if not self.check_pdftotext():
                    result['error'] = "pdftotext not installed. Use --method pypdf2 or install poppler-utils"
                    result['duration_seconds'] = (datetime.now() - start_time).total_seconds()
                    self.log.append(result)
                    return result
                # Use pdftotext command
                subprocess.run(
                    ['pdftotext', '-layout', str(pdf_path), str(txt_path)],
                    check=True,
                    capture_output=True
                )

            elif method == 'pypdf2':
                # Use PyPDF2
                import PyPDF2
                with open(pdf_path, 'rb') as pdf_file:
                    reader = PyPDF2.PdfReader(pdf_file)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text() + "\n\n"

                with open(txt_path, 'w', encoding='utf-8') as txt_file:
                    txt_file.write(text)

            elif method == 'pdfplumber':
                # Use pdfplumber
                import pdfplumber
                text = ""
                with pdfplumber.open(pdf_path) as pdf:
                    for page in pdf.pages:
                        text += page.extract_text() + "\n\n"

                with open(txt_path, 'w', encoding='utf-8') as txt_file:
                    txt_file.write(text)

            # Check output
            if txt_path.exists() and txt_path.stat().st_size > 0:
                result['success'] = True
                result['output_size'] = txt_path.stat().st_size
                result['pdf_size'] = pdf_path.stat().st_size
                result['compression_ratio'] = f"{txt_path.stat().st_size / pdf_path.stat().st_size:.2%}"
            else:
                result['error'] = "Output file empty or not created"

        except subprocess.CalledProcessError as e:
            result['error'] = f"pdftotext error: {e.stderr.decode()}"
        except Exception as e:
            result['error'] = str(e)

        result['duration_seconds'] = (datetime.now() - start_time).total_seconds()
        self.log.append(result)

        return result

    def batch_extract_year(self, year, dry_run=False, method='pdftotext'):
        """
        Extract all PDFs for a given year

        Args:
            year: Year to process (e.g., 2024)
            dry_run: If True, only show what would be done
            method: Extraction method ('pdftotext', 'pypdf2', or 'pdfplumber')

        Returns:
            dict: Summary of conversion results
        """
        year_path = self.base_path / str(year)

        # Try both "PDFs" and "PDF" (case-sensitive)
        pdf_path = year_path / "PDFs"
        if not pdf_path.exists():
            pdf_path = year_path / "PDF"

        txt_path = year_path / "text"
        if not txt_path.exists():
            txt_path = year_path / "Text"

        if not pdf_path.exists():
            return {'error': f"PDF directory not found: {year_path}/PDFs or {year_path}/PDF"}

        results = {
            'year': year,
            'total': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0,
            'files': []
        }

        # Process agenda and minutes
        for doc_type in ['agenda', 'minutes']:
            pdf_dir = pdf_path / doc_type
            txt_dir = txt_path / doc_type

            if not pdf_dir.exists():
                continue

            for pdf_file in sorted(pdf_dir.glob("*.pdf")):
                # Skip macOS resource fork files
                if pdf_file.name.startswith("._"):
                    continue

                results['total'] += 1

                # Generate output filename
                txt_file = txt_dir / f"{pdf_file.stem}.txt"

                # Skip if already exists
                if txt_file.exists():
                    results['skipped'] += 1
                    print(f"  ⏭️  Skipped: {pdf_file.name} (already exists)")
                    continue

                print(f"  🔄 Converting: {pdf_file.name}")

                if not dry_run:
                    result = self.extract_text(pdf_file, txt_file, method=method)

                    if result['success']:
                        results['success'] += 1
                        print(f"     ✅ Success: {result['output_size']:,} bytes ({result['compression_ratio']})")
                    else:
                        results['failed'] += 1
                        print(f"     ❌ Failed: {result.get('error', 'Unknown error')}")

                    results['files'].append(result)
                else:
                    print(f"     [DRY RUN] Would convert to: {txt_file}")

        return results

    def batch_extract_all(self, years=None, dry_run=False, method='auto'):
        """
        Extract all PDFs for multiple years

        Args:
            years: List of years to process (None = all available)
            dry_run: If True, only show what would be done
            method: Extraction method ('auto', 'pdftotext', 'pypdf2', or 'pdfplumber')
        """
        if years is None:
            # Find all year directories
            years = sorted([
                int(d.name) for d in self.base_path.iterdir()
                if d.is_dir() and d.name.isdigit()
            ])

        # Auto-detect method if needed
        if method == 'auto':
            method = self.get_available_method()
            if method is None:
                print("❌ Error: No PDF extraction method available!")
                print("   Install one of the following:")
                print("   - poppler-utils (brew install poppler)")
                print("   - PyPDF2 (pip install PyPDF2)")
                print("   - pdfplumber (pip install pdfplumber)")
                return []

        print(f"\n📄 PDF to Text Batch Converter")
        print(f"{'='*50}")
        print(f"Base path: {self.base_path}")
        print(f"Years to process: {years}")
        print(f"Method: {method}")
        print(f"Dry run: {dry_run}\n")

        all_results = []

        for year in years:
            print(f"\n📅 Processing {year}...")
            results = self.batch_extract_year(year, dry_run=dry_run, method=method)

            if 'error' in results:
                print(f"   ⚠️  {results['error']}")
            else:
                print(f"\n   Summary for {year}:")
                print(f"   Total PDFs: {results['total']}")
                print(f"   ✅ Converted: {results['success']}")
                print(f"   ⏭️  Skipped: {results['skipped']}")
                print(f"   ❌ Failed: {results['failed']}")

            all_results.append(results)

        # Save log
        if not dry_run and self.log:
            with open(self.log_path, 'w') as f:
                json.dump(self.log, f, indent=2)
            print(f"\n📝 Conversion log saved: {self.log_path}")

        return all_results


def main():
    """Command-line interface"""
    import argparse

    parser = argparse.ArgumentParser(description='Convert PDFs to text in batch')
    parser.add_argument('base_path', help='Base directory with year folders')
    parser.add_argument('--years', nargs='+', type=int, help='Specific years to process')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done')
    parser.add_argument('--method', default='auto',
                        choices=['auto', 'pdftotext', 'pypdf2', 'pdfplumber'],
                        help='Extraction method (default: auto-detect)')

    args = parser.parse_args()

    converter = PDFToTextConverter(args.base_path)
    converter.batch_extract_all(years=args.years, dry_run=args.dry_run, method=args.method)


if __name__ == '__main__':
    main()
