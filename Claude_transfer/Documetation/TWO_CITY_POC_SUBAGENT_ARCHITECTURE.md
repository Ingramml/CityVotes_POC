# Two-City POC Sub-Agent Architecture

## Recommended Sub-Agents for Your Two-City POC

Based on your Two-City POC project (Santa Ana and Pomona voting data visualization), here are the specific sub-agents that would benefit your implementation:

### **1. Data Validation Sub-Agent**
**Purpose**: Validate uploaded JSON files against your universal schema

**Benefits**: 
- Ensures data quality before processing
- Provides specific error messages to users
- Handles different city data formats consistently

**Implementation**: 
```python
class DataValidationAgent:
    def __init__(self):
        self.schema = self.load_universal_schema()
        
    def validate_json(self, file_data, city_name):
        """Validate uploaded JSON against universal schema"""
        # Validate against universal JSON schema
        # Check city-specific requirements
        # Return validation results with detailed errors
        
    def validate_vote_structure(self, vote_data):
        """Ensure vote data has required fields"""
        required_fields = ['agenda_item_number', 'outcome', 'tally']
        # Validation logic
        
    def validate_member_votes(self, member_votes, city_config):
        """Check member votes against city's council roster"""
        # Cross-reference with city configuration
```

### **2. City Configuration Sub-Agent**
**Purpose**: Manage city-specific settings and metadata

**Benefits**:
- Centralizes Santa Ana and Pomona configurations
- Easy to add new cities later
- Handles council member lists, colors, patterns

**Implementation**:
```python
class CityConfigAgent:
    def __init__(self):
        self.configs = self.load_city_configs()
        
    def get_city_config(self, city_name):
        """Return city-specific configuration"""
        # Return council members, colors, voting patterns
        return {
            'name': city_name,
            'council_members': self.configs[city_name]['members'],
            'colors': self.configs[city_name]['colors'],
            'total_seats': len(self.configs[city_name]['members']),
            'vote_patterns': self.configs[city_name]['patterns']
        }
        
    def validate_city_data(self, data, city_name):
        """Check if data matches city expectations"""
        # Check if data matches city expectations
        config = self.get_city_config(city_name)
        # Validate member names, vote counts, etc.
        
    def get_supported_cities(self):
        """Return list of configured cities"""
        return list(self.configs.keys())
```

### **3. Data Processing Sub-Agent**
**Purpose**: Transform raw JSON into dashboard-ready data

**Benefits**:
- Standardizes data formats across cities
- Calculates metrics (vote success rates, member alignment)
- Handles edge cases (abstentions, absences)

**Implementation**:
```python
class DataProcessingAgent:
    def __init__(self, city_config_agent):
        self.city_config = city_config_agent
        
    def process_voting_data(self, raw_data, city_name):
        """Transform raw JSON into dashboard data"""
        config = self.city_config.get_city_config(city_name)
        
        # Calculate summary statistics
        summary = self.calculate_summary_stats(raw_data)
        
        # Prepare chart data
        chart_data = self.prepare_chart_data(raw_data, config)
        
        # Handle missing/invalid votes
        cleaned_data = self.clean_vote_data(raw_data)
        
        return {
            'summary': summary,
            'charts': chart_data,
            'cleaned_votes': cleaned_data,
            'metadata': {
                'total_votes': len(raw_data.get('votes', [])),
                'city': city_name,
                'processed_at': datetime.now().isoformat()
            }
        }
        
    def calculate_summary_stats(self, data):
        """Calculate key metrics for dashboard cards"""
        # Vote success rate, member participation, etc.
        
    def calculate_member_alignment(self, votes):
        """Calculate how often members vote together"""
        # Member voting pattern analysis
```

### **4. Chart Generation Sub-Agent**
**Purpose**: Create standardized visualizations

**Benefits**:
- Consistent chart styling across cities
- Handles different data sizes gracefully
- Easy to add new chart types

