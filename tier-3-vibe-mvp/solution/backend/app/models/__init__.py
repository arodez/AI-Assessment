"""Importing this module registers User/Event/Registration on db.metadata.

Both create_app() and migrations/env.py import this before calling
db.create_all() / autogenerating — a classic Flask-SQLAlchemy trap is
calling create_all() before the models have ever been imported, which
silently creates zero tables.
"""

from app.models.event import Event
from app.models.registration import Registration
from app.models.user import User

__all__ = ["User", "Event", "Registration"]
