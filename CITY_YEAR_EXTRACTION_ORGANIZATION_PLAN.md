# City-Year Extraction Organization Plan
## Systematic Approach to Managing Format Changes Over Time

**Created:** 2025-11-18
**Purpose:** Organize vote extraction by city and year to handle format variations efficiently

---

## 🎯 Core Problem

### Why This Matters
Cities change their meeting document formats over time:
- 📄 **Format changes:** Agenda/minutes layouts evolve
- 👥 **Council changes:** Members change, affecting names
- 📋 **Process changes:** Voting procedures may change
- 🗓️ **Year-specific patterns:** Different eras, different formats

### Goal
**Keep extraction clean, targeted, and maintainable** by organizing:
- One extractor version per city-year combination
- Only train on relevant documents
- Track format evolution systematically

---

## 📁 Proposed Directory Structure

```
CityVotes_POC/
├── extractors/
│   ├── santa_ana/
│   │   ├── 2019/
│   │   │   ├── extractor_config.json
│   │   │   ├── training_data/
│   │   │   │   ├── 20190205_manual.json
│   │   │   │   ├── 20190312_manual.json
│   │   │   │   └── 20191015_manual.json
│   │   │   ├── patterns/
│   │   │   │   ├── vote_patterns.json
│   │   │   │   └── member_names.json
│   │   │   ├── source_documents/
│   │   │   │   ├── 20190205_agenda.txt
│   │   │   │   ├── 20190205_minutes.txt
│   │   │   │   └── ...
│   │   │   ├── ai_results/
│   │   │   ├── comparisons/
│   │   │   └── README.md
│   │   │
│   │   ├── 2020/
│   │   │   ├── extractor_config.json
│   │   │   ├── training_data/
│   │   │   ├── patterns/
│   │   │   ├── source_documents/
│   │   │   ├── ai_results/
│   │   │   ├── comparisons/
│   │   │   ├── README.md
│   │   │   └── CHANGES_FROM_2019.md  # Documents what changed
│   │   │
│   │   ├── 2021/
│   │   ├── 2022/
│   │   ├── 2023/
│   │   ├── 2024/
│   │   │   ├── extractor_config.json
│   │   │   ├── training_data/
│   │   │   ├── patterns/
│   │   │   ├── source_documents/
│   │   │   ├── ai_results/
│   │   │   ├── comparisons/
│   │   │   └── README.md
│   │   │
│   │   └── extractor_santa_ana.py  # Base extractor
│   │
│   ├── pomona/
│   │   ├── 2023/
│   │   ├── 2024/
│   │   └── extractor_pomona.py
│   │
│   ├── shared/
│   │   ├── base_extractor.py
│   │   ├── common_patterns.json
│   │   └── utilities.py
│   │
│   └── README.md
│
├── agents/
│   └── (existing agent code - uses extractors/)
│
└── tools/
    ├── detect_format_change.py
    ├── migrate_patterns.py
    └── compare_years.py
```

---

## 🗂️ Configuration System

### Per-City-Year Config File

**Example: `extractors/santa_ana/2024/extractor_config.json`**

