# Decisions

- Added a process-local in-memory TTL cache (`backend/src/services/cache_service.py`) for analytics endpoints to reduce repeated DB + AI work.
- Implemented cache invalidation via a DB-derived cache-buster (`count + max(updated_at)`), embedded into cache keys, so cache entries automatically roll over when applications change.
- Kept AI-powered skills gap TTL short (60s) to avoid serving stale/variable AI responses.
- 2026-01-27: Appended `DBAutoApplyConfig` after `GlobalAISettings` per model ordering request.
