# Manual Download and Organization Workflow
**Purpose:** Practical guide for downloading Santa Ana meeting PDFs from the portal

**Created:** 2025-11-24
**Website:** https://santa-ana.primegov.com/public/portal

---

## 🎯 Overview

The Santa Ana PrimeGov portal uses dynamic JavaScript loading, making automated scraping difficult. This guide provides a **manual download workflow** with **automatic organization**.

### Workflow Summary

1. **Manual Download** → Download PDFs from portal using your browser
2. **Automatic Organization** → Script organizes files into proper structure
3. **Text Extraction** → Batch convert PDFs to text
4. **Vote Extraction** → Extract vote data (CSV workflow)

---

## 📥 Step 1: Manual Download from Portal

### Access the Portal

1. Visit: https://santa-ana.primegov.com/public/portal
2. You'll see a list of meetings with dates

###Filter Meetings

Look for these meeting types:
- **Regular City Council Meeting**
- **Regular City Council and Special Housing Authority Meeting**
- **Special City Council Meeting**

Skip other types (e.g., "Special Closed Session", "Workshop", "Public Hearing")

### Download Documents

For each meeting:

1. Click on the meeting title
2. Look for "Agenda" and "Minutes" links
3. Click each link to download the PDF
4. **Save to your Downloads folder** (or a dedicated folder)

**Note:** The browser will save files with names like:
- `Meetings4660Agenda_20241211013955955.pdf`
- `Meetings4660Minutes_20250624175240859.pdf`

**Don't worry about the filenames** - the organizer script will rename them properly!

### Download Tips

**Batch Downloading:**
- Open multiple meeting pages in tabs
- Download all agendas first, then all minutes
- Or download one meeting's complete set before moving to next

**Missing Documents:**
- Some meetings may not have minutes yet (future meetings)
- Some older meetings may only have one document type
- This is normal!

**File Size Warning:**
- Minutes PDFs can be 8-35 MB each
- Agendas are typically 1-4 MB each
- Ensure you have enough disk space

---

## 📁 Step 2: Organize Downloaded Files

### Using the Organizer Script

**Dry run first (see what would happen):**
```bash
python3 tools/organize_downloaded_pdfs.py \
  --source ~/Downloads \
  --output "/Volumes/Samsung USB/City_extraction/Santa_Ana" \
  --dry-run
```

**Actually organize files:**
```bash
python3 tools/organize_downloaded_pdfs.py \
  --source ~/Downloads \
  --output "/Volumes/Samsung USB/City_extraction/Santa_Ana"
```

### What the Script Does

**Automatically:**
1. ✅ Extracts date from filename
2. ✅ Identifies document type (agenda/minutes)
3. ✅ Identifies meeting type
4. ✅ Renames to standard format: `YYYYMMDD_type_meeting-name.pdf`
5. ✅ Places in correct year/type folder
6. ✅ Skips duplicates

**Example transformation:**
```
Input:  Meetings4660Minutes_20250624175240859.pdf
Output: /Volumes/.../2024/pdfs/minutes/20240624_minutes_regular_city_council_meeting.pdf
```

### Output Structure

```
/Volumes/Samsung USB/City_extraction/Santa_Ana/
├── 2024/
│   └── pdfs/
│       ├── agenda/
│       │   ├── 20240116_agenda_regular_city_council_meeting.pdf
│       │   ├── 20240220_agenda_regular_city_council_and_special_housing_authority.pdf
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

## 🔄 Step 3: Extract Text

After organizing PDFs, extract text:

```bash
python3 tools/pdf_to_text_batch.py \
  "/Volumes/Samsung USB/City_extraction/Santa_Ana" \
  --years 2024
```

This creates matching text files in `text/agenda/` and `text/minutes/` folders.

---

## ⚡ Complete Workflow Example

### Download One Year (e.g., 2024)

**1. Manual Download (15-30 minutes for ~24 meetings):**
```
Visit: https://santa-ana.primegov.com/public/portal
Filter to 2024
Download agendas and minutes for all Regular/Special City Council meetings
Save to ~/Downloads
```

**2. Organize (1 minute):**
```bash
python3 tools/organize_downloaded_pdfs.py \
  --source ~/Downloads \
  --output "/Volumes/Samsung USB/City_extraction/Santa_Ana"
```

**3. Extract Text (5-10 minutes for 24 meetings):**
```bash
python3 tools/pdf_to_text_batch.py \
  "/Volumes/Samsung USB/City_extraction/Santa_Ana" \
  --years 2024
```

**4. Start Extraction Work:**
```bash
# Copy files to project
./tools/copy_work_files.sh 2024 20240220

# Extract votes to CSV
# (Manual process - see CSV_EXTRACTION_WORKFLOW.md)
```

---

## 📝 Organizing Tips

### Rename Before Organizing (Optional)

If you want to rename files as you download, use this format:
```
YYYYMMDD_agenda_description.pdf
YYYYMMDD_minutes_description.pdf

