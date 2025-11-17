# TWO_CITY_POC_IMPLEMENTATION_INSTRUCTIONS.md

## Comprehensive Implementation Instructions for Two-City Voting POC

This guide provides step-by-step instructions to build, test, and deploy the Two-City Voting Proof of Concept (POC) project for Santa Ana and Pomona. It fills all gaps identified in the PRD and implementation guide, ensuring any developer or LLM can complete the project independently.

---

## 1. Project Structure & Scaffolding

Create the following folder and file structure:

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
│   ├── index.html           # Main dashboard template
│   └── upload.html          # File upload page
├── sample_data/
│   ├── santa_ana_item_22.json
│   ├── santa_ana_sample.json
│   └── pomona_sample.json
├── utils/
│   └── validation.py        # JSON validation helpers
├── tests/
│   └── test_app.py          # Unit tests
└── README.md                # Project instructions
```

---

## 2. Flask Backend Implementation

- **app.py**: Create a Flask app with routes for:
  - `/` (dashboard)
  - `/upload` (file upload)
  - `/api/process` (process uploaded JSON)
  - `/api/cities` (get city configs)
- Use `city_configs.py` for city-specific settings (members, colors, etc).
- Use `json_schema.py` and `validation.py` to validate uploaded JSON files.
- Store uploaded files in `sample_data/` for session processing.

---

## 3. Frontend Implementation

- **templates/index.html**: Dashboard with summary cards, charts, tables, and filters.
- **templates/upload.html**: Drag-and-drop file upload zone, progress bar, error messages.
- **static/style.css**: Basic styling for dashboard and upload page.
- **static/chart.js**: Use Chart.js for visualizations (pie, bar, line charts).
- **JavaScript**: Handle file upload, chart rendering, data filtering, and city switching.

---

## 4. Sample Data Files

- **santa_ana_item_22.json**: Annotated sample from Santa Ana (Item 22).
- **santa_ana_sample.json**: Additional Santa Ana meeting example.
- **pomona_sample.json**: Placeholder structure for Pomona (update after text processing).
- **Edge Cases**: Create test files with missing fields, invalid data, and large datasets.

---

## 5. Dependencies & Setup

- **requirements.txt**:
  ```
  flask
  pandas
  numpy
  jsonschema
  ```
- **Setup Instructions**:
  ```bash
  python -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  python app.py
  ```
- Document environment variables if needed (e.g., for deployment).

---

## 6. Testing Framework

- **tests/test_app.py**: Unit tests for backend routes, JSON validation, error handling.
- **Manual Testing**: Upload sample files, check dashboard rendering, switch cities.
- **Edge Case Testing**: Validate error handling for bad data, missing fields, large files.

---

## 7. Deployment Instructions

- **Recommended Hosting**: Heroku, PythonAnywhere, Render, or DigitalOcean App Platform.
- **Deployment Steps**:
  - Create account on chosen platform
  - Push code to remote repository
  - Set up environment (Python 3.11+, install dependencies)
  - Configure static and template folders
  - Set environment variables if needed
  - Run `python app.py` or use platform-specific start command
- **Frontend Hosting**: If separating frontend, use Netlify or Vercel for static files.

---

## 8. README & Documentation

- **README.md**: Include project overview, setup instructions, usage guide, sample data info, testing steps, and deployment guide.
- **Code Comments**: Document all major functions and classes.
- **Extensibility**: Instructions for adding new cities, updating configs, and extending analytics.

---

## 9. Success Criteria & Validation

- Can upload and process JSON files for both cities
- All dashboard views functional
- City comparison working
- Deployed and accessible online
- Documentation complete
- Ready for additional city integration

---

## 10. Extending the POC

- Add new city configs in `config/city_configs.py`
- Update frontend city selector
- Add new sample data files
- Enhance analytics and visualizations
- Integrate database if needed

---

**This guide ensures a complete, independent implementation of the Two-City Voting POC.**
