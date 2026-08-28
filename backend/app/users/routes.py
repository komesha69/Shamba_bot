"""Users API routes."""
from flask import Blueprint, jsonify, g
from backend.app.auth.decorators import jwt_required, permission_required
from backend.app.models.user import User

users_bp = Blueprint("users", __name__, url_prefix="/api/users")


@users_bp.route("", methods=["GET"])
@jwt_required
@permission_required("MANAGE_USERS")
def list_users():
    """List all users (restricted to MANAGE_USERS permission)."""
    users = User.query.all()
    return jsonify({
        "success": True,
        "data": {
            "users": [u.to_dict() for u in users]
        }
    }), 200
