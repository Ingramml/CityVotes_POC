# External Storage Structure Guide
**Purpose:** Optimal organization for PDFs and extracted text files on external storage (Samsung USB)

**Created:** 2025-11-24
**Status:** Recommended structure for space-efficient archival storage

---

## 🎯 Design Goals

1. **Space Efficiency**: Keep large PDFs on external storage, not in git repo
2. **Easy Navigation**: Find files by city, year, and date quickly
3. **Clear File Naming**: Understand what each file is without opening it
4. **Parallel Structure**: Match internal project structure for consistency
5. **Future-Proof**: Easily add more cities, years, and file types

---

## 📁 Recommended Storage Structure

### Current Structure Analysis

**What you have now:**
```
/Volumes/Samsung USB/City_extraction/Santa_Ana/
├── PDF/
│   ├── 2024/           # PDFs organized by year ✅ GOOD
│   ├── 2023/
│   ├── 2021/
│   └── text_files/     # ⚠️ All years mixed together
└── [other files]
```

**Issues with current structure:**
1. ❌ Text files are all mixed in one folder (hard to find specific year)
2. ❌ PDFs in root folder (2024 agendas) should be in year folders
3. ❌ Doesn't match internal project structure

---

## ✅ Recommended Structure (Option A: Mirrored)

**Mirrors your internal project structure** for consistency:

```
/Volumes/Samsung USB/City_extraction/Santa_Ana/
├── 2014/
│   ├── pdfs/
│   │   ├── agenda/
│   │   │   └── 20141021_agenda_city_council_meeting.pdf
│   │   └── minutes/
│   │       └── 20141021_minutes_city_council_meeting.pdf
│   └── text/
│       ├── agenda/
│       │   └── 20141021_agenda_city_council_meeting.txt
│       └── minutes/
│           └── 20141021_minutes_city_council_meeting.txt
│
├── 2019/
│   ├── pdfs/
│   │   ├── agenda/
│   │   └── minutes/
│   └── text/
│       ├── agenda/
│       └── minutes/
│
├── 2021/
│   ├── pdfs/
│   │   ├── agenda/
│   │   └── minutes/
│   └── text/
│       ├── agenda/
│       └── minutes/
│
├── 2024/
│   ├── pdfs/
│   │   ├── agenda/
│   │   │   ├── 20240112_agenda_regular_city_council_meeting.pdf
│   │   │   ├── 20240214_agenda_regular_city_council_meeting.pdf
│   │   │   └── ...
│   │   └── minutes/
│   │       ├── 20240116_minutes_regular_city_council_meeting.pdf
│   │       ├── 20240220_minutes_regular_city_council_meeting.pdf
│   │       └── ...
│   └── text/
│       ├── agenda/
│       │   ├── 20240112_agenda_regular_city_council_meeting.txt
│       │   └── ...
│       └── minutes/
│           ├── 20240116_minutes_regular_city_council_meeting.txt
│           └── ...
│
└── README.md  # Documentation of structure
```

**Benefits:**
- ✅ Matches internal project: `extractors/santa_ana/YYYY/source_documents/`
- ✅ Easy year navigation
- ✅ Clear separation of agenda vs minutes
- ✅ Text files grouped with their year
- ✅ Can symlink specific years into project when needed

---

## 🔄 Alternative Structure (Option B: Centralized Text)

