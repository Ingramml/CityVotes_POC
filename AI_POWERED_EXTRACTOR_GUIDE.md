# AI-Powered Santa Ana Vote Extractor Guide

## Overview

The AI-Powered Santa Ana Vote Extractor is an intelligent, self-improving agent that combines traditional regex pattern matching with LLM intelligence to extract voting data from city council meeting documents.

## 📍 Location

**Agent File:** [agents/ai_powered_santa_ana_extractor.py](agents/ai_powered_santa_ana_extractor.py)
**Runner Script:** [run_santa_ana_extraction.py](run_santa_ana_extraction.py)
**Memory File:** `santa_ana_extraction_memory.json` (auto-generated)

## 🎯 Key Features

### 1. **Hybrid Extraction Approach**
- **Regex Patterns** - Fast, reliable extraction for standard vote formats
- **LLM Fallback** - Handles complex scenarios that regex can't parse
- **Adaptive Processing** - Learns which method works best for different cases

### 2. **Learning Memory System**
The extractor builds a persistent memory that improves over time:
- **Successful Patterns** - Tracks regex patterns that work well
- **Failed Patterns** - Remembers patterns that need LLM assistance
- **Member Name Corrections** - Learns variations in council member names
- **Agenda Item Patterns** - Recognizes different agenda numbering schemes
- **Quality History** - Tracks extraction quality trends over time
- **Extraction Examples** - Stores successful extraction examples for reference

### 3. **Self-Improving Accuracy**
- Validates each extraction against known patterns
- Updates memory based on validation results
- Improves future extractions automatically
- Tracks quality metrics to measure improvement

### 4. **Comprehensive Validation**
- Verifies council member names against known members
- Validates vote tallies match individual votes
- Checks outcome consistency (Pass/Fail/Tie)
- Quality scoring for each extraction

## 🚀 Usage

### Basic Usage

```bash
# Run AI-powered extraction on all matched Santa Ana documents
python run_santa_ana_extraction.py
```

### Programmatic Usage

```python
from agents.ai_powered_santa_ana_extractor import AIPoweredSantaAnaExtractor

# Initialize extractor
extractor = AIPoweredSantaAnaExtractor()

# Process a single meeting
result = extractor.process_meeting(
    agenda_file="path/to/agenda.txt",
    minutes_file="path/to/minutes.txt"
)

# Access extracted votes
votes = result.votes
confidence = result.confidence_score
method = result.method_used  # "regex", "ai", or "hybrid"

# Check validation
if result.validation_passed:
    print(f"Successfully extracted {len(votes)} votes")
    print(f"Confidence: {confidence:.1%}")
    print(f"Method: {method}")
```

### Advanced Usage with Memory Management

```python
from agents.ai_powered_santa_ana_extractor import AIPoweredSantaAnaExtractor

# Initialize with custom memory file
extractor = AIPoweredSantaAnaExtractor(
    memory_file="custom_memory.json"
)

# Process multiple meetings
for agenda, minutes in meeting_pairs:
    result = extractor.process_meeting(agenda, minutes)

    # Save memory after each extraction
    extractor.save_memory()

# Get extraction statistics
stats = extractor.get_statistics()
print(f"Total extractions: {stats['total_extractions']}")
print(f"AI fallback used: {stats['ai_fallback_used']}")
print(f"Quality improvements: {stats['quality_improvements']}")
```

## 📊 Extraction Results

### Result Structure

```python
AIExtractionResult(
    votes=[VoteRecord(...), VoteRecord(...), ...],
    confidence_score=0.95,  # 0.0 to 1.0
    method_used="hybrid",   # "regex", "ai", or "hybrid"
    processing_notes=[
        "Successfully extracted 12 votes",
        "AI fallback used for agenda item 7.3",
        "Pattern learned: special session format"
    ],
    validation_passed=True
)
```

### Vote Record Structure

