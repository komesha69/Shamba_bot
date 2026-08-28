"""Authentication API routes."""
import logging
from flask import Blueprint, request, jsonify, g
from backend.app.auth.services import authenticate_user, generate_jwt_token
from backend.app.auth.decorators import jwt_required

logger = logging.getLogger("shamba.auth")
auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Authenticate user and issue JWT token.
    Accepts: { "username": "...", "password": "..." } or { "email": "...", "password": "..." }
    """
    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        logger.warning("Invalid or malformed JSON payload received in /api/auth/login")
        return jsonify({
            "success": False,
            "error": {
                "code": "INVALID_PAYLOAD",
                "message": "Invalid JSON body provided."
            }
        }), 400

    identifier = data.get("username") or data.get("email") or data.get("identifier")
    password = data.get("password")

    if not identifier or not password:
        logger.info("Login rejected: Missing username/email or password.")
        return jsonify({
            "success": False,
            "error": {
                "code": "INVALID_CREDENTIALS",
                "message": "Invalid username or password."
            }
        }), 401

    user, error_code, error_message = authenticate_user(identifier, password)

    if not user:
        status_code = 403 if error_code == "ACCOUNT_INACTIVE" else 401
        return jsonify({
            "success": False,
            "error": {
                "code": error_code or "INVALID_CREDENTIALS",
                "message": error_message or "Invalid username or password."
            }
        }), status_code

    token = generate_jwt_token(user)

    return jsonify({
        "success": True,
        "data": {
            "token": token,
            "user": user.to_dict()
        }
    }), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required
def get_current_user():
    """
    Return currently authenticated user's profile, role, and assigned permissions.
    """
    user = g.current_user
    return jsonify({
        "success": True,
        "data": {
            "user": user.to_dict()
        }
    }), 200


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """
    Logout endpoint. Frontend clears local token storage.
    """
    auth_header = request.headers.get("Authorization")
    user_info = "anonymous"
    if auth_header and "Bearer " in auth_header:
        user_info = "authenticated token session"
    logger.info("Logout processed for %s", user_info)

    return jsonify({
        "success": True,
        "data": {
            "message": "Successfully logged out."
        }
    }), 200
