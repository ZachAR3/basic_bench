import asyncio
import unittest
from retry import retry


class HiddenRetryTests(unittest.IsolatedAsyncioTestCase):
    async def test_exact_attempt_count_and_delays(self):
        attempts = 0
        delays = []

        async def operation():
            nonlocal attempts
            attempts += 1
            raise LookupError("failed")

        async def sleep(delay):
            delays.append(delay)

        with self.assertRaises(LookupError):
            await retry(operation, max_attempts=3, base_delay=0.5, sleep=sleep)
        self.assertEqual(attempts, 3)
        self.assertEqual(delays, [0.5, 1.0])

    async def test_invalid_attempts(self):
        async def operation():
            return 1

        with self.assertRaises(ValueError):
            await retry(operation, max_attempts=0)

    async def test_cancellation_not_retried(self):
        attempts = 0

        async def operation():
            nonlocal attempts
            attempts += 1
            raise asyncio.CancelledError()

        with self.assertRaises(asyncio.CancelledError):
            await retry(operation)
        self.assertEqual(attempts, 1)

    async def test_success_never_sleeps(self):
        delays = []

        async def operation():
            return 42

        async def sleep(delay):
            delays.append(delay)

        self.assertEqual(await retry(operation, sleep=sleep), 42)
        self.assertEqual(delays, [])

    async def test_success_on_last_attempt_has_only_prior_delays(self):
        attempts = 0
        delays = []

        async def operation():
            nonlocal attempts
            attempts += 1
            if attempts < 4:
                raise OSError("transient")
            return "done"

        async def sleep(delay):
            delays.append(delay)

        result = await retry(operation, max_attempts=4, base_delay=0.25, sleep=sleep)
        self.assertEqual(result, "done")
        self.assertEqual(delays, [0.25, 0.5, 1.0])

    async def test_original_final_exception_is_raised(self):
        errors = [ValueError("first"), RuntimeError("second")]

        async def operation():
            raise errors.pop(0)

        async def sleep(_):
            pass

        with self.assertRaisesRegex(RuntimeError, "second"):
            await retry(operation, max_attempts=2, sleep=sleep)
