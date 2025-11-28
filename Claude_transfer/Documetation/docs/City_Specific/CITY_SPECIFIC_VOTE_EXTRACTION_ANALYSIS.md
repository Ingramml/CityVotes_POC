# City-Specific Vote Extraction Sub-Agents: Architecture Analysis

## Executive Summary

**Yes, using sub-agents per city for vote extraction makes strong architectural and practical sense.** Each city has unique formatting, layout patterns, terminology, and document structures that require specialized extraction logic. This document analyzes the benefits and implementation strategies for city-specific vote extraction sub-agents.

## Why City-Specific Sub-Agents Are Optimal

### 1. **Document Format Variations**

Each city produces meeting minutes with distinct characteristics:

#### **Santa Ana Characteristics:**
- PDF format with consistent header structure
- Vote results typically in table format
- Member names listed with titles (Mayor, Councilmember)
- Specific terminology: "Motion carried 6-1" vs "Passed 6-1"
- Agenda item numbering: "Item 22", "22.", "22)"
- Roll call votes listed individually

#### **Pomona Characteristics:**
- Text-based minutes format
- Vote results embedded in narrative text
- Different member naming conventions
- Unique agenda item structures
- Bulk consent calendar handling

#### **Phoenix/Glendale/Other Cities:**
- Each has proprietary meeting minute templates
- Different PDF generators create unique extraction challenges
- Varying vote recording methods (tables vs. narrative vs. structured lists)
- City-specific legal terminology and procedures

### 2. **Pattern Recognition Benefits**

City-specific agents can:
- **Learn city-specific layouts** and adapt extraction accordingly
- **Recognize city-specific vote patterns** (unanimous consent, roll calls, voice votes)
- **Handle city-specific exceptions** (recusals, late arrivals, procedural votes)
- **Understand local terminology** and voting procedures

### 3. **Error Reduction**

Specialized agents reduce extraction errors by:
- **Eliminating cross-contamination** between city formats
- **Focused validation rules** tailored to each city's standards
- **City-specific quality assurance** patterns
- **Targeted debugging** when issues arise

## Proposed Architecture: City-Specific Extraction Sub-Agents

```
┌─────────────────────────────────────────────────┐
│              Vote Extraction Manager            │
│            (Orchestrator Agent)                 │
└─────────────────┬───────────────────────────────┘
                  │
    ┌─────────────┼─────────────────────────────────┐
    │             │                                 │
    ▼             ▼                                 ▼
┌─────────┐  ┌─────────┐  ┌─────────┐         ┌─────────┐
│ Santa   │  │ Pomona  │  │ Phoenix │  . . .  │  City   │
│ Ana     │  │ Extract │  │ Extract │         │ Extract │
│ Extract │  │ Agent   │  │ Agent   │         │ Agent N │
│ Agent   │  └─────────┘  └─────────┘         └─────────┘
└─────────┘
     │
     ▼
┌─────────────────────────────────────────────────┐
│         Validation & Standardization            │
│              (Post-Process Agent)               │
└─────────────────────────────────────────────────┘
```

## Implementation Strategy

### 1. **Base Extraction Agent Class**

```python
from abc import ABC, abstractmethod

class BaseVoteExtractionAgent(ABC):
    def __init__(self, city_name: str):
        self.city_name = city_name
        self.patterns = self.load_city_patterns()
        self.validators = self.load_city_validators()
    
    @abstractmethod
    def extract_votes(self, text_content: str) -> List[VoteRecord]:
        """Extract votes from city-specific text format"""
        pass
    
    @abstractmethod
    def preprocess_text(self, raw_text: str) -> str:
        """City-specific text preprocessing"""
        pass
    
    @abstractmethod
    def validate_extraction(self, votes: List[VoteRecord]) -> bool:
        """City-specific validation rules"""
        pass
    
    def standardize_output(self, votes: List[VoteRecord]) -> List[Dict]:
        """Convert to universal JSON format"""
        return [vote.to_universal_format() for vote in votes]
```

### 2. **City-Specific Implementations**

#### **Santa Ana Extraction Agent**

