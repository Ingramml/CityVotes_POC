# VoteExtractionAgent

## Overview

The VoteExtractionAgent is a sophisticated document processing agent designed to extract structured voting data from city council meeting documents. Based on comprehensive analysis of Santa Ana council meeting patterns, this agent handles the complex task of parsing agenda and minutes documents to produce validated, dashboard-ready voting records.

## Key Features

### 🎯 **Core Capabilities**
- **Document Processing**: Handles agenda and minutes document pairs
- **Vote Extraction**: Extracts motion details, vote outcomes, and member votes
- **Context Management**: Tracks member states, recusals, and role changes
- **Cross-Document Correlation**: Links agenda items with minutes vote records
- **Quality Validation**: Comprehensive validation with quality scoring
- **Dashboard Integration**: Outputs structured data for visualization

### 📊 **Advanced Features**
- **Motion Relationship Tracking**: Handles original motions, amendments, and substitute motions
- **Member State Management**: Tracks attendance, recusals, and temporary role changes
- **OCR Error Correction**: Built-in correction for common OCR errors
- **Format Adaptability**: Handles various meeting types and document formats
- **Temporal Context**: Maintains meeting timeline and event sequence

## Architecture

### Class Structure

```python
VoteExtractionAgent
├── Document Processing
│   ├── _load_document()
│   ├── _preprocess_agenda()
│   └── _preprocess_minutes()
├── Pattern Matching
│   ├── Motion patterns (MOTION: ... moved to ...)
│   ├── Vote result patterns (carried/failed, vote counts)
│   └── Member vote patterns (AYES:, NOES:, etc.)
├── Context Management
│   ├── MemberState tracking
│   ├── MotionContext tracking
│   └── Meeting state management
└── Output Generation
    ├── VoteRecord creation
    ├── Validation scoring
    └── Dashboard formatting
```

### Data Models

#### VoteRecord
```python
@dataclass
class VoteRecord:
    motion_id: str
    agenda_item_number: str
    agenda_item_title: str
    outcome: str  # 'Pass', 'Fail'
    vote_count: str  # '7-0', '4-3', etc.
    member_votes: Dict[str, str]  # member -> vote
    tally: Dict[str, int]  # vote type counts
    recusals: Dict[str, str]  # member -> reason
    motion_context: MotionContext
    validation_notes: List[str]
```

#### MotionContext
```python
@dataclass
class MotionContext:
    id: str
    type: str  # 'original', 'substitute', 'amendment'
    text: str
    mover: str
    seconder: str
    agenda_item: str
    parent_motion_id: Optional[str]
    timestamp: datetime
    status: str  # 'pending', 'voted', 'failed'
```

## Usage

### Basic Usage

```python
from agents.vote_extraction_agent import VoteExtractionAgent

# Initialize agent
agent = VoteExtractionAgent()

# Process meeting documents
result = agent.process_meeting_documents(
    agenda_path="path/to/agenda.txt",
    minutes_path="path/to/minutes.txt"
)

# Check results
if result['success']:
    votes = result['votes']
    print(f"Extracted {len(votes)} vote records")

    for vote in votes:
        print(f"Item {vote['agenda_item_number']}: {vote['outcome']}")
        print(f"  Motion by: {vote['mover']}")
        print(f"  Vote: {vote['vote_count']}")
else:
    print(f"Extraction failed: {result['message']}")
```

### Integration with File Upload

```python
def process_uploaded_documents(agenda_file, minutes_file, city_name):
    """Process uploaded documents through VoteExtractionAgent"""

    # Save uploaded files temporarily
    agenda_path = save_temp_file(agenda_file)
    minutes_path = save_temp_file(minutes_file)

    try:
        # Initialize agent
        agent = VoteExtractionAgent()

        # Process documents
        result = agent.process_meeting_documents(agenda_path, minutes_path)

        # Transform for dashboard
        if result['success']:
            dashboard_data = transform_for_dashboard(result)
            store_session_data(city_name, dashboard_data)
            return dashboard_data
        else:
            raise ProcessingError(result['message'])

    finally:
        # Cleanup temporary files
        cleanup_temp_files([agenda_path, minutes_path])
```

## Pattern Recognition

### Motion Patterns
The agent recognizes various motion formats:

```regex
MOTION: COUNCILMEMBER BACERRA moved to approve the budget,
        seconded by COUNCILMEMBER PHAN.
```

### Vote Result Patterns
```regex
The motion carried, 7-0, by the following roll call vote:
The motion failed, 3-4, by the following roll call vote:
```

### Member Vote Patterns
```
AYES: COUNCILMEMBER BACERRA, COUNCILMEMBER PHAN, MAYOR AMEZCUA
NOES: COUNCILMEMBER HERNANDEZ
ABSTAIN: NONE
ABSENT: NONE
```

## Validation and Quality Control

### Validation Checks
1. **Vote Count Consistency**: Reported counts vs. actual member votes
2. **Outcome Logic**: Pass/Fail consistency with vote tallies
3. **Member Participation**: All present members accounted for
4. **Motion Requirements**: Valid mover and seconder present
5. **Cross-Document Correlation**: Agenda-minutes item matching

### Quality Scoring
- **Quality Score**: Percentage of votes that pass all validations
- **Error Reporting**: Detailed validation notes for each issue
- **Threshold Management**: Configurable quality thresholds

