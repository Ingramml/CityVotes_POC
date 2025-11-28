# Two-City Vote Analysis Platform - Product Requirements Document (PRD)

## Project Overview
**Goal:** Create a proof of concept web platform for analyzing city council voting data for Santa Ana and Pomona, with the foundation to expand to additional cities.

**Timeline:** 2 weeks  
**Tech Stack:** Python backend, web frontend, session-based processing  
**Deployment:** Online hosting

## Core Requirements

### 1. Data Input & Processing
- **Manual JSON Upload:** Drag-and-drop interface for JSON files
- **Universal Format:** Both cities use standardized vote JSON structure
- **Session-Based:** No persistent database, process files in user session
- **City Configuration:** Separate processing logic/display for Santa Ana vs Pomona

### 2. Dashboard Features
#### POC-Focused Dashboards (3 Core Views):

1. **Vote Summary Dashboard** *(Essential - Core Functionality)*
   - Total votes processed with visual indicators
   - Pass/Fail/Tie breakdown with percentages and pie charts
   - Member participation rates and attendance statistics
   - Quick-hit metrics showing system value immediately

2. **Council Member Analysis Dashboard** *(High Value - Detailed Insights)*
   - Individual member voting records (Aye/Nay/Abstain ratios)
   - Member alignment matrix showing voting partnerships
   - Attendance tracking with present/absent patterns
   - Top agreeing/disagreeing member pairs analysis

3. **City Comparison View** *(POC Differentiator - Scalability Demo)*
   - Side-by-side Santa Ana vs Pomona metrics comparison
   - Council structure differences (7 vs 5 members)
   - Comparative voting patterns and pass rates
   - Demonstrates multi-city platform potential

*Note: Temporal voting trends and controversy analysis deferred to post-POC for timeline management*

### 3. Technical Architecture
- **Backend:** Python Flask with Sub-Agent Architecture
- **Frontend:** HTML/CSS/JavaScript with Chart.js
- **Sub-Agents:**
  - **DataValidationAgent**: JSON structure validation and error detection
  - **CityConfigAgent**: City-specific configurations and council member management
  - **FileProcessingAgent**: File upload workflow, session management, and data processing
- **File Processing:** Secure temporary file handling with validation
- **Session Management:** In-memory session storage with automatic cleanup
- **Charts/Visualization:** Chart.js for responsive data visualization
- **Hosting:** Multiple deployment options (user choice)

## User Journey
1. User visits website
2. Selects city (Santa Ana or Pomona)
3. Uploads JSON file(s) with meeting data
4. System processes and validates data
5. User navigates between dashboard views
6. Session expires, user starts over (no data persistence)

## Data Requirements

### Universal JSON Format (matching implemented sub-agents):
```json
{
  "votes": [
    {
      "agenda_item_number": "7.1",
      "agenda_item_title": "Budget Amendment Resolution",
      "outcome": "Pass",
      "tally": {
        "ayes": 5,
        "noes": 2,
        "abstain": 0,
        "absent": 0
      },
      "member_votes": {
        "Mayor Valerie Amezcua": "Aye",
        "Vince Sarmiento": "Aye",
        "Phil Bacerra": "Nay",
        "Thai Viet Phan": "Abstain",
        "Benjamin Vazquez": "Absent"
      },
      "meeting_date": "2024-01-15"
    }
  ]
}
```

**Key Format Requirements:**
- Root `votes` array containing all vote records
- `outcome` values: "Pass", "Fail", "Tie", "Continued"
- `member_votes` as object mapping member names to vote choices
- Vote choices: "Aye", "Nay", "Abstain", "Absent", "Recusal"
- `tally` object with numeric counts for verification

### City-Specific Configurations:
- **Council member lists**
- **Meeting frequency/patterns**
- **City-specific vote types**
- **Display customizations**

## Success Criteria
1. **Functional:** Successfully upload and process JSON files for both cities
2. **Visual:** Clear, informative dashboards displaying vote patterns
3. **Scalable:** Code structure allows easy addition of new cities
4. **User-Friendly:** Intuitive interface for non-technical users
5. **Fast:** Page loads and data processing under 3 seconds

## Non-Requirements (Future Features)
- Database persistence
- User authentication
- PDF processing
- Automated data collection
- Advanced analytics
- Mobile optimization

## Risk Mitigation
- **Data Validation:** Robust JSON schema validation
- **Error Handling:** Clear error messages for invalid uploads
- **Performance:** File size limits to prevent session overload
- **Fallbacks:** Graceful handling of missing/malformed data

## Deliverables
1. Working web application
2. Documentation for adding new cities
3. Sample JSON files for testing
4. Deployment guide
5. User manual

---

*This PRD serves as the foundation for a 2-week sprint to deliver a functional proof of concept that demonstrates the viability of scaling to a multi-city platform.*
