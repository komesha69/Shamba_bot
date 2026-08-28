"""Role model and role_permissions association table."""
from datetime import datetime
from backend.app.extensions import db

# Many-to-many relationship table between roles and permissions
role_permissions = db.Table(
    "role_permissions",
    db.Column("role_id", db.Integer, db.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    db.Column("permission_id", db.Integer, db.ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
)


class Role(db.Model):
    """Role entity for role-based access control."""
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False, index=True)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    permissions = db.relationship(
        "Permission",
        secondary=role_permissions,
        lazy="subquery",
        backref=db.backref("roles", lazy=True),
    )
    users = db.relationship("User", back_populates="role", lazy="dynamic")

    def has_permission(self, perm_name: str) -> bool:
        """Check if role has specific permission."""
        return any(p.name == perm_name for p in self.permissions)

    def to_dict(self):
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "permissions": [p.name for p in self.permissions],
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<Role {self.name}>"
