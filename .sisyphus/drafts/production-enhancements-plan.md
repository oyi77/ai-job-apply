# Draft: Production Enhancements Work Plan

## Metis Analysis Summary (Completed)

### Key Findings from Existing Codebase:
- **Anti-Detection**: Already partially implemented in `browser_automation_service.py` (lines 61, 92, 93, 102)
  - webdriver override exists
  - window.chrome mock exists
  - plugins/languages spoofing exists
  
- **Scheduler**: Has basic event listeners (EXECUTED/ERROR) but no persistence
  - Uses in-memory `self.reminder_jobs` dictionary
  - No JOB_MISSED handling
  
- **Platform Handlers**: Use fixed sleeps and element waits (not optimal)
  - `platform_handlers.py:73`, `118`, `129`

- **Tests**: May be out of sync with current implementation

### Questions Needing User Input:
1. **Scheduler Persistence Strategy**:
   - Option A: SQLAlchemyJobStore only (APScheduler native)
   - Option B: First-class reminder tables + rehydration from app data
   - Option C: Both (hybrid approach)

2. **JOB_MISSED Handling**:
   - A) Reschedule automatically
   - B) Notify user/admin
   - C) Log only
   - D) Multiple of above

3. **Anti-Detection Configuration**:
   - A) Always enabled globally
   - B) Config-gated (per environment)
   - C) Config-gated (per platform)

### Risks Identified:
1. Test drift - tests may target different API
2. Playwright Python API mismatch - `pressSequentially()` may not exist
3. Persistence collisions - in-memory vs jobstore conflicts

### Guardrails (from Metis):
- MUST NOT: Add proxy rotation, CAPTCHA solving, or bot-fingerprint services
- MUST NOT: Add new tables unless explicitly required
- MUST: Define exact scope boundaries for each enhancement
- MUST: Add explicit acceptance criteria for restart resilience

## Research In Progress:
- [ ] Validate Playwright Python API for `pressSequentially()` 
- [ ] Find all `add_job` calls and wait strategies
- [ ] Check existing reminder models in database

## Open Questions for User:
1. Which scheduler persistence strategy do you prefer?
2. What should happen when a job is missed?
3. Should anti-detection be globally enabled or configurable?

## Scope Boundaries:
### IN:
- Enhanced stealth scripts in BrowserManager
- Scheduler event listeners (MISSED handling)
- SQLAlchemy job store integration
- Smart waiting optimization
- Test updates for new APIs

### OUT:
- No new API endpoints
- No UI changes
- No proxy/CAPTCHA services
- No new database tables (unless persistence strategy requires)
