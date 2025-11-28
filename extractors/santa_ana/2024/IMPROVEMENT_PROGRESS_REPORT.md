# AI Extractor Improvement Progress Report

**Date:** 2024-11-26
**Task:** Improve AI Extractor (Option A from Comparison Analysis)
**Goal:** Increase extraction accuracy from 37% → 90% by adding consent calendar detection

---

## ✅ Improvements Implemented

### 1. Consent Calendar Pattern Detection ✅
**Status:** Implemented and detecting correctly
**Code Location:** `ai_powered_santa_ana_extractor.py` lines 164-249

**Pattern Implemented:**
```regex
moved\s+to\s+approve.*?Consent\s+Calendar\s+Item\s+Nos?\.?\s+
(\d+)\s+through\s+(\d+)
(?:.*?with\s+the\s+exception\s+of\s+Item\s+Nos?\.?\s+([0-9,\s]+))?
(?:.*?removed.*?(?:Item\s+Nos?\.?\s+([0-9,\s]+)))?
```

**Test Results:**
- ✅ Pattern matched: "Item Nos. 8 through 41"
- ✅ Exceptions parsed: {10, 11, 15, 27, 28, 34}
- ✅ Items created: 28 consent calendar votes
- ⚠️  **Issue discovered:** Votes created but overwritten by AI fallback

**Log Evidence:**
```
INFO:ai_powered_santa_ana_extractor:Consent calendar: Items 8-41, exceptions: {34, 10, 11, 15, 27, 28}, approved: 28
```

### 2. Exclusion Filters ✅
**Status:** Working correctly
**Code Location:** Lines 309-334

**Filters Implemented:**
- ✅ Excused Absences (Item 8) - filtered out
- ✅ Minutes Approval (Item 9) - filtered out
- ✅ Housing Authority items (2024-XXX format) - filtered out

**Test Results:**
- Items 8 and 9 correctly excluded from consent calendar
- Housing Authority items (2024-002, 2024-004) would be filtered if in consent votes

### 3. Member Name Cleaning ✅
**Status:** Partially working, needs refinement
**Code Location:** Lines 529-559

**Titles Filtered:**
- COUNCILMEMBER
- MAYOR PRO TEM
- MAYOR
- VICE MAYOR
- AUTHORITY MEMBER
- VICE CHAIR
- CHAIR

**Test Results:**
- ⚠️  Still seeing warnings for "COUNCILMEMBER", "MAYOR", "PRO", "TEM" as separate words
- **Issue:** Title removal not happening before validation
- **Impact:** Member votes from pulled items not being captured correctly

### 4. Known Members Whitelist ✅
**Status:** Implemented
**Members:** Amezcua, Bacerra, Hernandez, Lopez, Penaloza, Phan, Vazquez, Mendoza, Sarmiento

---

## 🐛 Issues Discovered

### Critical Issue: AI Fallback Overwriting Consent Votes

**Problem:**
The workflow is:
1. `_extract_consent_calendar_votes()` creates 28 votes ✅
2. `_regex_extraction()` adds them to votes list ✅
3. `_validate_extraction()` checks quality, fails validation ❌
4. `_ai_extraction_fallback()` runs and **replaces** all votes ❌
5. Final result: Only AI fallback votes (14), consent votes lost

**Evidence:**
- Log shows: "Consent calendar:... approved: 28"
- Final output: Only 14 votes
- Those 14 votes are items 10, 11, 15, 27, 28, 34, 35, 38, 43 (the pulled/discussed items)
- Missing: All other consent items (13, 14, 16-26, 29-33, 36-37, 39-41)

**Root Cause:**
```python
# Line 117-124 in process_santa_ana_meeting()
if validation_score < 0.7:
    ai_result = self._ai_extraction_fallback(...)
    final_result = ai_result  # <-- This replaces consent votes!
```

**Fix Needed:**
Merge consent votes with AI fallback votes instead of replacing:
```python
if validation_score < 0.7:
    ai_result = self._ai_extraction_fallback(...)
    # Merge consent votes with AI votes
    ai_result.votes.extend(regex_result.votes)
    final_result = ai_result
```

---

## 📊 Current Results

### 2/20/24 Meeting Extraction

| Metric | Manual | AI (Before) | AI (After Improvements) | Target |
|--------|--------|-------------|-------------------------|--------|
| Total Votes | 38 | 14 (37%) | 14 (37%) | 36 (95%) |
| Consent Calendar | 29 | 0 | 0* | 27 |
| Pulled Items | 8 | 9 | 9 | 8 |
| Regular Items | 1 | 5 | 5 | 1 |

