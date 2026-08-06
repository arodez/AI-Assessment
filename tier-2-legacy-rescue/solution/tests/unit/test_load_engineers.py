"""Unit tests for `load_engineers`.

Covers the CSV-loading concerns documented in ../../BUGS.md: header-name
parsing regardless of column order (#5), an optional `deadline` (#4),
skip accounting for rows that are genuinely malformed (#7, #9), and the
mutable-default-argument state leak the original implementation had (#3).

Required vs. optional fields, as loaded: `name`, `email`, `team`, and
`status` must all be present and non-blank or the row is skipped and
counted; `deadline` is the one field allowed to be blank (self-paced /
optional courses), in which case the engineer simply has no deadline to
be evaluated as overdue against.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import date
from pathlib import Path

import pytest

from report_generator_fixed import Engineer, LoadResult, load_engineers


def test_loads_well_formed_rows(write_csv: Callable[..., Path]) -> None:
    path = write_csv(
        [
            ("Ana Torres", "ana@example.com", "Platform", "completed", "2026-06-30"),
            ("Luis Mendoza", "luis@example.com", "Platform", "pending", "2026-06-15"),
            ("Sofia Reyes", "sofia@example.com", "Data", "in_progress", "2026-08-01"),
        ]
    )

    result = load_engineers(path)

    assert result == LoadResult(
        engineers=[
            Engineer("Ana Torres", "ana@example.com", "Platform", "completed", date(2026, 6, 30)),
            Engineer("Luis Mendoza", "luis@example.com", "Platform", "pending", date(2026, 6, 15)),
            Engineer("Sofia Reyes", "sofia@example.com", "Data", "in_progress", date(2026, 8, 1)),
        ],
        skipped=0,
    )


def test_reads_columns_by_header_name_not_position(write_csv: Callable[..., Path]) -> None:
    """A reordered CSV must still parse correctly (BUGS.md #5)."""
    path = write_csv(
        header=("email", "name", "deadline", "course_status", "team"),
        rows=[("diego@example.com", "Diego Fuentes", "2026-06-20", "pending", "Data")],
    )

    [engineer] = load_engineers(path).engineers

    assert engineer == Engineer(
        "Diego Fuentes", "diego@example.com", "Data", "pending", date(2026, 6, 20)
    )


def test_normalizes_status_case_and_whitespace_at_load_time(write_csv: Callable[..., Path]) -> None:
    path = write_csv(
        [
            ("Diego Fuentes", "diego@example.com", "Data", "Pending", "2026-06-20"),
            ("Valeria Nunez", "valeria@example.com", "Platform", "in_progress ", "2026-07-10"),
        ]
    )

    statuses = [e.status for e in load_engineers(path).engineers]

    assert statuses == ["pending", "in_progress"]


def test_blank_deadline_is_kept_as_none_and_not_skipped(write_csv: Callable[..., Path]) -> None:
    """A missing deadline is valid input, not a parse failure (BUGS.md #4)."""
    path = write_csv([("Renata Vega", "renata@example.com", "Mobile", "pending", "")])

    result = load_engineers(path)

    assert result.skipped == 0
    [engineer] = result.engineers
    assert engineer.deadline is None


def test_unknown_status_is_kept_as_is_not_skipped(write_csv: Callable[..., Path]) -> None:
    """Unrecognized statuses are `count_by_status`'s concern (BUGS.md #9), not loading's."""
    path = write_csv([("Casey Lee", "casey@example.com", "Data", "blocked", "2026-07-01")])

    result = load_engineers(path)

    assert result.skipped == 0
    assert result.engineers[0].status == "blocked"


@pytest.mark.parametrize(
    ("rows", "reason"),
    [
        pytest.param(
            [("Renata Vega", "renata@example.com", "Mobile")],
            "short row (missing status and deadline columns entirely)",
        ),
        pytest.param(
            [("Casey Lee", "casey@example.com", "Data", "", "2026-07-01")],
            "blank status (required field)",
        ),
        pytest.param(
            [("Casey Lee", "casey@example.com", "Data", "pending", "not-a-date")],
            "unparsable deadline",
        ),
        pytest.param([()], "fully blank row, e.g. a stray trailing newline in the export"),
    ],
)
def test_malformed_rows_are_skipped_and_counted(
    write_csv: Callable[..., Path], rows: list[tuple[str, ...]], reason: str
) -> None:
    path = write_csv(rows)

    result = load_engineers(path)

    assert result.engineers == [], reason
    assert result.skipped == 1, reason


def test_repeated_calls_do_not_leak_state_across_each_other(write_csv: Callable[..., Path]) -> None:
    """Regression test for the mutable-default-argument bug (BUGS.md #3).

    The original's `append_row(row, rows=[])` reused the same list across
    every call for the lifetime of the process; two calls to
    `load_engineers` on the same file must each return an independent,
    correctly-sized result.
    """
    path = write_csv([("Ana Torres", "ana@example.com", "Platform", "completed", "2026-06-30")])

    first = load_engineers(path)
    second = load_engineers(path)

    assert first.engineers is not second.engineers
    assert len(first.engineers) == len(second.engineers) == 1


def test_missing_file_raises_file_not_found(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_engineers(tmp_path / "does-not-exist.csv")


def test_completely_empty_file_yields_no_engineers_and_no_skips(tmp_path: Path) -> None:
    """A file with no header row at all (0 bytes) is empty input, not malformed input."""
    path = tmp_path / "empty.csv"
    path.write_text("", encoding="utf-8")

    result = load_engineers(path)

    assert result == LoadResult(engineers=[], skipped=0)
