"""Simple TTL cache with async lock."""
import asyncio
from typing import Any, Callable, Hashable, Optional
from cachetools import TTLCache


class AsyncTTLCache:
    def __init__(self, maxsize: int = 1000, ttl: int = 300):
        self._cache: TTLCache = TTLCache(maxsize=maxsize, ttl=ttl)
        self._lock = asyncio.Lock()

    async def get(self, key: Hashable) -> Optional[Any]:
        async with self._lock:
            return self._cache.get(key)

    async def set(self, key: Hashable, value: Any) -> None:
        async with self._lock:
            self._cache[key] = value

    async def get_or_set(self, key: Hashable, factory: Callable) -> Any:
        cached = await self.get(key)
        if cached is not None:
            return cached
        value = await factory()
        await self.set(key, value)
        return value


token_cache = AsyncTTLCache(maxsize=2000, ttl=300)
market_cache = AsyncTTLCache(maxsize=2000, ttl=120)
rpc_cache = AsyncTTLCache(maxsize=4000, ttl=60)