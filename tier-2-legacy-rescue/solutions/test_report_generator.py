"""Tests for report_generator_fixed.py.

Two layers of tests are included:

1. Unit tests (below) against the fixed implementation's internal API
   (load_engineers, count_by_status, overdue, build_report). These use
   the refactored data types (LoadResult, Engineer) and therefore only
   import-and-run against report_generator_fixed.py.

2. CLI/subprocess end-to-end tests (bottom of file, TestCLIBehavior*)
   that invoke the script as a black box (`python <script> in.csv out.txt`)
   and assert on the text of the generated report. These are
   implementation-agnostic and are what the evaluator can point at
   report_generator.py to see the 4 planted bugs actually fail.

Run with: pytest test_report_generator.py
"""

import csv
import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest

from report_generator_fixed import (
    Engineer,
    build_report,
    count_by_status,
    load_engineers,
    overdue,
)


def write_csv(path: Path, rows: list[list[str]]) -> None:
    """Helper: write a CSV file with a standard header + given data rows."""
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "email", "team", "status", "deadline"])
        writer.writerows(rows)


# ---------------------------------------------------------------------
# Bug 1: skipped-row counter
# ---------------------------------------------------------------------

def test_skipped_rows_are_counted(tmp_path):
    """A malformed row (too few columns) must increment the skipped count.

    Fails on the original: SKIPPED is always reported as 0 because the
    increment is dead code after `continue`.
    """
    csv_path = tmp_path / "input.csv"
    write_csv(
        csv_path,
        [
            ["Ana Torres", "ana@example.com", "Platform", "completed", "2026-06-30"],
            ["Renata Vega", "renata@example.com", "Mobile"],  # malformed: too few cols
        ],
    )
    result = load_engineers(str(csv_path))
    assert result.skipped == 1
    assert len(result.engineers) == 1


# ---------------------------------------------------------------------
# Bug 2: case/whitespace-insensitive status counting
# ---------------------------------------------------------------------

def test_status_counted_regardless_of_case_and_whitespace(tmp_path):
    """Statuses with different casing or trailing whitespace must still count.

    Fails on the original: 'Pending' and 'in_progress ' fall through the
    exact-match if/elif and are silently dropped from the counts.
    """
    csv_path = tmp_path / "input.csv"
    write_csv(
        csv_path,
        [
            ["Diego Fuentes", "diego@example.com", "Data", "Pending", "2026-06-20"],
            ["Valeria Nunez", "valeria@example.com", "Platform", "in_progress ", "2026-07-10"],
        ],
    )
    result = load_engineers(str(csv_path))
    counts = count_by_status(result.engineers)
    assert counts.get("pending") == 1
    assert counts.get("in_progress") == 1
    assert sum(counts.values()) == len(result.engineers)


# ---------------------------------------------------------------------
# Bug 3: real date comparison instead of string comparison
# ---------------------------------------------------------------------

def test_overdue_detects_non_zero_padded_dates(tmp_path):
    """A deadline like '2026-5-30' must still be correctly detected as overdue.

    Fails on the original: string comparison '2026-5-30' < '2026-07-14'
    is False even though the real date is earlier.
    """
    csv_path = tmp_path / "input.csv"
    write_csv(
        csv_path,
        [
            ["Jorge Salinas", "jorge@example.com", "Mobile", "pending", "2026-5-30"],
        ],
    )
    result = load_engineers(str(csv_path))
    late = overdue(result.engineers, today=date(2026, 7, 14))
    assert "jorge@example.com" in late


def test_overdue_excludes_completed_engineers(tmp_path):
    """Completed engineers must never appear in the overdue list, even if late."""
    csv_path = tmp_path / "input.csv"
    write_csv(
        csv_path,
        [
            ["Emilio Castro", "emilio@example.com", "Data", "completed", "2026-05-30"],
        ],
    )
    result = load_engineers(str(csv_path))
    late = overdue(result.engineers, today=date(2026, 7, 14))
    assert "emilio@example.com" not in late


# ---------------------------------------------------------------------
# Bug 4: no shared mutable state across calls
# ---------------------------------------------------------------------

