"""Cache management and statistics endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from src.core.cache import cache_region
from src.config import config
from src.api.dependencies import get_current_user
from src.models.user import User
from loguru import logger

router = APIRouter(prefix="/cache", tags=["cache"])


@router.get("/stats", response_model=Dict[str, Any])
async def get_cache_stats(current_user: User = Depends(get_current_user)):
    """
    Get cache statistics and configuration info.
    
    Returns information about:
    - Cache backend type
    - Cache configuration
    - Basic usage statistics (if available)
    """
    try:
        stats = {
            "backend": config.cache_backend,
            "enabled": config.cache_enabled,
            "expiration_time": config.cache_expiration_time,
            "redis_url": config.redis_url if config.cache_backend == "dogpile.cache.redis" else None,
        }
        
        # Try to get backend-specific stats
        try:
            backend = cache_region.backend
            if hasattr(backend, 'client'):
                # Redis backend
                if config.cache_backend == "dogpile.cache.redis":
                    try:
                        import redis
                        # Get Redis info
                        redis_client = backend.client
                        info = redis_client.info('stats')
                        stats['redis_stats'] = {
                            'total_connections_received': info.get('total_connections_received', 'N/A'),
                            'total_commands_processed': info.get('total_commands_processed', 'N/A'),
                            'keyspace_hits': info.get('keyspace_hits', 'N/A'),
                            'keyspace_misses': info.get('keyspace_misses', 'N/A'),
                        }
                        
                        # Calculate hit rate if available
                        hits = info.get('keyspace_hits', 0)
                        misses = info.get('keyspace_misses', 0)
                        total = hits + misses
                        if total > 0:
                            stats['hit_rate'] = f"{(hits / total * 100):.2f}%"
                    except Exception as e:
                        logger.warning(f"Could not fetch Redis stats: {e}")
                        stats['redis_stats'] = "unavailable"
            else:
                # Memory backend
                stats['backend_type'] = 'memory'
                stats['note'] = 'Memory backend does not provide detailed statistics'
        except Exception as e:
            logger.warning(f"Could not fetch backend stats: {e}")
            stats['backend_stats'] = "unavailable"
        
        logger.info(f"Cache stats retrieved by user {current_user.email}")
        return {"data": stats}
        
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve cache statistics"
        )


@router.post("/invalidate")
async def invalidate_cache(current_user: User = Depends(get_current_user)):
    """
    Invalidate all cache entries.
    
    This is an admin operation that clears the entire cache.
    Use with caution as it will cause cache misses until data is re-cached.
    """
    try:
        cache_region.invalidate()
        logger.warning(f"Cache invalidated by user {current_user.email}")
        return {
            "data": {
                "message": "Cache invalidated successfully",
                "invalidated_by": current_user.email
            }
        }
        
    except Exception as e:
        logger.error(f"Error invalidating cache: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to invalidate cache"
        )


@router.delete("/key/{cache_key}")
async def delete_cache_key(cache_key: str, current_user: User = Depends(get_current_user)):
    """
    Delete a specific cache key.
    
    This allows targeted cache invalidation for specific entries.
    """
    try:
        cache_region.delete(cache_key)
        logger.info(f"Cache key '{cache_key}' deleted by user {current_user.email}")
        return {
            "data": {
                "message": f"Cache key '{cache_key}' deleted successfully",
                "key": cache_key
            }
        }
        
    except Exception as e:
        logger.error(f"Error deleting cache key '{cache_key}': {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete cache key '{cache_key}'"
        )