```python
validation_results = {
    'total_votes': 5,
    'valid_votes': 4,
    'quality_score': 0.8,  # 80%
    'validation_errors': [
        'Vote count mismatch in item 3.2',
        'Missing seconder in item 5.1'
    ]
}
```

## Configuration

### Quality Thresholds
```python
quality_thresholds = {
    'min_content_length': 1000,      # Minimum document length
    'max_ocr_error_rate': 0.1,       # Maximum OCR error tolerance
    'min_vote_sections': 1,          # Minimum vote sections required
    'min_quality_score': 0.5         # Minimum overall quality score
}
```

### Pattern Customization
```python
# Custom patterns for different cities
custom_patterns = {
    'motion': re.compile(r"MOTION: (.+?) moved (.+?), seconded by (.+?)"),
    'vote_result': re.compile(r"motion (carried|failed), (\d+-\d+)"),
    # ... additional patterns
}

agent = VoteExtractionAgent()
agent.patterns.update(custom_patterns)
```

## Error Handling

### Common Issues and Solutions

1. **Document Quality Issues**
   ```python
   # Adjust quality thresholds for specific documents
   agent.quality_thresholds['min_content_length'] = 500
   ```

2. **OCR Errors**
   ```python
   # Add custom OCR corrections
   agent.member_name_corrections.update({
       'BACFRRA': 'BACERRA',
       'PH4N': 'PHAN'
   })
   ```

3. **Missing Vote Sections**
   ```python
   # Handle incomplete documents
   if not result['success']:
       logger.warning(f"Processing failed: {result['message']}")
       # Implement fallback processing or manual review
   ```

## Testing

### Integration Test
Run the comprehensive integration test:

```bash
python3 test_vote_extraction_integration.py
```

### Unit Tests
```python
# Test individual components
from agents.vote_extraction_agent import VoteExtractionAgent

agent = VoteExtractionAgent()

# Test pattern matching
motion_text = "MOTION: COUNCILMEMBER SMITH moved to approve..."
assert agent.patterns['motion'].search(motion_text)

# Test member name cleaning
clean_name = agent._clean_member_name("COUNCILMEMBER BACERRA")
assert clean_name == "Bacerra"
```

## Performance Considerations

### Processing Speed
- **Document Size**: Handles documents up to 50MB efficiently
- **Pattern Matching**: Optimized regex patterns for speed
- **Memory Usage**: Efficient memory management for large documents

### Scalability
- **Batch Processing**: Designed for processing multiple document pairs
- **Caching**: Supports result caching for repeated processing
- **Parallel Processing**: Thread-safe for concurrent document processing

## Integration Points

### Dashboard Pipeline
```python
def integrate_with_dashboard(extraction_result):
    """Transform extraction result for dashboard consumption"""

    return {
        'vote_summary': calculate_summary_metrics(extraction_result),
        'member_analysis': analyze_member_patterns(extraction_result),
        'raw_votes': extraction_result['votes']
    }
```

### File Upload System
```python
def handle_document_upload(agenda_file, minutes_file, city_name):
    """Handle document upload through VoteExtractionAgent"""

    agent = VoteExtractionAgent()
    result = agent.process_meeting_documents(
        save_upload(agenda_file),
        save_upload(minutes_file)
    )

    if result['success']:
        update_session_data(city_name, result)
        return redirect_to_dashboard()
    else:
        flash_error(result['message'])
        return redirect_to_upload()
```

## Future Enhancements

### Planned Features
1. **Machine Learning Integration**: Pattern recognition improvement
2. **Multi-Language Support**: Spanish council meetings
3. **Audio Processing**: Direct audio-to-votes extraction
4. **Historical Analysis**: Trend analysis across multiple meetings

### Advanced Capabilities
1. **Amendment Chain Tracking**: Complex motion relationship handling
2. **Real-time Processing**: Live meeting transcription processing
3. **Multi-City Standardization**: Unified processing across different cities

## Troubleshooting

### Common Issues

#### Low Quality Scores
```python
# Check validation errors
if result['validation_results']['quality_score'] < 0.5:
    errors = result['validation_results']['validation_errors']
    for error in errors:
        logger.warning(f"Validation issue: {error}")
```

#### Pattern Matching Failures
```python
# Debug pattern matching
text = "MOTION: COUNCILMEMBER SMITH moved..."
for pattern_name, pattern in agent.patterns.items():
    match = pattern.search(text)
    print(f"{pattern_name}: {match is not None}")
```

#### Missing Agenda Correlation
```python
# Check agenda item extraction
agenda_data = agent._preprocess_agenda(agenda_content)
print(f"Found {len(agenda_data['items'])} agenda items")
```

## Support and Documentation

### Key Resources
- **Santa Ana Documentation**: `Claude_transfer/Documentation/Santa_Ana_Voteextractor_info.md`
- **Integration Tests**: `test_vote_extraction_integration.py`
- **Pattern Examples**: Embedded in agent code with extensive comments

### Logging
Enable detailed logging for debugging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Agent will output detailed processing information
```

---

## Summary

The VoteExtractionAgent represents a sophisticated solution for extracting structured voting data from council meeting documents. Built on comprehensive analysis of Santa Ana meeting patterns, it provides:

- **Robust document processing** with quality validation
- **Sophisticated pattern recognition** for various vote formats
- **Context-aware processing** with member state tracking
- **Dashboard-ready output** with comprehensive validation
- **Extensible architecture** for multi-city deployment

The agent successfully bridges the gap between raw council meeting documents and structured data suitable for analysis and visualization, forming a critical component of the CityVotes POC platform.