```json
{
  "city": "Santa Ana",
  "state": "CA",
  "year": 2024,
  "date_range": {
    "start": "2024-01-01",
    "end": "2024-12-31"
  },

  "format_info": {
    "format_version": "v3",
    "last_format_change": "2023-07-01",
    "changes_from_previous": [
      "New agenda item numbering (X.Y format)",
      "Added vote tally summary at end of each section",
      "Changed member name formatting (now includes titles)"
    ]
  },

  "council_members": [
    {
      "name": "Valerie Amezcua",
      "title": "Mayor",
      "served_from": "2022-12-01",
      "served_to": null,
      "name_variations": ["Amezcua", "V. Amezcua", "Mayor Amezcua", "Valerie Amezcua"]
    },
    {
      "name": "Vince Sarmiento",
      "title": "Councilmember",
      "served_from": "2020-12-01",
      "served_to": "2024-11-30",
      "name_variations": ["Sarmiento", "V. Sarmiento", "Vince Sarmiento"]
    }
    // ... all members with their service dates
  ],

  "document_patterns": {
    "agenda_structure": {
      "item_number_format": "\\d+\\.\\d+",
      "section_headers": ["CONSENT CALENDAR", "BUSINESS ITEMS", "PUBLIC HEARINGS"],
      "vote_location": "end_of_item"
    },
    "minutes_structure": {
      "vote_intro_patterns": [
        "Status:\\s+(\\d+)\\s*-\\s*(\\d+)\\s*-\\s*(\\d+)\\s*-\\s*(\\d+)",
        "Motion\\s+(?:carried|passed|failed)",
        "Roll\\s+Call\\s+Vote:"
      ],
      "tally_formats": [
        "Status: {ayes}-{noes}-{abstain}-{absent} - {outcome}",
        "{ayes} to {noes}",
        "Ayes: {count}, Noes: {count}"
      ]
    }
  },

  "training_metadata": {
    "documents_annotated": 5,
    "total_votes_in_training": 87,
    "accuracy_achieved": 0.94,
    "last_updated": "2024-11-18",
    "notes": "Format stable since July 2023"
  },

  "inherits_from": {
    "year": 2023,
    "patterns_reused": ["member_names", "basic_tally"],
    "patterns_updated": ["agenda_numbering", "vote_intro"]
  }
}
```

---

## 🔄 Workflow: Year-by-Year Organization

### Phase 1: Initial City-Year Setup

#### Step 1.1: Detect Format Boundaries
**Goal:** Identify when formats change within a city

```python
# tools/detect_format_change.py

import json
from pathlib import Path
from collections import defaultdict

def detect_format_changes(city_name, source_dir):
    """
    Analyze meeting documents to detect format changes
    Returns: List of years/dates where format changes occurred
    """

    # Group documents by year
    docs_by_year = defaultdict(list)
    for doc in Path(source_dir).glob('*_minutes.txt'):
        year = doc.stem[:4]  # Extract year from filename
        docs_by_year[year].append(doc)

    # Analyze patterns in each year
    format_fingerprints = {}
    for year, docs in sorted(docs_by_year.items()):
        print(f"Analyzing {year}...")

        # Sample 2-3 documents from the year
        sample_docs = docs[:3]

        fingerprint = {
            'year': year,
            'sample_size': len(sample_docs),
            'patterns_found': extract_patterns(sample_docs),
            'item_numbering': detect_numbering_scheme(sample_docs),
            'vote_format': detect_vote_format(sample_docs),
            'member_count': count_unique_members(sample_docs)
        }

        format_fingerprints[year] = fingerprint

    # Compare year-to-year to find changes
    changes = []
    years = sorted(format_fingerprints.keys())

    for i in range(len(years) - 1):
        current_year = years[i]
        next_year = years[i+1]

        differences = compare_fingerprints(
            format_fingerprints[current_year],
            format_fingerprints[next_year]
        )

        if differences:
            changes.append({
                'from_year': current_year,
                'to_year': next_year,
                'changes': differences
            })

    return changes

def extract_patterns(docs):
    """Extract common text patterns from documents"""
    patterns = {
        'vote_intro': set(),
        'tally_format': set(),
        'outcome_words': set()
    }

    for doc in docs:
        text = open(doc).read()

        # Look for vote-related patterns
        import re
        vote_intros = re.findall(r'((?:Motion|Vote|Status):\s*.{0,50})', text)
        patterns['vote_intro'].update(vote_intros[:10])  # Sample

        tally_matches = re.findall(r'(\d+\s*-\s*\d+)', text)
        patterns['tally_format'].update(tally_matches[:10])

        # ... more pattern detection

    return {k: list(v) for k, v in patterns.items()}

# Usage:
changes = detect_format_changes('Santa Ana', '/Volumes/Samsung USB/...')
print(json.dumps(changes, indent=2))
```

