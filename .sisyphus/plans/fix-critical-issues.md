# Fix Critical Issues & Implement Missing Features

## TL;DR

> **Quick Summary**: Fix broken services (scheduler, JobSpy), refactor disabled test files, and implement high-priority missing frontend/backend features
>
> **Deliverables**: Working scheduler, JobSpy fallback, 3 test files fixed, Account Deletion API, Interview Prep API, Job Search Filter UI
> 
> **Estimated Effort**: Large (100+ tasks across 8 weeks)
> **Parallel Execution**: YES - independent fixes can happen in parallel
> 
> **Critical Path**: Fix scheduler -> Enable JobSpy -> Fix tests -> Implement missing APIs

---

## Priority Matrix

| Priority | Description | Tasks | Estimated Time |
|----------|-------------|-------|----------------|
| **P1 - Critical** | Broken services affecting core functionality | Scheduler fix, JobSpy fallback | Week 1 |
| **P2 - High** | Test infrastructure and code quality | Test file fixes, stub implementations | Week 2 |
| **P3 - Medium** | New API implementations | Account Deletion, Interview Prep APIs | Weeks 3-5 |
| **P4 - Low** | Frontend enhancements | UI for new APIs, search filters | Weeks 6-8 |

---

## Context

### Current Issues Identified

**Broken Services (P1 - Critical):**
1. **Scheduler Service**: Health check shows `running: false` - not actually starting background tasks
2. **JobSpy Integration**: Marked as unavailable in health check (`jobspy_available: false`)

**Disabled Test Files (P2 - High)** (need refactoring to work):
1. `backend/tests/unit/test_notification_service.py.skip` - Missing EmailService, ReminderNotificationBuilder, etc.
2. `backend/tests/unit/test_resume_builder_service.py.skip` - Wrong type names (TemplateType vs ResumeTemplate)
3. `backend/tests/unit/services/test_auto_apply_service.py.skip` - Duplicate test file

**Missing Frontend Features (P3/P4)** (waiting for backend):
1. **Account Deletion API** - Backend endpoint not implemented yet (frontend ready in Settings.tsx:134)
2. **Interview Prep API** - Pending implementation in AIServices.tsx:691
3. **Job Search Filter** - "not yet implemented in the UI" comment in Resumes.test.tsx

---

## Test Coverage Targets

| Component | Current | Target | Notes |
|-----------|---------|--------|-------|
| **Backend Unit Tests** | ~80% | **80%** | Maintain current level |
| **Backend Integration** | ~60% | **70%** | Increase for API endpoints |
| **Frontend Unit Tests** | ~65% | **70%** | Focus on critical paths |
| **E2E Tests** | ~30% | **50%** | Add for new features |

**Test Commands:**
```bash
# Backend coverage
cd backend && python -m pytest tests/ --cov=src --cov-report=html --cov-fail-under=80

# Frontend coverage  
cd frontend && npm run test:coverage
```

---

## Work Objectives

### Core Objective
Fix all broken services and implement high-priority missing features to restore full system functionality.

### Concrete Deliverables
- [ ] Working Scheduler Service (background task scheduling)
- [ ] JobSpy fallback (when real scraping fails, use realistic mock data)
- [ ] Fixed test_notification_service.py (all imports resolved)
- [ ] Fixed test_resume_builder_service.py (correct types)
- [ ] Removed duplicate test_auto_apply_service.py
- [ ] Account Deletion API (backend endpoint + frontend UI) **[Requires Auth]**
- [ ] Interview Preparation API (backend endpoint + frontend UI)
- [ ] Job Search Filter (backend + frontend UI)

### Definition of Done
- [ ] Scheduler health shows `running: true` with active scheduled tasks
- [ ] JobSpy fallback responds with realistic mock job data
- [ ] All test files collect and run without errors
- [ ] Account deletion flow complete (UI + API) with proper authorization
- [ ] Interview prep API creates reminders for scheduled interviews
- [ ] Job search supports filtering by keywords/location/date

---

## Must Have
- Scheduler must start and manage background tasks
- JobSpy must return meaningful fallback data when real scraping unavailable
- All test imports must resolve to existing classes
- Account deletion must be safe with confirmation **and require authenticated user**
- Interview prep must schedule reminders
- Job search must support filtering criteria

### Must NOT Have (Guardrails)
- Do not implement full JobSpy scraping (use fallback approach)
- Do not create duplicate service files
- Account deletion requires user authentication (PREREQUISITE)
- Tests should not be permanently disabled - only skip truly broken ones

---

## Database Migration Strategy (Alembic)

