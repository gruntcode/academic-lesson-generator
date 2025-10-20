#!/usr/bin/env python3
"""
Academic Lesson Generator - Main Application Entry Point

This application generates comprehensive academic lessons using AI.
"""
import os
from app import create_app
from app.llm_service import llm_service
from config import Config

# Create the Flask application
app = create_app()

# Initialize the LLM service with the API key
if Config.GROQ_API_KEY:
    try:
        llm_service.initialize(Config.GROQ_API_KEY)
        app.logger.info("LLM service initialized successfully")
    except Exception as e:
        app.logger.error(f"Failed to initialize LLM service: {e}")
else:
    app.logger.warning("GROQ_API_KEY not set. Please configure it in .env file.")


if __name__ == '__main__':
    # Check if GROQ_API_KEY is set
    if not Config.GROQ_API_KEY:
        print("=" * 60)
        print("WARNING: GROQ_API_KEY environment variable is not set.")
        print("Please set it in your .env file or environment before making API calls.")
        print("=" * 60)
        print()
    
    # Get configuration from environment
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', '5000'))
    
    print(f"Starting Academic Lesson Generator on http://{host}:{port}")
    print(f"Debug mode: {debug}")
    print()
    
    app.run(host=host, port=port, debug=debug)