**Output:**
```json
[
  {
    "from_year": "2019",
    "to_year": "2020",
    "changes": [
      "agenda_numbering: simple numbers → X.Y format",
      "vote_format: added Status line"
    ]
  },
  {
    "from_year": "2022",
    "to_year": "2023",
    "changes": [
      "member_names: added formal titles",
      "vote_location: moved to end of sections"
    ]
  }
]
```

**Time:** 1 hour automated analysis
**Output:** Format change timeline

---

#### Step 1.2: Create Year Directories
**Goal:** Set up organized structure

```bash
#!/bin/bash
# setup_city_year_structure.sh

CITY="santa_ana"
YEARS=(2019 2020 2021 2022 2023 2024)

for YEAR in "${YEARS[@]}"; do
    BASE_DIR="extractors/${CITY}/${YEAR}"

    # Create directory structure
    mkdir -p "${BASE_DIR}"/{training_data,patterns,source_documents,ai_results,comparisons}

    # Create config template
    cat > "${BASE_DIR}/extractor_config.json" << EOF
{
  "city": "Santa Ana",
  "state": "CA",
  "year": ${YEAR},
  "date_range": {
    "start": "${YEAR}-01-01",
    "end": "${YEAR}-12-31"
  },
  "format_info": {
    "format_version": "TO_BE_DETERMINED",
    "changes_from_previous": []
  },
  "council_members": [],
  "document_patterns": {},
  "training_metadata": {
    "documents_annotated": 0,
    "accuracy_achieved": 0
  }
}
EOF

    # Create README
    cat > "${BASE_DIR}/README.md" << EOF
# Santa Ana ${YEAR} Vote Extraction

## Format Information
- **Format Version:** TO_BE_DETERMINED
- **Council Members:** (to be filled)
- **Document Count:** TBD

## Training Status
- [ ] Format analysis complete
- [ ] 3-5 documents annotated
- [ ] Patterns extracted
- [ ] AI extractor configured
- [ ] Accuracy validated

## Changes from Previous Year
(To be documented after analysis)
EOF

    echo "✓ Created structure for ${YEAR}"
done
```

**Time:** 5 minutes
**Output:** Organized directory structure for all years

---

### Phase 2: Year-Specific Training

#### Step 2.1: Focus on One Year at a Time
**Strategy:** Start with most recent, work backwards

**Recommended Order:**
1. **2024** (most recent, most important)
2. **2023** (previous year, check for changes)
3. **2022** (if format changed, need separate handling)
4. **2021** (skip if same as 2022)
5. **Older years** (as needed)

**Per-Year Process:**
```bash
# For each year (e.g., 2024):

# 1. Select 3-5 representative documents
find "/Volumes/Samsung USB" -name "2024*minutes*.txt" | head -5

# 2. Copy to year-specific folder
cp [source_files] extractors/santa_ana/2024/source_documents/

# 3. Annotate those documents
# (Use fresh start process, but within year folder)

# 4. Extract year-specific patterns
python tools/extract_year_patterns.py \\
    --city santa_ana \\
    --year 2024 \\
    --training-dir extractors/santa_ana/2024/training_data

# 5. Configure extractor for that year
# (Update extractor_config.json with patterns)

# 6. Test and validate
python tools/test_year_extractor.py \\
    --city santa_ana \\
    --year 2024

# 7. Document findings
```

**Time per year:** 4-6 hours (first year), 2-3 hours (subsequent years if format similar)

---

#### Step 2.2: Inherit & Customize
**Goal:** Reuse patterns when formats are similar

