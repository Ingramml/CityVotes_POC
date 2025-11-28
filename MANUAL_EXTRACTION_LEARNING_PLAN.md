# Manual Extraction Learning Plan
## Using Human-Annotated Data to Teach the AI Extractor

**Created:** 2025-11-18
**Purpose:** Systematic approach to improve AI extractor accuracy using manual extractions as ground truth

---

## 📋 Overview

This plan outlines how to use manually-created vote extractions to:
1. Identify AI extractor weaknesses
2. Learn new patterns
3. Improve extraction accuracy
4. Build a self-improving system

---

## 🎯 Goals

### Primary Goal
**Increase AI extractor accuracy from current baseline to 95%+ on standard meetings**

### Secondary Goals
- Identify common extraction failures
- Build pattern library from successful manual extractions
- Create feedback loop for continuous improvement
- Document lessons learned for future cities

---

## 📂 Available Resources

### Manual Extraction Files Found
Location: `/Volumes/Samsung USB/City_extraction/Santa_Ana/`

**Template Files (Annotated Examples):**
- `templates/template_1_20211005_minutes_regular_city_council_and_housing_authority_meeting.json`
- `templates/template_2_20210907_minutes_regular_city_council_and_housing_authority_meetin.json`
- `templates/template_3_20210316_minutes_regular_city_council_meeting.json`
- `templates/20210907_annotation_walkthrough.json`
- `templates/20141118_annotation_walkthrough.json`

**Actual Extraction:**
- `PDF/text_files/20190205_minutes_city_council_and_housing_authority_meetings_incl_votes.json`

### Source Documents
- PDF files in: `PDF/`
- Text files: Need to locate or convert PDFs

---

## 🔄 Learning Workflow

### Phase 1: Data Collection & Organization (Week 1)

#### Step 1.1: Import Manual Extractions
```bash
# Copy manual extractions to project
cp "/Volumes/Samsung USB/City_extraction/Santa_Ana/templates/"*.json \\
   manual_extractions/santa_ana/templates/

cp "/Volumes/Samsung USB/City_extraction/Santa_Ana/PDF/text_files/"*.json \\
   manual_extractions/santa_ana/actual/

# Create inventory
python -c "
import json
from pathlib import Path

extractions = list(Path('manual_extractions/santa_ana').rglob('*.json'))
print(f'Found {len(extractions)} manual extraction files')
for f in extractions:
    data = json.load(open(f))
    print(f'{f.name}: {len(data.get(\"votes\", []))} votes')
"
```

**Deliverable:** Organized manual extraction library

---

#### Step 1.2: Map to Source Documents
```bash
# For each manual extraction, find corresponding source files
# Create mapping file: extraction_source_mapping.json

{
  "20211005": {
    "manual_extraction": "manual_extractions/santa_ana/templates/template_1_20211005_*.json",
    "agenda_file": "/path/to/20211005_agenda.txt",
    "minutes_file": "/path/to/20211005_minutes.txt",
    "meeting_type": "regular_city_council_and_housing_authority"
  },
  ...
}
```

**Deliverable:** Complete mapping of extractions to sources

---

### Phase 2: Baseline Assessment (Week 1-2)

#### Step 2.1: Run AI Extractor on Same Documents
```python
# For each manual extraction:
# 1. Load manual extraction (ground truth)
# 2. Run AI extractor on same source documents
# 3. Compare results
# 4. Calculate accuracy metrics

python compare_extractions.py \\
    manual_extractions/santa_ana/templates/template_1_20211005.json \\
    /path/to/20211005_agenda.txt \\
    /path/to/20211005_minutes.txt
```

**Metrics to Track:**
- Vote detection rate (% of votes found)
- False positive rate (% of incorrect votes)
- Outcome accuracy (Pass/Fail/Tie correctness)
- Member name accuracy
- Tally accuracy
- Agenda item matching

**Deliverable:** Baseline accuracy report

---

#### Step 2.2: Categorize Failures
Create taxonomy of extraction failures:

**Categories:**
1. **Missing Votes** - AI didn't extract vote at all
   - Why? Pattern not recognized? Text format unusual?

2. **False Positives** - AI extracted something that wasn't a vote
   - Why? Over-eager pattern matching?

3. **Incorrect Outcome** - Found vote but wrong Pass/Fail
   - Why? Tally interpretation error?

4. **Member Name Errors** - Wrong names or missing members
   - Why? Name variation? Spelling?

5. **Tally Errors** - Wrong vote counts
   - Why? Parsing error? Math mistake?

6. **Agenda Item Mismatch** - Wrong agenda number
   - Why? Correlation error?

**Deliverable:** Categorized failure analysis

---

### Phase 3: Pattern Learning (Week 2-3)

