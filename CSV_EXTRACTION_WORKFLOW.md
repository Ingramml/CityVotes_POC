# CSV-Based Extraction Workflow
## Working with Pre-Extracted Vote Data in CSV Format

**Created:** 2025-11-18
**Purpose:** Guide for when you have extracted vote data as CSV files per year

---

## 🎯 Overview

**Your Situation:**
- You have (or will have) CSV files with extracted vote data
- One CSV per year (e.g., `santa_ana_2021_votes.csv`, `santa_ana_2024_votes.csv`)
- Want to use this data to train/improve the AI extractor

**This Changes Things Because:**
- CSV format ≠ JSON format the AI extractor uses
- Need conversion step: CSV → JSON
- CSV is more human-friendly for manual extraction
- Can work in spreadsheet software (Excel, Google Sheets)

---

## 📋 Expected CSV Format

### Option A: Simple Vote List (Recommended)

**File:** `santa_ana_2021_votes.csv`

```csv
meeting_date,agenda_item,item_title,outcome,ayes,noes,abstain,absent,member_votes
2021-10-05,7.1,Budget Amendment,Pass,5,2,0,0,"Amezcua:Aye|Sarmiento:Aye|Bacerra:Nay|Hernandez:Aye|Phan:Aye|Vazquez:Nay|Penaloza:Aye"
2021-10-05,8.2,Zoning Change,Pass,6,1,0,0,"Amezcua:Aye|Sarmiento:Aye|Bacerra:Nay|Hernandez:Aye|Phan:Aye|Vazquez:Aye|Penaloza:Aye"
2021-10-05,9.1,Contract Approval,Pass,7,0,0,0,"Amezcua:Aye|Sarmiento:Aye|Bacerra:Aye|Hernandez:Aye|Phan:Aye|Vazquez:Aye|Penaloza:Aye"
```

**Columns:**
- `meeting_date` - Date of meeting (YYYY-MM-DD)
- `agenda_item` - Agenda item number (e.g., "7.1")
- `item_title` - Description of item
- `outcome` - Pass/Fail/Tie/Continued
- `ayes` - Number of yes votes
- `noes` - Number of no votes
- `abstain` - Number of abstentions
- `absent` - Number of absent members
- `member_votes` - Pipe-separated member:vote pairs

---

### Option B: Separate Member Columns

**File:** `santa_ana_2021_votes.csv`

```csv
meeting_date,agenda_item,item_title,outcome,Amezcua,Sarmiento,Bacerra,Hernandez,Phan,Vazquez,Penaloza
2021-10-05,7.1,Budget Amendment,Pass,Aye,Aye,Nay,Aye,Aye,Nay,Aye
2021-10-05,8.2,Zoning Change,Pass,Aye,Aye,Nay,Aye,Aye,Aye,Aye
2021-10-05,9.1,Contract Approval,Pass,Aye,Aye,Aye,Aye,Aye,Aye,Aye
```

**Easier to read/edit in spreadsheet!**

---

## 🔄 Workflow with CSV Data

### Phase 1: Prepare Your CSV (Before You Have Data)

#### Step 1: Create CSV Template

```bash
# Create template for manual extraction
cat > extractors/santa_ana/2024/training_data/TEMPLATE_2024_votes.csv << 'EOF'
meeting_date,agenda_item,item_title,outcome,Amezcua,Sarmiento,Bacerra,Hernandez,Phan,Vazquez,Penaloza,notes
2024-01-16,,,Pass,Aye,Aye,Aye,Aye,Aye,Aye,Aye,
2024-01-16,,,Pass,Aye,Aye,Aye,Aye,Aye,Aye,Aye,
EOF

echo "✅ Template created: extractors/santa_ana/2024/training_data/TEMPLATE_2024_votes.csv"
echo "📝 Open in Excel/Google Sheets and fill in from meeting minutes"
```

**Instructions for filling template:**
1. Open meeting minutes document
2. For each vote found, add a row to CSV
3. Fill in all columns
4. Save as CSV when done
5. Place in appropriate year folder

---

### Phase 2: Convert CSV to JSON (When You Have Data)

#### Step 2: CSV → JSON Converter

