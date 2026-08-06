"""Unit tests for `build_report`, pinning the exact text format.

Design decision made explicit by these tests: status lines are always
emitted in a fixed canonical order — `completed`, `pending`, `in_progress`,
`unknown` — each only when its count is greater than zero. The original
relied on plain dict-insertion order, so the line order in its report
actually depended on which status happened to appear first in the CSV,
which isn't a behavior worth preserving; a compliance report should read
the same way regardless of input row order.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import date

from report_generator_fixed import Engineer, build_report


def test_full_report_matches_expected_format(
    make_engineer: Callable[..., Engineer], reference_today: date
) -> None:
    engineers = [
        make_engineer(email="a@example.com", status="completed"),
        make_engineer(email="b@example.com", status="completed"),
        make_engineer(email="c@example.com", status="pending", deadline=date(2026, 5, 30)),
        make_engineer(email="d@example.com", status="in_progress"),
        make_engineer(email="e@example.com", status="blocked"),
    ]

    report = build_report(engineers, skipped=2, today=reference_today)

    assert report == (
        "WEEKLY TRAINING COMPLIANCE REPORT\n"
        "completed: 2\n"
        "pending: 1\n"
        "in_progress: 1\n"
        "unknown: 1\n"
        "skipped rows: 2\n"
        "overdue engineers:\n"
        "  - c@example.com\n"
    )


def test_omits_status_lines_with_zero_count(
    make_engineer: Callable[..., Engineer], reference_today: date
) -> None:
    engineers = [make_engineer(status="completed")]

    report = build_report(engineers, skipped=0, today=reference_today)

    assert report == (
        "WEEKLY TRAINING COMPLIANCE REPORT\n"
        "completed: 1\n"
        "skipped rows: 0\n"
        "overdue engineers:\n"
    )


def test_overdue_header_is_present_even_with_no_overdue_engineers(
    make_engineer: Callable[..., Engineer], reference_today: date
) -> None:
    engineers = [make_engineer(status="completed")]

    report = build_report(engineers, skipped=0, today=reference_today)

    assert report.endswith("overdue engineers:\n")


def test_empty_engineer_list_still_produces_a_well_formed_report(reference_today: date) -> None:
    report = build_report([], skipped=0, today=reference_today)

    assert report == "WEEKLY TRAINING COMPLIANCE REPORT\nskipped rows: 0\noverdue engineers:\n"


def test_lists_multiple_overdue_engineers_in_input_order(
    make_engineer: Callable[..., Engineer], reference_today: date
) -> None:
    engineers = [
        make_engineer(email="first@example.com", status="pending", deadline=date(2020, 1, 1)),
        make_engineer(email="second@example.com", status="in_progress", deadline=date(2020, 1, 2)),
    ]

    report = build_report(engineers, skipped=0, today=reference_today)

    assert "  - first@example.com\n  - second@example.com\n" in report