#### Step 3.1: Extract Successful Patterns from Manual Data
```python
# Analyze manual extractions to find patterns
# Example: What text patterns precede votes?

from pathlib import Path
import json
import re

def extract_vote_patterns(manual_file, source_file):
    """
    Extract text patterns around successfully identified votes
    """
    manual = json.load(open(manual_file))
    source_text = open(source_file).read()

    patterns = []
    for vote in manual['votes']:
        # Find this vote's text in source
        # Extract surrounding context
        # Identify patterns
        pass

    return patterns

# Build pattern library
all_patterns = {}
for manual_file in Path('manual_extractions').rglob('*.json'):
    patterns = extract_vote_patterns(manual_file, corresponding_source)
    all_patterns[manual_file.stem] = patterns

# Save pattern library
with open('learned_patterns.json', 'w') as f:
    json.dump(all_patterns, f, indent=2)
```

**Patterns to Learn:**
- Vote introduction phrases ("Motion made by...", "Vote:", etc.)
- Tally formats ("5-2", "Ayes: 5, Noes: 2", etc.)
- Member name variations
- Outcome indicators ("Carried", "Failed", "Passed")
- Special cases (unanimous, recusals, abstentions)

**Deliverable:** Pattern library JSON file

---

#### Step 3.2: Update AI Extractor with Learned Patterns
```python
# In agents/ai_powered_santa_ana_extractor.py

# Add new regex patterns from pattern library
LEARNED_PATTERNS = {
    'vote_intro': [
        r'Motion\\s+(?:made\\s+)?by\\s+([A-Za-z\\s]+)',
        r'Council\\s+Member\\s+([A-Za-z\\s]+)\\s+moved',
        # ... patterns from manual analysis
    ],

    'tally_formats': [
        r'(\\d+)\\s*-\\s*(\\d+)',  # 5-2 format
        r'Ayes?:\\s*(\\d+).*Noes?:\\s*(\\d+)',  # Explicit format
        # ... more patterns
    ],

    'member_names': {
        'Amezcua': ['Amezcua', 'V. Amezcua', 'Mayor Amezcua', 'Valerie Amezcua'],
        'Bacerra': ['Bacerra', 'Phil Bacerra', 'P. Bacerra'],
        # ... more variations
    }
}

def enhance_extraction_with_learned_patterns(self, text):
    """Use learned patterns to improve extraction"""
    # Try learned patterns first
    # Fall back to original patterns
    # Use LLM for truly ambiguous cases
    pass
```

**Deliverable:** Updated AI extractor with new patterns

---

### Phase 4: Iterative Improvement (Week 3-4)

#### Step 4.1: Test Improvements
```bash
# Re-run comparison on all manual extractions
for file in manual_extractions/santa_ana/**/*.json; do
    python compare_extractions.py "$file" <agenda> <minutes>
done

# Compare before/after accuracy
python -c "
import json
from pathlib import Path

before = json.load(open('baseline_accuracy.json'))
after = json.load(open('improved_accuracy.json'))

print('Improvement Report:')
print(f'Detection rate: {before[\"detection\"]} → {after[\"detection\"]} (+{after[\"detection\"]-before[\"detection\"]}%)')
print(f'Accuracy rate: {before[\"accuracy\"]} → {after[\"accuracy\"]} (+{after[\"accuracy\"]-before[\"accuracy\"]}%)')
"
```

**Deliverable:** Improvement metrics report

---

#### Step 4.2: Learning Memory System
```python
# Update santa_ana_extraction_memory.json automatically

class LearningMemoryUpdater:
    def update_from_comparison(self, comparison_result):
        """
        Update learning memory based on comparison results
        """
        # For successful patterns: increment success count
        # For failed patterns: record failure
        # For new patterns: add to memory

        memory = ExtractionMemory.load()

        # Update successful patterns
        for pattern in comparison_result['successful_patterns']:
            memory.successful_patterns[pattern] = \\
                memory.successful_patterns.get(pattern, 0) + 1

        # Record failures
        for pattern in comparison_result['failed_patterns']:
            memory.failed_patterns[pattern] = \\
                memory.failed_patterns.get(pattern, 0) + 1

        # Add new member name corrections
        for old_name, correct_name in comparison_result['name_corrections'].items():
            memory.member_name_corrections[old_name] = correct_name

        # Update quality history
        memory.quality_history.append(comparison_result['accuracy'])

        memory.save()
```

**Deliverable:** Auto-updating learning memory

---

### Phase 5: Documentation & Knowledge Transfer (Week 4)

#### Step 5.1: Document Lessons Learned
Create `EXTRACTION_LESSONS_LEARNED.md`:

```markdown
# Lessons Learned from Manual Extraction Review

## Common Extraction Challenges

### 1. Member Name Variations
**Problem:** Council members' names appear in many formats
**Examples:**
- "Amezcua" vs "V. Amezcua" vs "Mayor Valerie Amezcua"
- "Bacerra" vs "Phil Bacerra" vs "P. Bacerra"

**Solution:** Build comprehensive name variation map

### 2. Tally Format Inconsistencies
**Problem:** Vote tallies written inconsistently
**Examples:**
- "5-2" vs "Ayes: 5, Noes: 2" vs "Five in favor, two opposed"

**Solution:** Multiple regex patterns for different formats

### 3. Special Session Handling
**Problem:** Special sessions have different formats
**Solution:** Detect session type and apply appropriate patterns

... more lessons ...
```

