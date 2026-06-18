import csv
import io
import unittest
from csv_utils import rows_to_csv


class HiddenCsvTests(unittest.TestCase):
    def roundtrip(self, rows):
        text = rows_to_csv(rows)
        return list(csv.reader(io.StringIO(text)))

    def test_quotes_newline_unicode_and_none(self):
        rows = [["héllo", 'a"b', "x\ny", None]]
        self.assertEqual(self.roundtrip(rows), [["héllo", 'a"b', "x\ny", ""]])

    def test_empty(self):
        self.assertEqual(rows_to_csv([]), "")

    def test_unix_newlines(self):
        self.assertNotIn("\r\n", rows_to_csv([["x"], ["y"]]))

    def test_carriage_returns_and_leading_spaces(self):
        rows = [[" a", "b\rc", "d\r\ne", "tail "]]
        self.assertEqual(self.roundtrip(rows), rows)

    def test_many_round_trip_shapes(self):
        atoms = ["", ",", '"', "\n", "é", "🙂", "a,b", 'a"b', "a\nb", None, 0, False]
        for width in range(1, 6):
            row = [atoms[(width * 3 + index) % len(atoms)] for index in range(width)]
            expected = [["" if value is None else str(value) for value in row]]
            self.assertEqual(self.roundtrip([row]), expected)

    def test_quote_followed_by_comma(self):
        self.assertEqual(self.roundtrip([['x",y', "z"]]), [['x",y', "z"]])