```python
# tools/migrate_patterns.py

def migrate_patterns_to_new_year(from_year, to_year, city):
    """
    Copy patterns from previous year and allow customization
    """

    from_config = load_config(f"extractors/{city}/{from_year}/extractor_config.json")
    to_config = load_config(f"extractors/{city}/{to_year}/extractor_config.json")

    # Check what can be reused
    reusable = {
        'member_names': check_member_continuity(from_year, to_year),
        'vote_patterns': check_pattern_similarity(from_year, to_year),
        'tally_formats': check_tally_formats(from_year, to_year)
    }

    # Copy reusable patterns
    if reusable['vote_patterns'] > 0.8:  # 80% similar
        print(f"✓ Vote patterns similar, copying from {from_year}")
        copy_patterns(from_config, to_config, 'vote_patterns')
    else:
        print(f"✗ Vote patterns changed significantly, need new training")

    # Update member names (they often change)
    print("Updating council members for {to_year}...")
    to_config['council_members'] = detect_members_for_year(city, to_year)

    # Save updated config
    save_config(to_config, f"extractors/{city}/{to_year}/extractor_config.json")

    # Document what was inherited
    create_inheritance_report(from_year, to_year, reusable)
```

**Output:** Faster setup for similar years

---

### Phase 3: Extractor Selection at Runtime

#### Step 3.1: Smart Year Detection
**Goal:** Automatically pick right extractor version for a document

```python
# agents/year_aware_extractor.py

from pathlib import Path
import json
from datetime import datetime

class YearAwareExtractor:
    """
    Automatically selects the right extractor configuration
    based on document date
    """

    def __init__(self, city):
        self.city = city
        self.configs = self._load_all_year_configs()

    def _load_all_year_configs(self):
        """Load all year configurations for a city"""
        configs = {}
        config_dir = Path(f"extractors/{self.city}")

        for year_dir in config_dir.glob('*/'):
            if year_dir.is_dir() and year_dir.name.isdigit():
                config_file = year_dir / 'extractor_config.json'
                if config_file.exists():
                    configs[year_dir.name] = json.load(open(config_file))

        return configs

    def extract_from_document(self, agenda_file, minutes_file):
        """
        Extract votes using year-appropriate configuration
        """

        # Detect year from filename
        year = self._detect_year(agenda_file, minutes_file)

        # Get appropriate config
        config = self.get_config_for_year(year)

        # Use config to extract
        return self._extract_with_config(agenda_file, minutes_file, config)

    def _detect_year(self, agenda_file, minutes_file):
        """Extract year from filename or content"""

        # Try filename first
        filename = Path(minutes_file).name
        if filename[:4].isdigit():
            return filename[:4]

        # Try reading date from document
        # ... parsing logic ...

        return None

    def get_config_for_year(self, year):
        """
        Get the appropriate extractor config for a given year
        Falls back to nearest available if exact year not found
        """

        if year in self.configs:
            return self.configs[year]

        # Find nearest year
        available_years = sorted([int(y) for y in self.configs.keys()])
        target_year = int(year)

        # Find closest year
        nearest = min(available_years, key=lambda y: abs(y - target_year))

        print(f"⚠ No config for {year}, using {nearest} (nearest available)")
        return self.configs[str(nearest)]

    def _extract_with_config(self, agenda_file, minutes_file, config):
        """Run extraction using specific configuration"""

        from agents.ai_powered_santa_ana_extractor import AIPoweredSantaAnaExtractor

        # Create extractor instance
        extractor = AIPoweredSantaAnaExtractor()

        # Configure with year-specific settings
        extractor.council_members = set(
            m['name'] for m in config['council_members']
        )

        extractor.name_variations = {
            m['name']: m['name_variations']
            for m in config['council_members']
        }

        extractor.vote_patterns = config['document_patterns']['minutes_structure']['vote_intro_patterns']

        # Extract
        result = extractor.process_meeting(agenda_file, minutes_file)

        return result

# Usage:
extractor = YearAwareExtractor('santa_ana')
result = extractor.extract_from_document(
    'extractors/santa_ana/2024/source_documents/20240116_agenda.txt',
    'extractors/santa_ana/2024/source_documents/20240116_minutes.txt'
)
print(f"Extracted {len(result.votes)} votes using 2024 configuration")
```

---

## 📊 Benefits of This Organization

