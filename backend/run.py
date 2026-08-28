"""Application entry point."""
import os
import sys

# Add project root to sys.path so 'backend' package imports work cleanly
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.app import create_app
from backend.app.extensions import db
from backend.app.commands import seed_roles_and_permissions, seed_admin_user

app = create_app()

# Auto-initialize and seed tables if starting up
with app.app_context():
    try:
        db.create_all()
        roles = seed_roles_and_permissions()
        seed_admin_user(roles)
    except Exception as e:
        app.logger.error("Auto initialization failed: %s", str(e))

if __name__ == "__main__":
    port = int(os.getenv("BACKEND_PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=os.getenv("FLASK_ENV") == "development")
