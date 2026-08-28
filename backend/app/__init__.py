"""Flask Application Factory."""
import logging
import os
import sys
from flask import Flask, jsonify
from backend.app.config import Config
from backend.app.extensions import db, migrate, cors


def setup_logging(app: Flask):
    """Configure structured logging for authentication and server events."""
    log_level = logging.DEBUG if app.config.get("DEBUG") else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def create_app(config_class=Config):
    """Create and configure the Flask application instance."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    setup_logging(app)
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    # Register blueprints
    from backend.app.auth.routes import auth_bp
    from backend.app.users.routes import users_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)

    # Health check endpoint
    @app.route("/api/health", methods=["GET"])
    def health_check():
        return jsonify({
            "success": True,
            "data": {
                "status": "healthy",
                "service": "shamba-auth-api",
                "environment": os.getenv("FLASK_ENV", "production"),
            }
        }), 200

    # Global error handlers for consistent JSON format
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({
            "success": False,
            "error": {
                "code": "BAD_REQUEST",
                "message": str(e.description) if hasattr(e, "description") else "Bad request."
            }
        }), 400

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({
            "success": False,
            "error": {
                "code": "RESOURCE_NOT_FOUND",
                "message": "The requested API endpoint was not found."
            }
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({
            "success": False,
            "error": {
                "code": "METHOD_NOT_ALLOWED",
                "message": "The HTTP method is not allowed for this endpoint."
            }
        }), 405

    @app.errorhandler(500)
    def internal_server_error(e):
        app.logger.error("Internal Server Error: %s", str(e))
        return jsonify({
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "Unable to connect to Shamba. Please try again."
            }
        }), 500

    # Security headers on every response
    @app.after_request
    def set_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response

    # Register custom CLI commands
    from backend.app.commands import register_commands
    register_commands(app)

    return app
