# CityVotes POC - Two-City Vote Analysis Platform

A proof of concept web application for analyzing city council voting data from Santa Ana and Pomona, California. Built with Flask, Sub-Agent architecture, and responsive web design.

## 🎯 Features

### Core Functionality
- **Drag & Drop File Upload**: Upload JSON voting data files with intuitive interface
- **Data Validation**: Comprehensive validation using DataValidationAgent
- **Session Management**: Secure temporary data storage with automatic cleanup
- **Multi-City Support**: Designed for Santa Ana and Pomona with easy expansion

### Dashboard Views
1. **Vote Summary Dashboard**: Overview metrics, pass/fail ratios, member participation
2. **Council Member Analysis**: Individual voting patterns, alignment matrix, behavior analysis
3. **City Comparison Dashboard**: Side-by-side analysis of voting patterns between cities

### Technical Architecture
- **Sub-Agent Pattern**: Modular architecture with specialized agents
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Real-time Charts**: Interactive visualizations using Chart.js
- **RESTful API**: JSON endpoints for external integration

## 🏗️ Architecture

### Sub-Agents
- **DataValidationAgent**: Validates JSON structure and content
- **CityConfigAgent**: Manages city-specific configurations and settings
- **FileProcessingAgent**: Orchestrates file upload workflow and session management

### Folder Structure
```
CityVotes_POC/
├── app/                     # Main Flask application
│   ├── routes/             # Route handlers (main, api, dashboard)
│   ├── templates/          # Jinja2 templates
│   ├── static/             # CSS, JavaScript, images
│   └── __init__.py         # App factory
├── agents/                 # Sub-agent implementations
├── config/                 # Configuration files
├── data/                   # Sample data and uploads
├── docs/                   # Documentation (organized by topic)
│   ├── Architecture/      # System architecture and design
│   ├── City_Specific/     # City-specific extraction guides
│   ├── Guides/            # Operational guides
│   ├── Implementation/    # Implementation instructions
│   ├── Research/          # Research findings
│   └── README.md         # Documentation index
├── Documents/             # Project management docs
├── Session_Archives/      # Archived session data
├── daily_claude_logs/     # Claude session logging system
├── app.py                 # Main application entry point
├── run.py                 # Enhanced startup with port fallback
├── requirements.txt       # Python dependencies
├── test_all_agents.py    # Comprehensive agent tests
├── test_all_city_extractors.py  # City extractor tests
└── README.md             # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- pip package manager

### Installation
1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd CityVotes_POC
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Open in browser**
   ```
   http://localhost:5000
   ```

### Testing with Sample Data
1. Visit `/sample-data` to get sample JSON
2. Save the JSON as `santa_ana_sample.json`
3. Upload via the drag-and-drop interface
4. Select "Santa Ana, CA" as the city
5. Explore the three dashboard views

## 📊 Dashboard Features

### Vote Summary Dashboard
- **Key Metrics**: Total votes, pass rate, active members
- **Vote Outcomes Chart**: Visual breakdown of Pass/Fail/Tie votes
- **Member Participation**: Bar chart showing member activity
- **Member Summary Table**: Detailed voting statistics per member

### Council Member Analysis Dashboard
- **Member Cards**: Individual voting patterns and participation rates
- **Alignment Analysis**: Most/least aligned member pairs
- **Alignment Matrix**: Heat map showing member voting agreement
- **Voting Behavior Chart**: Comparative analysis of member voting patterns

### City Comparison Dashboard
- **City Overview Cards**: Key metrics for each city
- **Pass Rate Comparison**: Bar chart comparing city performance
- **Vote Volume Analysis**: Distribution of total votes
- **Detailed Comparison Table**: Side-by-side metrics
- **Outcome Distribution**: Stacked bar chart of vote outcomes

## 📋 Data Format

### Required JSON Structure
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
        "Phil Bacerra": "Nay"
      },
      "meeting_date": "2024-01-15"
    }
  ]
}
```

### Validation Rules
- `outcome` must be: "Pass", "Fail", "Tie", or "Continued"
- `member_votes` values must be: "Aye", "Nay", "Abstain", "Absent", or "Recusal"
- `tally` counts should match individual member votes
- All required fields must be present

## 🏛️ City Configuration

