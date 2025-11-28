# Manual Annotation Guide for Vote Extraction

This guide provides step-by-step instructions for creating high-quality annotated samples to improve vote extraction across all cities.

## Quick Start Process

### Step 1: Run Analysis Tool

```bash
# Analyze a city's files
python3 tools/quick_city_analyzer.py /path/to/city/files --create-templates --output-dir analysis_output

# Example for Santa Ana
python3 tools/quick_city_analyzer.py /Users/michaelingram/Documents/GitHub/CityData_extraction/Santa_Ana_CA --create-templates
```

This will generate:
- `{CITY}_analysis.json` - Pattern analysis results
- `{CITY}_patterns.json` - Regex pattern library 
- `annotation_templates/` - Pre-filled templates for top files

### Step 2: Review Analysis Results

The analysis will tell you:
- How many files contain votes
- Which vote patterns are most common
- Which files are best candidates for annotation
- Specific recommendations for that city

### Step 3: Manual Annotation Process

For each recommended file:

1. **Open the source text file**
2. **Find vote sections** (tool will suggest line ranges)
3. **Fill in the annotation template** with correct data
4. **Document any issues or patterns**

## Annotation Template Structure

```json
{
  "file_info": {
    "source": "meeting_2024_01_15.txt",
    "vote_count": 3,
    "detected_patterns": ["motion_carried", "ayes_list"]
  },
  "vote_sections": [
    {
      "section_id": 1,
      "line_range": "45-52",
      "raw_text": "Motion by Councilmember Smith, second by Jones.\nMotion carried, 5-2\nAYES: Smith, Jones, Brown, Davis, Wilson\nNOES: Taylor, Anderson",
      "expected_output": {
        "agenda_item_number": "12",
        "agenda_item_title": "Budget Amendment Approval",
        "motion_type": "original",
        "outcome": "Pass",
        "tally": {
          "ayes": 5,
          "noes": 2,
          "abstain": 0,
          "absent": 0
        },
        "member_votes": {
          "John Smith": "Aye",
          "Mary Jones": "Aye",
          "Bob Brown": "Aye",
          "Susan Davis": "Aye",
          "Mike Wilson": "Aye",
          "Lisa Taylor": "No",
          "Tom Anderson": "No"
        }
      },
      "patterns": {
        "vote_format": "motion_carried",
        "member_format": "AYES: Last, Last, Last",
        "difficulty": "Easy"
      },
      "notes": [
        "Standard format, easy to extract",
        "Member names in last name only format"
      ]
    }
  ]
}
```

## Annotation Guidelines

### ✅ What Makes a Good Sample

1. **Diverse Patterns**: Include different vote formats found in that city
2. **Clear Examples**: Choose files with readable text and obvious vote sections
3. **Complete Information**: Include all council members and vote tallies
4. **Edge Cases**: Document unusual scenarios (ties, recusals, continued items)
5. **OCR Issues**: Note common OCR errors and how they appear

### 📝 Required Fields to Annotate

**For Every Vote:**
- `agenda_item_number` - Item number from agenda
- `agenda_item_title` - Brief description of what was voted on
- `outcome` - "Pass", "Fail", "Tie", or "Continued"
- `tally` - Exact vote counts (ayes, noes, abstain, absent)

**When Available:**
- `member_votes` - Individual council member votes
- `motion_type` - "original", "substitute", "amendment"
- `motion_by` / `second_by` - Who made and seconded the motion

### 🔍 Pattern Documentation

For each vote section, document:

```json
"patterns": {
  "vote_format": "motion_carried",           // Type of vote pattern
  "member_format": "AYES: Last, First",     // How names are listed
  "difficulty": "Easy|Medium|Hard",         // Extraction difficulty
  "ocr_quality": "High|Medium|Low"          // Text quality
}
```

### 🐛 Common Issues to Document

**OCR Artifacts:**
- `Councilmcmber` → `Councilmember`
- `carricd` → `carried` 
- `8enavides` → `Benavides`
- `—` → `-` (em dash vs hyphen)

**Format Variations:**
- "Motion carried 5-2" vs "Status: 5-2-Pass"
- "AYES: Smith, Jones" vs "YES: John Smith, Mary Jones"
- Date formats: "January 15, 2024" vs "01/15/2024"

**Edge Cases:**
- Unanimous votes: "Motion carried unanimously"
- Failed motions: "Motion failed 2-5"
- Continued items: "Item 12 was continued"
- Recusals: "Councilmember X recused"

## Creating City-Specific Documentation

### Step 4: Organize by City

Create this structure for each city:

```
docs/extraction/{CITY_NAME}/
├── samples/
│   ├── annotated_sample_1.json
│   ├── annotated_sample_2.json
│   └── annotated_sample_3.json
├── patterns/
│   ├── vote_patterns.md
│   └── ocr_corrections.md
└── README.md
```

### Step 5: Document Patterns

In `vote_patterns.md`, document:

```markdown
# Houston Vote Patterns

## Pattern 1: Motion Carried Format
**Example:** "Motion carried, 6-1"
**Regex:** `motion\s+(carried|failed),?\s*(\d+)-(\d+)`
**Frequency:** 45% of votes
**Notes:** Most common format, easy to extract

## Pattern 2: Vote Status Format  
**Example:** "Vote: 5 Yes, 2 No"
**Regex:** `vote:\s*(\d+)\s*yes,?\s*(\d+)\s*no`
**Frequency:** 30% of votes
**Notes:** Used in newer meetings (2022+)
```

### Step 6: Test and Validate

1. **Run extraction** on annotated samples
2. **Compare results** to hand-labeled expected output
3. **Calculate accuracy** metrics
4. **Identify failure patterns**
5. **Iterate and improve**

## Quality Metrics

Track these metrics for each city:

- **Coverage**: % of files with detectable votes
- **Accuracy**: % of correctly extracted vote data
- **Completeness**: % of votes with all member names
- **Pattern Diversity**: Number of different vote formats

## Expected Timeline

**Per City (10-20 sample files):**
- Analysis: 30 minutes
- Annotation: 2-3 hours  
- Documentation: 1 hour
- Testing: 30 minutes

**Total for all cities:** ~40 hours of focused work

## Tools Summary

1. **`quick_city_analyzer.py`** - Automated pattern analysis
2. **Manual annotation** - Hand-label sample files
3. **Pattern documentation** - Create regex libraries
4. **Quality testing** - Validate extraction accuracy

This systematic approach will create comprehensive pattern libraries and samples for all cities, dramatically improving vote extraction accuracy across the entire system.
