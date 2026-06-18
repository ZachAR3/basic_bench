import unittest
from datetime import date, time

from recurrence import DailyRule, expand_daily


class RecurrenceTests(unittest.TestCase):
    def test_utc_daily(self):
        rule = DailyRule(time(9, 30), "UTC", 3)
        values = expand_daily(date(2026, 1, 5), rule)
        self.assertEqual([value.isoformat() for value in values], [
            "2026-01-05T09:30:00+00:00",
            "2026-01-06T09:30:00+00:00",
            "2026-01-07T09:30:00+00:00",
        ])

    def test_regular_new_york_week(self):
        rule = DailyRule(time(18, 0), "America/New_York", 2)
        values = expand_daily(date(2026, 1, 10), rule)
        self.assertEqual([(value.hour, value.minute) for value in values], [(18, 0), (18, 0)])

    def test_rule_validation(self):
        with self.assertRaises(ValueError):
            DailyRule(time(9), "UTC", 0)


if __name__ == "__main__":
    unittest.main()