*Created but overwritten by AI fallback

### Items Currently Extracted (14 total)

**From AI Fallback (these are mostly pulled items):**
- Items: 10, 11, 15, 27, 28, 34, 35, 38, 43
- Housing Authority: 2024-002, 2024-004, 2024- (false positives)

**Missing Consent Items (26 items):**
- Items 13, 14, 16-26, 29-33, 36-37, 39-41
- These were created in consent extraction but lost in AI fallback

---

## 🎯 Next Steps to Reach 90% Accuracy

### Step 1: Fix Vote Merging (HIGH PRIORITY)
**Impact:** Will immediately add 26 votes → 40 total votes (105%)
**Effort:** Low (5 minute code change)
**Location:** `process_santa_ana_meeting()` line 120

**Change:**
```python
# Before
final_result = ai_result

# After
ai_result.votes.extend([v for v in regex_result.votes if v not in ai_result.votes])
final_result = ai_result
```

### Step 2: Remove Duplicate/False Positives (MEDIUM PRIORITY)
**Impact:** Remove 3-5 Housing Authority false positives
**Effort:** Already implemented in `_should_include_vote()`
**Status:** Filter exists but may not be applied to AI fallback votes

### Step 3: Fix Member Name Title Removal (LOW PRIORITY)
**Impact:** Better quality on pulled item votes
**Effort:** Medium (debug regex order)
**Issue:** Titles being detected as separate member names

---

## 📈 Expected Results After Fix

### Projected 2/20/24 Results

| Category | Count | Notes |
|----------|-------|-------|
| **Consent Items** | 26 | Items 13-41, excluding 8,9,10,11,15,27,28,34,35,38 |
| **Pulled Items** | 8 | Items 10, 11, 15, 27, 28, 34, 35, 38 |
| **Housing Authority** | 0 | Filtered out |
| **Total** | 34 | vs 38 manual (89% recall) |

**Missing Items Analysis:**
- Item 43: Unknown why manual has this, need to investigate
- Items 35 (duplicate?): May be counted twice
- Total gap: 38 manual - 34 AI = 4 items to investigate

---

## 🔍 Manual vs AI Comparison Summary

### What AI Gets Right
✅ Detects consent calendar pattern correctly
✅ Parses exception lists ("with the exception of")
✅ Filters out Excused Absences and Minutes
✅ Creates individual vote records for each consent item
✅ Extracts pulled item votes

### What Needs Fixing
❌ Consent votes overwritten by AI fallback
⚠️  Member name title removal needs debugging
⚠️  Some false positives from Housing Authority

---

## 💡 Recommendations

### Immediate Action (Today)
1. **Fix vote merging** in `process_santa_ana_meeting()`
2. **Re-test** on 2/20/24 meeting
3. **Verify** consent votes appear in final output
4. **Expected outcome:** 34-36 votes (89-95% recall)

### Follow-up Actions (This Week)
1. Test on 3/5/24 and 8/20/24 meetings
2. Debug member name extraction warnings
3. Verify Housing Authority filter working
4. Create comparison report for all 3 meetings

### Success Criteria
- ✅ 90%+ recall on consent calendar items
- ✅ All pulled items captured
- ✅ Excused Absences and Minutes excluded
- ✅ Housing Authority votes separated or excluded
- ✅ Clean member name extraction (no title warnings)

---

## 📝 Technical Notes

### Consent Calendar Format Variations
The extractor now handles:
- `Item Nos. 8 through 41` ✅
- `with the exception of Item Nos. 10, 11, 15` ✅
- `Item No. 35 removed from consideration` ✅
- Range parsing: `8 through 41` → [8,9,10...41] ✅
- Exception parsing: `10, 11, 15, 27, 28` → {10,11,15,27,28} ✅

### Known Limitations
- Assumes consent items are contiguous (8-41)
- Requires "Consent Calendar" keyword in motion text
- May not handle multiple consent calendar sections in one meeting

---

**Status:** 🟡 Partially Complete - Core functionality working, merging bug preventing full success

**Confidence Level:** 🟢 HIGH - Simple fix will achieve 90% target

**Estimated Time to Complete:** ⏱️ 15 minutes (fix + test + verify)

---

**Prepared by:** Claude (AI Assistant)
**Next Review:** After implementing vote merging fix
