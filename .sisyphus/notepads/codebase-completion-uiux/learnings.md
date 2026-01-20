# Learnings - Codebase Completion & UI/UX Enhancement

## Backend testing + JWT utilities
- Pytest on Windows can choke on dotted test filenames (e.g. `test_auth.test.py`) when using importlib mode; adding `--import-mode=importlib` and ensuring `tests/` is a package avoids collection/import weirdness.
- For coverage targeting, `pytest-cov` expects dotted module paths (e.g. `--cov=src.utils.token_manager`) rather than filesystem paths; module targets make coverage collection reliable.
- Keeping JWT refresh logic in a small `TokenManager` (pure token verification + rotation) makes it easy to unit test without DB/session dependencies.

## [2026-01-19T18:09] Task 2: Frontend Testing Framework

**Completed**: ✅
- Created Button.test.tsx with 4 passing tests
- Implemented Button.tsx component with TypeScript
- Created Button.module.css for styling
- Coverage: 100% for Button component
- Tests: 12 passed (including existing ui/Button tests)

**Key Learnings**:
- Vitest already installed and configured
- React Testing Library patterns working well
- CSS Modules path: ../styles/components/Button.module.css
- Test pattern: RED-GREEN-REFACTOR workflow validated

## [2026-01-20T07:35] Task 3: Configure Test Coverage and CI

**Completed**: ✅
- Test coverage infrastructure already fully configured
- package.json has all required scripts: test:coverage, test:unit, test:watch
- vitest.config.ts properly configured with v8 provider and thresholds (80/75/80/80)
- test-utils/setup.ts exists with comprehensive mocks (IntersectionObserver, ResizeObserver, matchMedia, localStorage, sessionStorage)
- Coverage command generates reports successfully
- Button.tsx: 100% coverage verified

**Key Learnings**:
- Test infrastructure was already production-ready (no changes needed)
- Coverage thresholds: 80% statements, 75% branches, 80% functions, 80% lines
- Pre-existing test issues:
  - E2E tests (10 files) fail when run through vitest (meant for Playwright runner)
  - Settings.test.tsx has 4 failing tests due to mock issues
  - PasswordReset tests fail due to missing @/components/ui/Button import
- These are pre-existing issues, not introduced by Task 3
- Running single test file causes threshold warnings (expected)

## [2026-01-20T07:45] Task 4: Enhance JWT Security

**Completed**: ✅
- Created rate limiter middleware at src/middleware/rate_limiter.py
- Created comprehensive JWT security tests at tests/test_jwt_security.py
- All 9 tests pass, verifying:
  - Expired access tokens are rejected
  - Expired refresh tokens are rejected
  - Valid refresh tokens create new token pairs
  - Wrong token types are rejected
  - Empty/invalid subjects are rejected
- Rate limiter supports auth (10/min), general (60/min), and strict (5/min) limits

**Key Learnings**:
- TokenManager.refresh_tokens is async - must use pytest.mark.asyncio and await
- Config has rate_limit_api_per_minute, not rate_limit_general_per_minute
- Rate limiter module-level config variables need to handle missing config values gracefully
- JWT token validation properly rejects expired tokens with ValueError

## [2026-01-20T07:50] Task 5: Complete Frontend Auth UI

**Completed**: ✅
- Created AuthContext.tsx with comprehensive auth state management
- Enhanced Login.tsx with react-hook-form and Zod validation
- Created AuthContext tests (4/4 passing)
- Created renderWithRouter test utility
- Form validation now catches invalid email format

**Key Learnings**:
- react-hook-form with Zod resolver provides clean form validation
- AuthContext handles login, logout, register, and session persistence
- Test mocks for authService need careful setup for async operations
- Use waitFor for async state updates in tests
- Import paths in tests: from `frontend/src/contexts/__tests__/` use `../AuthContext` not `../../src/contexts/AuthContext`

## [2026-01-20T07:55] Task 6: Add Auth Error Handling

**Completed**: ✅
- ErrorBoundary component already existed (production-ready)
- Created comprehensive error types in src/types/errors.ts
- Created error handling tests (25/25 passing)
- Error types: NetworkError, AuthenticationError, AuthorizationError, ValidationError, NotFoundError, ServerError
- Helper functions: createApiError, getUserFriendlyErrorMessage, parseApiError

**Key Learnings**:
- ErrorBoundary already implemented with user-friendly error display
- Error types should not expose sensitive technical details to users
- createApiError factory maps HTTP status codes to appropriate error types
- getUserFriendlyErrorMessage provides safe error messages for users
- parseApiError handles various API error response formats

