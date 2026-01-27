# Work Plan: Feature 13 (AI Auto Job Hunt) & Final Testing

**Goal:** Implement the "AI Auto Job Hunt" feature (backend & frontend) and complete comprehensive testing (E2E).

## Phase 1: Backend Implementation (Auto Job Hunt)

### 1.1 Database Model
- **Action:** Append `DBAutoApplyConfig` to `backend/src/database/models.py`.
- **Fields:** `user_id`, `keywords` (JSON), `locations` (JSON), `min_salary`, `daily_limit`, `is_active`.
- **Relationship:** One-to-One with `DBUser`.
- **Guardrails:**
  - `daily_limit` must be <= 50 (Hard Cap).
  - `keywords` list size <= 10.
  - `locations` list size <= 5.
- **Verification:** `cd backend && python -c "from src.database.models import DBAutoApplyConfig; print(DBAutoApplyConfig.__tablename__)"`

### 1.2 Pydantic Schemas
- **Action:** Create `backend/src/models/automation.py`.
- **Schemas:**
  - `AutoApplyConfigCreate`: Validates `daily_limit` (1-50), `min_salary` (>0).
  - `AutoApplyConfigUpdate`: Optional fields validation.
  - `AutoApplyConfig`: Response model.
- **Verification:** `cd backend && python -c "from src.models.automation import AutoApplyConfig; print('Schema OK')"`

### 1.3 Service Logic
- **Action:** Create `backend/src/services/auto_apply_service.py`.
- **Methods:**
  - `create_config`, `get_config`, `update_config`.
  - `run_automation_cycle(user_id: str)`:
    1. **Pre-check:** Verify user has active config and `daily_limit` not reached today.
    2. **Job Search:** Use `JobSearchService` with fallback handling (try-except).
    3. **Filter:** Remove duplicates (check `ApplicationRepository` by title+company).
    4. **Apply (Internal Only):** Create `DBJobApplication` with status `APPLIED` (mocked - NO external calls).
    5. **Limit Check:** Stop if `daily_limit` hit OR if 5 consecutive failures occur (Circuit Breaker).
    6. **Log:** Record activity in `DBAIActivity` (success/failure).
- **Edge Case Handling:**
  - If `JobSearchService` fails -> Log error, do not crash.
  - If 0 jobs found -> Log "No jobs found", exit cycle.
  - If `daily_limit` reached -> Log "Daily limit reached", exit.
- **Verification:** `cd backend && pytest tests/unit/test_auto_apply_service.py`

### 1.4 API Endpoints
- **Action:** Create `backend/src/api/v1/auto_apply.py`.
- **Endpoints:**
  - `GET /config`: Get user config.
  - `PUT /config`: Update config (validate limits).
  - `POST /start`: Trigger automation manually (Rate limit: 1 per minute, enforced by `RateLimiter`).
  - `GET /history`: Get automation logs from `DBAIActivity`.
- **Wiring:** Register in `backend/src/api/app.py`.
- **Verification:** `curl -X POST http://localhost:8000/api/v1/auto-apply/start` (expect 401 if unauthorized, 200 if OK).

## Phase 2: Frontend Implementation

### 2.1 UI Component
- **Action:** Create `frontend/src/pages/AutoApply.tsx`.
- **Features:**
  - Toggle Switch (Enable/Disable).
  - Multi-select for Keywords & Locations.
  - Slider for Daily Limit (Range 1-50).
  - Activity Log Table (Date, Action, Status, Details).
  - "Run Now" button (with loading state).

### 2.2 Integration Tests
- **Action:** Create `frontend/src/__tests__/pages/AutoApply.test.tsx`.
- **Cases:**
  - Renders configuration form correctly.
  - Updates settings successfully (mock API).
  - Displays validation error if limit > 50.
  - Displays activity log items.
  - Handles API errors (e.g., failed to start).
- **Verification:** `npm test -- src/__tests__/pages/AutoApply.test.tsx`

## Phase 3: End-to-End Testing

### 3.1 Playwright Spec
- **Action:** Create `frontend/tests/e2e/auto-apply.spec.ts`.
- **Flow:**
  1. Login.
  2. Navigate to Auto Apply.
  3. Enable feature.
  4. Configure keywords=["Python"], limit=5.
  5. Click "Save" -> Verify success toast.
  6. Click "Run Now" -> Verify "Cycle started" toast.
  7. Reload -> Verify activity log shows "Started".
- **Verification:** `npx playwright test tests/e2e/auto-apply.spec.ts`

## Phase 4: Final Verification
- **Action:** Run full test suite.
- **Command:** `npm run test:e2e` + `pytest`.
- **Success Criteria:**
  - All unit tests pass (Backend + Frontend).
  - E2E tests pass (Auth, Resumes, Job Search, Auto Apply).
  - No "is not a constructor" errors in frontend.
  - No 500 errors in backend logs during E2E.

---

**Ready for Execution.**
