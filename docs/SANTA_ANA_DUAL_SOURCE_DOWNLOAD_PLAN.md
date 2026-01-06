# Santa Ana Dual-Source Document Download Plan

**Created:** 2025-11-28
**Status:** Active
**Purpose:** Optimal document retrieval using both PrimeGov and Laserfiche systems

---

## Overview

Santa Ana maintains **two separate document management systems** with different content and potentially different quality levels:

| System | URL | Technology | Primary Content |
|--------|-----|------------|-----------------|
| **PrimeGov** | `santa-ana.primegov.com` | Modern web portal | Recent meetings (2020+), videos |
| **Laserfiche** | `publicdocs.santa-ana.org/WebLink/` | ASP.NET WebForms | Historical docs, resolutions, ordinances |

This plan leverages both systems to maximize document coverage and quality.

---

## System Comparison

### PrimeGov Portal

**URL:** `https://santa-ana.primegov.com/public/portal`

**Characteristics:**
- Modern JavaScript-based portal
- API available (`/api/meetings`)
- Video links included
- Meeting type filtering
- Year-based navigation tabs

**Current Tool:** `tools/download_santa_ana_selenium.py`

**Strengths:**
- Easy navigation
- Consistent document naming
- Video links captured
- Meeting metadata available

**Weaknesses:**
- May have lower resolution PDFs (compiled/optimized for web)
- Limited historical data
- Requires Selenium for full functionality

---

### Laserfiche WebLink 9

**URL:** `https://publicdocs.santa-ana.org/WebLink/`

**Characteristics:**
- ASP.NET WebForms architecture
- Cookie-based sessions required
- ViewState management needed
- `__doPostBack()` JavaScript navigation
- Direct folder ID access

**Documentation:** `Santa_Ana_Document_Extraction_Instructions.md`

**Key Folder IDs:**

| Folder | ID | Direct URL |
|--------|-----|------------|
| Agenda Packets | 32945 | `Browse.aspx?startid=32945&dbid=1` |
| Minutes | 73985 | `Browse.aspx?startid=73985` |
| Resolutions | 4 | `Browse.aspx?startid=4` |
| Ordinances | 3 | `Browse.aspx?startid=3` |
| Contracts | 6 | `Browse.aspx?startid=6` |

**Strengths:**
- Original document quality (not recompiled)
- Extensive historical archive
- Additional document types (resolutions, ordinances)
- Plain text option available

**Weaknesses:**
- Complex navigation (ViewState, postbacks)
- Requires careful session management
- Older interface

---

## PDF Quality Comparison Method

Before committing to one source, compare PDF quality using these metrics:

### Quick Comparison Script

