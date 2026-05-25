"""Route handlers for the Academic Lesson Generator."""

import os

import groq
from flask import (
    Blueprint,
    after_this_request,
    current_app,
    jsonify,
    render_template,
    request,
    send_file,
)

from app import limiter
from app.llm_service import llm_service
from app.pdf_generator import pdf_generator
from app.utils import sanitize_filename, validate_grade_level, validate_topic

main_bp = Blueprint("main", __name__)


def _per_minute_limit():
    return f"{current_app.config['RATE_LIMIT_PER_MINUTE']}/minute"


def _per_hour_limit():
    return f"{current_app.config['RATE_LIMIT_PER_HOUR']}/hour"


@main_bp.route("/")
def index():
    """Render the main page."""
    return render_template("index.html")


@main_bp.route("/generate-lesson", methods=["POST"])
@limiter.limit(_per_minute_limit)
@limiter.limit(_per_hour_limit)
def generate_lesson():
    """Generate a lesson and return a PDF file."""
    try:
        topic = request.form.get("topic", "").strip()
        grade_level = request.form.get("grade_level", "").strip()

        is_valid, error_msg = validate_topic(topic)
        if not is_valid:
            current_app.logger.warning(f"Invalid topic: {error_msg}")
            return jsonify({"error": error_msg}), 400

        is_valid, error_msg = validate_grade_level(grade_level)
        if not is_valid:
            current_app.logger.warning(f"Invalid grade level: {error_msg}")
            return jsonify({"error": error_msg}), 400

        current_app.logger.info(f"Generating lesson for topic: {topic}, grade: {grade_level}")

        try:
            lesson_content = llm_service.generate_lesson_content(topic, grade_level)
        except groq.APIError as e:
            current_app.logger.error(f"Groq API error: {e}")
            return (
                jsonify({"error": "AI service is currently unavailable. Please try again later."}),
                503,
            )
        except ValueError as e:
            current_app.logger.error(f"LLM service error: {e}")
            return jsonify({"error": "Service configuration error. Please contact support."}), 500

        try:
            pdf_path = pdf_generator.create_pdf(topic, grade_level, lesson_content)
        except Exception as e:
            current_app.logger.error(f"PDF generation error: {e}")
            return jsonify({"error": "Failed to generate PDF. Please try again."}), 500

        @after_this_request
        def cleanup(response):
            try:
                if os.path.exists(pdf_path):
                    os.unlink(pdf_path)
                    current_app.logger.info(f"Cleaned up temporary file: {pdf_path}")
            except Exception as e:
                current_app.logger.error(f"Failed to cleanup temp file {pdf_path}: {e}")
            return response

        safe_topic = sanitize_filename(topic)
        download_name = f"{safe_topic}_lesson.pdf"

        current_app.logger.info(f"Sending PDF: {download_name}")

        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=download_name,
            mimetype="application/pdf",
        )

    except Exception:
        current_app.logger.exception("Unexpected error in generate_lesson")
        return jsonify({"error": "An unexpected error occurred. Please try again."}), 500


@main_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    status = {
        "status": "healthy",
        "service": "Academic Lesson Generator",
        "llm_configured": llm_service.client is not None,
    }
    return jsonify(status), 200
