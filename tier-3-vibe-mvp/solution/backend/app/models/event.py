from app.extensions import db
from app.models.enums import EventType, LocationType, enum_values
from app.models.mixins import TimestampMixin


class Event(TimestampMixin, db.Model):  # type: ignore[name-defined]
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140), nullable=False)
    start = db.Column(db.DateTime, nullable=False)
    # "end" is a reserved SQLite keyword (CASE...END). SQLAlchemy
    # auto-quotes it in generated DDL/DML, so the ORM path just works — but
    # anyone hand-typing a verification query in the sqlite3 CLI must quote
    # it too: SELECT id, title, "end" FROM events;
    end = db.Column(db.DateTime, nullable=False)
    # Total capacity set at creation, NOT a live count. Remaining
    # availability is always computed as
    #   spots - count(registrations WHERE status='Confirmed')
    # and is never stored as a column, so it can't drift out of sync.
    spots = db.Column(db.Integer, nullable=False)
    event_type = db.Column(
        db.Enum(
            EventType,
            values_callable=enum_values,
            create_constraint=True,
            name="ck_events_event_type",
        ),
        nullable=False,
    )
    location_type = db.Column(
        db.Enum(
            LocationType,
            values_callable=enum_values,
            create_constraint=True,
            name="ck_events_location_type",
        ),
        nullable=False,
    )
    description = db.Column(db.Text, nullable=True)
    # Path the cover photo was copied/uploaded to, relative to uploads/
    # (e.g. "events/ama-room.jpg") — a convention the future API phase's
    # static-file route resolves against UPLOAD_DIR.parent.
    image = db.Column(db.String(255), nullable=True)
    # array(text) (BRIEF) -> db.JSON: stored as TEXT with automatic Python
    # list <-> JSON (de)serialization at the ORM boundary, no SQLite
    # extension required.
    location = db.Column(db.JSON, nullable=True)
    host_name = db.Column(db.String(100), nullable=True)
    host_team = db.Column(db.String(100), nullable=True)

    registrations = db.relationship(
        "Registration", back_populates="event", lazy="dynamic"
    )

    __table_args__ = (
        # Structural facts about the columns themselves (BRIEF literally
        # types spots as "positive integer" and requires end > start) —
        # not app-layer business validation, so cheap to enforce here too.
        db.CheckConstraint("spots > 0", name="ck_events_spots_positive"),
        db.CheckConstraint('"end" > start', name="ck_events_end_after_start"),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Event {self.id} {self.title!r}>"

    # No created_by/organizer column: any is_admin=true user manages any
    # event — a single flat organizer role in this MVP, not per-event
    # ownership (see BRIEF §7.3).

    # Field-length bounds from BRIEF (title 3-140, description <=2000,
    # host_name/host_team <=100, location entries <=5x200 chars) are NOT
    # enforced as DB CHECKs: SQLite ignores VARCHAR(n) length modifiers
    # entirely, and "3-140 non-whitespace" is business validation better
    # owned by the future API layer, not duplicated into schema DDL.
