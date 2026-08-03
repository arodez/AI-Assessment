"""Weekly training-compliance report generator.

Reads a CSV of engineers and their training status, and writes a plain
text compliance report summarizing status counts and overdue engineers.

CLI:
    python report_generator_fixed.py <input.csv> <output.txt>
"""

from __future__ import annotations

import csv
import sys
from dataclasses import dataclass
from datetime import date
from typing import NamedTuple


VALID_STATUSES = ("completed", "pending", "in_progress")


@dataclass
class Engineer:
    """A single engineer's training-compliance record."""

    name: str
    email: str
    team: str
    status: str
    deadline: date


class LoadResult(NamedTuple):
    """Result of loading engineers from a CSV file."""

    engineers: list[Engineer]
    skipped: int


def _normalize_status(raw_status: str) -> str:
    """Normalize a status string for comparison (trim whitespace, lowercase)."""
    return raw_status.strip().lower()


def _parse_deadline(raw_deadline: str) -> date:
    """Parse a deadline string into a date, tolerating missing zero-padding
    (e.g. '2026-5-30' as well as '2026-05-30').

    Raises:
        ValueError: if the string is not a parseable Y-M-D date.
    """
    year, month, day = raw_deadline.strip().split("-")
    return date(int(year), int(month), int(day))


def _parse_row(row: list[str]) -> Engineer:
    """Parse a single CSV row into an Engineer.

    Raises:
        ValueError: if the row has too few columns or the deadline is not
            a parseable Y-M-D date.
        IndexError: if the row has too few columns (also caught by callers
            as part of malformed-row handling).
    """
    if len(row) < 5:
        raise ValueError(f"expected 5 columns, got {len(row)}: {row!r}")

    name, email, team, status, deadline_str = row[0], row[1], row[2], row[3], row[4]
    deadline = _parse_deadline(deadline_str)
    return Engineer(
        name=name,
        email=email,
        team=team,
        status=_normalize_status(status),
        deadline=deadline,
    )


def load_engineers(path: str) -> LoadResult:
    """Load engineer records from a CSV file at `path`.

    Rows that are malformed (too few columns, unparseable date, etc.) are
    skipped and counted rather than raising. The header row is always
    skipped.

    Returns:
        A LoadResult with the list of successfully parsed engineers and
        the count of rows that were skipped due to bad data.
    """
    engineers: list[Engineer] = []
    skipped = 0

    with open(path, newline="") as f:
        reader = csv.reader(f)
        next(reader, None)  # skip header
        for row in reader:
            if not row:
                continue
            try:
                engineers.append(_parse_row(row))
            except (ValueError, IndexError):
                skipped += 1
                continue

    return LoadResult(engineers=engineers, skipped=skipped)


def count_by_status(engineers: list[Engineer]) -> dict[str, int]:
    """Count engineers per known training status.

    Statuses outside VALID_STATUSES are ignored here (already normalized
    by _parse_row), matching the original report's set of tracked
    statuses.
    """
    counts: dict[str, int] = {}
    for engineer in engineers:
        if engineer.status in VALID_STATUSES:
            counts[engineer.status] = counts.get(engineer.status, 0) + 1
    return counts


def overdue(engineers: list[Engineer], today: date) -> list[str]:
    """Return emails of engineers who are not completed and past deadline."""
    return [
        engineer.email
        for engineer in engineers
        if engineer.status != "completed" and engineer.deadline < today
    ]


def build_report(engineers: list[Engineer], skipped: int, today: date) -> str:
    """Build the full text report as a single string."""
    counts = count_by_status(engineers)
    late = overdue(engineers, today)

    lines = ["WEEKLY TRAINING COMPLIANCE REPORT"]
    for status, n in counts.items():
        lines.append(f"{status}: {n}")
    lines.append(f"skipped rows: {skipped}")
    lines.append("overdue engineers:")
    for email in late:
        lines.append(f"  - {email}")

    return "\n".join(lines) + "\n"


def main() -> None:
    """CLI entry point: python report_generator_fixed.py <input.csv> <output.txt>."""
    if len(sys.argv) != 3:
        print(
            f"usage: python {sys.argv[0]} <input.csv> <output.txt>",
            file=sys.stderr,
        )
        sys.exit(1)

    input_path, output_path = sys.argv[1], sys.argv[2]
    result = load_engineers(input_path)
    report = build_report(result.engineers, result.skipped, today=date(2026, 7, 14))

    with open(output_path, "w") as out:
        out.write(report)


if __name__ == "__main__":
    main()
