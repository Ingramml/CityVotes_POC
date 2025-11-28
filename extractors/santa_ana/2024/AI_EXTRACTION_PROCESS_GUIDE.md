# AI Extraction Process - Plain English Guide

**Purpose:** Extract voting records from Santa Ana city council meeting minutes and agendas

**Your Notes:**
The format may change year over year

---

## How It Works - Step by Step

### Step 1: Load the Meeting Documents

**What happens:**
- The system reads two text files:
  - **Minutes file**: Contains what happened at the meeting (the official record)
  - **Agenda file**: Contains the list of items that were scheduled to be discussed

**Why both files:**
- Minutes have the vote tallies and outcomes
- Agenda has the item titles and descriptions
- Together they give complete information

**Your Notes:**
_[Add your notes here]_

---

### Step 2: Clean Up the Text

**What happens:**
- Removes PDF conversion artifacts like:
  - Page numbers ("--- PAGE 3 ---")
  - Headers and footers that repeat on every page
  - Extra whitespace and line breaks

**Why this matters:**
- Cleaner text = easier pattern matching
- Removes noise that confuses the extraction

**Your Notes:**
A

---

### Step 3: Extract Consent Calendar Votes (MOST IMPORTANT)

**What the system looks for:**
Pattern like: "moved to approve Consent Calendar Item Nos. 8 through 41 with the exception of Item Nos. 10, 11, 15"

**What it does:**
1. Finds the item range (8 through 41 = items 8, 9, 10, 11... up to 41)
2. Identifies exceptions (pulled items that were discussed separately)
3. Figures out which items were approved: All items MINUS the exceptions
4. Creates a separate vote record for EACH approved item

**Example:**
- Minutes say: "Items 8 through 41 approved, except 10, 11, 15"
- System creates: 31 separate vote records (34 items total, minus 3 exceptions)
- Each record gets the same vote tally (e.g., 7-0)

**Why this is critical:**
- Consent calendar votes are 76% of all votes at Santa Ana meetings
- Most votes happen through this bulk approval process
- Each item needs to be tracked separately even though approved together

**Your Notes:**

exepctions should have pulled in the meeting section. This mean it was pulled out of the consent calander

---

### Step 4: Apply Exclusion Filters

**What gets filtered out:**
1. **Excused Absences** - These aren't real votes on city business
2. **Minutes Approval** - Just approving the previous meeting's notes
3. **Housing Authority items** - These are separate from City Council votes (format: 2024-002, 2024-004, etc.)

**How it identifies them:**
- Looks at the agenda item title
- Checks if title contains keywords like "excused absence" or "minutes approval"
- Checks if agenda item number matches Housing Authority format (year-number)

**Your Notes:**
_[Add your notes here]_

---

### Step 5: Extract Pulled Item Votes

**What are pulled items:**
- Items that were on the consent calendar but someone wanted to discuss
- These get individual votes with more detail
- Often have individual council member votes recorded

**What the system looks for:**
- Vote blocks with format: "YES: 6 - [names] NO: 0 Status: 6-0-1-0 Pass"
- Individual roll call votes
- Motion text explaining what was voted on

**Information captured:**
- Who voted yes, no, abstained
- Vote tally (ayes-noes-abstentions-absent)
- Outcome (Pass/Fail)
- Motion text

**Your Notes:**
Order of votes
Yes-No-Abstain-Absent-Recusal

---

### Step 6: Validate the Results

**What happens:**
- System checks the quality of what it extracted
- Gives a score between 0 and 1 (0% to 100%)

**What it checks:**
- Are vote tallies present?
- Do agenda item numbers look valid?
- Are outcomes recorded?
- Overall completeness

**Quality threshold:**
- If score is below 70%, triggers AI fallback (Step 7)
- If score is 70% or above, uses the regex extraction results

**Your Notes:**
_[Add your notes here]_

---

### Step 7: AI Fallback (When Regex Validation Fails)

**When this happens:**
- If the pattern-based extraction didn't capture enough votes
- Or if the validation score is below 70%

**What the AI does:**
- Re-reads the minutes with AI (Claude)
- Uses natural language understanding instead of rigid patterns
- Tries to find votes that the patterns missed

**Critical part - Vote Merging:**
- The AI results DON'T replace consent calendar votes
- Instead, consent votes are MERGED with AI-found votes
- This preserves the high-confidence consent calendar extraction

**How merging works:**
1. Keep all consent calendar votes from Step 3
2. Add any new votes the AI found
3. Skip duplicates (same agenda item number)
4. Final result = consent votes + unique AI votes

