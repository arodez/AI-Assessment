"""App configuration and the runtime paths every entry point (app factory,
Alembic's env.py, the seed script) needs to agree on.
"""

import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent  # solution/backend/
load_dotenv(BASE_DIR / ".env")

INSTANCE_DIR = BASE_DIR / "instance"
UPLOAD_DIR = BASE_DIR / "uploads" / "events"

_default_db_path = INSTANCE_DIR / "app.db"


class Config:
    # Built from an already-absolute path so the sqlite:/// URL never depends
    # on the process's current working directory at connect time.
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{_default_db_path.as_posix()}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", str(UPLOAD_DIR))

    # --- Auth (BRIEF §7.1: JWT, no refresh/logout flow, fixed expiry) ---
    JWT_SECRET_KEY = os.environ.get(
        "JWT_SECRET_KEY", "dev-only-change-me-not-a-real-secret-32chars"
    )
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        hours=int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRES_HOURS", "24"))
    )
    JWT_TOKEN_LOCATION = ["headers"]  # Authorization: Bearer <token> only, no cookies

    # --- CORS (the future React frontend's allowed origin(s)) ---
    CORS_ALLOWED_ORIGINS = [
        origin.strip()
        for origin in os.environ.get("CORS_ALLOWED_ORIGINS", "").split(",")
        if origin.strip()
    ]

    # --- Upload guardrails ---
    # Defense in depth ahead of the app-level 5MB image check below: Flask
    # rejects any request body over this size outright, before it's even
    # fully read into memory.
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH_MB", "6")) * 1024 * 1024

    # Cover-photo validation constants (BRIEF §7.3), kept alongside
    # UPLOAD_FOLDER since both the image-processing service and the
    # EventCreateRequest schema need to agree on them.
    IMAGE_ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}
    IMAGE_MIN_WIDTH = 400
    IMAGE_MIN_HEIGHT = 250
    IMAGE_MAX_DIM = 4000
    IMAGE_MAX_BYTES = 5 * 1024 * 1024


def ensure_runtime_dirs() -> None:
    """Create instance/ and uploads/events/ if missing.

    Called both by create_app() (normal app startup) and by
    migrations/env.py (Alembic runs standalone, without going through the
    app factory) so the SQLite file always has somewhere to be created.
    """
    INSTANCE_DIR.mkdir(parents=True, exist_ok=True)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
