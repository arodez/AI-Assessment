from app.models import Registration
from app.models.enums import RegistrationStatus


def test_register_happy_path_decrements_remaining(
    client, make_user, make_event, auth_headers
):
    attendee = make_user()
    event = make_event(spots=5)

    resp = client.post(f"/event/{event.id}/register", headers=auth_headers(attendee))

    assert resp.status_code == 201
    body = resp.get_json()
    assert body["viewer_status"] == "confirmed"
    assert body["remaining_spots"] == 4


def test_register_no_token_unauthorized(client, make_event):
    event = make_event()
    resp = client.post(f"/event/{event.id}/register")
    assert resp.status_code == 401


def test_register_nonexistent_event_404(client, make_user, auth_headers):
    attendee = make_user()
    resp = client.post("/event/999999/register", headers=auth_headers(attendee))
    assert resp.status_code == 404


def test_register_bad_id_400(client, make_user, auth_headers):
    attendee = make_user()
    resp = client.post("/event/not-a-number/register", headers=auth_headers(attendee))
    assert resp.status_code == 400


def test_register_duplicate_confirmed_400(client, make_user, make_event, auth_headers):
    attendee = make_user()
    event = make_event(spots=5)
    client.post(f"/event/{event.id}/register", headers=auth_headers(attendee))

    resp = client.post(f"/event/{event.id}/register", headers=auth_headers(attendee))

    assert resp.status_code == 400
    assert resp.get_json()["error"] == "already_registered"


def test_register_full_event_400(client, make_user, make_event, auth_headers):
    event = make_event(spots=1)
    first = make_user()
    second = make_user()
    client.post(f"/event/{event.id}/register", headers=auth_headers(first))

    resp = client.post(f"/event/{event.id}/register", headers=auth_headers(second))

    assert resp.status_code == 400
    assert resp.get_json()["error"] == "event_full"


def test_cancel_happy_path(client, make_user, make_event, auth_headers):
    attendee = make_user()
    event = make_event(spots=5)
    client.post(f"/event/{event.id}/register", headers=auth_headers(attendee))

    resp = client.delete(f"/event/{event.id}/register", headers=auth_headers(attendee))

    assert resp.status_code == 204
    reg = Registration.query.filter_by(user_id=attendee.id, event_id=event.id).first()
    assert reg.status == RegistrationStatus.CANCELLED


def test_cancel_never_registered_400(client, make_user, make_event, auth_headers):
    attendee = make_user()
    event = make_event()

    resp = client.delete(f"/event/{event.id}/register", headers=auth_headers(attendee))

    assert resp.status_code == 400
    assert resp.get_json()["error"] == "no_active_registration"


def test_cancel_already_cancelled_400(client, make_user, make_event, auth_headers):
    attendee = make_user()
    event = make_event()
    client.post(f"/event/{event.id}/register", headers=auth_headers(attendee))
    client.delete(f"/event/{event.id}/register", headers=auth_headers(attendee))

    resp = client.delete(f"/event/{event.id}/register", headers=auth_headers(attendee))

    assert resp.status_code == 400
    assert resp.get_json()["error"] == "no_active_registration"


def test_cancel_nonexistent_event_404(client, make_user, auth_headers):
    attendee = make_user()
    resp = client.delete("/event/999999/register", headers=auth_headers(attendee))
    assert resp.status_code == 404


def test_resignup_after_cancel_reuses_same_row(
    client, make_user, make_event, auth_headers, session
):
    attendee = make_user()
    event = make_event(spots=5)

    client.post(f"/event/{event.id}/register", headers=auth_headers(attendee))
    original = Registration.query.filter_by(
        user_id=attendee.id, event_id=event.id
    ).first()
    original_id = original.id

    client.delete(f"/event/{event.id}/register", headers=auth_headers(attendee))

    resp = client.post(f"/event/{event.id}/register", headers=auth_headers(attendee))

    assert resp.status_code == 201
    assert resp.get_json()["viewer_status"] == "confirmed"

    rows = Registration.query.filter_by(user_id=attendee.id, event_id=event.id).all()
    assert len(rows) == 1  # never a second row, the same one flipped back
    assert rows[0].id == original_id
    assert rows[0].status == RegistrationStatus.CONFIRMED


def test_resignup_after_cancel_still_blocked_if_backfilled(
    client, make_user, make_event, auth_headers
):
    """A cancelled slot could be backfilled by someone else in the
    meantime — re-signup isn't exempt from the full-event check.
    """
    event = make_event(spots=1)
    first = make_user()
    second = make_user()

    client.post(f"/event/{event.id}/register", headers=auth_headers(first))
    client.delete(f"/event/{event.id}/register", headers=auth_headers(first))
    client.post(
        f"/event/{event.id}/register", headers=auth_headers(second)
    )  # backfills

    resp = client.post(f"/event/{event.id}/register", headers=auth_headers(first))

    assert resp.status_code == 400
    assert resp.get_json()["error"] == "event_full"
