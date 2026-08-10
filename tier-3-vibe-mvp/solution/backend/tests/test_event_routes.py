import io
import json
from datetime import UTC, datetime, timedelta

from PIL import Image

from app.models import Event

FUTURE = datetime.now(UTC).replace(tzinfo=None) + timedelta(days=7)


def _valid_form(**overrides):
    form = {
        "title": "Docker Basics",
        "start": FUTURE.isoformat(),
        "end": (FUTURE + timedelta(hours=1)).isoformat(),
        "spots": "10",
        "event_type": "workshop",
        "location_type": "in_person",
    }
    form.update(overrides)
    return form


def _png_bytes():
    buf = io.BytesIO()
    Image.new("RGB", (800, 600), color="red").save(buf, format="PNG")
    buf.seek(0)
    return buf


# ---- POST /event ----------------------------------------------------------


def test_create_event_happy_path_with_image(client, make_user, auth_headers):
    admin = make_user(is_admin=True)

    resp = client.post(
        "/event",
        headers=auth_headers(admin),
        data={**_valid_form(), "image": (_png_bytes(), "cover.png")},
        content_type="multipart/form-data",
    )

    assert resp.status_code == 201
    body = resp.get_json()
    assert body["title"] == "Docker Basics"
    assert body["remaining_spots"] == 10
    assert body["image_url"].startswith("/uploads/events/")
    assert Event.query.count() == 1


def test_create_event_happy_path_without_image(client, make_user, auth_headers):
    admin = make_user(is_admin=True)

    resp = client.post("/event", headers=auth_headers(admin), data=_valid_form())

    assert resp.status_code == 201
    assert resp.get_json()["image_url"] is None


def test_create_event_non_admin_forbidden_no_row_created(
    client, make_user, auth_headers
):
    attendee = make_user(is_admin=False)

    resp = client.post("/event", headers=auth_headers(attendee), data=_valid_form())

    assert resp.status_code == 403
    assert resp.get_json()["error"] == "forbidden"
    assert Event.query.count() == 0


def test_create_event_no_token_unauthorized(client):
    resp = client.post("/event", data=_valid_form())
    assert resp.status_code == 401


def test_create_event_missing_title_rejected(client, make_user, auth_headers):
    admin = make_user(is_admin=True)
    form = _valid_form()
    del form["title"]

    resp = client.post("/event", headers=auth_headers(admin), data=form)

    assert resp.status_code == 400
    assert resp.get_json()["error"] == "validation_error"
    assert Event.query.count() == 0


def test_create_event_end_before_start_rejected(client, make_user, auth_headers):
    admin = make_user(is_admin=True)
    form = _valid_form(
        start=FUTURE.isoformat(), end=(FUTURE - timedelta(hours=1)).isoformat()
    )

    resp = client.post("/event", headers=auth_headers(admin), data=form)

    assert resp.status_code == 400
    assert resp.get_json()["error"] == "validation_error"


def test_create_event_non_positive_spots_rejected(client, make_user, auth_headers):
    admin = make_user(is_admin=True)

    resp = client.post(
        "/event", headers=auth_headers(admin), data=_valid_form(spots="0")
    )

    assert resp.status_code == 400


def test_create_event_invalid_enum_rejected(client, make_user, auth_headers):
    admin = make_user(is_admin=True)

    resp = client.post(
        "/event", headers=auth_headers(admin), data=_valid_form(event_type="not_a_type")
    )

    assert resp.status_code == 400


def test_create_event_virtual_without_url_rejected(client, make_user, auth_headers):
    admin = make_user(is_admin=True)
    form = _valid_form(
        location_type="virtual", location=json.dumps(["Room only, no link"])
    )

    resp = client.post("/event", headers=auth_headers(admin), data=form)

    assert resp.status_code == 400


def test_create_event_virtual_with_url_accepted(client, make_user, auth_headers):
    admin = make_user(is_admin=True)
    form = _valid_form(
        location_type="virtual", location=json.dumps(["https://zoom.us/j/123456"])
    )

    resp = client.post("/event", headers=auth_headers(admin), data=form)

    assert resp.status_code == 201


# ---- GET /events ------------------------------------------------------------


def test_list_events_no_token_unauthorized(client):
    resp = client.get("/events")
    assert resp.status_code == 401


def test_list_events_sorted_and_hides_attendee_data(
    client, make_user, make_event, auth_headers
):
    viewer = make_user()
    make_event(
        title="Later Event",
        start=FUTURE + timedelta(days=5),
        end=FUTURE + timedelta(days=5, hours=1),
    )
    make_event(title="Sooner Event", start=FUTURE, end=FUTURE + timedelta(hours=1))

    resp = client.get("/events", headers=auth_headers(viewer))

    assert resp.status_code == 200
    titles = [e["title"] for e in resp.get_json()]
    assert titles == ["Sooner Event", "Later Event"]
    for event in resp.get_json():
        assert "attendees" not in event
        assert "email" not in event


def test_list_events_excludes_past_events(client, make_user, make_event, auth_headers):
    viewer = make_user()
    past = datetime.now(UTC).replace(tzinfo=None) - timedelta(days=1)
    make_event(title="Past Event", start=past - timedelta(hours=1), end=past)
    make_event(title="Future Event", start=FUTURE, end=FUTURE + timedelta(hours=1))

    resp = client.get("/events", headers=auth_headers(viewer))

    titles = [e["title"] for e in resp.get_json()]
    assert titles == ["Future Event"]


def test_list_events_remaining_spots_and_viewer_status(
    client, make_user, make_event, auth_headers, session
):
    from app.models import Registration
    from app.models.enums import RegistrationStatus

    viewer = make_user()
    event = make_event(spots=5)
    session.add(
        Registration(
            user_id=viewer.id,
            event_id=event.id,
            status=RegistrationStatus.CONFIRMED,
            sign_up_at=datetime.now(UTC).replace(tzinfo=None),
        )
    )
    session.commit()

    resp = client.get("/events", headers=auth_headers(viewer))

    body = resp.get_json()[0]
    assert body["remaining_spots"] == 4
    assert body["viewer_status"] == "confirmed"


# ---- GET /event/:id/details ---------------------------------------------


def test_event_details_happy_path(client, make_user, make_event, auth_headers):
    viewer = make_user()
    event = make_event()

    resp = client.get(f"/event/{event.id}/details", headers=auth_headers(viewer))

    assert resp.status_code == 200
    assert resp.get_json()["id"] == event.id


def test_event_details_bad_id(client, make_user, auth_headers):
    viewer = make_user()

    resp = client.get("/event/not-a-number/details", headers=auth_headers(viewer))

    assert resp.status_code == 400
    assert resp.get_json()["error"] == "bad_request"


def test_event_details_not_found(client, make_user, auth_headers):
    viewer = make_user()

    resp = client.get("/event/999999/details", headers=auth_headers(viewer))

    assert resp.status_code == 404


def test_event_details_no_token(client, make_event):
    event = make_event()
    resp = client.get(f"/event/{event.id}/details")
    assert resp.status_code == 401
