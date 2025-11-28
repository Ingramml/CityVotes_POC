# Agent vs Skill: Santa Ana Manual Extraction

**Date:** 2025-11-27
**Decision:** Which approach for manual Santa Ana vote extraction?
**Options:** Task Agent vs Skill

---

## TL;DR Recommendation

**USE AN AGENT** 🎯

**Reasoning:**
Manual extraction is a **complex, multi-step research task** that requires autonomous exploration, decision-making, and adaptation. Agents are specifically designed for this type of work.

---

## Decision Matrix

| Factor | Agent | Skill | Winner |
|--------|-------|-------|--------|
| **Task Complexity** | ✅ High complexity | ❌ Simple, repeatable | **Agent** |
| **Exploration Needed** | ✅ Must explore docs | ❌ Fixed workflow | **Agent** |
| **Iteration Required** | ✅ Multi-step process | ❌ Single execution | **Agent** |
| **Autonomy Needed** | ✅ Independent decisions | ❌ User-guided | **Agent** |
| **Tool Access** | ✅ All tools | ⚠️ Limited tools | **Agent** |
| **State Management** | ✅ Maintains context | ❌ Stateless | **Agent** |
| **Error Recovery** | ✅ Can adapt | ❌ Fixed flow | **Agent** |
| **Learning Capability** | ✅ Improves over time | ❌ Static | **Agent** |

**Final Score:** Agent wins 8/8 categories

---

## What is Manual Extraction?

Manual extraction for Santa Ana meetings involves:

1. **Reading meeting minutes** - Navigate through 20-100 pages
2. **Identifying vote sections** - Find consent calendar, pulled items, regular votes
3. **Parsing vote data** - Extract agenda item numbers, outcomes, tallies, member votes
4. **Handling exceptions** - Deal with amended items, recusals, special cases
5. **Cross-referencing agendas** - Match items to titles and descriptions
6. **Validating data quality** - Check for duplicates, missing data, inconsistencies
7. **Formatting output** - Structure data into CSV/JSON
8. **Iterating on errors** - Fix issues found during validation

**This is NOT a simple, repeatable task.**

---

## Why Agent is Better

### 1. Complex Multi-Step Workflow

**What Manual Extraction Requires:**

```
1. Read minutes document (20-100 pages)
2. Locate consent calendar section
3. Parse range: "Items 8 through 41"
4. Parse exceptions: "except 10, 11, 15"
5. Calculate approved items: [8,9,12,13,14,16,...,41]
6. For each item:
   a. Read agenda to get title
   b. Extract vote tally
   c. Check for recusals
   d. Format record
7. Locate pulled items section
8. For each pulled item:
   a. Parse discussion
   b. Extract individual votes
   c. Handle amendments
9. Validate all records
10. Output to CSV/JSON
```

**Agent Capability:** ✅ Can execute all steps autonomously
**Skill Capability:** ❌ Too complex for linear execution

---

### 2. Exploration and Discovery

**Challenges:**
- Vote sections aren't always in the same place
- Format variations between meetings
- Different wording for same concepts
- Need to search for specific text patterns

**Agent Approach:**
```python
# Agent can explore autonomously
agent.search_for_pattern("consent calendar")
agent.read_section(start_line, end_line)
agent.identify_vote_format()
agent.adapt_extraction_strategy()
```

**Skill Approach:**
```python
# Skill follows fixed steps
1. Read file X
2. Search for pattern Y
3. Extract using regex Z
# (Breaks if format changes)
```

**Winner:** Agent - Can adapt to variations

---

### 3. Iteration and Refinement

**Real Scenario:**

```
Iteration 1: Extract 20 votes
Iteration 2: Realize missed consent calendar
Iteration 3: Re-extract, now have 40 votes
Iteration 4: Find 5 duplicates, deduplicate
Iteration 5: Notice Excused Absences should be excluded
Iteration 6: Filter and re-validate
Final: 37 votes (correct)
```

**Agent:** ✅ Can iterate within same execution
**Skill:** ❌ Would require 6 separate skill invocations