**If you prefer keeping text files together** (since they're small):

```
/Volumes/Samsung USB/City_extraction/Santa_Ana/
├── pdfs/
│   ├── 2014/
│   │   ├── agenda/
│   │   └── minutes/
│   ├── 2019/
│   │   ├── agenda/
│   │   └── minutes/
│   ├── 2021/
│   │   ├── agenda/
│   │   └── minutes/
│   └── 2024/
│       ├── agenda/
│       └── minutes/
│
└── text/
    ├── 2014/
    │   ├── agenda/
    │   └── minutes/
    ├── 2019/
    │   ├── agenda/
    │   └── minutes/
    ├── 2021/
    │   ├── agenda/
    │   └── minutes/
    └── 2024/
        ├── agenda/
        └── minutes/
```

**Benefits:**
- ✅ PDFs separated from text (clear size boundary)
- ✅ All text files in one tree
- ✅ Still organized by year

**Drawbacks:**
- ⚠️ Doesn't mirror project structure
- ⚠️ Need to navigate two trees (pdfs/ and text/)

---

## 📝 File Naming Convention

**Standard format:**
```
YYYYMMDD_type_meeting-description.ext

Examples:
20240220_agenda_regular_city_council_meeting.pdf
20240220_minutes_regular_city_council_meeting.txt
20240305_agenda_special_housing_authority_meeting.pdf
```

**Components:**
- `YYYYMMDD`: Date (sortable, searchable)
- `type`: agenda or minutes
- `meeting-description`: Short description (lowercase, underscores)
- `ext`: pdf or txt

**What you currently have (examples):**
```
✅ GOOD: 20240220_minutes_regular_city_council_and_special_housing_authority.pdf
✅ GOOD: 20240305_minutes_regular_city_council_meeting.txt
❌ BAD:  Meetings4406Agenda_20240112175420068.pdf  (unclear prefix, timestamp suffix)
```

---

## 🔧 Migration Script

### Reorganize Current Files into Option A Structure

**Step 1: Create new structure**
```bash
#!/bin/bash
# Run from: /Volumes/Samsung USB/City_extraction/Santa_Ana/

YEARS=(2014 2015 2016 2017 2018 2019 2021 2022 2023 2024 2025)

for year in "${YEARS[@]}"; do
    mkdir -p "$year/pdfs/agenda"
    mkdir -p "$year/pdfs/minutes"
    mkdir -p "$year/text/agenda"
    mkdir -p "$year/text/minutes"
done

echo "✅ Directory structure created"
```

**Step 2: Move PDFs from year folders**
```bash
#!/bin/bash
# Move PDFs from PDF/YYYY/ to YYYY/pdfs/

for year in 2014 2015 2016 2017 2018 2019 2021 2022 2023 2024 2025; do
    if [ -d "PDF/$year" ]; then
        echo "Processing $year PDFs..."

        # Move agenda PDFs
        find "PDF/$year" -name "*agenda*" -type f -exec mv {} "$year/pdfs/agenda/" \;

        # Move minutes PDFs
        find "PDF/$year" -name "*minutes*" -type f -exec mv {} "$year/pdfs/minutes/" \;

        echo "  ✅ $year PDFs organized"
    fi
done
```

**Step 3: Move text files from text_files/**
```bash
#!/bin/bash
# Organize text files by year

if [ -d "PDF/text_files" ]; then
    echo "Processing text files..."

    for file in PDF/text_files/*.txt; do
        filename=$(basename "$file")

        # Extract year from filename (YYYYMMDD pattern)
        year=$(echo "$filename" | grep -oE "^[0-9]{4}")

        if [ ! -z "$year" ]; then
            # Determine if agenda or minutes
            if [[ "$filename" == *"agenda"* ]]; then
                mv "$file" "$year/text/agenda/"
                echo "  → $filename → $year/text/agenda/"
            elif [[ "$filename" == *"minutes"* ]]; then
                mv "$file" "$year/text/minutes/"
                echo "  → $filename → $year/text/minutes/"
            else
                echo "  ⚠️  Unknown type: $filename"
            fi
        else
            echo "  ⚠️  No year found: $filename"
        fi
    done

    echo "✅ Text files organized"
fi
```

**Step 4: Move loose PDFs from root**
```bash
#!/bin/bash
# Move PDFs from PDF/ root to appropriate year folders

cd PDF

for file in *.pdf; do
    # Skip if already processed
    if [ "$file" == "*.pdf" ]; then
        continue
    fi

    # Extract date from Meetings format
    if [[ "$file" =~ Meetings[0-9]+Agenda_([0-9]{8}) ]]; then
        date="${BASH_REMATCH[1]}"
        year="${date:0:4}"

        # Create better filename
        month="${date:4:2}"
        day="${date:6:2}"

        newname="${year}${month}${day}_agenda_regular_city_council_meeting.pdf"

        mv "$file" "../$year/pdfs/agenda/$newname"
        echo "  → $file → $year/pdfs/agenda/$newname"
    fi
done

echo "✅ Root PDFs organized"
```

---

## 📊 Space Analysis

**Typical file sizes:**
- PDF (minutes): 8-35 MB each
- PDF (agenda): 1-4 MB each
- TXT (extracted): 40-150 KB each (1-2% of PDF size)

**Storage estimates:**

| Content | Files | Size per Year |
|---------|-------|---------------|
| PDFs (24 meetings/year) | ~48 files | ~300-500 MB |
| Text files | ~48 files | ~5-10 MB |

**For 10 years of data:**
- PDFs: ~3-5 GB
- Text files: ~50-100 MB

**Recommendation:**
- ✅ Keep PDFs on external storage
- ✅ Keep text files on external storage too (but could copy to project)
- ✅ Copy only specific text files to project as needed for training

---

## 🔗 Linking to Project

**Workflow for using external files in project:**

### Option 1: Copy Specific Files (Recommended)
```bash
# Copy just the files you need for current work
cp "/Volumes/Samsung USB/City_extraction/Santa_Ana/2024/text/minutes/20240220_minutes*.txt" \
   extractors/santa_ana/2024/source_documents/
```

### Option 2: Symlink Entire Year
```bash
# Link entire year folder
ln -s "/Volumes/Samsung USB/City_extraction/Santa_Ana/2024" \
      extractors/santa_ana/2024/external_docs
```

### Option 3: Mount-Based Access
```python
# In your Python scripts, check if external drive is mounted
import os
from pathlib import Path

EXTERNAL_DRIVE = Path("/Volumes/Samsung USB/City_extraction/Santa_Ana")

def get_source_file(year, meeting_date, file_type="minutes"):
    """Get path to source file, checking external drive first"""

    # Try external drive
    external_path = EXTERNAL_DRIVE / str(year) / "text" / file_type / f"{meeting_date}_{file_type}_*.txt"
    matches = list(external_path.parent.glob(external_path.name))
    if matches:
        return matches[0]

    # Fall back to local copy
    local_path = Path(f"extractors/santa_ana/{year}/source_documents/{meeting_date}_{file_type}_*.txt")
    matches = list(local_path.parent.glob(local_path.name))
    if matches:
        return matches[0]

    return None
```

---

## 🎯 Recommended Action Plan

### Immediate (Today)
1. **Create migration script** using templates above
2. **Test on one year** (e.g., 2024) to verify structure works
3. **Document any filename issues** that need manual fixing

### Short-term (This Week)
1. **Run full migration** to reorganize all files
2. **Update README** on external drive explaining structure
3. **Create helper scripts** for copying files to project
4. **Test workflow** with one complete extraction cycle

### Long-term
1. **Automate PDF downloads** directly to correct folders
2. **Automate text extraction** saving to correct folders
3. **Sync scripts** to copy needed files to project

---

## 📋 Quick Reference

**Find all 2024 minutes (PDF):**
```bash
ls /Volumes/Samsung\ USB/City_extraction/Santa_Ana/2024/pdfs/minutes/
```

**Find all 2024 minutes (text):**
```bash
ls /Volumes/Samsung\ USB/City_extraction/Santa_Ana/2024/text/minutes/
```

**Copy 2024 text files to project:**
```bash
cp /Volumes/Samsung\ USB/City_extraction/Santa_Ana/2024/text/minutes/*.txt \
   extractors/santa_ana/2024/source_documents/
```

**Check file count per year:**
```bash
for year in 2014 2019 2021 2024; do
    count=$(find "$year" -name "*.pdf" | wc -l)
    echo "$year: $count PDFs"
done
```

---

## ⚠️ Important Notes

1. **Backup First**: Before running migration, backup current structure
2. **Test Scripts**: Run on a single year first to verify correctness
3. **.gitignore**: Ensure PDFs are excluded from git in project
4. **Drive Name**: Scripts assume "Samsung USB" - update if different
5. **Filename Cleanup**: Some files may need manual renaming (Meetings* format)

---

## 📚 See Also

- [CSV_EXTRACTION_WORKFLOW.md](CSV_EXTRACTION_WORKFLOW.md) - How CSV workflow uses these files
- [extractors/README.md](extractors/README.md) - Project directory structure
- [Documents/context.md](Documents/context.md) - Current project status
