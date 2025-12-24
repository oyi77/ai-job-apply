# Design: Caching Infrastructure

## Context

Need production-grade distributed caching with Redis for scalability and performance.

## Decisions

### Decision: Redis for Distributed Caching
**What**: Use Redis for distributed caching
**Why**:
- Industry standard
- High performance
- Distributed support
- Rich data structures

**Fallback**: In-memory SimpleCache if Redis unavailable

### Decision: Cache-Aside Pattern
**What**: Use cache-aside (lazy loading) pattern
**Why**:
- Simple to implement
- Works well with existing code
- Easy to understand

**Flow**:
1. Check cache
2. If miss, query database
3. Store in cache
4. Return data

### Decision: Cache Key Naming
**What**: Structured cache key naming
**Format**: `{entity}:{id}:{user_id}` or `{entity}:{query_hash}:{user_id}`

**Examples**:
- `application:123:user_456`
- `resume:789:user_456`
- `analytics:stats:user_456`

### Decision: Cache TTL Strategy
**What**: Different TTLs for different data types
**Configuration**:
- Applications: 5 minutes
- Resumes: 10 minutes
- Analytics: 1 minute
- Job search: 15 minutes

## Risks / Trade-offs

### Risk: Cache Invalidation Complexity
**Mitigation**: Clear invalidation patterns, comprehensive testing

### Risk: Redis Dependency
**Mitigation**: Fallback to in-memory cache, health checks

