"""Shared helpers for route handlers.

Route id handling deliberately does NOT use Flask's `<int:event_id>`
converter: that converter 404s on a non-numeric segment before the view
even runs, but BRIEF wants a non-numeric id to be a 400 ("bad id"), not a
404. Routes take `<event_id>` as a plain string; parse_event_id() does
the 400-or-int conversion instead, called from inside the view — i.e.
after any @admin_required check has already run, preserving the
"403 before 404 (or 400)" ordering BRIEF requires for admin-only routes.
"""

from app.errors import APIError, NotFoundError
from app.extensions import db
from app.models import Event


def parse_event_id(raw: str) -> int:
    if not raw.isdigit():
        raise APIError("Event id must be a positive integer.")
    return int(raw)


def get_event_or_404(event_id: int) -> Event:
    event = db.session.get(Event, event_id)
    if event is None:
        raise NotFoundError("Event not found.")
    return event
