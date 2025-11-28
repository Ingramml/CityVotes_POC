# Santa Ana Extraction Status - Combined Approach
**Date:** 2025-11-18
**Approach:** Combined (City-Year Organization + Fresh Start Quality)

---

## 📊 Current Status

### Existing Manual Extractions Organized

| Year | Files | Status | Next Steps |
|------|-------|--------|------------|
| **2014** | 1 file | ✅ Organized | Need source documents, run comparison |
| **2019** | 1 file | ✅ Organized | Need source documents, run comparison |
| **2021** | 4 files | ✅ Organized | Need source documents, run comparison |
| **2024** | 0 files | 📝 Ready for annotation | Select 3-5 meetings, annotate |

**Total Manual Extractions:** 6 files across 3 years

---

## 🎯 Recommended Priority Order

### Phase 1: Start with 2021 (HIGHEST PRIORITY)
**Why:**
- ✅ Most manual extractions (4 files)
- Most recent complete year with data
- Good baseline before tackling 2024

**Immediate Actions:**
1. Find source documents for 2021 extractions
2. Run AI comparison on all 4 files
3. Analyze accuracy baseline
4. Identify patterns and improvements

**Time:** 4-6 hours
**Expected Outcome:** Understand current AI accuracy, identify gaps

---

### Phase 2: Tackle 2024 (PRODUCTION FOCUS)
**Why:**
- Most important for current use
- Fresh start with perfect annotations
- Build on lessons from 2021

**Immediate Actions:**
1. Select 3-5 representative 2024 meetings
2. Manually annotate perfectly (use 2021 as guide)
3. Run AI comparison
4. Implement improvements
5. Achieve 95%+ accuracy

**Time:** 15-20 hours
**Expected Outcome:** Production-ready 2024 extractor

---

### Phase 3: Historical Years (OPTIONAL)
**2019 and 2014:**
- Only if needed for historical analysis
- Lower priority unless format insights needed

---

## 📁 Directory Structure Created

```
extractors/
├── santa_ana/
│   ├── 2014/
│   │   ├── training_data/
│   │   │   └── 20141118_annotation_walkthrough.json
│   │   ├── patterns/
│   │   ├── source_documents/  (need to find)
│   │   ├── ai_results/
│   │   └── comparisons/
│   │
│   ├── 2019/
│   │   ├── training_data/
│   │   │   └── 20190205_minutes_city_council_and_housing_authority_meetings_incl_votes.json
│   │   ├── patterns/
│   │   ├── source_documents/  (need to find)
│   │   ├── ai_results/
│   │   └── comparisons/
│   │
│   ├── 2021/
│   │   ├── training_data/
│   │   │   ├── 20210907_annotation_walkthrough.json
│   │   │   ├── template_1_20211005_minutes_regular_city_council_and_housing_authority_meeting.json
│   │   │   ├── template_2_20210907_minutes_regular_city_council_and_housing_authority_meetin.json
│   │   │   └── template_3_20210316_minutes_regular_city_council_meeting.json
│   │   ├── patterns/
│   │   ├── source_documents/  (need to find)
│   │   ├── ai_results/
│   │   └── comparisons/
│   │
│   └── 2024/
│       ├── training_data/  (ready for new annotations)
│       ├── patterns/
│       ├── source_documents/
│       ├── ai_results/
│       └── comparisons/
│
└── shared/
    └── (common utilities)
```

---

## 🚀 Immediate Next Steps (Start Here!)

### Step 1: Find Source Documents for 2021 (30 min)

```bash
# Search for 2021 source documents on external drive
find "/Volumes/Samsung USB/City_extraction/Santa_Ana" -name "*2021*" -name "*.txt" | grep -E "(agenda|minutes)"

# Copy found documents to appropriate folder
# Example:
cp "/Volumes/Samsung USB/City_extraction/Santa_Ana/PDF/text_files/20211005_minutes.txt" \\
   extractors/santa_ana/2021/source_documents/

cp "/Volumes/Samsung USB/City_extraction/Santa_Ana/PDF/text_files/20211005_agenda.txt" \\
   extractors/santa_ana/2021/source_documents/
```

---

### Step 2: Run First Comparison (30 min)

```bash
# For each 2021 manual extraction, run comparison
python compare_extractions.py \\
    extractors/santa_ana/2021/training_data/template_1_20211005_*.json \\
    extractors/santa_ana/2021/source_documents/20211005_agenda.txt \\
    extractors/santa_ana/2021/source_documents/20211005_minutes.txt

# Output will be in: extractors/santa_ana/2021/comparisons/
```

---

### Step 3: Analyze Baseline Results (1 hour)

