# Learnings

- Analytics performance: fetch applications once and pass the list into analytics computations to avoid N+1 repository calls.
- Use `asyncio.gather()` in the dashboard endpoint to parallelize independent analytics computations.
- In-memory caching: keep cache keys user-scoped (`analytics:{user_id}:...`) and include query params + a cache-buster to avoid stale data.
