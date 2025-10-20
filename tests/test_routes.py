"""Tests for route handlers."""
import pytest
from unittest.mock import patch, MagicMock
import groq


class TestIndexRoute:
    """Test the index route."""
    
    def test_index_returns_200(self, client):
        """Test that index page loads successfully."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Academic Lesson Generator' in response.data


class TestHealthCheckRoute:
    """Test the health check endpoint."""
    
    def test_health_check(self, client):
        """Test health check returns correct status."""
        response = client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert 'service' in data


class TestGenerateLessonRoute:
    """Test the lesson generation route."""
    
    def test_generate_lesson_missing_topic(self, client):
        """Test that missing topic returns 400."""
        response = client.post('/generate-lesson', data={
            'grade_level': 'Middle School (Grades 6-8)'
        })
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_generate_lesson_missing_grade_level(self, client):
        """Test that missing grade level returns 400."""
        response = client.post('/generate-lesson', data={
            'topic': 'Photosynthesis'
        })
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_generate_lesson_topic_too_short(self, client):
        """Test that topic too short returns 400."""
        response = client.post('/generate-lesson', data={
            'topic': 'AB',
            'grade_level': 'Middle School (Grades 6-8)'
        })
        assert response.status_code == 400
        data = response.get_json()
        assert 'at least 3 characters' in data['error']
    
    def test_generate_lesson_topic_too_long(self, client):
        """Test that topic too long returns 400."""
        response = client.post('/generate-lesson', data={
            'topic': 'A' * 201,
            'grade_level': 'Middle School (Grades 6-8)'
        })
        assert response.status_code == 400
        data = response.get_json()
        assert 'less than' in data['error']
    
    def test_generate_lesson_invalid_characters(self, client):
        """Test that invalid characters in topic returns 400."""
        response = client.post('/generate-lesson', data={
            'topic': 'Test<script>alert("xss")</script>',
            'grade_level': 'Middle School (Grades 6-8)'
        })
        assert response.status_code == 400
        data = response.get_json()
        assert 'invalid characters' in data['error']
    
    def test_generate_lesson_invalid_grade_level(self, client):
        """Test that invalid grade level returns 400."""
        response = client.post('/generate-lesson', data={
            'topic': 'Photosynthesis',
            'grade_level': 'Invalid Grade'
        })
        assert response.status_code == 400
        data = response.get_json()
        assert 'Invalid grade level' in data['error']
    
    @patch('app.routes.llm_service')
    @patch('app.routes.pdf_generator')
    def test_generate_lesson_success(self, mock_pdf, mock_llm, client, sample_lesson_content, tmp_path):
        """Test successful lesson generation."""
        # Setup mocks
        mock_llm.generate_lesson_content.return_value = sample_lesson_content
        
        # Create a temporary PDF file
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b'%PDF-1.4 test content')
        mock_pdf.create_pdf.return_value = str(pdf_file)
        
        response = client.post('/generate-lesson', data={
            'topic': 'Photosynthesis',
            'grade_level': 'Middle School (Grades 6-8)'
        })
        
        assert response.status_code == 200
        assert response.content_type == 'application/pdf'
        mock_llm.generate_lesson_content.assert_called_once()
        mock_pdf.create_pdf.assert_called_once()
    
    @patch('app.routes.llm_service')
    def test_generate_lesson_groq_api_error(self, mock_llm, client):
        """Test handling of Groq API errors."""
        mock_llm.generate_lesson_content.side_effect = groq.APIError("API Error")
        
        response = client.post('/generate-lesson', data={
            'topic': 'Photosynthesis',
            'grade_level': 'Middle School (Grades 6-8)'
        })
        
        assert response.status_code == 503
        data = response.get_json()
        assert 'unavailable' in data['error']
    
    @patch('app.routes.llm_service')
    @patch('app.routes.pdf_generator')
    def test_generate_lesson_pdf_error(self, mock_pdf, mock_llm, client, sample_lesson_content):
        """Test handling of PDF generation errors."""
        mock_llm.generate_lesson_content.return_value = sample_lesson_content
        mock_pdf.create_pdf.side_effect = Exception("PDF Error")
        
        response = client.post('/generate-lesson', data={
            'topic': 'Photosynthesis',
            'grade_level': 'Middle School (Grades 6-8)'
        })
        
        assert response.status_code == 500
        data = response.get_json()
        assert 'Failed to generate PDF' in data['error']


class TestErrorHandlers:
    """Test error handlers."""
    
    def test_404_handler(self, client):
        """Test 404 error handler."""
        response = client.get('/nonexistent')
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
