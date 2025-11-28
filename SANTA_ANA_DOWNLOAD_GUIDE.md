# Santa Ana Meeting Download Guide
**Purpose:** Download agendas and minutes from Santa Ana PrimeGov portal

**Created:** 2025-11-24
**Website:** https://santa-ana.primegov.com/public/portal

---

## 🎯 Overview

This guide helps you download meeting documents (agendas and minutes) from the Santa Ana city council portal and automatically organize them into the recommended folder structure.

### What Gets Downloaded

**Meeting Types (Filtered):**
- Regular City Council Meeting
- Regular City Council and Special Housing Authority Meeting
- Special City Council Meeting

**Document Types:**
- Agendas (PDF)
- Minutes (PDF)

**File Naming Format:**
```
YYYYMMDD_type_meeting-name.pdf

Examples:
20240220_agenda_regular_city_council_meeting.pdf
20240220_minutes_regular_city_council_and_special_housing_authority.pdf
```

---

## 🚀 Quick Start

### Basic Usage

**Download all 2024 meetings (dry run first):**
```bash
python3 tools/download_santa_ana_meetings.py \
  --output-dir "/Volumes/Samsung USB/City_extraction/Santa_Ana" \
  --years 2024 \
  --dry-run
```

**Actually download (remove --dry-run):**
```bash
python3 tools/download_santa_ana_meetings.py \
  --output-dir "/Volumes/Samsung USB/City_extraction/Santa_Ana" \
  --years 2024
```

### Download Multiple Years

```bash
python3 tools/download_santa_ana_meetings.py \
  --output-dir "/Volumes/Samsung USB/City_extraction/Santa_Ana" \
  --years 2024 2023 2022 2021
```

### Download Only Agendas or Minutes

**Agendas only:**
```bash
python3 tools/download_santa_ana_meetings.py \
  --output-dir "/Volumes/Samsung USB/City_extraction/Santa_Ana" \
  --years 2024 \
  --types agenda
```

**Minutes only:**
```bash
python3 tools/download_santa_ana_meetings.py \
  --output-dir "/Volumes/Samsung USB/City_extraction/Santa_Ana" \
  --years 2024 \
  --types minutes
```

---

## 📁 Output Structure

Files are automatically organized into the recommended structure:

```
/Volumes/Samsung USB/City_extraction/Santa_Ana/
├── 2024/
│   └── pdfs/
│       ├── agenda/
│       │   ├── 20240116_agenda_regular_city_council_meeting.pdf
│       │   ├── 20240220_agenda_regular_city_council_meeting.pdf
│       │   └── ...
│       └── minutes/
│           ├── 20240116_minutes_regular_city_council_meeting.pdf
│           ├── 20240220_minutes_regular_city_council_meeting.pdf
│           └── ...
├── 2023/
│   └── pdfs/
│       ├── agenda/
│       └── minutes/
└── ...
```

---

## ⚙️ Command-Line Options

### Required Options

| Option | Description | Example |
|--------|-------------|---------|
| `--output-dir` | Base directory for downloads | `/Volumes/Samsung USB/City_extraction/Santa_Ana` |

### Optional Options

| Option | Description | Default |
|--------|-------------|---------|
| `--years` | Specific years to download | All available |
| `--types` | Document types (agenda, minutes) | Both |
| `--meeting-types` | Custom meeting type filter | Regular/Special City Council |
| `--delay` | Delay between downloads (seconds) | 2.0 |
| `--dry-run` | Show what would download without downloading | False |

---

## 🔍 Meeting Type Filtering

### Default Meeting Types (Included)

The script automatically filters for these meeting types:
1. **Regular City Council Meeting**
2. **Regular City Council and Special Housing Authority Meeting**
3. **Special City Council Meeting**

All other meeting types (e.g., "Special Closed Session", "Public Hearing", "Workshop") are automatically filtered out.

### Custom Meeting Type Filter

To include different meeting types:

```bash
python3 tools/download_santa_ana_meetings.py \
  --output-dir "/Volumes/Samsung USB/City_extraction/Santa_Ana" \
  --years 2024 \
  --meeting-types "Regular City Council Meeting" "Public Hearing"
```

---

## 📊 Features

### Automatic Features

✅ **Duplicate Detection**: Skips files that already exist
✅ **Year Organization**: Automatically sorts into year folders
✅ **Type Separation**: Agendas and minutes in separate folders
✅ **Meeting Filtering**: Only downloads specified meeting types
✅ **Progress Reporting**: Shows download progress and statistics
✅ **Error Handling**: Gracefully handles missing documents and errors
✅ **Rate Limiting**: Delays between downloads to be respectful

### Download Statistics

After completion, you'll see a summary like:

```
📊 Download Summary
============================================================
Meetings found: 45
Meetings filtered out: 12
Meetings processed: 33
Agendas downloaded: 28
Minutes downloaded: 31
Skipped (already exist): 4
Errors: 0

✅ Complete!
```

---

## 🔄 Workflow Integration

### Step 1: Download PDFs

