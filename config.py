"""Configuration management for Academic Lesson Generator."""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Base configuration class."""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Groq API Configuration
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    GROQ_MODEL = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')
    MAX_TOKENS = int(os.getenv('MAX_TOKENS', '32000'))
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', '5'))
    RATE_LIMIT_PER_HOUR = int(os.getenv('RATE_LIMIT_PER_HOUR', '20'))
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'app.log')
    
    # PDF Generation
    TEMP_FILE_CLEANUP_DELAY = int(os.getenv('TEMP_FILE_CLEANUP_DELAY', '3600'))
    
    # Input Validation
    MAX_TOPIC_LENGTH = 200
    MAX_GRADE_LEVEL_LENGTH = 100
    
    ALLOWED_GRADE_LEVELS = [
        "Elementary School (Grades K-2)",
        "Elementary School (Grades 3-5)",
        "Middle School (Grades 6-8)",
        "High School (Grades 9-10)",
        "High School (Grades 11-12)",
        "College Undergraduate",
        "Graduate Level"
    ]


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
