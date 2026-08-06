"""Weekly training-compliance report generator.

Reads an engineer training-status CSV export and writes a plain-text
report summarizing how many engineers are in each training status and
which ones are overdue (not completed, past their deadline).

CLI usage (kept unchanged from the original script)::

    python report_generator_fixed.py <input.csv> <output.txt>

This is the corrected, refactored replacement for ``report_generator.py``;
see ``../ANALYSIS.md`` and ``../BUGS.md`` for the audit and defect list
that drove the fixes and design decisions baked in here.
"""

from __future__ import annotations

import csv
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import NamedTuple

#: Status values the report recognizes and tallies individually. Anything
#: else is grouped under the "unknown" bucket instead of being silently
#: dropped, unlike the original (see ../BUGS.md #9).
KNOWN_STATUSES: tuple[str, ...] = ("completed", "pending", "in_progress")

#: Order status lines appear in the report, regardless of which status
#: happened to appear first in the source CSV. The original relied on
#: plain dict-insertion order, so its line order was data-dependent; a
#: compliance report should read the same way regardless of row order.
_REPORT_STATUS_ORDER: tuple[str, ...] = (*KNOWN_STATUSES, "unknown")

#: CSV columns required for a row to be usable; a row missing or blank in
#: any of these is dropped and counted as skipped. ``deadline`` is
#: deliberately excluded — it's the one optional field (see ../BUGS.md #4).
_REQUIRED_COLUMNS: tuple[str, ...] = ("name", "email", "team", "course_status")


@dataclass(frozen=True)
class Engineer:
    """A single engineer's training-compliance record."""

    name: str
    email: str
    team: str
    status: str
    deadline: date | None


class LoadResult(NamedTuple):
    """Outcome of loading engineers from a CSV file."""

    engineers: list[Engineer]
    skipped: int


def normalize_status(raw: str) -> str:
    """Normalize a raw status string for comparison.

    Strips surrounding whitespace and lowercases; does not validate the
    result against any known set of statuses — that's :func:`count_by_status`'s
    job.

    Args:
        raw: The raw status string, as read from the CSV.

    Returns:
        The stripped, lowercased status.
    """
    return raw.strip().lower()


def parse_deadline(raw: str) -> date | None:
    """Parse a deadline string into a date, or ``None`` if blank.

    Accepts zero-padded and non-zero-padded ``YYYY-MM-DD`` values (e.g.
    both ``2026-06-15`` and ``2026-6-15`` parse to the same date) —
    ``datetime.strptime`` natively tolerates single-digit month/day, which
    is what the original's lexicographic string comparison got wrong.

    Args:
        raw: The raw deadline string, as read from the CSV.

    Returns:
        The parsed date, or ``None`` if ``raw`` is blank (a missing
        deadline is valid input, not a parse error — self-paced or
        optional courses may not have one).

    Raises:
        ValueError: If ``raw`` is non-blank but isn't a valid
            ``YYYY-M-D`` date.
    """
    stripped = raw.strip()
    if not stripped:
        return None
    return datetime.strptime(stripped, "%Y-%m-%d").date()


def _required_field(record: dict[str, str | None], column: str) -> str | None:
    """Return the stripped value of ``column`` in ``record``, or ``None`` if missing/blank."""
    value = record.get(column)
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def load_engineers(path: str | Path) -> LoadResult:
    """Load engineer records from a CSV export.

    Columns are read by header name, not position (see ../BUGS.md #5), so
    the export's column order doesn't matter. A row is dropped — and
    counted in ``LoadResult.skipped`` — if any of ``name``, ``email``,
    ``team``, or ``course_status`` is missing or blank, or if
    ``deadline`` is present but isn't a valid date. A blank ``deadline``
    is kept as ``None`` rather than causing the row to be dropped.

    Args:
        path: Path to the CSV file to read.

    Returns:
        The parsed engineers plus a count of rows that were skipped.

    Raises:
        FileNotFoundError: If ``path`` does not exist.
    """
    engineers: list[Engineer] = []
    skipped = 0

    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        header = next(reader, None)
        if header is None:
            return LoadResult(engineers=[], skipped=0)

        for row in reader:
            record: dict[str, str | None] = dict(zip(header, row, strict=False))

            name = _required_field(record, "name")
            email = _required_field(record, "email")
            team = _required_field(record, "team")
            status_raw = _required_field(record, "course_status")
            if name is None or email is None or team is None or status_raw is None:
                skipped += 1
                continue

            try:
                deadline = parse_deadline(record.get("deadline") or "")
            except ValueError:
                skipped += 1
                continue

            engineers.append(
                Engineer(
                    name=name,
                    email=email,
                    team=team,
                    status=normalize_status(status_raw),
                    deadline=deadline,
                )
            )

    return LoadResult(engineers=engineers, skipped=skipped)


