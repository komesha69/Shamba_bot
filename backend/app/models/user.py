"""User model."""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from backend.app.extensions import db


class User(db.Model):
    """User account entity."""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), default="active", nullable=False, index=True)  # active, inactive, suspended
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    role = db.relationship("Role", back_populates="users")

    def set_password(self, password: str):
        """Securely hash and set password."""
        self.password_hash = generate_password_hash(password, method="pbkdf2:sha256")

    def check_password(self, password: str) -> bool:
        """Verify password against stored hash."""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    @property
    def is_active(self) -> bool:
        """Check if user account is active."""
        return self.status == "active"

    def has_permission(self, perm_name: str) -> bool:
        """Check if user has permission through assigned role."""
        if not self.role:
            return False
        return self.role.has_permission(perm_name)

    def to_dict(self):
        """Serialize user data safely without exposing password_hash."""
        permissions = []
        if self.role and self.role.permissions:
            permissions = [p.name for p in self.role.permissions]

        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "username": self.username,
            "status": self.status,
            "role": self.role.name if self.role else None,
            "role_id": self.role_id,
            "permissions": permissions,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
        }

    def __repr__(self):
        return f"<User {self.username} ({self.status})>"