---

### 4. Autonomous Decision Making

**Decisions Manual Extraction Makes:**

- Is this a consent calendar vote or regular vote?
- Should this item be excluded? (Excused Absences, Minutes, etc.)
- Is this item number a duplicate?
- Is this tally format "7-0" or "7-0-0-0"?
- Should I search agenda or minutes for this info?
- Is this member name valid or a title that needs cleaning?

**Agent:** ✅ Can make decisions based on context
**Skill:** ❌ Requires all decisions pre-programmed

---

### 5. Error Handling and Recovery

**Common Errors:**

- Pattern doesn't match (format variation)
- Missing data (incomplete minutes)
- Duplicate records (need deduplication)
- Invalid member names (need validation)
- Inconsistent numbering (skip or interpolate?)

**Agent Response:**
```
1. Try pattern A
2. If fails, try pattern B
3. If still fails, use AI fallback
4. Validate results
5. If quality low, retry with different approach
```

**Skill Response:**
```
1. Try pattern A
2. Error: Pattern not found
3. Skill exits
4. User must debug and re-invoke
```

**Winner:** Agent - Self-correcting

---

### 6. State and Context Management

**Manual Extraction State:**

```python
{
  "current_meeting": "20240220",
  "votes_found": 37,
  "duplicates_removed": 5,
  "excluded_items": ["8 (Excused)", "9 (Minutes)"],
  "patterns_tried": ["pattern_1", "pattern_2"],
  "validation_status": "passing",
  "next_step": "validate_member_names"
}
```

**Agent:** ✅ Maintains full state throughout execution
**Skill:** ❌ Stateless - loses context between invocations

---

### 7. Tool Access

**Tools Needed for Manual Extraction:**

- **Read** - Read minutes and agenda files
- **Grep** - Search for vote patterns
- **Bash** - Run Python extraction scripts
- **Write** - Save output CSV/JSON
- **Edit** - Fix errors in output
- **Task** - Delegate sub-tasks (optional)

**Agent:** ✅ Has access to ALL tools
**Skill:** ⚠️ Has access to all tools BUT linear execution limits usefulness

---

### 8. Learning and Improvement

**Over Multiple Meetings:**

```
Meeting 1 (2/20/24):
- Learn: Consent calendar format
- Learn: Exception handling pattern
- Result: 97.4% recall

Meeting 2 (3/5/24):
- Apply learned patterns
- Discover: Different consent wording
- Adapt: Add new pattern to library
- Result: 65.4% recall (manual data issues)

Meeting 3 (8/20/24):
- Apply all learned patterns
- Discover: New format variation
- Adapt: Add pattern 3
- Result: 126.7% recall (need deduplication fix)
```

**Agent:** ✅ Can maintain and apply learned patterns across invocations (with proper setup)
**Skill:** ❌ Static - cannot learn or adapt

---

## Agent Architecture Recommendation

### Agent Type: `santa-ana-manual-extractor`

**Purpose:** Autonomously extract vote records from Santa Ana meeting minutes and agendas

**Capabilities:**
- Multi-step extraction workflow
- Pattern discovery and matching
- Data validation and quality checks
- Error recovery and retry logic
- Output formatting (CSV/JSON)

**Tools Available:**
- All tools (Read, Grep, Bash, Write, Edit, Task)

**Example Usage:**

```python
# User invokes agent
/task santa-ana-manual-extractor "Extract votes from 2/20/24 meeting"

# Agent executes autonomously:
# 1. Read minutes and agenda
# 2. Search for consent calendar
# 3. Parse vote records
# 4. Validate and deduplicate
# 5. Output CSV
# 6. Report results
```

**Benefits:**
- ✅ Single invocation for entire process
- ✅ Handles errors automatically
- ✅ Adapts to format variations
- ✅ Provides detailed progress updates
- ✅ Learns from previous extractions

---

## When Would a Skill Be Appropriate?

Skills are best for **simple, repeatable tasks** with:
- Fixed input/output
- Single-step execution
- No exploration needed
- No error recovery required

