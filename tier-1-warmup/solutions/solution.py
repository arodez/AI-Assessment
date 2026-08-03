"""Read a CSV of engineers and report course_status counts + pending emails.

Usage:
    python solution.py [path_to_csv]

If no path is given, defaults to "engineers.csv" in the current directory.

Outputs:
    (a) Count per course_status, printed to stdout.
    (b) Emails with status "pending" (valid emails only), written to
        pending.txt in the current directory.
"""

import csv
import re
import sys
from collections import Counter

DEFAULT_INPUT_PATH = "./data/engineers.csv"
OUTPUT_PATH = "pending.txt"
MISSING_STATUS_LABEL = "missing"
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
REQUIRED_COLUMNS = ("name", "email", "course_status")
ENCODINGS_TO_TRY = ("utf-8-sig", "latin-1")


def read_csv_rows(path):
    """Read the CSV at `path`, trying a small list of encodings.

    Returns a tuple of (rows, fieldnames, encoding_used).
    Raises FileNotFoundError or UnicodeDecodeError if the file cannot
    be read at all.
    """
    last_error = None
    for encoding in ENCODINGS_TO_TRY:
        try:
            with open(path, newline="", encoding=encoding) as csv_file:
                reader = csv.DictReader(csv_file)
                rows = list(reader)
                return rows, reader.fieldnames, encoding
        except UnicodeDecodeError as error:
            last_error = error
            continue
    raise last_error


def is_row_completely_empty(row):
    """True if every value in the row is missing or blank."""
    return all(not (value or "").strip() for value in row.values())


def is_valid_email(email):
    """Basic structural check: non-empty and matches a simple pattern."""
    email = (email or "").strip()
    return bool(EMAIL_PATTERN.match(email))


def normalize_status(raw_status):
    """Return the status trimmed, or the 'missing' label if blank/absent."""
    status = (raw_status or "").strip()
    return status if status else MISSING_STATUS_LABEL


def process_rows(rows, fieldnames):
    """Process parsed CSV rows into a status counter, pending emails,
    and a log of imperfect-row notes for reporting.

    Returns (status_counts, pending_emails, imperfect_notes, discarded_count).
    """
    status_counts = Counter()
    pending_emails = []
    imperfect_notes = []
    discarded_count = 0

    missing_columns = [col for col in REQUIRED_COLUMNS if col not in (fieldnames or [])]
    if missing_columns:
        imperfect_notes.append(
            f"Header is missing expected column(s): {', '.join(missing_columns)}. "
            "Proceeding with the columns that are present."
        )

    for line_number, row in enumerate(rows, start=2):  # header is line 1
        if is_row_completely_empty(row):
            discarded_count += 1
            imperfect_notes.append(f"Row {line_number}: completely empty, discarded.")
            continue

        name = (row.get("name") or "").strip()
        email = (row.get("email") or "").strip()
        raw_status = row.get("course_status")
        status = normalize_status(raw_status)

        if not name:
            imperfect_notes.append(f"Row {line_number}: missing name.")

        if status == MISSING_STATUS_LABEL:
            imperfect_notes.append(
                f"Row {line_number}: missing or blank course_status, "
                f"counted as '{MISSING_STATUS_LABEL}'."
            )

        status_counts[status] += 1

        if status == "pending":
            if is_valid_email(email):
                pending_emails.append(email)
            else:
                imperfect_notes.append(
                    f"Row {line_number}: status is 'pending' but email "
                    f"'{email}' looks invalid, excluded from {OUTPUT_PATH}."
                )

    return status_counts, pending_emails, imperfect_notes, discarded_count


def write_pending_emails(emails, path):
    with open(path, "w", encoding="utf-8") as output_file:
        for email in emails:
            output_file.write(email + "\n")


def print_status_counts(status_counts):
    print("Course status counts:")
    for status in sorted(status_counts):
        print(f"  {status}: {status_counts[status]}")


def print_imperfect_summary(imperfect_notes, discarded_count):
    if not imperfect_notes:
        print("\nNo imperfect rows found.")
        return
    print(f"\n{len(imperfect_notes)} note(s) about imperfect rows:")
    for note in imperfect_notes:
        print(f"  - {note}")
    if discarded_count:
        print(f"\n{discarded_count} row(s) were completely empty and discarded.")


def main():
    input_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_INPUT_PATH

    try:
        rows, fieldnames, encoding_used = read_csv_rows(input_path)
    except FileNotFoundError:
        print(f"Error: could not find input file '{input_path}'.", file=sys.stderr)
        sys.exit(1)
    except UnicodeDecodeError:
        print(
            f"Error: could not decode '{input_path}' with any of the "
            f"supported encodings {ENCODINGS_TO_TRY}.",
            file=sys.stderr,
        )
        sys.exit(1)

    if not rows:
        print(f"'{input_path}' has no data rows (only a header, or is empty).")
        write_pending_emails([], OUTPUT_PATH)
        return

    print(f"Read '{input_path}' using encoding '{encoding_used}'.")

    status_counts, pending_emails, imperfect_notes, discarded_count = process_rows(
        rows, fieldnames
    )

    write_pending_emails(pending_emails, OUTPUT_PATH)

    print_status_counts(status_counts)
    print(f"\nWrote {len(pending_emails)} pending email(s) to '{OUTPUT_PATH}'.")
    print_imperfect_summary(imperfect_notes, discarded_count)


if __name__ == "__main__":
    main()