### Prerequisites
```bash
# Install Alembic if not present
cd backend && pip install alembic

# Initialize Alembic (if not already done)
alembic init alembic
```

### Migration Commands
```bash
# Create new migration
cd backend && alembic revision --autogenerate -m "description_of_change"

# Apply migrations
cd backend && alembic upgrade head

# Rollback one step
cd backend && alembic downgrade -1

# View current migration status
cd backend && alembic current
```

### Migration Required For
- **Phase 4**: Interview Prep tables (interviews, interview_prep_reminders)
- **Phase 5**: Job search filter preferences table (user_search_preferences)

---

## Execution Strategy

### Phase 1: Fix Broken Services (P1 - Week 1)

**Task 1.1-1.6: Scheduler Service Fix**
- [x] 1.1 Debug why scheduler shows `running: false`
  - **FOUND**: Scheduler has `start()` method that sets `_running = True`, but health check runs BEFORE startup completes
  - **ROOT CAUSE**: `backend/main.py` line 241-243 calls `scheduler.start()` in `app.on_event('startup')`, but ServiceRegistry initializes services asynchronously
  - **HEALTH CHECK TIMING**: Health endpoint at line 477 runs before all services are initialized
- [x] 1.2 Implement background task startup in ServiceRegistry
  - **File**: `backend/src/services/service_registry.py` line 238-243
  - **Fix**: Ensure `initialize()` waits for scheduler to be ready before returning
- [x] 1.3 Verify scheduler.start() is called during app startup
  - **Add**: Startup logging to confirm scheduler.start() is called
- [ ] 1.4 Test with manual task creation via API
  - **Test**: Create test endpoint or manual trigger to verify scheduled tasks execute
- [ ] 1.5 Add monitoring for scheduled task execution
  - **Add**: Debug logging for reminder job execution
- [x] 1.6 Fix health check to accurately reflect running status

**Verification Commands (Task 1.x):**
```bash
# Start backend and check health
cd backend && python main.py &
sleep 5
curl -s http://localhost:8000/health | python -c "import sys,json; d=json.load(sys.stdin); print('Scheduler running:', d.get('scheduler',{}).get('running', 'NOT_FOUND'))"

# Check scheduler logs
cd backend && grep -i "scheduler" logs/*.log | tail -20
```

**Task 2.1-2.5: JobSpy Integration Enhancement**
- [x] 2.1 Analyze current fallback implementation in JobSearchService
  - **FOUND**: `job_search_service.py` line 224-232 has `use_mock=True` parameter
  - **MOCK DATA**: Returns 15 realistic mock jobs with company names, positions, locations
- [x] 2.2 Verify mock job data generator exists
  - **EXISTS**: Mock generator in JobSearchService (lines 1083-1311)
- [x] 2.3 Verify company/position/title generation for fallback jobs
  - **EXISTS**: Mock data includes company names, titles based on keywords (lines 1097-1130)
- [x] 2.4 Implement intelligent fallback strategy
  - **VERIFIED**: System already automatically falls back to enriched mock data when JobSpy is unavailable or fails.
- [ ] 2.5 Update health check to show `jobspy_available: true` with fallback status

**Verification Commands (Task 2.x):**
```bash
# Test job search endpoint with fallback
curl -s "http://localhost:8000/api/v1/jobs/search?query=python&location=remote&limit=5" | python -c "import sys,json; d=json.load(sys.stdin); print('Jobs found:', len(d.get('jobs',[])), '| Mock used:', d.get('mock_data_used', False))"

# Check health endpoint for jobspy status
curl -s http://localhost:8000/health | python -c "import sys,json; d=json.load(sys.stdin); print('JobSpy available:', d.get('job_search',{}).get('jobspy_available', 'NOT_FOUND'))"
```

**Rollback Strategy (Phase 1):**
```bash
# If scheduler fix causes issues, revert to previous behavior:
git checkout HEAD~1 -- backend/src/services/service_registry.py backend/src/services/scheduler_service.py

# Restart services
pkill -f "python main.py"
cd backend && python main.py
```

---

### Phase 2: Refactor Test Files (P2 - Week 2)

**Task 3.1-3.3: Test File Fixes**
- [ ] 3.1 Fix test_notification_service.py
  - Create stub/mock for EmailService
  - Create stub/mock for ReminderNotificationBuilder
  - Create stub/mock for NotificationType enum
  - Remove pytestmark skip decorator
  - Add missing imports (timedelta, sys)
  - Write tests for actually available functionality
- [ ] 3.2 Fix test_resume_builder_service.py
  - Fix ResumeTemplate import
  - Create stub/mock for ResumeSection if not available
  - Remove pytestmark skip decorator
  - Add missing type definitions
