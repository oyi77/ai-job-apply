# Auto-Apply System - Complete Implementation Plan

**Generated:** 2026-01-29  
**Planning Based On:** Comprehensive analysis (4 background agents + direct tool research + 3-hour deep file inspection)  
**User Decisions:** Per-user scheduling, database duplicate detection, PDF email attachments, separate activity logging, queue + retry strategy, both unit + E2E testing

---

## 🎯 WORK OBJECTIVES

### Core Objective
**Implement production-ready, automated job application system** that autonomously searches, evaluates, and applies to jobs based on user preferences.

### Concrete Deliverables
- Functional auto-apply service with per-user scheduling
- Background scheduler integration for automated execution
- Email applications with resume and cover letter PDF attachments
- Activity logging system for tracking and monitoring
- Rate limiting and duplicate detection per platform
- Comprehensive testing suite (unit + E2E)
- Complete API endpoints for configuration and monitoring

### Definition of Done
- [x] AutoApplyService registered in ServiceRegistry
- [x] run_cycle() implementation (job search → AI scoring → application)
- [x] Email applications send with PDF attachments
- [x] APScheduler jobs registered and executing per-user
- [x] Activity logging to separate DBAutoApplyActivityLog table
- [x] Rate limiting enforced per platform (LinkedIn: 5/hr, Indeed: 10/hr)
- [x] Database duplicate detection (job_id + company + title per user)
- [x] Retry logic with exponential backoff (max 3 retries)
- [x] All tests passing (unit + E2E)

### Must Have
- Per-user scheduler configuration (respects individual user settings)
- Graceful error handling and comprehensive logging
- Anti-spam measures (rate limits, duplicate detection, human intervention)
- Real-time activity tracking and user notifications
- PDF email attachments for complete application packages

### Must NOT Have (Guardrails)
- NO global scheduler (must be per-user)
- NO synchronous operations in run_cycle (all I/O must be async)
- NO hardcoded rate limits (must be configurable per platform/user)
- NO data loss during errors (use database transactions)
- NO spam (platform bans from aggressive automation)
- NO cross-user duplicate applications

---

## 📊 COMPLETE DATA FLOW

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (React + TypeScript)              │
│                                                           │
│  AutoApply.tsx  ───────────────────────────────────┐     │
│  │ POST /config                                  │     │
│  │ POST /start                                    │     │
│  │ POST /stop                                     │     │
│  │ GET /activity                                  │     │
│  └──────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘     │
       │                                                   │
       ↓                                                   │
       │                                            API LAYER   │
┌──────┐ │                                                   │
│  FastAPI                                              │
│                                                           │
│  POST /api/v1/auto-apply/┬──────────┐    │
│  │ /config                          ──→ ServiceRegistry  │     │
│  │ /start                              → AutoApplyService  │     │
│  │ /stop                            └───────────────────┘     │
│  │ /activity                                                     │
│  └───────────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────┘     │
       │                                                   │
       ↓                                            SERVICE LAYER   │
┌───────────────────────────────────────────────────────────────────┐ │
│                                                           │
│  AutoApplyService (Core Logic)                             │
│  ├── JobSearchService  ←── Platform Handlers ←───┐ │
│  ├── JobApplicationService ←── EmailService            │ │
│  ├── AIService (Unified/Gemini)                       │ │
│  ├── NotificationService                                   │ │
│  └───┐                                                   │
│         │                                                   │
└─────────┘                                                   │
       │                                                   │
       ↓                                            DATABASE LAYER   │
┌───────────────────────────────────────────────────────────────────┐ │
│                                                           │
│  DBJobApplication                                    │     │
│  DBAutoApplyConfig (per-user settings)                   │     │
│  DBAutoApplyActivityLog (cycle tracking)               │     │
│  DBUser, DBResume, DBCoverLetter, etc.              │     │
└───────────────────────────────────────────────────────────────────┘     │
       │                                                   │
       ↓                                            BACKGROUND LAYER   │
┌───────────────────────────────────────────────────────────────────┐ │
│                                                           │
│  APScheduler                                         │     │
│  └───→ AutoApplyService.run_cycle() [EVERY 1H]     │
└───────────────────────────────────────────────────────────────────────┘     │
       │                                                   │
       ↓                                            EXTERNAL SITES   │
