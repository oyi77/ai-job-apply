

## 2026-02-11 Task 2.4 Blocker - Duplicate Detection E2E Test
- Test implemented in `frontend/tests/e2e/auto-apply.spec.ts` at lines 217-295
- Test logic: Tracks applied jobs in Set, detects duplicate on second cycle
- **Issue**: The mock route handler isn't being called between cycles as expected
- **Error**: `duplicateDetected` flag remains false even after second cycle
- **Root Cause**: The activity endpoint may not be called during the test cycles, or state isn't persisting between parallel workers
- **Status**: Test marked as failing - needs revision of mock strategy
- **Next Steps**: Consider using localStorage or a different approach to track state between cycles

