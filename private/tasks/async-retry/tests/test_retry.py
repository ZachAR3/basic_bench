import asyncio
import unittest
from retry import retry


class RetryTests(unittest.IsolatedAsyncioTestCase):
    async def test_eventual_success(self):
        attempts = 0

        async def operation():
            nonlocal attempts
            attempts += 1
            if attempts < 2:
                raise RuntimeError("no")
            return "ok"

        delays = []
        result = await retry(operation, max_attempts=3, sleep=lambda d: capture(delays, d))
        self.assertEqual(result, "ok")
        self.assertEqual(attempts, 2)


async def capture(values, value):
    values.append(value)


if __name__ == "__main__":
    unittest.main()
