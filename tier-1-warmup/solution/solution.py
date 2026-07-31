import sys
import os
import csv
import re
from collections import Counter


def validate_email(email):
    """Return True if email matches a basic valid format."""
    email_regex = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    return re.match(email_regex, email.strip()) is not None


def process_csv(csv_path):
    """
    Read and validate the CSV at csv_path.

    Returns:
        status_counts (Counter): count of valid rows per course_status.
        pending_emails (list):   emails whose course_status == 'pending'.

    Raises:
        FileNotFoundError: if csv_path does not exist.
        ValueError:        if the file is empty or missing required columns.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"File '{csv_path}' not found.")

    status_counts = Counter()
    pending_emails = []

    with open(csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)

        # --- Header validation ---
        try:
            headers = next(reader)
        except StopIteration:
            raise ValueError("The CSV file is empty.")

        cleaned_headers = [h.strip().lower() for h in headers]
        expected = ['name', 'email', 'course_status']
        missing = [col for col in expected if col not in cleaned_headers]
        if missing:
            raise ValueError(
                f"Missing required column(s): {missing}. "
                f"Expected {expected}, found {headers}."
            )

        name_idx   = cleaned_headers.index('name')
        email_idx  = cleaned_headers.index('email')
        status_idx = cleaned_headers.index('course_status')
        # Map of required column name → its header index (used for per-row validation)
        required_col_map = [('name', name_idx), ('email', email_idx), ('course_status', status_idx)]

        # --- Row processing ---
        for line_num, row in enumerate(reader, start=2):
            # Skip truly empty lines (e.g. trailing newlines)
            if not row:
                continue
            # Skip rows where every cell is whitespace-only (e.g. ', , ')
            if all(cell.strip() == '' for cell in row):
                print(
                    f"Skipping line {line_num}: All fields are empty or whitespace-only.",
                    file=sys.stderr
                )
                continue

            # Check each required column is reachable — extra non-required columns are ignored
            missing_required = [(col, idx) for col, idx in required_col_map if idx >= len(row)]
            if missing_required:
                cols_str = ', '.join(f"'{col}'" for col, _ in missing_required)
                print(
                    f"Skipping malformed line {line_num}: "
                    f"Missing required column(s) {cols_str} "
                    f"(row has only {len(row)} column(s)).",
                    file=sys.stderr
                )
                continue

            name   = row[name_idx].strip()
            email  = row[email_idx].strip()
            status = row[status_idx].strip().lower()

            if not name:
                print(f"Skipping line {line_num}: Name is empty.", file=sys.stderr)
                continue
            if not email or not validate_email(email):
                print(f"Skipping line {line_num}: Invalid or empty email '{email}'.", file=sys.stderr)
                continue
            if not status:
                print(f"Skipping line {line_num}: Course status is empty.", file=sys.stderr)
                continue

            status_counts[status] += 1
            if status == 'pending':
                pending_emails.append(email)

    return status_counts, pending_emails


def write_pending(pending_emails, output_path):
    """Write pending email addresses to output_path, one per line."""
    with open(output_path, mode='w', encoding='utf-8') as f:
        for email in pending_emails:
            f.write(email + '\n')


def main():
    print("=== Engineer CSV Processor — Starting ===\n")

    script_dir       = os.path.dirname(os.path.abspath(__file__))
    default_csv_path = os.path.join(script_dir,'..', 'data', 'engineers.csv')
    csv_path         = sys.argv[1] if len(sys.argv) > 1 else default_csv_path

    # --- Process CSV ---
    try:
        status_counts, pending_emails = process_csv(csv_path)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error reading CSV: {e}", file=sys.stderr)
        sys.exit(1)

    # --- Print status counts ---
    print("--- Status Counts ---")
    if not status_counts:
        print("No valid status records found.")
    else:
        for status, count in sorted(status_counts.items()):
            print(f"  {status}: {count}")

    # --- Write pending.txt ---
    output_path = os.path.join(script_dir, 'pending.txt')
    try:
        write_pending(pending_emails, output_path)
        print(f"\nPending emails ({len(pending_emails)}) written to '{output_path}'")
    except Exception as e:
        print(f"Error writing output file: {e}", file=sys.stderr)
        sys.exit(1)

    print("\n=== Engineer CSV Processor — Finished ===")


if __name__ == '__main__':
    main()
