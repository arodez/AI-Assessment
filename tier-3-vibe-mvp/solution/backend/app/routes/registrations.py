"""POST /event/:id/register, DELETE /event/:id/register — BRIEF §7.4.

The two endpoints with real branching logic; see docstrings below and
PLAN-backend.md §7 for the full rationale.
"""

from datetime import UTC, datetime

from flask import Blueprint, jsonify
from flask.typing import ResponseReturnValue
from flask_jwt_extended import jwt_required

from app.auth import current_user_id
from app.errors import AlreadyRegisteredError, EventFullError, NoActiveRegistrationError
from app.extensions import db
from app.models import Registration
from app.models.enums import RegistrationStatus
from app.routes.helpers import get_event_or_404, parse_event_id
from app.routes.serializers import serialize_event

bp = Blueprint("registrations", __name__)


def _utcnow() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


@bp.post("/event/<event_id>/register")
@jwt_required()
def register(event_id: str) -> ResponseReturnValue:
    parsed_id = parse_event_id(event_id)
    event = get_event_or_404(parsed_id)
    uid = current_user_id()

    existing = Registration.query.filter_by(user_id=uid, event_id=event.id).first()

    if existing is not None and existing.status == RegistrationStatus.CONFIRMED:
        raise AlreadyRegisteredError("You are already registered for this event.")

    # Checked for BOTH a fresh signup and a re-signup-after-cancel — a
    # cancelled slot could have been backfilled by someone else since.
    confirmed_count = event.registrations.filter_by(
        status=RegistrationStatus.CONFIRMED
    ).count()
    if confirmed_count >= event.spots:
        raise EventFullError("This event is full.")

    if existing is not None:
        # Re-signup after cancellation: flip the SAME row back to
        # Confirmed rather than inserting a second one — the unique
        # constraint on (user_id, event_id) would reject a second row
        # anyway, and BRIEF requires reusing it.
        existing.status = RegistrationStatus.CONFIRMED
        existing.sign_up_at = _utcnow()
    else:
        db.session.add(
            Registration(
                user_id=uid,
                event_id=event.id,
                status=RegistrationStatus.CONFIRMED,
                sign_up_at=_utcnow(),
            )
        )

    db.session.commit()
    return jsonify(serialize_event(event, viewer_id=uid)), 201


@bp.delete("/event/<event_id>/register")
@jwt_required()
def cancel(event_id: str) -> ResponseReturnValue:
    parsed_id = parse_event_id(event_id)
    event = get_event_or_404(parsed_id)
    uid = current_user_id()

    existing = Registration.query.filter_by(user_id=uid, event_id=event.id).first()
    # "Never registered" and "already cancelled" collapse to the same 400
    # — BRIEF's wording is just "no active registration", no need for two
    # separate error codes.
    if existing is None or existing.status == RegistrationStatus.CANCELLED:
        raise NoActiveRegistrationError(
            "You have no active registration for this event."
        )

    existing.status = RegistrationStatus.CANCELLED
    # sign_up_at is deliberately left untouched — BRIEF defines it as
    # refreshed only when status moves TO Confirmed, not away from it.
    db.session.commit()
    return "", 204
