# Two-City Proof of Concept - Implementation Guide

## Project Structure
```
two-city-poc/
├── backend/
│   ├── app.py              # Flask/FastAPI main application
│   ├── data_processor.py   # JSON processing and validation
│   ├── city_configs.py     # Santa Ana & Pomona configurations
│   ├── analytics.py        # Vote analysis functions
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── uploads/        # Temporary file storage
│   ├── templates/
│   │   ├── index.html      # Landing page
│   │   ├── upload.html     # File upload interface
│   │   ├── dashboard.html  # Main dashboard
│   │   └── comparison.html # City comparison view
├── config/
│   ├── santa_ana.json     # Council members, patterns
│   └── pomona.json        # Council members, patterns
├── sample_data/
│   ├── santa_ana_sample.json
│   └── pomona_sample.json
└── README.md
```

## Implementation Timeline (2 Weeks)

### Week 1: Core Infrastructure
**Days 1-2: Project Setup**
- [x] Initialize project structure
- [x] Set up Python virtual environment
- [x] Create basic Flask application
- [x] Design universal JSON schema
- [x] Create city configuration files

**Days 3-4: Data Processing**
- [ ] Implement JSON validation
- [ ] Build data processing pipeline
- [ ] Create analytics functions
- [ ] Add error handling

**Days 5-7: Basic Frontend**
- [ ] Create file upload interface
- [ ] Build basic dashboard layout
- [ ] Implement city selection
- [ ] Add session management

### Week 2: Dashboards & Polish
**Days 8-10: Dashboard Development**
- [ ] Vote Summary Dashboard
- [ ] Council Member Analysis
- [ ] Voting Patterns Visualization
- [ ] City Comparison View

**Days 11-12: Integration & Testing**
- [ ] Connect frontend to backend
- [ ] Test with real Santa Ana data
- [ ] Create Pomona sample data
- [ ] Bug fixes and optimization

**Days 13-14: Deployment & Documentation**
- [ ] Deploy to hosting platform
- [ ] Write user documentation
- [ ] Create demo video/screenshots
- [ ] Final testing and polish

## Technical Implementation Details

### 1. Backend Architecture (Python Flask)

#### `app.py` - Main Application
```python
from flask import Flask, request, render_template, session
from data_processor import process_vote_data
from analytics import generate_analytics
from city_configs import get_city_config

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload/<city>')
def upload_page(city):
    config = get_city_config(city)
    return render_template('upload.html', city=city, config=config)

@app.route('/process', methods=['POST'])
def process_data():
    # Handle JSON upload and processing
    pass

@app.route('/dashboard/<city>')
def dashboard(city):
    # Display analytics for processed data
    pass
```

#### `data_processor.py` - JSON Processing
```python
import json
import jsonschema
from datetime import datetime

VOTE_SCHEMA = {
    "type": "object",
    "required": ["agenda_item", "motion", "vote_result", "vote_breakdown", "member_votes", "meeting_date"],
    "properties": {
        "agenda_item": {"type": "string"},
        "motion": {"type": "string"},
        "vote_result": {"enum": ["Pass", "Fail"]},
        "vote_breakdown": {
            "type": "object",
            "properties": {
                "ayes": {"type": "integer"},
                "noes": {"type": "integer"},
                "abstain": {"type": "integer"},
                "absent": {"type": "integer"},
                "recused": {"type": "integer"}
            }
        }
    }
}

def validate_vote_data(data):
    # Validate against schema
    pass

def process_vote_file(file_content, city):
    # Process uploaded JSON file
    pass
```

#### `city_configs.py` - City-Specific Settings
```python
CITY_CONFIGS = {
    "santa_ana": {
        "name": "Santa Ana",
        "council_members": ["Bacerra", "Hernandez", "Lopez", "Mendoza", "Phan", "Penaloza", "Sarmiento"],
        "total_seats": 7,
        "vote_patterns": ["consent_calendar", "individual_items", "reconsiderations"],
        "colors": {"primary": "#1f77b4", "secondary": "#ff7f0e"}
    },
    "pomona": {
        "name": "Pomona", 
        "council_members": ["TBD"], # Will be configured when Pomona text data is processed
        "total_seats": "TBD", # Will be determined from meeting data analysis
        "vote_patterns": ["TBD"], # Will be identified during data processing
        "colors": {"primary": "#2ca02c", "secondary": "#d62728"},
        "data_source": "text_format", # Note: User has text data, not JSON yet
        "status": "pending_data_processing"
    }
}
```

### 2. Frontend Implementation

#### File Upload Interface
- Drag-and-drop zone for JSON files
- File validation (size, format)
- Progress indicators
- Error messaging

#### Dashboard Components
1. **Summary Cards:** Total votes, pass rate, member participation
2. **Charts:** Pie charts for vote breakdowns, bar charts for member votes
3. **Tables:** Detailed vote listings, member voting records
4. **Filters:** Date range, vote result, agenda item type

#### Key JavaScript Functions
```javascript
// File upload handling
function handleFileUpload(file, city) {
    // Validate and upload JSON file
}

// Chart generation
function createVotingChart(data, elementId) {
    // Use Chart.js to create visualizations
}

// Data filtering
function filterVoteData(data, filters) {
    // Apply user-selected filters
}
```

### 3. Data Analytics

#### Core Metrics
- **Vote Success Rate:** Percentage of items that pass
- **Member Alignment:** How often members vote together
- **Participation Rate:** Attendance and voting participation
- **Controversy Index:** Measure of vote splits

#### Visualization Types
- Pie charts for vote breakdowns
- Bar charts for member voting patterns
- Line charts for trends over time
- Heatmaps for member alignment

### 4. City Comparison Features
- Side-by-side metric comparisons
- Different council sizes and structures
- Voting pattern differences
- Visual styling per city

## Deployment Strategy

### Hosting Options
1. **Heroku:** Easy Python deployment, good for proof of concept
2. **Vercel:** Excellent for frontend-heavy applications  
3. **PythonAnywhere:** Simple Python hosting
4. **DigitalOcean App Platform:** Scalable option
5. **AWS/Google Cloud:** Full control and scaling
6. **Netlify + Backend:** Separate frontend/backend deployment
7. **Railway:** Modern alternative to Heroku
8. **Render:** Simple full-stack deployment

**Recommendation:** Choose based on your preference - all options will work for this proof of concept.

### Environment Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install flask pandas numpy jsonschema

# Run development server
python app.py
```

## Testing Strategy

### Sample Data Requirements
- **Santa Ana:** Use your annotated Item 22 as baseline
- **Pomona:** Will be created after processing text format meeting data
- **Edge Cases:** Test with missing fields, invalid data, large files
- **Phase 1:** Start with Santa Ana only, add Pomona when data is ready

### Validation Checkpoints
1. JSON schema validation works correctly
2. All dashboard views render properly
3. City switching maintains session data
4. File upload handles errors gracefully
5. Charts display accurate data

## Future Extensibility

### Adding New Cities
1. Add city configuration to `city_configs.py`
2. Create city-specific color scheme
3. Update frontend city selector
4. Test with city's vote data format

### Potential Enhancements
- Database integration
- Advanced analytics
- Export functionality
- Mobile responsiveness
- Real-time data feeds

---

## Success Metrics
- [x] Can upload and process JSON files for both cities
- [ ] All 4 dashboard views functional
- [ ] City comparison working
- [ ] Deployed and accessible online
- [ ] Documentation complete
- [ ] Ready for additional city integration

**Target Completion:** End of Week 2  
**First Demo:** End of Week 1 (basic functionality)  
**Final Demo:** End of Week 2 (full feature set)**
