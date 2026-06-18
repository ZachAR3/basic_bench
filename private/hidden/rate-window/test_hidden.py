import unittest
from collections import deque
from random import Random
from rate_limiter import SlidingWindowLimiter


class HiddenRateTests(unittest.TestCase):
    def test_exact_boundary_expires(self):
        limiter = SlidingWindowLimiter(1, 10)
        self.assertTrue(limiter.allow(5))
        self.assertTrue(limiter.allow(15))

    def test_rejection_does_not_consume_capacity(self):
        limiter = SlidingWindowLimiter(1, 10)
        self.assertTrue(limiter.allow(0))
        self.assertFalse(limiter.allow(1))
        self.assertTrue(limiter.allow(10))

    def test_repeated_rejections_do_not_extend_block(self):
        limiter = SlidingWindowLimiter(2, 5)
        self.assertTrue(limiter.allow(0))
        self.assertTrue(limiter.allow(0.5))
        for now in (1, 2, 3, 4, 4.999):
            self.assertFalse(limiter.allow(now))
        self.assertTrue(limiter.allow(5))
        self.assertTrue(limiter.allow(5.5))

    def test_randomized_reference_model(self):
        random = Random(417)
        limiter = SlidingWindowLimiter(5, 3.5)
        accepted = deque()
        now = 0.0
        for _ in range(500):
            now += random.random() * 0.7
            cutoff = now - 3.5
            while accepted and accepted[0] <= cutoff:
                accepted.popleft()
            expected = len(accepted) < 5
            if expected:
                accepted.append(now)
            self.assertEqual(limiter.allow(now), expected)

    def test_fractional_exact_boundary(self):
        limiter = SlidingWindowLimiter(1, 0.25)
        self.assertTrue(limiter.allow(10.0))
        self.assertTrue(limiter.allow(10.25))
