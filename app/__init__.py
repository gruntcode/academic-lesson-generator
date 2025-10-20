"""Academic Lesson Generator Flask Application."""
import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import config


# Initialize Flask-Limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)


def create_app(config_name=None):
    """Application factory pattern."""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    # Get the parent directory (project root) for templates and static files
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    app = Flask(__name__, 
                template_folder=os.path.join(parent_dir, 'templates'),
                static_folder=os.path.join(parent_dir, 'static'))
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    limiter.init_app(app)
    
    # Setup logging
    setup_logging(app)
    
    # Register blueprints
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    # Log startup
    app.logger.info(f'Academic Lesson Generator started in {config_name} mode')
    
    return app


def setup_logging(app):
    """Configure application logging."""
    if not app.debug and not app.testing:
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        # Setup file handler with rotation
        file_handler = RotatingFileHandler(
            f'logs/{app.config["LOG_FILE"]}',
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(getattr(logging, app.config['LOG_LEVEL']))
        app.logger.addHandler(file_handler)
    
    app.logger.setLevel(getattr(logging, app.config.get('LOG_LEVEL', 'INFO')))
    app.logger.info('Academic Lesson Generator startup')
