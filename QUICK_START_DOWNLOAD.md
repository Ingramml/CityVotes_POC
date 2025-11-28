# Quick Start: Download Santa Ana Meeting Documents

**Quick reference for downloading Santa Ana city council meeting documents**

---

## 🚀 How to Launch the Workflow

### Step 1: Activate Virtual Environment

```bash
source .venv/bin/activate
```

### Step 2: Run the Downloader

**Download one year (2024):**
```bash
python3 tools/download_santa_ana_selenium.py \
  --years 2024 \
  --output "/Volumes/Samsung USB/City_extraction/Santa_Ana"
```

**Download multiple years:**
```bash
python3 tools/download_santa_ana_selenium.py \
  --years 2024 2023 2022 \
  --output "/Volumes/Samsung USB/City_extraction/Santa_Ana"
```

**Dry run first (recommended):**
```bash
python3 tools/download_santa_ana_selenium.py \
  --years 2024 \
  --output "/Volumes/Samsung USB/City_extraction/Santa_Ana" \
  --dry-run
```

---

## 📋 Command Options

| Option | Description | Example |
|--------|-------------|---------|
| `--years` | **Required**. Years to download | `--years 2024 2023` |
| `--output` | Base directory for organized files | `--output "/path/to/output"` |
| `--types` | Document types (agenda/minutes) | `--types agenda minutes` |
| `--download-dir` | Temporary download directory | `--download-dir ~/Downloads` |
| `--dry-run` | Test without downloading | `--dry-run` |
| `--debug` | Detailed debug information | `--debug` |
| `--no-headless` | Show browser window | `--no-headless` |

---

## 📊 What You'll See

### During Download

```
📥 Santa Ana Meeting Downloader (Selenium)
============================================================
Output directory: /Volumes/Samsung USB/City_extraction/Santa_Ana
Years: [2024]
Dry run: False

🌐 Setting up browser...
✅ Using Chrome WebDriver
🌐 Loading portal...

📅 Processing Year 2024
============================================================
  📅 Navigated to year 2024

  📄 Page 1
     Found 0 meetings on this page

  📄 Page 23
     Found 5 meetings on this page

  ✅ Total meetings found: 308
  ✅ Matching meeting types: 23
  ⏭️  Filtered out: 285

  🔄 Processing 23 meetings...

  [1/23] 2024-12-03: Regular City Council Meeting
    📥 Downloading agenda...
      ✅ Downloaded: 1,234,567 bytes
    📥 Downloading minutes...
      ✅ Downloaded: 2,345,678 bytes
```

### After Download - Summary

```
============================================================
📊 Download Summary
============================================================
Meetings found: 308
Meetings filtered out: 285
Meetings processed: 23
Agendas downloaded: 22
Minutes downloaded: 22
Skipped (already exist): 0
Errors: 0

📅 Year-by-Year Breakdown:

  2024:
    Meetings found: 308
    Meetings processed: 23
    Agendas downloaded: 22
    Minutes downloaded: 22

✅ Complete!

📄 Detailed report saved to: /Volumes/Samsung USB/City_extraction/Santa_Ana/download_report_20251124_123456.json
   Total size downloaded: 456.78 MB
📊 CSV spreadsheet saved to: /Volumes/Samsung USB/City_extraction/Santa_Ana/download_report_20251124_123456.csv
```

---

## 📁 Output Structure

Files are automatically organized:

```
/Volumes/Samsung USB/City_extraction/Santa_Ana/
├── download_report_20251124_123456.json  # Detailed download report (JSON)
├── download_report_20251124_123456.csv   # Spreadsheet with video links (CSV)
├── 2024/
│   └── PDFs/
│       ├── agenda/
│       │   ├── 20241203_agenda_regular_city_council_meeting.pdf
│       │   ├── 20241119_agenda_regular_city_council_meeting.pdf
│       │   └── ...
│       └── minutes/
│           ├── 20241203_minutes_regular_city_council_meeting.pdf
│           ├── 20241119_minutes_regular_city_council_meeting.pdf
│           └── ...
├── 2023/
│   └── PDFs/
│       ├── agenda/
│       └── minutes/
└── ...
```

---

## 📄 Download Reports

After downloading, you'll get **two report files**:

### 1. JSON Report (Detailed)

The JSON report (`download_report_YYYYMMDD_HHMMSS.json`) contains:

```json
{
  "timestamp": "2025-11-24T12:34:56",
  "summary": {
    "total_meetings_found": 308,
    "total_meetings_processed": 23,
    "total_agendas_downloaded": 22,
    "total_minutes_downloaded": 22,
    "total_files_downloaded": 44,
    "total_size_mb": 456.78
  },
  "year_stats": {
    "2024": {
      "meetings_found": 308,
      "meetings_processed": 23,
      "agendas_downloaded": 22,
      "minutes_downloaded": 22
    }
  },
  "downloaded_files": [
    {
      "filename": "20241203_agenda_regular_city_council_meeting.pdf",
      "path": "/Volumes/Samsung USB/City_extraction/Santa_Ana/2024/pdfs/agenda/20241203_agenda_regular_city_council_meeting.pdf",
      "type": "agenda",
      "meeting_title": "Regular City Council Meeting",
      "meeting_date": "2024-12-03",
      "year": 2024,
      "size_bytes": 1234567
    },
    ...
  ]
}
```

