# Storage and Extraction Quick Start Guide
**Purpose:** Fast reference for PDF storage, text extraction, and workflow

**Created:** 2025-11-24

---

## 🎯 Quick Summary

**Storage Strategy:**
- ✅ PDFs → External drive (large files, 8-35 MB each)
- ✅ Text → External drive (small files, 40-150 KB each)
- ✅ CSV/JSON → Project repo (actively edited)
- ✅ Source docs → Project repo (only current work, copied from external)

**Space Savings:** 99.94% reduction in repo size

---

## 📁 Directory Structure

### External Storage (Samsung USB)
```
/Volumes/Samsung USB/City_extraction/Santa_Ana/
├── 2024/
│   ├── pdfs/
│   │   ├── agenda/
│   │   └── minutes/
│   ├── text/
│   │   ├── agenda/
│   │   └── minutes/
│   └── extractions/        (archived CSV/JSON)
├── 2021/  (same structure)
└── 2019/  (same structure)
```

### Project Repository
```
extractors/santa_ana/
└── 2024/
    ├── training_data/
    │   ├── santa_ana_vote_extraction_2024.csv
    │   └── santa_ana_vote_extraction_2024.json
    └── source_documents/   (only current work)
        ├── 20240220_minutes.txt  (copied)
        └── 20240220_agenda.txt   (copied)
```

---

## 🚀 Common Tasks

### 1. Download and Organize New PDFs

```bash
# Save directly to organized structure
/Volumes/Samsung USB/City_extraction/Santa_Ana/2024/pdfs/minutes/20240220_minutes_regular_city_council_meeting.pdf
/Volumes/Samsung USB/City_extraction/Santa_Ana/2024/pdfs/agenda/20240220_agenda_regular_city_council_meeting.pdf
```

### 2. Extract Text from PDFs

**Extract all 2024 PDFs:**
```bash
python3 tools/pdf_to_text_batch.py \
  "/Volumes/Samsung USB/City_extraction/Santa_Ana" \
  --years 2024
```

**Dry run first (see what would happen):**
```bash
python3 tools/pdf_to_text_batch.py \
  "/Volumes/Samsung USB/City_extraction/Santa_Ana" \
  --years 2024 --dry-run
```

**Extract all years:**
```bash
python3 tools/pdf_to_text_batch.py \
  "/Volumes/Samsung USB/City_extraction/Santa_Ana"
```

### 3. Copy Files to Project for Work

```bash
# Copy specific meeting's text files
./tools/copy_work_files.sh 2024 20240220

# This copies both agenda and minutes (if found) to:
# extractors/santa_ana/2024/source_documents/
```

### 4. Manual Vote Extraction

1. Open the copied text file
2. Extract votes into CSV spreadsheet
3. Save CSV: `extractors/santa_ana/2024/training_data/santa_ana_vote_extraction_2024.csv`

### 5. Convert CSV to JSON

```bash
python3 tools/csv_to_json.py \
  extractors/santa_ana/2024/training_data/santa_ana_vote_extraction_2024.csv
```

### 6. Archive Completed Work

```bash
# Archive extraction data back to external storage
./tools/archive_work_files.sh 2024

# This backs up CSV, JSON, AI results, and comparisons to:
# /Volumes/Samsung USB/City_extraction/Santa_Ana/2024/extractions/
```

---

## 🔧 Setup (One-Time)

### Install PDF Extraction Tool

**macOS:**
```bash
brew install poppler
```

**Ubuntu/Debian:**
```bash
sudo apt-get install poppler-utils
```

**Verify:**
```bash
pdftotext -v
```

### Alternative: Python Libraries

```bash
# If pdftotext not available, install Python alternatives
pip install PyPDF2 pdfplumber
```

---

## 📋 File Naming Convention

**Format:**
```
YYYYMMDD_type_description.ext
```