```python
#!/usr/bin/env python3
"""
Compare PDF quality between PrimeGov and Laserfiche sources
"""

import os
import subprocess
from pathlib import Path

def get_pdf_info(pdf_path):
    """Extract PDF metadata and quality indicators"""
    info = {
        'path': str(pdf_path),
        'file_size_kb': pdf_path.stat().st_size / 1024,
        'file_size_mb': pdf_path.stat().st_size / (1024 * 1024),
    }

    # Use pdfinfo (from poppler) if available
    try:
        result = subprocess.run(
            ['pdfinfo', str(pdf_path)],
            capture_output=True, text=True, timeout=30
        )
        for line in result.stdout.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower().replace(' ', '_')
                info[key] = value.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Use pdfimages to count/analyze images
    try:
        result = subprocess.run(
            ['pdfimages', '-list', str(pdf_path)],
            capture_output=True, text=True, timeout=30
        )
        lines = [l for l in result.stdout.split('\n') if l.strip() and not l.startswith('page')]
        info['image_count'] = len(lines) - 1  # Subtract header

        # Parse image resolutions
        resolutions = []
        for line in lines[1:]:  # Skip header
            parts = line.split()
            if len(parts) >= 7:
                try:
                    x_ppi = int(parts[5])
                    y_ppi = int(parts[6])
                    resolutions.append((x_ppi, y_ppi))
                except (ValueError, IndexError):
                    pass

        if resolutions:
            info['avg_image_dpi'] = sum(r[0] for r in resolutions) / len(resolutions)
            info['max_image_dpi'] = max(r[0] for r in resolutions)
            info['min_image_dpi'] = min(r[0] for r in resolutions)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Extract text and measure quality
    try:
        result = subprocess.run(
            ['pdftotext', '-layout', str(pdf_path), '-'],
            capture_output=True, text=True, timeout=60
        )
        text = result.stdout
        info['text_length'] = len(text)
        info['text_lines'] = len(text.split('\n'))
        info['text_words'] = len(text.split())

        # Check for common OCR issues
        info['has_garbled_text'] = bool(
            text.count('�') > 10 or  # Unicode errors
            text.count('  ') > text.count(' ') * 0.1  # Excessive spacing
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    return info


def compare_pdfs(primegov_pdf, laserfiche_pdf):
    """Compare two PDFs from different sources"""

    print("=" * 70)
    print("PDF QUALITY COMPARISON")
    print("=" * 70)

    pg_info = get_pdf_info(Path(primegov_pdf))
    lf_info = get_pdf_info(Path(laserfiche_pdf))

    print(f"\n{'Metric':<25} {'PrimeGov':<20} {'Laserfiche':<20} {'Winner':<10}")
    print("-" * 75)

    comparisons = [
        ('File Size (MB)', 'file_size_mb', 'higher'),
        ('Page Count', 'pages', 'equal'),
        ('Image Count', 'image_count', 'higher'),
        ('Avg Image DPI', 'avg_image_dpi', 'higher'),
        ('Max Image DPI', 'max_image_dpi', 'higher'),
        ('Text Length', 'text_length', 'higher'),
        ('Text Words', 'text_words', 'higher'),
        ('Garbled Text', 'has_garbled_text', 'lower'),
    ]

    scores = {'primegov': 0, 'laserfiche': 0}

    for label, key, prefer in comparisons:
        pg_val = pg_info.get(key, 'N/A')
        lf_val = lf_info.get(key, 'N/A')

        # Determine winner
        winner = '-'
        if pg_val != 'N/A' and lf_val != 'N/A':
            try:
                pg_num = float(pg_val) if not isinstance(pg_val, bool) else (1 if pg_val else 0)
                lf_num = float(lf_val) if not isinstance(lf_val, bool) else (1 if lf_val else 0)

                if prefer == 'higher':
                    if pg_num > lf_num:
                        winner = 'PrimeGov'
                        scores['primegov'] += 1
                    elif lf_num > pg_num:
                        winner = 'Laserfiche'
                        scores['laserfiche'] += 1
                elif prefer == 'lower':
                    if pg_num < lf_num:
                        winner = 'PrimeGov'
                        scores['primegov'] += 1
                    elif lf_num < pg_num:
                        winner = 'Laserfiche'
                        scores['laserfiche'] += 1
            except (ValueError, TypeError):
                pass

        # Format values
        if isinstance(pg_val, float):
            pg_val = f"{pg_val:.2f}"
        if isinstance(lf_val, float):
            lf_val = f"{lf_val:.2f}"

        print(f"{label:<25} {str(pg_val):<20} {str(lf_val):<20} {winner:<10}")

    print("-" * 75)
    print(f"\n{'OVERALL SCORE:':<25} {scores['primegov']:<20} {scores['laserfiche']:<20}")

    if scores['laserfiche'] > scores['primegov']:
        print("\n✅ RECOMMENDATION: Use Laserfiche as primary source")
    elif scores['primegov'] > scores['laserfiche']:
        print("\n✅ RECOMMENDATION: Use PrimeGov as primary source")
    else:
        print("\n⚖️  RECOMMENDATION: Sources are comparable - use PrimeGov for convenience")

    return scores


if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        print("Usage: python compare_pdf_quality.py <primegov.pdf> <laserfiche.pdf>")
        sys.exit(1)

    compare_pdfs(sys.argv[1], sys.argv[2])
```