### Clarity & Maintenance
| Benefit | How It Helps |
|---------|-------------|
| **Format isolation** | Changes in one year don't affect others |
| **Clear history** | Can see how formats evolved |
| **Targeted training** | Only annotate what's needed for each year |
| **Easy debugging** | Know exactly which config to check |
| **Scalability** | Add new years without disrupting old ones |

### Efficiency
| Benefit | Impact |
|---------|--------|
| **Reuse patterns** | Inherit from similar years (save 50-70% time) |
| **Focus effort** | Only work on years that matter |
| **Avoid contamination** | Old formats don't confuse new training |
| **Selective updates** | Update only affected years when fixing bugs |

### Multi-City Support
| Benefit | How |
|---------|-----|
| **Same structure for all cities** | Pomona, Irvine, etc. follow same pattern |
| **Compare cities** | See how different cities format votes |
| **Share patterns** | Common patterns in `shared/` directory |
| **Independent configs** | Each city-year self-contained |

---

## 🎯 Implementation Priorities

### Phase 1: Current Year (2024)
**Focus:** Get 2024 working perfectly
- Select 5 Santa Ana 2024 documents
- Annotate thoroughly
- Achieve 95%+ accuracy
- Document patterns

**Time:** 1 week
**Output:** Production-ready 2024 extractor

### Phase 2: Previous Year (2023)
**Focus:** Check for format changes
- Sample 2-3 documents from 2023
- Compare patterns with 2024
- If similar: inherit patterns (1 hour)
- If different: full training (1 week)

**Time:** 1 hour - 1 week depending on similarity
**Output:** 2023 extractor (if needed)

### Phase 3: Historical Years
**Focus:** Only if needed
- Work backwards from 2023
- Stop when format becomes too different or data too old
- Each year: assess if worth the effort

**Time:** Variable
**Output:** Historical extractors as needed

---

## 🔧 Tools to Build

### Priority 1: Year Detector
```python
# tools/detect_format_change.py
# Automatically finds format boundaries
```

### Priority 2: Year Setup Script
```bash
# tools/setup_year.sh
# Creates directory structure for new year
```

### Priority 3: Pattern Migrator
```python
# tools/migrate_patterns.py
# Copies patterns between similar years
```

### Priority 4: Year-Aware Extractor
```python
# agents/year_aware_extractor.py
# Auto-selects right config for document
```

---

## 📋 Quick Start Guide

### Starting Fresh with City-Year Organization

```bash
# 1. Set up structure
./tools/setup_city_year_structure.sh santa_ana

# 2. Analyze format changes (optional - helps prioritize)
python tools/detect_format_change.py --city santa_ana

# 3. Start with current year (2024)
cd extractors/santa_ana/2024

# 4. Copy 5 representative 2024 documents
find "/Volumes/Samsung USB" -name "2024*minutes*.txt" | head -5 | \\
    xargs -I {} cp {} source_documents/

# 5. Annotate using fresh start process
# (Follow EXTRACTION_LEARNING_FRESH_START_PLAN.md within this folder)

# 6. Extract patterns
python ../../tools/extract_year_patterns.py \\
    --city santa_ana \\
    --year 2024 \\
    --training-dir training_data/

# 7. Test
python ../../tools/test_year_extractor.py --city santa_ana --year 2024

# 8. Document
vim README.md  # Update with findings

# 9. Move to next year (2023) and repeat
```

---

## ✅ Success Criteria

### Per City-Year
- [ ] 3-5 documents annotated
- [ ] Patterns extracted and documented
- [ ] Config file complete
- [ ] 90%+ accuracy on test documents
- [ ] README documents format and changes
- [ ] Inherits from previous year (if applicable)

### Overall System
- [ ] Can automatically select right extractor for any document
- [ ] Clear documentation of format evolution
- [ ] Patterns reused where possible
- [ ] New years easy to add
- [ ] Multi-city support proven

---

**Ready to implement this organized approach? Let me know which year and city you want to start with!**

**Last Updated:** 2025-11-18
