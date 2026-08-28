"""Custom CLI commands for database setup and seeding."""
import os
import click
from flask import Flask
from backend.app.extensions import db
from backend.app.models.permission import Permission
from backend.app.models.role import Role
from backend.app.models.user import User

ALL_PERMISSIONS = [
    ("VIEW_DASHBOARD", "Permission to view operational dashboard"),
    ("VIEW_ANIMALS", "Permission to view livestock records"),
    ("SEARCH_ANIMALS", "Permission to search animal registry"),
    ("CREATE_BIRTH", "Permission to record livestock birth"),
    ("CREATE_DEATH", "Permission to record livestock mortality"),
    ("CREATE_WEIGHT", "Permission to record animal weighings"),
    ("CREATE_MOVEMENT", "Permission to record paddock/pen movements"),
    ("CREATE_SALE", "Permission to record livestock sales"),
    ("CREATE_PURCHASE", "Permission to record livestock acquisitions"),
    ("CREATE_TRANSFER", "Permission to record livestock transfers"),
    ("CREATE_SLAUGHTER", "Permission to record slaughter/processing"),
    ("VIEW_REPORTS", "Permission to access farm analytics and reports"),
    ("VIEW_AUDIT_LOG", "Permission to view system audit logs"),
    ("MANAGE_USERS", "Permission to manage system users and roles"),
    ("MANAGE_SETTINGS", "Permission to configure farm and system settings"),
]

ROLE_CONFIGS = {
    "Administrator": {
        "description": "Full system administrative access with user and farm management privileges",
        "permissions": [p[0] for p in ALL_PERMISSIONS],
    },
    "Farm Manager": {
        "description": "Operational farm management, record creation, reports and audit logs",
        "permissions": [
            "VIEW_DASHBOARD", "VIEW_ANIMALS", "SEARCH_ANIMALS",
            "CREATE_BIRTH", "CREATE_DEATH", "CREATE_WEIGHT", "CREATE_MOVEMENT",
            "CREATE_SALE", "CREATE_PURCHASE", "CREATE_TRANSFER", "CREATE_SLAUGHTER",
            "VIEW_REPORTS", "VIEW_AUDIT_LOG",
        ],
    },
    "Farm Worker": {
        "description": "Day-to-day livestock operational logging and task tracking",
        "permissions": [
            "VIEW_DASHBOARD", "VIEW_ANIMALS", "SEARCH_ANIMALS",
            "CREATE_BIRTH", "CREATE_DEATH", "CREATE_WEIGHT", "CREATE_MOVEMENT",
        ],
    },
    "Viewer": {
        "description": "Read-only access to livestock records and farm reports",
        "permissions": [
            "VIEW_DASHBOARD", "VIEW_ANIMALS", "SEARCH_ANIMALS", "VIEW_REPORTS",
        ],
    },
}


def seed_roles_and_permissions():
    """Ensure all default permissions and roles exist and are correctly mapped."""
    # 1. Seed Permissions
    permission_map = {}
    for code, desc in ALL_PERMISSIONS:
        perm = Permission.query.filter_by(name=code).first()
        if not perm:
            perm = Permission(name=code, description=desc)
            db.session.add(perm)
            click.echo(f"  + Created permission: {code}")
        permission_map[code] = perm

    db.session.commit()

    # 2. Seed Roles and map permissions
    role_map = {}
    for role_name, config in ROLE_CONFIGS.items():
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            role = Role(name=role_name, description=config["description"])
            db.session.add(role)
            click.echo(f"  + Created role: {role_name}")
        
        # Update permissions
        role.permissions = [permission_map[p_name] for p_name in config["permissions"] if p_name in permission_map]
        role_map[role_name] = role

    db.session.commit()
    return role_map


def seed_admin_user(role_map):
    """Seed or update the default administrator user from environment variables."""
    admin_username = os.getenv("ADMIN_DEFAULT_USERNAME", "admin")
    admin_email = os.getenv("ADMIN_DEFAULT_EMAIL", "admin@mpelabushifarms.com")
    admin_password = os.getenv("ADMIN_DEFAULT_PASSWORD", "Admin@Mpelabushi2026!")
    admin_name = os.getenv("ADMIN_DEFAULT_NAME", "System Administrator")

    admin_role = role_map.get("Administrator") or Role.query.filter_by(name="Administrator").first()
    if not admin_role:
        raise ValueError("Administrator role must exist before creating admin user.")

    admin = User.query.filter((User.username == admin_username) | (User.email == admin_email)).first()
    if not admin:
        admin = User(
            name=admin_name,
            email=admin_email,
            username=admin_username,
            status="active",
            role_id=admin_role.id,
        )
        admin.set_password(admin_password)
        db.session.add(admin)
        click.echo(f"  + Created administrator user: {admin_username} ({admin_email})")
    else:
        admin.name = admin_name
        admin.status = "active"
        admin.role_id = admin_role.id
        admin.set_password(admin_password)
        click.echo(f"  * Updated administrator user credentials: {admin_username}")

    db.session.commit()


def register_commands(app: Flask):
    """Register click commands on the Flask app."""

    @app.cli.command("init-db")
    def init_db_command():
        """Create database tables and seed baseline roles and permissions."""
        click.echo("Initializing database schema...")
        db.create_all()
        click.echo("Seeding roles and permissions...")
        role_map = seed_roles_and_permissions()
        click.echo("Database initialized successfully.")

    @app.cli.command("seed-admin")
    def seed_admin_command():
        """Seed the system administrator account and required roles/permissions."""
        click.echo("Ensuring database tables exist...")
        db.create_all()
        click.echo("Seeding roles and permissions...")
        role_map = seed_roles_and_permissions()
        click.echo("Seeding administrator account...")
        seed_admin_user(role_map)
        click.echo("Administrator seeding completed successfully.")
