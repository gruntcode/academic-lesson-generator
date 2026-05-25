"""Tests for utility functions."""

import pytest

from app.utils import format_list_item, sanitize_filename, validate_grade_level, validate_topic


class TestValidateTopic:
    """Test topic validation."""

    def test_valid_topic(self, app):
        """Test validation of valid topic."""
        with app.app_context():
            is_valid, error = validate_topic("Photosynthesis")
            assert is_valid is True
            assert error is None

    def test_empty_topic(self, app):
        """Test validation of empty topic."""
        with app.app_context():
            is_valid, error = validate_topic("")
            assert is_valid is False
            assert "required" in error

    def test_topic_too_short(self, app):
        """Test validation of too short topic."""
        with app.app_context():
            is_valid, error = validate_topic("AB")
            assert is_valid is False
            assert "at least 3 characters" in error

    def test_topic_too_long(self, app):
        """Test validation of too long topic."""
        with app.app_context():
            is_valid, error = validate_topic("A" * 201)
            assert is_valid is False
            assert "less than" in error

    def test_topic_invalid_characters(self, app):
        """Test validation of topic with invalid characters."""
        with app.app_context():
            is_valid, error = validate_topic("Test<script>")
            assert is_valid is False
            assert "invalid characters" in error


class TestValidateGradeLevel:
    """Test grade level validation."""

    def test_valid_grade_level(self, app):
        """Test validation of valid grade level."""
        with app.app_context():
            is_valid, error = validate_grade_level("Middle School (Grades 6-8)")
            assert is_valid is True
            assert error is None

    def test_empty_grade_level(self, app):
        """Test validation of empty grade level."""
        with app.app_context():
            is_valid, error = validate_grade_level("")
            assert is_valid is False
            assert "required" in error

    def test_invalid_grade_level(self, app):
        """Test validation of invalid grade level."""
        with app.app_context():
            is_valid, error = validate_grade_level("Invalid Grade")
            assert is_valid is False
            assert "Invalid grade level" in error


class TestSanitizeFilename:
    """Test filename sanitization."""

    def test_sanitize_simple_filename(self):
        """Test sanitization of simple filename."""
        result = sanitize_filename("Photosynthesis")
        assert result == "Photosynthesis"

    def test_sanitize_filename_with_spaces(self):
        """Test sanitization of filename with spaces."""
        result = sanitize_filename("American Revolution")
        assert result == "American_Revolution"

    def test_sanitize_filename_with_special_chars(self):
        """Test sanitization of filename with special characters."""
        result = sanitize_filename("Test@#$%File")
        assert "@" not in result
        assert "#" not in result

    def test_sanitize_filename_with_path(self):
        """Test sanitization removes path components."""
        result = sanitize_filename("/path/to/file.txt")
        assert "/" not in result
        assert result == "file.txt"


class TestFormatListItem:
    """Test list item formatting."""

    def test_format_plain_text(self):
        """Test formatting plain text."""
        result = format_list_item("This is a point")
        assert result == "• This is a point"

    def test_format_with_dash(self):
        """Test formatting text with dash."""
        result = format_list_item("- This is a point")
        assert result == "• This is a point"

    def test_format_with_asterisk(self):
        """Test formatting text with asterisk."""
        result = format_list_item("* This is a point")
        assert result == "• This is a point"

    def test_format_with_bullet(self):
        """Test formatting text with bullet."""
        result = format_list_item("• This is a point")
        assert result == "• This is a point"

    def test_format_empty_string(self):
        """Test formatting empty string."""
        result = format_list_item("")
        assert result == ""