### Quality Indicators

| Metric | What It Measures | Better Source Has |
|--------|-----------------|-------------------|
| **File Size** | Overall data density | Larger = more detail |
| **Image DPI** | Scan/render resolution | Higher = clearer text |
| **Text Extraction** | OCR/embedded text quality | More words = better extraction |
| **Garbled Characters** | Unicode/encoding issues | Fewer = cleaner source |
| **Page Count** | Should match | Equal |

### Manual Quality Check

1. **Download same meeting from both sources**
2. **Open side-by-side and compare:**
   - Text sharpness (zoom to 200%)
   - Image clarity
   - Table alignment
   - Header/footer quality
3. **Test text extraction:**
   ```bash
   pdftotext -layout primegov_agenda.pdf primegov.txt
   pdftotext -layout laserfiche_agenda.pdf laserfiche.txt
   diff primegov.txt laserfiche.txt
   ```

---

## Download Workflow

### Phase 1: Quality Assessment (Do First)

```bash
# 1. Download one meeting from each source manually
# PrimeGov: Navigate to https://santa-ana.primegov.com/public/portal
# Laserfiche: Navigate to https://publicdocs.santa-ana.org/WebLink/Browse.aspx?startid=73985

# 2. Compare quality
python3 tools/compare_pdf_quality.py \
    ~/Downloads/primegov_minutes_20240820.pdf \
    ~/Downloads/laserfiche_minutes_20240820.pdf
```

### Phase 2: Primary Source Download

**If Laserfiche wins quality test:**

```bash
# Create Laserfiche downloader (needs implementation)
python3 tools/download_santa_ana_laserfiche.py \
    --folders minutes agendas \
    --years 2024 2023 2022 2021 2020 \
    --output "/Volumes/Samsung USB/City_extraction/Santa_Ana"
```

**If PrimeGov wins or is comparable:**

```bash
# Use existing Selenium tool
python3 tools/download_santa_ana_selenium.py \
    --years 2024 2023 2022 2021 2020 \
    --types agenda minutes \
    --output "/Volumes/Samsung USB/City_extraction/Santa_Ana"
```

### Phase 3: Fill Gaps with Secondary Source

```bash
# After primary download, check for missing meetings
python3 tools/check_meeting_coverage.py \
    --dir "/Volumes/Samsung USB/City_extraction/Santa_Ana" \
    --years 2024 2023 2022

# Download missing from alternate source
```

### Phase 4: Historical Documents (Laserfiche Only)

```bash
# Pre-2020 documents only available in Laserfiche
python3 tools/download_santa_ana_laserfiche.py \
    --folders minutes agendas \
    --years 2019 2018 2017 2016 2015 \
    --output "/Volumes/Samsung USB/City_extraction/Santa_Ana"
```

### Phase 5: Supplementary Documents (Laserfiche Only)

```bash
# Resolutions - useful for vote context
python3 tools/download_santa_ana_laserfiche.py \
    --folders resolutions \
    --years 2024 2023 2022 \
    --output "/Volumes/Samsung USB/City_extraction/Santa_Ana"
```

---

## Implementation Plan

### Existing Tools (Ready to Use)

| Tool | Source | Status |
|------|--------|--------|
| `download_santa_ana_selenium.py` | PrimeGov | ✅ Ready |
| `download_santa_ana_meetings.py` | PrimeGov | ✅ Ready (requests-based fallback) |
| `pdf_to_text_batch.py` | N/A | ✅ Ready |

### Tools to Create

| Tool | Source | Priority | Effort |
|------|--------|----------|--------|
| `compare_pdf_quality.py` | Both | HIGH | LOW |
| `download_santa_ana_laserfiche.py` | Laserfiche | HIGH | MEDIUM |
| `check_meeting_coverage.py` | Both | MEDIUM | LOW |

### Laserfiche Downloader Requirements

