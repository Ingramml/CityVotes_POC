# Sample Document Analysis & Pattern Library Framework

This document provides a systematic approach to creating comprehensive pattern libraries and annotated samples for all cities in the vote extraction system.

## Overview

To improve vote extraction accuracy across all cities, we need:

1. **Annotated Sample Files** - Hand-labeled examples with expected outputs
2. **Pattern Variation Catalogs** - Comprehensive documentation of format variations
3. **Edge Case Documentation** - Handling of unusual scenarios
4. **Historical Format Analysis** - Changes over time
5. **OCR Artifact Catalogs** - Common errors and corrections

## Implementation Framework

### Step 1: Create City-Specific Documentation Structure

For each city, create the following directory structure:

```
docs/extraction/{CITY_NAME}/
├── samples/
│   ├── annotated/           # Hand-labeled sample files
│   ├── edge_cases/          # Unusual scenarios
│   ├── failed_extractions/  # Examples that don't work
│   └── historical/          # Format changes over time
├── patterns/
│   ├── vote_formats.md      # All vote pattern variations
│   ├── member_patterns.md   # Council member name patterns
│   ├── ocr_artifacts.md     # Common OCR errors
│   └── regex_library.py     # Compiled pattern library
├── analysis/
│   ├── format_evolution.md  # Historical changes
│   ├── success_metrics.md   # Extraction accuracy data
│   └── improvement_log.md   # Tracked improvements
└── validation/
    ├── test_cases.json      # Automated test data
    ├── gold_standard.json   # Perfect extraction examples
    └── benchmark_results.md # Performance metrics
```

### Step 2: Annotated Sample File Template

Each annotated sample should follow this structure:

```markdown
# Sample: [City] - [Meeting Date] - [Meeting Type]

## Metadata
- **File**: original_filename.txt
- **Date**: YYYY-MM-DD
- **Type**: Regular/Special/Emergency
- **Format Version**: v1.0 (if known)
- **OCR Quality**: High/Medium/Low
- **Extraction Difficulty**: Easy/Medium/Hard

## Vote Sections Found

### Vote 1: [Agenda Item]
**Location**: Lines 45-52
**Raw Text**:
```
[Exact text from document]
```

**Expected Output**:
```json
{
  "agenda_item_number": "12",
  "agenda_item_title": "Budget Amendment",
  "outcome": "Pass",
  "tally": {"ayes": 5, "noes": 2, "abstain": 0, "absent": 0},
  "member_votes": {
    "John Smith": "Aye",
    "Jane Doe": "No"
  }
}
```

**Pattern Analysis**:
- Vote format: "Motion carried 5-2"
- Member list format: "AYES: Smith, Jones..."
- Special considerations: None

**Extraction Notes**:
- Easy to extract
- Standard format
- No OCR issues
```

### Step 3: Pattern Variation Catalog

Create comprehensive pattern documentation for each city:

```python
# Example: Houston Vote Patterns
HOUSTON_VOTE_PATTERNS = {
    "format_v1": {
        "period": "2018-2020",
        "vote_line": r"Motion (?:carried|failed),?\s*(\d+)-(\d+)",
        "member_format": "AYES: Last, First; Last, First",
        "example": "Motion carried, 7-0\nAYES: Turner, Sylvester; Boykins, Jerry",
        "notes": "Formal comma-separated format"
    },
    "format_v2": {
        "period": "2021-present", 
        "vote_line": r"Vote:\s*(\d+)\s*Yes,?\s*(\d+)\s*No",
        "member_format": "YES: First Last, First Last",
        "example": "Vote: 6 Yes, 1 No\nYES: Sylvester Turner, Jerry Boykins",
        "notes": "Simplified format, space-separated names"
    }
}
```

### Step 4: OCR Artifact Documentation

Document common OCR errors and corrections:

```python
OCR_CORRECTIONS = {
    "common_errors": {
        # Character substitutions
        "0": ["O", "o"],  # Zero confused with letter O
        "1": ["l", "I"],  # One confused with lowercase l or I
        "8": ["B"],       # Eight confused with B
        "rn": ["m"],      # r+n confused with m
        
        # Word-level errors
        "councilmernber": "councilmember",
        "rnotion": "motion",
        "carricd": "carried",
        "Ayes": ["AYES", "AVES", "A YES"],
        
        # Punctuation errors
        "—": "-",         # Em dash to hyphen
        "–": "-",         # En dash to hyphen
        ":": [";", "."],  # Colon confusion
    },
    
    "city_specific": {
        "Santa Ana": {
            "Tinajero": ["Tinaj3ro", "Tinajcro"],
            "Benavides": ["8enavides", "Bcnavides"],
            "Sarmiento": ["Sarrniento", "Sanniento"]
        },
        "Houston": {
            "Boykins": ["8oykins", "Bovkins"],
            "Gallegos": ["Gallcgos", "Gailegos"]
        }
    }
}
```