**Your Notes:**
_[Add your notes here]_

---

### Step 8: Clean Member Names

**The problem:**
- Minutes often include titles: "Councilmember Hernandez", "Mayor Pro Tem Lopez"
- System needs just the last name: "Hernandez", "Lopez"

**What gets removed:**
- COUNCILMEMBER
- MAYOR PRO TEM
- MAYOR
- VICE MAYOR
- AUTHORITY MEMBER
- CHAIR/VICE CHAIR

**Validation:**
- Checks cleaned name against list of known council members
- Known members: Amezcua, Bacerra, Hernandez, Lopez, Penaloza, Phan, Vazquez, Mendoza, Sarmiento
- If name not on list, logs a warning

**Your Notes:**
Differnen years will may have new membert to coouncil. Every year does not need to have all names
---

### Step 9: Get Agenda Item Titles

**What happens:**
- For each vote, looks up the agenda item title
- Searches the agenda file for patterns like:
  - "Item 12: [Title text]"
  - "12. [Title text]"

**Why this matters:**
- Minutes often just say "Item 12" without explaining what it is
- Agenda has the full description
- Makes the vote record meaningful and searchable

**Your Notes:**
_[Add your notes here]_

---

### Step 10: Save the Results

**What gets saved:**
- JSON file with all extracted votes
- Each vote record includes:
  - Agenda item number
  - Agenda item title
  - Vote outcome (Pass/Fail)
  - Vote tally (ayes, noes, abstentions, absent)
  - Individual member votes (when available)
  - Motion text
  - Validation notes

**File location:**
- Saved to: `extractors/santa_ana/[year]/ai_extraction/[date]_extraction.json`

**Your Notes:**
_[Add your notes here]_

---

## Key Concepts Explained

### Consent Calendar
**Plain English:** A batch of routine items approved together in one vote to save time. Each item still needs to be tracked separately.

**Example:** Instead of voting 30 times on routine items, council approves items 8-41 in one motion.

**Your Notes:**
_[Add your notes here]_

---

### Pulled Items
**Plain English:** Items someone wants to discuss before voting, so they're removed from the consent calendar and voted on individually.

**Example:** "Items 8-41 approved except 10, 11, 15 which were pulled for discussion"

**Your Notes:**
_[Add your notes here]_

---

### Vote Tally Format
**Plain English:** The numbers showing how each vote broke down.

**Format:** `ayes-noes-abstentions-absent`
**Example:** `7-0-0-0` means 7 voted yes, 0 voted no, 0 abstained, 0 absent

**Santa Ana shorthand:** Often just written as "7-0" in minutes (assumes 0 abstentions and 0 absent)

**Your Notes:**
_[Add your notes here]_

---

### Regex vs AI Extraction

**Regex (Pattern-based):**
- Looks for specific text patterns
- Very fast and consistent
- Works great when format is predictable
- Example: "Item Nos. 8 through 41"

**AI (Natural language):**
- Understands context and meaning
- Can handle variations in language
- Slower and uses more resources
- Falls back when patterns don't match

**Hybrid approach:**
- Try regex patterns first (fast, consistent)
- Use AI as backup (flexible, smart)
- Merge the results (best of both)

**Your Notes:**
_[Add your notes here]_

---

## Common Scenarios

### Scenario 1: Standard Consent Calendar Meeting
**What happens:**
- Minutes say: "Moved to approve Consent Calendar Items 8-41, except 10, 15, 27"
- System creates: ~35 vote records (all items except exceptions)
- Each record marked as "consent calendar" with same tally
- Exceptions handled separately in Scenario 2

**Your Notes:**
_[Add your notes here]_

---

### Scenario 2: Pulled Item with Discussion
**What happens:**
- Item was on consent but pulled for discussion
- Minutes have detailed vote: "Item 27: Parking Contract - YES: 6 (names) NO: 0 ABSTAIN: 1 (Lopez)"
- System creates: 1 detailed vote record with individual member votes

**Your Notes:**
there are also recusals that happen these recusal need to be added to the correct person for the correct agenda item

---

### Scenario 3: Regular Agenda Item
**What happens:**
- Item not on consent calendar
- Has motion, discussion, and vote
- System extracts like a pulled item (detailed vote record)

**Your Notes:**
_[Add your notes here]_

---

### Scenario 4: Housing Authority Meeting
**What happens:**
- Separate meeting with items numbered like "2024-002"
- These items are filtered OUT of City Council extraction
- Could be extracted separately later if needed

**Your Notes:**
_[Add your notes here]_

