"""WSGI entry point used by gunicorn / production servers."""

from app import create_app
from app.llm_service import llm_service
from config import Config

application = create_app()

if Config.GROQ_API_KEY:
    try:
        llm_service.initialize(Config.GROQ_API_KEY)
        application.logger.info("LLM service initialized successfully")
    except Exception as exc:
        application.logger.error(f"Failed to initialize LLM service: {exc}")
else:
    application.logger.warning(
        "GROQ_API_KEY not set. Lesson generation will fail until it is configured."
    )