## Implementation Steps

### Step 1: Audit Existing Files

First, analyze what we already have:

```bash
# Scan all city directories for text files
find /Users/michaelingram/Documents/GitHub/CityData_extraction -name "*.txt" -type f | head -20
```

### Step 2: Create Sample Analysis Scripts

```python
# sample_analyzer.py
def analyze_city_files(city_dir: str) -> Dict:
    """Analyze all files in a city directory to identify patterns."""
    analysis = {
        "file_count": 0,
        "date_range": {"earliest": None, "latest": None},
        "vote_patterns_found": [],
        "common_ocr_errors": {},
        "format_variations": []
    }
    
    for txt_file in Path(city_dir).glob("*.txt"):
        # Analyze each file
        pass
    
    return analysis
```

### Step 3: Create Annotation Tools

```python
# annotation_tool.py
class VoteAnnotationTool:
    """Interactive tool for creating annotated samples."""
    
    def annotate_file(self, file_path: str):
        """Guide user through annotating a meeting file."""
        text = self.load_file(file_path)
        
        # Display text with line numbers
        self.display_text_with_lines(text)
        
        # Interactive vote section identification
        vote_sections = self.identify_vote_sections(text)
        
        # Generate annotation file
        self.create_annotation(file_path, vote_sections)
```

### Step 4: Quality Metrics Framework

```python
# metrics.py
class ExtractionMetrics:
    """Track extraction quality across cities."""
    
    def __init__(self):
        self.metrics = {
            "accuracy": 0.0,
            "recall": 0.0,
            "precision": 0.0,
            "common_failures": [],
            "improvement_areas": []
        }
    
    def compare_extraction_to_gold_standard(self, extracted: Dict, gold: Dict) -> Dict:
        """Compare extracted data to hand-annotated gold standard."""
        pass
```

## Recommended Implementation Sequence

### Phase 1: Santa Ana (Already Started)
1. ✅ Create documentation structure 
2. ✅ Basic pattern library
3. 🔄 Annotate 5-10 sample files
4. 🔄 Document OCR artifacts
5. 🔄 Create test cases

### Phase 2: High-Volume Cities
**Houston, Phoenix, Columbus**
1. Analyze existing files
2. Identify most common patterns
3. Create basic pattern library
4. Annotate representative samples

### Phase 3: Remaining Cities
**Glendale, Pomona, LA County, Tuscon, Cincinnati, Avondale**
1. Quick pattern analysis
2. Basic annotation
3. Focus on unique patterns

### Phase 4: Cross-City Analysis
1. Identify common patterns across cities
2. Create shared pattern library
3. Develop universal OCR corrections
4. Build comprehensive test suite

## Tools Needed

### 1. File Analysis Tool
```bash
python analyze_city_patterns.py --city Santa_Ana --output patterns/
```

### 2. Interactive Annotation Tool
```bash
python annotate_samples.py --file meeting.txt --output annotated/
```

### 3. Pattern Testing Tool
```bash
python test_patterns.py --city Houston --pattern-file patterns.json
```

### 4. Quality Assessment Tool
```bash
python assess_extraction.py --gold-standard gold.json --extracted output.json
```

## Expected Deliverables

### For Each City:
1. **10-20 annotated sample files** covering different time periods and formats
2. **Comprehensive pattern library** with regex patterns and examples
3. **OCR artifact catalog** with city-specific corrections
4. **Test case suite** for automated validation
5. **Quality metrics report** showing extraction accuracy

### Cross-City:
1. **Universal pattern library** for common vote formats
2. **Shared OCR corrections** applicable to multiple cities  
3. **Format evolution timeline** showing changes over time
4. **Best practices guide** for handling edge cases
5. **Automated quality assessment pipeline**

This framework will systematically improve vote extraction accuracy across all cities by providing comprehensive documentation, patterns, and validation tools.