Review comparison reports to understand:
- **Vote detection rate:** How many votes did AI find vs manual?
- **False positives:** Did AI extract things that aren't votes?
- **Accuracy:** How well do extracted votes match manual?
- **Common errors:** What patterns cause problems?

---

### Step 4: Document Findings (30 min)

Create: `extractors/santa_ana/2021/BASELINE_ANALYSIS.md`

Document:
- Overall accuracy metrics
- Top 5 failure types
- Patterns that work well
- Patterns that need improvement

---

### Step 5: Implement Improvements (2-3 hours)

Based on findings:
1. Add missing regex patterns to AI extractor
2. Expand member name variations
3. Handle special cases (consent calendar, etc.)
4. Update learning memory

---

### Step 6: Re-test and Measure Improvement (1 hour)

```bash
# Run comparisons again with improved extractor
python compare_extractions.py ...

# Compare before/after metrics
python tools/calculate_improvement.py \\
    --before extractors/santa_ana/2021/comparisons/baseline/ \\
    --after extractors/santa_ana/2021/comparisons/improved/
```

---

## 📋 Tracking Progress

### 2021 Extractions Checklist

- [ ] **20211005** (template_1)
  - [ ] Source documents located
  - [ ] Baseline comparison run
  - [ ] Accuracy measured
  - [ ] Improvements implemented
  - [ ] Final accuracy validated

- [ ] **20210907** (template_2 & walkthrough)
  - [ ] Source documents located
  - [ ] Baseline comparison run
  - [ ] Accuracy measured

- [ ] **20210316** (template_3)
  - [ ] Source documents located
  - [ ] Baseline comparison run
  - [ ] Accuracy measured

### 2024 Annotations Checklist

- [ ] Select 5 representative meetings
- [ ] Annotate meeting 1
- [ ] Annotate meeting 2
- [ ] Annotate meeting 3
- [ ] Annotate meeting 4
- [ ] Annotate meeting 5
- [ ] Run comparisons
- [ ] Achieve 95%+ accuracy

---

## 🎯 Success Metrics

### By End of Week 1 (2021 Focus)
- [ ] All 2021 comparisons complete
- [ ] Baseline accuracy measured
- [ ] Top 10 improvements identified
- [ ] Initial improvements implemented
- [ ] 10-20% accuracy improvement achieved

### By End of Week 2 (2024 Focus)
- [ ] 5 new 2024 meetings annotated
- [ ] 2024 comparisons complete
- [ ] Lessons from 2021 applied to 2024
- [ ] 90-95% accuracy on 2024 documents
- [ ] Production-ready 2024 extractor

---

## 🔧 Tools Available

### Created
- ✅ `compare_extractions.py` - Comparison tool
- ✅ City-year directory structure
- ✅ Organized manual extractions

### To Create
- [ ] `find_source_documents.py` - Auto-locate source files
- [ ] `batch_compare_year.py` - Compare all files in a year
- [ ] `calculate_improvement.py` - Before/after metrics
- [ ] `extract_year_patterns.py` - Learn patterns from year

---

## 💡 Tips for Success

### When Looking for Source Documents
```bash
# Try these searches on external drive
find "/Volumes/Samsung USB" -name "*20211005*"
find "/Volumes/Samsung USB" -name "*20210907*"
find "/Volumes/Samsung USB" -name "*20210316*"

# Look in these likely directories:
# - PDF/text_files/
# - docs/
# - documentation/
```

### When Running Comparisons
- Start with one file to test the process
- Make sure manual extraction format matches expected format
- Save comparison reports for later analysis
- Take notes on patterns you observe

### When Implementing Improvements
- Make small, targeted changes
- Test after each change
- Document what you changed and why
- Keep track of accuracy improvements

---

## 🎓 Learning Outcomes

By following this Combined Approach, you will:

1. ✅ **Understand current AI accuracy** (from 2021 baseline)
2. ✅ **Identify specific failure patterns** (from comparisons)
3. ✅ **Implement targeted improvements** (pattern by pattern)
4. ✅ **Validate improvements work** (measurable accuracy gains)
5. ✅ **Build production system** (95%+ accuracy on 2024)
6. ✅ **Create scalable process** (works for any city/year)

---

## 📞 Need Help?

If you get stuck:
1. Check the detailed plans (EXTRACTION_LEARNING_FRESH_START_PLAN.md, etc.)
2. Review comparison reports for clues
3. Look at template files for examples
4. Ask for guidance on specific issues

---

**Next Action:** Find source documents for 2021 extractions and run first comparison!

**Last Updated:** 2025-11-18
**Status:** Ready to begin Phase 1 (2021 baseline)
