import sys
import csv
from datetime import datetime
from typing import List, Dict, Optional

class EngineerList(list):
    """A custom list subclass to hold metadata such as skipped row count without using global mutable state."""
    def __init__(self, *args, skipped_count: int = 0, **kwargs):
        super().__init__(*args, **kwargs)
        self.skipped_count = skipped_count

def append_row(row: Dict[str, str], rows: Optional[List[Dict[str, str]]] = None) -> List[Dict[str, str]]:
    """Appends an engineer record to the provided list or initializes a new list if None.
    
    Args:
        row: A dictionary containing engineer details.
        rows: An optional list of engineer records.
        
    Returns:
        The updated list containing the new record.
    """
    if rows is None:
        rows = []
    rows.append(row)
    return rows

def normalize_date(date_str: str) -> str:
    """Parses and normalizes a date string into YYYY-MM-DD format to ensure correct lexicographical comparison.
    
    Args:
        date_str: The raw date string.
        
    Returns:
        A zero-padded, formatted date string (YYYY-MM-DD).
        
    Raises:
        ValueError: If the date cannot be parsed.
    """
    cleaned = date_str.strip()
    for fmt in ('%Y-%m-%d', '%Y/%m/%d', '%Y-%m-%j'):
        try:
            dt = datetime.strptime(cleaned, fmt)
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            continue
    # Try parsing flexible parts (e.g. YYYY-M-D)
    parts = cleaned.split('-')
    if len(parts) == 3:
        try:
            dt = datetime(int(parts[0]), int(parts[1]), int(parts[2]))
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            pass
    parts = cleaned.split('/')
    if len(parts) == 3:
        try:
            dt = datetime(int(parts[0]), int(parts[1]), int(parts[2]))
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            pass
    raise ValueError(f"Unsupported date format: {date_str}")

def load_engineers(path: str) -> EngineerList:
    """Loads and parses engineer compliance records from a CSV file.
    
    Args:
        path: Path to the input CSV file.
        
    Returns:
        An EngineerList containing parsed and validated engineer dictionaries.
    """
    engineers = None
    skipped = 0
    try:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            try:
                next(reader)
            except StopIteration:
                return EngineerList([], skipped_count=0)
            
            for row in reader:
                try:
                    if len(row) < 5:
                        raise ValueError("Row contains insufficient columns.")
                    
                    normalized_status = row[3].strip().lower()
                    normalized_deadline = normalize_date(row[4])
                    
                    engineers = append_row({
                        'name': row[0].strip(),
                        'email': row[1].strip(),
                        'team': row[2].strip(),
                        'status': normalized_status,
                        'deadline': normalized_deadline,
                    }, engineers)
                except Exception:
                    skipped += 1
    except FileNotFoundError:
        return EngineerList([], skipped_count=0)
        
    return EngineerList(engineers or [], skipped_count=skipped)

def count_by_status(engineers: List[Dict[str, str]]) -> Dict[str, int]:
    """Counts the number of engineers in each training status.
    
    Args:
        engineers: A list of engineer record dictionaries.
        
    Returns:
        A dictionary mapping status names to their respective counts.
    """
    counts: Dict[str, int] = {}
    for e in engineers:
        s = e['status']
        if s == 'completed':
            counts['completed'] = counts.get('completed', 0) + 1
        elif s == 'pending':
            counts['pending'] = counts.get('pending', 0) + 1
        elif s == 'in_progress':
            counts['in_progress'] = counts.get('in_progress', 0) + 1
    return counts

def overdue(engineers: List[Dict[str, str]], today: str = '2026-07-14') -> List[str]:
    """Identifies emails of engineers with overdue training deadlines.
    
    Args:
        engineers: A list of engineer record dictionaries.
        today: Reference ISO date string (YYYY-MM-DD).
        
    Returns:
        A list of overdue engineer emails.
    """
    result: List[str] = []
    try:
        normalized_today = normalize_date(today)
    except ValueError:
        normalized_today = today
        
    for e in engineers:
        if e['status'] != 'completed' and e['deadline'] < normalized_today:
            result.append(e['email'])
    return result

def main() -> None:
    """Main orchestration function to run the compliance report generator."""
    if len(sys.argv) < 3:
        print("Usage: python report_generator_fixed.py <input_csv> <output_txt>")
        sys.exit(1)
        
    engineers = load_engineers(sys.argv[1])
    counts = count_by_status(engineers)
    late = overdue(engineers)
    skipped = getattr(engineers, 'skipped_count', 0)
    
    with open(sys.argv[2], 'w', encoding='utf-8') as out:
        out.write('WEEKLY TRAINING COMPLIANCE REPORT\n')
        for status, n in counts.items():
            out.write(f'{status}: {n}\n')
        out.write(f'skipped rows: {skipped}\n')
        out.write('overdue engineers:\n')
        for email in late:
            out.write(f'  - {email}\n')

if __name__ == '__main__':
    main()