**Examples of Skill-Appropriate Tasks:**

1. **Convert PDF to Text**
   - Input: PDF file path
   - Output: Text file
   - Simple, repeatable

2. **Format CSV Column**
   - Input: CSV file, column name
   - Output: Formatted CSV
   - Single transformation

3. **Validate JSON Schema**
   - Input: JSON file, schema
   - Output: Validation result
   - Boolean check

**Manual extraction is NOT skill-appropriate because:**
- ❌ Not simple (10+ steps)
- ❌ Not repeatable (format varies)
- ❌ Requires exploration
- ❌ Requires error recovery

---

## Skill Architecture (If You Insisted)

**IF** you absolutely had to use a skill (not recommended):

### Skill: `extract-santa-ana-votes`

**Workflow:**
```
1. User provides: meeting date, minutes path, agenda path
2. Skill executes fixed extraction script
3. Outputs CSV to predefined location
4. Reports success/failure
```

**Problems:**
- ⚠️ Fixed workflow cannot adapt
- ⚠️ No error recovery
- ⚠️ No iteration capability
- ⚠️ User must handle failures manually
- ⚠️ Cannot learn or improve

**When This Might Work:**
- All meetings have IDENTICAL format
- No edge cases or variations
- No validation needed
- User accepts failures

**Reality:** Santa Ana meetings have format variations, so this will fail frequently.

---

## Comparison Example

### Task: Extract votes from 8/20/24 meeting

**Agent Approach:**

```
Agent: Reading minutes...
Agent: Found consent calendar: "Consent Calendar Items: 8 through 37"
Agent: Pattern 1 didn't match, trying Pattern 2...
Agent: Pattern 2 matched! Extracting 29 consent items...
Agent: Searching for pulled items...
Agent: Found 5 pulled items (24, 25, 29, 31, 39)
Agent: Validating results...
Agent: Warning: Item 8 is "Excused Absences" - excluding
Agent: Warning: Item 9 is "Minutes" - excluding
Agent: After filtering: 27 consent + 5 pulled = 32 votes
Agent: Validation passed! Writing to CSV...
Agent: Complete: 32 votes extracted
```

**Skill Approach:**

```
Skill: Executing extraction script...
Skill: Error: Pattern "moved to approve Consent Calendar Item Nos." not found
Skill: Execution failed

User: *Reads error, updates pattern, re-invokes skill*

Skill: Executing extraction script...
Skill: Extracted 37 votes
Skill: Complete

User: *Checks output, finds Excused Absences included*
User: *Manually removes 2 items*
User: *Finds duplicates*
User: *Manually deduplicates*
User: Final count: 32 votes
```

**Winner:** Agent - Handles variations and validation autonomously

---

## Cost Comparison

### Agent
- **Invocations:** 1
- **User time:** 0 minutes (autonomous)
- **Token usage:** Higher (more LLM calls)
- **Success rate:** Higher (adaptive)

### Skill
- **Invocations:** 2-5 (iterations to fix errors)
- **User time:** 10-20 minutes (debugging and manual fixes)
- **Token usage:** Lower per invocation (but more invocations)
- **Success rate:** Lower (rigid approach)

**Overall:** Agent is more cost-effective due to:
- ✅ Fewer total iterations
- ✅ Less user time
- ✅ Higher success rate
- ✅ Better quality output

---

## Edge Cases That Require Agent

### Edge Case 1: Format Variation

**Scenario:** Meeting uses new consent calendar wording

**Agent:**
```
1. Try known patterns
2. Patterns fail
3. Search for "consent" keyword
4. Analyze surrounding text
5. Infer new pattern
6. Extract successfully
7. Log new pattern for future
```

**Skill:**
```
1. Try fixed pattern
2. Pattern fails
3. Exit with error
4. User must update skill code
```

---

### Edge Case 2: Missing Data

**Scenario:** Agenda file has no titles for items 15-20

