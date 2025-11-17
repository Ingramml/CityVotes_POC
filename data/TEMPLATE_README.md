# Santa Ana Vote Extraction Training Data Template

## Overview
This directory contains the standardized template for manually parsing Santa Ana City Council votes into machine learning training data. The goal is to achieve **85%+ automated extraction accuracy** by providing high-quality labeled examples.

## Files in This Directory

| File | Purpose |
|------|---------|
| **santa_ana_vote_extraction_template.csv** | Master template with example records and field format guide |
| **MANUAL_PARSING_INSTRUCTIONS.md** | Detailed step-by-step parsing instructions |
| **TEMPLATE_README.md** | This file - quick start guide for using the template |

## Quick Start

### 1. Copy the Template
```bash
cp santa_ana_vote_extraction_template.csv santa_ana_manual_votes_YYYYMMDD.csv
```
Replace `YYYYMMDD` with today's date (e.g., `santa_ana_manual_votes_20241020.csv`)

### 2. Remove Example Rows
Keep the header row and the `EXAMPLE_TEMPLATE` row for reference. Delete all rows starting with `EX001` through `EX015` (or keep them as examples).

### 3. Start Parsing
Open your source document (agenda or minutes text file) and begin extracting vote information following the field definitions below.

## Template Structure

### 36 Fields Organized in 6 Categories

#### **Category 1: Meeting Metadata** (5 fields)
Identify these ONCE per meeting, then copy to all vote rows from that meeting:

| Field | Format | Example | Notes |
|-------|--------|---------|-------|
| `example_id` | EX### | `EX001` | Sequential ID for cross-referencing |
| `meeting_date` | YYYY-MM-DD | `2024-01-16` | Extract from document header |
| `meeting_type` | Text | `regular` | Options: regular, special, emergency, joint_housing, joint_successor |
| `agenda_file` | Filename | `20240116_Meetings4406Agenda.txt` | Exact filename |
| `minutes_file` | Filename | `20240116_minutes_regular_city_council_meeting.txt` | Exact filename |
| `meeting_id` | SA_YYYYMMDD | `SA_20240116` | Standardized format |

#### **Category 2: Vote Details** (5 fields)
Extract for EACH vote:

| Field | Format | Example | Notes |
|-------|--------|---------|-------|
| `agenda_item_number` | Text/Number | `26` or `CONSENT` | Keep original format from document |
| `agenda_item_title` | Text (<50 chars) | `Budget Amendment Resolution` | Short descriptive title |
| `agenda_item_description` | Text | `Approve amendment to FY2024 budget for emergency infrastructure repairs totaling $850000` | Full context, 1-2 sentences |
| `motion_text` | Text | `moved to approve the recommended action for Agenda Item No. 26` | Motion language before vote |
| `motion_type` | Text | `original` | Options: original, substitute, amendment, procedural, consent |

#### **Category 3: Motion Participants** (2 fields)

| Field | Format | Example | Notes |
|-------|--------|---------|-------|
| `mover` | Last name | `Bacerra` | Last name only, use `Unknown` if not stated |
| `seconder` | Last name | `Phan` | Last name only, use `Unknown` if not stated |

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

#### **Category 4: Vote Results** (7 fields)

| Field | Format | Example | Notes |
|-------|--------|---------|-------|
| `outcome` | Text | `Pass` | Options: Pass, Fail, Tie, Continued, Withdrawn |
| `vote_count` | X-Y | `7-0` or `4-3` | Format: ayes-noes |
| `tally_ayes` | Integer | `7` | Number who voted yes |
| `tally_noes` | Integer | `0` | Number who voted no |
| `tally_abstain` | Integer | `0` | Number who abstained |
| `tally_absent` | Integer | `0` | Number absent from meeting |
| `tally_recused` | Integer | `0` | Number who recused due to conflict |

**VALIDATION CHECK:** tally_ayes + tally_noes + tally_abstain + tally_absent + tally_recused = total council members

#### **Category 5: Individual Member Votes** (9 fields)
One field per council member (past and present):

| Field | Format | Options | Notes |
|-------|--------|---------|-------|
| `amezcua_vote` | Text | Aye, Nay, Abstain, Absent, Recused | Leave blank if not on council during meeting |
| `bacerra_vote` | Text | Aye, Nay, Abstain, Absent, Recused | |
| `hernandez_vote` | Text | Aye, Nay, Abstain, Absent, Recused | |
| `penaloza_vote` | Text | Aye, Nay, Abstain, Absent, Recused | |
| `phan_vote` | Text | Aye, Nay, Abstain, Absent, Recused | |
| `vazquez_vote` | Text | Aye, Nay, Abstain, Absent, Recused | |
| `sarmiento_vote` | Text | Aye, Nay, Abstain, Absent, Recused | Historical member (2021-2023) |
| `lopez_vote` | Text | Aye, Nay, Abstain, Absent, Recused | Historical member (2021-2023) |
| `mendoza_vote` | Text | Aye, Nay, Abstain, Absent, Recused | Historical member (2021-2023) |

