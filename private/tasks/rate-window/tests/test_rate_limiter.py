import unittest
from rate_limiter import SlidingWindowLimiter


class RateTests(unittest.TestCase):
    def test_limit(self):
        limiter = SlidingWindowLimiter(2, 10)
        self.assertTrue(limiter.allow(1))
        self.assertTrue(limiter.allow(2))
        self.assertFalse(limiter.allow(3))

    def test_old_events_expire(self):
        limiter = SlidingWindowLimiter(1, 5)
        self.assertTrue(limiter.allow(0))
        self.assertTrue(limiter.allow(6))


if __name__ == "__main__":
    unittest.main()