### 2. CSV Spreadsheet (Easy to View)

The CSV report (`download_report_YYYYMMDD_HHMMSS.csv`) contains:

| meeting_date | meeting_title | year | document_type | filename | file_path | size_mb | download_url | video_link |
|--------------|---------------|------|---------------|----------|-----------|---------|--------------|------------|
| 2024-12-03 | Regular City Council Meeting | 2024 | agenda | 20241203_agenda_... | /Volumes/.../... | 2.34 | https://portal.../CompiledDocument/... | https://... |
| 2024-12-03 | Regular City Council Meeting | 2024 | minutes | 20241203_minutes_... | /Volumes/.../... | 5.67 | https://portal.../CompiledDocument/... | https://... |

**Columns:**
- `meeting_date` - Date of meeting
- `meeting_title` - Full meeting title
- `year` - Year (for easy filtering)
- `document_type` - agenda or minutes
- `filename` - PDF filename
- `file_path` - Full path to downloaded PDF
- `size_mb` - File size in MB
- `download_url` - URL used to download the document
- `video_link` - URL to meeting video (if available)

**Open in Excel or Google Sheets** for easy viewing, sorting, and filtering!

---

## ⚡ Quick Examples

### 1. First Time - Test with Dry Run

```bash
# Activate environment
source .venv/bin/activate

# Test what would be downloaded
python3 tools/download_santa_ana_selenium.py \
  --years 2024 \
  --output "/Volumes/Samsung USB/City_extraction/Santa_Ana" \
  --dry-run

# If it looks good, run for real (remove --dry-run)
python3 tools/download_santa_ana_selenium.py \
  --years 2024 \
  --output "/Volumes/Samsung USB/City_extraction/Santa_Ana"
```

### 2. Download Only Agendas

```bash
python3 tools/download_santa_ana_selenium.py \
  --years 2024 \
  --types agenda \
  --output "/Volumes/Samsung USB/City_extraction/Santa_Ana"
```

### 3. Download Multiple Years

```bash
python3 tools/download_santa_ana_selenium.py \
  --years 2024 2023 2022 2021 2020 2019 \
  --output "/Volumes/Samsung USB/City_extraction/Santa_Ana"
```

### 4. Debug Mode (If Something Goes Wrong)

```bash
python3 tools/download_santa_ana_selenium.py \
  --years 2024 \
  --output "/Volumes/Samsung USB/City_extraction/Santa_Ana" \
  --debug \
  --no-headless
```

---

## 🔄 Complete Workflow

### Download → Extract → Work with Files

```bash
# 1. Activate environment
source .venv/bin/activate

# 2. Download PDFs (6-12 minutes)
python3 tools/download_santa_ana_selenium.py \
  --years 2024 \
  --output "/Volumes/Samsung USB/City_extraction/Santa_Ana"

# 3. Extract text from PDFs (5-10 minutes)
python3 tools/pdf_to_text_batch.py \
  "/Volumes/Samsung USB/City_extraction/Santa_Ana" \
  --years 2024

# 4. Copy working files to project (< 1 minute)
./tools/copy_work_files.sh 2024 20240220

# 5. Extract votes (Manual CSV workflow)
# See CSV_EXTRACTION_WORKFLOW.md
```

---

## 🛠️ Troubleshooting

### Chrome Driver Not Found

```bash
# Install ChromeDriver
brew install chromedriver

# Or check if it's installed
which chromedriver
chromedriver --version
```

### External Drive Not Mounted

```bash
# Check if drive is mounted
ls -la "/Volumes/Samsung USB"

# If not, mount it in Finder
```

### Port Already in Use / Download Issues

```bash
# Run with visible browser to see what's happening
python3 tools/download_santa_ana_selenium.py \
  --years 2024 \
  --output "/Volumes/Samsung USB/City_extraction/Santa_Ana" \
  --no-headless \
  --debug
```

### Python Virtual Environment Not Activated

```bash
# Activate it
source .venv/bin/activate

# Check it's activated (you should see (.venv) in prompt)
which python3
```

---

## 📌 Quick Reference Card

**Basic Command:**
```bash
source .venv/bin/activate
python3 tools/download_santa_ana_selenium.py --years 2024 --output "/Volumes/Samsung USB/City_extraction/Santa_Ana"
```

**With All Options:**
```bash
python3 tools/download_santa_ana_selenium.py \
  --years 2024 2023 \
  --output "/Volumes/Samsung USB/City_extraction/Santa_Ana" \
  --types agenda minutes \
  --download-dir ~/Downloads \
  [--dry-run] \
  [--debug] \
  [--no-headless]
```

---

## 📚 Related Documentation

- [SELENIUM_DOWNLOAD_SETUP.md](SELENIUM_DOWNLOAD_SETUP.md) - Full setup guide
- [Documents/SELENIUM_DOWNLOADER_SUCCESS.md](Documents/SELENIUM_DOWNLOADER_SUCCESS.md) - Technical details
- [PDF_TO_TEXT_WORKFLOW.md](PDF_TO_TEXT_WORKFLOW.md) - Text extraction
- [CSV_EXTRACTION_WORKFLOW.md](CSV_EXTRACTION_WORKFLOW.md) - Vote extraction

---

**Last Updated:** 2025-11-24
**Status:** Production-ready ✅