- [ ] 3.3 Clean up duplicate test file
  - Delete `backend/tests/unit/services/test_auto_apply_service.py.skip`
  - Keep only `backend/tests/unit/test_auto_apply_service.py`

**Verification Commands (Task 3.x):**
```bash
# Run fixed test files individually
cd backend && python -m pytest tests/unit/test_notification_service.py -v --tb=short

cd backend && python -m pytest tests/unit/test_resume_builder_service.py -v --tb=short

# Verify no .skip files remain
ls backend/tests/unit/*.skip 2>/dev/null && echo "ERROR: .skip files still exist" || echo "OK: No .skip files"

# Run full test suite with coverage
cd backend && python -m pytest tests/ --cov=src --cov-fail-under=80 -v
```

**Rollback Strategy (Phase 2):**
```bash
# If test fixes break other tests, restore .skip extension
cd backend/tests/unit
mv test_notification_service.py test_notification_service.py.skip
mv test_resume_builder_service.py test_resume_builder_service.py.skip
```

---

### Phase 3: Implement Account Deletion API (P3 - Week 3)

**PREREQUISITE CHECK**: Authentication must be working before implementing account deletion.

**Pre-Implementation Verification:**
```bash
# Verify auth endpoints exist and work
curl -s http://localhost:8000/api/v1/auth/me -H "Authorization: Bearer test_token" | python -c "import sys,json; d=json.load(sys.stdin); print('Auth status:', 'OK' if 'user' in d or 'id' in d else 'MISSING')"

# If auth returns error, DO NOT proceed with account deletion
# Implement authentication first
```

**Task 4.1-4.4: Account Deletion API**
- [ ] 4.1 Verify authentication system is working (BLOCKER)
- [ ] 4.2 Create AccountService interface in `backend/src/core/account_service.py`
- [ ] 4.3 Implement AccountService in `backend/src/services/account_service.py`
  - `DELETE /api/v1/accounts/me` - delete current user's account (soft delete)
  - `GET /api/v1/accounts/me` - get current user account info
  - Requires valid JWT token
- [ ] 4.4 Add to router in `backend/src/api/v1/accounts.py`
- [ ] 4.5 Write tests for account service

**Verification Commands (Task 4.x):**
```bash
# Test account deletion endpoint (requires valid auth token)
TOKEN="your_jwt_token_here"
curl -s -X DELETE http://localhost:8000/api/v1/accounts/me -H "Authorization: Bearer $TOKEN" -w "\nHTTP Status: %{http_code}\n"

# Expected: 204 No Content (success) or 401 Unauthorized (if not authenticated)
```

**Rollback Strategy (Phase 3):**
```bash
# Remove account deletion endpoint if issues arise
git checkout HEAD~1 -- backend/src/api/v1/accounts.py backend/src/services/account_service.py
# Restart backend
```

---

### Phase 4: Interview Preparation API (P3 - Week 4)

**Task 5.1-5.5: Interview Prep API**
- [ ] 5.1 Create InterviewPrepService interface in `backend/src/core/interview_service.py`
- [ ] 5.2 Implement InterviewPrepService in `backend/src/services/interview_prep_service.py`
  - `POST /api/v1/interviews/prepare` - create prep reminders
  - `GET /api/v1/interviews/upcoming` - get upcoming interviews
  - `PUT /api/v1/interviews/{id}` - update prep status
  - `DELETE /api/v1/interviews/{id}` - cancel prep
- [ ] 5.3 Create database migration for interview tables
  ```bash
  cd backend && alembic revision --autogenerate -m "add_interview_prep_tables"
  cd backend && alembic upgrade head
  ```
- [ ] 5.4 Add to router in `backend/src/api/v1/interviews.py`
- [ ] 5.5 Write tests for interview service

**Verification Commands (Task 5.x):**
```bash
# Test interview prep creation
curl -s -X POST http://localhost:8000/api/v1/interviews/prepare \
  -H "Content-Type: application/json" \
  -d '{"application_id": "test-app-1", "interview_date": "2026-02-10T10:00:00Z", "notes": "Prepare for technical round"}' \
  | python -c "import sys,json; d=json.load(sys.stdin); print('Interview prep ID:', d.get('id', 'ERROR'))"

# Get upcoming interviews
curl -s http://localhost:8000/api/v1/interviews/upcoming | python -c "import sys,json; d=json.load(sys.stdin); print('Upcoming interviews:', len(d.get('interviews', [])))"
```

**Rollback Strategy (Phase 4):**
```bash
# Rollback database migration
cd backend && alembic downgrade -1

# Remove interview API files
git checkout HEAD~1 -- backend/src/api/v1/interviews.py backend/src/services/interview_prep_service.py
```

