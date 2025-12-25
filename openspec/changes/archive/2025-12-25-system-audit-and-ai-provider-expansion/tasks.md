# Tasks: System Audit and AI Provider Expansion

## 1. Backend Audit & Quality Assurance
- [x] 1.1 Run baseline backend tests: `pytest backend/tests/`
- [x] 1.2 Resolve all existing errors in backend unit tests
- [x] 1.3 Resolve all existing errors in backend integration tests
- [x] 1.4 Add unit tests for `AIProviderManager` to ensure robust provider switching
- [x] 1.5 Run type checks and fix all `mypy` errors in `backend/src/`
- [x] 1.6 Run linting and fix all formatting issues using `make fix-quality`

## 2. AI Provider Expansion
- [x] 2.1 Enhance `OpenAIProvider` to ensure full coverage of `AIProvider` abstract methods
- [x] 2.2 Implement `OpenRouterProvider` in `backend/src/services/providers/openrouter_provider.py`
- [x] 2.3 Update `Settings` model in `backend/src/config.py` to include OpenRouter configuration
- [x] 2.4 Register `OpenRouterProvider` in `AIProviderManager.initialize()`
- [x] 2.5 Add unit tests for `OpenRouterProvider` (mocked API calls)
- [x] 2.6 Verify `AIProviderManager` fallback logic between Gemini, OpenAI, and OpenRouter

## 3. Frontend Audit & UI Functionality
- [x] 3.1 Run baseline frontend tests: `npm test` in `frontend/`
- [x] 3.2 Resolve any failing component tests or hook tests
- [x] 3.3 Add OpenRouter configuration fields to `Settings.tsx`
- [x] 3.4 Verify end-to-end functionality of all pages:
    - [x] Dashboard: Data loading and visualization
    - [x] Applications: CRUD operations and status transitions
    - [x] Resumes: Upload, parsing, and management
    - [x] Cover Letters: Generation and editing
    - [x] Job Search: Multi-platform search and matching
    - [x] AI Services: Optimization and analysis tools
- [x] 3.5 Run `tsc` check for frontend and fix all TypeScript errors

## 4. Final System Verification
- [x] 4.1 Execute full test suite with 95%+ backend and 90%+ frontend coverage
- [x] 4.2 Perform manual end-to-end walkthrough of the primary user journeys
- [x] 4.3 Verify 0 errors in browser console during application usage
- [x] 4.4 Final check of "0 error" status across all logged services