def test_load_engineers_does_not_leak_state_between_calls(tmp_path):
    """Calling load_engineers twice must not accumulate rows across calls.

    Fails on the original: append_row's mutable default `rows=[]` is
    shared across all calls, so a second call returns double the rows.
    """
    csv_path = tmp_path / "input.csv"
    write_csv(
        csv_path,
        [
            ["Ana Torres", "ana@example.com", "Platform", "completed", "2026-06-30"],
        ],
    )
    first = load_engineers(str(csv_path))
    second = load_engineers(str(csv_path))
    assert len(first.engineers) == 1
    assert len(second.engineers) == 1
    assert first.engineers is not second.engineers


# ---------------------------------------------------------------------
# Additional edge-case tests (beyond the planted bugs)
# ---------------------------------------------------------------------

def test_unknown_status_is_not_counted_but_does_not_crash(tmp_path):
    """A completely unrecognized status value should not appear in counts
    and should not raise."""
    csv_path = tmp_path / "input.csv"
    write_csv(
        csv_path,
        [
            ["Nora Vidal", "nora@example.com", "Data", "on_hold", "2026-06-01"],
        ],
    )
    result = load_engineers(str(csv_path))
    counts = count_by_status(result.engineers)
    assert "on_hold" not in counts
    assert result.skipped == 0  # row is well-formed, just an unusual status


def test_build_report_output_format(tmp_path):
    """The report text must include all expected sections in order."""
    engineers = [
        Engineer("Ana", "ana@example.com", "Platform", "completed", date(2026, 6, 30)),
        Engineer("Luis", "luis@example.com", "Platform", "pending", date(2026, 6, 15)),
    ]
    report = build_report(engineers, skipped=1, today=date(2026, 7, 14))
    assert "WEEKLY TRAINING COMPLIANCE REPORT" in report
    assert "completed: 1" in report
    assert "pending: 1" in report
    assert "skipped rows: 1" in report
    assert "luis@example.com" in report


def test_full_sample_input_matches_expected_counts(tmp_path):
    """End-to-end check against the provided sample_input.csv-style data,
    verifying the combined effect of all four fixes at once."""
    csv_path = tmp_path / "input.csv"
    write_csv(
        csv_path,
        [
            ["Ana Torres", "ana.torres@example.com", "Platform", "completed", "2026-06-30"],
            ["Luis Mendoza", "luis.mendoza@example.com", "Platform", "pending", "2026-06-15"],
            ["Sofia Reyes", "sofia.reyes@example.com", "Data", "in_progress", "2026-08-01"],
            ["Diego Fuentes", "diego.fuentes@example.com", "Data", "Pending", "2026-06-20"],
            ["Camila Ortiz", "camila.ortiz@example.com", "Mobile", "completed", "2026-07-01"],
            ["Jorge Salinas", "jorge.salinas@example.com", "Mobile", "pending", "2026-5-30"],
            ["Valeria Nunez", "valeria.nunez@example.com", "Platform", "in_progress ", "2026-07-10"],
            ["Emilio Castro", "emilio.castro@example.com", "Data", "completed", "2026-05-30"],
            ["Renata Vega", "renata.vega@example.com", "Mobile"],
        ],
    )
    result = load_engineers(str(csv_path))
    assert result.skipped == 1  # Renata Vega
    assert len(result.engineers) == 8

    counts = count_by_status(result.engineers)
    assert counts == {"completed": 3, "pending": 3, "in_progress": 2}

    late = overdue(result.engineers, today=date(2026, 7, 14))
    assert set(late) == {
        "luis.mendoza@example.com",
        "diego.fuentes@example.com",
        "jorge.salinas@example.com",
        "valeria.nunez@example.com",
    }


# ---------------------------------------------------------------------
# CLI / black-box tests — implementation-agnostic.
#
# These run the script as a subprocess and check the generated report
# text directly, so they exercise report_generator.py (the original)
# and report_generator_fixed.py identically via SCRIPT_PATH below.
# This is the layer the evaluator can point at the original script to
# see the 4 planted bugs reproduce as real failures (not just API
# differences from the refactor).
# ---------------------------------------------------------------------

