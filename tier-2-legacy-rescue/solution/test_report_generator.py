import os
import tempfile
import unittest
from solution import report_generator_fixed

class TestReportGenerator(unittest.TestCase):
    """Test suite for validating fixes and correctness of report_generator_fixed.py."""

    def setUp(self):
        self.temp_files = []

    def tearDown(self):
        for path in self.temp_files:
            try:
                os.remove(path)
            except OSError:
                pass

    def create_temp_csv(self, content: str) -> str:
        """Helper to create temporary CSV files."""
        fd, path = tempfile.mkstemp(suffix=".csv")
        with os.fdopen(fd, 'w', newline='', encoding='utf-8') as f:
            f.write(content)
        self.temp_files.append(path)
        return path

    def test_mutable_default_argument_accumulation(self):
        """Test that consecutive loads do not accumulate records across calls (Bug 1)."""
        csv1 = self.create_temp_csv("name,email,team,status,deadline\nAlice,alice@eg.com,A,completed,2026-07-10\n")
        csv2 = self.create_temp_csv("name,email,team,status,deadline\nBob,bob@eg.com,B,completed,2026-07-12\n")
        
        engineers1 = report_generator_fixed.load_engineers(csv1)
        engineers2 = report_generator_fixed.load_engineers(csv2)
        
        self.assertEqual(len(engineers1), 1)
        self.assertEqual(engineers1[0]['name'], 'Alice')
        
        # In the buggy implementation, len(engineers2) would be 2 containing both Alice and Bob.
        self.assertEqual(len(engineers2), 1)
        self.assertEqual(engineers2[0]['name'], 'Bob')

    def test_skipped_counter_unreachable_code(self):
        """Test that malformed rows are skipped and correctly increment the skipped count (Bug 2)."""
        csv_content = (
            "name,email,team,status,deadline\n"
            "Alice,alice@eg.com,A,completed,2026-07-10\n"
            "MalformedRowWithFewColumns\n"
            "Bob,bob@eg.com,B,completed,2026-07-12\n"
        )
        csv_path = self.create_temp_csv(csv_content)
        engineers = report_generator_fixed.load_engineers(csv_path)
        
        self.assertEqual(len(engineers), 2)
        # In the buggy implementation, skipped_count would be 0
        self.assertEqual(getattr(engineers, 'skipped_count', 0), 1)

    def test_empty_file_stop_iteration(self):
        """Test that loading an empty file does not raise a StopIteration exception (Bug 3)."""
        empty_csv = self.create_temp_csv("")
        
        # In the buggy implementation, this would raise StopIteration
        try:
            engineers = report_generator_fixed.load_engineers(empty_csv)
        except StopIteration:
            self.fail("StopIteration raised on empty CSV file")
            
        self.assertEqual(len(engineers), 0)
        self.assertEqual(getattr(engineers, 'skipped_count', 0), 0)

    def test_date_lexicographical_comparison(self):
        """Test that unpadded or flexible dates are compared correctly as chronological dates (Bug 4)."""
        engineers = [
            {'name': 'Alice', 'email': 'alice@eg.com', 'team': 'A', 'status': 'pending', 'deadline': '2026-5-30'},
            {'name': 'Bob', 'email': 'bob@eg.com', 'team': 'B', 'status': 'pending', 'deadline': '2026-07-15'}
        ]
        # Normalize deadlines to zero-padded strings to match report_generator_fixed behavior
        normalized_engineers = []
        for e in engineers:
            normalized_e = e.copy()
            normalized_e['deadline'] = report_generator_fixed.normalize_date(e['deadline'])
            normalized_engineers.append(normalized_e)
            
        late = report_generator_fixed.overdue(normalized_engineers, today='2026-07-14')
        
        # Alice should be overdue since 2026-05-30 is before 2026-07-14.
        self.assertIn('alice@eg.com', late)
        self.assertNotIn('bob@eg.com', late)

    def test_status_case_and_whitespace_normalization(self):
        """Test that statuses with leading/trailing spaces or capitalized letters are normalized and counted (Bug 5)."""
        csv_content = (
            "name,email,team,status,deadline\n"
            "Alice,alice@eg.com,A,completed ,2026-07-10\n"
            "Bob,bob@eg.com,B,Pending,2026-07-12\n"
            "Charlie,charlie@eg.com,C,in_progress,2026-07-14\n"
        )
        csv_path = self.create_temp_csv(csv_content)
        engineers = report_generator_fixed.load_engineers(csv_path)
        counts = report_generator_fixed.count_by_status(engineers)
        
        # In the buggy implementation, counts would be: {'in_progress': 1}
        self.assertEqual(counts.get('completed'), 1)
        self.assertEqual(counts.get('pending'), 1)
        self.assertEqual(counts.get('in_progress'), 1)

if __name__ == '__main__':
    unittest.main()
