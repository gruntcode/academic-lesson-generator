"""Route handlers for the Academic Lesson Generator."""
import os
import groq
from flask import Blueprint, render_template, request, jsonify, send_file, current_app, after_this_request
from app import limiter
from app.llm_service import llm_service
from app.pdf_generator import pdf_generator
from app.utils import validate_topic, validate_grade_level, sanitize_filename


# Create blueprint
main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')


@main_bp.route('/generate-lesson', methods=['POST'])
@limiter.limit(f"{os.getenv('RATE_LIMIT_PER_MINUTE', '5')}/minute")
@limiter.limit(f"{os.getenv('RATE_LIMIT_PER_HOUR', '20')}/hour")
def generate_lesson():
    """
    Generate a lesson and return a PDF file.
    
    Returns:
        PDF file or JSON error response
    """
    try:
        # Get and validate form data
        topic = request.form.get('topic', '').strip()
        grade_level = request.form.get('grade_level', '').strip()
        
        # Validate topic
        is_valid, error_msg = validate_topic(topic)
        if not is_valid:
            current_app.logger.warning(f"Invalid topic: {error_msg}")
            return jsonify({"error": error_msg}), 400
        
        # Validate grade level
        is_valid, error_msg = validate_grade_level(grade_level)
        if not is_valid:
            current_app.logger.warning(f"Invalid grade level: {error_msg}")
            return jsonify({"error": error_msg}), 400
        
        current_app.logger.info(f"Generating lesson for topic: {topic}, grade: {grade_level}")
        
        # Generate lesson content using LLM
        try:
            lesson_content = llm_service.generate_lesson_content(topic, grade_level)
        except groq.APIError as e:
            current_app.logger.error(f"Groq API error: {e}")
            return jsonify({"error": "AI service is currently unavailable. Please try again later."}), 503
        except ValueError as e:
            current_app.logger.error(f"LLM service error: {e}")
            return jsonify({"error": "Service configuration error. Please contact support."}), 500
        
        # Generate PDF
        try:
            pdf_path = pdf_generator.create_pdf(topic, grade_level, lesson_content)
        except Exception as e:
            current_app.logger.error(f"PDF generation error: {e}")
            return jsonify({"error": "Failed to generate PDF. Please try again."}), 500
        
        # Setup cleanup after request
        @after_this_request
        def cleanup(response):
            """Clean up temporary PDF file after sending."""
            try:
                if os.path.exists(pdf_path):
                    os.unlink(pdf_path)
                    current_app.logger.info(f"Cleaned up temporary file: {pdf_path}")
            except Exception as e:
                current_app.logger.error(f"Failed to cleanup temp file {pdf_path}: {e}")
            return response
        
        # Sanitize filename
        safe_topic = sanitize_filename(topic)
        download_name = f"{safe_topic}_lesson.pdf"
        
        current_app.logger.info(f"Sending PDF: {download_name}")
        
        # Return the PDF file for download
        return send_file(
            pdf_path, 
            as_attachment=True,
            download_name=download_name,
            mimetype='application/pdf'
        )
    
    except Exception as e:
        current_app.logger.exception("Unexpected error in generate_lesson")
        return jsonify({"error": "An unexpected error occurred. Please try again."}), 500


@main_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.
    
    Returns:
        JSON response with service status
    """
    status = {
        "status": "healthy",
        "service": "Academic Lesson Generator",
        "llm_configured": llm_service.client is not None
    }
    return jsonify(status), 200


@main_bp.errorhandler(429)
def ratelimit_handler(e):
    """
    Handle rate limit exceeded errors.
    
    Args:
        e: The rate limit error
        
    Returns:
        JSON error response
    """
    current_app.logger.warning(f"Rate limit exceeded: {request.remote_addr}")
    return jsonify({
        "error": "Rate limit exceeded. Please try again later.",
        "message": str(e.description)
    }), 429


@main_bp.errorhandler(404)
def not_found_handler(e):
    """
    Handle 404 errors.
    
    Args:
        e: The error
        
    Returns:
        JSON error response
    """
    return jsonify({"error": "Resource not found"}), 404


@main_bp.errorhandler(500)
def internal_error_handler(e):
    """
    Handle 500 errors.
    
    Args:
        e: The error
        
    Returns:
        JSON error response
    """
    current_app.logger.exception("Internal server error")
    return jsonify({"error": "Internal server error"}), 500
