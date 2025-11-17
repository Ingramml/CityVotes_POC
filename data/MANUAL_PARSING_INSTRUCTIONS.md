# Santa Ana City Council Vote Manual Parsing Instructions

## Overview
This document provides detailed instructions for manually parsing Santa Ana City Council votes from text files into the standardized CSV format for machine learning training data.

## Required Files
- **Sample CSV**: `santa_ana_manual_votes_sample.csv` (in this folder)
- **Source Documents**: Agenda and minutes text files from `/Volumes/SSD/CityVotes/Santa_Ana_CA/`
- **Mapping Reference**: `santa_ana_mapping_report.csv` for document pairs

## CSV Structure Summary
The CSV contains **36 fields** organized in 6 categories:
1. **Meeting Metadata** (5 fields): Date, type, source files, IDs
2. **Vote Details** (5 fields): Item number, title, description, motion, type
3. **Motion Participants** (2 fields): Mover, seconder
4. **Vote Results** (7 fields): Outcome, counts, tallies
5. **Individual Member Votes** (9 fields): Each council member's position
6. **Quality Control** (7 fields): Parsing notes, validation, scoring

## Step-by-Step Parsing Process

### STEP 1: Meeting Metadata Setup
**Before parsing votes, fill out meeting information:**

#### meeting_date
- **Format**: YYYY-MM-DD
- **Source**: Extract from filename or document header
- **Example**: `2024-01-16`

#### meeting_type
- **Options**: `regular`, `special`, `emergency`, `joint_housing`, `joint_successor`
- **Source**: Look for meeting type in document title
- **Example**: "Regular City Council Meeting" → `regular`

#### agenda_file & minutes_file
- **Format**: Exact filename from source
- **Example**: `20240116_Meetings4406Agenda.txt`

#### meeting_id
- **Format**: SA_YYYYMMDD
- **Example**: `SA_20240116`

### STEP 2: Locate Vote Blocks

**Santa Ana Vote Pattern to Look For:**
```
YES: 7 – Penaloza, Phan, Lopez, Bacerra, Hernandez, Mendoza, Sarmiento
NO: 0
ABSTAIN: 0
ABSENT: 0
Status: 7 – 0 – 0 – 0 – Pass
```

**Search Strategy:**
1. Search document for "YES:" patterns
2. Look for "Status:" lines with vote counts
3. Find motion context above vote block
4. Check for any recusal notes in surrounding text

### STEP 3: Extract Vote Information

#### agenda_item_number
- **Source**: Look for item number before vote (e.g., "Item 26", "7.1", "CONSENT")
- **Format**: Keep original format from document
- **Examples**: `26`, `7.1`, `CONSENT`, `CONSENT-A`

#### agenda_item_title
- **Source**: Brief descriptive title from agenda or motion context
- **Length**: Keep under 50 characters
- **Example**: `Budget Amendment Resolution`

#### agenda_item_description
- **Source**: Full context from agenda or motion text
- **Length**: 1-2 sentences describing the item
- **Example**: `Approve amendment to FY2024 budget for emergency infrastructure repairs totaling $850000`

#### motion_text
- **Source**: Look for motion language before vote block
- **Common Patterns**:
  - "moved to approve..."
  - "moved to deny..."
  - "moved to continue..."
- **Example**: `moved to approve the recommended action for Agenda Item No. 26`

#### motion_type
- **Options**: `original`, `substitute`, `amendment`, `procedural`, `consent`
- **Default**: `original` if unclear
- **Consent**: Items approved as group without individual discussion

### STEP 4: Motion Participants

#### mover & seconder
- **Format**: Last name only (e.g., `Bacerra`, not `Councilmember Bacerra`)
- **Source**: Look for "moved by" and "seconded by" before vote
- **Unknown**: Use `Unknown` if not clearly stated

**Current Council Members (2024):**
- Amezcua (Mayor)
- Bacerra
- Hernandez
- Penaloza
- Phan (Mayor Pro Tem)
- Vazquez

**Historical Members (2021-2023):**
- Sarmiento
- Lopez
- Mendoza

### STEP 5: Vote Results

#### outcome
- **Options**: `Pass`, `Fail`, `Tie`, `Continued`, `Withdrawn`
- **Source**: Status line or explicit statement in minutes
- **Pass**: Motion carries
- **Fail**: Motion fails
- **Tie**: Equal votes (rare)

#### vote_count
- **Format**: "X-Y" (ayes-noes)
- **Source**: Status line format "Status: 7 – 0 – 0 – 0 – Pass"
- **Example**: `7-0`, `4-3`, `5-2`

#### Tally Fields (tally_ayes, tally_noes, tally_abstain, tally_absent, tally_recused)
- **Source**: Status line numbers in order
- **Format**: Integer only
- **Example**: Status "7 – 0 – 0 – 0" → ayes=7, noes=0, abstain=0, absent=0

### STEP 6: Individual Member Votes

**For each council member column:**
- **Options**: `Aye`, `Nay`, `Abstain`, `Absent`, `Recused`
- **Source**: Parse comma-separated names from YES/NO lines
- **Empty**: Leave blank for historical members not present

