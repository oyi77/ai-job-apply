"""Middleware for monitoring database query performance."""

import time
from typing import Callable, Any, Optional
from functools import wraps
from ..utils.logger import get_logger

logger = get_logger(__name__)

# Threshold for slow queries (in seconds)
SLOW_QUERY_THRESHOLD = 0.1  # 100ms


def monitor_query_performance(func: Callable) -> Callable:
    """
    Decorator to monitor database query performance.
    
    Args:
        func: Function to monitor
        
    Returns:
        Wrapped function with performance monitoring
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        query_name = func.__name__
        
        try:
            result = await func(*args, **kwargs)
            elapsed_time = time.time() - start_time
            
            # Log query performance
            if elapsed_time > SLOW_QUERY_THRESHOLD:
                logger.warning(
                    f"Slow query detected: {query_name} took {elapsed_time:.3f}s "
                    f"(threshold: {SLOW_QUERY_THRESHOLD}s)"
                )
            else:
                logger.debug(
                    f"Query {query_name} completed in {elapsed_time:.3f}s"
                )
            
            return result
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(
                f"Query {query_name} failed after {elapsed_time:.3f}s: {e}",
                exc_info=True
            )
            raise
    
    return wrapper


def log_query_metrics(query_name: str, duration: float, row_count: Optional[int] = None):
    """
    Log query performance metrics.
    
    Args:
        query_name: Name of the query
        duration: Query duration in seconds
        row_count: Number of rows returned (optional)
    """
    metrics = {
        "query": query_name,
        "duration": duration,
        "row_count": row_count,
        "slow": duration > SLOW_QUERY_THRESHOLD
    }
    
    if duration > SLOW_QUERY_THRESHOLD:
        logger.warning(
            f"Slow query: {query_name} - {duration:.3f}s "
            f"({row_count} rows)" if row_count else f"({duration:.3f}s)"
        )
    else:
        logger.debug(
            f"Query metrics: {query_name} - {duration:.3f}s "
            f"({row_count} rows)" if row_count else f"({duration:.3f}s)"
        )