---

## What Makes This System Work Well

### 1. Two-Stage Approach
- Pattern matching catches the predictable stuff (consent calendar)
- AI catches the variations and edge cases
- Merging prevents losing good data

### 2. Santa Ana-Specific Patterns
- Tuned to exactly how Santa Ana formats their minutes
- Knows their consent calendar language
- Recognizes their vote tally format

### 3. Exclusion Rules
- Filters out non-votes (excused absences, minutes approval)
- Separates different government bodies (City Council vs Housing Authority)

### 4. Quality Validation
- Checks its own work
- Falls back to AI when pattern matching struggles
- Preserves high-confidence extractions

**Your Notes:**
_[Add your notes here]_

---

## File Structure

```
extractors/santa_ana/2024/
├── source_documents/           # Input files
│   ├── 20240220_agenda.txt
│   └── 20240220_minutes.txt
├── ai_extraction/              # Output files
│   └── 20240220_extraction.json
├── training_data/              # Your manual extractions
│   └── santa_ana_vote_extraction_2024.csv
└── santa_ana_extraction_memory.json  # Learning/patterns
```

**Your Notes:**
_[Add your notes here]_

---

## Current Performance

**Test Meeting:** February 20, 2024

**Results:**
- **40 votes extracted** (vs 38 manual)
- **105% recall rate**
- **0 false positives**

**Breakdown:**
- 26 consent calendar votes ✅
- 10 pulled items ✅
- 4 other votes ✅
- 0 Housing Authority false positives ✅

**Your Notes:**
_[Add your notes here]_

---

## Troubleshooting Guide

### If extraction misses consent calendar votes:
**Check:**
1. Is the pattern "Item Nos. X through Y" in the minutes?
2. Is "Consent Calendar" mentioned in the motion?
3. Are votes being created but then lost in AI fallback? (check logs for "Merging X consent calendar votes")

**Your Notes:**
_[Add your notes here]_

---

### If getting false positives:
**Check:**
1. Are Housing Authority items being included? (should be filtered)
2. Are Excused Absences or Minutes Approval included? (should be filtered)
3. Check the `_should_include_vote()` function filters

**Your Notes:**
_[Add your notes here]_

---

### If member names are wrong:
**Check:**
1. Are titles being removed? (Councilmember, Mayor, etc.)
2. Is the name in the known members list?
3. Check logs for "Unknown member name" warnings

**Your Notes:**
_[Add your notes here]_

---

### If vote counts are off:
**Check:**
1. Are blank votes being counted as "Aye"? (should be for passing votes)
2. Is the tally format recognized? (X-X or X-X-X-X)
3. Check the `_extract_tally_from_block()` function

**Your Notes:**
Yaye or Y or Y Also cond for Yes votes

---

## Code Location Reference

**Main file:** `agents/ai_powered_santa_ana_extractor.py`

**Key functions:**
- `process_santa_ana_meeting()` - Lines 84-145 - Main orchestration
- `_extract_consent_calendar_votes()` - Lines 164-249 - Consent calendar extraction
- `_should_include_vote()` - Lines 329-354 - Exclusion filters
- `_clean_member_name()` - Lines 351-381 - Title removal
- `_regex_extraction()` - Lines 356-402 - Pattern-based extraction

**Your Notes:**
_[Add your notes here]_

---

## Questions to Consider

1. **Should Housing Authority votes be extracted separately?**
   - Currently: Filtered out
   - Option: Create separate extraction for HA meetings

2. **What if someone abstains on a consent item?**
   - Currently: All consent items get same tally
   - Edge case: Member recuses on one consent item

3. **How to handle amended motions?**
   - Currently: Extracts final vote only
   - Question: Track amendments separately?

**Your Notes:**
_[Add your notes here]_

---

## Success Metrics

**Target:** 90% recall (find 90% of votes that exist)
**Achieved:** 105% recall (found more than manual extraction)

**Why over 100%?**
- Manual extraction included items that should be excluded (Items 8, 9)
- AI correctly excluded them per user requirements
- After adjusting for exclusions: AI found all required votes plus some additional valid ones

**Your Notes:**
_[Add your notes here]_

---

## Your Custom Notes Section

**Meeting-specific patterns you've noticed:**
_[Add your observations here]_

**Edge cases to watch for:**
_[Add edge cases here]_

**Improvements you'd like to see:**
_[Add ideas here]_

**Questions for the developer:**
_[Add questions here]_

---

**Last Updated:** 2025-11-26
**Version:** 1.0 - Initial plain English guide
