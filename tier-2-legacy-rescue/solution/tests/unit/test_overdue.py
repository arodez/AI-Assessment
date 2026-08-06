"""Unit tests for `overdue`.

Covers date-based comparison replacing the original's lexicographic string
comparison (BUGS.md #1), a `None` deadline never being overdue (BUGS.md
#4), and `today` defaulting to the real clock instead of a frozen literal
(BUGS.md #6).

Preserved on purpose: `overdue` keeps the original's permissive "anything
that isn't 'completed'" rule rather than restricting itself to the known
`pending` / `in_progress` statuses. ANALYSIS.md flagged that this makes
`overdue` and `count_by_status` disagree on what counts as a valid status
(an engineer with a typo'd status is "uncounted" by one and can still be
"overdue" per the other) — noted as a known inconsistency, not something
these tests correct.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import date, timedelta

from report_generator_fixed import Engineer, overdue


def test_completed_engineer_is_never_overdue(
    make_engineer: Callable[..., Engineer], reference_today: date
) -> None:
    engineer = make_engineer(status="completed", deadline=date(2020, 1, 1))

    assert overdue([engineer], today=reference_today) == []


def test_pending_engineer_past_deadline_is_overdue(
    make_engineer: Callable[..., Engineer], reference_today: date
) -> None:
    engineer = make_engineer(email="late@example.com", status="pending", deadline=date(2026, 5, 30))

    assert overdue([engineer], today=reference_today) == ["late@example.com"]


def test_in_progress_engineer_past_deadline_is_overdue(
    make_engineer: Callable[..., Engineer], reference_today: date
) -> None:
    engineer = make_engineer(
        email="late@example.com", status="in_progress", deadline=date(2026, 5, 30)
    )

    assert overdue([engineer], today=reference_today) == ["late@example.com"]


def test_deadline_equal_to_today_is_not_yet_overdue(
    make_engineer: Callable[..., Engineer], reference_today: date
) -> None:
    engineer = make_engineer(status="pending", deadline=reference_today)

    assert overdue([engineer], today=reference_today) == []


def test_future_deadline_is_not_overdue(
    make_engineer: Callable[..., Engineer], reference_today: date
) -> None:
    engineer = make_engineer(status="pending", deadline=reference_today + timedelta(days=1))

    assert overdue([engineer], today=reference_today) == []


def test_no_deadline_is_never_overdue(
    make_engineer: Callable[..., Engineer], reference_today: date
) -> None:
    engineer = make_engineer(status="pending", deadline=None)

    assert overdue([engineer], today=reference_today) == []


def test_unrecognized_status_is_still_overdue_eligible(
    make_engineer: Callable[..., Engineer], reference_today: date
) -> None:
    """Matches the original's permissive rule: anything that isn't 'completed' can be overdue."""
    engineer = make_engineer(email="typo@example.com", status="blocked", deadline=date(2020, 1, 1))

    assert overdue([engineer], today=reference_today) == ["typo@example.com"]


def test_preserves_input_order(
    make_engineer: Callable[..., Engineer], reference_today: date
) -> None:
    first = make_engineer(email="first@example.com", status="pending", deadline=date(2020, 1, 1))
    second = make_engineer(email="second@example.com", status="pending", deadline=date(2020, 1, 2))

    assert overdue([first, second], today=reference_today) == [
        "first@example.com",
        "second@example.com",
    ]


def test_defaults_to_the_real_current_date_when_today_is_not_supplied(
    make_engineer: Callable[..., Engineer],
) -> None:
    long_overdue = make_engineer(
        email="long.overdue@example.com", status="pending", deadline=date(2000, 1, 1)
    )
    far_future = make_engineer(
        email="far.future@example.com", status="pending", deadline=date(2999, 1, 1)
    )

    result = overdue([long_overdue, far_future])

    assert result == ["long.overdue@example.com"]
