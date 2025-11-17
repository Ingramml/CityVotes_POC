"""
Main routes for CityVotes POC
Handles home page, file upload, and core functionality
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
import json
import uuid

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    """Home page with city selection and upload interface"""
    # Get supported cities
    cities = current_app.city_config.get_city_display_names()

    # Initialize session if needed
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        session.permanent = True

    return render_template('home.html', cities=cities)

@main_bp.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload with drag-and-drop support"""
    try:
        # Validate form data
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(url_for('main.home'))

        file = request.files['file']
        city = request.form.get('city')

        if not file or file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('main.home'))

        if not city:
            flash('Please select a city', 'error')
            return redirect(url_for('main.home'))

        # Process file with FileProcessingAgent
        session_id = session.get('session_id')
        result = current_app.file_processor.process_uploaded_file(file, city, session_id)

        if result['success']:
            flash(f'Successfully processed {result["data_summary"]["total_votes"]} votes for {result["data_summary"]["city"]}', 'success')

            # Store city in session for dashboard navigation
            session['current_city'] = city

            return redirect(url_for('dashboard.vote_summary'))
        else:
            flash(f'Upload failed: {result["error"]}', 'error')

            # Show validation errors if available
            if 'validation_errors' in result:
                for error in result['validation_errors'][:3]:  # Show first 3 errors
                    flash(f'Validation: {error}', 'warning')

            return redirect(url_for('main.home'))

    except Exception as e:
        flash(f'Upload error: {str(e)}', 'error')
        return redirect(url_for('main.home'))

@main_bp.route('/upload')
def upload_page():
    """Dedicated upload page"""
    # Get supported cities
    cities = current_app.city_config.get_city_display_names()

    # Initialize session if needed
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        session.permanent = True

    # Get pre-selected city if any
    selected_city = session.get('selected_city')

    return render_template('upload.html', cities=cities, selected_city=selected_city)

@main_bp.route('/city/<city_name>')
def city_page(city_name):
    """Individual city page with information and navigation"""
    # Validate city
    config = current_app.city_config.get_city_config(city_name)
    if not config:
        flash(f'City "{city_name}" not supported', 'error')
        return redirect(url_for('main.home'))

    # Initialize session if needed
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        session.permanent = True

    # Check if user has data for this city
    session_id = session.get('session_id')
    has_data = False
    data_summary = None

    if session_id:
        session_data = current_app.file_processor.get_session_data(session_id, city_name)
        if session_data:
            has_data = True
            data_summary = {
                'total_votes': len(session_data.get('votes', [])),
                'upload_time': session_data.get('upload_time'),
                'filename': session_data.get('filename')
            }

    return render_template('city_page.html',
                         city_config=config,
                         city_name=city_name,
                         has_data=has_data,
                         data_summary=data_summary)

@main_bp.route('/city/<city_name>/upload')
def city_upload(city_name):
    """Redirect to upload page with pre-selected city"""
    # Validate city
    config = current_app.city_config.get_city_config(city_name)
    if not config:
        flash(f'City "{city_name}" not supported', 'error')
        return redirect(url_for('main.home'))

    # Set selected city in session
    session['selected_city'] = city_name
    return redirect(url_for('main.upload_page'))

@main_bp.route('/health')
def health_check():
    """System health check"""
    return {
        'status': 'healthy',
        'sub_agents': {
            'data_validator': 'active',
            'city_config': 'active',
            'file_processor': 'active'
        },
        'supported_cities': current_app.city_config.get_supported_cities()
    }

@main_bp.route('/sample-data')
def sample_data():
    """Provide sample JSON data for testing"""
    sample = {
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
                    "Johnathan Ryan Hernandez": "Aye",
                    "Thai Viet Phan": "Aye",
                    "Benjamin Vazquez": "Nay",
                    "David Penaloza": "Aye"
                }
            }
        ]
    }

    return render_template('sample_data.html', sample_json=json.dumps(sample, indent=2))