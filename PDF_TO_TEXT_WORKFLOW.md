# PDF to Text Extraction and Storage Workflow
**Purpose:** Complete guide for converting PDFs to text and organizing both file types efficiently

**Created:** 2025-11-24
**Status:** Recommended workflow for extraction and storage

---

## 🎯 Overview

**The Problem:**
- PDFs are large (8-35 MB each for minutes)
- Text files are small (40-150 KB, ~1-2% of PDF size)
- Need both formats: PDFs for archival, text for AI processing
- External storage has space, project repo should stay lean

**The Solution:**
- Store PDFs on external drive (Samsung USB)
- Extract text and store alongside PDFs on external drive
- Copy only needed text files to project for active work
- Keep project repo clean (no large files in git)

---

## 📁 Storage Strategy

### External Storage (Samsung USB)
```
/Volumes/Samsung USB/City_extraction/Santa_Ana/
├── 2024/
│   ├── pdfs/
│   │   ├── agenda/
│   │   │   └── 20240220_agenda_regular_city_council_meeting.pdf (3 MB)
│   │   └── minutes/
│   │       └── 20240220_minutes_regular_city_council_meeting.pdf (24 MB)
│   └── text/
│       ├── agenda/
│       │   └── 20240220_agenda_regular_city_council_meeting.txt (80 KB)
│       └── minutes/
│           └── 20240220_minutes_regular_city_council_meeting.txt (150 KB)
```

**Store on external:**
- ✅ All PDFs (original source files)
- ✅ All extracted text files (permanent archive)
- ✅ Conversion logs and metadata

### Project Repository
```
extractors/santa_ana/2024/
├── training_data/
│   ├── santa_ana_vote_extraction_2024.csv
│   └── santa_ana_vote_extraction_2024.json
└── source_documents/        # Only active working files
    ├── 20240220_minutes.txt  (copied from external as needed)
    └── 20240220_agenda.txt   (copied from external as needed)
```

**Store in project:**
- ✅ CSV extraction data (small, actively edited)
- ✅ JSON conversion data (small)
- ✅ Text files for CURRENT work only (copy from external)
- ❌ PDFs (too large, use external)
- ❌ Full text archive (use external)

---

## 🔧 PDF to Text Extraction Methods

### Method 1: pdftotext (Recommended)

**Install:**
```bash
# macOS
brew install poppler

# Verify installation
pdftotext -v
```

**Extract single file:**
```bash
pdftotext -layout "/path/to/file.pdf" "/path/to/output.txt"
```

**Options:**
- `-layout`: Preserve page layout (recommended for city documents)
- `-raw`: Plain text extraction
- `-table`: Better for tabular data
- `-nopgbrk`: Remove page breaks

**Example:**
```bash
pdftotext -layout \
  "/Volumes/Samsung USB/City_extraction/Santa_Ana/2024/pdfs/minutes/20240220_minutes.pdf" \
  "/Volumes/Samsung USB/City_extraction/Santa_Ana/2024/text/minutes/20240220_minutes.txt"
```

### Method 2: Python PyPDF2 (Fallback)

**Install:**
```bash
pip install PyPDF2
```

**Extract:**
```python
import PyPDF2
from pathlib import Path

def extract_text_pypdf2(pdf_path, output_path):
    """Extract text using PyPDF2"""
    with open(pdf_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n\n"

    with open(output_path, 'w', encoding='utf-8') as txt_file:
        txt_file.write(text)

    return output_path
```

### Method 3: pdfplumber (Best for Tables)

**Install:**
```bash
pip install pdfplumber
```

**Extract with layout preservation:**
```python
import pdfplumber

def extract_text_pdfplumber(pdf_path, output_path):
    """Extract text using pdfplumber (good for tables)"""
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n\n"

    with open(output_path, 'w', encoding='utf-8') as txt_file:
        txt_file.write(text)

    return output_path
```

---

## 🤖 Automated Batch Extraction Script

### Complete Extraction Tool

**File: `tools/pdf_to_text_batch.py`**

