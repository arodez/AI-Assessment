"""Tests for report_generator_fixed.py — each targets one planted bug fix.

These are written against report_generator_fixed; swapping the import to the
original report_generator reproduces the corresponding bug as a test failure.
"""

import csv
import os

import pytest

from report_generator_fixed import count_by_status, load_engineers, overdue

SAMPLE_CSV = os.path.join(os.path.dirname(__file__), '..', 'data', 'sample_input.csv')


def write_csv(path, rows):
    with open(path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['name', 'email', 'team', 'status', 'deadline'])
        writer.writerows(rows)


# Bug 1: mutable default argument leaking state across calls.
def test_load_engineers_is_isolated_across_repeated_calls(tmp_path):
    path = tmp_path / 'input.csv'
    write_csv(path, [['Ana', 'ana@example.com', 'Platform', 'completed', '2026-01-01']])

    first, _ = load_engineers(str(path))
    second, _ = load_engineers(str(path))

    assert len(first) == 1
    assert len(second) == 1


# Bug 2: skip counter never incremented for malformed rows.
def test_load_engineers_counts_skipped_rows(tmp_path):
    path = tmp_path / 'input.csv'
    write_csv(path, [
        ['Ana', 'ana@example.com', 'Platform', 'completed', '2026-01-01'],
        ['Incomplete', 'incomplete@example.com', 'Mobile'],
    ])

    engineers, skipped = load_engineers(str(path))

    assert len(engineers) == 1
    assert skipped == 1


# Bug 3: status counting is case/whitespace sensitive.
def test_count_by_status_normalizes_case_and_whitespace():
    engineers = [
        {'name': 'A', 'email': 'a@x.com', 'team': 't', 'status': 'Pending', 'deadline': '2026-01-01'},
        {'name': 'B', 'email': 'b@x.com', 'team': 't', 'status': 'in_progress ', 'deadline': '2026-01-01'},
        {'name': 'C', 'email': 'c@x.com', 'team': 't', 'status': 'completed', 'deadline': '2026-01-01'},
    ]

    counts = count_by_status(engineers)

    assert counts == {'pending': 1, 'in_progress': 1, 'completed': 1}


# Bug 4: overdue comparison done as raw strings, breaks on non-zero-padded dates.
def test_overdue_flags_non_zero_padded_date_as_late():
    engineers = [
        {'name': 'Jorge', 'email': 'jorge@example.com', 'team': 'Mobile', 'status': 'pending', 'deadline': '2026-5-30'},
    ]

    late = overdue(engineers, today='2026-07-14')

    assert late == ['jorge@example.com']


def test_overdue_excludes_completed_and_future_deadlines():
    engineers = [
        {'name': 'Done', 'email': 'done@example.com', 'team': 't', 'status': 'completed', 'deadline': '2020-01-01'},
        {'name': 'Future', 'email': 'future@example.com', 'team': 't', 'status': 'pending', 'deadline': '2099-01-01'},
    ]

    late = overdue(engineers, today='2026-07-14')

    assert late == []


# End-to-end test against the provided sample data.
def test_end_to_end_sample_input_matches_expected_report():
    engineers, skipped = load_engineers(SAMPLE_CSV)
    counts = count_by_status(engineers)
    late = overdue(engineers)

    assert skipped == 1
    assert counts == {'completed': 3, 'pending': 3, 'in_progress': 2}
    assert late == [
        'luis.mendoza@example.com',
        'diego.fuentes@example.com',
        'jorge.salinas@example.com',
        'valeria.nunez@example.com',
    ]


if __name__ == '__main__':
    raise SystemExit(pytest.main([__file__, '-v']))
