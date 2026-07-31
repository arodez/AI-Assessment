"""
Unit tests for solution.py

Covers:
    - Missing input file
    - Empty CSV file
    - Invalid / missing column headers
    - Missing data (empty name, email, status)
    - Invalid email format
    - All-whitespace rows (e.g. ', , ') are skipped with a warning
    - Happy path (correct data + pending emails)
"""

import os
import sys
import tempfile
import textwrap
import unittest
from collections import Counter

# Ensure the parent directory is on the path so we can import solution
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from solution import process_csv, validate_email, write_pending


class TestValidateEmail(unittest.TestCase):
    """Unit tests for the validate_email helper."""

    def test_valid_email(self):
        self.assertTrue(validate_email("user@example.com"))

    def test_valid_email_subdomain(self):
        self.assertTrue(validate_email("user@mail.example.org"))

    def test_invalid_email_no_at(self):
        self.assertFalse(validate_email("userexample.com"))

    def test_invalid_email_no_domain(self):
        self.assertFalse(validate_email("user@"))

    def test_invalid_email_no_tld(self):
        self.assertFalse(validate_email("user@domain"))

    def test_invalid_email_spaces(self):
        self.assertFalse(validate_email("user @example.com"))

    def test_empty_email(self):
        self.assertFalse(validate_email(""))


class TestProcessCSVMissingFile(unittest.TestCase):
    """process_csv raises FileNotFoundError when the file does not exist."""

    def test_missing_file(self):
        with self.assertRaises(FileNotFoundError) as ctx:
            process_csv("/nonexistent/path/engineers.csv")
        self.assertIn("not found", str(ctx.exception))


