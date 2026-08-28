"""Authentication services and JWT token management."""
import logging
from datetime import datetime, timezone
import jwt
from flask import current_app
from backend.app.models.user import User
from backend.app.extensions import db

logger = logging.getLogger("shamba.auth")


def generate_jwt_token(user: User) -> str:
    """Generate a signed JWT token containing user identity and role."""
    secret_key = current_app.config["JWT_SECRET_KEY"]
    expires_delta = current_app.config["JWT_ACCESS_TOKEN_EXPIRES"]
    
    now = datetime.now(timezone.utc)
    exp = now + expires_delta

    payload = {
        "sub": str(user.id),
        "username": user.username,
        "email": user.email,
        "role": user.role.name if user.role else None,
        "iat": now,
        "exp": exp,
    }

    token = jwt.encode(payload, secret_key, algorithm="HS256")
    return token


def decode_jwt_token(token: str) -> dict:
    """Decode and validate JWT token signature and expiration."""
    secret_key = current_app.config["JWT_SECRET_KEY"]
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        logger.info("Authentication attempt with expired token.")
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError as e:
        logger.warning("Authentication attempt with invalid token: %s", str(e))
        raise ValueError("Invalid token")


def authenticate_user(identifier: str, password: str):
    """
    Authenticate user by username or email and password.
    Returns (user, error_code, error_message).
    """
    clean_identifier = (identifier or "").strip().lower()
    
    if not clean_identifier or not password:
        logger.info("Authentication attempt rejected: missing identifier or password.")
        return None, "INVALID_CREDENTIALS", "Invalid username or password."

    # Look up by email or username (case-insensitive)
    user = User.query.filter(
        (db.func.lower(User.username) == clean_identifier) | 
        (db.func.lower(User.email) == clean_identifier)
    ).first()

    if not user:
        logger.info("Authentication failed: user not found for identifier '%s'", clean_identifier)
        return None, "INVALID_CREDENTIALS", "Invalid username or password."

    if not user.check_password(password):
        logger.info("Authentication failed: incorrect password for user ID %s (%s)", user.id, user.username)
        return None, "INVALID_CREDENTIALS", "Invalid username or password."

    if not user.is_active:
        logger.warning("Authentication rejected: account is inactive for user ID %s (%s)", user.id, user.username)
        return None, "ACCOUNT_INACTIVE", "Your account is inactive. Please contact an administrator."

    # Record last login timestamp
    try:
        user.last_login_at = datetime.utcnow()
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error("Failed to update last_login_at for user %s: %s", user.id, str(e))

    logger.info("Authentication successful for user ID %s (%s, role: %s)", user.id, user.username, user.role.name if user.role else "None")
    return user, None, None
