# Task 4.1: Auto-Apply API Unit Tests - BLOCKED

**Date:** 2026-02-06T22:45:00.000Z

## Status: ❌ BLOCKED - Cannot Proceed

## Attempted Work

### Test File Created
**File:** `backend/tests/unit/test_auto_apply_api.py`
**Size:** 254 lines
**Tests:** 20 test cases implemented

### Test Structure

```python
# Test file created with:
- 20 unit tests for all auto-apply API endpoints
- Fixtures for mocking AutoApplyService
- FastAPI TestClient setup
- Proper assertions and error handling
```

## Critical Blocker

### Issue: ServiceRegistry Missing Method

**Error Message:**
```python
AttributeError: <class 'src.services.service_registry.ServiceRegistry'> does not have attribute 'get_auto_apply_service'
```

**Impact:** ALL tests fail because the patch for `get_auto_apply_service()` cannot find the method.

**Root Cause:**
1. Auto-apply API endpoints (backend/src/api/v1/auto_apply.py) use:
   ```python
   service = await service_registry.get_auto_apply_service()
   ```

2. ServiceRegistry class does NOT have `get_auto_apply_service()` method

3. AutoApplyService was never properly registered with a retrievable method

**Evidence:**
```bash
# LSP diagnostics show 8 errors:
# backend/src/api/v1/auto_apply.py:22,31,40,50,62,74,89,98,108
ERROR: Cannot access attribute "get_auto_apply_service" for class "ServiceRegistry"
```

## Test Coverage

**Tested Endpoints:**
1. POST /api/v1/auto-apply/config
2. GET /api/v1/auto-apply/config
3. POST /api/v1/auto-apply/start
4. POST /api/v1/auto-apply/stop
5. GET /api/v1/auto-apply/activity
6. POST /api/v1/auto-apply/rate-limits
7. GET /api/v1/auto-apply/queue
8. POST /api/v1/auto-apply/retry-queued
9. POST /api/v1/auto-apply/skip-queued
10. Authentication requirement

**Result:** 0/20 tests passing due to ServiceRegistry blocker

## Required Actions

### HIGH PRIORITY - Fix ServiceRegistry

1. **Add `get_auto_apply_service()` method to ServiceRegistry**
   ```python
   def get_auto_apply_service(self, user_id: str) -> AutoApplyService:
       """Get or create AutoApplyService for user."""
       if user_id not in self._services:
           from src.services.auto_apply_service import AutoApplyServiceProvider
           provider = AutoApplyServiceProvider()
           self.register_service("auto_apply_service", provider)
       return self._services["auto_apply_service"].get_service()
   ```

2. **Register AutoApplyService properly with user-scoped instances**
   - AutoApplyServiceProvider should support per-user isolation
   - Each user gets their own AutoApplyService instance
   - Not a shared singleton

### ALTERNATIVE - Direct Service Access

1. **Bypass ServiceRegistry temporarily**
   - Modify tests to import AutoApplyService directly
   - Mock service methods without going through ServiceRegistry
   - Remove `app_with_mocked_service` fixture complexity

2. **Or use `get_service("auto_apply_service")` method**
   - If ServiceRegistry has `get_service()` method
   - Tests can call: `service_registry.get_service("auto_apply_service")`

## Next Steps

### Immediate Action Required

**Cannot proceed with Task 4.1 until ServiceRegistry is fixed:**

1. **Coordinate with backend engineering** to implement `get_auto_apply_service()` in ServiceRegistry
2. **Or modify API tests** to work around ServiceRegistry limitation
3. **Mark task as blocked** in plan file with detailed blocker documentation

### Estimated Time to Fix

ServiceRegistry fix: **2-4 hours**
Test file updates: **30 minutes**
Rerun tests: **15 minutes**

**Total: 3-5 hours**

## Conclusion

Task 4.1 (Auto-Apply API Unit Tests) is BLOCKED by missing ServiceRegistry infrastructure. The test file is created but cannot be executed successfully without fixing the underlying service registry issue.

**Recommendation:** Coordinate with backend engineering team to prioritize ServiceRegistry fix, or modify tests to work around the limitation.