```bash
# Download all 2024 meetings
python3 tools/download_santa_ana_meetings.py \
  --output-dir "/Volumes/Samsung USB/City_extraction/Santa_Ana" \
  --years 2024
```

### Step 2: Extract Text

```bash
# Convert PDFs to text
python3 tools/pdf_to_text_batch.py \
  "/Volumes/Samsung USB/City_extraction/Santa_Ana" \
  --years 2024
```

### Step 3: Copy to Project

```bash
# Copy specific meeting to project for work
./tools/copy_work_files.sh 2024 20240220
```

### Step 4: Extract Votes

Manual CSV extraction or AI extraction (see CSV_EXTRACTION_WORKFLOW.md)

---

## 🛠️ Troubleshooting

### Issue: "No meetings found"

**Possible Causes:**
- Portal API changed or is down
- Network connectivity issues
- Year filter too restrictive

**Solutions:**
1. Try without year filter to see all meetings
2. Check https://santa-ana.primegov.com/public/portal in browser
3. Check network connection

### Issue: "Error getting CSRF token"

**Solutions:**
1. Check if website is accessible
2. Try again (temporary network issue)
3. Update script if portal structure changed

### Issue: Downloads are slow

**Solutions:**
1. Reduce delay: `--delay 1.0` (but be respectful!)
2. Download one year at a time
3. Use `--types agenda` or `--types minutes` to download one type at a time

### Issue: Some documents missing

**This is normal!**
- Not all meetings have both agenda and minutes
- Some meetings may not be published yet
- Check the portal manually to verify

The script will report:
```
⏭️  No agenda found
✅ Downloaded minutes
```

### Issue: Permission denied

**Solutions:**
1. Check external drive is mounted: `ls /Volumes/`
2. Check write permissions on output directory
3. Create directory manually first

---

## 📝 Examples

### Download Current Year Only

```bash
python3 tools/download_santa_ana_meetings.py \
  --output-dir "/Volumes/Samsung USB/City_extraction/Santa_Ana" \
  --years 2024
```

### Download Historical Data (Multiple Years)

```bash
python3 tools/download_santa_ana_meetings.py \
  --output-dir "/Volumes/Samsung USB/City_extraction/Santa_Ana" \
  --years 2024 2023 2022 2021 2020 2019
```

### Resume Interrupted Download

Just run the same command again - it will skip files that already exist:

```bash
python3 tools/download_santa_ana_meetings.py \
  --output-dir "/Volumes/Samsung USB/City_extraction/Santa_Ana" \
  --years 2024
```

### Test Before Downloading (Dry Run)

```bash
python3 tools/download_santa_ana_meetings.py \
  --output-dir "/Volumes/Samsung USB/City_extraction/Santa_Ana" \
  --years 2024 \
  --dry-run
```

This will show you:
- How many meetings will be downloaded
- What they'll be named
- Where they'll be saved
- WITHOUT actually downloading anything

---

## ⚠️ Important Notes

### Be Respectful

1. **Rate Limiting**: Default 2-second delay between downloads
2. **Don't Spam**: Don't run multiple instances simultaneously
3. **Off-Peak Hours**: Consider running during off-peak hours for large batches

### Portal Limitations

1. **API Access**: This script relies on the portal's public API
2. **Changes**: Portal structure may change, requiring script updates
3. **Availability**: Some historical documents may not be available

### File Sizes

- **Agendas**: Typically 1-4 MB each
- **Minutes**: Typically 8-35 MB each
- **Estimate**: ~30-50 MB per meeting (both documents)
- **Year Total**: ~1-2 GB for 24-30 meetings per year

---

## 🔗 Related Documentation

- [EXTERNAL_STORAGE_STRUCTURE_GUIDE.md](EXTERNAL_STORAGE_STRUCTURE_GUIDE.md) - Storage organization
- [PDF_TO_TEXT_WORKFLOW.md](PDF_TO_TEXT_WORKFLOW.md) - Text extraction after download
- [CSV_EXTRACTION_WORKFLOW.md](CSV_EXTRACTION_WORKFLOW.md) - Vote extraction process
- [STORAGE_AND_EXTRACTION_QUICKSTART.md](STORAGE_AND_EXTRACTION_QUICKSTART.md) - Complete workflow

---

## 🆘 Getting Help

### Check Portal Manually

Visit: https://santa-ana.primegov.com/public/portal

Verify:
- Meetings are visible in browser
- Documents are available for download
- Dates and meeting types match expectations

### Script Issues

If the script isn't working:
1. Check Python version: `python3 --version` (need 3.7+)
2. Check dependencies: `pip3 list | grep -E "(requests|beautifulsoup4)"`
3. Test with dry run first: `--dry-run`
4. Check output directory permissions

### Report Issues

If you find bugs or need updates:
1. Note the specific error message
2. Check what year/meeting caused the issue
3. Verify the portal is accessible in browser
4. Check if portal structure has changed

---

**Last Updated:** 2025-11-24
**Script:** [tools/download_santa_ana_meetings.py](tools/download_santa_ana_meetings.py)
