"""
Performance Monitoring Dashboard for Caching

This module provides utilities to monitor cache performance and generate reports.
"""

import time
from typing import Dict, Any, List
from datetime import datetime, timezone
from ..core.cache import cache_region
from loguru import logger


class CachePerformanceMonitor:
    """Monitor and track cache performance metrics."""
    
    def __init__(self):
        self.metrics = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "errors": 0,
            "total_get_time": 0.0,
            "total_set_time": 0.0,
            "start_time": datetime.now(timezone.utc)
        }
    
    def record_hit(self, duration: float = 0.0):
        """Record a cache hit."""
        self.metrics["hits"] += 1
        self.metrics["total_get_time"] += duration
    
    def record_miss(self, duration: float = 0.0):
        """Record a cache miss."""
        self.metrics["misses"] += 1
        self.metrics["total_get_time"] += duration
    
    def record_set(self, duration: float = 0.0):
        """Record a cache set operation."""
        self.metrics["sets"] += 1
        self.metrics["total_set_time"] += duration
    
    def record_delete(self):
        """Record a cache delete operation."""
        self.metrics["deletes"] += 1
    
    def record_error(self):
        """Record a cache error."""
        self.metrics["errors"] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current performance statistics."""
        total_requests = self.metrics["hits"] + self.metrics["misses"]
        hit_rate = (self.metrics["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        avg_get_time = (self.metrics["total_get_time"] / total_requests) if total_requests > 0 else 0
        avg_set_time = (self.metrics["total_set_time"] / self.metrics["sets"]) if self.metrics["sets"] > 0 else 0
        
        uptime = (datetime.now(timezone.utc) - self.metrics["start_time"]).total_seconds()
        
        return {
            "cache_hits": self.metrics["hits"],
            "cache_misses": self.metrics["misses"],
            "total_requests": total_requests,
            "hit_rate_percent": round(hit_rate, 2),
            "cache_sets": self.metrics["sets"],
            "cache_deletes": self.metrics["deletes"],
            "cache_errors": self.metrics["errors"],
            "avg_get_time_ms": round(avg_get_time * 1000, 2),
            "avg_set_time_ms": round(avg_set_time * 1000, 2),
            "uptime_seconds": round(uptime, 2),
            "requests_per_second": round(total_requests / uptime, 2) if uptime > 0 else 0
        }
    
    def reset(self):
        """Reset all metrics."""
        self.metrics = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "errors": 0,
            "total_get_time": 0.0,
            "total_set_time": 0.0,
            "start_time": datetime.now(timezone.utc)
        }
        logger.info("Cache performance metrics reset")


# Global performance monitor instance
performance_monitor = CachePerformanceMonitor()


def get_performance_dashboard() -> Dict[str, Any]:
    """
    Get comprehensive performance dashboard data.
    
    Returns:
        Dictionary containing all performance metrics and cache status
    """
    stats = performance_monitor.get_stats()
    
    # Try to get backend-specific stats
    try:
        backend = cache_region.backend
        backend_info = {
            "backend_type": type(backend).__name__,
            "configured": True
        }
        
        # Add Redis-specific stats if available
        if hasattr(backend, 'client'):
            try:
                import redis
                redis_client = backend.client
                info = redis_client.info('stats')
                backend_info['redis_stats'] = {
                    'keyspace_hits': info.get('keyspace_hits', 0),
                    'keyspace_misses': info.get('keyspace_misses', 0),
                    'total_commands': info.get('total_commands_processed', 0)
                }
            except Exception as e:
                logger.warning(f"Could not fetch Redis stats: {e}")
                backend_info['redis_stats'] = "unavailable"
    except Exception as e:
        logger.warning(f"Could not fetch backend info: {e}")
        backend_info = {"backend_type": "unknown", "configured": False}
    
    return {
        "performance_metrics": stats,
        "backend_info": backend_info,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
