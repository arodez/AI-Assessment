import time

import pytest
from sqlalchemy.exc import IntegrityError

from app.models import User


def test_timestamps_set_on_insert(session):
    user = User(first_name="Ada", last_name="Lovelace", email="ada@company.com")
    session.add(user)
    session.commit()

    assert user.created_at is not None
    assert user.updated_at is not None
    # created_at/updated_at share one TimestampMixin default (_utcnow), but
    # SQLAlchemy invokes each column's default callable separately at
    # flush, so they can differ by a handful of microseconds — assert
    # "practically simultaneous", not bit-for-bit equal.
    assert abs((user.updated_at - user.created_at).total_seconds()) < 1


def test_updated_at_refreshes_on_update(session):
    user = User(first_name="Ada", last_name="Lovelace", email="ada@company.com")
    session.add(user)
    session.commit()
    original_updated_at = user.updated_at

    # SQLite datetime() has second-level granularity in practice for this
    # test's purposes; sleep briefly so the refreshed timestamp is
    # unambiguously later, not just equal-by-coincidence.
    time.sleep(1.1)
    user.last_name = "King"
    session.commit()

    assert user.updated_at > original_updated_at
    assert user.created_at < user.updated_at


def test_email_uniqueness_raises_integrity_error(session):
    session.add(User(first_name="Ada", last_name="Lovelace", email="ada@company.com"))
    session.commit()

    session.add(User(first_name="Someone", last_name="Else", email="ada@company.com"))
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()
