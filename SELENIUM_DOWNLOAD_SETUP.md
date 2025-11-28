# Selenium Download Setup Guide
**Purpose:** Setup and use Selenium for automated downloads from Santa Ana portal

**Created:** 2025-11-24
**Status:** Recommended for bulk downloads

---

## 🎯 Overview

**Selenium** is a browser automation tool that can handle JavaScript-rendered pages like the Santa Ana PrimeGov portal.

### Advantages over Manual Download

- ✅ Fully automated - no manual clicking
- ✅ Can download entire years at once
- ✅ Handles pagination automatically
- ✅ Filters meeting types automatically
- ✅ Organizes files automatically

### Time Comparison

| Method | Time for 24 Meetings |
|--------|---------------------|
| Manual + Organizer | 20-40 minutes |
| Selenium | 5-10 minutes (automated) |

---

## 🔧 Setup (One-Time)

### Step 1: Install Selenium

```bash
# Activate virtual environment
source .venv/bin/activate

# Install Selenium
pip install selenium
```

### Step 2: Install Browser Driver

#### Option A: Chrome (Recommended)

```bash
# Install ChromeDriver
brew install chromedriver

# Or download from: https://chromedriver.chromium.org/
```

#### Option B: Firefox (Alternative)

```bash
# Install GeckoDriver for Firefox
brew install geckodriver

# Or download from: https://github.com/mozilla/geckodriver/releases
```

###Step 3: Verify Installation

```bash
# Check ChromeDriver
chromedriver --version

# Or check GeckoDriver
geckodriver --version
```

### Step 4: Test Selenium

```bash
# Test with dry run
python3 tools/download_santa_ana_selenium.py \
  --years 2024 \
  --output "/Volumes/Samsung USB/City_extraction/Santa_Ana" \
  --dry-run
```

---

## 🚀 Usage

### Basic Usage

**Download one year:**
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

### Options

| Option | Description | Example |
|--------|-------------|---------|
| `--years` | Years to download (required) | `--years 2024 2023` |
| `--output` | Output directory | `--output "/path/to/output"` |
| `--types` | Document types (agenda/minutes) | `--types agenda` |
| `--download-dir` | Temporary download location | `--download-dir ~/Downloads` |
| `--dry-run` | Test without downloading | `--dry-run` |
| `--no-headless` | Show browser window | `--no-headless` |

### Examples

**Download only agendas for 2024:**
```bash
python3 tools/download_santa_ana_selenium.py \
  --years 2024 \
  --types agenda \
  --output "/Volumes/Samsung USB/City_extraction/Santa_Ana"
```

**Download with visible browser (for debugging):**
```bash
python3 tools/download_santa_ana_selenium.py \
  --years 2024 \
  --output "/Volumes/Samsung USB/City_extraction/Santa_Ana" \
  --no-headless
```

**Dry run first (recommended):**
```bash
python3 tools/download_santa_ana_selenium.py \
  --years 2024 \
  --output "/Volumes/Samsung USB/City_extraction/Santa_Ana" \
  --dry-run
```

---

## 🔄 Complete Workflow

### Download and Extract One Year

```bash
# Step 1: Download PDFs (5-10 minutes)
python3 tools/download_santa_ana_selenium.py \
  --years 2024 \
  --output "/Volumes/Samsung USB/City_extraction/Santa_Ana"

# Step 2: Extract Text (5-10 minutes)
python3 tools/pdf_to_text_batch.py \
  "/Volumes/Samsung USB/City_extraction/Santa_Ana" \
  --years 2024

# Step 3: Copy to Project for Work
./tools/copy_work_files.sh 2024 20240220

# Step 4: Extract Votes (Manual CSV)
# See CSV_EXTRACTION_WORKFLOW.md
```

### Download Multiple Years

```bash
# Download all years at once
python3 tools/download_santa_ana_selenium.py \
  --years 2024 2023 2022 2021 2020 2019 \
  --output "/Volumes/Samsung USB/City_extraction/Santa_Ana"

# Extract text for all years
python3 tools/pdf_to_text_batch.py \
  "/Volumes/Samsung USB/City_extraction/Santa_Ana" \
  --years 2024 2023 2022 2021 2020 2019
```