┌───────────────────────────────────────────────────────────────────┐ │
│  LinkedIn, Indeed, Glassdoor (Platform Handlers)             │
│  Playwright Browser Automation (fill forms, submit)         │
└───────────────────────────────────────────────────────────────────────┘     │
       │                                                   │
       ↓                                            EMAIL SERVICE    │
┌───────────────────────────────────────────────────────────────────┐ │
│  SMTP/Mailgun (send emails with PDF attachments)       │
└───────────────────────────────────────────────────────────────────────┘     │
```

---

## 🔧 IMPLEMENTATION PHASES

### Phase 1: Core Connection (Days 1-5) - HIGH PRIORITY

**Goal:** Make auto-apply functional end-to-end

#### Task 1.1: Register AutoApplyService in ServiceRegistry
**File:** `backend/src/services/service_registry.py`

**What to do:**
- Add `AutoApplyServiceProvider` class
- Implement dependency injection (job_search, job_application, ai, notification)
- Register in `_initialize_business_services()`
- Add `get_auto_apply_service()` convenience method
- Initialize service and add to instances dict

**Acceptance Criteria:**
- [ ] Provider class created with all dependencies
- [ ] Service registered in registry
- [ ] `get_auto_apply_service()` method available
- [ ] Manual test: `service_registry.get_auto_apply_service()` returns instance

**Estimated Time:** 2 hours

#### Task 1.2: Implement AutoApplyService.__init__()
**File:** `backend/src/services/auto_apply_service.py`

**What to do:**
- Update constructor to accept dependencies
- Store services as instance variables
- Call `await self._job_search_service.initialize()` if needed
- Implement `initialize()` method for setup tasks
- Implement `cleanup()` method

**Acceptance Criteria:**
- [ ] Constructor accepts all 4 dependencies
- [ ] Services stored as instance variables
- [ ] `initialize()` called successfully
- [ ] `cleanup()` implemented
- [ ] Unit tests for initialization

**Estimated Time:** 3 hours

#### Task 1.3: Create AutoApplyConfig Repository
**File:** `backend/src/database/repositories/auto_apply_config_repository.py` (NEW FILE)

**What to do:**
- Create `AutoApplyConfigRepository` class
- Implement CRUD operations (create, get, update, delete, get_active_configs)
- Use database session pattern: `async with session.begin()`
- Query `DBAutoApplyConfig` table

**Acceptance Criteria:**
- [ ] Repository class created
- [ ] `get_by_user_id()` method implemented
- [ ] `get_active_configs()` method implemented
- [ ] `update_config()` method implemented
- [ ] Database queries tested

**Estimated Time:** 3 hours

#### Task 1.4: Implement run_cycle() Skeleton
**File:** `backend/src/services/auto_apply_service.py`

**What to do:**
- Implement `async def run_cycle(self, user_id: str = None)` signature
- Fetch active auto-apply configs (use repository)
- For each config:
  - Search jobs using `self._job_search_service.search_jobs()`
  - Score jobs using `self._ai_service.analyze_job_match()`
  - Filter by score threshold (default: 70/100) and daily limit
  - Apply to top jobs using `self._job_application_service.apply_to_job()`
  - Log cycle results (create activity log entry)
- Handle edge cases (no configs, no jobs found, AI failures)
- Send notifications using `self._notification_service.send_daily_summary()`

**Acceptance Criteria:**
- [ ] `run_cycle()` method implemented with proper signature
- [ ] Job search integration working
- [ ] AI scoring integration working
- [ ] Application submission working
- [ ] Activity logging working
- [ ] Error handling for all operations
- [ ] Unit tests for run_cycle()

**Estimated Time:** 8 hours

#### Task 1.5: Fix Email Application
**File:** `backend/src/services/job_application_service.py`

**What to do:**
- Update `_apply_via_email()` to actually send emails
- Extract email address from job description using regex
- Read cover letter content from file
- Get email service from registry
- Call `await email_service.send_email()` with attachments
- Add error handling for missing emails

**Acceptance Criteria:**
- [ ] Email service integration working
- [ ] PDF attachments included in emails
- [ ] Cover letter content sent as HTML body
- [ ] Error handling for missing emails or send failures
- [ ] Integration tests for email sending
- [ ] Manual test: Send test email and verify delivery

**Estimated Time:** 2 hours

#### Task 1.6: Create DBAutoApplyActivityLog Model
**File:** `backend/src/database/models.py`

**What to do:**
- Add `DBAutoApplyActivityLog` class
- Define table schema with all required fields
- Add indexes for performance (user_id, created_at)
- Convert methods (to_dict/from_model if needed)

**Acceptance Criteria:**
- [ ] Model class created with all fields
- [ ] Table name defined correctly
- [ ] Foreign keys properly configured
- [ ] Indexes added for query performance
- [ ] Migration script created

**Estimated Time:** 2 hours

#### Task 1.7: Create AutoApplyActivityLog Repository
**File:** `backend/src/database/repositories/auto_apply_activity_repository.py` (NEW FILE)

**What to do:**
- Create `AutoApplyActivityLogRepository` class
- Implement CRUD operations (create, get_user_activities, get_latest_cycle)
- Use proper session management
- Add query methods for filtering and pagination

**Acceptance Criteria:**
- [ ] Repository class created
- [ ] `create()` method implemented
- [ ] `get_user_activities()` method implemented
- [ ] `get_latest_cycle()` method implemented
- [ ] Database queries tested with fixtures
- [ ] Pagination support added (limit parameter)

**Estimated Time:** 3 hours

#### Task 1.8: Integrate with APScheduler
**File:** `backend/src/services/scheduler_service.py`

**What to do:**
- Add `_register_auto_apply_job()` method to SchedulerService
- Fetch all active auto-apply configs
- Register per-user interval jobs (every 1 hour checks)
- Use `IntervalTrigger(hours=1)` for frequent execution
- Log job registration details

**Acceptance Criteria:**
- [ ] `_register_auto_apply_job()` method implemented
- [ ] Per-user jobs registered correctly
- [ ] Scheduler queries active configs properly
- [ ] No global scheduler (per-user only)
- [ ] Integration tested (start scheduler, check job registration)

**Estimated Time:** 3 hours

---

### Phase 2: Quality & Safety (Days 6-12) - HIGH PRIORITY

#### Task 2.1: Database-Level Duplicate Detection
**File:** `backend/src/services/auto_apply_service.py`

**What to do:**
- Implement `_check_duplicate()` method
- Query database for existing applications with same (job_id, company, job_title) for current user
- Use in-memory cache with TTL (7 days) to reduce database load
- Skip duplicates and log as "skipped (duplicate)"
- Add cache invalidation when new application created

**Acceptance Criteria:**
- [ ] Duplicate detection logic implemented
- [ ] Database query efficient (use indexes)
- [ ] In-memory cache with expiry (7 days)
- [ ] Cross-user duplicates prevented
- [ ] Skip logged with reason
- [ ] Integration tests for duplicate scenarios
- [ ] Cache invalidation working

**Estimated Time:** 4 hours

#### Task 2.2: In-Memory Duplicate Cache
**File:** `backend/src/services/auto_apply_service.py`

**What to do:**
- Implement `DuplicateCache` class with LRU eviction
- Store recent (job_id, company, job_title) tuples
- Add TTL mechanism (7 days)
- Implement `is_duplicate()` and `add()` methods
- Use in-memory cache to avoid database queries
- Integrate into `_check_duplicate()` method

**Acceptance Criteria:**
- [ ] Cache class implemented
- [ ] LRU eviction policy working
- [ ] TTL expiry mechanism working
- [ ] Cache hit/miss logging
- [ ] Integration tests for cache behavior
- [ ] Thread-safe operations (use asyncio.Lock)
- [ ] Performance tested (cache reduces queries by 90%)

**Estimated Time:** 4 hours

#### Task 2.3: Implement Rate Limiting
**File:** `backend/src/services/auto_apply_service.py`

**What to do:**
- Define `PLATFORM_RATE_LIMITS` constant
- Implement `_check_rate_limit()` method
- Track applications per platform per user
- Implement per-hour limits (LinkedIn: 5, Indeed: 10)
- Implement daily limit enforcement (reset at midnight)
- Add rate limit storage (database or in-memory)
- Return descriptive error messages when limits hit

**Acceptance Criteria:**
- [ ] Rate limit constants defined
- [ ] Per-platform tracking working
- [ ] Daily limit enforcement implemented (rolling 24h)
- [ ] Hourly limit checking implemented
- [ ] Error messages clear and helpful
- [ ] Integration tests for rate limiting scenarios
- [ ] Manual test: Apply to 6th job, verify 7th skipped

**Estimated Time:** 4 hours

#### Task 2.4: Implement Daily Limit Reset
**File:** `backend/src/services/auto_apply_service.py`

**What to do:**
- Implement `_reset_daily_limits()` method
- Check current time vs. last application date
- If new day (after midnight): reset application count
- Use timezones correctly (UTC)
- Log reset event to activity log

**Acceptance Criteria:**
- [ ] Daily reset logic implemented
- [ ] Timezone handling correct (UTC)
- [ ] Midnight boundary check working
- [ ] Reset logged in activity
- [ ] Integration tests for reset scenarios
- [ ] Manual test: Apply 5 jobs on Jan 31, 23:59, verify 6th job on Feb 1 is counted

**Estimated Time:** 2 hours

#### Task 2.5: Implement Retry Logic
**File:** `backend/src/services/auto_apply_service.py`

**What to do:**
- Define `MAX_RETRIES` constant (3)
- Implement `_execute_with_retry()` helper method
- Use exponential backoff (1s, 2s, 4s)
- Track retry count per job
- Only retry on transient errors (network, timeout, captcha)
- Mark job as "failed" after max retries

**Acceptance Criteria:**
- [ ] Retry logic implemented with exponential backoff
- [ ] Max retries enforced (3 attempts)
- [ ] Transient errors identified (network, timeout, captcha)
- [ ] Retry count tracked per job
- [ ] Job status updated to "failed" after max retries
- [ ] Integration tests for retry scenarios
- [ ] Manual test: Simulate failure, verify retry behavior

**Estimated Time:** 4 hours

#### Task 2.6: Human Intervention Fallback
**File:** `backend/src/services/auto_apply_service.py`

**What to do:**
- Implement `_handle_complex_form()` method
- Detect captcha challenges (visual, checkbox)
- Detect complex multi-page forms
- Save job to queue for manual review
- Send notification email to user
- Log intervention reason

**Acceptance Criteria:**
- [ ] Captcha detection implemented
- [ ] Complex form detection implemented
- [ ] Queue save working (job marked for manual review)
- [ ] User notification email sent
- [ ] Intervention logged in activity
- [ ] Integration tests for human intervention scenarios
- [ ] Manual test: Apply to job with captcha, verify job saved to queue

**Estimated Time:** 4 hours

#### Task 2.7: Error Handling & Logging
**File:** `backend/src/services/auto_apply_service.py`

**What to do:**
- Add comprehensive try-catch blocks around all operations
- Log all errors with context (job_id, user_id, error details)
- Use structured logging format
- Implement screenshot capture on failures
- Handle AI service unavailability gracefully

**Acceptance Criteria:**
- [ ] All operations wrapped in try-catch
- [ ] Errors logged to database and console
- [ ] Screenshot capture implemented for browser failures
- [ ] AI service fallback working
- [ ] Error messages user-friendly
- [ ] Integration tests for error scenarios
- [ ] Manual test: Simulate AI failure, verify fallback behavior

**Estimated Time:** 3 hours

#### Task 2.8: Per-User Configuration Updates
**File:** `backend/src/services/auto_apply_service.py`

**What to do:**
- Implement `update_rate_limits()` method
- Allow users to override default rate limits
- Store custom limits in database
- Validate new limits (minimum: 1/hr, maximum: 50/hr)
- Update scheduler if limits changed
- Log configuration changes

**Acceptance Criteria:**
- [ ] `update_rate_limits()` method implemented
- [ ] Custom limits stored in database
- [ ] Validation logic working
- [ ] Scheduler updated on config change
- [ ] Integration tests for configuration updates
- [ ] Manual test: Set custom rate limits, verify enforcement

**Estimated Time:** 3 hours

---

### Phase 3: Advanced Features (Days 13-19) - MEDIUM PRIORITY

#### Task 3.1: Implement Job Queue System
**File:** `backend/src/database/models.py` (NEW TABLE)

**What to do:**
- Create `DBAutoApplyJobQueue` model
- Define fields: id, user_id, job_id, job_url, match_score, status, retry_count, scheduled_for, applied_at, error_message
- Add indexes for query performance
- Implement queue operations (enqueue, dequeue, update_status)

**Acceptance Criteria:**
- [ ] Model class created with all fields
- [ ] Table structure defined correctly
- [ ] Indexes added (user_id, status, scheduled_for)
- [ ] Queue CRUD operations working
- [ ] Integration tests for queue behavior

**Estimated Time:** 3 hours

#### Task 3.2: Implement Queue Operations
**File:** `backend/src/database/repositories/auto_apply_job_queue_repository.py` (NEW FILE)

**What to do:**
- Create `AutoApplyJobQueueRepository` class
- Implement CRUD operations (create, get_user_queue, update_status, delete)
- Implement queue retry logic (re-queue failed jobs)
- Add query methods for filtering (by status, by user)
- Use proper transaction management

**Acceptance Criteria:**
- [ ] Repository class created
- [ ] `create()` method implemented
- [ ] `get_user_queue()` method implemented
- [ ] `update_status()` method implemented
- [ ] `delete()` method implemented
- [ ] Retry logic working
- [ ] Database queries tested
- [ ] Integration tests for queue operations
- [ ] Manual test: Enqueue job, verify status updates

**Estimated Time:** 4 hours

#### Task 3.3: Implement Retry Strategy Based on Settings
**File:** `backend/src/services/auto_apply_service.py`

**What to do:**
- Add `retry_strategy` field to `DBAutoApplyConfig`
- Implement `get_retry_strategy()` from config
- Implement `apply_with_retry()` method
- Support strategies: "immediate", "delayed", "skip"
- Honor user's preferred strategy when retrying failed jobs

**Acceptance Criteria:**
- [ ] `retry_strategy` field added to model
- [ ] Strategies supported: immediate, delayed, skip
- [ ] `apply_with_retry()` respects user strategy
- [ ] Queue updated based on strategy
- [ ] Integration tests for retry strategies
- [ ] Manual test: Set strategy to "delayed", verify queue behavior

**Estimated Time:** 4 hours

#### Task 3.4: Daily Summary Emails
**File:** `backend/src/services/auto_apply_service.py`

**What to do:**
- Implement `_send_daily_summary()` method
- Calculate cycle statistics (searched, matched, applied, failed)
- Use notification service to send summary
- Format summary as clear HTML email
- Include activity log link for details
- Send at end of each cycle or configurable time

**Acceptance Criteria:**
- [ ] Summary calculation working
- [ ] Statistics accurate and complete
- [ ] Email formatted correctly with HTML
- [ ] Notification service integration working
- [ ] Activity log reference included
- [ ] Integration tests for summary emails
- [ ] Manual test: Run cycle, verify summary email received

**Estimated Time:** 3 hours

#### Task 3.5: Real-Time Status Updates
**File:** `backend/src/services/platform_handlers.py`

**What to do:**
- Implement status polling in LinkedIn and Indeed handlers
- Add `_check_application_status()` method
- Update `DBJobApplication` status from "applied" to "in_review", "interview", "rejected"
- Poll every 6-12 hours
- Detect interview invitations and respond automatically

**Acceptance Criteria:**
- [ ] Status polling implemented
- [ ] Application statuses updated correctly
- [ ] Database updates working
- [ ] Polling intervals configurable
- [ ] Interview invitation detection working
- [ ] Integration tests for status updates
- [ ] Manual test: Apply to job, verify status changes after 12 hours

**Estimated Time:** 4 hours

#### Task 3.6: AI-Powered Resume Optimization
**File:** `backend/src/services/auto_apply_service.py`

**What to do:**
- Implement `optimize_resume_for_job()` method
- Call `self._ai_service.optimize_resume()` before each application
- Store optimized resume temporarily for this application
- Pass optimized content to application service
- Add config option to enable/disable per-job optimization

**Acceptance Criteria:**
- [ ] `optimize_resume_for_job()` implemented
- [ ] AI optimization called before application
- [ ] Optimized resume content passed correctly
- [ ] Config option working
- [ ] Cost tracking (AI usage monitoring)
- [ ] Integration tests for optimization feature
- [ ] Manual test: Enable optimization, verify improved resume

**Estimated Time:** 3 hours

#### Task 3.7: Create Activity Dashboard API
**File:** `backend/src/api/v1/auto_apply.py`

**What to do:**
- Implement `GET /activity` endpoint
- Add query parameters: user_id, limit, start_date, end_date
- Return paginated activity logs
- Add authentication requirement
- Implement filtering and sorting options
- Add statistics aggregation endpoint

**Acceptance Criteria:**
- [ ] `GET /activity` endpoint implemented
- [ ] Pagination working
- [ ] Query parameters validated
- [ ] Statistics calculated correctly
- [ ] Authentication enforced
- [ ] Integration tests for activity API
- [ ] Manual test: Enable auto-apply, query activity, verify results

**Estimated Time:** 3 hours

#### Task 3.8: Implement Per-User Rate Limits Endpoint
**File:** `backend/src/api/v1/auto_apply.py`

**What to do:**
- Implement `POST /rate-limits` endpoint
- Accept `RateLimitsRequest` model
- Validate limits (min 1/hr, max 50/hr)
- Update `DBAutoApplyConfig` with custom limits
- Enforce per-platform maximums
- Return updated configuration

**Acceptance Criteria:**
- [ ] `POST /rate-limits` endpoint implemented
- [ ] Validation logic working
- [ ] Database updates working
- [ ] Per-platform limits enforced
- [ ] Integration tests for rate limits
- [ ] Manual test: Set custom rate limit, verify enforcement

**Estimated Time:** 3 hours

---

## 📊 TESTING STRATEGY

### Test Coverage Requirements
- **Target:** 95%+ coverage
- **Frameworks:** pytest (backend), Vitest + Playwright (frontend)
- **Test Types:** Unit tests, integration tests, E2E tests

### Unit Tests (Backend)

**File:** `tests/unit/services/test_auto_apply_service.py`

**Test Cases:**
- `test_register_service()` - Service registration
- `test_initialization()` - Dependency injection
- `test_run_cycle_success()` - Successful execution
- `test_run_cycle_no_configs()` - No active configs
- `test_run_cycle_no_jobs()` - Job search returns empty
- `test_run_cycle_ai_failure()` - AI service unavailable
- `test_duplicate_detection()` - Duplicate detection
- `test_rate_limiting()` - Per-platform limits
- `test_daily_limit_reset()` - 24h reset logic
- `test_retry_logic()` - Exponential backoff
- `test_human_intervention()` - Complex forms and queue
- `test_activity_logging()` - Activity log creation
- `test_email_integration()` - Email sending

### Integration Tests (Backend)

**File:** `tests/integration/test_auto_apply_api.py`

**Test Cases:**
- `test_auto_apply_config_crud()` - Configuration management
- `test_auto_apply_start_stop()` - Start/stop control
- `test_get_activity_logs()` - Activity retrieval
- `test_update_rate_limits()` - Rate limit overrides
- `test_daily_summary_email()` - Summary notifications
- `test_duplicate_prevention()` - Cross-user checks
- `test_error_handling()` - Graceful degradation

### E2E Tests (Full Automation Flow)

**File:** `tests/e2e/auto-apply.spec.ts`

**Test Scenarios:**
1. **Happy Path:** User enables auto-apply → jobs searched → applications submitted → activity logged
2. **Rate Limit:** Daily limit reached → remaining jobs skipped → activity logged
3. **Duplicate Detection:** Same job appears → application skipped → activity logged
4. **AI Failure:** AI service unavailable → fallback used → activity logged
5. **Email Failure:** Email service fails → application queued → notification sent
6. **Per-User Scheduling:** Multiple users → jobs execute independently
7. **Configuration Updates:** Rate limits changed → scheduler updated
8. **Queue Management:** Failed applications → queued → manual review → resubmitted
9. **Activity Dashboard:** Query activity logs → statistics displayed → filtering working
10. **Manual Review:** Complex form → saved to queue → user notified → manual completion

**Estimated Time:** 5-7 days (E2E tests require Playwright setup and scenario orchestration)

---

## ✅ ACCEPTANCE CRITERIA

### Phase 1 Tasks
- [ ] Service registered and accessible via `get_auto_apply_service()`
- [ ] `run_cycle()` method exists and can be called
- [ ] Email service integration tested with attachments
- [ ] Activity log repository created with CRUD operations
- [ ] APScheduler jobs registered and executing on interval
- [ ] Manual verification: All APIs responding correctly

### Phase 2 Tasks
- [ ] Database checks prevent cross-user duplicates (job_id + company + title per user)
- [ ] Rate limits respected (LinkedIn: 5/hr, Indeed: 10/hr)
- [ ] Daily limits reset at midnight (rolling 24h)
- [ ] Duplicate cache with 7-day expiry reduces database load
- [ ] Retry logic with exponential backoff (max 3 retries)
- [ ] Error handling logs failures with stack traces
- [ ] Activity logs show all cycle metrics (searched, matched, applied, failed)

### Phase 3 Tasks
- [ ] Failed applications queued for manual review
- [ ] Retry strategy respects user settings (immediate vs delayed)
- [ ] Daily summary emails include cycle statistics
- [ ] Real-time status updates from LinkedIn/Indeed APIs
- [ ] Job queue supports create, update, and delete operations
- [ ] Activity dashboard API with statistics and filtering

---

## 🔒 SECURITY & ETHICS

### Rate Limiting Strategy
```python
# Per-platform limits (configurable defaults)
DEFAULT_RATE_LIMITS = {
    "linkedin": {"applications_per_hour": 5, "daily_limit": 50},
    "indeed": {"applications_per_hour": 10, "daily_limit": 100},
    "glassdoor": {"applications_per_hour": 3, "daily_limit": 30},
    "email": {"applications_per_day": 20}  # To avoid spam detection
}