```python
# tools/csv_to_json.py

import csv
import json
import sys
from pathlib import Path

def csv_to_json(csv_file, output_file=None):
    """
    Convert extracted votes CSV to JSON format expected by AI extractor
    """

    votes = []

    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)

        for row in reader:
            # Skip empty rows
            if not row.get('meeting_date'):
                continue

            # Extract member votes from individual columns
            member_votes = {}
            member_columns = ['Amezcua', 'Sarmiento', 'Bacerra', 'Hernandez',
                            'Phan', 'Vazquez', 'Penaloza']

            for member in member_columns:
                if member in row and row[member]:
                    member_votes[member] = row[member]

            # Or from pipe-separated field (Option A format)
            if 'member_votes' in row and row['member_votes']:
                for pair in row['member_votes'].split('|'):
                    if ':' in pair:
                        name, vote = pair.split(':')
                        member_votes[name] = vote

            # Calculate tally
            tally = {
                'ayes': int(row.get('ayes', 0)) if row.get('ayes') else len([v for v in member_votes.values() if v == 'Aye']),
                'noes': int(row.get('noes', 0)) if row.get('noes') else len([v for v in member_votes.values() if v == 'Nay']),
                'abstain': int(row.get('abstain', 0)) if row.get('abstain') else len([v for v in member_votes.values() if v == 'Abstain']),
                'absent': int(row.get('absent', 0)) if row.get('absent') else len([v for v in member_votes.values() if v == 'Absent'])
            }

            # Create vote object
            vote = {
                'agenda_item_number': row.get('agenda_item', ''),
                'agenda_item_title': row.get('item_title', ''),
                'outcome': row.get('outcome', ''),
                'tally': tally,
                'member_votes': member_votes,
                'meeting_date': row.get('meeting_date', '')
            }

            votes.append(vote)

    # Create output JSON
    output = {
        'votes': votes,
        'metadata': {
            'source': str(csv_file),
            'total_votes': len(votes),
            'conversion_date': str(datetime.now())
        }
    }

    # Save to file
    if not output_file:
        output_file = Path(csv_file).with_suffix('.json')

    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"✅ Converted {len(votes)} votes from CSV to JSON")
    print(f"📄 Output: {output_file}")

    return output

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python csv_to_json.py <csv_file> [output_json]")
        sys.exit(1)

    csv_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    csv_to_json(csv_file, output_file)
```

**Usage:**
```bash
# Convert your CSV to JSON
python tools/csv_to_json.py extractors/santa_ana/2024/training_data/2024_votes.csv

# Output: extractors/santa_ana/2024/training_data/2024_votes.json
```

---

### Phase 3: Use Converted Data for Training

#### Step 3: Run Comparison with JSON Data

Once converted to JSON, use the standard comparison workflow:

```bash
# Convert CSV to JSON (if not done)
python tools/csv_to_json.py extractors/santa_ana/2021/training_data/2021_votes.csv

# Find source documents
cp "/Volumes/Samsung USB/.../2021_minutes.txt" extractors/santa_ana/2021/source_documents/

# Run AI extractor on source
python run_santa_ana_extraction.py \
    --minutes extractors/santa_ana/2021/source_documents/2021_minutes.txt \
    --output extractors/santa_ana/2021/ai_results/2021_ai.json

# Compare manual (CSV-converted) vs AI
python compare_extractions.py \
    extractors/santa_ana/2021/training_data/2021_votes.json \
    extractors/santa_ana/2021/source_documents/2021_agenda.txt \
    extractors/santa_ana/2021/source_documents/2021_minutes.txt
```

---

## 🎯 Revised Quick Start (With CSV Data)

### When You Have CSV Files

1. **Receive/Create CSV per year**
   - Place in: `extractors/santa_ana/YYYY/training_data/`
   - Filename: `YYYY_votes.csv` (e.g., `2021_votes.csv`)

2. **Convert CSV to JSON**
   ```bash
   python tools/csv_to_json.py extractors/santa_ana/2021/training_data/2021_votes.csv
   ```

3. **Get source documents**
   ```bash
   # Copy from external drive
   cp "/Volumes/Samsung USB/.../2021_*.txt" extractors/santa_ana/2021/source_documents/
   ```

4. **Run AI extraction**
   ```bash
   python run_santa_ana_extraction.py \
       --minutes extractors/santa_ana/2021/source_documents/2021_minutes.txt \
       --output extractors/santa_ana/2021/ai_results/2021_ai.json
   ```