---

## 📊 What Happens During Download

### Process Flow

1. **Browser Startup**
   - Selenium launches Chrome/Firefox
   - Navigates to Santa Ana portal
   - Waits for page to load

2. **Year Navigation**
   - Clicks on specified year tab (e.g., "2024")
   - Waits for meeting table to populate

3. **Meeting Discovery**
   - Scans all pages of meetings
   - Extracts meeting titles, dates, and document links
   - Filters by meeting type (Regular/Special City Council only)

4. **Document Download**
   - For each meeting:
     - Downloads agenda (if available)
     - Downloads minutes (if available)
     - Skips if already downloaded
     - Renames to standard format
     - Moves to correct year/type folder

5. **Progress Reporting**
   - Shows current meeting being processed
   - Reports download status
   - Displays summary statistics

### Meeting Type Filter

**Automatically includes:**
- Regular City Council Meeting
- Regular City Council and Special Housing Authority Meeting
- Special City Council Meeting

**Automatically excludes:**
- Special Closed Session
- Workshop
- Public Hearing
- Committee meetings
- Other non-standard meetings

---

## ⚡ Performance

### Speed Estimates

**Per Meeting:**
- Download agenda: ~5-10 seconds
- Download minutes: ~10-20 seconds
- Total per meeting: ~15-30 seconds

**Per Year (24 meetings):**
- With both agenda + minutes: ~6-12 minutes
- Agendas only: ~2-4 minutes
- Minutes only: ~4-8 minutes

**Multiple Years:**
- Linear: each additional year adds ~6-12 minutes
- Can run in background while you work

### Optimization Tips

1. **Run in Headless Mode** (default)
   - Faster than visible browser
   - Lower resource usage

2. **Download by Type**
   - Get agendas first: `--types agenda`
   - Then get minutes: `--types minutes`
   - Easier to verify each step

3. **Run Overnight**
   - For many years, run overnight
   - Set up with nohup:
   ```bash
   nohup python3 tools/download_santa_ana_selenium.py --years 2024 2023 2022 2021 2020 2019 > download.log 2>&1 &
   ```

---

## 🛠️ Troubleshooting

### ChromeDriver Not Found

**Error:** `selenium.common.exceptions.WebDriverException: 'chromedriver' executable needs to be in PATH`

**Solution:**
```bash
# Install ChromeDriver
brew install chromedriver

# Or manually download and add to PATH
export PATH=$PATH:/path/to/chromedriver
```

### ChromeDriver Version Mismatch

**Error:** `This version of ChromeDriver only supports Chrome version X`

**Solution:**
```bash
# Update Chrome browser to latest version
# Then update ChromeDriver
brew upgrade chromedriver
```

### Permission Denied (macOS)

**Error:** `"chromedriver" cannot be opened because the developer cannot be verified`

**Solution:**
```bash
# Remove quarantine attribute
xattr -d com.apple.quarantine /usr/local/bin/chromedriver

# Or use System Preferences > Security & Privacy to allow
```

### Download Location Issues

**Problem:** Files not appearing in expected location

**Solution:**
- Check `--download-dir` setting
- Verify external drive is mounted
- Check available disk space

### Portal Changes

**Problem:** Script stops working after portal updates

**Solution:**
- Check if portal URL changed
- Check if table structure changed
- Report issue for script update

### Timeout Errors

**Error:** `TimeoutException: Message: ...`

**Solution:**
- Increase wait times in script
- Check internet connection
- Try with visible browser (`--no-headless`) to see what's happening

---

## 🔍 Debugging

### Run with Visible Browser

```bash
python3 tools/download_santa_ana_selenium.py \
  --years 2024 \
  --output "/Volumes/Samsung USB/City_extraction/Santa_Ana" \
  --no-headless
```

This lets you see:
- Browser navigation
- What's being clicked
- Any error messages in browser
- Download progress

### Check Download Directory

```bash
# Check what's in Downloads folder
ls -lh ~/Downloads/*.pdf

# Watch downloads in real-time
watch -n 1 ls -lh ~/Downloads
```

### Verify Output

