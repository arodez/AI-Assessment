"""GET /event/:id/attendance, GET /event/:id/attendance/download — admin
only, BRIEF §7.4.

Both routes are @admin_required, which checks the is_admin JWT claim
BEFORE the view body runs — so a non-admin gets 403 even against a
nonexistent event id, never leaking whether the resource exists.
"""

from flask import Blueprint, Response, jsonify
from flask.typing import ResponseReturnValue

from app.auth import admin_required
from app.models import Event, Registration, User
from app.routes.helpers import get_event_or_404, parse_event_id
from app.services.csv_export import build_roster_csv

bp = Blueprint("attendance", __name__)


def _roster(event: Event) -> list[dict]:
    rows = (
        Registration.query.filter_by(event_id=event.id)
        .join(User, Registration.user_id == User.id)
        .order_by(Registration.sign_up_at.asc())
        .all()
    )
    return [
        {
            "full_name": f"{r.user.first_name} {r.user.last_name}",
            "email": r.user.email,
            "sign_up_at": r.sign_up_at.isoformat(),
            "status": r.status.value,
        }
        for r in rows
    ]


@bp.get("/event/<event_id>/attendance")
@admin_required
def attendance(event_id: str) -> ResponseReturnValue:
    parsed_id = parse_event_id(event_id)
    event = get_event_or_404(parsed_id)
    return jsonify(_roster(event)), 200


@bp.get("/event/<event_id>/attendance/download")
@admin_required
def attendance_download(event_id: str) -> ResponseReturnValue:
    parsed_id = parse_event_id(event_id)
    event = get_event_or_404(parsed_id)
    csv_text, filename = build_roster_csv(event)
    return Response(
        csv_text,
        mimetype="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