class TestProcessCSVEmptyFile(unittest.TestCase):
    """process_csv raises ValueError when the CSV file is completely empty."""

    def test_empty_file(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            tmp_path = f.name  # write nothing

        try:
            with self.assertRaises(ValueError) as ctx:
                process_csv(tmp_path)
            self.assertIn("empty", str(ctx.exception).lower())
        finally:
            os.unlink(tmp_path)


class TestProcessCSVInvalidColumns(unittest.TestCase):
    """process_csv raises ValueError for wrong or missing column headers."""

    def _write_tmp(self, content):
        f = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        f.write(textwrap.dedent(content))
        f.close()
        return f.name

    def test_completely_wrong_headers(self):
        path = self._write_tmp("""\
            id,address,status
            1,somewhere,done
        """)
        try:
            with self.assertRaises(ValueError) as ctx:
                process_csv(path)
            self.assertIn("Missing required column", str(ctx.exception))
        finally:
            os.unlink(path)

    def test_missing_one_column(self):
        # 'course_status' is absent
        path = self._write_tmp("""\
            name,email
            Ana,ana@example.com
        """)
        try:
            with self.assertRaises(ValueError) as ctx:
                process_csv(path)
            self.assertIn("course_status", str(ctx.exception))
        finally:
            os.unlink(path)


class TestProcessCSVMissingData(unittest.TestCase):
    """Rows with empty name, email, or status are skipped gracefully."""

    def _write_tmp(self, content):
        f = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        f.write(textwrap.dedent(content))
        f.close()
        return f.name

    def test_empty_name_is_skipped(self):
        path = self._write_tmp("""\
            name,email,course_status
            ,noname@example.com,pending
            Ana,ana@example.com,completed
        """)
        try:
            counts, pending = process_csv(path)
            self.assertEqual(counts['completed'], 1)
            self.assertNotIn('noname@example.com', pending)
        finally:
            os.unlink(path)

    def test_empty_status_is_skipped(self):
        path = self._write_tmp("""\
            name,email,course_status
            Ana,ana@example.com,
            Luis,luis@example.com,pending
        """)
        try:
            counts, pending = process_csv(path)
            self.assertEqual(counts['pending'], 1)
            self.assertEqual(len(pending), 1)
        finally:
            os.unlink(path)

    def test_too_few_columns_is_skipped(self):
        path = self._write_tmp("""\
            name,email,course_status
            Ana,ana@example.com
            Luis,luis@example.com,pending
        """)
        try:
            counts, pending = process_csv(path)
            # Only the valid row counts
            self.assertEqual(counts['pending'], 1)
        finally:
            os.unlink(path)


class TestProcessCSVInvalidEmail(unittest.TestCase):
    """Rows with an invalid email address are skipped."""

    def test_invalid_email_row_skipped(self):
        content = textwrap.dedent("""\
            name,email,course_status
            Bad User,not-an-email,pending
            Good User,good@example.com,pending
        """)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(content)
            tmp_path = f.name

        try:
            counts, pending = process_csv(tmp_path)
            self.assertNotIn('not-an-email', pending)
            self.assertIn('good@example.com', pending)
            self.assertEqual(counts['pending'], 1)
        finally:
            os.unlink(tmp_path)


class TestProcessCSVHappyPath(unittest.TestCase):
    """Full happy-path test with a well-formed CSV."""

    def test_correct_counts_and_pending_list(self):
        content = textwrap.dedent("""\
            name,email,course_status
            Ana Torres,ana@example.com,completed
            Luis Mendoza,luis@example.com,pending
            Sofia Reyes,sofia@example.com,in_progress
            Diego Fuentes,diego@example.com,pending
        """)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(content)
            tmp_path = f.name

        try:
            counts, pending = process_csv(tmp_path)
            self.assertEqual(counts['completed'], 1)
            self.assertEqual(counts['pending'], 2)
            self.assertEqual(counts['in_progress'], 1)
            self.assertIn('luis@example.com', pending)
            self.assertIn('diego@example.com', pending)
        finally:
            os.unlink(tmp_path)


class TestWritePending(unittest.TestCase):
    """write_pending writes one email per line to the output file."""

    def test_writes_emails(self):
        emails = ['a@example.com', 'b@example.com']
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            tmp_path = f.name

        try:
            write_pending(emails, tmp_path)
            with open(tmp_path) as f:
                lines = [l.strip() for l in f.readlines()]
            self.assertEqual(lines, emails)
        finally:
            os.unlink(tmp_path)

    def test_empty_list_creates_empty_file(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            tmp_path = f.name

        try:
            write_pending([], tmp_path)
            self.assertEqual(os.path.getsize(tmp_path), 0)
        finally:
            os.unlink(tmp_path)


class TestProcessCSVExtraColumns(unittest.TestCase):
    """
    Extra non-required columns in the header or trailing extra values in
    data rows must be silently ignored. Only rows that are genuinely missing
    a required column should be skipped.
    """

    def _write_tmp(self, content):
        f = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        f.write(textwrap.dedent(content))
        f.close()
        return f.name

    def test_extra_trailing_column_in_header_row_is_ignored(self):
        """Header has an extra column at the end; rows without that column are still valid."""
        path = self._write_tmp("""\
            name,email,course_status,department
            Ana,ana@example.com,completed,Engineering
            Luis,luis@example.com,pending,Design
            Sofia,sofia@example.com,in_progress
        """)
        try:
            counts, pending = process_csv(path)
            self.assertEqual(counts['completed'], 1)
            self.assertEqual(counts['pending'], 1)
            self.assertEqual(counts['in_progress'], 1)
            self.assertIn('luis@example.com', pending)
        finally:
            os.unlink(path)

    def test_extra_trailing_values_in_data_rows_are_ignored(self):
        """Data rows with extra columns beyond the required ones are processed correctly."""
        path = self._write_tmp("""\
            name,email,course_status
            Ana,ana@example.com,completed,extra1,extra2
            Luis,luis@example.com,pending,extra3
        """)
        try:
            counts, pending = process_csv(path)
            self.assertEqual(counts['completed'], 1)
            self.assertEqual(counts['pending'], 1)
        finally:
            os.unlink(path)

    def test_non_required_column_between_required_ones_shifts_index(self):
        """
        When a non-required column is inserted BETWEEN required ones
        (e.g. name,email,misc,course_status), rows that supply all four
        columns are accepted; rows that lack the required course_status
        position are skipped with a specific message.
        """
        path = self._write_tmp("""\
            name,email,misc,course_status
            Ana,ana@example.com,some_misc,completed
            Luis,luis@example.com,other,pending
            Bad,bad@example.com
        """)
        try:
            counts, pending = process_csv(path)
            # Ana and Luis have all four columns → both counted
            self.assertEqual(counts['completed'], 1)
            self.assertEqual(counts['pending'], 1)
            self.assertIn('luis@example.com', pending)
            # Bad row has only 2 columns → skipped
            self.assertEqual(sum(counts.values()), 2)
        finally:
            os.unlink(path)

    def test_missing_required_column_in_row_shows_column_name(self):
        """The skip message names the specific missing required column(s)."""
        import io
        # Header: name(0), email(1), misc(2), course_status(3)
        # Row 'Ana,ana@example.com,some_misc' has 3 columns → missing only 'course_status' at idx 3
        path = self._write_tmp("""\
            name,email,misc,course_status
            Ana,ana@example.com,some_misc
        """)
        try:
            captured = io.StringIO()
            sys.stderr = captured
            try:
                process_csv(path)
            finally:
                sys.stderr = sys.__stderr__

            warning = captured.getvalue()
            self.assertIn("'course_status'", warning)
            # email is at index 1 — present in the row — must NOT appear in the warning
            self.assertNotIn("'email'", warning)
        finally:
            os.unlink(path)



class TestProcessCSVWhitespaceOnlyRow(unittest.TestCase):
    """
    A row like ', , ' is parsed by the CSV reader as a non-empty list
    of whitespace-only strings. Previously it was silently skipped;
    now it must emit a warning and not contribute to counts or pending.
    """

    def _write_tmp(self, content):
        f = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        f.write(textwrap.dedent(content))
        f.close()
        return f.name

    def test_whitespace_only_row_is_skipped_not_counted(self):
        """A row of only commas/spaces must not appear in status_counts."""
        path = self._write_tmp("""\
            name,email,course_status
            Ana,ana@example.com,completed
            , , 
            Luis,luis@example.com,pending
        """)
        try:
            counts, pending = process_csv(path)
            # Only the two valid rows should count
            self.assertEqual(sum(counts.values()), 2)
            self.assertEqual(counts['completed'], 1)
            self.assertEqual(counts['pending'], 1)
        finally:
            os.unlink(path)

    def test_whitespace_only_row_prints_warning(self):
        """A row of only commas/spaces must print a warning to stderr."""
        import io
        path = self._write_tmp("""\
            name,email,course_status
            , , 
            Ana,ana@example.com,completed
        """)
        try:
            # Capture stderr to verify warning message
            captured = io.StringIO()
            sys.stderr = captured
            try:
                process_csv(path)
            finally:
                sys.stderr = sys.__stderr__

            warning = captured.getvalue()
            self.assertIn("All fields are empty or whitespace-only", warning)
        finally:
            os.unlink(path)

    def test_only_whitespace_rows_yields_empty_counts(self):
        """A CSV with only whitespace rows (no valid data) returns empty counts."""
        path = self._write_tmp("""\
            name,email,course_status
            , , 
            ,  ,
        """)
        try:
            counts, pending = process_csv(path)
            self.assertEqual(len(counts), 0)
            self.assertEqual(pending, [])
        finally:
            os.unlink(path)



if __name__ == '__main__':
    unittest.main(verbosity=2)