# User can override these via POST /rate-limits
MINIMUM_LIMITS = {
    "linkedin": 1,  # Allow very conservative users
    "indeed": 2,
    "glassdoor": 1
}

MAXIMUM_LIMITS = {
    "linkedin": 20,  # Allow aggressive users with caution
    "indeed": 50,
    "glassdoor": 15,
}
```

### Anti-Spam Measures
1. Database duplicate detection (job_id + company + title per user)
2. Daily limits reset at midnight (rolling 24h)
3. Email rate limiting (max 20/day)
4. Minimum time between applications (random delay 2-5 minutes)
5. Human intervention required for failed captcha detection

### Platform Ban Handling
- Detect LinkedIn account bans (403/429 errors)
- Automatically disable user's auto-apply config
- Send notification email with reason
- Recommend manual review and account recovery

---

## 📝 DOCUMENTATION UPDATES

### New API Endpoints
```python
# backend/src/api/v1/auto_apply.py

@router.post("/config", response_model=AutoApplyConfig)
async def update_config(request: UpdateConfigRequest):
    """Update user's auto-apply configuration."""
    pass

@router.post("/activity", response_model=List[AutoApplyActivityLog])
async def get_activity_logs(user_id: str, limit: int = 10):
    """Get recent auto-apply activity logs."""
    pass