**Deliverable:** Comprehensive lessons learned documentation

---

#### Step 5.2: Create Training Dataset
```python
# Convert manual extractions into training examples

def create_training_example(manual_file, source_file):
    """
    Create structured training example from manual extraction
    """
    manual_data = json.load(open(manual_file))
    source_text = open(source_file).read()

    return {
        'date': manual_data.get('meeting_date'),
        'type': manual_data.get('meeting_type'),
        'source_text': source_text,
        'expected_votes': manual_data['votes'],
        'extraction_notes': manual_data.get('notes', []),
        'difficulty': manual_data.get('difficulty_rating', 'medium')
    }

# Build training dataset
training_data = []
for manual_file in Path('manual_extractions').rglob('*.json'):
    example = create_training_example(manual_file, find_source(manual_file))
    training_data.append(example)

# Save for future use
with open('santa_ana_training_dataset.json', 'w') as f:
    json.dump(training_data, f, indent=2)
```

**Deliverable:** Reusable training dataset

---

## 📊 Success Metrics

### Quantitative Metrics
- **Baseline Accuracy:** Measure current state
- **Target Accuracy:** 95%+ for standard meetings
- **Improvement Rate:** Track week-over-week gains
- **Coverage:** % of vote types handled correctly

### Qualitative Metrics
- **Edge Case Handling:** Can handle special sessions, recusals, etc.
- **Robustness:** Works across different meeting formats
- **Confidence:** AI correctly assesses its own confidence
- **Explainability:** Can explain why it made extraction decisions

---

## 🔧 Tools & Scripts

### Essential Scripts
1. **compare_extractions.py** - Compare manual vs AI (✅ Created)
2. **extract_patterns.py** - Extract patterns from manual data (To create)
3. **update_learning_memory.py** - Auto-update memory from comparisons (To create)
4. **batch_comparison.py** - Run comparisons on all manual files (To create)
5. **accuracy_report.py** - Generate accuracy metrics (To create)

### Helper Functions
```python
# utilities/extraction_helpers.py

def load_manual_extraction(file_path):
    """Standard way to load manual extractions"""
    pass

def find_source_documents(manual_file):
    """Find corresponding agenda/minutes for manual extraction"""
    pass

def calculate_accuracy(manual, ai):
    """Calculate detailed accuracy metrics"""
    pass

def generate_improvement_suggestions(comparison):
    """Suggest specific improvements based on failures"""
    pass
```

---

## 📅 Timeline

### Week 1: Setup & Baseline
- Days 1-2: Import and organize manual extractions
- Days 3-4: Map to source documents
- Days 5-7: Run baseline comparisons, calculate accuracy

### Week 2: Analysis & Pattern Learning
- Days 1-3: Categorize failures, identify patterns
- Days 4-5: Extract patterns from manual data
- Days 6-7: Document lessons learned

### Week 3: Implementation
- Days 1-3: Update AI extractor with learned patterns
- Days 4-5: Test improvements
- Days 6-7: Iterate based on results

### Week 4: Validation & Documentation
- Days 1-3: Final testing and validation
- Days 4-5: Create training dataset
- Days 6-7: Document and prepare for next cities

---

## 🎓 Knowledge Transfer to Other Cities

Once Santa Ana is optimized:

1. **Extract Generalizable Patterns**
   - Which patterns work across cities?
   - Which are Santa Ana-specific?

2. **Create City Extractor Template**
   - Base patterns all cities use
   - Customization points for each city

3. **Build Quick-Start Guide**
   - How to bootstrap new city extractor
   - Minimum manual extractions needed

---

## 🔄 Continuous Improvement Loop

```
Manual Extraction → AI Extraction → Compare → Analyze Failures →
Learn Patterns → Update AI → Test → Measure Improvement → Repeat
```

**Automated Workflow:**
1. User provides manual extraction
2. System automatically runs AI on same docs
3. Comparison runs automatically
4. Patterns extracted and added to memory
5. AI re-tests itself
6. Improvement metrics logged

---

## 📚 References

- [AI-Powered Extractor Guide](AI_POWERED_EXTRACTOR_GUIDE.md)
- [Manual Extraction Guidelines](/Volumes/Samsung USB/City_extraction/Santa_Ana/README_MANUAL_EXTRACTION.md)
- [Comparison Tool](compare_extractions.py)

---

## ✅ Next Immediate Steps

1. **Copy manual extractions to project**
   ```bash
   python -c "import shutil; shutil.copytree('/Volumes/Samsung USB/City_extraction/Santa_Ana/templates', 'manual_extractions/santa_ana/templates')"
   ```

2. **Run first comparison**
   ```bash
   python compare_extractions.py \\
       manual_extractions/santa_ana/templates/template_1_20211005.json \\
       <agenda_file> \\
       <minutes_file>
   ```

3. **Analyze results and identify first improvement**

4. **Implement improvement and re-test**

5. **Measure improvement**

---

**Last Updated:** 2025-11-18
**Status:** Ready to begin Phase 1