```python
class SantaAnaExtractionAgent(BaseVoteExtractionAgent):
    def __init__(self):
        super().__init__("santa_ana")
        self.member_patterns = {
            "mayor": r"Mayor\s+([A-Za-z\s]+)",
            "councilmember": r"Councilmember\s+([A-Za-z\s]+)"
        }
        self.vote_patterns = {
            "item_header": r"Item\s+(\d+)[:\.\)]?\s*(.+?)(?=\n)",
            "motion": r"Motion\s+(?:by|made by)\s+([^,]+),\s*seconded\s+by\s+([^\.]+)",
            "roll_call": r"(?:Roll\s+call|Vote):\s*(.+?)(?=\n|\.|Motion)",
            "outcome": r"Motion\s+(carried|failed|passed)\s+(\d+-\d+(?:-\d+)?)"
        }
    
    def extract_votes(self, text_content: str) -> List[VoteRecord]:
        preprocessed = self.preprocess_text(text_content)
        votes = []
        
        # Extract agenda items
        items = re.finditer(self.vote_patterns["item_header"], preprocessed)
        
        for item_match in items:
            vote_record = self._extract_single_vote(item_match, preprocessed)
            if vote_record and self.validate_extraction([vote_record]):
                votes.append(vote_record)
        
        return votes
    
    def preprocess_text(self, raw_text: str) -> str:
        # Santa Ana specific preprocessing
        # - Fix OCR errors common in Santa Ana PDFs
        # - Standardize spacing around vote counts
        # - Handle page breaks in vote sections
        
        corrections = {
            r"Gouncilmember": "Councilmember",  # Common OCR error
            r"(\d)\s*-\s*(\d)": r"\1-\2",       # Standardize vote counts
            r"Motion\s+carired": "Motion carried"  # Another OCR error
        }
        
        processed = raw_text
        for pattern, replacement in corrections.items():
            processed = re.sub(pattern, replacement, processed)
        
        return processed
    
    def validate_extraction(self, votes: List[VoteRecord]) -> bool:
        for vote in votes:
            # Santa Ana specific validation
            if not vote.agenda_item_number:
                return False
            if vote.total_members != 7:  # Santa Ana has 7 council members
                return False
            if not self._valid_santa_ana_member_names(vote.member_votes):
                return False
        return True
```

#### **Pomona Extraction Agent**

```python
class PomonaExtractionAgent(BaseVoteExtractionAgent):
    def __init__(self):
        super().__init__("pomona")
        self.text_format = True  # Pomona uses text, not PDF
        self.narrative_patterns = {
            # Pomona embeds votes in narrative text
            "embedded_vote": r"([A-Za-z\s]+)\s+moved\s+(.+?)\.\s*([A-Za-z\s]+)\s+seconded\.\s*(.+?)(?=\n|[A-Z])",
            "vote_result": r"(?:Motion|Vote)\s+(passed|failed|carried)\s*(?:by\s+)?(?:a\s+vote\s+of\s+)?(\d+-\d+(?:-\d+)?)?",
            "member_vote": r"([A-Za-z\s]+):\s*(aye|nay|abstain|absent)"
        }
    
    def extract_votes(self, text_content: str) -> List[VoteRecord]:
        # Pomona-specific extraction logic for narrative text format
        votes = []
        
        # Split by agenda items (Pomona uses different numbering)
        sections = self._split_by_agenda_items(text_content)
        
        for section in sections:
            if self._contains_vote(section):
                vote_record = self._extract_narrative_vote(section)
                if vote_record:
                    votes.append(vote_record)
        
        return votes
    
    def preprocess_text(self, raw_text: str) -> str:
        # Pomona specific preprocessing for text format
        # - Handle line breaks in member names
        # - Standardize vote terminology
        # - Clean up formatting artifacts
        
        processed = raw_text.replace('\r\n', '\n')
        processed = re.sub(r'\n\s*\n', '\n', processed)  # Remove extra line breaks
        
        return processed
```

### 3. **Orchestrator Agent**

