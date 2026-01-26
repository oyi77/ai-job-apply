"""In-memory TTL cache used by analytics endpoints.

This cache is process-local (per backend worker). It intentionally does not
persist across restarts and does not share state across multiple workers.
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class _CacheEntry:
    value: Any
    expires_at: float

    def is_expired(self, now: float) -> bool:
        return now >= self.expires_at


class AnalyticsCacheService:
    """Simple in-memory TTL cache for aggregated analytics results."""

    def __init__(self) -> None:
        self._cache: Dict[str, _CacheEntry] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[Any]:
        """Get cached value if present and not expired."""
        now = time.monotonic()
        async with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return None
            if entry.is_expired(now):
                self._cache.pop(key, None)
                return None
            return entry.value

    async def set(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        """Store value with TTL (seconds)."""
        expires_at = time.monotonic() + max(ttl_seconds, 0)
        async with self._lock:
            self._cache[key] = _CacheEntry(value=value, expires_at=expires_at)

    async def delete(self, key: str) -> None:
        """Remove a cached value."""
        async with self._lock:
            self._cache.pop(key, None)

    async def clear(self) -> None:
        """Clear all cached values."""
        async with self._lock:
            self._cache.clear()

    async def cleanup(self) -> int:
        """Remove expired entries.

        Returns:
            Number of removed entries.
        """
        now = time.monotonic()
        async with self._lock:
            expired_keys = [k for k, v in self._cache.items() if v.is_expired(now)]
            for key in expired_keys:
                self._cache.pop(key, None)
            return len(expired_keys)

    async def invalidate_user(self, user_id: str) -> int:
        """Invalidate all analytics cache entries for a user.

        Returns:
            Number of removed entries.
        """
        prefix = f"analytics:{user_id}:"
        async with self._lock:
            keys = [k for k in self._cache.keys() if k.startswith(prefix)]
            for key in keys:
                self._cache.pop(key, None)
            return len(keys)


# Process-wide singleton used by API routers/services.
analytics_cache_service = AnalyticsCacheService()