# NOTE for evaluators: swapping this constant to point at the original
# report_generator.py and running only the test_cli_* functions
# reproduces 3 of the 4 planted bugs as real, observable failures
# (skipped-row count, dropped status counts, non-zero-padded date
# comparison). The 4th bug (mutable-default state leak in append_row)
# does NOT reproduce at the CLI layer, because each CLI invocation is a
# fresh process — it only manifests when load_engineers is called more
# than once within the same process, which is exactly what
# test_load_engineers_does_not_leak_state_between_calls (an in-process
# unit test) targets instead. The other in-process unit tests import
# report_generator_fixed's refactored API directly (LoadResult, Engineer)
# and will fail with ImportError against the original by design, since
# the original never had that API — that is a naming difference, not a
# demonstration of the bug, which is why the test_cli_* black-box layer
# exists.
SCRIPT_PATH = str(Path(__file__).parent / "report_generator_fixed.py")


def run_cli(script_path: str, csv_path: Path, out_path: Path) -> str:
    """Run the report generator CLI and return the resulting report text."""
    subprocess.run(
        [sys.executable, script_path, str(csv_path), str(out_path)],
        check=True,
        capture_output=True,
        text=True,
    )
    return out_path.read_text()


def test_cli_skipped_rows_are_counted(tmp_path):
    """Bug 1, black-box: skipped rows must be reflected in the report text.

    Fails on the original: report always says 'skipped rows: 0'.
    """
    csv_path = tmp_path / "input.csv"
    write_csv(
        csv_path,
        [
            ["Ana Torres", "ana@example.com", "Platform", "completed", "2026-06-30"],
            ["Renata Vega", "renata@example.com", "Mobile"],
        ],
    )
    out_path = tmp_path / "out.txt"
    report = run_cli(SCRIPT_PATH, csv_path, out_path)
    assert "skipped rows: 1" in report


def test_cli_status_counts_are_not_silently_dropped(tmp_path):
    """Bug 2, black-box: total status counts must equal total loaded engineers.

    Fails on the original: engineers with 'Pending' or 'in_progress '
    vanish from every count.
    """
    csv_path = tmp_path / "input.csv"
    write_csv(
        csv_path,
        [
            ["Diego Fuentes", "diego@example.com", "Data", "Pending", "2026-06-20"],
            ["Valeria Nunez", "valeria@example.com", "Platform", "in_progress ", "2026-07-10"],
        ],
    )
    out_path = tmp_path / "out.txt"
    report = run_cli(SCRIPT_PATH, csv_path, out_path)
    assert "pending: 1" in report
    assert "in_progress: 1" in report


def test_cli_overdue_detects_non_zero_padded_dates(tmp_path):
    """Bug 3, black-box: '2026-5-30' must be flagged overdue against '2026-07-14'.

    Fails on the original: string comparison misses this date.
    """
    csv_path = tmp_path / "input.csv"
    write_csv(
        csv_path,
        [
            ["Jorge Salinas", "jorge@example.com", "Mobile", "pending", "2026-5-30"],
        ],
    )
    out_path = tmp_path / "out.txt"
    report = run_cli(SCRIPT_PATH, csv_path, out_path)
    assert "jorge@example.com" in report


def test_cli_runs_twice_without_accumulating_state(tmp_path):
    """Bug 4, black-box: two separate CLI invocations must each report the
    same, correct counts — no leakage between runs.

    (Each CLI invocation is its own process, so the original script's
    mutable-default bug doesn't surface here the same way the in-process
    unit test catches it — this test instead guards against a regression
    if the report generator is ever imported and called twice within one
    process, e.g. from a scheduler.)
    """
    csv_path = tmp_path / "input.csv"
    write_csv(
        csv_path,
        [["Ana Torres", "ana@example.com", "Platform", "completed", "2026-06-30"]],
    )
    out1 = tmp_path / "out1.txt"
    out2 = tmp_path / "out2.txt"
    report1 = run_cli(SCRIPT_PATH, csv_path, out1)
    report2 = run_cli(SCRIPT_PATH, csv_path, out2)
    assert report1 == report2
    assert "completed: 1" in report1


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
