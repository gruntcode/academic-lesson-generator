"""Configuration management for Academic Lesson Generator."""

import os
import secrets

from dotenv import load_dotenv

load_dotenv()


_DEV_SECRET_KEY = "dev-secret-key-change-in-production"


class Config:
    """Base configuration class."""

    SECRET_KEY = os.getenv("SECRET_KEY", _DEV_SECRET_KEY)
    DEBUG = os.getenv("FLASK_DEBUG", "False").lower() == "true"

    # Groq API
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
    # openai/gpt-oss-120b allows up to 65,536 completion tokens, but Groq's on-demand
    # tier caps us at 8,000 tokens/minute and counts prompt + max_tokens against that
    # limit up front. The lesson prompt is ~600 tokens, so anything above ~7,400 here
    # gets rejected with a 413 before generation starts.
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "7000"))
    GROQ_TEMPERATURE = float(os.getenv("GROQ_TEMPERATURE", "0.4"))

    # Rate limiting
    RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "5"))
    RATE_LIMIT_PER_HOUR = int(os.getenv("RATE_LIMIT_PER_HOUR", "20"))

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "app.log")

    # PDF generation
    TEMP_FILE_CLEANUP_DELAY = int(os.getenv("TEMP_FILE_CLEANUP_DELAY", "3600"))

    # Input validation
    MAX_TOPIC_LENGTH = 200
    MAX_GRADE_LEVEL_LENGTH = 100

    ALLOWED_GRADE_LEVELS = [
        "Elementary School (Grades K-2)",
        "Elementary School (Grades 3-5)",
        "Middle School (Grades 6-8)",
        "High School (Grades 9-10)",
        "High School (Grades 11-12)",
        "College Undergraduate",
        "Graduate Level",
    ]

    @classmethod
    def validate(cls):
        """Hook for per-environment validation. No-op by default."""
        return


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False

    @classmethod
    def validate(cls):
        secret = os.getenv("SECRET_KEY")
        if not secret or secret == _DEV_SECRET_KEY:
            raise RuntimeError(
                "SECRET_KEY must be set to a strong, unique value in production. "
                "Generate one with: python -c 'import secrets; print(secrets.token_hex(32))'"
            )
        if not os.getenv("GROQ_API_KEY"):
            raise RuntimeError("GROQ_API_KEY must be set in production.")


class TestingConfig(Config):
    """Testing configuration."""

    TESTING = True
    DEBUG = True
    SECRET_KEY = secrets.token_hex(16)


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