---

### Phase 5: Job Search Enhancement (P3 - Week 5)

**Note**: This is JOB SEARCH filtering, not Resume search. The feature allows users to filter job search results by various criteria.

**Task 6.1-6.6: Job Search Filter Enhancement**
- [ ] 6.1 Enhance JobSearchService to support additional filters
  - `keywords` - Filter by multiple keywords
  - `location` - Filter by location (city, state, country, remote)
  - `date_posted` - Filter by posting date (today, week, month)
  - `salary_range` - Filter by salary range
  - `experience_level` - Filter by experience level
- [ ] 6.2 Add filter parameters to search models (JobSearchFilter model)
- [ ] 6.3 Update `GET /api/v1/jobs/search` endpoint to accept query params
- [ ] 6.4 Implement filter logic in search service
- [ ] 6.5 Update frontend to pass filter parameters
- [ ] 6.6 Write tests for filtering functionality

**Verification Commands (Task 6.x):**
```bash
# Test job search with filters
curl -s "http://localhost:8000/api/v1/jobs/search?keywords=python,fastapi&location=remote&date_posted=week&experience_level=mid" \
  | python -c "import sys,json; d=json.load(sys.stdin); print('Filtered jobs:', len(d.get('jobs', [])), '| Filters applied:', d.get('filters_applied', {}))"

# Test empty filter handling
curl -s "http://localhost:8000/api/v1/jobs/search?query=developer" \
  | python -c "import sys,json; d=json.load(sys.stdin); print('Default search works:', len(d.get('jobs', [])) > 0)"
```

**Rollback Strategy (Phase 5):**
```bash
# Revert job search service changes
git checkout HEAD~1 -- backend/src/services/job_search_service.py backend/src/api/v1/jobs.py
```

---

### Phase 6: Frontend - Account Deletion UI (P4 - Week 6)

**Task 7.1-7.6: Account Deletion UI**
- [ ] 7.1 Add delete account button to Settings page (`frontend/src/pages/Settings.tsx:134`)
- [ ] 7.2 Implement confirmation dialog before deletion (must require typing "DELETE" to confirm)
- [ ] 7.3 Call `DELETE /api/v1/accounts/me` API endpoint
- [ ] 7.4 Show success/error notifications
- [ ] 7.5 Redirect to login page after successful deletion
- [ ] 7.6 Write tests for account deletion flow

**Verification Commands (Task 7.x):**
```bash
# Start frontend and verify Settings page loads
cd frontend && npm run dev &
sleep 5
curl -s http://localhost:5173 | grep -q "Settings" && echo "Frontend running" || echo "Frontend error"

# Run frontend tests
cd frontend && npm run test -- Settings.test.tsx
```

---

### Phase 7: Frontend - Interview Preparation UI (P4 - Week 7)

**Task 8.1-8.7: Interview Prep UI**
- [ ] 8.1 Add interview prep modal/component
- [ ] 8.2 Implement form for scheduling interview prep reminders
- [ ] 8.3 Add job application linking to prep
- [ ] 8.4 Add notes field for preparation
- [ ] 8.5 Add date/time picker
- [ ] 8.6 Implement prep completion status tracking
- [ ] 8.7 Connect to InterviewPrepService API endpoints

**Verification Commands (Task 8.x):**
```bash
# Run frontend tests for interview prep
cd frontend && npm run test -- InterviewPrep.test.tsx

# Manual verification: navigate to AIServices page
# Open browser to http://localhost:5173/ai-services
# Verify interview prep section is visible
```

---

### Phase 8: Frontend - Job Search Filter UI (P4 - Week 8)

**Task 9.1-9.8: Job Search Filter UI**
- [ ] 9.1 Add search filter panel to Jobs page
- [ ] 9.2 Implement keyword filter input field (multi-select/tags)
- [ ] 9.3 Implement location filter (with autocomplete)
- [ ] 9.4 Add date range filter dropdown (today/week/month/any)
- [ ] 9.5 Add experience level filter (entry/mid/senior/lead)
- [ ] 9.6 Add salary range slider
- [ ] 9.7 Integrate with existing search results
- [ ] 9.8 Write tests for filter components

**Verification Commands (Task 9.x):**
```bash
# Run frontend tests for job search filters
cd frontend && npm run test -- JobSearch.test.tsx

# Manual verification: navigate to Jobs page
# Open browser to http://localhost:5173/jobs
# Verify filter panel is visible and functional
```

---

