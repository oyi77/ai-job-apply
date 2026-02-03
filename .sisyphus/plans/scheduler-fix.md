# Scheduler Service Fix - Implementation Plan

## Issue Summary
**Problem**: Scheduler service health check shows `running: false` because `SchedulerServiceProvider.initialize()` never calls `scheduler.start()`.

**Root Cause**: In `backend/src/services/service_registry.py` (lines 755-771), the `SchedulerServiceProvider` calls `await self._service.initialize()` but never calls `await self._service.start()`.

**Impact**: Background tasks (reminder jobs, cleanup jobs) are never executed because the APScheduler is not started.

---

## Fix Implementation

### File: `backend/src/services/service_registry.py`

**Location**: Lines 755-771 (SchedulerServiceProvider class)

**Current Code**:
```python
class SchedulerServiceProvider(ServiceProvider):
    """Provider for scheduler service."""

    def get_service(self):
        return self._service

    async def initialize(self) -> None:
        from src.services.scheduler_service import SchedulerService

        self._service = SchedulerService()
        await self._service.initialize()

    async def cleanup(self) -> None:
        if hasattr(self._service, "cleanup"):
            await self._service.cleanup()
        if hasattr(self._service, "stop"):
            await self._service.stop()
```

**Fixed Code**:
```python
class SchedulerServiceProvider(ServiceProvider):
    """Provider for scheduler service."""

    def get_service(self):
        return self._service

    async def initialize(self) -> None:
        from src.services.scheduler_service import SchedulerService

        self._service = SchedulerService()
        await self._service.initialize()
        # Start the scheduler so it's ready to execute background tasks
        await self._service.start()

    async def cleanup(self) -> None:
        if hasattr(self._service, "cleanup"):
            await self._service.cleanup()
        if hasattr(self._service, "stop"):
            await self._service.stop()
```

**Change**: Added `await self._service.start()` after `initialize()` on line 766.

---

## Verification Steps

### Step 1: Apply the Fix
```bash
cd C:\Users\Snap-PC-Dev-026\ai-job-apply
# Edit backend/src/services/service_registry.py
# Add await self._service.start() after line 765
```

### Step 2: Restart Backend Server
```bash
# Stop existing backend if running
pkill -f "python main.py" 2>/dev/null || true

# Restart backend
cd backend && python main.py &
sleep 5
```

### Step 3: Verify Scheduler is Running
```bash
# Check health endpoint
curl -s http://localhost:8000/health | python -c "import sys,json; d=json.load(sys.stdin); print('Scheduler status:', d.get('scheduler', {}))"

# Expected output:
# Scheduler status: {'running': True, 'jobs_count': 2, 'initialized': True}
```

### Step 4: Verify Jobs are Scheduled
```bash
# Check scheduler API endpoint
curl -s http://localhost:8000/api/v1/scheduler/jobs | python -c "import sys,json; d=json.load(sys.stdin); print('Scheduled jobs:', len(d.get('jobs', [])))"

# Expected: 2 jobs (check_reminders, cleanup_old_jobs)
```

---

## Rollback Plan

If the fix causes issues:
```bash
# Revert the change
git checkout HEAD~1 -- backend/src/services/service_registry.py

# Restart backend
pkill -f "python main.py" 2>/dev/null || true
cd backend && python main.py &
```

---

## Expected Outcome

**Before Fix**:
```json
{
  "scheduler": {
    "running": false,
    "initialized": true,
    "jobs_count": 0
  }
}
```

**After Fix**:
```json
{
  "scheduler": {
    "running": true,
    "initialized": true,
    "jobs_count": 2
  }
}
```

---

## Integration with Main Plan

This fix is part of **Phase 1: Fix Broken Services** in `.sisyphus/plans/fix-critical-issues.md`.

**Task IDs**: 1.2-1.6 in the main plan.

**Priority**: P1 - Critical (blocks scheduler functionality)

---

## Files Affected

| File | Change |
|------|--------|
| `backend/src/services/service_registry.py` | Add `await self._service.start()` call |

## Dependencies
- None (scheduler service has no dependencies)

## Risks
- **Low Risk**: This is a simple one-line addition that follows the existing pattern
- **Mitigation**: The fix is wrapped in try/catch in the service initialization, so failures won't crash the app
