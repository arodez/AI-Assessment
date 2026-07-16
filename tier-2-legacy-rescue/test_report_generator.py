"""Tests for report_generator_fixed.py.

These tests verify both correct behavior and the fixes for the four legacy bugs:
- B1: Mutable default argument in append_row
- B2: Case/whitespace sensitivity in status matching
- B3: Date comparisons with non-zero-padded months/days
- B4: Skip counter for malformed rows
"""

import pytest
import os
from report_generator_fixed import (
    append_row,
    load_engineers,
    count_by_status,
    overdue,
    parse_date,
)


def test_append_row_no_accumulation():
    """B1 Fix: Verify append_row does not persist rows across calls with default arguments."""
    row1 = {'name': 'Ana'}
    res1 = append_row(row1)
    assert len(res1) == 1
    assert res1[0] == row1

    row2 = {'name': 'Luis'}
    res2 = append_row(row2)
    # If the bug was present, res2 would have len 2 and contain row1
    assert len(res2) == 1
    assert res2[0] == row2


def test_count_by_status_normalization():
    """B2 Fix: Verify status counting normalizes cases and trailing whitespace."""
    engineers = [
        {'status': 'completed'},
        {'status': 'Pending'},       # Capitalized
        {'status': 'in_progress '},  # Trailing space
        {'status': 'COMPLETED'},     # Uppercase
        {'status': 'unknown'}        # Invalid status should be ignored
    ]
    counts = count_by_status(engineers)
    assert counts.get('completed') == 2
    assert counts.get('pending') == 1
    assert counts.get('in_progress') == 1
    assert 'unknown' not in counts


def test_overdue_non_zero_padded_dates():
    """B3 Fix: Verify date comparison correctly handles non-zero-padded months and days."""
    engineers = [
        {'email': 'luis@example.com', 'status': 'pending', 'deadline': '2026-06-15'},
        {'email': 'jorge@example.com', 'status': 'pending', 'deadline': '2026-5-30'},   # May 30 (non-zero-padded)
        {'email': 'sofia@example.com', 'status': 'pending', 'deadline': '2026-08-01'},  # Aug 1
    ]
    late = overdue(engineers, today='2026-07-14')
    # Luis and Jorge are overdue relative to 2026-07-14.
    # If B3 were present, Jorge (2026-5-30) would be compared lexicographically
    # and evaluated as AFTER 2026-07-14 (since '5' > '0').
    assert 'luis@example.com' in late
    assert 'jorge@example.com' in late
    assert 'sofia@example.com' not in late


def test_load_engineers_skipped_rows(tmp_path):
    """B4 Fix: Verify malformed rows are counted as skipped and don't raise UnboundLocalError."""
    import report_generator_fixed
    report_generator_fixed.SKIPPED = 0

    csv_content = (
        "name,email,team,course_status,deadline\n"
        "Ana Torres,ana.torres@example.com,Platform,completed,2026-06-30\n"
        "Renata Vega,renata.vega@example.com,Mobile\n"  # Malformed (short) row
    )
    p = tmp_path / "test_input.csv"
    p.write_text(csv_content, encoding='utf-8')

    engineers = load_engineers(str(p))
    assert len(engineers) == 1
    assert report_generator_fixed.SKIPPED == 1


def test_load_engineers_empty_file(tmp_path):
    """Verify that an empty input file is handled gracefully and returns empty list."""
    import report_generator_fixed
    report_generator_fixed.SKIPPED = 0

    p = tmp_path / "empty.csv"
    p.write_text("", encoding='utf-8')

    engineers = load_engineers(str(p))
    assert len(engineers) == 0
    assert report_generator_fixed.SKIPPED == 0


def test_parse_date_invalid():
    """Verify parse_date raises ValueError on invalid formats."""
    with pytest.raises(ValueError):
        parse_date("2026-07")
    with pytest.raises(ValueError):
        parse_date("abc")
    with pytest.raises(ValueError):
        parse_date("2026-13-01")  # Invalid month
