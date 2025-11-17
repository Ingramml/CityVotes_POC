# Santa Ana Vote Extraction - Quick Reference Guide

## 1-Page Cheat Sheet for Manual Parsing

### Setup (Once per session)
1. Copy template: `cp santa_ana_vote_extraction_template.csv your_working_file.csv`
2. Open source document (agenda or minutes text file)
3. Fill in meeting metadata (date, type, files, ID)

---

## Field Quick Reference

### Meeting Metadata (Copy to all votes from same meeting)
| Field | Format | Example |
|-------|--------|---------|
| example_id | EX### | EX001 |
| meeting_date | YYYY-MM-DD | 2024-01-16 |
| meeting_type | regular/special/emergency | regular |
| agenda_file | filename.txt | 20240116_Meetings4406Agenda.txt |
| minutes_file | filename.txt | 20240116_minutes_regular.txt |
| meeting_id | SA_YYYYMMDD | SA_20240116 |

### Vote Details (Extract for each vote)
| Field | Format | Example |
|-------|--------|---------|
| agenda_item_number | Text/Number | 26 or CONSENT |
| agenda_item_title | Text (<50 chars) | Budget Amendment Resolution |
| agenda_item_description | 1-2 sentences | Approve amendment to FY2024 budget... |
| motion_text | Full motion | moved to approve the recommended action |
| motion_type | original/substitute/amendment/consent | original |

### Motion Participants
| Field | Format | Example |
|-------|--------|---------|
| mover | Last name only | Bacerra |
| seconder | Last name only | Phan |

### Vote Results
| Field | Format | Example |
|-------|--------|---------|
| outcome | Pass/Fail/Tie/Continued/Withdrawn | Pass |
| vote_count | X-Y | 7-0 |
| tally_ayes | Integer | 7 |
| tally_noes | Integer | 0 |
| tally_abstain | Integer | 0 |
| tally_absent | Integer | 0 |
| tally_recused | Integer | 0 |

### Individual Votes (9 members: current + historical)
**Current (2024):** Amezcua, Bacerra, Hernandez, Penaloza, Phan, Vazquez
**Historical (2021-2023):** Sarmiento, Lopez, Mendoza

Each member's vote: `Aye`, `Nay`, `Abstain`, `Absent`, `Recused`, or blank (not on council)

### Quality Control
| Field | Format | Example |
|-------|--------|---------|
| recusals_notes | none or reason | conflict of interest |
| meeting_section | open/closed/consent | open |
| vote_sequence | Integer | 1, 2, 3... |
| validation_notes | Your observations | clear unanimous vote |
| data_quality_score | 1-10 | 10 |
| parsed_by | Initials | MI |
| parse_date | YYYY-MM-DD | 2024-10-20 |

---

## Santa Ana Vote Patterns to Search For

### Pattern 1: Modern Format
```
MOTION: COUNCILMEMBER BACERRA moved to approve...,
        seconded by COUNCILMEMBER PHAN.

The motion carried, 7-0, by the following roll call vote:

AYES: MAYOR AMEZCUA, COUNCILMEMBERS BACERRA, PHAN...
NOES: NONE
ABSTAIN: NONE
ABSENT: NONE
```

### Pattern 2: Older Format
```
YES: 7 – Penaloza, Phan, Lopez, Bacerra, Hernandez, Mendoza, Sarmiento
NO: 0
ABSTAIN: 0
ABSENT: 0
Status: 7 – 0 – 0 – 0 – Pass
```

---

## Quality Score Guide

| Score | Description | When to Use |
|-------|-------------|-------------|
| 10 | Perfect - all fields clear | Routine unanimous votes |
| 8-9 | Excellent - minor gaps | Seconder unknown, but vote clear |
| 6-7 | Good - some inference | Motion text unclear but votes complete |
| 4-5 | Acceptable - significant gaps | Multiple fields inferred |
| 1-3 | Poor - major issues | Corrupted text, heavy uncertainty |

---

## Validation Checklist (Before Saving)

- [ ] **Math**: ayes + noes + abstain + absent + recused = council size
- [ ] **Alignment**: Count of "Aye" = tally_ayes
- [ ] **Outcome**: Pass/Fail matches vote count
- [ ] **Names**: Last names only, correct spelling
- [ ] **Sequence**: vote_sequence is 1, 2, 3... (no gaps)
- [ ] **Historical members**: Blank for periods not serving

---

## Common Issues & Solutions

| Problem | Solution |
|---------|----------|
| Can't find mover/seconder | Use `Unknown` |
| Vote totals don't match | Document in validation_notes, lower score |
| OCR errors in names | Match to member list, note issue |
| Multiple interpretations | Pick best, note alternative |
| Page break splits vote | Search nearby pages, piece together |

---

## Efficient Workflow

1. **Search keywords**: "YES:", "AYES:", "motion carried", "Status:"
2. **Extract tallies first** (easiest to find)
3. **Parse member votes** (match to comma-separated names)
4. **Find motion context** (look backward from vote block)
5. **Validate math** (before moving to next vote)
6. **Document issues** (in validation_notes)

**Average time per vote:** 3-5 minutes (simple) to 10-15 minutes (complex)

---

## Quick Troubleshooting

**Vote count 7-0 but only 6 members listed?**
→ Check for name split across lines or OCR error

**All historical members showing votes in 2024?**
→ Wrong - leave blank if not serving during meeting

**Consent calendar with 10 items - one vote or ten?**
→ Usually ONE vote for entire consent calendar

**Motion amended then voted - which text to use?**
→ Final motion text after amendments, note type as "amendment"

---

## File Management

**Naming:**
- Working: `santa_ana_manual_votes_YYYYMMDD.csv`
- Backup: `santa_ana_manual_votes_YYYYMMDD_backup.csv`

**Save frequency:** Every 2-3 votes

---

## Example Row (Copy & Modify)

```csv
EX001,2024-01-16,regular,20240116_Meetings4406Agenda.txt,20240116_minutes.txt,SA_20240116,26,Budget Amendment,Approve FY2024 budget amendment,moved to approve Item 26,original,Bacerra,Phan,Pass,7-0,7,0,0,0,0,Aye,Aye,Aye,Aye,Aye,Aye,,,,,none,open,1,clear unanimous vote,10,MI,2024-10-20
```

---

## For More Help

- **Detailed instructions**: [MANUAL_PARSING_INSTRUCTIONS.md](MANUAL_PARSING_INSTRUCTIONS.md)
- **Full template guide**: [TEMPLATE_README.md](TEMPLATE_README.md)
- **Example data**: [santa_ana_vote_extraction_template.csv](santa_ana_vote_extraction_template.csv)

**Goal:** 85%+ automated extraction accuracy through high-quality training data
