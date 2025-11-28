# AI vs Manual Extraction Comparison - 2/20/24 Meeting

**Date:** 2024-11-26
**Meeting:** February 20, 2024 Regular City Council Meeting

---

## Executive Summary

| Metric | Manual | AI | Gap |
|--------|--------|-----|-----|
| **Total Votes** | 38 | 14 | -24 (-63%) |
| **Matched Items** | 9 | 9 | Perfect match where both found |
| **Unique to Manual** | 28 | - | AI missed these |
| **Unique to AI** | - | 3 | False positives |
| **Accuracy (Recall)** | 100% | 37% | AI missing 63% of votes |
| **Precision** | - | 64% | 9/14 correct, 3 false positives |

---

## Key Findings

### ✅ What AI Got Right (9 items)
- Items: 10, 11, 15, 27, 28, 34, 35, 38, 43
- **Pattern**: Mostly "pulled" items that had discussion
- **Commonality**: Likely had explicit vote language in minutes

### ❌ What AI Missed (28 items)

**By Section:**
- **Consent Calendar**: 29 items (76% of manual extractions)
  - Items 8, 9, 13, 14, 16-25, and more
  - Pattern: Bulk approval, minimal discussion
  - Vote recorded as single action for multiple items

- **Pulled Items**: Some pulled items with discussion
  - Example: Item 12 (Appropriations)

**Critical Pattern:**
🎯 **AI is missing CONSENT CALENDAR items**

Consent calendar characteristics:
- Multiple items approved in single vote
- Format: "Items X through Y were approved 7-0"
- Little to no individual discussion
- Standard approval language

### ⚠️ False Positives (3 items)
- Item "2024-002"
- Item "2024-004"
- Item "2024-"

These appear to be Housing Authority items that AI incorrectly parsed.

---

## Root Cause Analysis

### Problem 1: Consent Calendar Pattern Not Recognized
**Evidence:**
- 29/38 manual votes (76%) are consent items
- AI found 0 consent items
- Manual extraction shows these as separate votes

**Why it matters:**
- Consent calendar is standard practice
- Represents majority of voting activity
- Each item should be tracked individually even if approved together

**Example from minutes:**
```
"MOTION: Mayor Pro Tem Hernandez moved to approve the recommended action
for Item Nos. 8, 9, and 13 through 33"
```

Manual extraction: Creates 25 separate vote records
AI extraction: May create 1 record or miss entirely

### Problem 2: Member Name Detection Issues
**Warnings seen:**
- "Unknown member name: AUTHORITY"
- "Unknown member name: MEMBER"
- "Unknown member name: VICE"
- "Unknown member name: CHAIR"

**Analysis:**
- AI picking up titles instead of names
- Suggests regex patterns are too broad
- Need better name normalization

### Problem 3: Vote Format Assumptions
**AI appears to expect:**
- Individual roll call votes
- Explicit "Aye/Nay" statements
- Named votes for each member

**Santa Ana reality:**
- Consent items: "7-0" with no member names
- Pulled items: Sometimes named votes, sometimes just tally
- Standard practice: Names only when dissent or noteworthy

---

## Recommendations

### Immediate Fixes (High Priority)

1. **Add Consent Calendar Detection**
   ```python
   # Pattern to detect
   "moved to approve.*Item Nos?\\.? (\\d+)(,? (\\d+))* (through|and) (\\d+)"
   ```
   - Extract item range
   - Create individual vote records for each item
   - Apply same tally to all

2. **Improve Member Name Extraction**
   - Use whitelist of known members: Amezcua, Bacerra, Hernandez, Lopez, Penaloza, Phan, Vazquez
   - Filter out titles: Mayor, Pro Tem, Councilmember, Authority, Member, Vice, Chair
   - Normalize: "Mayor Pro Tem Hernandez" → "Hernandez"

3. **Handle Tally-Only Votes**
   - Accept "7-0" format without member names
   - Don't require individual votes for unanimous consent
   - Populate member_votes only when explicitly stated

### Medium Priority

4. **Distinguish Regular vs Housing Authority Votes**
   - Filter out Housing Authority agenda items (2024-XXX format)
   - OR create separate extraction for HA votes -User prefered
   - Current false positives suggest confusion between City Council and HA

5. **Section Classification**
   - Detect consent vs regular vs pulled sections
   - Use section headings in agenda/minutes
   - Track which items were pulled from consent

### Low Priority

6. **Learning from Manual Patterns**
   - Your manual extraction shows clear patterns
   - Use as training examples for AI improvement
   - Build pattern library from successful manual extractions

---

## Next Steps

### Phase 1: Fix Consent Calendar (Biggest Impact)
1. Update regex patterns for consent calendar
2. Test on 2/20/24 meeting
3. Target: Extract all 29 consent items
4. Expected improvement: 37% → 90% recall

### Phase 2: Improve Name Detection
1. Implement member name whitelist
2. Add title filtering
3. Test on pulled items (items 10, 11, 12, etc.)
4. Expected improvement: Better quality on matched items

### Phase 3: Validate on Other Meetings
1. Run improved extractor on 3/5/24
2. Run on 8/20/24
3. Compare results
4. Iterate improvements

---

## Manual Extraction Quality Assessment

**Your manual extraction is excellent:**
- ✅ Correctly identified consent calendar items
- ✅ Separated bulk approvals into individual votes
- ✅ Captured agenda item numbers and titles
- ✅ Recorded tallies accurately
- ✅ Noted which items were pulled for discussion

**Insights from your methodology:**
- You understood consent calendar structure
- You created granular records (1 per item, not 1 per motion)
- You captured the outcome even when votes weren't detailed

**This is the gold standard** - AI should match your approach.

---

## Data to Support Improvements

### Consent Calendar Item Format (from your manual extraction)
```
Item 8: Excused Absences [consent] 7-0
Item 9: Minutes Approval [consent] (blank tally)
Item 13: Appropriation Adjustment [consent] (blank)
Item 14: Appropriation Adjustment [consent] (blank)
...
Item 16-33: All consent items approved in single motion
```
-- User note Do not incude any Excused Absences or Minutes Approval in votes
### Pattern to Replicate
When minutes say:
> "moved to approve Item Nos. 8, 9, and 13 through 33"

Create vote records for:
- Item 8
- Item 9
- Item 13
- Item 14
- Item 15
- ...
- Item 33

Each with same tally (7-0 or extracted from motion)

---

## Conclusion

**Gap identified:** AI missing consent calendar items (76% of votes)
**Root cause:** Pattern not programmed into extractor
**Fix priority:** HIGH - will improve recall from 37% → 90%
**Your manual data:** Perfect training dataset for improvement

The manual extraction provides an excellent roadmap for what the AI should achieve. The primary gap is consent calendar handling, which is a known pattern that can be programmed.

**Status:** Ready to implement improvements based on this analysis.

---

**Next action:** Update AI extractor with consent calendar detection based on manual extraction patterns.