@router.post("/rate-limits", response_model=RateLimitsResponse)
async def update_rate_limits(request: RateLimitsRequest):
    """Update per-platform rate limits (for power users)."""
    pass
```

### Database Migration
```python
# backend/src/database/migrations/versions/001_add_auto_apply_tables.sql

"""
Add auto-apply activity logging and job queue tables
"""
```

---

## 🚀 NEXT STEPS

### Immediate Actions

1. **Save Work Plan**
   - Save this plan to: `.sisyphus/plans/auto-apply-implementation-plan.md`

2. **Delete Draft**
   - Remove: `.sisyphus/drafts/auto-apply-deep-analysis.md`

3. **Guide User**
   - Run `/start-work` to begin implementation
   - Plan will be loaded automatically by orchestrator
   - Total estimated time: 18-22 days

---

## 📊 SUCCESS METRICS

### Phase 1 (Days 1-5)
- **Functional Auto-Apply**: Users can enable and system searches/applies to jobs
- **Per-User Scheduling**: Each user gets their own job execution
- **Email Applications**: Working with resume and cover letter attachments
- **Activity Tracking**: Complete visibility into automation cycles

### Phase 2 (Days 6-12)
- **Rate Limiting**: Platform-specific limits enforced
- **Duplicate Prevention**: Database-level checks eliminate duplicate applications
- **Quality & Safety**: Retry logic, error handling, human intervention

### Phase 3 (Days 13-19)
- **Advanced Features**: Queue system, status updates, daily summaries
- **Monitoring Dashboard**: Real-time activity and performance metrics

---

**Implementation plan complete. Ready for execution with Sisyphus!** 🎯