**Examples:**
- ✅ `20240220_agenda_regular_city_council_meeting.pdf`
- ✅ `20240220_minutes_regular_city_council_meeting.txt`
- ✅ `20240305_agenda_special_housing_authority.pdf`

**Components:**
- `YYYYMMDD` - Date (sortable)
- `type` - agenda or minutes
- `description` - Meeting type (lowercase, underscores)
- `ext` - pdf or txt

---

## 🔍 Checking Status

### Check What PDFs Need Text Extraction

```bash
# Count PDFs vs text files
echo "2024 PDFs: $(find "/Volumes/Samsung USB/City_extraction/Santa_Ana/2024/pdfs" -name "*.pdf" | wc -l)"
echo "2024 Text: $(find "/Volumes/Samsung USB/City_extraction/Santa_Ana/2024/text" -name "*.txt" | wc -l)"
```

### Check What's in Project

```bash
ls -lh extractors/santa_ana/2024/source_documents/
ls -lh extractors/santa_ana/2024/training_data/
```

### Check External Drive Space

```bash
du -sh "/Volumes/Samsung USB/City_extraction/Santa_Ana"/*
```

---

## 📊 Typical Workflow

```
1. Download PDFs → Save to external /YYYY/pdfs/
                    ↓
2. Extract Text  → Batch convert to external /YYYY/text/
                    ↓
3. Copy to Work  → Copy needed files to project source_documents/
                    ↓
4. Extract Votes → Manual CSV extraction from text files
                    ↓
5. Convert       → CSV → JSON conversion
                    ↓
6. AI Extract    → (Optional) Run AI extractor
                    ↓
7. Compare       → (Optional) Compare manual vs AI
                    ↓
8. Archive       → Copy results back to external /YYYY/extractions/
                    ↓
9. Clean         → Remove source_documents from project (optional)
```

---

## 🛠️ Tool Reference

| Tool | Purpose | Location |
|------|---------|----------|
| `pdf_to_text_batch.py` | Batch PDF→text conversion | `tools/` |
| `csv_to_json.py` | Convert CSV to JSON | `tools/` |
| `copy_work_files.sh` | Copy files from external to project | `tools/` |
| `archive_work_files.sh` | Archive results to external | `tools/` |

---

## ⚠️ Important Notes

1. **External Drive Required**: All scripts expect Samsung USB at `/Volumes/Samsung USB/`
2. **Backup**: PDFs and text on external drive are your primary archive
3. **Git Ignore**: PDFs are excluded from git automatically
4. **Space**: Project stays small (~1-2 MB vs 400+ MB with PDFs)
5. **Flexibility**: Can work on any year without loading all years

---

## 📚 Detailed Documentation

- [EXTERNAL_STORAGE_STRUCTURE_GUIDE.md](EXTERNAL_STORAGE_STRUCTURE_GUIDE.md) - Full storage organization
- [PDF_TO_TEXT_WORKFLOW.md](PDF_TO_TEXT_WORKFLOW.md) - Detailed extraction guide
- [CSV_EXTRACTION_WORKFLOW.md](CSV_EXTRACTION_WORKFLOW.md) - Vote extraction process

---

## 🆘 Troubleshooting

### External drive not found
```bash
# Check if mounted
ls /Volumes/

# If "Samsung USB" not listed, plug in drive
```

### pdftotext not found
```bash
# Install poppler
brew install poppler

# Or use Python fallback
python3 tools/pdf_to_text_batch.py --method pypdf2 ...
```

### Text extraction failed
```bash
# Check PDF is readable
file "/path/to/file.pdf"

# Try different extraction method
python3 tools/pdf_to_text_batch.py --method pdfplumber ...
```

### Can't find text files
```bash
# Check if extraction was run
ls "/Volumes/Samsung USB/City_extraction/Santa_Ana/2024/text/minutes/"

# If empty, run extraction
python3 tools/pdf_to_text_batch.py ...
```

---

**Last Updated:** 2025-11-24
