from app.extensions import db
from app.models.enums import RegistrationStatus, enum_values
from app.models.mixins import TimestampMixin


class Registration(TimestampMixin, db.Model):  # type: ignore[name-defined]
    """The Users_Events junction table from BRIEF §7.3."""

    __tablename__ = "users_events"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=False)
    status = db.Column(
        db.Enum(
            RegistrationStatus,
            values_callable=enum_values,
            create_constraint=True,
            name="ck_users_events_status",
        ),
        nullable=False,
    )
    sign_up_at = db.Column(db.DateTime, nullable=False)

    user = db.relationship("User", backref=db.backref("registrations", lazy="dynamic"))
    event = db.relationship("Event", back_populates="registrations")

    __table_args__ = (
        # One row per user per event. A cancellation sets status='Cancelled'
        # and never deletes the row; re-signing up after a cancellation
        # flips this same row back to 'Confirmed' with a new sign_up_at —
        # the duplicate check this constraint enforces only ever blocks a
        # *second* CONFIRMED registration attempt, handled at the API layer
        # via an UPDATE instead of a second INSERT.
        db.UniqueConstraint("user_id", "event_id", name="uq_users_events_user_event"),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Registration user={self.user_id} event={self.event_id} {self.status}>"
