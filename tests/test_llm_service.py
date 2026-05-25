"""Tests for LLM service."""

from unittest.mock import Mock, patch

import groq
import pytest

from app.llm_service import LLMService


class TestLLMService:
    """Test LLM service functionality."""

    def test_initialize_with_valid_key(self):
        """Test initialization with valid API key."""
        service = LLMService()
        service.initialize("test_api_key")
        assert service.client is not None

    def test_initialize_with_empty_key(self):
        """Test initialization with empty API key."""
        service = LLMService()
        with pytest.raises(ValueError, match="GROQ_API_KEY is required"):
            service.initialize("")

    def test_initialize_with_none_key(self):
        """Test initialization with None API key."""
        service = LLMService()
        with pytest.raises(ValueError, match="GROQ_API_KEY is required"):
            service.initialize(None)

    @patch("groq.Groq")
    def test_generate_lesson_content_success(self, mock_groq_class, app):
        """Test successful lesson content generation."""
        with app.app_context():
            # Setup mock
            mock_client = Mock()
            mock_groq_class.return_value = mock_client

            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Generated lesson content"
            mock_client.chat.completions.create.return_value = mock_response

            # Test
            service = LLMService()
            service.initialize("test_key")

            result = service.generate_lesson_content("Photosynthesis", "Middle School")

            assert result == "Generated lesson content"
            mock_client.chat.completions.create.assert_called_once()

    def test_generate_lesson_content_without_initialization(self):
        """Test generation without initialization."""
        service = LLMService()

        with pytest.raises(ValueError, match="not initialized"):
            service.generate_lesson_content("Topic", "Grade")

    @patch("groq.Groq")
    def test_generate_lesson_content_api_error(self, mock_groq_class, app):
        """Test handling of API errors."""
        import httpx

        with app.app_context():
            mock_client = Mock()
            mock_groq_class.return_value = mock_client
            mock_client.chat.completions.create.side_effect = groq.APIError(
                "API Error",
                request=httpx.Request("POST", "https://api.groq.com/test"),
                body=None,
            )

            service = LLMService()
            service.initialize("test_key")

            with pytest.raises(groq.APIError):
                service.generate_lesson_content("Topic", "Grade")

    def test_build_prompt(self, app):
        """Test prompt building."""
        with app.app_context():
            service = LLMService()
            prompt = service._build_prompt("Photosynthesis", "Middle School")

            assert "Photosynthesis" in prompt
            assert "Middle School" in prompt
            assert "LESSON CONTENT" in prompt
            assert "KEY POINTS" in prompt
            assert "QUIZ" in prompt