**Implementation**:
```python
class ChartGenerationAgent:
    def __init__(self):
        self.chart_configs = self.load_chart_configs()
        
    def create_vote_breakdown_chart(self, vote_data, city_name):
        """Generate pie chart data for vote outcomes"""
        # Count pass/fail/tie votes
        # Return Chart.js compatible data structure
        return {
            'type': 'pie',
            'data': {
                'labels': ['Pass', 'Fail', 'Tie'],
                'datasets': [{
                    'data': [pass_count, fail_count, tie_count],
                    'backgroundColor': self.get_city_colors(city_name)
                }]
            }
        }
        
    def create_member_voting_chart(self, member_data, city_name):
        """Generate bar chart data for member voting patterns"""
        # Generate bar chart data
        
    def create_timeline_chart(self, votes_by_date):
        """Generate line chart for voting trends over time"""
        # Time series visualization
        
    def get_city_colors(self, city_name):
        """Get city-specific color palette"""
        # Return colors from city configuration
```

### **5. Session Management Sub-Agent**
**Purpose**: Handle user sessions and data persistence

**Benefits**:
- Manages uploaded files per user
- Handles city switching
- Implements data cleanup

**Implementation**:
```python
class SessionManagementAgent:
    def __init__(self):
        self.sessions = {}  # In production, use Redis or database
        
    def store_user_data(self, session_id, city, data):
        """Store processed data for user session"""
        if session_id not in self.sessions:
            self.sessions[session_id] = {}
        
        self.sessions[session_id][city] = {
            'data': data,
            'uploaded_at': datetime.now(),
            'expires_at': datetime.now() + timedelta(hours=2)
        }
        
    def get_user_data(self, session_id, city):
        """Retrieve user's data for specific city"""
        if session_id in self.sessions and city in self.sessions[session_id]:
            session_data = self.sessions[session_id][city]
            if datetime.now() < session_data['expires_at']:
                return session_data['data']
        return None
        
    def cleanup_expired_sessions(self):
        """Remove expired session data"""
        # Cleanup logic for expired sessions
        
    def get_user_cities(self, session_id):
        """Get list of cities user has uploaded data for"""
        if session_id in self.sessions:
            return list(self.sessions[session_id].keys())
        return []
```

## **Architecture for Your POC**

```
┌─────────────────┐
│   Flask App     │ (Main Controller)
│   (Routes)      │
└────────┬────────┘
         │
    ┌────▼─────┬──────────┬─────────────┬──────────────┐
    │          │          │             │              │
┌───▼────┐ ┌──▼───┐ ┌────▼─────┐ ┌─────▼──────┐ ┌───▼────┐
│Session │ │Data  │ │  City    │ │    Data    │ │ Chart  │
│Manager │ │Valid │ │  Config  │ │ Processing │ │ Gen    │
│ Agent  │ │Agent │ │  Agent   │ │   Agent    │ │ Agent  │
└────────┘ └──────┘ └──────────┘ └────────────┘ └────────┘
```

## **Flask Integration Example**

```python
# app.py
from flask import Flask, request, session, jsonify, render_template

app = Flask(__name__)

# Initialize sub-agents
data_validator = DataValidationAgent()
city_config = CityConfigAgent()
data_processor = DataProcessingAgent(city_config)
chart_generator = ChartGenerationAgent()
session_manager = SessionManagementAgent()

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload with sub-agent coordination"""
    file = request.files['file']
    city = request.form['city']
    session_id = session.get('id')
    
    # Step 1: Validate uploaded file
    file_data = json.load(file)
    is_valid, errors = data_validator.validate_json(file_data, city)
    
    if not is_valid:
        return jsonify({'error': 'Validation failed', 'details': errors}), 400
    
    # Step 2: Process data
    processed_data = data_processor.process_voting_data(file_data, city)
    
    # Step 3: Generate charts
    charts = {
        'vote_breakdown': chart_generator.create_vote_breakdown_chart(
            processed_data['cleaned_votes'], city
        ),
        'member_voting': chart_generator.create_member_voting_chart(
            processed_data['cleaned_votes'], city
        )
    }
    processed_data['charts'] = charts
    
    # Step 4: Store in session
    session_manager.store_user_data(session_id, city, processed_data)
    
    return jsonify({'success': True, 'redirect': '/dashboard'})

@app.route('/dashboard')
def dashboard():
    """Display dashboard with sub-agent data"""
    session_id = session.get('id')
    city = request.args.get('city', 'santa_ana')
    
    # Get data from session manager
    data = session_manager.get_user_data(session_id, city)
    
    if not data:
        return redirect('/upload')
    
    # Get city configuration for display
    city_config_data = city_config.get_city_config(city)
    
    return render_template('dashboard.html', 
                         data=data, 
                         city_config=city_config_data,
                         available_cities=session_manager.get_user_cities(session_id))

@app.route('/api/cities')
def get_cities():
    """API endpoint for supported cities"""
    return jsonify(city_config.get_supported_cities())
```

