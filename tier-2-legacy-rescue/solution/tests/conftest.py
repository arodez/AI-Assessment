"""Shared pytest fixtures for the report_generator_fixed test suite.

Fixtures build minimal, targeted input (a CSV file, an `Engineer` record)
rather than relying on one large shared fixture file, so each test can
construct exactly the input it needs to demonstrate one behavior. The one
exception is `sample_csv_path`, used by integration tests that exercise the
real shipped sample data end to end.
"""

from __future__ import annotations

import csv
from collections.abc import Callable, Iterable, Sequence
from datetime import date
from pathlib import Path

import pytest

from report_generator_fixed import Engineer

# Matches the production schema documented in ../data/sample_input.csv.
# Column order here is irrelevant to the fixed implementation (it reads by
# header name, not position — see bug #5 in ../BUGS.md); `write_csv` still
# needs *a* default so most tests don't have to spell it out every time.
_CSV_HEADER: tuple[str, ...] = ("name", "email", "team", "course_status", "deadline")


@pytest.fixture
def write_csv(tmp_path: Path) -> Callable[..., Path]:
    """Return a factory that writes `rows` (+ `header`) to a CSV under `tmp_path`."""

    def _write(
        rows: Iterable[Sequence[str]],
        *,
        header: Sequence[str] = _CSV_HEADER,
        filename: str = "input.csv",
    ) -> Path:
        path = tmp_path / filename
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(header)
            writer.writerows(rows)
        return path

    return _write


@pytest.fixture
def make_engineer() -> Callable[..., Engineer]:
    """Return a factory for `Engineer` records with sensible, overridable defaults."""

    def _make(
        name: str = "Test Engineer",
        email: str = "test.engineer@example.com",
        team: str = "Platform",
        status: str = "completed",
        deadline: date | None = None,
    ) -> Engineer:
        return Engineer(name=name, email=email, team=team, status=status, deadline=deadline)

    return _make


@pytest.fixture
def reference_today() -> date:
    """The date the original script hardcoded as its overdue reference point.

    Reused so tests that pin `today` explicitly stay comparable to the
    scenarios documented in ../BUGS.md (bug #6 covers the default-clock fix).
    """
    return date(2026, 7, 14)


@pytest.fixture
def sample_csv_path() -> Path:
    """Path to the real sample input fixture shipped with the repo."""
    path = Path(__file__).resolve().parents[2] / "data" / "sample_input.csv"
    assert path.exists(), f"expected sample input at {path}"
    return path
