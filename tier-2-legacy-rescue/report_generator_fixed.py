"""Weekly training compliance report generator.

This module processes training data for engineers, calculates status counts,
and flags overdue training tasks.
"""

import sys
import csv
from datetime import date
from typing import List, Dict, Any, Optional

# Global variable to track the count of skipped malformed rows.
SKIPPED: int = 0


def parse_date(date_str: str) -> date:
    """Parses a YYYY-MM-DD date string (supporting non-zero-padded values).

    Args:
        date_str: A string in YYYY-MM-DD or YYYY-M-D format.

    Returns:
        A datetime.date object.

    Raises:
        ValueError: If the date format is invalid or cannot be parsed.
    """
    parts = date_str.strip().split('-')
    if len(parts) != 3:
        raise ValueError(f"Invalid date format: {date_str}")
    return date(int(parts[0]), int(parts[1]), int(parts[2]))


def append_row(row: Dict[str, str], rows: Optional[List[Dict[str, str]]] = None) -> List[Dict[str, str]]:
    """Appends an engineer record to a list of rows.

    This function avoids mutable default argument bugs by initializing a new list
    if no list is passed.

    Args:
        row: The engineer record dictionary.
        rows: The accumulated list of engineer records.

    Returns:
        The updated list containing the new record.
    """
    if rows is None:
        rows = []
    rows.append(row)
    return rows


def load_engineers(path: str) -> List[Dict[str, str]]:
    """Reads a CSV file of engineers and parses it into a list of records.

    Args:
        path: Path to the input CSV file.

    Returns:
        A list of dictionaries representing the parsed engineers.
    """
    global SKIPPED
    engineers: Optional[List[Dict[str, str]]] = None
    
    with open(path, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        try:
            next(reader)  # Skip header row
        except StopIteration:
            return []  # Empty file
            
        for row in reader:
            try:
                # Ensure the row has enough columns before indexing
                if len(row) < 5:
                    raise IndexError("Malformed row: insufficient columns")
                    
                engineers = append_row({
                    'name': row[0].strip(),
                    'email': row[1].strip(),
                    'team': row[2].strip(),
                    'status': row[3].strip(),
                    'deadline': row[4].strip(),
                }, engineers)
            except Exception:
                SKIPPED += 1
                continue
                
    return engineers or []


def count_by_status(engineers: List[Dict[str, str]]) -> Dict[str, int]:
    """Counts engineers grouped by their normalized training status.

    Only counts statuses matching 'completed', 'pending', or 'in_progress'.

    Args:
        engineers: List of parsed engineer records.

    Returns:
        A dictionary mapping status names to counts.
    """
    counts: Dict[str, int] = {}
    for e in engineers:
        s = e['status'].strip().lower()
        if s in ('completed', 'pending', 'in_progress'):
            counts[s] = counts.get(s, 0) + 1
    return counts


def overdue(engineers: List[Dict[str, str]], today: str = '2026-07-14') -> List[str]:
    """Identifies emails of engineers whose training is overdue.

    Args:
        engineers: List of parsed engineer records.
        today: Reference date string in YYYY-MM-DD or YYYY-M-D format.

    Returns:
        A list of overdue engineers' email addresses.
    """
    result: List[str] = []
    try:
        today_date = parse_date(today)
    except ValueError:
        # Fallback to the default reference date if invalid format provided
        today_date = date(2026, 7, 14)
        
    for e in engineers:
        status_clean = e['status'].strip().lower()
        if status_clean != 'completed':
            try:
                deadline_date = parse_date(e['deadline'])
                if deadline_date < today_date:
                    result.append(e['email'])
            except ValueError:
                # Skip comparison if deadline date is unparseable/invalid
                continue
    return result


def main() -> None:
    """Main execution orchestrator."""
    if len(sys.argv) < 3:
        print("Usage: python report_generator_fixed.py <input.csv> <output.txt>")
        sys.exit(1)
        
    engineers = load_engineers(sys.argv[1])
    counts = count_by_status(engineers)
    late = overdue(engineers)
    
    with open(sys.argv[2], mode='w', encoding='utf-8') as out:
        out.write('WEEKLY TRAINING COMPLIANCE REPORT\n')
        # Maintain order: completed, pending, in_progress
        for status in ('completed', 'pending', 'in_progress'):
            if status in counts:
                out.write(f'{status}: {counts[status]}\n')
            else:
                out.write(f'{status}: 0\n')
                
        out.write(f'skipped rows: {SKIPPED}\n')
        out.write('overdue engineers:\n')
        for email in late:
            out.write(f'  - {email}\n')


if __name__ == '__main__':
    main()
