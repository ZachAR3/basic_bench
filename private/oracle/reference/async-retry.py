import asyncio


async def retry(operation, max_attempts=3, base_delay=0.1, sleep=asyncio.sleep):
    if not isinstance(max_attempts, int) or max_attempts < 1:
        raise ValueError("max_attempts must be a positive integer")
    for attempt in range(max_attempts):
        try:
            return await operation()
        except asyncio.CancelledError:
            raise
        except Exception:
            if attempt == max_attempts - 1:
                raise
            await sleep(base_delay * (2**attempt))