## Risk Mitigation Strategies

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **Scheduler fix breaks existing functionality** | High | Medium | Feature flag for new scheduler behavior; keep old code as fallback |
| **Test fixes introduce new failures** | Medium | Medium | Run tests in isolation first; maintain .skip files until fully fixed |
| **Auth dependency blocks account deletion** | High | Low | Verify auth early; implement mock auth for testing if needed |
| **Database migration fails** | High | Low | Always test migrations in dev first; keep rollback scripts ready |
| **Frontend changes break existing UI** | Medium | Medium | Component-level testing; visual regression tests |
| **Performance degradation with new filters** | Medium | Medium | Add database indexes; implement query caching |

---

## Success Criteria

### Phase 1: Scheduler Working
- [ ] Scheduler.start() successfully calls background task execution
- [ ] Health endpoint shows `"running": true` for scheduler
- [ ] Scheduled tasks persist and execute at correct times
- [ ] No errors in scheduler logs

### Phase 2: JobSpy Fallback
- [ ] JobSearchService returns meaningful mock jobs when scraping fails
- [ ] Mock jobs include realistic company names, positions, locations
- [ ] Health check shows `jobspy_available: true` with `fallback_mode: true`
- [ ] Fallback is seamless to end user (no performance degradation)

### Phase 3: Tests Fixed
- [ ] test_notification_service.py collects and runs without import errors
- [ ] test_resume_builder_service.py collects and runs with correct types
- [ ] No `.skip` files remain in tests/unit/
- [ ] Backend test coverage >= 80%

### Phase 4: Account Deletion
- [ ] Backend API responds to `DELETE /api/v1/accounts/me` with 204 No Content
- [ ] Endpoint requires valid authentication (401 if not authenticated)
- [ ] Frontend shows confirmation dialog before deletion
- [ ] Success/error notifications appear
- [ ] User is logged out and redirected after deletion

### Phase 5: Interview Prep
- [ ] Backend creates interview prep records in database
- [ ] Frontend UI allows scheduling prep reminders
- [ ] Prep is linked to job application
- [ ] API allows updating prep status and notes

### Phase 6: Job Search Filter
- [ ] Backend API accepts filter parameters (keywords, location, date, etc.)
- [ ] Filtered results return correctly
- [ ] Frontend UI has filter inputs that work
- [ ] Search performance with filters is acceptable (<500ms)

---

## Commit Strategy

After completing each major phase:
1. **Phase 1**: `fix(services): restore scheduler and JobSpy functionality`
2. **Phase 2**: `fix(tests): resolve test file import errors and remove skips`
3. **Phase 3**: `feat(api): implement account deletion endpoint with auth`
4. **Phase 4**: `feat(api): add interview preparation service`
5. **Phase 5**: `feat(search): add job search filtering capabilities`
6. **Phase 6**: `feat(ui): implement account deletion flow`
7. **Phase 7**: `feat(ui): add interview preparation interface`
8. **Phase 8**: `feat(ui): add job search filter panel`

---

## References

### Core Service Files
- `backend/src/services/scheduler_service.py` - Scheduler implementation
- `backend/src/services/job_search_service.py` - JobSpy fallback logic
- `backend/src/services/service_registry.py` - Service initialization (line 233-243)
- `backend/src/services/notification_service.py` - Needs EmailService implementation
- `backend/main.py` - App startup (line 241)

### Test Files to Fix
- `backend/tests/unit/test_notification_service.py.skip` - Line 19+ has missing imports
- `backend/tests/unit/test_resume_builder_service.py.skip` - Line 24: has wrong type names
- `backend/tests/unit/services/test_auto_apply_service.py.skip` - Duplicate file, DELETE

### Frontend Files to Update
- `frontend/src/pages/Settings.tsx` - Line 134: calls `/api/v1/accounts` (needs backend)
- `frontend/src/__tests__/pages/Resumes.test.tsx` - Line 1: "not yet implemented" comment
- `frontend/src/services/api.ts` - Add account deletion endpoints

### Documentation
- `openspec/changes/complete-authentication/` - Authentication changes proposal
- `openspec/changes/add-production-deployment/` - Production deployment proposal
- `docs/11-api-endpoints-detailed.md` - API endpoint reference

---

## Start Work

This plan provides a roadmap to fix all critical issues and implement missing high-priority features.

**To begin execution**, run:
```bash
/start-work
```

This will:
1. Register the plan as your active boulder
2. Track progress across sessions
3. Enable automatic continuation if interrupted

**Manual Start Alternative:**
```bash
cd C:\Users\Snap-PC-Dev-026\ai-job-apply

# Phase 1 (highest priority - broken services)
# Start with scheduler fix in service_registry.py
```

Good luck! 
