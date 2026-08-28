"""Authentication and Security Test Suite."""
import os
import sys
import pytest
from datetime import datetime, timedelta, timezone
import jwt

# Ensure project root is in path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.app import create_app
from backend.app.config import TestingConfig
from backend.app.extensions import db
from backend.app.models.permission import Permission
from backend.app.models.role import Role
from backend.app.models.user import User
from backend.app.commands import seed_roles_and_permissions


@pytest.fixture
def app():
    """Create test application configured with in-memory database."""
    app = create_app(TestingConfig)
    with app.app_context():
        db.create_all()
        role_map = seed_roles_and_permissions()
        
        # Create active test user
        admin_role = role_map["Administrator"]
        user = User(
            name="System Administrator",
            username="admin",
            email="admin@mpelabushifarms.com",
            status="active",
            role_id=admin_role.id,
        )
        user.set_password("AdminPass123!")
        db.session.add(user)

        # Create inactive user
        worker_role = role_map["Farm Worker"]
        inactive_user = User(
            name="Inactive Worker",
            username="inactive_worker",
            email="inactive@mpelabushifarms.com",
            status="inactive",
            role_id=worker_role.id,
        )
        inactive_user.set_password("WorkerPass123!")
        db.session.add(inactive_user)

        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_1_valid_login(client):
    """Test 1 — Valid login produces 200, JWT token, user role and permissions."""
    response = client.post("/api/auth/login", json={
        "username": "admin",
        "password": "AdminPass123!"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert "token" in data["data"]
    user = data["data"]["user"]
    assert user["username"] == "admin"
    assert user["role"] == "Administrator"
    assert "VIEW_DASHBOARD" in user["permissions"]
    assert "MANAGE_USERS" in user["permissions"]
    assert "password" not in user
    assert "password_hash" not in user


def test_2_invalid_password(client):
    """Test 2 — Invalid password produces 401 and generic error message."""
    response = client.post("/api/auth/login", json={
        "username": "admin",
        "password": "WrongPassword999!"
    })
    assert response.status_code == 401
    data = response.get_json()
    assert data["success"] is False
    assert data["error"]["code"] == "INVALID_CREDENTIALS"
    assert "Invalid username or password" in data["error"]["message"]


def test_3_unknown_user(client):
    """Test 3 — Unknown username produces 401 and generic error message."""
    response = client.post("/api/auth/login", json={
        "username": "nonexistent_user",
        "password": "AnyPassword123!"
    })
    assert response.status_code == 401
    data = response.get_json()
    assert data["success"] is False
    assert data["error"]["code"] == "INVALID_CREDENTIALS"
    assert "Invalid username or password" in data["error"]["message"]


def test_4_logout(client):
    """Test 4 — Logout endpoint returns 200."""
    response = client.post("/api/auth/logout")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True


def test_5_direct_protected_route_access_without_token(client):
    """Test 5 — Direct protected route access without auth produces 401."""
    response = client.get("/api/auth/me")
    assert response.status_code == 401
    data = response.get_json()
    assert data["success"] is False
    assert data["error"]["code"] == "AUTH_HEADER_MISSING"


def test_6_valid_and_invalid_token(client, app):
    """Test 6 — Token validation and expired/invalid token handling."""
    # 1. Successful login to get token
    login_resp = client.post("/api/auth/login", json={
        "username": "admin",
        "password": "AdminPass123!"
    })
    token = login_resp.get_json()["data"]["token"]

    # 2. Access /api/auth/me with valid token
    me_resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    assert me_resp.get_json()["data"]["user"]["username"] == "admin"

    # 3. Access with forged / invalid token
    bad_resp = client.get("/api/auth/me", headers={"Authorization": "Bearer totally.invalid.token"})
    assert bad_resp.status_code == 401

    # 4. Access with expired token
    with app.app_context():
        expired_payload = {
            "sub": "1",
            "username": "admin",
            "exp": datetime.now(timezone.utc) - timedelta(hours=1),
            "iat": datetime.now(timezone.utc) - timedelta(hours=2),
        }
        expired_token = jwt.encode(expired_payload, app.config["JWT_SECRET_KEY"], algorithm="HS256")

    expired_resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {expired_token}"})
    assert expired_resp.status_code == 401
    assert expired_resp.get_json()["error"]["code"] == "INVALID_TOKEN"


def test_7_inactive_account(client):
    """Test 7 — Inactive user account is blocked from login."""
    response = client.post("/api/auth/login", json={
        "username": "inactive_worker",
        "password": "WorkerPass123!"
    })
    assert response.status_code == 403
    data = response.get_json()
    assert data["success"] is False
    assert data["error"]["code"] == "ACCOUNT_INACTIVE"
    assert "account is inactive" in data["error"]["message"].lower()


def test_8_database_persistence_and_attributes(app):
    """Test 8 — Database user attributes and role/permission mappings."""
    with app.app_context():
        user = User.query.filter_by(username="admin").first()
        assert user is not None
        assert user.role is not None
        assert user.role.name == "Administrator"
        assert user.has_permission("VIEW_DASHBOARD") is True
        assert user.has_permission("MANAGE_USERS") is True
        assert user.has_permission("CREATE_BIRTH") is True


def test_9_password_security(app):
    """Test 9 — Passwords are NOT plaintext in the database."""
    with app.app_context():
        user = User.query.filter_by(username="admin").first()
        assert user.password_hash != "AdminPass123!"
        assert "pbkdf2:sha256:" in user.password_hash or "scrypt:" in user.password_hash
        assert user.check_password("AdminPass123!") is True
        assert user.check_password("WrongPassword") is False