Based on `Santa_Ana_Document_Extraction_Instructions.md`:

```python
class LaserficheDownloader:
    """
    Requirements:
    1. Cookie-based session management
    2. ASP.NET ViewState handling
    3. __doPostBack() navigation simulation
    4. Folder hierarchy traversal
    5. Direct download URL construction
    """

    BASE_URL = "https://publicdocs.santa-ana.org/WebLink/"

    FOLDERS = {
        'agendas': 32945,
        'minutes': 73985,
        'resolutions': 4,
        'ordinances': 3,
        'contracts': 6
    }

    def navigate_folder(self, folder_id):
        """
        Navigate to folder using:
        - Browse.aspx?startid={folder_id}&dbid=1
        - Maintain ViewState across requests
        - Handle pagination
        """
        pass

    def download_document(self, doc_id):
        """
        Download using:
        - DocView.aspx?id={doc_id}&dbid=1&openfile=true
        - Or ElectronicFile.aspx?docid={doc_id}&dbid=1
        """
        pass

    def get_plain_text(self, doc_id):
        """
        Get text version:
        - Navigate to DocView.aspx?id={doc_id}&dbid=1
        - Find "View Plain Text" link
        - Extract text content
        """
        pass
```

---

## Output Directory Structure

```
Santa_Ana/
├── 2024/
│   ├── PDFs/
│   │   ├── agenda/
│   │   │   └── 20240820_agenda_regular_city_council_meeting.pdf
│   │   └── minutes/
│   │       └── 20240820_minutes_regular_city_council_meeting.pdf
│   ├── text/
│   │   ├── agenda/
│   │   │   └── 20240820_agenda_regular_city_council_meeting.txt
│   │   └── minutes/
│   │       └── 20240820_minutes_regular_city_council_meeting.txt
│   └── extractions/
│       └── 20240820_votes.json
├── 2023/
│   └── ...
├── resolutions/
│   ├── 2024/
│   └── ...
├── reports/
│   ├── primegov_download_report.json
│   ├── laserfiche_download_report.json
│   └── quality_comparison.json
└── metadata/
    ├── meeting_index.json
    └── coverage_report.json
```

---

## Decision Matrix: Which Source to Use

| Scenario | Recommended Source | Reason |
|----------|-------------------|--------|
| Recent meetings (2020+) | Quality test winner | Best quality available |
| Historical (pre-2020) | Laserfiche | Only source |
| Resolutions/Ordinances | Laserfiche | Only source |
| Missing from primary | Secondary source | Fill gaps |
| Video links needed | PrimeGov | Only source |
| Plain text needed | Laserfiche | Built-in option |

---

## Next Steps

1. **[ ] Run quality comparison** on 2-3 sample meetings
2. **[ ] Document quality results** in this file
3. **[ ] Create `compare_pdf_quality.py`** tool
4. **[ ] Create `download_santa_ana_laserfiche.py`** if Laserfiche wins
5. **[ ] Download 2024 meetings** from winning source
6. **[ ] Download historical meetings** from Laserfiche
7. **[ ] Run vote extraction** on downloaded documents

---

## Quality Test Results

*(To be filled in after running comparison)*

### Test Meeting: August 20, 2024

| Metric | PrimeGov | Laserfiche | Winner |
|--------|----------|------------|--------|
| File Size (MB) | TBD | TBD | TBD |
| Image DPI | TBD | TBD | TBD |
| Text Words | TBD | TBD | TBD |
| Text Quality | TBD | TBD | TBD |

**Conclusion:** TBD

---

## References

- [Santa_Ana_Document_Extraction_Instructions.md](../Santa_Ana_Document_Extraction_Instructions.md) - Laserfiche technical details
- [tools/download_santa_ana_selenium.py](../tools/download_santa_ana_selenium.py) - PrimeGov Selenium downloader
- [tools/download_santa_ana_meetings.py](../tools/download_santa_ana_meetings.py) - PrimeGov requests downloader
