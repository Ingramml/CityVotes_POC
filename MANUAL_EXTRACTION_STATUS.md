# Manual Extraction Status & Next Steps

**Date:** 2025-11-18
**Status:** Ready for Review & Comparison

---

## 📂 Files Imported

### Location
All manual extractions copied to: `manual_extractions/santa_ana/`

### Inventory

**Templates (Annotation Examples):**
1. `template_1_20211005_minutes_regular_city_council_and_housing_authority_meeting.json`
   - Source: 20211005 minutes
   - Contains ~1200 vote sections needing annotation
   - Pattern types: vote_tally, status_vote

2. `template_2_20210907_minutes_regular_city_council_and_housing_authority_meetin.json`
3. `template_3_20210316_minutes_regular_city_council_meeting.json`
4. `20210907_annotation_walkthrough.json`
5. `20141118_annotation_walkthrough.json`
6. `item_22_template.json` - Single item template
7. `city_config_template.json` - City configuration

**Actual Extractions:**
1. `20190205_minutes_city_council_and_housing_authority_meetings_incl_votes.json`
   - Complete meeting extraction
   - Different format (agenda items with embedded votes)
   - Needs conversion to AI extractor format

**Total:** 8 files

---

## 🔍 What We Have

### Template Files (Training Data)
These are **NOT complete extractions** - they are:
- Text snippets from meeting minutes
- Vote sections identified for annotation
- Training examples showing patterns
- Guidelines for manual annotation process

**Format:**
```json
{
  "file_info": { "source": "...", "vote_count": 1200 },
  "vote_sections": [
    {
      "line_range": "38-44",
      "text": "ABSTAIN: 1, Status: 6-0-1-0 - Pass",
      "suggested_patterns": ["vote_tally", "status_vote"]
    }
  ],
  "annotation_template": {
    "agenda_item_number": "FILL_IN",
    "outcome": "Pass/Fail/Tie",
    ...
  }
}
```

### Actual Extraction (1 file)
- Full meeting extraction
- Every agenda item documented
- Votes embedded in items
- Different schema than AI extractor expects

---

## 🎯 What We Need

### For AI Extractor Training

We need **completed annotations** in this format:
```json
{
  "votes": [
    {
      "agenda_item_number": "10",
      "agenda_item_title": "Appoint Kimberly Cabrera...",
      "outcome": "Pass",
      "tally": {
        "ayes": 7,
        "noes": 0,
        "abstain": 0,
        "absent": 0
      },
      "member_votes": {
        "Mayor Sarmiento": "Aye",
        "Councilmember Phan": "Aye",
        ...
      }
    }
  ]
}
```

### Current Status

❌ **We don't have this yet!**

The template files show WHERE votes are in the text, but haven't been fully annotated with:
- Individual member votes
- Complete agenda item details
- Proper schema format

---

## 📋 Next Steps

### Option 1: Complete the Annotations (Recommended)

**Process:**
1. Take template files (which identify vote locations)
2. For each vote section, manually fill in the complete data
3. Save as properly formatted extraction files
4. Then run comparisons

**Time estimate:** 2-4 hours per meeting

**Tools needed:**
- Source text files from `/Volumes/Samsung USB/City_extraction/Santa_Ana/PDF/text_files/`
- Template as guide
- Manual annotation based on reading the text

### Option 2: Use Templates to Teach Pattern Recognition

**Process:**
1. Analyze the vote section text snippets
2. Extract common patterns (like "Status: 6-0-1-0 - Pass")
3. Update AI extractor regex patterns
4. Test on full documents

**Benefit:** Faster, focuses on pattern learning
**Limitation:** Can't measure accuracy without ground truth

### Option 3: Focus on the One Complete Extraction

**Process:**
1. Convert `20190205` extraction to AI extractor format
2. Find corresponding source text files
3. Run comparison on that single meeting
4. Use lessons learned to improve extractor

**Benefit:** Immediate comparison possible
**Limitation:** Only one example

---

## 🔄 Recommended Workflow

### Phase 1: Quick Wins (This Session)

1. **Convert existing extraction to proper format**
   ```python
   # Convert 20190205 extraction format
   # From: agenda_items with embedded votes
   # To: {votes: [...]} format
   ```

2. **Find source files for 20190205**
   ```bash
   find "/Volumes/Samsung USB" -name "*20190205*"
   ```

3. **Run first comparison**
   ```bash
   python compare_extractions.py \\
       manual_extractions/santa_ana/actual/20190205_converted.json \\
       <agenda_file> \\
       <minutes_file>
   ```

4. **Document findings**
   - What did AI miss?
   - What patterns need improvement?
   - Immediate fixes possible?

### Phase 2: Pattern Learning (Next Session)

1. **Extract patterns from templates**
   - Analyze vote section text
   - Identify common formats
   - Add to AI extractor

2. **Test pattern improvements**
   - Run on known documents
   - Measure improvement

### Phase 3: Complete Annotations (Future)

1. **Systematically annotate templates**
   - Complete all template vote sections
   - Build comprehensive training set

2. **Full comparison suite**
   - Run all comparisons
   - Comprehensive accuracy measurement

---

## 📊 Tools Available

### Created Tools
✅ `compare_extractions.py` - Comparison tool
✅ `manual_extractions/` - Directory structure
✅ `MANUAL_EXTRACTION_LEARNING_PLAN.md` - Detailed plan

### Needed Tools
- [ ] `convert_extraction_format.py` - Convert 20190205 format
- [ ] `extract_patterns_from_templates.py` - Learn from templates
- [ ] `annotate_template.py` - Helper for completing annotations

---

## 🎯 Immediate Action Items

### Today (Highest Priority)

1. **Create format converter**
   - Convert 20190205 extraction to AI format
   - Save as comparison-ready file

2. **Locate source documents**
   - Find 20190205 agenda/minutes txt files
   - Verify they're readable

3. **Run first comparison**
   - Use compare_extractions.py
   - Generate initial accuracy baseline

4. **Document 3-5 key findings**
   - Start EXTRACTION_LESSONS_LEARNED.md
   - List immediate improvement opportunities

### This Week

1. Extract patterns from template vote sections
2. Update AI extractor with learned patterns
3. Re-test and measure improvement

### Next Week

1. Begin systematic template annotation
2. Build comprehensive training set
3. Achieve 90%+ accuracy on standard meetings

---

## 📚 Resources

**External Drive:**
- Source files: `/Volumes/Samsung USB/City_extraction/Santa_Ana/`
- Documentation: `README_MANUAL_EXTRACTION.md`
- Templates: `templates/`

**Project Files:**
- Manual extractions: `manual_extractions/santa_ana/`
- Comparison tool: `compare_extractions.py`
- Learning plan: `MANUAL_EXTRACTION_LEARNING_PLAN.md`
- AI Extractor: `agents/ai_powered_santa_ana_extractor.py`

---

## ✅ Session Goals - Updated

Based on what we have:

- [x] Import manual extraction files
- [x] Understand extraction formats
- [ ] Convert 20190205 to proper format
- [ ] Find source documents
- [ ] Run first comparison
- [ ] Document initial findings

**Realistic today:** Complete first comparison and identify 3-5 improvement opportunities

---

**Last Updated:** 2025-11-18
**Next Action:** Create format converter for 20190205 extraction