```bash
# Count downloaded PDFs
find "/Volumes/Samsung USB/City_extraction/Santa_Ana/2024/pdfs" -name "*.pdf" | wc -l

# List recent downloads
ls -lt "/Volumes/Samsung USB/City_extraction/Santa_Ana/2024/pdfs/agenda/" | head -10
```

---

## 📋 Comparison: Manual vs Selenium

| Aspect | Manual + Organizer | Selenium |
|--------|-------------------|----------|
| **Setup Time** | None | 10-15 minutes (one-time) |
| **Time per Year** | 20-40 minutes | 6-12 minutes |
| **User Interaction** | Constant clicking | Run and walk away |
| **Error Handling** | Manual recovery | Automatic retry |
| **Meeting Filtering** | Manual selection | Automatic |
| **File Organization** | Requires organizer script | Automatic |
| **Browser Required** | Any browser | Chrome or Firefox |
| **Reliability** | Very high | High (depends on portal) |
| **Best For** | Small batches, one-time | Bulk downloads, multiple years |

### When to Use Each

**Manual + Organizer:**
- First time downloading
- Only need a few meetings
- Portal structure changed
- Want maximum control

**Selenium:**
- Downloading entire years
- Regular updates (e.g., monthly)
- Multiple years at once
- Want automation

---

## ✅ Best Practices

### Before Running

1. **Test with Dry Run:**
   ```bash
   python3 tools/download_santa_ana_selenium.py --years 2024 --dry-run
   ```

2. **Start with One Year:**
   - Test with current year first
   - Verify downloads work correctly
   - Then expand to multiple years

3. **Check Disk Space:**
   ```bash
   df -h "/Volumes/Samsung USB"
   ```

### During Run

1. **Monitor Progress:**
   - Script prints status for each meeting
   - Watch for error messages
   - Check download counts

2. **Don't Interrupt:**
   - Let it complete fully
   - Interrupting mid-download may leave temp files
   - Can resume - it skips existing files

### After Completion

1. **Verify Downloads:**
   ```bash
   # Count files
   find "/Volumes/Samsung USB/City_extraction/Santa_Ana/2024/pdfs" -name "*.pdf" | wc -l

   # Check file sizes
   du -sh "/Volumes/Samsung USB/City_extraction/Santa_Ana/2024/pdfs"/*
   ```

2. **Extract Text:**
   ```bash
   python3 tools/pdf_to_text_batch.py \
     "/Volumes/Samsung USB/City_extraction/Santa_Ana" \
     --years 2024
   ```

3. **Clean Up Downloads Folder:**
   ```bash
   # Remove any leftover PDFs from Downloads
   rm ~/Downloads/Meetings*.pdf
   ```

---

## 🔗 Related Documentation

- [MANUAL_DOWNLOAD_WORKFLOW.md](MANUAL_DOWNLOAD_WORKFLOW.md) - Alternative manual approach
- [EXTERNAL_STORAGE_STRUCTURE_GUIDE.md](EXTERNAL_STORAGE_STRUCTURE_GUIDE.md) - Storage organization
- [PDF_TO_TEXT_WORKFLOW.md](PDF_TO_TEXT_WORKFLOW.md) - Text extraction
- [STORAGE_AND_EXTRACTION_QUICKSTART.md](STORAGE_AND_EXTRACTION_QUICKSTART.md) - Quick reference

---

## 🆘 Getting Help

### Check Requirements

```bash
# Python version (need 3.7+)
python3 --version

# Selenium installed
pip list | grep selenium

# ChromeDriver installed
chromedriver --version
```

### Test Components

```bash
# Test Selenium import
python3 -c "from selenium import webdriver; print('Selenium OK')"

# Test ChromeDriver
chromedriver --version

# Test script help
python3 tools/download_santa_ana_selenium.py --help
```

### Report Issues

If the script isn't working:
1. Note the exact error message
2. Check which year/meeting caused the issue
3. Try with `--no-headless` to see browser
4. Verify portal is accessible in regular browser

---

**Last Updated:** 2025-11-24
**Script:** [tools/download_santa_ana_selenium.py](tools/download_santa_ana_selenium.py)
**Status:** Production-ready for automated downloads