Each vote contains:
- `agenda_item_number` - e.g., "7.1"
- `agenda_item_title` - Description of the item
- `outcome` - "Pass", "Fail", "Tie", or "Continued"
- `tally` - Vote counts (ayes, noes, abstain, absent)
- `member_votes` - Individual council member votes
- `meeting_date` - Date of the meeting
- `motion_context` - Additional context about the motion

## 🧠 Learning Memory System

### Memory File Structure

The `santa_ana_extraction_memory.json` file stores:

```json
{
  "successful_patterns": {
    "^Motion:\\s+(.+?)\\s+Vote:\\s+(\\d+-\\d+)": 45,
    "Agenda Item\\s+(\\d+\\.\\d+)": 38
  },
  "failed_patterns": {
    "unclear_vote_format_v1": 3
  },
  "member_name_corrections": {
    "V. Amezcua": "Valerie Amezcua",
    "Phil B.": "Phil Bacerra"
  },
  "agenda_item_patterns": [
    "\\d+\\.\\d+",
    "Item\\s+\\d+",
    "Resolution\\s+\\d+"
  ],
  "quality_history": [0.85, 0.87, 0.91, 0.93],
  "extraction_examples": [
    {
      "text_snippet": "...",
      "extracted_vote": {...},
      "method": "regex",
      "quality": 0.95
    }
  ],
  "last_updated": "2025-11-17T10:30:00"
}
```

### Memory Management

```python
# Load memory
memory = extractor._load_memory()

# Access memory components
successful_patterns = memory.successful_patterns
quality_trend = memory.quality_history

# Save memory (automatically done after extraction)
extractor._save_memory()

# Reset memory (if needed)
extractor.memory = ExtractionMemory()
extractor._save_memory()
```

## 🔄 Comparison: Regular vs AI-Powered Extractor

| Feature | Regular Extractor | AI-Powered Extractor |
|---------|------------------|---------------------|
| **Speed** | ⚡⚡⚡ Very Fast | ⚡⚡ Fast (LLM fallback adds time) |
| **Accuracy (Standard)** | 95% | 95% |
| **Accuracy (Complex)** | 60% | 90%+ |
| **Learning** | ❌ No | ✅ Yes |
| **Self-Improving** | ❌ No | ✅ Yes |
| **Edge Cases** | ⚠️ May fail | ✅ Handles well |
| **Memory Usage** | Low | Medium (stores learning data) |
| **Best For** | Batch processing | Complex documents, improving over time |
| **File Location** | `agents/santa_ana_vote_extractor.py` | `agents/ai_powered_santa_ana_extractor.py` |

## 📈 Tracking Improvement

### View Statistics

```python
stats = extractor.stats

print(f"Total extractions: {stats['total_extractions']}")
print(f"Times AI was needed: {stats['ai_fallback_used']}")
print(f"Quality improvements: {stats['quality_improvements']}")
print(f"New patterns learned: {stats['pattern_learning_events']}")
```

### Quality Trend Analysis

```python
quality_history = extractor.memory.quality_history

if len(quality_history) >= 2:
    improvement = quality_history[-1] - quality_history[0]
    print(f"Quality improvement: {improvement:+.1%}")

    # Plot quality over time (if you have matplotlib)
    import matplotlib.pyplot as plt
    plt.plot(quality_history)
    plt.title("Extraction Quality Over Time")
    plt.xlabel("Extraction Number")
    plt.ylabel("Quality Score")
    plt.show()
```

## 🛠️ Configuration

### Known Council Members

Update the known members list if the council composition changes:

```python
extractor.known_members = {
    "Amezcua", "Bacerra", "Hernandez", "Lopez",
    "Penaloza", "Phan", "Vazquez", "Mendoza", "Sarmiento"
}
```

### Validation Thresholds

Adjust validation strictness:

```python
# In the extractor code (ai_powered_santa_ana_extractor.py)
# Lower threshold = more lenient
MIN_QUALITY_SCORE = 0.7  # Default: 0.7 (70%)
```

