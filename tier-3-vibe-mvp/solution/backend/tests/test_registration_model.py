from datetime import datetime

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.models import Event, Registration, User
from app.models.enums import RegistrationStatus


def _make_user_and_event(session):
    user = User(first_name="Ada", last_name="Lovelace", email="ada@company.com")
    event = Event(
        title="Test Event",
        start=datetime(2026, 9, 1, 10, 0),
        end=datetime(2026, 9, 1, 11, 0),
        spots=2,
        event_type="workshop",
        location_type="in_person",
    )
    session.add_all([user, event])
    session.commit()
    return user, event


def test_status_enum_rejects_invalid_value(session):
    """status is a db.Enum(..., create_constraint=True) column, so an
    invalid value is rejected by a real DB CHECK — raised as IntegrityError
    at commit, not merely a Python-side type-validation error.
    """
    user, event = _make_user_and_event(session)
    reg = Registration(
        user_id=user.id,
        event_id=event.id,
        status="not_a_real_status",
        sign_up_at=datetime(2026, 8, 8, 9, 0),
    )
    session.add(reg)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_status_check_constraint_enforced_at_db_layer(session):
    """Insert raw SQL directly, bypassing the ORM's Enum type entirely, to
    prove the CHECK constraint itself enforces this — not just something
    SQLAlchemy's Python-side column type happens to catch.
    """
    user, event = _make_user_and_event(session)
    with pytest.raises(IntegrityError):
        session.execute(
            text(
                "INSERT INTO users_events "
                "(user_id, event_id, status, sign_up_at, created_at, updated_at) "
                "VALUES (:user_id, :event_id, 'Bogus', '2026-08-08 09:00:00', "
                "'2026-08-08 09:00:00', '2026-08-08 09:00:00')"
            ),
            {"user_id": user.id, "event_id": event.id},
        )
        session.commit()
    session.rollback()


def test_unique_user_event_constraint(session):
    user, event = _make_user_and_event(session)
    session.add(
        Registration(
            user_id=user.id,
            event_id=event.id,
            status=RegistrationStatus.CONFIRMED.value,
            sign_up_at=datetime(2026, 8, 8, 9, 0),
        )
    )
    session.commit()

    session.add(
        Registration(
            user_id=user.id,
            event_id=event.id,
            status=RegistrationStatus.CONFIRMED.value,
            sign_up_at=datetime(2026, 8, 9, 9, 0),
        )
    )
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_foreign_key_enforcement_rejects_orphan_ids(session):
    """Proves the PRAGMA foreign_keys=ON connect listener (app/extensions.py)
    is actually wired up — SQLite silently ignores FK violations by default
    per-connection unless that pragma is set.
    """
    session.add(
        Registration(
            user_id=999_999,
            event_id=999_999,
            status=RegistrationStatus.CONFIRMED.value,
            sign_up_at=datetime(2026, 8, 8, 9, 0),
        )
    )
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_computed_remaining_spots_via_relationship(session):
    user, event = _make_user_and_event(session)  # event.spots == 2
    other_user = User(first_name="Grace", last_name="Hopper", email="grace@company.com")
    session.add(other_user)
    session.commit()

    session.add_all(
        [
            Registration(
                user_id=user.id,
                event_id=event.id,
                status=RegistrationStatus.CONFIRMED.value,
                sign_up_at=datetime(2026, 8, 8, 9, 0),
            ),
            Registration(
                user_id=other_user.id,
                event_id=event.id,
                status=RegistrationStatus.CANCELLED.value,
                sign_up_at=datetime(2026, 8, 7, 9, 0),
            ),
        ]
    )
    session.commit()

    confirmed = event.registrations.filter_by(
        status=RegistrationStatus.CONFIRMED.value
    ).count()
    remaining = event.spots - confirmed

    assert confirmed == 1
    assert remaining == 1  # 1 Confirmed + 1 Cancelled out of 2 spots -> 1 left
