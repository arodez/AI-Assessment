"""Unit tests for `count_by_status`.

Exercises engineer records directly via the `make_engineer` fixture rather
than going through `load_engineers`, so these tests hold regardless of how
status normalization happens upstream. Covers happy-path tallying and the
`unknown` bucket for unrecognized status values (BUGS.md #9), which
replaces the original's silent drop of anything outside the three known
statuses.
"""

from __future__ import annotations

from collections.abc import Callable

from report_generator_fixed import Engineer, count_by_status


def test_tallies_known_statuses(make_engineer: Callable[..., Engineer]) -> None:
    engineers = [
        make_engineer(status="completed"),
        make_engineer(status="completed"),
        make_engineer(status="pending"),
        make_engineer(status="in_progress"),
    ]

    assert count_by_status(engineers) == {"completed": 2, "pending": 1, "in_progress": 1}


def test_omits_statuses_with_zero_engineers(make_engineer: Callable[..., Engineer]) -> None:
    """Only statuses actually present get a line — matches the original's report format."""
    engineers = [make_engineer(status="completed")]

    counts = count_by_status(engineers)

    assert counts == {"completed": 1}
    assert "pending" not in counts
    assert "in_progress" not in counts


def test_normalizes_case_and_whitespace_independently_of_the_caller(
    make_engineer: Callable[..., Engineer],
) -> None:
    """Defends against un-normalized input, regardless of what `load_engineers` already did."""
    engineers = [make_engineer(status="Pending"), make_engineer(status="  in_progress ")]

    assert count_by_status(engineers) == {"pending": 1, "in_progress": 1}


def test_unrecognized_statuses_are_grouped_under_unknown(
    make_engineer: Callable[..., Engineer],
) -> None:
    engineers = [
        make_engineer(status="completed"),
        make_engineer(status="blocked"),
        make_engineer(status="not_started"),
    ]

    assert count_by_status(engineers) == {"completed": 1, "unknown": 2}


def test_empty_input_yields_empty_counts() -> None:
    assert count_by_status([]) == {}