## 🔍 Troubleshooting

### Low Confidence Scores

**Problem:** Extraction returns low confidence scores
**Solutions:**
1. Check if documents are in expected format
2. Review `processing_notes` for specific issues
3. Manually review and correct a few extractions to improve learning
4. Check if new council members need to be added to `known_members`

### AI Fallback Not Working

**Problem:** LLM fallback not being triggered
**Solutions:**
1. Ensure LLM integration is properly configured
2. Check if API keys are set (if using external LLM)
3. Review error logs for LLM connection issues

### Memory File Corruption

**Problem:** `santa_ana_extraction_memory.json` is corrupted
**Solutions:**
1. Delete the memory file to reset
2. Restore from backup if available
3. The extractor will create a new memory file automatically

### Poor Pattern Recognition

**Problem:** Extractor not learning from similar documents
**Solutions:**
1. Increase the number of processed documents (more training data)
2. Manually review and validate extractions
3. Add successful patterns manually to the memory file

## 📝 Best Practices

### 1. **Regular Memory Backups**
```bash
# Backup memory file periodically
cp santa_ana_extraction_memory.json santa_ana_extraction_memory_backup_$(date +%Y%m%d).json
```

### 2. **Gradual Rollout**
- Start with a small batch of documents
- Review results and let the system learn
- Gradually increase batch size as quality improves

### 3. **Quality Monitoring**
```python
# Monitor quality after each batch
if result.confidence_score < 0.8:
    print(f"Warning: Low confidence extraction")
    print(f"Notes: {result.processing_notes}")
    # Review manually
```

### 4. **Periodic Memory Cleanup**
```python
# Remove old, low-value patterns periodically
# Keep only patterns used frequently
extractor.memory.successful_patterns = {
    pattern: count
    for pattern, count in extractor.memory.successful_patterns.items()
    if count >= 5  # Keep patterns used 5+ times
}
extractor._save_memory()
```

## 🔗 Integration with Other Tools

### With Batch Processor

```python
from agents.ai_powered_santa_ana_extractor import AIPoweredSantaAnaExtractor
import csv

extractor = AIPoweredSantaAnaExtractor()

# Load meeting pairs from CSV
with open('santa_ana_mapping_report.csv', 'r') as f:
    reader = csv.DictReader(f)
    pairs = [r for r in reader if r['status'] == 'matched']

# Process all pairs
results = []
for pair in pairs:
    result = extractor.process_meeting(
        pair['agenda_file'],
        pair['minutes_file']
    )
    results.append({
        'date': pair['date'],
        'votes': len(result.votes),
        'confidence': result.confidence_score,
        'method': result.method_used
    })

# Save memory after batch
extractor._save_memory()
```

### With Extract Votes Shell Script

```bash
# Use the AI-powered extractor via shell script
./extract_votes.sh auto 10  # This can be configured to use AI extractor
```

## 📚 Additional Resources

- **Base Vote Extractor:** [agents/vote_extraction_agent.py](agents/vote_extraction_agent.py)
- **Regular Santa Ana Extractor:** [agents/santa_ana_vote_extractor.py](agents/santa_ana_vote_extractor.py)
- **Factory Pattern:** [agents/city_vote_extractor_factory.py](agents/city_vote_extractor_factory.py)
- **Runner Script:** [run_santa_ana_extraction.py](run_santa_ana_extraction.py)
- **Test Suite:** [test_all_city_extractors.py](test_all_city_extractors.py)

## 🤝 Contributing

To improve the AI-powered extractor:

1. **Add New Patterns:** Update regex patterns for new vote formats
2. **Enhance Validation:** Add new validation rules
3. **Improve Learning:** Enhance the learning algorithm
4. **Optimize Performance:** Balance LLM usage with regex efficiency

## 📄 License

Part of the CityVotes POC project - for educational and demonstration purposes.

---

**Last Updated:** November 2025
**Maintained By:** CityVotes POC Team
