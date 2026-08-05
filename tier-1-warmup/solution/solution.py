#!/usr/bin/env python3
"""CLI that summarizes engineer course_status from a CSV.

Reads a CSV of engineers (name, email, course_status), prints a total count
and a per-status breakdown, and writes the emails of engineers whose status
is "pending" to a timestamped pending-<timestamp>.txt file.

All three CSV columns are treated as optional. Rows that are malformed
(missing columns, blank values, extra columns) are handled gracefully rather
than raising — see normalize_status()/is_blank_row() for the exact rules.

Usage:
    python solution.py path/to/engineers.csv
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

REQUIRED_FIELDS = ("name", "email", "course_status")


def read_raw_rows(csv_path: str) -> list[dict]:
    """Read a CSV file into a list of raw row dicts.

    Uses csv.DictReader against the file's own header row, so column order
    doesn't matter as long as the header names match REQUIRED_FIELDS.
    DictReader already handles the two known malformed-row shapes for us:
    rows with fewer fields than the header get the missing keys set to None
    (via `restval`, which defaults to None), and rows with extra fields have
    the overflow collected under the `None` key (via `restkey`) and simply
    ignored below. Fully blank physical lines are skipped by DictReader
    itself before they ever reach us.

    A UnicodeDecodeError (e.g. a non-UTF-8 file) is caught and retried with
    `errors="replace"` so a bad encoding doesn't crash the tool outright; a
    warning is printed to stderr in that case.
    """
    try:
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return list(reader)
    except UnicodeDecodeError:
        print(
            f"Warning: {csv_path} is not valid UTF-8; re-reading with "
            "replacement characters for undecodable bytes.",
            file=sys.stderr,
        )
        with open(csv_path, newline="", encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            return list(reader)


def normalize_row(raw: dict) -> dict:
    """Normalize a raw DictReader row to {"name", "email", "course_status"}.

    Missing columns (None, from DictReader's restval) become "", and every
    value is stripped of surrounding whitespace. Any extra/unexpected
    columns (collected by DictReader under the None key) are ignored here.
    """
    return {field: (raw.get(field) or "").strip() for field in REQUIRED_FIELDS}


def is_blank_row(row: dict) -> bool:
    """True iff every field of a normalized row is empty.

    Covers both a fully blank line (already filtered by DictReader, but kept
    here for safety/direct callers) and a "row that's just commas" (",,"),
    which DictReader turns into a row of three empty strings rather than an
    empty list.
    """
    return all(row[field] == "" for field in REQUIRED_FIELDS)


def normalize_status(status: str) -> str:
    """Normalize a course_status value for grouping/matching.

    Trims whitespace and lowercases so " Pending ", "PENDING", and "pending"
    are treated as the same status. A missing/blank status normalizes to
    the literal group label "unknown".
    """
    normalized = status.strip().lower()
    return normalized if normalized else "unknown"


def is_pending(status: str) -> bool:
    """True iff a course_status value normalizes to "pending"."""
    return normalize_status(status) == "pending"


def process_rows(raw_rows: list[dict]) -> tuple[int, Counter, list[str]]:
    """Turn raw CSV rows into (total_count, status_counts, pending_emails).

    - Every non-blank row counts toward the total, even if name and/or
      email are missing.
    - Rows are grouped by normalize_status(course_status); missing/blank
      statuses land in the "unknown" bucket.
    - An email is added to the pending list only when its status is
      "pending" AND the email field is non-blank (a pending row with no
      email is still counted in the status tally, but there's nothing
      meaningful to write to the pending file).
    - No de-duplication is performed anywhere: duplicate rows are each
      counted, and duplicate pending emails are each written.
    """
    total = 0
    status_counts: Counter = Counter()
    pending_emails: list[str] = []

    for raw in raw_rows:
        row = normalize_row(raw)
        if is_blank_row(row):
            continue

        total += 1
        status = normalize_status(row["course_status"])
        status_counts[status] += 1

        if status == "pending" and row["email"]:
            pending_emails.append(row["email"])

    return total, status_counts, pending_emails


def format_status_lines(status_counts: Counter) -> list[str]:
    """Render one output line per status, sorted alphabetically by status.

    Alphabetical order is a deliberate choice for deterministic, testable
    output — the spec doesn't mandate an order, and insertion order would
    depend on row order in the input file.
    """
    return [
        f"{count} engineers in {status} status"
        for status, count in sorted(status_counts.items())
    ]


def generate_timestamp(now: datetime | None = None) -> str:
    """Return the current datetime in ISO format, filesystem-safe.

    Raw ISO timestamps contain colons (e.g. "14:05:30"), which are awkward
    or invalid in filenames on some filesystems, so colons are replaced
    with hyphens. `now` can be injected for deterministic unit tests.
    """
    return (now or datetime.now()).isoformat(timespec="seconds").replace(":", "-")


def pending_filename(timestamp: str) -> str:
    """Build the pending-report filename for a given timestamp string."""
    return f"pending-{timestamp}.txt"


def write_pending_file(path: Path, emails: list[str]) -> None:
    """Write one email per line to `path`, with a trailing newline."""
    content = "\n".join(emails)
    if content:
        content += "\n"
    path.write_text(content, encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Summarize engineer course_status from a CSV and write a "
            "pending-emails report."
        )
    )
    parser.add_argument(
        "csv_path",
        help="Path to a CSV file with name, email, course_status columns.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    csv_path = Path(args.csv_path)
    if not csv_path.is_file():
        print(f"Error: {csv_path} is not a file or does not exist.", file=sys.stderr)
        return 1

    raw_rows = read_raw_rows(str(csv_path))
    total, status_counts, pending_emails = process_rows(raw_rows)

    print(f"Processed total engineers: {total}")
    for line in format_status_lines(status_counts):
        print(line)

    # pending-<timestamp>.txt is written to the current working directory
    # the script is invoked from (not next to the input CSV), since the
    # input may live in a shared/reference location that shouldn't be
    # polluted with generated output. See GUIDE.md for the full rationale.
    timestamp = generate_timestamp()
    filename = pending_filename(timestamp)
    write_pending_file(Path(filename), pending_emails)
    print(f"Pending results generated in {filename}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
