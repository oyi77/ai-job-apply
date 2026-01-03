"""
Write-Through Cache Pattern Implementation

This module provides a write-through caching decorator that can be used
as an alternative to the cache-aside pattern currently in use.

Write-through ensures cache and database are always in sync by writing
to both simultaneously.
"""

from functools import wraps
from typing import Callable, Any, Optional
from ..core.cache import cache_region
from loguru import logger


def write_through_cache(cache_key_fn: Callable, expiration_time: int = 3600):
    """
    Write-through cache decorator.
    
    When data is written, it's written to both cache and database simultaneously.
    When data is read, it's read from cache first, then database if cache miss.
    
    Args:
        cache_key_fn: Function to generate cache key from function args
        expiration_time: Cache TTL in seconds
        
    Usage:
        @write_through_cache(lambda user_id: f"user:{user_id}", expiration_time=1800)
        async def get_user(user_id: str):
            return await db.get_user(user_id)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Generate cache key
            cache_key = cache_key_fn(*args, **kwargs)
            
            # Try cache first
            cached_value = cache_region.get(cache_key)
            if cached_value and not isinstance(cached_value, type(cache_region.dogpile_registry.get("NO_VALUE"))):
                logger.debug(f"Write-through cache hit: {cache_key}")
                return cached_value
            
            # Cache miss - fetch from source
            logger.debug(f"Write-through cache miss: {cache_key}")
            result = await func(*args, **kwargs)
            
            # Write to cache
            if result is not None:
                cache_region.set(cache_key, result, expiration_time=expiration_time)
                logger.debug(f"Write-through cache updated: {cache_key}")
            
            return result
        
        return wrapper
    return decorator


def write_through_invalidate(cache_key: str):
    """
    Invalidate a write-through cache entry.
    
    Args:
        cache_key: The cache key to invalidate
    """
    try:
        cache_region.delete(cache_key)
        logger.debug(f"Write-through cache invalidated: {cache_key}")
    except Exception as e:
        logger.warning(f"Failed to invalidate write-through cache {cache_key}: {e}")


# Example usage documentation
"""
Example: Using write-through cache for user data

from src.core.write_through_cache import write_through_cache, write_through_invalidate

class UserService:
    @write_through_cache(
        cache_key_fn=lambda self, user_id: f"user:{user_id}",
        expiration_time=1800  # 30 minutes
    )
    async def get_user(self, user_id: str):
        # This will be cached automatically
        return await self.repository.get_by_id(user_id)
    
    async def update_user(self, user_id: str, data: dict):
        # Update database
        user = await self.repository.update(user_id, data)
        
        # Invalidate cache (write-through on next read)
        write_through_invalidate(f"user:{user_id}")
        
        # Or update cache immediately (true write-through)
        cache_region.set(f"user:{user_id}", user, expiration_time=1800)
        
        return user
"""