## **Implementation Benefits**

### **For Your Two-Week Timeline**
- Each sub-agent can be developed independently
- Easy to test individual components
- Parallel development of different features
- Clear separation of concerns
- Simplified debugging (issues isolated to specific agents)

### **For Future Scaling**
- Adding Pomona requires minimal changes to existing agents
- New cities just need configuration updates
- Easy to enhance individual capabilities
- Modular testing and debugging
- Can replace individual agents without affecting others

### **Development and Maintenance**
- Each agent has single responsibility
- Clear interfaces between components
- Easy to add new features (new chart types, validation rules)
- Simplified unit testing
- Better error isolation and handling

## **Simple Implementation Strategy**

**Week 1**: 
- Implement Data Validation and City Config agents
- Basic Data Processing agent
- Simple Session Management
- Basic Flask integration

**Week 2**:
- Chart Generation agent
- Complete Flask integration
- Error handling improvements
- Testing and refinement

## **Minimal Viable Sub-Agents**

If you want to start even simpler, focus on these two core agents:

1. **Data Validation Agent** - Essential for file upload safety and data quality
2. **City Configuration Agent** - Critical for supporting both Santa Ana and Pomona

The others can be implemented as simple functions initially and converted to full sub-agents as the project grows.

## **Testing Strategy**

Each sub-agent can be tested independently:

```python
# test_data_validation_agent.py
def test_valid_json():
    agent = DataValidationAgent()
    valid_data = load_test_data('valid_santa_ana.json')
    is_valid, errors = agent.validate_json(valid_data, 'santa_ana')
    assert is_valid
    assert len(errors) == 0

def test_invalid_json():
    agent = DataValidationAgent()
    invalid_data = {'invalid': 'structure'}
    is_valid, errors = agent.validate_json(invalid_data, 'santa_ana')
    assert not is_valid
    assert len(errors) > 0
```

## **Example Prompts for Building Each Sub-Agent**

### **Prompt 1: Data Validation Agent**

```
Create a Python class called DataValidationAgent for a Flask voting data application. This agent should:

1. Validate uploaded JSON files against a universal voting data schema
2. Check for required fields: agenda_item_number, outcome, tally, member_votes
3. Validate vote outcomes are one of: "Pass", "Fail", "Tie", "Continued"
4. Ensure tally counts match individual member votes
5. Cross-reference member names against city-specific council rosters
6. Return detailed validation results with specific error messages
7. Handle edge cases like missing fields, invalid vote counts, unknown members

The universal JSON schema should include:
- agenda_item_number (string)
- agenda_item_title (string)
- motion_type (string: "original", "substitute", "amendment")
- outcome (string: "Pass", "Fail", "Tie", "Continued")
- tally (object with ayes, noes, abstain, absent counts)
- member_votes (object mapping member names to vote choices)
- meeting_date (string in ISO format)

Include comprehensive error handling and user-friendly error messages. Use jsonschema library for validation.
```

### **Prompt 2: City Configuration Agent**

```
Create a Python class called CityConfigAgent that manages city-specific configurations for a voting data application supporting Santa Ana and Pomona. This agent should:

1. Store and retrieve city configurations including:
   - Council member names and titles
   - City colors (primary/secondary for charts)
   - Total council seats
   - Common voting patterns
   - City-specific validation rules

2. Provide methods to:
   - Get complete city configuration by name
   - Validate data against city-specific requirements
   - List all supported cities
   - Check if a member name exists in a city's roster
   - Get city-appropriate color schemes

3. Handle city-specific data like:
   - Santa Ana: 7 council members, specific color scheme, known voting patterns
   - Pomona: TBD configuration (placeholder for future implementation)

4. Support easy addition of new cities
5. Include data validation for council member names with common variations
6. Provide default configurations and graceful fallbacks

Store configurations in a structured format (JSON or Python dict) and include error handling for missing cities or invalid requests.
```

### **Prompt 3: Data Processing Agent**

