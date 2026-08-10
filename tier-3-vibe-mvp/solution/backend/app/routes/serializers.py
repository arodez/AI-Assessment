"""Response shaping shared by GET /events and GET /event/:id/details.

Two fields here go beyond BRIEF's literal schema — deliberate gap-fills,
documented in docs/API.md:

- `remaining_spots`: BRIEF requires GET /events to include "computed
  remaining spots"; computed the same way everywhere (spots - count of
  Confirmed registrations), never stored.
- `viewer_status`: not in BRIEF's data model at all, but the mockups'
  Feed screen renders a different CTA per event ("Sign up" / "You're
  going" / "Cancel") based on whether the CALLING user is registered —
  there's no other way for the frontend to know that without an extra
  round-trip per card.
- `image_url`: a browser-loadable path (via the /uploads static route
  added in app/__init__.py), not the raw DB-internal `events/<file>`
  value.
"""

from app.models import Event
from app.models.enums import RegistrationStatus


def _image_url(event: Event) -> str | None:
    return f"/uploads/{event.image}" if event.image else None


def _viewer_status(event: Event, viewer_id: int | None) -> str | None:
    if viewer_id is None:
        return None
    reg = event.registrations.filter_by(user_id=viewer_id).first()
    if reg is None:
        return None
    return "confirmed" if reg.status == RegistrationStatus.CONFIRMED else "cancelled"


def serialize_event(event: Event, viewer_id: int | None) -> dict:
    confirmed_count = event.registrations.filter_by(
        status=RegistrationStatus.CONFIRMED
    ).count()

    return {
        "id": event.id,
        "title": event.title,
        "start": event.start.isoformat(),
        "end": event.end.isoformat(),
        "spots": event.spots,
        "remaining_spots": event.spots - confirmed_count,
        "event_type": event.event_type.value,
        "location_type": event.location_type.value,
        "description": event.description,
        "image_url": _image_url(event),
        "location": event.location,
        "host_name": event.host_name,
        "host_team": event.host_team,
        "viewer_status": _viewer_status(event, viewer_id),
        "created_at": event.created_at.isoformat(),
        "updated_at": event.updated_at.isoformat(),
    }
