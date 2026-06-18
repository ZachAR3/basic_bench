import unittest
from csv_utils import rows_to_csv


class CsvTests(unittest.TestCase):
    def test_basic_rows(self):
        self.assertEqual(rows_to_csv([[1, 2], [3, 4]]), "1,2\n3,4\n")

    def test_comma(self):
        self.assertEqual(rows_to_csv([["a,b", "c"]]), '"a,b",c\n')


if __name__ == "__main__":
    unittest.main()