Examples:
20240220_agenda_regular_city_council_meeting.pdf
20240220_minutes_regular_city_council_meeting.pdf
```

If you use this format, the organizer will still work and just move them to the correct folders.

### Batch Organization

You can download PDFs over several sessions and organize them all at once:

```bash
# Download meetings 1-10 on Day 1
# Download meetings 11-20 on Day 2
# Download meetings 21-30 on Day 3

# Then organize all at once:
python3 tools/organize_downloaded_pdfs.py --source ~/Downloads ...
```

### Verify Organization

After organizing, check the structure:

```bash
# Count PDFs organized
find "/Volumes/Samsung USB/City_extraction/Santa_Ana/2024/pdfs" -name "*.pdf" | wc -l

# List agenda files
ls -lh "/Volumes/Samsung USB/City_extraction/Santa_Ana/2024/pdfs/agenda/"

# List minutes files
ls -lh "/Volumes/Samsung USB/City_extraction/Santa_Ana/2024/pdfs/minutes/"
```

---

## 🔍 Troubleshooting

### Organizer can't extract date

**Issue:** `Could not extract date from filename`

**Cause:** Filename doesn't contain recognizable date pattern

**Solution:** Rename manually to include date in format `YYYYMMDD` or `YYYY-MM-DD`:
```bash
mv "problem_file.pdf" "20240220_agenda_city_council.pdf"
```

### Organizer can't determine document type

**Issue:** `Could not determine document type (agenda/minutes)`

**Cause:** Filename doesn't contain "agenda" or "minutes"

**Solution:** Rename to include document type:
```bash
mv "20240220_city_council.pdf" "20240220_agenda_city_council.pdf"
```

### File already exists at destination

**Issue:** `File already exists at destination`

**Cause:** You already organized this file

**Solution:** This is normal! The organizer skips duplicates. You can safely delete the source file.

### Wrong year folder

**Issue:** File organized into wrong year

**Cause:** Date extraction picked wrong date from filename

**Solution:** Move file manually to correct year folder:
```bash
mv ".../2025/pdfs/minutes/file.pdf" ".../2024/pdfs/minutes/file.pdf"
```

---

## 📊 Expected Results

### For One Complete Year (24-30 meetings)

**PDFs Downloaded:**
- ~24-30 agenda PDFs (~60-120 MB total)
- ~24-30 minutes PDFs (~200-800 MB total)
- Total: ~260-920 MB

**Text Files (after extraction):**
- ~24-30 agenda text files (~2-4 MB total)
- ~24-30 minutes text files (~3-6 MB total)
- Total: ~5-10 MB

**Time Investment:**
- Manual download: 15-30 minutes
- Organization: 1 minute
- Text extraction: 5-10 minutes
- **Total: 20-40 minutes per year**

---

## 💡 Pro Tips

### Use Browser Download Manager

Modern browsers track downloads:
- **Chrome:** `chrome://downloads/`
- **Safari:** Downloads folder icon in toolbar
- **Firefox:** Downloads arrow in toolbar

This helps track which files you've already downloaded.

### Create Download Checklist

Track progress by year and meeting type:

```
2024 Downloads Progress:
□ January - Regular City Council
□ January - Special Housing Authority
□ February - Regular City Council
...

Total: 0/24 complete
```

### Download in Chronological Order

Start with most recent year and work backwards:
1. 2024 (most recent, most useful)
2. 2023
3. 2022
4. etc.

This ensures you get the most valuable data first.

### Dedicate a Downloads Folder

Create a dedicated folder for Santa Ana documents:

```bash
mkdir ~/Documents/SantaAna_Downloads
```

Then use that as your `--source` in the organizer:

```bash
python3 tools/organize_downloaded_pdfs.py \
  --source ~/Documents/SantaAna_Downloads \
  --output "/Volumes/Samsung USB/City_extraction/Santa_Ana"
```

---

## 🔗 Related Documentation

- [EXTERNAL_STORAGE_STRUCTURE_GUIDE.md](EXTERNAL_STORAGE_STRUCTURE_GUIDE.md) - Storage organization
- [PDF_TO_TEXT_WORKFLOW.md](PDF_TO_TEXT_WORKFLOW.md) - Text extraction
- [CSV_EXTRACTION_WORKFLOW.md](CSV_EXTRACTION_WORKFLOW.md) - Vote extraction
- [STORAGE_AND_EXTRACTION_QUICKSTART.md](STORAGE_AND_EXTRACTION_QUICKSTART.md) - Complete workflow

---

## ✅ Checklist: Download Complete Year

- [ ] Visit Santa Ana PrimeGov portal
- [ ] Filter to target year
- [ ] Download all agendas for Regular/Special City Council meetings
- [ ] Download all minutes for Regular/Special City Council meetings
- [ ] Run organizer script (dry run first!)
- [ ] Verify PDFs organized correctly
- [ ] Run text extraction
- [ ] Verify text files created
- [ ] Clean up Downloads folder
- [ ] Update your download progress tracking

---

**Last Updated:** 2025-11-24
**Tools:** [tools/organize_downloaded_pdfs.py](tools/organize_downloaded_pdfs.py)
