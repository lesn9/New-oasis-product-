"""Shared aiohttp session."""
from typing import Optional
import aiohttp

from config import get_config
from utils.logging import get_logger

log = get_logger(__name__)

_session: Optional[aiohttp.ClientSession] = None


async def get_session() -> aiohttp.ClientSession:
    global _session
    if _session is None or _session.closed:
        cfg = get_config()
        timeout = aiohttp.ClientTimeout(total=cfg.http_timeout_seconds)
        connector = aiohttp.TCPConnector(limit=cfg.max_concurrent_requests, ttl_dns_cache=300)
        _session = aiohttp.ClientSession(timeout=timeout, connector=connector)
    return _session


async def close_session() -> None:
    global _session
    if _session and not _session.closed:
        await _session.close()
        _session = None


async def get_json(url: str, *, params: dict | None = None, headers: dict | None = None):
    session = await get_session()
    async with session.get(url, params=params, headers=headers) as resp:
        resp.raise_for_status()
        return await resp.json()


async def post_json(url: str, *, json: dict | None = None, headers: dict | None = None):
    session = await get_session()
    async with session.post(url, json=json, headers=headers) as resp:
        resp.raise_for_status()
        return await resp.json()
