import asyncio


async def retry(operation, max_attempts=3, base_delay=0.1, sleep=asyncio.sleep):
    last_error = None
    for retry_index in range(max_attempts + 1):
        try:
            return await operation()
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            last_error = exc
            await sleep(base_delay * (2**retry_index))
    raise last_error
