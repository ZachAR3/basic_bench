import unittest
from datetime import UTC, date, time

from recurrence import DailyRule, expand_daily


class HiddenRecurrenceTests(unittest.TestCase):
    def test_spring_forward_keeps_wall_time_after_transition(self):
        rule = DailyRule(time(9), "America/New_York", 3)
        values = expand_daily(date(2026, 3, 7), rule)
        self.assertEqual([value.hour for value in values], [9, 9, 9])
        self.assertEqual([value.utcoffset().total_seconds() for value in values], [-18000, -14400, -14400])

    def test_nonexistent_time_moves_to_first_valid_minute(self):
        rule = DailyRule(time(2, 30), "America/New_York", 3, gap_policy="forward")
        values = expand_daily(date(2026, 3, 7), rule)
        self.assertEqual([(value.day, value.hour, value.minute) for value in values], [
            (7, 2, 30),
            (8, 3, 0),
            (9, 2, 30),
        ])

    def test_skip_policy_does_not_consume_count(self):
        rule = DailyRule(time(2, 30), "America/New_York", 3, gap_policy="skip")
        values = expand_daily(date(2026, 3, 7), rule)
        self.assertEqual([(value.day, value.hour, value.minute) for value in values], [
            (7, 2, 30),
            (9, 2, 30),
            (10, 2, 30),
        ])

    def test_fall_overlap_policy_selects_distinct_instants(self):
        earliest = expand_daily(
            date(2026, 11, 1),
            DailyRule(time(1, 30), "America/New_York", 1, overlap_policy="earliest"),
        )[0]
        latest = expand_daily(
            date(2026, 11, 1),
            DailyRule(time(1, 30), "America/New_York", 1, overlap_policy="latest"),
        )[0]
        self.assertNotEqual(earliest.astimezone(UTC), latest.astimezone(UTC))
        self.assertLess(earliest.astimezone(UTC), latest.astimezone(UTC))

    def test_half_hour_dst_transition(self):
        rule = DailyRule(time(8, 15), "Australia/Lord_Howe", 3)
        values = expand_daily(date(2026, 10, 3), rule)
        self.assertEqual([(value.hour, value.minute) for value in values], [(8, 15)] * 3)
        self.assertNotEqual(values[0].utcoffset(), values[1].utcoffset())

    def test_results_retain_requested_timezone(self):
        values = expand_daily(date(2026, 3, 28), DailyRule(time(12), "Europe/Paris", 3))
        self.assertTrue(all(value.tzinfo.key == "Europe/Paris" for value in values))
