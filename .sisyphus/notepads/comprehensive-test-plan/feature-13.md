# Learnings for Feature 13 (Auto Job Hunt)

## Decisions
- **One-to-One Relationship**: `DBAutoApplyConfig` is linked 1:1 with `DBUser` to keep configuration simple per user.
- **Service Layer**: Introduced `AutoApplyService` to encapsulate logic, keeping API endpoints clean.
- **Mocking**: Using `AsyncMock` in pytest to isolate service tests from DB operations.

## Gotchas
- **Pydantic V2**: Deprecation warnings for `dict()` method (use `model_dump()`) and `json_encoders`. Need to update models to use `ConfigDict`.
- **Datetime**: `datetime.utcnow()` is deprecated. Should use `datetime.now(timezone.utc)`.
- **Frontend State**: Need to ensure React Query cache is invalidated properly on config updates.

## Status
- **Backend**:
  - Model `DBAutoApplyConfig` created.
  - Pydantic schemas created.
  - Service structure defined.
  - API endpoints drafted.
  - Unit tests passed (5/5).
- **Frontend**:
  - `AutoApply.tsx` page created.
  - `AutoApply.test.tsx` created.
  - E2E spec created.
  - **Blocking Issue**: `autoApplyService` and `Toggle` component missing/not exported. Need to implement them before frontend tests will pass.
