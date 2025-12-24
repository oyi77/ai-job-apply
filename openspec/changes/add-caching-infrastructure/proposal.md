# Change: Add Caching Infrastructure

## Why

The system currently has basic in-memory caching (SimpleCache) but needs production-grade caching:
- Redis for distributed caching
- Cache invalidation strategies
- Cache warming
- Performance improvement for frequently accessed data

TDD mentions Redis caching as future, HLD mentions it in scalability design. Critical for performance at scale.

## What Changes

### Backend
- **Redis Integration**: Add Redis client and connection
- **Cache Service**: Create Redis-based cache service
- **Cache Strategies**: Implement cache-aside, write-through patterns
- **Cache Invalidation**: Smart cache invalidation on updates
- **Cache Warming**: Pre-populate cache with common queries

### Configuration
- **Redis Configuration**: Environment-based Redis config
- **Cache TTL Configuration**: Configurable cache expiration
- **Cache Key Management**: Structured cache key naming

## Impact

- **Affected specs**: performance, scalability, caching
- **Affected code**:
  - `backend/src/services/cache_service.py` (enhance or replace)
  - `backend/src/utils/cache.py` (enhance with Redis)
  - `backend/src/config.py` - Add Redis configuration
  - All services using cache
- **Dependencies**: redis-py (Python Redis client)
- **Breaking changes**: None (backward compatible with SimpleCache fallback)

## Success Criteria

- Redis caching working
- Cache hit rate > 80% for common queries
- Cache invalidation working correctly
- Performance improvement measurable
- Fallback to in-memory cache if Redis unavailable

