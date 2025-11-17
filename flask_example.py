#!/usr/bin/env python3
"""
Simple Flask Integration Example with Sub-Agents
Demonstrates how to use the Data Validation and City Configuration agents in a Flask app
"""

import sys
import os
from flask import Flask, request, jsonify, render_template_string
import json

# Add current directory to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from agents import DataValidationAgent, CityConfigAgent
    AGENTS_AVAILABLE = True
    print("✓ Sub-agents imported successfully")
except ImportError as e:
    print(f"✗ Failed to import sub-agents: {e}")
    print("  Make sure you're running from the correct directory")
    AGENTS_AVAILABLE = False

app = Flask(__name__)

# Initialize sub-agents with fallback
if AGENTS_AVAILABLE:
    data_validator = DataValidationAgent()
    city_config = CityConfigAgent()
    print("✓ Sub-agents initialized successfully")
else:
    data_validator = None
    city_config = None
    print("✗ Running in fallback mode without sub-agents")

# Simple HTML template for testing
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>CityVotes POC - Sub-Agent Demo</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .card { border: 1px solid #ddd; padding: 20px; margin: 10px 0; border-radius: 5px; }
        .success { background-color: #d4edda; border-color: #c3e6cb; }
        .error { background-color: #f8d7da; border-color: #f5c6cb; }
        .info { background-color: #d1ecf1; border-color: #bee5eb; }
        pre { background-color: #f8f9fa; padding: 10px; border-radius: 3px; overflow-x: auto; }
        .upload-form { background-color: #f8f9fa; padding: 20px; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>CityVotes POC - Sub-Agent Integration Demo</h1>

    <div class="card info">
        <h3>Available Cities</h3>
        <p><strong>Supported Cities:</strong> {{ cities }}</p>
    </div>

    <div class="upload-form">
        <h3>Test File Upload</h3>
        <form method="post" enctype="multipart/form-data" action="/upload">
            <p>
                <label>City:</label>
                <select name="city" required>
                    <option value="">Select City...</option>
                    <option value="santa_ana">Santa Ana, CA</option>
                    <option value="pomona">Pomona, CA</option>
                </select>
            </p>
            <p>
                <label>JSON File:</label>
                <input type="file" name="file" accept=".json" required>
            </p>
            <p>
                <button type="submit">Upload & Validate</button>
            </p>
        </form>
    </div>

    <div class="card info">
        <h3>Sample Test Data</h3>
        <p>You can test with this sample JSON structure:</p>
        <pre>{{ sample_data }}</pre>
    </div>

    <div class="card info">
        <h3>API Endpoints</h3>
        <ul>
            <li><strong>GET /api/cities</strong> - Get supported cities</li>
            <li><strong>GET /api/city/&lt;city_name&gt;</strong> - Get city configuration</li>
            <li><strong>POST /upload</strong> - Upload and validate JSON file</li>
            <li><strong>POST /api/validate</strong> - Validate JSON data via API</li>
        </ul>
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    """Home page with sub-agent demo interface"""
    if not AGENTS_AVAILABLE:
        return render_template_string('''
        <html><body>
        <h1>CityVotes POC - Setup Issue</h1>
        <div style="background: #f8d7da; padding: 20px; border-radius: 5px; margin: 20px;">
            <h3>Sub-agents not available</h3>
            <p>There was an issue loading the sub-agents. Please check:</p>
            <ul>
                <li>Run from the correct directory (CityVotes_POC/)</li>
                <li>Make sure agents/ directory exists</li>
                <li>Try: <code>python3 test_agents.py</code> first</li>
            </ul>
            <p><a href="/health">Check System Health</a></p>
        </div>
        </body></html>
        ''')

    cities = city_config.get_city_display_names()

    # Sample data for testing
    sample_data = {
        "votes": [{
            "agenda_item_number": "7.1",
            "agenda_item_title": "Sample Motion",
            "outcome": "Pass",
            "tally": {
                "ayes": 4,
                "noes": 1
            },
            "member_votes": {
                "Mayor Valerie Amezcua": "Aye",
                "Vince Sarmiento": "Aye"
            }
        }]
    }

    return render_template_string(HTML_TEMPLATE,
                                cities=list(cities.values()),
                                sample_data=json.dumps(sample_data, indent=2))

@app.route('/health')
def health_check():
    """System health check endpoint"""
    health_info = {
        'flask': 'OK',
        'agents_available': AGENTS_AVAILABLE,
        'current_directory': os.getcwd(),
        'python_path': sys.path[:3]  # First 3 entries
    }

    if AGENTS_AVAILABLE:
        health_info['supported_cities'] = city_config.get_supported_cities()
        health_info['validation_ready'] = True
    else:
        health_info['error'] = 'Sub-agents not imported'

    return jsonify(health_info)

@app.route('/api/cities', methods=['GET'])
def get_cities():
    """API endpoint to get supported cities"""
    if not AGENTS_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Sub-agents not available'
        }), 503

    cities = city_config.get_city_display_names()
    return jsonify({
        'success': True,
        'cities': cities,
        'total_cities': len(cities)
    })

@app.route('/api/city/<city_name>', methods=['GET'])
def get_city_config(city_name):
    """API endpoint to get city configuration"""
    config = city_config.get_city_config(city_name)

    if not config:
        return jsonify({
            'success': False,
            'error': f'City "{city_name}" not found',
            'supported_cities': city_config.get_supported_cities()
        }), 404

    return jsonify({
        'success': True,
        'city_config': config
    })

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload with sub-agent validation"""
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file uploaded'
            }), 400

        file = request.files['file']
        city = request.form.get('city')

        if not city:
            return jsonify({
                'success': False,
                'error': 'City not specified'
            }), 400

        # Check if city is supported
        city_cfg = city_config.get_city_config(city)
        if not city_cfg:
            return jsonify({
                'success': False,
                'error': f'Unsupported city: {city}',
                'supported_cities': city_config.get_supported_cities()
            }), 400

        # Parse JSON file
        try:
            file_data = json.load(file)
        except json.JSONDecodeError as e:
            return jsonify({
                'success': False,
                'error': f'Invalid JSON file: {str(e)}'
            }), 400

        # Step 1: Validate with Data Validation Agent
        is_valid, validation_errors = data_validator.validate_json(file_data, city)

        if not is_valid:
            return jsonify({
                'success': False,
                'error': 'Validation failed',
                'validation_errors': validation_errors,
                'city': city_cfg['display_name']
            }), 400

        # Step 2: Get additional info from City Configuration Agent
        colors = city_config.get_city_colors(city)
        council_size = city_config.get_council_size(city)

        # Step 3: Basic processing summary
        summary = data_validator.get_validation_summary(file_data)

        return jsonify({
            'success': True,
            'message': 'File uploaded and validated successfully!',
            'data': {
                'city': city_cfg['display_name'],
                'validation_summary': summary,
                'city_config': {
                    'council_size': council_size,
                    'colors': colors
                },
                'next_steps': [
                    'Data is valid and ready for processing',
                    'Would integrate with dashboard visualization',
                    'Would store in session for user interaction'
                ]
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@app.route('/api/validate', methods=['POST'])
def validate_json_api():
    """API endpoint for JSON validation without file upload"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400

        city = data.get('city', 'santa_ana')  # Default to Santa Ana
        vote_data = data.get('data')

        if not vote_data:
            return jsonify({
                'success': False,
                'error': 'No vote data provided'
            }), 400

        # Validate with sub-agent
        is_valid, errors = data_validator.validate_json(vote_data, city)

        # Get city info
        city_cfg = city_config.get_city_config(city)

        response = {
            'success': True,
            'validation': {
                'is_valid': is_valid,
                'errors': errors,
                'city': city_cfg['display_name'] if city_cfg else 'Unknown'
            }
        }

        if is_valid:
            summary = data_validator.get_validation_summary(vote_data)
            response['validation']['summary'] = summary

        return jsonify(response)

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

def start_server():
    """Start the Flask server with proper configuration"""
    print("\n" + "="*50)
    print("CityVotes POC - Sub-Agent Flask Demo")
    print("="*50)

    if AGENTS_AVAILABLE:
        print("✓ Sub-agents initialized:")
        print(f"  - Data Validation Agent: Ready")
        print(f"  - City Configuration Agent: {len(city_config.get_supported_cities())} cities configured")
    else:
        print("⚠ Running in fallback mode (sub-agents not available)")

    print(f"\n✓ Current directory: {os.getcwd()}")
    print(f"✓ Python path includes: {current_dir}")

    # Try multiple ports in case 5000 is busy
    ports_to_try = [5000, 5001, 8000, 8080]

    for port in ports_to_try:
        try:
            print(f"\n🚀 Starting server...")
            print(f"   URL: http://127.0.0.1:{port}")
            print(f"   ALT: http://localhost:{port}")
            print("\nEndpoints:")
            print("  - GET  /health (system status)")
            print("  - GET  /api/cities")
            print("  - GET  /api/city/<city_name>")
            print("  - POST /upload (file upload)")
            print("  - POST /api/validate (JSON validation)")
            print("\n" + "="*50)

            app.run(debug=True, host='0.0.0.0', port=port, threaded=True)
            break

        except OSError as e:
            if "Address already in use" in str(e):
                print(f"Port {port} is busy, trying next port...")
                continue
            else:
                print(f"Error starting server on port {port}: {e}")
                break
    else:
        print("Could not start server on any available port")

if __name__ == '__main__':
    start_server()