"""Academic Lesson Generator Flask Application."""

import logging
import os
from logging.handlers import RotatingFileHandler

from flask import Flask, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from config import config

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)


def create_app(config_name=None):
    """Application factory."""
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    app = Flask(
        __name__,
        template_folder=os.path.join(parent_dir, "templates"),
        static_folder=os.path.join(parent_dir, "static"),
    )
    cfg = config[config_name]
    cfg.validate()
    app.config.from_object(cfg)

    limiter.init_app(app)
    setup_logging(app)
    register_error_handlers(app)
    register_security_headers(app)

    from app.routes import main_bp

    app.register_blueprint(main_bp)

    app.logger.info(f"Academic Lesson Generator started in {config_name} mode")

    return app


def setup_logging(app):
    """Configure application logging."""
    log_level = getattr(logging, app.config.get("LOG_LEVEL", "INFO"))

    if not app.testing:
        os.makedirs("logs", exist_ok=True)

        file_handler = RotatingFileHandler(
            f'logs/{app.config["LOG_FILE"]}',
            maxBytes=10_240_000,  # 10 MB
            backupCount=10,
        )
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]")
        )
        file_handler.setLevel(log_level)
        app.logger.addHandler(file_handler)

    app.logger.setLevel(log_level)
    app.logger.info("Academic Lesson Generator startup")


def register_error_handlers(app):
    """Register error handlers at app level so unmatched routes are covered."""

    @app.errorhandler(404)
    def not_found(_e):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(429)
    def ratelimit_handler(e):
        app.logger.warning(f"Rate limit exceeded: {request.remote_addr}")
        return (
            jsonify(
                {
                    "error": "Rate limit exceeded. Please try again later.",
                    "message": str(e.description),
                }
            ),
            429,
        )

    @app.errorhandler(500)
    def internal_error(_e):
        app.logger.exception("Internal server error")
        return jsonify({"error": "Internal server error"}), 500


def register_security_headers(app):
    """Attach baseline security headers to every response."""

    @app.after_request
    def _set_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; "
            "style-src 'self' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "script-src 'self'; "
            "img-src 'self' data:;",
        )
        return response
