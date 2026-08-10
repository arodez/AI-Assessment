"""POST /event, GET /events, GET /event/:id/details — BRIEF §7.4."""

from datetime import UTC, datetime

from flask import Blueprint, jsonify, request
from flask.typing import ResponseReturnValue
from flask_jwt_extended import jwt_required
from pydantic import ValidationError

from app.auth import admin_required, current_user_id
from app.errors import ValidationEnvelopeError
from app.extensions import db
from app.models import Event
from app.routes.helpers import get_event_or_404, parse_event_id
from app.routes.serializers import serialize_event
from app.schemas.event import EventCreateRequest
from app.services.image_processing import process_cover_image

bp = Blueprint("events", __name__)


def _utcnow() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


@bp.post("/event")
@admin_required
def create_event() -> ResponseReturnValue:
    try:
        payload = EventCreateRequest.model_validate(request.form.to_dict())
    except ValidationError as exc:
        raise ValidationEnvelopeError.from_pydantic(exc) from exc

    # Image is validated (and, if present, written to disk) BEFORE any DB
    # write — a rejected image must not leave a partially-created Event.
    image_path = process_cover_image(request.files.get("image"))

    event = Event(
        title=payload.title,
        start=payload.start,
        end=payload.end,
        spots=payload.spots,
        event_type=payload.event_type,
        location_type=payload.location_type,
        description=payload.description,
        image=image_path,
        location=payload.location,
        host_name=payload.host_name,
        host_team=payload.host_team,
    )
    db.session.add(event)
    db.session.commit()

    return jsonify(serialize_event(event, viewer_id=current_user_id())), 201


@bp.get("/events")
@jwt_required()
def list_events() -> ResponseReturnValue:
    events = (
        Event.query.filter(Event.start > _utcnow()).order_by(Event.start.asc()).all()
    )
    viewer_id = current_user_id()
    return jsonify([serialize_event(e, viewer_id) for e in events]), 200


@bp.get("/event/<event_id>/details")
@jwt_required()
def event_details(event_id: str) -> ResponseReturnValue:
    parsed_id = parse_event_id(event_id)
    event = get_event_or_404(parsed_id)
    return jsonify(serialize_event(event, viewer_id=current_user_id())), 200