**VALIDATION CHECK:** Count of "Aye" votes must equal `tally_ayes`

#### **Category 6: Quality Control** (7 fields)

| Field | Format | Example | Notes |
|-------|--------|---------|-------|
| `recusals_notes` | Text | `none` or reason | Use `none` if no recusals; otherwise brief reason |
| `meeting_section` | Text | `open` | Options: open, closed, consent, regular |
| `vote_sequence` | Integer | `1`, `2`, `3` | Order of votes in the meeting (start at 1) |
| `validation_notes` | Text | `clear unanimous vote on budget item` | Your parsing observations |
| `data_quality_score` | 1-10 | `10` | Quality rating (see scoring guide below) |
| `parsed_by` | Initials | `MI` | Your initials |
| `parse_date` | YYYY-MM-DD | `2024-09-24` | Date you completed parsing |

## Data Quality Scoring Guide

### Score 10 - Perfect
- All fields clearly identifiable
- No ambiguity in interpretation
- Vote counts match individual votes perfectly
- Motion text accurately captured

**Example:** EX001, EX002 - Clear consent calendar and unanimous votes

### Score 8-9 - Excellent
- Minor missing information (e.g., seconder not stated)
- Vote results clear
- Most context present

**Example:** EX003 - Leadership vote with one dissent, all info clear

### Score 6-7 - Good
- Some inference required
- Motion context partially unclear
- Core vote information intact

**Example:** EX005, EX010 - Split votes with all essential data

### Score 4-5 - Acceptable
- Significant missing information
- Heavy inference required
- Core tallies present but context weak

**Example:** EX012 - Vote with recusal, some fields inferred

### Score 1-3 - Poor
- Major gaps in information
- Vote block partially corrupted
- Multiple fields uncertain

**Note:** If your score is below 5, document specific issues in `validation_notes`

## Common Santa Ana Vote Pattern

When searching through text files, look for this typical pattern:

```
MOTION: COUNCILMEMBER BACERRA moved to approve the budget amendment,
        seconded by COUNCILMEMBER PHAN.

The motion carried, 7-0, by the following roll call vote:

AYES: MAYOR AMEZCUA, COUNCILMEMBERS BACERRA, HERNANDEZ, PENALOZA,
      PHAN, VAZQUEZ, SARMIENTO
NOES: NONE
ABSTAIN: NONE
ABSENT: NONE
```

Alternative format (older meetings):
```
YES: 7 – Penaloza, Phan, Lopez, Bacerra, Hernandez, Mendoza, Sarmiento
NO: 0
ABSTAIN: 0
ABSENT: 0
Status: 7 – 0 – 0 – 0 – Pass
```

## Template Usage Examples

### Example 1: Unanimous Consent Calendar (EX001)
This demonstrates:
- Consent calendar format (multiple items as one vote)
- Perfect quality score (10)
- All current council members voting "Aye"
- Historical members left blank (not on council in 2024)

### Example 2: Contested Leadership Vote (EX003)
This demonstrates:
- Split vote (6-1)
- One dissenting vote documented
- Quality score 9 (minor note about dissent)
- Validation notes explaining the political context

### Example 3: Failed Motion (EX007, EX014)
This demonstrates:
- "Fail" outcome when noes exceed ayes
- Vote count showing minority-majority split
- How to document motion failure

### Example 4: Member Absent (EX011)
This demonstrates:
- Tally showing 1 absent
- Member vote marked as "Absent"
- Vote count excludes absent member (6-0 with 1 absent)
- Notes explaining impact of absence

### Example 5: Recusal with Conflict (EX012)
This demonstrates:
- Abstain vote with documented reason
- Tally showing 1 abstention
- Recusals_notes field documenting the conflict
- Lower quality score (6) due to complexity

## Validation Checklist

Before saving your work, verify:

