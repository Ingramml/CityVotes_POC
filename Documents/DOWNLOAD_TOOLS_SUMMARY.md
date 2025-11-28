# Download Tools Summary
**Date:** 2025-11-24
**Status:** ✅ Complete - **Selenium automation working!**

---

## 🎯 Goal

Download and organize Santa Ana city council meeting PDFs (agendas and minutes) from the PrimeGov portal.

---

## ✅ Recommended Solution: Selenium Automation (WORKING!)

**Status:** Production-ready automated downloader

**Time:** 6-12 minutes per year (fully automated)

```bash
# One command downloads entire year
python3 tools/download_santa_ana_selenium.py \
  --years 2024 \
  --output "/Volumes/Samsung USB/City_extraction/Santa_Ana"
```

**See:** [SELENIUM_DOWNLOADER_SUCCESS.md](SELENIUM_DOWNLOADER_SUCCESS.md) for details

---

## 💡 Alternative: Manual Download + Automatic Organization

### Why Manual Download?

The Santa Ana PrimeGov portal (https://santa-ana.primegov.com/public/portal) uses **dynamic JavaScript loading** for meeting data. The meeting table is populated via AJAX after the page loads, making it difficult to scrape directly.

**Attempted Solutions:**
1. ❌ API scraping - No public API available
2. ❌ HTML scraping - Data not in initial HTML (loaded via JavaScript)
3. ✅ **Manual download + automatic organization** - Reliable and practical

### Recommended Workflow

**Time:** 20-40 minutes per year

```bash
# Step 1: Manual Download (15-30 min)
# Visit portal in browser, download PDFs to ~/Downloads

# Step 2: Automatic Organization (1 min)
python3 tools/organize_downloaded_pdfs.py \
  --source ~/Downloads \
  --output "/Volumes/Samsung USB/City_extraction/Santa_Ana"

# Step 3: Text Extraction (5-10 min)
python3 tools/pdf_to_text_batch.py \
  "/Volumes/Samsung USB/City_extraction/Santa_Ana" \
  --years 2024
```

---

## 🛠️ Tools Created

### 1. PDF Organizer (Primary Tool)

**File:** [tools/organize_downloaded_pdfs.py](../tools/organize_downloaded_pdfs.py)

**Purpose:** Automatically organizes PDFs downloaded manually from browser

**Features:**
- ✅ Extracts date from filename (multiple formats supported)
- ✅ Identifies document type (agenda/minutes)
- ✅ Identifies meeting type
- ✅ Renames to standard format: `YYYYMMDD_type_meeting-name.pdf`
- ✅ Places in correct year/type folder structure
- ✅ Skips duplicates
- ✅ Dry-run mode for testing

**Usage:**
```bash
# Dry run first
python3 tools/organize_downloaded_pdfs.py \
  --source ~/Downloads \
  --output "/Volumes/Samsung USB/City_extraction/Santa_Ana" \
  --dry-run

# Actually organize
python3 tools/organize_downloaded_pdfs.py \
  --source ~/Downloads \
  --output "/Volumes/Samsung USB/City_extraction/Santa_Ana"
```

**Supported Filename Formats:**
- `Meetings4660Minutes_20250624175240859.pdf` (PrimeGov format)
- `20240220_minutes_city_council.pdf` (Manual naming)
- `2024-02-20_agenda_meeting.pdf` (Alternative format)

### 2. Automated Downloader (Experimental)

**File:** [tools/download_santa_ana_meetings.py](../tools/download_santa_ana_meetings.py)

**Status:** Experimental - Limited by JavaScript rendering

**Issue:** Portal loads meeting data dynamically via JavaScript/AJAX. The initial HTML doesn't contain meeting information.

**Possible Future Solutions:**
- Use Selenium/Playwright for browser automation
- Reverse-engineer AJAX API calls
- Use browser extension for bulk downloads

**Current Status:** Not recommended for production use

---

## 📚 Documentation Created

### 1. Manual Download Workflow Guide

**File:** [MANUAL_DOWNLOAD_WORKFLOW.md](../MANUAL_DOWNLOAD_WORKFLOW.md)

**Contents:**
- Step-by-step manual download instructions
- How to use the organizer script
- Meeting type filtering guidelines
- Troubleshooting common issues
- Time estimates and expected results
- Pro tips for efficient downloading

### 2. Automated Downloader Guide

**File:** [SANTA_ANA_DOWNLOAD_GUIDE.md](../SANTA_ANA_DOWNLOAD_GUIDE.md)

**Contents:**
- Documentation for experimental automated downloader
- Command-line options
- Portal structure analysis
- Future automation possibilities

---

## 📁 Output Structure

Files are organized into the recommended structure:

```
/Volumes/Samsung USB/City_extraction/Santa_Ana/
├── 2024/
│   └── PDFs/
│       ├── agenda/
│       │   ├── 20240116_agenda_regular_city_council_meeting.pdf
│       │   ├── 20240220_agenda_regular_city_council_and_special_housing_authority.pdf
│       │   └── ...
│       └── minutes/
│           ├── 20240116_minutes_regular_city_council_meeting.pdf
│           ├── 20240220_minutes_regular_city_council_meeting.pdf
│           └── ...
├── 2023/
│   └── PDFs/
│       ├── agenda/
│       └── minutes/
└── ...
```

---

## 🔍 Meeting Type Filtering

**Included Meeting Types:**
- Regular City Council Meeting
- Regular City Council and Special Housing Authority Meeting
- Special City Council Meeting

**Excluded Meeting Types:**
- Special Closed Session
- Workshop
- Public Hearing
- Other non-standard meeting types

The organizer script automatically identifies meeting types based on filename patterns.

---

## ⚡ Complete Workflow

### Download One Year (2024 Example)

**1. Visit Portal (15-30 minutes)**
```
URL: https://santa-ana.primegov.com/public/portal
- Click "2024" tab
- For each Regular/Special City Council meeting:
  - Click meeting title
  - Download Agenda PDF
  - Download Minutes PDF
- Save all to ~/Downloads
```

**2. Organize PDFs (1 minute)**
```bash
python3 tools/organize_downloaded_pdfs.py \
  --source ~/Downloads \
  --output "/Volumes/Samsung USB/City_extraction/Santa_Ana"
```

**3. Extract Text (5-10 minutes)**
```bash
python3 tools/pdf_to_text_batch.py \
  "/Volumes/Samsung USB/City_extraction/Santa_Ana" \
  --years 2024
```

**4. Verify Results**
```bash
# Count PDFs
find "/Volumes/Samsung USB/City_extraction/Santa_Ana/2024/pdfs" -name "*.pdf" | wc -l

# Count text files
find "/Volumes/Samsung USB/City_extraction/Santa_Ana/2024/text" -name "*.txt" | wc -l
```

**5. Continue with Vote Extraction**
```bash
# Copy files to project
./tools/copy_work_files.sh 2024 20240220

# Extract votes (manual CSV)
# See CSV_EXTRACTION_WORKFLOW.md
```

---

## 📊 Expected Results

### For One Complete Year

**PDFs:**
- ~24-30 agenda PDFs (~60-120 MB)
- ~24-30 minutes PDFs (~200-800 MB)
- Total: ~260-920 MB

**Text Files (after extraction):**
- ~24-30 agenda text files (~2-4 MB)
- ~24-30 minutes text files (~3-6 MB)
- Total: ~5-10 MB

**Time Investment:**
- Manual download: 15-30 minutes
- Organization: 1 minute
- Text extraction: 5-10 minutes
- **Total: 20-40 minutes per year**

---

## 🚀 Getting Started

### Setup (One-Time)

```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Verify tools are executable
ls -l tools/*.py tools/*.sh

# Test PDF organizer (dry run)
python3 tools/organize_downloaded_pdfs.py --help
```

### First Download Session

1. **Visit Portal:**
   - Go to https://santa-ana.primegov.com/public/portal
   - Click "2024" tab
   - Familiarize yourself with the interface

2. **Download Sample Meeting:**
   - Choose one meeting (e.g., most recent)
   - Download both agenda and minutes
   - Note where files are saved

3. **Test Organizer:**
   ```bash
   python3 tools/organize_downloaded_pdfs.py \
     --source ~/Downloads \
     --output "/Volumes/Samsung USB/City_extraction/Santa_Ana" \
     --dry-run
   ```

4. **Verify Output:**
   - Check the dry-run output
   - Verify file naming looks correct
   - Verify folder structure is correct

5. **Actually Organize:**
   ```bash
   python3 tools/organize_downloaded_pdfs.py \
     --source ~/Downloads \
     --output "/Volumes/Samsung USB/City_extraction/Santa_Ana"
   ```

6. **Extract Text:**
   ```bash
   python3 tools/pdf_to_text_batch.py \
     "/Volumes/Samsung USB/City_extraction/Santa_Ana" \
     --years 2024
   ```

7. **Verify Success:**
   ```bash
   ls -lh "/Volumes/Samsung USB/City_extraction/Santa_Ana/2024/pdfs/agenda/"
   ls -lh "/Volumes/Samsung USB/City_extraction/Santa_Ana/2024/text/agenda/"
   ```

---

## 💡 Tips for Efficient Downloading

### Batch Processing

Download PDFs in batches:
- Day 1: Download all January-March meetings
- Day 2: Download all April-June meetings
- Day 3: Download all July-September meetings
- Day 4: Download all October-December meetings
- Day 5: Organize all at once and extract text

### Browser Tips

- Open multiple tabs for different meetings
- Use browser's download manager to track progress
- Create a checklist to track which meetings you've downloaded

### Quality Control

After organizing, verify:
```bash
# Count meetings per year
find "/Volumes/Samsung USB/City_extraction/Santa_Ana/2024/pdfs" -type f | wc -l

# Check for missing pairs (agenda without minutes or vice versa)
# Should have roughly equal numbers of agendas and minutes
```

---

## 🔗 Related Documentation

- [MANUAL_DOWNLOAD_WORKFLOW.md](../MANUAL_DOWNLOAD_WORKFLOW.md) - Complete manual workflow guide
- [EXTERNAL_STORAGE_STRUCTURE_GUIDE.md](../EXTERNAL_STORAGE_STRUCTURE_GUIDE.md) - Storage organization
- [PDF_TO_TEXT_WORKFLOW.md](../PDF_TO_TEXT_WORKFLOW.md) - Text extraction
- [CSV_EXTRACTION_WORKFLOW.md](../CSV_EXTRACTION_WORKFLOW.md) - Vote extraction
- [STORAGE_AND_EXTRACTION_QUICKSTART.md](../STORAGE_AND_EXTRACTION_QUICKSTART.md) - Quick reference

---

## ✅ Summary

**What Works:**
- ✅ Manual download from portal (browser)
- ✅ Automatic organization with Python script
- ✅ Text extraction with batch tool
- ✅ Integration with existing CSV workflow

**What Doesn't Work (Yet):**
- ❌ Fully automated scraping (JavaScript limitation)

**Recommended Approach:**
Manual download (15-30 min) + automatic organization (1 min) = Practical and reliable workflow

**Future Improvements:**
- Browser automation with Selenium/Playwright
- Browser extension for bulk downloads
- AJAX API reverse-engineering

---

**Created:** 2025-11-24
**Status:** Production-ready
**Recommended Tool:** [tools/organize_downloaded_pdfs.py](../tools/organize_downloaded_pdfs.py)
