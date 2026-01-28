# Learnings for Comprehensive Test Plan

## Conventions
- Use `pytest-asyncio` for async tests.
- Use `unittest.mock.patch` for dependencies.
- Fixtures are located in `backend/tests/conftest.py` (assumed) or defined in test files.
- Tests follow AAA pattern (Arrange, Act, Assert).

## Gotchas
- `TestClient` from `fastapi.testclient` might not support `json` parameter in `delete` method in older versions, but typically `httpx` based clients do. The current code says `# TestClient doesn't support json parameter for DELETE`. I should check if I can use `request` method or if I need to mock the service call regardless of the client limitation if I am unit testing the service logic mostly. Wait, these are endpoint tests, so they use TestClient. If TestClient DELETE doesn't support body, I might need to use `client.request("DELETE", url, json=...)`.

## Decisions
- Will focus on `backend/tests/unit/test_resume_endpoints.py` first.

## Cover Letter Generation Bug Fix (2026-01-28)

### Bug Description
- **Issue**: AI cover letter generation was blocked when user did NOT select a Job Application
- **Root Cause**: Hard gate `if (selectedResume && selectedJob)` at line 181 required both resume AND selected job
- **Impact**: "Custom job details" flow (filling Job Title/Company manually) was impossible

### Solution Implemented
1. **Removed hard gate on selectedJob**: Changed condition to `if (selectedResume && jobTitle && company)`
   - Allows generation with form-filled job details (custom flow)
   - Still supports selected application flow (selectedJob)

2. **Added generatedJobInfo state**: New state to track job title/company from latest generation
   - Stores: `{ job_title: string; company: string }`
   - Populated in `handleGenerateCoverLetter` after mutation starts
   - Used by Save button instead of `selectedJob?.job_title/company`

3. **Fixed Save button logic**: Changed from `selectedJob?.job_title` to `generatedJobInfo?.job_title`
   - Works for both flows: selected application AND custom job details
   - Persists correct job info regardless of how generation was triggered

4. **Clear state on modal close**: Added cleanup in three places:
   - Modal `onClose` handler
   - Cancel button click
   - After successful save
   - Prevents stale data from previous generations

### Files Modified
- `frontend/src/pages/CoverLetters.tsx` (lines 49, 181-210, 754-759, 847-860, 891-896)

### Testing Notes
- E2E flow now works: Resume → Job Title/Company (no selection) → Generate → Save
- Backward compatible: Selected application flow still works
- State cleanup prevents modal reuse issues

### Pattern Applied
- **State management**: Local component state for generation context
- **Conditional rendering**: Guard checks form fields instead of just selectedJob
- **Cleanup pattern**: Clear all generation state on modal close/reset

## InputProps Compatibility Fix (2026-01-28)

### Problem
- `InputProps` type only supported controlled mode with `onChange?: (value: string) => void`
- React Hook Form's `register()` provides `onChange(event)` and `onBlur(event)` handlers
- Type mismatch caused build errors in Login.tsx, AutoApply.tsx, EmailSettingsForm.tsx

### Solution Implemented
1. **Extended InputProps interface**:
   - Now extends `Omit<React.InputHTMLAttributes<HTMLInputElement>, 'onChange' | 'ref' | 'size'>`
   - Supports both callback patterns: `(value: string) => void` and `(event: React.ChangeEvent) => void`
   - Added standard HTML attributes: `min`, `max`, `minLength`, `maxLength`, `pattern`, `step`, `autoComplete`, `autoFocus`, `readOnly`, `tabIndex`

2. **Updated Input.tsx handleChange**:
   - Detects callback signature and calls appropriately
   - Falls back to event pattern if value pattern fails
   - Maintains backward compatibility with existing controlled usage

3. **Fixed usage patterns**:
   - React Hook Form: `<Input {...register('email')} />` (no explicit name prop)
   - Controlled: `<Input name="field" value={val} onChange={(v) => setVal(v)} />`
   - Both patterns now work seamlessly

### Files Modified
- `frontend/src/types/index.ts` (InputProps interface)
- `frontend/src/components/ui/Input.tsx` (handleChange logic)
- `frontend/src/pages/Login.tsx` (removed duplicate name prop)
- `frontend/src/pages/AutoApply.tsx` (added missing name props)
- `frontend/src/components/forms/EmailSettingsForm.tsx` (added missing name prop)

### Key Learnings
- **Union types for callbacks**: Support multiple callback signatures with union types
- **Omit for conflicts**: Use `Omit` to exclude conflicting HTML attributes (size, onChange, ref)
- **Backward compatibility**: Always maintain support for existing usage patterns
- **Type safety with flexibility**: Can achieve both strict typing and flexible APIs

### Testing Notes
- Build now passes without Input-related TypeScript errors
- Both React Hook Form and controlled usage patterns work
- No breaking changes to existing components