### Santa Ana, CA
- **Council Size**: 7 members
- **Colors**: Blue (#1f4e79) and Gold (#f4b942)
- **Members**: Mayor Valerie Amezcua, Vince Sarmiento, Phil Bacerra, Johnathan Ryan Hernandez, Thai Viet Phan, Benjamin Vazquez, David Penaloza

### Pomona, CA
- **Council Size**: 5 members
- **Colors**: Green (#2c5530) and Gold (#ffd700)
- **Members**: Placeholder configuration (ready for real data)

## 🔧 API Endpoints

### Public API
- `GET /api/cities` - Get supported cities
- `GET /api/city/<city_name>` - Get city configuration
- `POST /api/validate` - Validate JSON data
- `GET /health` - System health check

### Session API
- `GET /api/session/data` - Get current session info
- `GET /api/session/cities` - Get cities with uploaded data
- `GET /api/dashboard/<city>/summary` - Get dashboard data for city

## 🚦 Deployment

### Development
```bash
python app.py
```

### Production with Gunicorn
```bash
gunicorn -c gunicorn_config.py app:app
```

### Environment Variables
- `SECRET_KEY`: Flask secret key for production
- `UPLOAD_FOLDER`: Directory for temporary file storage
- `PORT`: Server port (default: 5000)

### Deployment Platforms
- **Heroku**: Use included `Procfile`
- **Docker**: Compatible with containerization
- **Traditional Hosting**: Works with any Python hosting provider

## 🧪 Testing

### Test Sub-Agents
```bash
python test_all_agents.py
```

### Test Flask Application
```bash
python -m pytest tests/
```

### Manual Testing
1. Start the application
2. Upload sample data for both cities
3. Test all three dashboard views
4. Verify data validation with invalid JSON
5. Test session management and cleanup

## 📈 Performance

### Optimizations
- **Session-based storage**: No database overhead for POC
- **Lazy loading**: Charts load on demand
- **File size limits**: 10MB maximum upload
- **Auto cleanup**: Sessions expire after 2 hours
- **CDN assets**: Bootstrap, Chart.js, Font Awesome from CDN

### Scalability Notes
- In-memory sessions limit concurrent users
- For production: implement Redis or database sessions
- File storage should use cloud storage (S3, Google Cloud)
- Consider caching for frequently accessed city configurations

## 🔒 Security

### Implemented Measures
- **File validation**: JSON structure and size limits
- **Session security**: Secure cookies and CSRF protection
- **Input sanitization**: All user inputs validated
- **Temporary storage**: Files automatically cleaned up
- **Error handling**: No sensitive information exposed

### Security Considerations
- Sessions stored in memory (not persistent across restarts)
- File uploads limited to JSON format
- No user authentication required for POC
- All data processing happens server-side

## 🛠️ Development

### Adding New Cities
1. Update `CityConfigAgent` with new city configuration
2. Add member names, colors, and council size
3. Test with sample data for the new city
4. Update templates if city-specific styling needed

### Extending Dashboards
1. Add new route in `app/routes/dashboard.py`
2. Create template in `app/templates/dashboards/`
3. Add Chart.js visualizations if needed
4. Update navigation in base template

### Custom Sub-Agents
1. Create new agent in `agents/` directory
2. Follow existing patterns (init, main methods)
3. Add to `agents/__init__.py`
4. Integrate with Flask routes as needed

## 📝 License

This is a proof of concept project for educational and demonstration purposes.

## 🤝 Contributing

This is a POC project, but suggestions for improvements are welcome:
1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit pull request with description

## 📞 Support

### Common Issues
- **Import errors**: Ensure you're in the CityVotes_POC directory
- **Port conflicts**: Application tries multiple ports automatically
- **File upload errors**: Check file format is JSON and under 10MB
- **Dashboard not loading**: Verify data was uploaded and validated successfully

### Troubleshooting
1. Check console output for detailed error messages
2. Visit `/health` endpoint to verify system status
3. Use sample data to test basic functionality
4. Clear browser cache if experiencing issues

### Getting Help
- Check the troubleshooting guide in [FLASK_TROUBLESHOOTING.md](FLASK_TROUBLESHOOTING.md)
- Review sub-agent documentation in [README_SubAgents.md](README_SubAgents.md)
- Browse comprehensive documentation in [docs/](docs/)

## 📚 Additional Documentation

### Core Documentation
- [Sub-Agent Architecture](README_SubAgents.md) - Detailed sub-agent documentation
- [Vote Extraction Agent](README_VoteExtractionAgent.md) - Vote extraction system guide
- [AI-Powered Extractor Guide](AI_POWERED_EXTRACTOR_GUIDE.md) - Self-improving AI extractor with learning capabilities
- [Documentation Index](docs/README.md) - Complete documentation catalog

### Storage and Workflow
- [Storage & Extraction Quick Start](STORAGE_AND_EXTRACTION_QUICKSTART.md) - Fast reference for PDF storage and text extraction
- [External Storage Structure Guide](EXTERNAL_STORAGE_STRUCTURE_GUIDE.md) - Complete guide for organizing PDFs and text files on external storage
- [Selenium Download Setup](SELENIUM_DOWNLOAD_SETUP.md) - **Automated** download using Selenium browser automation (recommended)
- [Manual Download Workflow](MANUAL_DOWNLOAD_WORKFLOW.md) - Manual download and organize PDFs from Santa Ana portal
- [PDF to Text Workflow](PDF_TO_TEXT_WORKFLOW.md) - Detailed guide for PDF extraction and storage strategy
- [CSV Extraction Workflow](CSV_EXTRACTION_WORKFLOW.md) - Working with pre-extracted vote data in CSV format

### Quick Links
- **Architecture**: See [docs/Architecture/](docs/Architecture/) for system design
- **City-Specific**: See [docs/City_Specific/](docs/City_Specific/) for city extraction patterns
- **Implementation**: See [docs/Implementation/](docs/Implementation/) for build guides
- **Research**: See [docs/Research/](docs/Research/) for technical research

## 🗑️ Code Consolidation (Nov 2025)

This project was recently consolidated to reduce duplication and improve maintainability:

### Files Removed
- **7 port workaround Python scripts** (~1000 lines) - Various attempts to solve macOS AirPlay port 5000 conflicts
  - `final_working_solution.py`, `final_port5000_solution.py`, `final_port5000_success.py`
  - `force_port5000_native.py`, `start_port5000.py`
  - `flask_example.py`, `run_flask.py`

- **2 port workaround shell scripts** - Additional port 5000 workarounds
  - `fix_port5000.sh` - AirPlay killer script
  - `nginx_port5000_proxy.sh` - Nginx proxy setup (overkill)
  - **Solution**: Use `run.py` which tries fallback ports automatically

- **3 redundant test files** - Functionality consolidated into comprehensive tests
  - `test_agents.py` → merged into `test_all_agents.py`
  - `test_improved_extractor.py` → covered by city extractor tests
  - `test_vote_extraction_integration.py` → functionality in `test_all_city_extractors.py`

- **7 duplicate documentation files** - Consolidated into organized structure
  - Implementation guides merged into master prompt
  - Research documents consolidated
  - Better organization in `docs/` folder

- **1 redundant config** - `requirements_flask.txt` removed (use `requirements.txt`)

### Impact
- **20 files removed total** (9 Python scripts + 2 shell scripts + 3 test files + 7 docs + 1 config)
- **Code reduction**: ~2,000+ lines of duplicate/dead code removed
- **Documentation**: 22 docs → 15 organized files in structured folders
- **Clarity**: Much easier to understand what each file does
- **Maintenance**: Single source of truth for each concept

### Utility Scripts Kept
- [extract_votes.sh](extract_votes.sh) - Convenient wrapper for vote extraction commands
- [batch_process_santa_ana.py](batch_process_santa_ana.py) - Production batch processor
- [run_santa_ana_extraction.py](run_santa_ana_extraction.py) - AI-powered extraction runner
- [analyze_santa_ana_results.py](analyze_santa_ana_results.py) - Results analysis and quality metrics
- [Claude_transfer/pdf_to_text.py](Claude_transfer/pdf_to_text.py) - PDF to text conversion utility
- [Claude_transfer/match_agenda_minutes.py](Claude_transfer/match_agenda_minutes.py) - Agenda/minutes pairing utility

### Port 5000 Troubleshooting
If you encounter "Address already in use" on port 5000 (macOS AirPlay Receiver):
1. **Option 1**: Use `run.py` instead of `app.py` - it automatically tries fallback ports
2. **Option 2**: Disable AirPlay Receiver in System Settings → Sharing → AirPlay Receiver
3. **Option 3**: Manually specify a different port: `python app.py --port 5001`

---

**CityVotes POC** - Demonstrating the future of civic data analysis through modern web technologies and intelligent sub-agent architecture.