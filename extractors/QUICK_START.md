# Quick Start: Combined Approach
**Your manual extractions are organized and ready!**

---

## ✅ What's Ready

### 2021 Files (Start Here!)
- ✅ **3 manual extractions** organized
- ✅ **3 source documents** copied
- ✅ Ready to run first comparison

### Structure Created
```
extractors/santa_ana/2021/
├── training_data/          ← Your 4 manual extractions
├── source_documents/       ← 3 text files ready
├── ai_results/             ← AI extractions will go here
└── comparisons/            ← Comparison reports will go here
```

---

## 🚀 Run Your First Comparison (5 minutes)

### Step 1: Check Manual Extraction Format

First, let's peek at one manual extraction to understand the format:

```bash
# Look at the first one
head -50 extractors/santa_ana/2021/training_data/template_1_20211005_*.json
```

**Note:** These templates show vote sections but may not be in the final format the AI extractor expects. We may need to convert or work with them as-is.

---

### Step 2: Run AI Extractor on Same Document

```bash
# Run AI extraction on 20211005 meeting
python run_santa_ana_extraction.py \\
    --minutes extractors/santa_ana/2021/source_documents/20211005_minutes_*.txt \\
    --output extractors/santa_ana/2021/ai_results/20211005_ai_extraction.json
```

**OR if you don't have agenda files:**

```python
# Quick Python script
python << 'EOF'
from agents.ai_powered_santa_ana_extractor import AIPoweredSantaAnaExtractor
import json

extractor = AIPoweredSantaAnaExtractor()

# Process just the minutes file (no agenda)
minutes_file = "extractors/santa_ana/2021/source_documents/20211005_minutes_regular_city_council_and_housing_authority_meeting.txt"

# Read and process
with open(minutes_file) as f:
    text = f.read()

result = extractor.extract_votes_from_text(text, meeting_date="2021-10-05")

# Save result
output = {
    'votes': [vars(v) for v in result] if hasattr(result, '__iter__') else [],
    'total_votes': len(result) if hasattr(result, '__len__') else 0
}

with open('extractors/santa_ana/2021/ai_results/20211005_ai_extraction.json', 'w') as f:
    json.dump(output, f, indent=2)

print(f"✅ Extracted {len(output['votes'])} votes")
EOF
```

---

### Step 3: Quick Manual Review

Before running automated comparison, do a quick manual check:

```bash
# See what AI extracted
cat extractors/santa_ana/2021/ai_results/20211005_ai_extraction.json | grep -A 5 '"agenda_item_number"' | head -30

# Compare with manual extraction
cat extractors/santa_ana/2021/training_data/template_1_20211005_*.json | grep -A 5 'vote_sections' | head -30
```

**Questions to ask:**
- Did AI find any votes?
- Do agenda item numbers match?
- Are there obvious missing votes?

---

## 📊 Understanding Your Manual Extraction Format

Your manual extractions appear to be **training templates**, not complete extractions. They contain:

- `vote_sections`: Text snippets where votes appear
- `line_range`: Where in document
- `suggested_patterns`: What patterns to look for

**This means:**
1. ✅ Good news: You've identified vote locations
2. ⚠️ Challenge: Need to convert to complete vote format for comparison

---

## 🔄 Two Paths Forward

### Path A: Use Templates for Pattern Learning (FASTER)

**Goal:** Extract patterns from your templates without full annotation

**Process:**
1. Analyze vote section text
2. Extract common patterns (tallies, member names, etc.)
3. Add patterns to AI extractor
4. Test improvements

**Time:** 2-3 hours
**Best for:** Quick improvements

---

### Path B: Complete the Annotations (MORE ACCURATE)

**Goal:** Convert templates to full vote extractions

**Process:**
1. For each vote section in templates
2. Fill in complete vote details
3. Save as proper extraction format
4. Run full comparison

**Time:** 6-8 hours for all 2021 files
**Best for:** Precise accuracy measurement

---

## 💡 My Recommendation: Start with Path A

Here's why:
- Your templates already identify vote locations (valuable!)
- Can learn patterns immediately
- Quick wins possible
- Can always complete annotations later

---

## 🎯 Path A: Quick Pattern Learning

### Step 1: Extract Patterns from Template 1

```python
# Pattern extraction script
python << 'EOF'
import json
from pathlib import Path
from collections import defaultdict

# Load template
template_file = "extractors/santa_ana/2021/training_data/template_1_20211005_minutes_regular_city_council_and_housing_authority_meeting.json"
template = json.load(open(template_file))

# Analyze vote sections
patterns = {
    'tally_formats': set(),
    'status_patterns': set(),
    'outcome_indicators': set()
}

for section in template.get('vote_sections', []):
    text = section.get('text', '')

    # Look for tally patterns
    import re

    # Status format: "Status: X-Y-Z-W - Outcome"
    status_matches = re.findall(r'Status:\s*(\d+)\s*-\s*(\d+)\s*-\s*(\d+)\s*-\s*(\d+)\s*-\s*(\w+)', text)
    if status_matches:
        patterns['status_patterns'].add(f"Status: {'-'.join(['X']*4)} - Outcome")

    # Look for outcome words
    if 'Pass' in text:
        patterns['outcome_indicators'].add('Pass')
    if 'Fail' in text:
        patterns['outcome_indicators'].add('Fail')

    # Tally formats
    tally_matches = re.findall(r'(\d+)\s*-\s*(\d+)(?:\s*-\s*(\d+))?(?:\s*-\s*(\d+))?', text)
    if tally_matches:
        patterns['tally_formats'].add('X-Y-Z-W format')

# Print findings
print("🔍 Patterns Found in 2021 Template 1:\n")
print("Tally Formats:")
for p in patterns['tally_formats']:
    print(f"  - {p}")

print("\nStatus Patterns:")
for p in patterns['status_patterns']:
    print(f"  - {p}")

print("\nOutcome Indicators:")
for p in patterns['outcome_indicators']:
    print(f"  - {p}")

# Save patterns
with open('extractors/santa_ana/2021/patterns/discovered_patterns.json', 'w') as f:
    json.dump({k: list(v) for k, v in patterns.items()}, f, indent=2)

print("\n✅ Patterns saved to extractors/santa_ana/2021/patterns/discovered_patterns.json")
EOF
```

---

### Step 2: Review Discovered Patterns

```bash
cat extractors/santa_ana/2021/patterns/discovered_patterns.json
```

---

### Step 3: Add Patterns to AI Extractor

Open `agents/ai_powered_santa_ana_extractor.py` and add discovered patterns.

---

## ✅ Next Steps

1. **Run pattern extraction** (above script)
2. **Review what patterns were found**
3. **Test AI extractor on 2021 documents**
4. **Measure improvement**
5. **Document findings**

---

## 📞 Need Help?

- **Understanding template format?** Check template_1 file
- **AI extractor not working?** Check if it needs agenda + minutes
- **Comparison tool issues?** May need format conversion first
- **Pattern extraction unclear?** I can help with specific examples

---

**Ready to start? Run the pattern extraction script above!**

**Last Updated:** 2025-11-18
