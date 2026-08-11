from datetime import timedelta

from flask_jwt_extended import create_access_token


def _envelope_shape(body):
    return set(body.keys()) == {"error", "message", "details"}


def test_unmatched_route_404_envelope(client):
    resp = client.get("/this-route-does-not-exist")

    assert resp.status_code == 404
    body = resp.get_json()
    assert _envelope_shape(body)
    assert body["error"] == "not_found"


def test_wrong_method_405_envelope(client, make_event):
    event = make_event()

    # /event/<id>/details only supports GET
    resp = client.post(f"/event/{event.id}/details")

    assert resp.status_code == 405
    body = resp.get_json()
    assert _envelope_shape(body)
    assert body["error"] == "method_not_allowed"


def test_missing_token_401_envelope(client):
    resp = client.get("/events")

    assert resp.status_code == 401
    body = resp.get_json()
    assert _envelope_shape(body)
    assert body["error"] == "missing_token"


def test_garbled_token_401_envelope(client):
    resp = client.get("/events", headers={"Authorization": "Bearer not-a-real-jwt"})

    assert resp.status_code == 401
    body = resp.get_json()
    assert _envelope_shape(body)
    assert body["error"] == "invalid_token"


def test_expired_token_401_envelope(client, app, make_user):
    user = make_user()
    with app.app_context():
        expired_token = create_access_token(
            identity=str(user.id),
            additional_claims={"email": user.email, "is_admin": user.is_admin},
            expires_delta=timedelta(seconds=-1),
        )

    resp = client.get("/events", headers={"Authorization": f"Bearer {expired_token}"})

    assert resp.status_code == 401
    body = resp.get_json()
    assert _envelope_shape(body)
    assert body["error"] == "token_expired"


def test_api_error_and_library_error_share_same_shape(client, make_user, auth_headers):
    """An app-raised 401 (e.g. a bad login) and a library-raised 401 (a
    garbled token) must be indistinguishable in shape to a client.
    """
    app_raised = client.post("/login", json={"email": "nobody@company.com"})
    library_raised = client.get("/events", headers={"Authorization": "Bearer garbage"})

    assert app_raised.status_code == library_raised.status_code == 401
    assert set(app_raised.get_json().keys()) == set(library_raised.get_json().keys())
