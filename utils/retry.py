"""Retry with exponential backoff."""
import asyncio
import random
from typing import Awaitable, Callable, TypeVar
import aiohttp

from utils.logging import get_logger

log = get_logger(__name__)

T = TypeVar("T")

RETRYABLE_STATUS = {429, 500, 502, 503, 504}


async def with_retry(
    func: Callable[[], Awaitable[T]],
    *,
    max_attempts: int = 4,
    base_delay: float = 0.5,
    max_delay: float = 8.0,
    label: str = "request",
) -> T:
    last_exc: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            return await func()
        except aiohttp.ClientResponseError as e:
            last_exc = e
            if e.status not in RETRYABLE_STATUS:
                raise
            log.warning(f"{label} HTTP {e.status} (attempt {attempt}/{max_attempts})")
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            last_exc = e
            log.warning(f"{label} network error: {e} (attempt {attempt}/{max_attempts})")

        if attempt == max_attempts:
            break
        delay = min(max_delay, base_delay * (2 ** (attempt - 1)))
        delay += random.uniform(0, 0.3)
        await asyncio.sleep(delay)

    if last_exc:
        raise last_exc
    raise RuntimeError(f"{label} failed with no exception recorded")