**Agent:**
```
1. Notice missing titles
2. Search minutes for context
3. Use generic titles: "Agenda Item 15"
4. Log warning for user review
5. Continue extraction
```

**Skill:**
```
1. Attempt title lookup
2. Find null/empty
3. Possibly crash or create bad data
4. User must manually fix
```

---

### Edge Case 3: Duplicate Detection

**Scenario:** Combined City Council + Housing Authority meeting

**Agent:**
```
1. Extract City Council votes: 40 items
2. Extract Housing Authority votes: 30 items
3. Detect 26 duplicate item numbers
4. Deduplicate using strategy
5. Output: 44 unique votes
6. Report: "Removed 26 duplicates"
```

**Skill:**
```
1. Extract all votes
2. Output 70 items (with duplicates)
3. User notices problem
4. User manually deduplicates
```

---

## Final Recommendation

### ✅ USE AN AGENT

**Recommended Agent Configuration:**

```python
{
  "agent_name": "santa-ana-manual-extractor",
  "agent_type": "general-purpose",  # Or create specialized type
  "description": "Extract vote records from Santa Ana meeting minutes",
  "tools": ["*"],  # All tools available
  "thoroughness": "very thorough",  # High quality extraction
  "autonomous": True,  # Can make decisions without user
  "learning_enabled": True,  # Improve over time
  "validation_required": True  # Always validate output
}
```

**Usage Pattern:**

```bash
# User invokes once
claude code /task santa-ana-manual-extractor \
  "Extract votes from meeting 2/20/24. Minutes: path/to/minutes.txt, Agenda: path/to/agenda.txt"

# Agent runs autonomously
# User receives completed CSV/JSON output
```

---

## Alternative: Hybrid Approach

If you want to leverage both approaches:

### Option: Agent + Skill

1. **Agent** handles complex extraction workflow
2. **Skill** handles simple post-processing

**Example:**

```bash
# Agent extracts votes
/task santa-ana-manual-extractor "Extract from 2/20/24"
# Output: raw_votes.json

# Skill formats output
/skill format-vote-csv --input raw_votes.json --output final_votes.csv
```

**Benefit:** Separation of concerns
**Drawback:** Added complexity

**Recommendation:** Stick with Agent-only approach for simplicity.

---

## Summary

| Aspect | Agent | Skill |
|--------|-------|-------|
| **Best For** | Complex, multi-step tasks | Simple, repeatable tasks |
| **Santa Ana Manual Extraction** | ✅ IDEAL | ❌ NOT SUITABLE |
| **Autonomy** | High | Low |
| **Error Handling** | Adaptive | None |
| **Learning** | Yes | No |
| **Tool Access** | Full | Full (but limited by linear flow) |
| **User Intervention** | Minimal | Frequent |
| **Success Rate** | High | Low (for this task) |
| **Recommended** | **YES** 🎯 | NO |

---

## Implementation Next Steps

If proceeding with Agent approach:

1. **Create agent specification**
   - Define input/output format
   - Document extraction workflow
   - Specify validation criteria

2. **Build agent prompt**
   - Clear task description
   - Step-by-step instructions
   - Edge case handling
   - Output format requirements

3. **Test on sample meetings**
   - Start with 2/20/24 (known good)
   - Test on 3/5/24 (challenging)
   - Test on 8/20/24 (format variation)

4. **Iterate and improve**
   - Capture learned patterns
   - Add to agent knowledge base
   - Refine error handling

5. **Deploy for production**
   - Run on all 2024 meetings
   - Expand to 2023, 2022
   - Monitor quality metrics

---

## Conclusion

For Santa Ana manual vote extraction, an **Agent is the clear choice**. The task is too complex, variable, and iterative for a Skill's linear execution model. An Agent provides the autonomy, adaptability, and error recovery needed to successfully extract votes from meetings with varying formats.

**Decision:** ✅ **IMPLEMENT AS AGENT**

---

**Prepared by:** Claude (AI Assistant)
**Date:** 2025-11-27
**Status:** Recommendation complete
**Next:** Implement santa-ana-manual-extractor agent
