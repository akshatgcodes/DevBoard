import time
from collections.abc import Awaitable, Callable
from typing import Any

from app.config import settings

_store: dict[str, tuple[float, Any]] = {}


async def cached(key: str, fetch: Callable[[], Awaitable[Any]]) -> Any:
    """Small in-process TTL cache so a dashboard refresh doesn't hammer public APIs."""
    hit = _store.get(key)
    if hit and time.monotonic() - hit[0] < settings.cache_ttl:
        return hit[1]
    value = await fetch()
    _store[key] = (time.monotonic(), value)
    return value


def clear() -> None:
    _store.clear()
