# Master Implementation Prompt for Two-City Vote Tracker POC

## Document Source Map
This implementation prompt combines key information from the following source documents:
- `TWO_CITY_POC_PRD.md` - Core requirements and project scope
- `TWO_CITY_POC_SUBAGENT_ARCHITECTURE.md` - System design and components
- `TWO_CITY_IMPLEMENTATION_GUIDE.md` - Technical implementation details
- `MANUAL_ANNOTATION_GUIDE.md` - Data standards and JSON format
- `POC_BLIND_SPOT_REMEDIATION_PLAN.md` - Security and production considerations
- `CITY_SPECIFIC_VOTE_EXTRACTION_ANALYSIS.md` - City-specific processing logic

---

## Implementation Prompt

### PROJECT CONTEXT AND REQUIREMENTS
[Source: TWO_CITY_POC_PRD.md]

Create a proof of concept web platform for analyzing city council voting data for Santa Ana and Pomona, California.

**Project Specifications:**
- Timeline: 2 weeks
- Tech Stack: Python/Flask backend, HTML/CSS/JS frontend
- Deployment: Simple cloud hosting (Heroku/PythonAnywhere)
- Data Handling: Manual JSON upload, session-based processing

**Core Features Required:**
1. File upload interface for JSON data
2. Data validation and processing
3. Basic dashboard with 4 views:
   - Vote Summary (pass/fail ratios)
   - Council Member Analysis
   - Voting Patterns
   - City Comparison
4. City-specific configuration handling
5. Error handling and user feedback

### TECHNICAL ARCHITECTURE
[Source: TWO_CITY_POC_SUBAGENT_ARCHITECTURE.md]

Implement a modular system using the following sub-agents:

**1. Data Validation Agent**
```python
class DataValidationAgent:
    def __init__(self):
        self.schema = self.load_universal_schema()
        
    def validate_json(self, file_data, city_name):
        """Validate uploaded JSON against universal schema"""
        # Implementation details from TWO_CITY_POC_SUBAGENT_ARCHITECTURE.md
```

**2. City Configuration Agent**
```python
class CityConfigAgent:
    def __init__(self):
        self.configs = self.load_city_configs()
        
    def get_city_config(self, city_name):
        """Return city-specific configuration"""
        # Implementation details from TWO_CITY_POC_SUBAGENT_ARCHITECTURE.md
```

[Additional agent implementations as documented in TWO_CITY_POC_SUBAGENT_ARCHITECTURE.md]

### PROJECT STRUCTURE
[Source: TWO_CITY_IMPLEMENTATION_GUIDE.md]

```
CityVoting_POC/
├── app.py                    # Main Flask app
├── requirements.txt          # Python dependencies
├── config/
│   ├── city_configs.py      # City configurations
│   └── json_schema.py       # JSON validation schema
├── static/
│   ├── style.css            # CSS styles
│   └── chart.js             # Chart.js library
├── templates/
│   ├── index.html           # Main dashboard
│   └── upload.html          # File upload page
├── utils/
│   └── validation.py        # JSON validation helpers
└── tests/
    └── test_app.py          # Unit tests
```

### DATA FORMATS AND VALIDATION
[Source: MANUAL_ANNOTATION_GUIDE.md]

**Universal JSON Schema:**
```json
{
    "agenda_item": {
        "type": "string",
        "required": true
    },
    "motion": {
        "type": "string",
        "required": false
    },
    "vote_result": {
        "type": "string",
        "enum": ["Pass", "Fail", "Continued"],
        "required": true
    },
    "vote_breakdown": {
        "type": "object",
        "properties": {
            "ayes": {"type": "integer"},
            "noes": {"type": "integer"},
            "abstain": {"type": "integer"},
            "absent": {"type": "integer"},
            "recused": {"type": "integer"}
        },
        "required": false
    },
    "member_votes": {
        "type": "object",
        "properties": {
            "ayes": {"type": "array"},
            "noes": {"type": "array"},
            "abstain": {"type": "array"},
            "absent": {"type": "array"},
            "recused": {"type": "array"}
        },
        "required": true
    },
    "meeting_date": {
        "type": "string",
        "format": "date",
        "required": true
    }
}
```

### CITY-SPECIFIC PROCESSING
[Source: CITY_SPECIFIC_VOTE_EXTRACTION_ANALYSIS.md]

**Santa Ana Configuration:**
- Council Size: 7 members
- Vote Format: "Motion carried/failed X-X"
- Member Format: "Councilmember LastName"
- Special Handling: Recusals explicitly stated

**Pomona Configuration:**
- Council Size: TBD
- Vote Format: Narrative text style
- Member Format: Name only
- Special Handling: Bulk consent calendar

### SECURITY AND PRODUCTION CONSIDERATIONS
[Source: POC_BLIND_SPOT_REMEDIATION_PLAN.md]

**1. File Upload Security:**
```python
# In app.py
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
ALLOWED_EXTENSIONS = {'json'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
```

**2. Session Management:**
```python
# In app.py
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)
```

**3. Error Handling:**
```python
@app.errorhandler(413)
def too_large(e):
    return render_template('error.html', error="File too large"), 413

@app.errorhandler(400)
def bad_request(e):
    return render_template('error.html', error="Invalid request"), 400
```

### IMPLEMENTATION TIMELINE
[Source: TWO_CITY_IMPLEMENTATION_GUIDE.md]

**Week 1: Core Infrastructure**
1. Project setup and Flask application
2. File upload and validation
3. Basic data processing
4. Simple dashboard layout

**Week 2: Features and Polish**
1. Chart implementation
2. City comparison features
3. Error handling and validation
4. Testing and deployment

### SUCCESS CRITERIA
[Source: TWO_CITY_POC_PRD.md]

The POC is considered successful when:
1. Users can upload JSON files for either city
2. Data is properly validated and processed
3. All 4 dashboard views are functional
4. City comparison works correctly
5. Basic error handling is in place
6. Application is deployed and accessible

### DEVELOPMENT CONSTRAINTS
[Source: TWO_CITY_POC_PRD.md]

1. Focus on MVP features only
2. Use session-based storage (no database)
3. Manual JSON upload only
4. Support modern browsers only
5. Basic responsive design
6. Simple deployment platform

---

## Implementation Notes

1. Start with core file upload and validation
2. Implement one dashboard view at a time
3. Test with sample data from both cities
4. Focus on functionality over design
5. Document setup and deployment steps
6. Include basic error messages and validation feedback

## Implementation Request

Please implement this Two-City Vote Tracker POC based on the specifications above. Focus on creating a working MVP that demonstrates the core functionality of vote data visualization for Santa Ana and Pomona city council meetings.
