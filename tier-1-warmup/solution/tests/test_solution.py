"""Tests for solution.py.

Run with: poetry run pytest -v (from the solution/ directory).

Fixture CSVs live in tests/fixtures/ and each isolates one behavior
(happy path, or a specific edge case). See GUIDE.md for the full table of
what each fixture covers.
"""

from __future__ import annotations

import glob
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import solution  # noqa: E402

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
REPO_ENGINEERS_CSV = Path(__file__).resolve().parents[2] / "data" / "engineers.csv"


def load(fixture_name: str) -> tuple[int, Counter, list[str]]:
    """Read a fixture CSV through the full parse+process pipeline."""
    raw_rows = solution.read_raw_rows(str(FIXTURES_DIR / fixture_name))
    return solution.process_rows(raw_rows)


# --- Unit tests on pure helpers -------------------------------------------


@pytest.mark.parametrize(
    "raw_status,expected",
    [
        ("pending", "pending"),
        ("Pending", "pending"),
        ("  Pending  ", "pending"),
        ("PENDING", "pending"),
        ("completed", "completed"),
        ("", "unknown"),
        ("   ", "unknown"),
    ],
)
def test_normalize_status(raw_status, expected):
    assert solution.normalize_status(raw_status) == expected


@pytest.mark.parametrize(
    "raw_status,expected",
    [
        ("pending", True),
        (" Pending ", True),
        ("PENDING", True),
        ("completed", False),
        ("", False),
    ],
)
def test_is_pending(raw_status, expected):
    assert solution.is_pending(raw_status) == expected


@pytest.mark.parametrize(
    "row,expected",
    [
        ({"name": "", "email": "", "course_status": ""}, True),
        ({"name": "Ana", "email": "", "course_status": ""}, False),
        ({"name": "", "email": "a@example.com", "course_status": ""}, False),
        ({"name": "", "email": "", "course_status": "pending"}, False),
    ],
)
def test_is_blank_row(row, expected):
    assert solution.is_blank_row(row) == expected


def test_generate_timestamp_format_and_no_colons():
    ts = solution.generate_timestamp(datetime(2026, 8, 4, 14, 5, 30))
    assert ts == "2026-08-04T14-05-30"
    assert ":" not in ts


def test_pending_filename():
    assert solution.pending_filename("2026-08-04T14-05-30") == (
        "pending-2026-08-04T14-05-30.txt"
    )


def test_write_pending_file(tmp_path):
    out = tmp_path / "pending-test.txt"
    solution.write_pending_file(out, ["a@example.com", "b@example.com"])
    assert out.read_text(encoding="utf-8") == "a@example.com\nb@example.com\n"


def test_write_pending_file_empty_list(tmp_path):
    out = tmp_path / "pending-empty.txt"
    solution.write_pending_file(out, [])
    assert out.read_text(encoding="utf-8") == ""


def test_format_status_lines_sorted_alphabetically():
    counts = Counter({"pending": 3, "completed": 1, "unknown": 2})
    lines = solution.format_status_lines(counts)
    assert lines == [
        "1 engineers in completed status",
        "3 engineers in pending status",
        "2 engineers in unknown status",
    ]


# --- Fixture-driven tests on process_rows ----------------------------------


def test_happy_path():
    total, counts, pending = load("happy_path.csv")
    assert total == 3
    assert counts == Counter({"completed": 1, "pending": 1, "in_progress": 1})
    assert pending == ["luis.mendoza@example.com"]


def test_header_only():
    total, counts, pending = load("header_only.csv")
    assert total == 0
    assert counts == Counter()
    assert pending == []


def test_blank_lines_excluded():
    total, counts, pending = load("blank_lines.csv")
    assert total == 3
    assert counts == Counter({"completed": 1, "pending": 1, "in_progress": 1})


def test_missing_course_status_column():
    total, counts, pending = load("missing_course_status_column.csv")
    assert total == 2
    assert counts == Counter({"unknown": 1, "completed": 1})


def test_blank_course_status():
    total, counts, pending = load("blank_course_status.csv")
    assert total == 2
    assert counts == Counter({"unknown": 1, "completed": 1})


def test_missing_name_still_counted():
    total, counts, pending = load("missing_name.csv")
    assert total == 2
    assert counts == Counter({"pending": 1, "completed": 1})
    assert pending == ["ghost@example.com"]


def test_missing_email_excluded_from_pending_file_but_counted():
    total, counts, pending = load("missing_email.csv")
    assert total == 2
    assert counts == Counter({"pending": 2})
    assert pending == ["luis.mendoza@example.com"]


def test_mixed_case_whitespace_status_normalizes_to_one_group():
    total, counts, pending = load("mixed_case_whitespace_status.csv")
    assert total == 3
    assert counts == Counter({"pending": 3})
    assert pending == [
        "luis.mendoza@example.com",
        "diego.fuentes@example.com",
        "jorge.salinas@example.com",
    ]


def test_duplicate_rows_not_deduplicated():
    total, counts, pending = load("duplicate_rows.csv")
    assert total == 2
    assert counts == Counter({"pending": 2})
    assert pending == ["luis.mendoza@example.com", "luis.mendoza@example.com"]


def test_extra_columns_ignored():
    total, counts, pending = load("extra_columns.csv")
    assert total == 2
    assert counts == Counter({"completed": 1, "pending": 1})
    assert pending == ["luis.mendoza@example.com"]


def test_comma_only_row_excluded():
    total, counts, pending = load("comma_only_row.csv")
    assert total == 2
    assert counts == Counter({"completed": 1, "pending": 1})


# --- End-to-end tests --------------------------------------------------


def test_main_end_to_end(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    fixture = FIXTURES_DIR / "happy_path.csv"

    exit_code = solution.main([str(fixture)])

    assert exit_code == 0
    out = capsys.readouterr().out
    assert "Processed total engineers: 3" in out
    assert "1 engineers in completed status" in out
    assert "1 engineers in in_progress status" in out
    assert "1 engineers in pending status" in out
    assert "Pending results generated in pending-" in out

    generated = glob.glob(str(tmp_path / "pending-*.txt"))
    assert len(generated) == 1
    assert Path(generated[0]).read_text(encoding="utf-8") == "luis.mendoza@example.com\n"


def test_main_missing_file_returns_error(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    missing = tmp_path / "does-not-exist.csv"

    exit_code = solution.main([str(missing)])

    assert exit_code == 1
    err = capsys.readouterr().err
    assert "does not exist" in err


def test_main_regression_against_real_sample_data(tmp_path, monkeypatch, capsys):
    """Regression check against the repo's real data/engineers.csv.

    Expected numbers (10 data rows total): 3 pending, 3 completed,
    2 in_progress, 2 unknown (Marco Rivera - blank status; Isabel Vargas -
    missing course_status column).
    """
    monkeypatch.chdir(tmp_path)

    exit_code = solution.main([str(REPO_ENGINEERS_CSV)])

    assert exit_code == 0
    out = capsys.readouterr().out
    assert "Processed total engineers: 10" in out
    assert "3 engineers in completed status" in out
    assert "2 engineers in in_progress status" in out
    assert "3 engineers in pending status" in out
    assert "2 engineers in unknown status" in out

    generated = glob.glob(str(tmp_path / "pending-*.txt"))
    assert len(generated) == 1
    pending_emails = Path(generated[0]).read_text(encoding="utf-8").splitlines()
    assert sorted(pending_emails) == sorted(
        [
            "luis.mendoza@example.com",
            "diego.fuentes@example.com",
            "jorge.salinas@example.com",
        ]
    )
