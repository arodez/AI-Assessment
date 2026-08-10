"""Shared extension instances, kept separate from app/__init__.py to avoid
circular imports (models import `db` from here, the app factory imports
both `db` and the models).
"""

from typing import Any

from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine

db = SQLAlchemy()
jwt = JWTManager()
cors = CORS()


@event.listens_for(Engine, "connect")
def _enable_sqlite_foreign_keys(dbapi_connection: Any, connection_record: Any) -> None:
    """SQLite disables foreign-key enforcement by default, per-connection.

    Without this, the FKs declared on Registration (user_id/event_id) would
    exist in the schema but silently allow orphan rows. This fires on every
    new DBAPI connection SQLAlchemy opens (app, CLI commands, tests, and
    Alembic all go through this Engine machinery), so setting it once here
    covers all of them.
    """
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
