from app.models import User


def test_login_success_returns_token_and_user(client, make_user):
    user = make_user(email="alice.kim@company.com", first_name="Alice", is_admin=True)

    resp = client.post("/login", json={"email": user.email})

    assert resp.status_code == 200
    body = resp.get_json()
    assert body["access_token"]
    assert body["user"] == {"id": user.id, "first_name": "Alice", "is_admin": True}


def test_login_is_case_insensitive(client, make_user):
    make_user(email="alice.kim@company.com")

    resp = client.post("/login", json={"email": "ALICE.KIM@COMPANY.COM"})

    assert resp.status_code == 200


def test_login_malformed_email_rejected_before_db_lookup(client, session):
    for bad in ["not-an-email", "", " alice.kim@company.com", "alice.kim@company.com "]:
        resp = client.post("/login", json={"email": bad})
        assert resp.status_code == 400, bad
        assert resp.get_json()["error"] == "validation_error"

    # No account should exist for any of these — login never creates users.
    assert User.query.count() == 0


def test_login_unrecognized_email_rejected_no_account_created(client, session):
    resp = client.post("/login", json={"email": "nobody@company.com"})

    assert resp.status_code == 401
    assert resp.get_json()["error"] == "unauthorized"
    assert User.query.count() == 0
