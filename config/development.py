"""
Development Configuration for CityVotes POC
"""

import os

class DevelopmentConfig:
    """Development configuration settings"""

    DEBUG = True
    TESTING = False

    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-cityvotes-secret-key-2024')

    # File Upload Settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'uploads'

    # Session Configuration
    PERMANENT_SESSION_LIFETIME = 7200  # 2 hours in seconds

    # Sub-Agent Configuration
    SUBAGENT_TIMEOUT = 30  # seconds
    SESSION_CLEANUP_INTERVAL = 3600  # 1 hour in seconds

    # Logging
    LOG_LEVEL = 'DEBUG'

    @staticmethod
    def init_app(app):
        """Initialize app with development settings"""
        # Create upload directory
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

        # Enable debug mode
        app.debug = True