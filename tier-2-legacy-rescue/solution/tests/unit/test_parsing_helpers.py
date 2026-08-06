"""Unit tests for the parsing/normalization helpers.

`normalize_status` and `parse_deadline` isolate the two data-cleaning
concerns the original script got wrong — case/whitespace-sensitive status
matching (BUGS.md #2) and string-based date comparison (BUGS.md #1) — so
they're tested independently of CSV loading.
"""

from __future__ import annotations

from datetime import date

import pytest

from report_generator_fixed import normalize_status, parse_deadline


class TestNormalizeStatus:
    """`normalize_status` strips whitespace and lowercases, nothing more."""

    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            ("pending", "pending"),
            ("Pending", "pending"),
            ("PENDING", "pending"),
            ("in_progress", "in_progress"),
            ("in_progress ", "in_progress"),
            ("  completed  ", "completed"),
        ],
    )
    def test_normalizes_case_and_whitespace(self, raw: str, expected: str) -> None:
        assert normalize_status(raw) == expected

    def test_does_not_validate_against_known_statuses(self) -> None:
        """Normalization is purely cosmetic; bucketing unknowns is `count_by_status`'s job."""
        assert normalize_status(" Blocked ") == "blocked"


class TestParseDeadline:
    """`parse_deadline` accepts zero-padded and non-padded ISO-ish dates."""

    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            ("2026-06-15", date(2026, 6, 15)),
            ("2026-5-30", date(2026, 5, 30)),  # non-padded month (BUGS.md #1)
            ("2026-5-3", date(2026, 5, 3)),  # non-padded month and day
        ],
    )
    def test_parses_padded_and_non_padded_dates(self, raw: str, expected: date) -> None:
        assert parse_deadline(raw) == expected

    @pytest.mark.parametrize("raw", ["", "   "])
    def test_blank_deadline_is_none(self, raw: str) -> None:
        """A blank deadline is valid input (optional/self-paced courses), not an error."""
        assert parse_deadline(raw) is None

    @pytest.mark.parametrize("raw", ["not-a-date", "2026-13-40", "06/15/2026"])
    def test_malformed_deadline_raises(self, raw: str) -> None:
        with pytest.raises(ValueError):
            parse_deadline(raw)