```python
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
            base_path: Root directory with YYYY/pdfs/ structure
            log_path: Optional path for conversion log
        """
        self.base_path = Path(base_path)
        self.log_path = Path(log_path) if log_path else self.base_path / "conversion_log.json"
        self.log = []

    def check_pdftotext(self):
        """Check if pdftotext is available"""
        return shutil.which('pdftotext') is not None

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

            if method == 'pdftotext' and self.check_pdftotext():
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

    def batch_extract_year(self, year, dry_run=False):
        """
        Extract all PDFs for a given year

        Args:
            year: Year to process (e.g., 2024)
            dry_run: If True, only show what would be done

        Returns:
            dict: Summary of conversion results
        """
        year_path = self.base_path / str(year)
        pdf_path = year_path / "pdfs"
        txt_path = year_path / "text"

        if not pdf_path.exists():
            return {'error': f"PDF directory not found: {pdf_path}"}

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
                    result = self.extract_text(pdf_file, txt_file)

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

    def batch_extract_all(self, years=None, dry_run=False):
        """
        Extract all PDFs for multiple years

        Args:
            years: List of years to process (None = all available)
            dry_run: If True, only show what would be done
        """
        if years is None:
            # Find all year directories
            years = sorted([
                int(d.name) for d in self.base_path.iterdir()
                if d.is_dir() and d.name.isdigit()
            ])

        print(f"\n📄 PDF to Text Batch Converter")
        print(f"{'='*50}")
        print(f"Base path: {self.base_path}")
        print(f"Years to process: {years}")
        print(f"Dry run: {dry_run}\n")

        all_results = []

        for year in years:
            print(f"\n📅 Processing {year}...")
            results = self.batch_extract_year(year, dry_run=dry_run)

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
    parser.add_argument('--method', default='pdftotext',
                        choices=['pdftotext', 'pypdf2', 'pdfplumber'],
                        help='Extraction method')

    args = parser.parse_args()

    converter = PDFToTextConverter(args.base_path)
    converter.batch_extract_all(years=args.years, dry_run=args.dry_run)


if __name__ == '__main__':
    main()
```

---

## 🚀 Usage Examples

### Extract All Years
```bash
python3 tools/pdf_to_text_batch.py \
  "/Volumes/Samsung USB/City_extraction/Santa_Ana"
```

### Extract Specific Years (Dry Run)
```bash
python3 tools/pdf_to_text_batch.py \
  "/Volumes/Samsung USB/City_extraction/Santa_Ana" \
  --years 2024 2021 \
  --dry-run
```

### Extract Single Year
```bash
python3 tools/pdf_to_text_batch.py \
  "/Volumes/Samsung USB/City_extraction/Santa_Ana" \
  --years 2024
```

### Use Alternative Method
```bash
python3 tools/pdf_to_text_batch.py \
  "/Volumes/Samsung USB/City_extraction/Santa_Ana" \
  --method pdfplumber
```

---

## 📊 Workflow Integration

### Step 1: Download PDFs
```bash
# Save directly to organized structure
/Volumes/Samsung USB/City_extraction/Santa_Ana/2024/pdfs/minutes/20240220_minutes.pdf
```

### Step 2: Extract Text
```bash
# Run batch converter
python3 tools/pdf_to_text_batch.py \
  "/Volumes/Samsung USB/City_extraction/Santa_Ana" \
  --years 2024
```

**Output:**
```
/Volumes/Samsung USB/City_extraction/Santa_Ana/2024/text/minutes/20240220_minutes.txt
```

### Step 3: Copy to Project (When Needed)
```bash
# Copy only the specific files you're working with
cp "/Volumes/Samsung USB/City_extraction/Santa_Ana/2024/text/minutes/20240220_minutes.txt" \
   extractors/santa_ana/2024/source_documents/
```

### Step 4: Extract Votes
```bash
# Use CSV workflow with copied text file
# (See CSV_EXTRACTION_WORKFLOW.md)
```

---

## 🔍 Quality Control

### Verify Extraction Quality

**Check file sizes:**
```bash
#!/bin/bash
# Compare PDF and text file sizes

for year in 2024 2021 2019; do
    echo "Year: $year"

    pdf_size=$(du -sh "$year/pdfs" | cut -f1)
    txt_size=$(du -sh "$year/text" | cut -f1)

    echo "  PDFs: $pdf_size"
    echo "  Text: $txt_size"
done
```

**Sample text files:**
```bash
# View first/last 50 lines of extracted text
head -50 "/Volumes/Samsung USB/City_extraction/Santa_Ana/2024/text/minutes/20240220_minutes.txt"
tail -50 "/Volumes/Samsung USB/City_extraction/Santa_Ana/2024/text/minutes/20240220_minutes.txt"
```

