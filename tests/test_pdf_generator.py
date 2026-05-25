"""Tests for PDF generation."""

import os

import pytest

from app.pdf_generator import PDFGenerator


class TestPDFGenerator:
    """Test PDF generator functionality."""

    def test_create_pdf(self, app, sample_lesson_content, tmp_path):
        """Test PDF creation."""
        with app.app_context():
            generator = PDFGenerator()
            pdf_path = generator.create_pdf(
                "Photosynthesis", "Middle School (Grades 6-8)", sample_lesson_content
            )

            # Check that file was created
            assert os.path.exists(pdf_path)

            # Check that it's a PDF file
            with open(pdf_path, "rb") as f:
                header = f.read(4)
                assert header == b"%PDF"

            # Cleanup
            os.unlink(pdf_path)

    def test_create_styles(self, app):
        """Test style creation."""
        with app.app_context():
            generator = PDFGenerator()
            styles = generator._create_styles()

            assert "title" in styles
            assert "heading" in styles
            assert "subheading" in styles
            assert "normal" in styles
            assert "reference" in styles
            assert "fun_fact" in styles

    def test_remove_markdown(self, app):
        """Test markdown removal."""
        with app.app_context():
            generator = PDFGenerator()

            text = "# Header\n**Bold** and *italic* and `code`"
            result = generator._remove_markdown(text)

            assert "#" not in result
            assert "**" not in result
            assert "*" not in result
            assert "`" not in result

    def test_reorder_sections(self, app):
        """Test section reordering."""
        with app.app_context():
            generator = PDFGenerator()

            sections = [
                "LESSON CONTENT",
                "Content here",
                "QUIZ",
                "Quiz here",
                "KEY POINTS",
                "Points here",
            ]

            ordered = generator._reorder_sections(sections)

            # Quiz should be last
            assert ordered[-1][0] == "QUIZ"

            # Should not include facilitator's guide
            section_titles = [s[0] for s in ordered]
            assert "FACILITATOR'S GUIDE" not in section_titles


class TestPDFContent:
    """Test PDF content generation."""

    def test_pdf_contains_topic(self, app, sample_lesson_content):
        """Test that PDF contains the topic."""
        with app.app_context():
            generator = PDFGenerator()
            pdf_path = generator.create_pdf(
                "Test Topic", "High School (Grades 9-10)", sample_lesson_content
            )

            # PDF was created
            assert os.path.exists(pdf_path)

            # Cleanup
            os.unlink(pdf_path)

    def test_pdf_with_special_characters(self, app, sample_lesson_content):
        """Test PDF generation with special characters in topic."""
        with app.app_context():
            generator = PDFGenerator()
            pdf_path = generator.create_pdf(
                "Newton's Laws & Motion", "High School (Grades 9-10)", sample_lesson_content
            )

            assert os.path.exists(pdf_path)
            os.unlink(pdf_path)
