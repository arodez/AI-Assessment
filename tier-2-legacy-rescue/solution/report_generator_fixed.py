"""Generates a weekly training-compliance report from a CSV of engineer records."""

import csv
import sys
from datetime import date
from typing import TypedDict


class Engineer(TypedDict):
    name: str
    email: str
    team: str
    status: str
    deadline: str


def load_engineers(path: str) -> tuple[list[Engineer], int]:
    """Read engineer rows from `path`, skipping malformed rows.

    Returns the list of parsed engineers and the count of rows skipped
    because they didn't have the expected 5 columns.
    """
    engineers: list[Engineer] = []
    skipped = 0
    with open(path) as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            try:
                engineers.append({
                    'name': row[0],
                    'email': row[1],
                    'team': row[2],
                    'status': row[3],
                    'deadline': row[4],
                })
            except IndexError:
                skipped += 1
                continue
    return engineers, skipped


def count_by_status(engineers: list[Engineer]) -> dict[str, int]:
    """Tally engineers per status, normalizing case and surrounding whitespace."""
    counts: dict[str, int] = {}
    for e in engineers:
        s = e['status'].strip().lower()
        if s in ('completed', 'pending', 'in_progress'):
            counts[s] = counts.get(s, 0) + 1
    return counts


def _parse_date(value: str) -> date:
    year, month, day = value.strip().split('-')
    return date(int(year), int(month), int(day))


def overdue(engineers: list[Engineer], today: str = '2026-07-14') -> list[str]:
    """Return the emails of non-completed engineers whose deadline has passed."""
    today_date = _parse_date(today)
    result = []
    for e in engineers:
        if e['status'].strip().lower() != 'completed' and _parse_date(e['deadline']) < today_date:
            result.append(e['email'])
    return result


def main() -> None:
    input_path, output_path = sys.argv[1], sys.argv[2]
    engineers, skipped = load_engineers(input_path)
    counts = count_by_status(engineers)
    late = overdue(engineers)
    with open(output_path, 'w') as out:
        out.write('WEEKLY TRAINING COMPLIANCE REPORT\n')
        for status, n in counts.items():
            out.write(f'{status}: {n}\n')
        out.write(f'skipped rows: {skipped}\n')
        out.write('overdue engineers:\n')
        for email in late:
            out.write(f'  - {email}\n')


if __name__ == '__main__':
    main()
