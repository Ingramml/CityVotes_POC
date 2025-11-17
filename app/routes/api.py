"""
API routes for CityVotes POC
JSON endpoints for AJAX requests and external integration
"""

from flask import Blueprint, jsonify, request, session, current_app

api_bp = Blueprint('api', __name__)

@api_bp.route('/cities')
def get_cities():
    """Get supported cities"""
    try:
        cities = current_app.city_config.get_city_display_names()
        supported = current_app.city_config.get_supported_cities()

        return jsonify({
            'success': True,
            'cities': cities,
            'supported_cities': supported,
            'total': len(cities)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/city/<city_name>')
def get_city_config(city_name):
    """Get city configuration details"""
    try:
        config = current_app.city_config.get_city_config(city_name)

        if not config:
            return jsonify({
                'success': False,
                'error': f'City "{city_name}" not found'
            }), 404

        return jsonify({
            'success': True,
            'city': config
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/session/data')
def get_session_data():
    """Get current session data"""
    try:
        session_id = session.get('session_id')
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'No active session'
            }), 404

        # Get session summary
        summary = current_app.file_processor.get_processing_summary(session_id)

        if 'error' in summary:
            return jsonify({
                'success': False,
                'error': summary['error']
            }), 404

        return jsonify({
            'success': True,
            'session': summary
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/session/cities')
def get_session_cities():
    """Get cities with data in current session"""
    try:
        session_id = session.get('session_id')
        if not session_id:
            return jsonify({
                'success': True,
                'cities': []
            })

        cities = current_app.file_processor.get_session_cities(session_id)
        city_info = {}

        for city_key in cities:
            config = current_app.city_config.get_city_config(city_key)
            city_info[city_key] = config['display_name'] if config else city_key.title()

        return jsonify({
            'success': True,
            'cities': cities,
            'city_info': city_info
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/dashboard/<city_name>/summary')
def get_dashboard_summary(city_name):
    """Get dashboard summary data for a city"""
    try:
        session_id = session.get('session_id')
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'No active session'
            }), 404

        # Get session data for city
        session_data = current_app.file_processor.get_session_data(session_id, city_name)
        if not session_data:
            return jsonify({
                'success': False,
                'error': f'No data found for {city_name}'
            }), 404

        processed_data = session_data['processed_data']

        return jsonify({
            'success': True,
            'city': city_name,
            'data': {
                'vote_summary': processed_data['vote_summary'],
                'member_analysis': processed_data['member_analysis'],
                'city_info': processed_data['city_info'],
                'upload_info': {
                    'filename': session_data['original_filename'],
                    'timestamp': session_data['upload_timestamp']
                }
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/dashboard/comparison')
def get_comparison_data():
    """Get data for city comparison dashboard"""
    try:
        session_id = session.get('session_id')
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'No active session'
            }), 404

        cities = current_app.file_processor.get_session_cities(session_id)

        if len(cities) < 2:
            return jsonify({
                'success': False,
                'error': 'Need at least 2 cities for comparison'
            }), 400

        comparison_data = {}

        for city in cities:
            session_data = current_app.file_processor.get_session_data(session_id, city)
            if session_data:
                city_config = current_app.city_config.get_city_config(city)
                comparison_data[city] = {
                    'display_name': city_config['display_name'] if city_config else city.title(),
                    'vote_summary': session_data['processed_data']['vote_summary'],
                    'member_count': len(session_data['processed_data']['member_analysis']),
                    'council_size': city_config['total_seats'] if city_config else 'Unknown',
                    'colors': city_config['colors'] if city_config else {'primary': '#6c757d'}
                }

        return jsonify({
            'success': True,
            'comparison': comparison_data,
            'cities_compared': len(comparison_data)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/validate', methods=['POST'])
def validate_json():
    """Validate JSON data without saving"""
    try:
        data = request.get_json()

        if not data or 'data' not in data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400

        city = data.get('city', 'santa_ana')
        vote_data = data['data']

        # Validate with DataValidationAgent
        is_valid, errors = current_app.data_validator.validate_json(vote_data, city)

        return jsonify({
            'success': True,
            'validation': {
                'is_valid': is_valid,
                'errors': errors,
                'city': city
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500