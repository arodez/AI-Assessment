#!/usr/bin/env python3
"""Count engineers by course_status and list pending emails.

Usage:
    python solution.py [path/to/engineers.csv]

Reads a CSV of engineers (name,email,course_status), prints the count of
engineers per status, and writes the emails of engineers with status
"pending" to pending.txt (one per line).
"""

import csv
import sys
from collections import Counter
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_INPUT = SCRIPT_DIR / "data" / "engineers.csv"
PENDING_OUTPUT = SCRIPT_DIR / "pending.txt"


def load_rows(csv_path: Path):
    """Yield (name, email, status) tuples, normalizing and validating each row.

    Rows missing a name or email are skipped and counted as "invalid".
    Rows missing a status are kept but bucketed under "unknown".
    """
    with csv_path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = (row.get("name") or "").strip()
            email = (row.get("email") or "").strip()
            status = (row.get("course_status") or "").strip().lower()

            if not name or not email:
                yield None, None, "invalid"
                continue

            yield name, email, status or "unknown"


def main():
    csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_INPUT

    if not csv_path.is_file():
        print(f"Error: input file not found: {csv_path}", file=sys.stderr)
        sys.exit(1)

    counts = Counter()
    pending_emails = []

    for name, email, status in load_rows(csv_path):
        counts[status] += 1
        if status == "pending":
            pending_emails.append(email)

    print("Counts per status:")
    for status, count in sorted(counts.items()):
        print(f"  {status}: {count}")

    PENDING_OUTPUT.write_text(
        "\n".join(pending_emails) + ("\n" if pending_emails else ""),
        encoding="utf-8",
    )
    print(f"\nWrote {len(pending_emails)} pending email(s) to {PENDING_OUTPUT}")


if __name__ == "__main__":
    main()
