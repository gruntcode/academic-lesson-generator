"""Pytest configuration and fixtures."""
import pytest
import os
from app import create_app
from app.llm_service import llm_service


@pytest.fixture
def app():
    """Create and configure a test application instance."""
    # Set test environment variables
    os.environ['GROQ_API_KEY'] = 'test_api_key'
    
    app = create_app('testing')
    
    # Initialize LLM service with test key
    llm_service.initialize('test_api_key')
    
    yield app


@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test CLI runner."""
    return app.test_cli_runner()


@pytest.fixture
def sample_lesson_content():
    """Provide sample lesson content for testing."""
    return """
TITLE PAGE:
Title: Photosynthesis
Grade Level: Middle School (Grades 6-8)
Date: January 1, 2025
Lesson Description: This lesson covers the process of photosynthesis in plants.
Learning Expectations:
- Understand the basic process of photosynthesis
- Identify the key components needed for photosynthesis
- Explain the importance of photosynthesis

LESSON CONTENT:
Photosynthesis is the process by which plants convert light energy into chemical energy.
Plants use sunlight, water, and carbon dioxide to produce glucose and oxygen.

KEY POINTS:
- Photosynthesis occurs in chloroplasts
- Chlorophyll is the green pigment that captures light
- The equation is: 6CO2 + 6H2O + light → C6H12O6 + 6O2

REVIEW QUESTIONS:
1. What is photosynthesis?
Answer: The process by which plants convert light energy into chemical energy.

REFERENCES:
1. Smith, J. (2020). Plant Biology. Academic Press.
2. Jones, M. (2019). Photosynthesis Explained. Science Publishers.

FUN FACT:
Plants produce enough oxygen through photosynthesis to support all life on Earth!

QUIZ:
1. What gas do plants take in during photosynthesis?
Answer: Carbon dioxide (CO2)
"""