5. **Compare and improve**
   ```bash
   python compare_extractions.py \
       extractors/santa_ana/2021/training_data/2021_votes.json \
       [source files...]
   ```

---

## 📊 Directory Structure with CSV

```
extractors/santa_ana/2021/
├── training_data/
│   ├── 2021_votes.csv           ← Your CSV data
│   └── 2021_votes.json          ← Auto-converted from CSV
├── source_documents/
│   ├── 20210316_minutes.txt     ← Original documents
│   ├── 20210907_minutes.txt
│   └── 20211005_minutes.txt
├── ai_results/
│   └── 2021_ai_extraction.json  ← AI's extraction
├── comparisons/
│   └── 2021_comparison.txt      ← Comparison report
└── patterns/
    └── learned_patterns.json     ← Patterns extracted
```

---

## ✅ Benefits of CSV Format

### For You:
- ✅ **Easier to create** - Use Excel/Google Sheets
- ✅ **Easier to edit** - Spreadsheet interface
- ✅ **Easier to review** - See all votes at once
- ✅ **Easier to validate** - Sort, filter, spot errors
- ✅ **Version control friendly** - Text-based format

### For The Process:
- ✅ **One CSV per year** - Simple organization
- ✅ **Can aggregate meetings** - Multiple meetings in one CSV
- ✅ **Easy to share** - Anyone can open CSV
- ✅ **Quick to update** - Add new meetings to CSV

---

## 🚀 Getting Started (Right Now)

### Since You Don't Have Data Yet:

#### Option 1: Wait for CSV Files
Just wait until you have CSV files, then:
1. Place CSV in appropriate year folder
2. Run converter
3. Follow comparison workflow

#### Option 2: Create CSV Template Now
```bash
# Run this to create templates for each year
for YEAR in 2019 2021 2024; do
    cat > extractors/santa_ana/${YEAR}/training_data/TEMPLATE_${YEAR}_votes.csv << 'EOF'
meeting_date,agenda_item,item_title,outcome,Amezcua,Sarmiento,Bacerra,Hernandez,Phan,Vazquez,Penaloza,notes
EOF
    echo "✅ Created template for ${YEAR}"
done
```

Then when ready, open template and fill in data from meeting minutes.

#### Option 3: Do Nothing Now
- Folders are ready and empty
- When you get CSV data, place it in the appropriate year folder
- Run the conversion and comparison workflow

---

## 🔧 Tools to Create

### Priority 1: CSV to JSON Converter
```bash
# Create the converter tool
mkdir -p tools
cat > tools/csv_to_json.py << 'EOF'
[paste converter code from above]
EOF

chmod +x tools/csv_to_json.py
```

### Priority 2: Batch CSV Processor
```python
# tools/batch_process_csv.py
# Process multiple CSV files at once
```

### Priority 3: CSV Validator
```python
# tools/validate_csv.py
# Check CSV format before conversion
```

---

## 📋 Checklist for When You Get CSV Data

- [ ] Receive CSV file(s) for specific year(s)
- [ ] Place in `extractors/santa_ana/YYYY/training_data/`
- [ ] Run CSV to JSON converter
- [ ] Verify JSON looks correct
- [ ] Find corresponding source documents
- [ ] Copy source docs to `source_documents/` folder
- [ ] Run AI extraction on sources
- [ ] Compare CSV-converted data with AI results
- [ ] Analyze accuracy gaps
- [ ] Implement improvements

---

## 💡 Key Differences from Original Plan

| Original Plan | CSV-Based Plan |
|--------------|----------------|
| Manually create JSON | Manually create CSV (easier!) |
| JSON annotations | CSV rows in spreadsheet |
| Complex format | Simple tabular format |
| Hard to edit | Easy to edit |
| Direct comparison | CSV → JSON → comparison |
| One JSON per meeting | One CSV per year (all meetings) |

**Bottom line:** CSV is more human-friendly for creating the training data!

---

## ✅ Current Status

- ✅ Directory structure ready (empty)
- ✅ Waiting for CSV data
- ⏳ CSV converter ready to build when needed
- 📝 Templates can be created on demand

**Next Action When You Have CSV:**
1. Drop CSV in appropriate year folder
2. Run: `python tools/csv_to_json.py <csv_file>`
3. Continue with comparison workflow

---

**Questions? Ready to create the CSV converter tool now, or wait until you have CSV data?**

**Last Updated:** 2025-11-18
