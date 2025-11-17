"""
Production Configuration for CityVotes POC
"""

import os

class ProductionConfig:
    """Production configuration settings"""

    DEBUG = False
    TESTING = False

    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("No SECRET_KEY set for production")

    # File Upload Settings
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB max file size
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', '/tmp/cityvotes_uploads')

    # Session Configuration
    PERMANENT_SESSION_LIFETIME = 7200  # 2 hours in seconds
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Sub-Agent Configuration
    SUBAGENT_TIMEOUT = 30  # seconds
    SESSION_CLEANUP_INTERVAL = 1800  # 30 minutes in seconds

    # Logging
    LOG_LEVEL = 'INFO'

    # Performance
    SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1 year cache for static files

    @staticmethod
    def init_app(app):
        """Initialize app with production settings"""
        # Create upload directory
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

        # Import logging
        import logging
        from logging.handlers import RotatingFileHandler

        # Set up file logging
        if not app.debug and not app.testing:
            file_handler = RotatingFileHandler(
                'logs/cityvotes.log', maxBytes=10240000, backupCount=10)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s '
                '[in %(pathname)s:%(lineno)d]'))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            app.logger.setLevel(logging.INFO)
            app.logger.info('CityVotes POC startup')