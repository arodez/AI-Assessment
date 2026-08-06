"""Integration tests exercising `report_generator_fixed` end to end.

Most tests call `main()` directly (in-process, so it's covered by
`--cov`) with an explicit `argv`, then inspect the written output file —
this is the real regression surface for the CLI contract in
../../../README.md ("Keep the CLI interface unchanged:
`python report_generator_fixed.py <input.csv> <output.txt>`"), which is
also why `main` takes no flag for overriding `today`: only the two
positional arguments are part of that contract.

Because of that constraint, tests that need a deterministic overdue
result build their own small CSV with deadlines computed relative to the
real `date.today()` at test time, rather than asserting an exact overdue
list against the shipped, date-fixed `data/sample_input.csv` — pinning
that against a moving "today" would make the suite flaky the day after
it's written. The counts-and-skipped-rows assertions below *are* run
against the real sample file, since those are date-independent.

One test additionally shells out to the real interpreter (`subprocess`)
as a literal black-box check of the documented command line; it's not
relied on for coverage — the in-process `main()` calls already cover the
module — just as a sanity check that the script is actually invocable the
way the README promises.
"""

from __future__ import annotations

import subprocess
import sys
from collections.abc import Callable
from datetime import date, timedelta
from pathlib import Path

import pytest

from report_generator_fixed import main


def test_end_to_end_counts_and_skipped_rows_against_sample_input(
    sample_csv_path: Path, tmp_path: Path
) -> None:
    output_path = tmp_path / "report.txt"

    exit_code = main([str(sample_csv_path), str(output_path)])

    assert exit_code == 0
    report = output_path.read_text(encoding="utf-8")
    assert "completed: 3" in report
    assert "pending: 3" in report  # Luis, Diego ("Pending"), Jorge Salinas
    assert "in_progress: 2" in report  # Sofia, Valeria ("in_progress ")
    assert "skipped rows: 1" in report  # Renata Vega (missing status/deadline)
    assert "unknown" not in report  # no unrecognized statuses in the sample data


def test_end_to_end_overdue_uses_the_real_current_date(
    write_csv: Callable[..., Path], tmp_path: Path
) -> None:
    today = date.today()
    overdue_deadline = str(today - timedelta(days=1))
    upcoming_deadline = str(today + timedelta(days=1))
    input_path = write_csv(
        [
            ("Overdue Engineer", "overdue@example.com", "Platform", "pending", overdue_deadline),
            ("On Track Engineer", "ontrack@example.com", "Platform", "pending", upcoming_deadline),
        ]
    )
    output_path = tmp_path / "report.txt"

    exit_code = main([str(input_path), str(output_path)])

    assert exit_code == 0
    report = output_path.read_text(encoding="utf-8")
    assert "overdue@example.com" in report
    assert "ontrack@example.com" not in report


def test_missing_arguments_returns_nonzero_and_prints_usage(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = main([])

    assert exit_code != 0
    assert "usage" in capsys.readouterr().err.lower()


def test_missing_input_file_returns_nonzero_and_does_not_write_output(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    missing_input = tmp_path / "missing.csv"
    output_path = tmp_path / "report.txt"

    exit_code = main([str(missing_input), str(output_path)])

    assert exit_code != 0
    assert str(missing_input) in capsys.readouterr().err
    assert not output_path.exists()


def test_repeated_calls_do_not_leak_state_across_each_other(
    write_csv: Callable[..., Path], tmp_path: Path
) -> None:
    """CLI-level regression test for the mutable-default-argument bug (BUGS.md #3, #8)."""
    first_input = write_csv(
        [("Ana Torres", "ana@example.com", "Platform", "completed", "2020-01-01")],
        filename="first.csv",
    )
    second_input = write_csv(
        [("Luis Mendoza", "luis@example.com", "Platform", "pending", "2020-01-01")],
        filename="second.csv",
    )
    first_output = tmp_path / "first_report.txt"
    second_output = tmp_path / "second_report.txt"

    main([str(first_input), str(first_output)])
    main([str(second_input), str(second_output)])

    assert "completed: 1" in first_output.read_text(encoding="utf-8")
    assert "pending" not in first_output.read_text(encoding="utf-8")
    assert "pending: 1" in second_output.read_text(encoding="utf-8")
    assert "completed" not in second_output.read_text(encoding="utf-8")


def test_cli_is_invocable_as_documented(sample_csv_path: Path, tmp_path: Path) -> None:
    """Black-box check of `python report_generator_fixed.py <input.csv> <output.txt>`."""
    script_path = Path(__file__).resolve().parents[2] / "report_generator_fixed.py"
    output_path = tmp_path / "report.txt"

    result = subprocess.run(
        [sys.executable, str(script_path), str(sample_csv_path), str(output_path)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert output_path.read_text(encoding="utf-8").startswith("WEEKLY TRAINING COMPLIANCE REPORT\n")
