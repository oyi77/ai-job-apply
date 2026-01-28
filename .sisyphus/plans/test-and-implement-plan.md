# Test & Implementation Plan: AI Job Assistant

## Phase 1: Frontend Unit/Integration Tests (Vitest)
**Goal:** 80% coverage for core feature pages.

### 1.1 Resume Management (`frontend/src/pages/Resumes.tsx`)
- **Test File:** `frontend/src/__tests__/pages/Resumes.test.tsx`
- **Cases:**
  - Renders resume list (mocked).
  - Opens upload modal on click.
  - Calls `resumeService.uploadResume` on form submit.
  - Handles upload errors.
  - Handles delete action.

### 1.2 Cover Letters (`frontend/src/pages/CoverLetters.tsx`)
- **Test File:** `frontend/src/__tests__/pages/CoverLetters.test.tsx`
- **Cases:**
  - Renders cover letter list.
  - Opens generation modal.
  - Calls `aiService.generateCoverLetter`.
  - Displays generated content.

### 1.3 Job Search (`frontend/src/pages/JobSearch.tsx`)
- **Test File:** `frontend/src/__tests__/pages/JobSearch.test.tsx`
- **Cases:**
  - Renders search inputs.
  - Calls `jobSearchService.searchJobs` on submit.
  - Renders job cards.
  - Handles "Apply" click (creates internal application).

### 1.4 AI Services (`frontend/src/pages/AIServices.tsx`)
- **Test File:** `frontend/src/__tests__/pages/AIServices.test.tsx`
- **Cases:**
  - Renders service cards (Optimize, Scan, Interview).
  - Opens respective modals.
  - Calls correct AI endpoints.
  - Displays results (e.g., match score, interview questions).

## Phase 2: End-to-End Tests (Playwright)
**Goal:** Verify critical user flows.

### 2.1 Cover Letter Flow
- **Spec:** `frontend/tests/e2e/cover-letters.spec.ts`
- **Flow:** Login -> Navigate to Cover Letters -> Click Generate -> Select Resume/Job -> Verify Result.

### 2.2 AI Service Flow
- **Spec:** `frontend/tests/e2e/ai-services.spec.ts`
- **Flow:** Login -> Navigate to AI Services -> Select "Resume Scanner" -> Select Resume/Job -> Verify Match Score.

## Phase 3: Feature 13 - AI Auto Job Hunt
**Goal:** Implement autonomous job search and application agent.

### 3.1 Backend Architecture
- **Model:** `AutoApplyConfig` (SQLAlchemy + Pydantic)
  - Fields: `user_id`, `keywords`, `locations`, `min_salary`, `daily_limit`, `is_active`.
- **Service:** `AutoApplyService`
  - Method: `run_cycle()` (Scheduled every hour).
  - Logic: 
    1. Fetch active configs.
    2. Search jobs (using `JobSearchService`).
    3. Filter by "Not Applied".
    4. Auto-create application record (Status: "Applied").
    5. (Mock) External submission or integration with browser automation.
- **API:** `POST /api/v1/auto-apply/config`, `POST /api/v1/auto-apply/start`.

### 3.2 Frontend Implementation
- **Component:** `AutoApplyDashboard` (New Tab in Dashboard).
- **Features:** Toggle ON/OFF, Set Keywords, View Activity Log.

## Phase 4: Execution Order
1. Implement Phase 1 Tests (Parallel).
2. Implement Phase 2 Tests.
3. Implement Phase 3 Backend (Model -> Service -> API).
4. Implement Phase 3 Frontend.
5. Final Verification.