```
Create a Python class called DataProcessingAgent that transforms raw voting JSON data into dashboard-ready analytics. This agent should:

1. Accept raw voting data and city configuration as inputs
2. Calculate key metrics:
   - Vote success rate (percentage of items that pass)
   - Member participation rate (attendance/voting frequency)
   - Member alignment scores (how often members vote together)
   - Controversy index (measure of vote splits)
   - Voting trends over time

3. Process and clean data:
   - Handle missing or invalid votes
   - Standardize member names across different formats
   - Deal with abstentions, absences, and recusals
   - Identify and flag unusual voting patterns

4. Generate analytics including:
   - Summary statistics for dashboard cards
   - Vote breakdown by outcome type
   - Member-by-member voting records
   - Time-series data for trend analysis
   - Comparative statistics across different agenda items

5. Return structured data optimized for:
   - Chart generation (Chart.js compatible formats)
   - Table displays
   - Summary cards
   - Export functionality

Include robust error handling, data validation, and performance optimization for processing multiple meetings worth of data.
```

### **Prompt 4: Chart Generation Agent**

```
Create a Python class called ChartGenerationAgent that generates Chart.js-compatible data structures for voting data visualizations. This agent should:

1. Generate multiple chart types:
   - Pie charts for vote outcome breakdowns (Pass/Fail/Tie)
   - Bar charts for member voting patterns
   - Line charts for voting trends over time
   - Heatmaps for member alignment matrices

2. Handle city-specific styling:
   - Use city-appropriate color schemes
   - Apply consistent branding across charts
   - Ensure accessibility with colorblind-friendly palettes

3. Create responsive chart configurations:
   - Adapt to different screen sizes
   - Include proper labels and legends
   - Handle varying data sizes (few votes vs. many votes)
   - Provide interactive tooltips and hover effects

4. Support multiple visualization formats:
   - Dashboard summary charts
   - Detailed analysis charts
   - Comparison charts between cities
   - Export-ready chart configurations

5. Include chart configuration for:
   - Vote breakdown (pie chart with Pass/Fail/Tie segments)
   - Member voting frequency (bar chart)
   - Voting trends timeline (line chart)
   - Member alignment matrix (heatmap)

Return Chart.js-compatible JSON configurations with proper datasets, labels, colors, and options. Include error handling for edge cases like empty data or missing values.
```

### **Prompt 5: Session Management Agent**

```
Create a Python class called SessionManagementAgent that handles user sessions and data persistence for a Flask voting data application. This agent should:

1. Manage user session data:
   - Store uploaded voting data per user session
   - Handle multiple cities per user session
   - Implement session expiration (2-hour default)
   - Provide secure session isolation between users

2. Data storage capabilities:
   - Store processed voting data temporarily
   - Handle file uploads and cleanup
   - Manage session state across page reloads
   - Support switching between cities within same session

3. Session operations:
   - Create new sessions with unique identifiers
   - Store and retrieve data by session ID and city
   - List cities available for a session
   - Clean up expired sessions automatically
   - Handle session errors gracefully

4. Integration features:
   - Work with Flask session management
   - Support both in-memory and persistent storage
   - Provide hooks for database integration later
   - Include logging for session activities

5. Security considerations:
   - Prevent session data leakage between users
   - Implement proper session timeout
   - Handle concurrent access safely
   - Include data sanitization

The agent should be production-ready with proper error handling, logging, and support for scaling to multiple concurrent users. Include methods for session cleanup, data validation, and integration with Flask's session system.
```

## **How to Use These Prompts**

1. **For Each Agent**: Copy the prompt and provide it to an AI assistant or development team
2. **Customization**: Modify the prompts based on your specific requirements
3. **Implementation Order**: Start with Data Validation and City Configuration agents first
4. **Testing**: Request unit tests and integration examples with each implementation
5. **Integration**: Ask for Flask integration examples after building individual agents

## **Additional Implementation Notes**

- Each prompt includes specific technical requirements and expected functionality
- The prompts assume familiarity with Python, Flask, and the voting data domain
- Consider requesting documentation and examples along with the code
- Test each agent independently before integration
- Use the prompts as a starting point and refine based on your specific needs

## **Benefits Summary**

This sub-agent architecture gives you:
- **Clean separation of concerns** for easier development
- **Scalable architecture** that grows with your project
- **Testable components** for better code quality
- **Flexible implementation** that fits your two-week timeline
- **Future-proof design** for adding more cities and features

The modular approach ensures that even as a POC, your code maintains professional standards and can serve as a foundation for a larger production system.
