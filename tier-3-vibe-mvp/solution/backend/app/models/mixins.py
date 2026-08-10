from datetime import UTC, datetime

from app.extensions import db


def _utcnow() -> datetime:
    # datetime.utcnow() is deprecated (loudly, on 3.12+). Storing naive-but-
    # actually-UTC datetimes is a deliberate MVP simplification: SQLite has
    # no timezone-aware column type, and mixing naive/aware datetimes in
    # later comparisons would be a worse foot-gun than just documenting
    # "everything in this DB is UTC, stored naive".
    return datetime.now(UTC).replace(tzinfo=None)


class TimestampMixin:
    """created_at/updated_at, consistent across Users, Events, Users_Events.

    `onupdate` fires automatically on any ORM-level UPDATE that touches at
    least one other column — e.g. a future cancel/re-signup flipping
    Registration.status will refresh updated_at with no extra plumbing.
    """

    created_at = db.Column(db.DateTime, nullable=False, default=_utcnow)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=_utcnow, onupdate=_utcnow
    )
