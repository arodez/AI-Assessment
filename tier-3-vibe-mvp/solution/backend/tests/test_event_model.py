from datetime import datetime

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.models import Event

VALID_KWARGS = dict(
    title="Test Event",
    start=datetime(2026, 9, 1, 10, 0),
    end=datetime(2026, 9, 1, 11, 0),
    spots=10,
    event_type="workshop",
    location_type="in_person",
)


@pytest.mark.parametrize("bad_spots", [0, -1])
def test_spots_must_be_positive(session, bad_spots):
    """spots > 0 is a DB CHECK — a plain Integer column, so this reaches
    the DB and raises IntegrityError, not a Python-side validation error.
    """
    kwargs = {**VALID_KWARGS, "spots": bad_spots}
    session.add(Event(**kwargs))
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_end_must_be_after_start(session):
    kwargs = {
        **VALID_KWARGS,
        "start": datetime(2026, 9, 1, 11, 0),
        "end": datetime(2026, 9, 1, 10, 0),
    }
    session.add(Event(**kwargs))
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_event_type_enum_rejects_invalid_value(session):
    """event_type is a db.Enum(..., create_constraint=True) column, so an
    invalid value is rejected by a real DB CHECK — raised as IntegrityError
    at commit. (Found the hard way: without create_constraint=True, this
    silently inserts and only fails later, confusingly, on read-back — see
    the comment in app/models/enums.py.)
    """
    kwargs = {**VALID_KWARGS, "event_type": "not_a_real_type"}
    session.add(Event(**kwargs))
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_location_type_enum_rejects_invalid_value(session):
    kwargs = {**VALID_KWARGS, "location_type": "not_a_real_location_type"}
    session.add(Event(**kwargs))
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_event_type_check_constraint_enforced_at_db_layer(session):
    """Insert raw SQL directly, bypassing the ORM's Enum type entirely, to
    prove the CHECK constraint itself enforces this — not just something
    SQLAlchemy's Python-side column type happens to catch.
    """
    with pytest.raises(IntegrityError):
        session.execute(
            text(
                "INSERT INTO events "
                '(title, start, "end", spots, event_type, location_type, '
                "created_at, updated_at) "
                "VALUES ('Bad', '2026-09-01 10:00:00', '2026-09-01 11:00:00', 5, "
                "'bogus_type', 'in_person', '2026-08-07 00:00:00', "
                "'2026-08-07 00:00:00')"
            )
        )
        session.commit()
    session.rollback()


def test_location_json_roundtrip(session):
    kwargs = {
        **VALID_KWARGS,
        "location": ["Room 12, The Studio", "https://zoom.us/j/1234567890"],
    }
    event = Event(**kwargs)
    session.add(event)
    session.commit()
    event_id = event.id  # capture before expunge — id is expired post-commit
    # (expire_on_commit=True) and can't lazy-reload once detached below.
    session.expunge_all()

    reloaded = session.get(Event, event_id)
    assert reloaded.location == ["Room 12, The Studio", "https://zoom.us/j/1234567890"]