**Check for extraction errors:**
```bash
# Find empty or very small text files
find . -name "*.txt" -size -1k
```

---

## 📈 Space Savings Analysis

### Before (All Files in Project)
```
extractors/
└── santa_ana/
    └── 2024/
        ├── 20240220_minutes.pdf        24 MB
        ├── 20240220_minutes.txt       150 KB
        ├── 20240305_minutes.pdf         8 MB
        ├── 20240305_minutes.txt        80 KB
        └── ... (24 meetings)
Total: ~400 MB PDFs + ~3 MB text = 403 MB
```

### After (External Storage Strategy)
```
External Storage:
/Volumes/Samsung USB/City_extraction/Santa_Ana/2024/
├── pdfs/  (400 MB - archived)
└── text/  (3 MB - archived)

Project Repository:
extractors/santa_ana/2024/source_documents/
├── 20240220_minutes.txt       150 KB  (only current work)
└── 20240220_agenda.txt         80 KB  (only current work)
Total: ~230 KB (0.06% of original)
```

**Savings: 402.8 MB (99.94% reduction in repo size)**

---

## 🛠️ Helper Scripts

### Copy Current Work Files to Project

**File: `tools/copy_work_files.sh`**

```bash
#!/bin/bash
# Copy specific text files from external storage to project

EXTERNAL_BASE="/Volumes/Samsung USB/City_extraction/Santa_Ana"
PROJECT_BASE="extractors/santa_ana"

# Usage: ./copy_work_files.sh 2024 20240220
YEAR=$1
MEETING_DATE=$2

if [ -z "$YEAR" ] || [ -z "$MEETING_DATE" ]; then
    echo "Usage: $0 YEAR MEETING_DATE"
    echo "Example: $0 2024 20240220"
    exit 1
fi

# Copy minutes
cp "$EXTERNAL_BASE/$YEAR/text/minutes/${MEETING_DATE}_minutes"*.txt \
   "$PROJECT_BASE/$YEAR/source_documents/" 2>/dev/null

# Copy agenda
cp "$EXTERNAL_BASE/$YEAR/text/agenda/${MEETING_DATE}_agenda"*.txt \
   "$PROJECT_BASE/$YEAR/source_documents/" 2>/dev/null

echo "✅ Files copied for $YEAR/$MEETING_DATE"
ls -lh "$PROJECT_BASE/$YEAR/source_documents/${MEETING_DATE}"*
```

### Archive Project Files Back to External

**File: `tools/archive_work_files.sh`**

```bash
#!/bin/bash
# Archive completed work files back to external storage

EXTERNAL_BASE="/Volumes/Samsung USB/City_extraction/Santa_Ana"
PROJECT_BASE="extractors/santa_ana"

YEAR=$1

if [ -z "$YEAR" ]; then
    echo "Usage: $0 YEAR"
    exit 1
fi

# Archive CSV and JSON to external
mkdir -p "$EXTERNAL_BASE/$YEAR/extractions"

cp "$PROJECT_BASE/$YEAR/training_data"/*.csv \
   "$EXTERNAL_BASE/$YEAR/extractions/"

cp "$PROJECT_BASE/$YEAR/training_data"/*.json \
   "$EXTERNAL_BASE/$YEAR/extractions/"

echo "✅ Extraction data archived to external storage"
```

---

## ✅ Recommended Workflow Summary

1. **Download PDFs** → Save to external storage year folders
2. **Extract text** → Batch convert, save to external storage
3. **Copy to project** → Copy only files for current work
4. **Extract votes** → Manual CSV extraction or AI extraction
5. **Archive results** → Copy CSV/JSON back to external storage
6. **Clean project** → Remove source documents when done

**Result:**
- ✅ Complete archive on external drive
- ✅ Lean project repository
- ✅ Fast git operations
- ✅ Easy to work with active files

---

## 📚 See Also

- [EXTERNAL_STORAGE_STRUCTURE_GUIDE.md](EXTERNAL_STORAGE_STRUCTURE_GUIDE.md) - Storage organization
- [CSV_EXTRACTION_WORKFLOW.md](CSV_EXTRACTION_WORKFLOW.md) - Vote extraction process
- [extractors/README.md](extractors/README.md) - Project structure
