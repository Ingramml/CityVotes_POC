# Extractors - City-Year Organization

**Status:** Ready for CSV data
**Structure:** Empty and waiting for your extracted vote data

---

## 📁 Directory Structure

```
extractors/
├── santa_ana/
│   ├── 2014/  (empty - ready for CSV)
│   ├── 2019/  (empty - ready for CSV)
│   ├── 2021/  (empty - ready for CSV)
│   └── 2024/  (empty - ready for CSV)
└── shared/     (common utilities)
```

All folders are empty and ready to receive:
- CSV files with extracted vote data
- Source documents (agenda/minutes text files)
- AI extraction results
- Comparison reports

---

## 🎯 Workflow with CSV Data

### Step 1: You Provide CSV Per Year

Place your CSV file in the appropriate year folder:
```bash
# Example structure after you add CSV
extractors/santa_ana/2021/training_data/2021_votes.csv
```

### Step 2: Convert CSV to JSON

```bash
python tools/csv_to_json.py extractors/santa_ana/2021/training_data/2021_votes.csv
```

This creates:
```
extractors/santa_ana/2021/training_data/2021_votes.json
```

### Step 3: Add Source Documents

Copy the original meeting documents:
```bash
cp /path/to/2021_minutes.txt extractors/santa_ana/2021/source_documents/
```

### Step 4: Run AI Extraction

```bash
python run_santa_ana_extraction.py \
    --minutes extractors/santa_ana/2021/source_documents/2021_minutes.txt \
    --output extractors/santa_ana/2021/ai_results/2021_ai.json
```

### Step 5: Compare & Improve

```bash
python compare_extractions.py \
    extractors/santa_ana/2021/training_data/2021_votes.json \
    extractors/santa_ana/2021/source_documents/2021_agenda.txt \
    extractors/santa_ana/2021/source_documents/2021_minutes.txt
```

---

## 📊 Expected CSV Format

### Option A: Separate Member Columns (Recommended)

```csv
meeting_date,agenda_item,item_title,outcome,Amezcua,Sarmiento,Bacerra,Hernandez,Phan,Vazquez,Penaloza
2021-10-05,7.1,Budget Amendment,Pass,Aye,Aye,Nay,Aye,Aye,Nay,Aye
2021-10-05,8.2,Zoning Change,Pass,Aye,Aye,Nay,Aye,Aye,Aye,Aye
```

**Benefits:**
- Easy to create in Excel/Google Sheets
- Easy to read and edit
- Clear column per council member

### Option B: Pipe-Separated Member Votes

```csv
meeting_date,agenda_item,item_title,outcome,ayes,noes,abstain,absent,member_votes
2021-10-05,7.1,Budget,Pass,5,2,0,0,"Amezcua:Aye|Sarmiento:Aye|Bacerra:Nay|..."
```

---

## 🔧 Tools Available

### CSV to JSON Converter
**Location:** `tools/csv_to_json.py`
**Usage:** `python tools/csv_to_json.py <csv_file>`

Converts your CSV data to JSON format for comparison with AI extractor.

### Comparison Tool
**Location:** `compare_extractions.py`
**Usage:** `python compare_extractions.py <manual_json> <agenda> <minutes>`

Compares your manual extraction (CSV-converted) with AI extraction.

---

## 📚 Documentation

- **[CSV_EXTRACTION_WORKFLOW.md](../CSV_EXTRACTION_WORKFLOW.md)** - Complete CSV workflow guide
- **[EXTRACTION_STATUS.md](EXTRACTION_STATUS.md)** - Detailed status and roadmap
- **[QUICK_START.md](QUICK_START.md)** - Original quick start (now outdated for CSV)

---

## ✅ Current Status

- ✅ Directory structure created
- ✅ All folders empty and ready
- ✅ CSV to JSON converter tool ready
- ⏳ Waiting for CSV data files

---

## 🚀 Next Steps

### When You Have CSV Data:

1. **Place CSV in year folder**
   ```bash
   # Example:
   cp ~/Downloads/santa_ana_2021_votes.csv extractors/santa_ana/2021/training_data/
   ```

2. **Convert to JSON**
   ```bash
   python tools/csv_to_json.py extractors/santa_ana/2021/training_data/santa_ana_2021_votes.csv
   ```

3. **Add source documents and run comparison**
   (Follow workflow above)

---

## 💡 Tips

### Creating CSV Data
- Use Excel or Google Sheets
- One row per vote
- One CSV can contain multiple meetings from same year
- Include all council members as columns
- Save as CSV when done

### File Naming
- Recommended: `santa_ana_YYYY_votes.csv`
- Examples: `santa_ana_2021_votes.csv`, `santa_ana_2024_votes.csv`

### Council Members
Current Santa Ana council members (2024):
- Mayor: Valerie Amezcua
- Councilmembers: Vince Sarmiento, Phil Bacerra, Johnathan Ryan Hernandez, Thai Viet Phan, Benjamin Vazquez, David Penaloza

---

**Ready to start when you have CSV data!**

**Last Updated:** 2025-11-18
