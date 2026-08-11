"""CSV roster export for GET /event/:id/attendance/download.

BRIEF §7.4: filename `${event_name}-${start_date:YYYY-MM-DD}-${today:YYYY-MM-DD}.csv`,
columns `full_name`, `email`, `sign_up_at`, `status`.
"""

import csv
import io
import re
from datetime import date

from app.models import Event, Registration, User


def _slugify(title: str) -> str:
    # Guards the Content-Disposition header value against embedded quotes/
    # slashes/non-ASCII that would otherwise break the header, while
    # keeping the filename recognizably derived from event_name.
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug or "event"


def build_roster_csv(event: Event) -> tuple[str, str]:
    """Returns (csv_text, filename)."""
    rows = (
        Registration.query.filter_by(event_id=event.id)
        .join(User, Registration.user_id == User.id)
        .order_by(Registration.sign_up_at.asc())
        .all()
    )

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["full_name", "email", "sign_up_at", "status"])
    for reg in rows:
        writer.writerow(
            [
                f"{reg.user.first_name} {reg.user.last_name}",
                reg.user.email,
                reg.sign_up_at.isoformat(),
                reg.status.value,
            ]
        )

    filename = (
        f"{_slugify(event.title)}-{event.start:%Y-%m-%d}-{date.today():%Y-%m-%d}.csv"
    )
    return buf.getvalue(), filename