```python
class VoteExtractionManager:
    def __init__(self):
        self.extractors = {
            'santa_ana': SantaAnaExtractionAgent(),
            'pomona': PomonaExtractionAgent(),
            'phoenix': PhoenixExtractionAgent(),
            'glendale': GlendaleExtractionAgent()
        }
        self.post_processor = PostProcessingAgent()
    
    def extract_votes(self, city_name: str, file_path: str) -> Dict:
        """Orchestrate vote extraction for specific city"""
        
        if city_name not in self.extractors:
            raise ValueError(f"No extractor available for {city_name}")
        
        # Get city-specific extractor
        extractor = self.extractors[city_name]
        
        # Read and preprocess file
        raw_text = self._read_file(file_path)
        
        # Extract votes using city-specific agent
        votes = extractor.extract_votes(raw_text)
        
        # Post-process and standardize
        standardized_votes = self.post_processor.standardize(votes, city_name)
        
        # Validate final output
        validation_results = self.post_processor.validate(standardized_votes)
        
        return {
            'city': city_name,
            'votes': standardized_votes,
            'extraction_metadata': {
                'total_votes_found': len(votes),
                'validation_passed': validation_results['passed'],
                'warnings': validation_results['warnings'],
                'extractor_version': extractor.version
            }
        }
```

## Benefits of City-Specific Approach

### 1. **Specialization Advantages**
- **Higher accuracy** due to format-specific optimization
- **Better error handling** for known city-specific issues
- **Faster development** with focused scope per agent
- **Easier maintenance** and updates per city

### 2. **Scalability Benefits**
- **Independent development** of new city extractors
- **Parallel processing** of multiple cities
- **Modular testing** and validation
- **Version control** per city extractor

### 3. **Quality Assurance**
- **City-specific test suites** with known good examples
- **Targeted debugging** when extraction fails
- **Focused optimization** for each city's unique challenges
- **Independent performance metrics** per city

### 4. **Flexibility**
- **Different extraction strategies** per city (regex vs. ML vs. hybrid)
- **City-specific preprocessing** pipelines
- **Customized validation rules** per city
- **Independent update cycles** for each city

## Implementation Timeline

### **Phase 1: Core Infrastructure (Week 1)**
- Build base extraction agent class
- Implement orchestrator agent
- Create standardization/validation framework
- Set up testing infrastructure

### **Phase 2: Santa Ana Agent (Week 1-2)**
- Implement Santa Ana specific extractor
- Test against known Santa Ana documents
- Optimize patterns and validation rules
- Document extraction accuracy metrics

### **Phase 3: Pomona Agent (Week 2-3)**
- Implement Pomona specific extractor
- Handle text format vs. PDF differences
- Test against Pomona meeting minutes
- Cross-validate with Santa Ana format differences

### **Phase 4: Additional Cities (Ongoing)**
- Phoenix, Glendale, Columbus agents
- Each city gets dedicated implementation sprint
- Independent testing and optimization
- Performance benchmarking per city

## Technical Considerations

### **Memory and Performance**
- Load extractors on-demand to save memory
- Cache compiled regex patterns per city
- Parallel processing for multiple documents
- Streaming processing for large documents

### **Error Handling**
- City-specific error recovery strategies
- Fallback to generic extractor if city-specific fails
- Detailed logging per city extractor
- User feedback for extraction quality

### **Maintenance**
- Version tracking per city extractor
- A/B testing for extraction improvements
- City-specific performance dashboards
- Automated regression testing per city

## Conclusion

**City-specific vote extraction sub-agents are the optimal architecture** for this project because:

1. **Each city has unique document formats** requiring specialized handling
2. **Accuracy improves significantly** with city-specific optimization
3. **Development becomes more manageable** with focused scope per agent
4. **Scaling to new cities** is straightforward and independent
5. **Maintenance and debugging** are simplified with specialized agents

This approach transforms a complex, multi-format extraction problem into manageable, city-specific challenges that can be solved independently and optimized specifically for each city's unique characteristics.

The investment in building city-specific agents pays dividends in extraction accuracy, maintainability, and the ability to rapidly onboard new cities with their unique formatting requirements.