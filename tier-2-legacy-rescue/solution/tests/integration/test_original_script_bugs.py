"""Black-box proof that the fixes in `report_generator_fixed.py` are real.

Shells out to the *original*, unfixed ``report_generator.py`` — never
imported, so this doesn't affect `report_generator_fixed`'s coverage
numbers — and asserts it reproduces the exact wrong output documented in
../../BUGS.md for the same sample input every other CLI test in this
directory runs against the fixed script. This is the automated version of
"every bug you report must be reproduced by you": these assertions would
fail if any of BUGS.md #1, #2, or #7 were fixed or hallucinated.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_original_script_reproduces_the_planted_bugs(sample_csv_path: Path, tmp_path: Path) -> None:
    original_script = Path(__file__).resolve().parents[3] / "report_generator.py"
    output_path = tmp_path / "original_report.txt"

    result = subprocess.run(
        [sys.executable, str(original_script), str(sample_csv_path), str(output_path)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    report = output_path.read_text(encoding="utf-8")

    # BUGS.md #2: case/whitespace-sensitive status matching undercounts —
    # Diego Fuentes ("Pending") and Valeria Nunez ("in_progress ") are
    # silently dropped from every bucket instead of being counted.
    assert "pending: 2" in report
    assert "in_progress: 1" in report

    # BUGS.md #7: the skipped-row counter is dead code, so it always
    # reports zero even though Renata Vega's short row was dropped.
    assert "skipped rows: 0" in report

    # BUGS.md #1: Jorge Salinas's non-zero-padded deadline (2026-5-30)
    # sorts after the reference date as a string, so he's wrongly absent
    # from the overdue list despite being months overdue.
    assert "jorge.salinas@example.com" not in report
