"""Simple in-memory cache for query results."""

from typing import Any, Optional, Dict
from datetime import datetime, timedelta
from threading import Lock
import hashlib
import json


class SimpleCache:
    """Simple thread-safe in-memory cache with TTL support."""
    
    def __init__(self, default_ttl: int = 300):
        """
        Initialize cache.
        
        Args:
            default_ttl: Default time-to-live in seconds (default: 5 minutes)
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = Lock()
        self.default_ttl = default_ttl
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from arguments."""
        key_data = {
            "prefix": prefix,
            "args": args,
            "kwargs": sorted(kwargs.items())
        }
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found or expired
        """
        with self._lock:
            if key not in self._cache:
                return None
            
            entry = self._cache[key]
            expires_at = entry.get("expires_at")
            
            if expires_at and datetime.utcnow() > expires_at:
                # Entry expired, remove it
                del self._cache[key]
                return None
            
            return entry.get("value")
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if None)
        """
        with self._lock:
            ttl = ttl or self.default_ttl
            expires_at = datetime.utcnow() + timedelta(seconds=ttl)
            
            self._cache[key] = {
                "value": value,
                "expires_at": expires_at,
                "created_at": datetime.utcnow()
            }
    
    def delete(self, key: str) -> None:
        """Delete key from cache."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
    
    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
    
    def cleanup_expired(self) -> int:
        """
        Remove expired entries from cache.
        
        Returns:
            Number of entries removed
        """
        with self._lock:
            now = datetime.utcnow()
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.get("expires_at") and entry["expires_at"] < now
            ]
            
            for key in expired_keys:
                del self._cache[key]
            
            return len(expired_keys)
    
    def size(self) -> int:
        """Get current cache size."""
        with self._lock:
            return len(self._cache)
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            now = datetime.utcnow()
            total = len(self._cache)
            expired = sum(
                1 for entry in self._cache.values()
                if entry.get("expires_at") and entry["expires_at"] < now
            )
            
            return {
                "total_entries": total,
                "expired_entries": expired,
                "active_entries": total - expired,
                "default_ttl": self.default_ttl
            }


# Global cache instance
_global_cache: Optional[SimpleCache] = None


def get_cache() -> SimpleCache:
    """Get global cache instance."""
    global _global_cache
    if _global_cache is None:
        _global_cache = SimpleCache(default_ttl=300)  # 5 minutes default
    return _global_cache