**Parsing Example:**
```
YES: 7 – Penaloza, Phan, Lopez, Bacerra, Hernandez, Mendoza, Sarmiento
NO: 0
```
Results in:
- penaloza_vote = `Aye`
- phan_vote = `Aye`
- bacerra_vote = `Aye`
- hernandez_vote = `Aye`
- etc.

**Special Cases:**
- **Absent**: Member not at meeting
- **Recused**: Member has conflict of interest
- **Abstain**: Member chooses not to vote

### STEP 7: Quality Control Fields

#### recusals_notes
- **Source**: Look for recusal explanations in minutes
- **Format**: Brief reason (e.g., "conflict of interest", "client relationship")
- **Default**: `none` if no recusals

#### meeting_section
- **Options**: `closed`, `open`, `consent`, `regular`
- **Source**: Which part of meeting agenda
- **Most votes**: `open` (regular session)

#### vote_sequence
- **Format**: Integer (1, 2, 3...)
- **Purpose**: Order of votes in the meeting
- **Start**: 1 for first vote in meeting

#### validation_notes
- **Purpose**: Your observations about parsing difficulty
- **Examples**:
  - "clear unanimous vote"
  - "contested leadership vote - Bacerra voted against"
  - "split vote on development project"
  - "Hernandez absent - strong environmental support"

#### data_quality_score
- **Scale**: 1-10 (10 = perfect)
- **Criteria**:
  - **10**: All fields clear, no ambiguity
  - **8-9**: Minor issues (missing mover/seconder)
  - **6-7**: Some inference required
  - **4-5**: Significant gaps in information
  - **1-3**: Major issues, low confidence

#### parsed_by
- **Format**: Your initials (e.g., `MI`, `JS`)

#### parse_date
- **Format**: YYYY-MM-DD
- **Value**: Date you completed the parsing

## Common Parsing Challenges

### Challenge 1: OCR Errors
**Problem**: Member names misspelled or garbled
**Solution**:
- Match to known member list
- Use context clues
- Note issues in validation_notes

### Challenge 2: Vote Blocks Spanning Pages
**Problem**: Vote information split across page breaks
**Solution**:
- Search surrounding pages for complete information
- Piece together from multiple sections
- Lower quality score if incomplete

### Challenge 3: Multiple Motions on Same Item
**Problem**: Original motion, then substitute motion
**Solution**:
- Create separate CSV rows for each vote
- Use motion_type to distinguish
- Note relationship in validation_notes

### Challenge 4: Missing Motion Context
**Problem**: Vote block without clear motion text
**Solution**:
- Look earlier in document for agenda item
- Use agenda_item_description as fallback
- Note in validation_notes: "motion text unclear"

## Quality Standards

### Excellent Quality (Score 9-10)
- All member votes clearly identified
- Motion text accurately captured
- Vote counts match individual votes
- No ambiguity in interpretation

### Good Quality (Score 7-8)
- Minor missing information (e.g., seconder unknown)
- Vote results clear but motion text incomplete
- Most member votes identified

### Acceptable Quality (Score 5-6)
- Core vote information present
- Some inference required for member votes
- Motion context partially unclear

### Poor Quality (Score 1-4)
- Significant missing information
- Heavy inference required
- Vote block partially corrupted/illegible

## Validation Checklist

Before submitting parsed data, verify:

- [ ] **Vote totals match**: tally_ayes + tally_noes + tally_abstain + tally_absent + tally_recused = total council members
- [ ] **Individual votes align**: Count of Aye votes = tally_ayes
- [ ] **Outcome correct**: Pass/Fail matches vote counts
- [ ] **Member names standardized**: Last names only, correct spelling
- [ ] **Quality score justified**: Matches actual parsing difficulty
- [ ] **Required fields complete**: No empty fields for meeting metadata

## File Management

### Naming Convention
- **Working File**: `santa_ana_manual_votes_YYYYMMDD.csv` (use your parsing date)
- **Final File**: `santa_ana_manual_votes_complete.csv`

### Version Control
- Save frequently during parsing session
- Keep backup copies of work in progress
- Note which meetings/votes you've completed

## Getting Help

### If You're Stuck:
1. **Check Sample CSV**: Reference the example rows
2. **Use Quality Score**: Lower score if uncertain rather than guess
3. **Document Issues**: Use validation_notes for challenges
4. **Ask Questions**: Better to clarify than make assumptions

### Common Questions:
- **"Can't find mover/seconder"**: Use `Unknown` and note in validation_notes
- **"Vote totals don't match"**: Lower quality score and explain in validation_notes
- **"Multiple interpretations possible"**: Pick most reasonable, note alternative in validation_notes

## Final Tips

1. **Work Systematically**: Complete one meeting at a time
2. **Double-Check Math**: Vote tallies should always add up
3. **Be Consistent**: Use same standards throughout
4. **Document Uncertainty**: Better to note issues than hide them
5. **Take Breaks**: Parsing accuracy decreases with fatigue

This manual parsing will create high-quality training data to improve automated vote extraction accuracy from 16% to 85%+.