def count_by_status(engineers: Sequence[Engineer]) -> dict[str, int]:
    """Tally engineers per status.

    Statuses outside :data:`KNOWN_STATUSES` are grouped under
    ``"unknown"`` instead of being dropped (see ../BUGS.md #9). Status
    values are re-normalized here regardless of what the caller already
    did, so this function's result doesn't depend on going through
    :func:`load_engineers` first. Only statuses actually present among
    ``engineers`` appear in the result.

    Args:
        engineers: The engineers to tally.

    Returns:
        A mapping of status (or ``"unknown"``) to count.
    """
    counts: dict[str, int] = {}
    for engineer in engineers:
        status = normalize_status(engineer.status)
        bucket = status if status in KNOWN_STATUSES else "unknown"
        counts[bucket] = counts.get(bucket, 0) + 1
    return counts


def overdue(engineers: Sequence[Engineer], today: date | None = None) -> list[str]:
    """Return the emails of engineers who are overdue.

    An engineer is overdue if their (normalized) status isn't
    ``"completed"`` and their deadline is before ``today`` — this keeps
    the original's permissive "anything that isn't completed" rule,
    rather than restricting to the known active statuses; see
    ``../ANALYSIS.md`` for the resulting, deliberately-unfixed
    inconsistency with :func:`count_by_status`, which is stricter about
    what counts as a known status. An engineer with no deadline is never
    overdue (see ../BUGS.md #4).

    Args:
        engineers: The engineers to check.
        today: The reference date to compare deadlines against. Defaults
            to :meth:`date.today` when not supplied (see ../BUGS.md #6 —
            the original hardcoded this instead).

    Returns:
        Overdue engineers' emails, in the same order as ``engineers``.
    """
    reference = today if today is not None else date.today()
    return [
        engineer.email
        for engineer in engineers
        if engineer.deadline is not None
        and normalize_status(engineer.status) != "completed"
        and engineer.deadline < reference
    ]


def build_report(engineers: Sequence[Engineer], skipped: int, today: date | None = None) -> str:
    """Render the plain-text weekly compliance report.

    Status lines are emitted in a fixed order (see
    :data:`_REPORT_STATUS_ORDER`) and only when their count is greater
    than zero.

    Args:
        engineers: The loaded engineers to report on.
        skipped: Count of rows dropped while loading; see
            :func:`load_engineers`.
        today: The reference date for the overdue check; forwarded to
            :func:`overdue`.

    Returns:
        The full report text, including a trailing newline.
    """
    counts = count_by_status(engineers)
    late = overdue(engineers, today=today)

    lines = ["WEEKLY TRAINING COMPLIANCE REPORT"]
    for status in _REPORT_STATUS_ORDER:
        count = counts.get(status, 0)
        if count:
            lines.append(f"{status}: {count}")
    lines.append(f"skipped rows: {skipped}")
    lines.append("overdue engineers:")
    lines.extend(f"  - {email}" for email in late)

    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point: ``report_generator_fixed.py <input.csv> <output.txt>``.

    Args:
        argv: Command-line arguments, excluding the program name. Defaults
            to ``sys.argv[1:]`` when not supplied — that default is what
            lets the script run normally from the command line while
            still being directly callable (and testable) with an
            explicit argument list.

    Returns:
        Process exit code: ``0`` on success, ``2`` on invalid usage, ``1``
        if the input file doesn't exist.
    """
    args = list(sys.argv[1:] if argv is None else argv)

    if len(args) != 2:
        print("Usage: report_generator_fixed.py <input.csv> <output.txt>", file=sys.stderr)
        return 2

    input_path, output_path = args

    try:
        engineers, skipped = load_engineers(input_path)
    except FileNotFoundError:
        print(f"Error: input file not found: {input_path}", file=sys.stderr)
        return 1

    report = build_report(engineers, skipped)
    Path(output_path).write_text(report, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
