"""
CityVotes POC Flask Application
Main application package initialization
"""

from flask import Flask
import os
from datetime import timedelta

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'cityvotes-poc-secret-key-2024')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)

    # Initialize sub-agents
    from agents import DataValidationAgent, CityConfigAgent, FileProcessingAgent

    app.data_validator = DataValidationAgent()
    app.city_config = CityConfigAgent()
    app.file_processor = FileProcessingAgent(app.data_validator, app.city_config)

    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.api import api_bp
    from app.routes.dashboard import dashboard_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')

    return app