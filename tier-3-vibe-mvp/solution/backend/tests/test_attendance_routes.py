from datetime import UTC, datetime

from app.models import Registration
from app.models.enums import RegistrationStatus


def _confirm(session, user, event, when=None):
    session.add(
        Registration(
            user_id=user.id,
            event_id=event.id,
            status=RegistrationStatus.CONFIRMED,
            sign_up_at=when or datetime.now(UTC).replace(tzinfo=None),
        )
    )
    session.commit()


def test_attendance_happy_path(client, make_user, make_event, auth_headers, session):
    admin = make_user(is_admin=True)
    attendee = make_user(
        first_name="Grace", last_name="Hopper", email="grace@company.com"
    )
    event = make_event()
    _confirm(session, attendee, event)

    resp = client.get(f"/event/{event.id}/attendance", headers=auth_headers(admin))

    assert resp.status_code == 200
    rows = resp.get_json()
    assert rows == [
        {
            "full_name": "Grace Hopper",
            "email": "grace@company.com",
            "sign_up_at": rows[0]["sign_up_at"],
            "status": "Confirmed",
        }
    ]


def test_attendance_non_admin_forbidden_existing_event(
    client, make_user, make_event, auth_headers
):
    attendee = make_user(is_admin=False)
    event = make_event()

    resp = client.get(f"/event/{event.id}/attendance", headers=auth_headers(attendee))

    assert resp.status_code == 403


def test_attendance_non_admin_forbidden_nonexistent_event_not_404(
    client, make_user, auth_headers
):
    """The explicit proof point: admin check runs before any event lookup,
    so a non-admin gets 403 even for an id that doesn't exist — never 404.
    """
    attendee = make_user(is_admin=False)

    resp = client.get("/event/999999/attendance", headers=auth_headers(attendee))

    assert resp.status_code == 403
    assert resp.get_json()["error"] == "forbidden"


def test_attendance_no_token(client, make_event):
    event = make_event()
    resp = client.get(f"/event/{event.id}/attendance")
    assert resp.status_code == 401


def test_attendance_bad_id_as_admin(client, make_user, auth_headers):
    admin = make_user(is_admin=True)
    resp = client.get("/event/not-a-number/attendance", headers=auth_headers(admin))
    assert resp.status_code == 400


def test_attendance_not_found_as_admin(client, make_user, auth_headers):
    admin = make_user(is_admin=True)
    resp = client.get("/event/999999/attendance", headers=auth_headers(admin))
    assert resp.status_code == 404


def test_attendance_download_csv_shape(
    client, make_user, make_event, auth_headers, session
):
    admin = make_user(is_admin=True)
    attendee = make_user(
        first_name="Grace", last_name="Hopper", email="grace@company.com"
    )
    event = make_event(title="Docker Basics!")
    _confirm(session, attendee, event, when=datetime(2026, 8, 8, 9, 0))

    resp = client.get(
        f"/event/{event.id}/attendance/download", headers=auth_headers(admin)
    )

    assert resp.status_code == 200
    assert resp.headers["Content-Type"].startswith("text/csv")
    disposition = resp.headers["Content-Disposition"]
    assert disposition.startswith("attachment; filename=")
    assert "docker-basics" in disposition

    lines = resp.get_data(as_text=True).splitlines()
    assert lines[0] == "full_name,email,sign_up_at,status"
    assert lines[1] == "Grace Hopper,grace@company.com,2026-08-08T09:00:00,Confirmed"


def test_attendance_download_exposes_content_disposition_via_cors(
    client, make_user, make_event, auth_headers
):
    """Regression guard: Content-Disposition isn't in the browser's default
    CORS-safelisted response headers, so a real cross-origin fetch()'s
    response.headers.get('Content-Disposition') silently returns null unless
    the server adds Access-Control-Expose-Headers — which the Flask test
    client's other requests never exercise, since CORS is a browser-side
    enforcement mechanism the test client doesn't simulate unless an Origin
    header is actually sent, as done here.
    """
    admin = make_user(is_admin=True)
    event = make_event()

    resp = client.get(
        f"/event/{event.id}/attendance/download",
        headers={**auth_headers(admin), "Origin": "http://localhost:5173"},
    )

    assert resp.status_code == 200
    exposed = resp.headers.get("Access-Control-Expose-Headers", "")
    assert "Content-Disposition" in exposed


def test_attendance_download_non_admin_forbidden(
    client, make_user, make_event, auth_headers
):
    attendee = make_user(is_admin=False)
    event = make_event()

    resp = client.get(
        f"/event/{event.id}/attendance/download", headers=auth_headers(attendee)
    )

    assert resp.status_code == 403