- [ ] **Math check**: tally_ayes + tally_noes + tally_abstain + tally_absent + tally_recused = council size
- [ ] **Individual votes align**: Count of "Aye" = tally_ayes, count of "Nay" = tally_noes
- [ ] **Outcome matches**: Pass/Fail is consistent with vote counts
- [ ] **Member names standardized**: Last names only, correct spelling
- [ ] **Historical members**: Blank for meetings they didn't attend (not Absent)
- [ ] **Required fields complete**: No empty meeting metadata fields
- [ ] **Quality score justified**: Score matches actual parsing difficulty
- [ ] **Example IDs unique**: No duplicate example_id values

## Working Efficiently

### Recommended Workflow

1. **Meeting Setup** (Do once per meeting)
   - Fill in meeting_date, meeting_type, filenames, meeting_id
   - Identify which council members were serving (historical vs current)

2. **Vote-by-Vote Extraction** (Repeat for each vote)
   - Search for vote pattern keywords: "YES:", "AYES:", "motion carried"
   - Extract vote tallies first
   - Extract individual member votes
   - Find motion context above the vote block
   - Document quality and observations

3. **Quality Review** (After completing all votes from one meeting)
   - Run math checks on all rows
   - Verify vote_sequence is sequential (1, 2, 3...)
   - Check consistency across similar votes

### Time Estimates
- **Simple unanimous vote**: 3-5 minutes
- **Split vote with debate**: 5-8 minutes
- **Complex motion with amendments**: 10-15 minutes
- **Average meeting (5-8 votes)**: 30-60 minutes

## Getting Help

### If You're Stuck

1. **Check the example rows** (EX001-EX015) for similar situations
2. **Reference MANUAL_PARSING_INSTRUCTIONS.md** for detailed guidance
3. **Use lower quality scores** rather than guessing
4. **Document uncertainty** in validation_notes field

### Common Questions

**Q: Can't find who moved/seconded the motion**
- A: Use `Unknown` in both fields and note in validation_notes

**Q: Vote totals don't match individual votes**
- A: Document the discrepancy in validation_notes, lower quality score to 4-6

**Q: Multiple interpretations possible**
- A: Choose most reasonable interpretation, note alternative in validation_notes

**Q: OCR errors in member names**
- A: Match to known member list, correct spelling, note in validation_notes if severe

**Q: Should I leave historical members blank or mark as Absent?**
- A: Leave blank if they weren't on council during that period; use "Absent" only if they were serving but not at the meeting

## Data Usage

This training data will be used to:
1. **Train machine learning models** for automated vote extraction
2. **Validate extraction algorithms** against human-parsed ground truth
3. **Improve pattern recognition** for Santa Ana-specific vote formats
4. **Calculate accuracy metrics** (baseline: 16%, target: 85%+)

Your careful, accurate parsing is critical to achieving these goals.

## File Management

### Naming Convention
- **Working file**: `santa_ana_manual_votes_YYYYMMDD.csv` (your parse date)
- **Backup file**: `santa_ana_manual_votes_YYYYMMDD_backup.csv`
- **Final file**: `santa_ana_manual_votes_complete.csv`

### Version Control
- Save frequently (after every 2-3 votes)
- Keep backup copies
- Note which meetings/dates you've completed in a separate tracking document

## Final Tips

1. **Be systematic** - Complete one meeting at a time
2. **Double-check math** - Vote tallies must add up correctly
3. **Be consistent** - Use same standards throughout your parsing
4. **Document uncertainty** - Better to note issues than hide them
5. **Take breaks** - Parsing accuracy decreases with fatigue
6. **Quality over speed** - A few high-quality records are more valuable than many low-quality ones

---

## Reference: Full Field List (36 fields)

```
example_id, meeting_date, meeting_type, agenda_file, minutes_file, meeting_id,
agenda_item_number, agenda_item_title, agenda_item_description, motion_text, motion_type,
mover, seconder,
outcome, vote_count, tally_ayes, tally_noes, tally_abstain, tally_absent, tally_recused,
amezcua_vote, bacerra_vote, hernandez_vote, penaloza_vote, phan_vote, vazquez_vote,
sarmiento_vote, lopez_vote, mendoza_vote,
recusals_notes, meeting_section, vote_sequence, validation_notes, data_quality_score,
parsed_by, parse_date
```

## Questions or Issues?

Refer to:
- [MANUAL_PARSING_INSTRUCTIONS.md](MANUAL_PARSING_INSTRUCTIONS.md) - Comprehensive parsing guide
- [santa_ana_vote_extraction_template.csv](santa_ana_vote_extraction_template.csv) - Template with examples
- Project documentation in `/Claude_transfer/Documentation/`

**Goal**: Create high-quality training data to improve automated vote extraction from 16% to 85%+ accuracy.
