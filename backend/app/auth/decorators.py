"""Authentication and Authorization Decorators."""
from functools import wraps
from flask import request, jsonify, g
from backend.app.auth.services import decode_jwt_token
from backend.app.extensions import db
from backend.app.models.user import User


def jwt_required(f):
    """
    Middleware decorator ensuring the request contains a valid JWT token.
    Populates g.current_user and g.jwt_payload.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({
                "success": False,
                "error": {
                    "code": "AUTH_HEADER_MISSING",
                    "message": "Authorization header is required."
                }
            }), 401

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return jsonify({
                "success": False,
                "error": {
                    "code": "INVALID_AUTH_HEADER",
                    "message": "Authorization header must be Bearer <token>."
                }
            }), 401

        token = parts[1]
        try:
            payload = decode_jwt_token(token)
        except ValueError as e:
            return jsonify({
                "success": False,
                "error": {
                    "code": "INVALID_TOKEN",
                    "message": str(e)
                }
            }), 401

        user_id = payload.get("sub")
        if not user_id:
            return jsonify({
                "success": False,
                "error": {
                    "code": "INVALID_TOKEN_PAYLOAD",
                    "message": "Token subject missing."
                }
            }), 401

        user = db.session.get(User, int(user_id))
        if not user or not user.is_active:
            return jsonify({
                "success": False,
                "error": {
                    "code": "ACCOUNT_INACTIVE_OR_DELETED",
                    "message": "User account is inactive or not found."
                }
            }), 401

        g.current_user = user
        g.jwt_payload = payload
        return f(*args, **kwargs)

    return decorated_function


def permission_required(perm_name: str):
    """
    Decorator requiring specific permission on the backend.
    Enforces backend security boundary independently from React UI.
    """
    def decorator(f):
        @wraps(f)
        @jwt_required
        def decorated_function(*args, **kwargs):
            user = getattr(g, "current_user", None)
            if not user or not user.has_permission(perm_name):
                return jsonify({
                    "success": False,
                    "error": {
                        "code": "FORBIDDEN",
                        "message": f"Permission '{perm_name}' required."
                    }
                }), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def role_required(*role_names):
    """
    Decorator requiring one of the specified roles.
    """
    def decorator(f):
        @wraps(f)
        @jwt_required
        def decorated_function(*args, **kwargs):
            user = getattr(g, "current_user", None)
            if not user or not user.role or user.role.name not in role_names:
                return jsonify({
                    "success": False,
                    "error": {
                        "code": "FORBIDDEN",
                        "message": "Access restricted to authorized roles."
                    }
                }), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator
