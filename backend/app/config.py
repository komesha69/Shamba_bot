"""Application configuration."""
import os
from datetime import timedelta
from dotenv import load_dotenv

# Load .env if present
load_dotenv()

class Config:
    """Base configuration."""
    SECRET_KEY = os.getenv("SECRET_KEY", "shamba-dev-secret-key-mpelabushi-2026")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "shamba-jwt-secret-key-mpelabushi-2026")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        minutes=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_MINUTES", "480"))
    )

    # Database resolution: Prefer DATABASE_URL; then DB_* parts; else default to local storage
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        db_user = os.getenv("DB_USER")
        db_pass = os.getenv("DB_PASSWORD", "")
        db_host = os.getenv("DB_HOST", "127.0.0.1")
        db_port = os.getenv("DB_PORT", "3306")
        db_name = os.getenv("DB_NAME")
        if db_user and db_name:
            db_url = f"mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}?charset=utf8mb4"
        else:
            # Fallback to local storage for testing / environments without configured MariaDB server
            base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
            db_url = f"sqlite:///{os.path.join(base_dir, 'shamba_local.db')}"

    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    } if "sqlite" not in db_url else {}


class TestingConfig(Config):
    """Test configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
