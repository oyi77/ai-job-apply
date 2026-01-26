# ✅ PLAN GENERATED: Codebase Completion & UI/UX Enhancement

## 🎯 Plan Status: APPROVED BY MOMUS

**Metis Review**: Plan was **REJECTED**, **FIXED**, and **RESUBMITTED** for high accuracy review.

Momus identified critical issues that I fixed:
1. **Incomplete TODO list** - Fixed truncated plan, added all tasks
2. **Invalid test references** - Corrected paths to match actual repo structure  
3. **Missing implementation details** - Added specific config, packages, and verification procedures
4. **Ambiguous acceptance criteria** - Made all tests repeatable and measurable

---

## 📋 Plan Summary

### **Objective**
Complete Phase 2 features and enhance UI/UX with a balanced approach, following TDD methodology to achieve 95%+ test coverage.

### **User Decisions Confirmed**
- **Testing**: TDD (Test-Driven Development)
- **UI/UX**: Balanced approach (Visual + Accessibility + Mobile)
- **Email**: Mailgun service
- **Animations**: Framer Motion

### **Scope Boundaries**
- **IN**: Phase 2 completion, TDD testing, UI/UX enhancements, Mailgun integration
- **OUT**: Phase 3 enterprise features, mobile app, major architecture changes

### **Guardrails Applied**
- Prevent scope creep to Phase 3
- Maintain backward compatibility with existing API
- Don't break existing authentication flow
- Ensure 100% TypeScript coverage

---

## 🚀 Ready to Execute

**Plan Location**: `.sisyphus/plans/codebase-completion-uiux.md`

The plan includes **30 detailed TODOs** organized in **8 phases**:

1. **Testing Infrastructure Setup** (Tasks 1-3)
2. **Authentication System Completion** (Tasks 4-6) 
3. **Email Notification System** (Tasks 7-12)
4. **Advanced Analytics Dashboard** (Tasks 13-16)
5. **UI/UX Component Enhancements** (Tasks 17-25)
6. **Mobile Experience Optimization** (Tasks 26-30)
7. **Critical Component Testing** (Tasks 31-32)
8. **Final Integration & Quality Assurance** (Tasks 33-35)

Each task includes:
- **TDD RED-GREEN-REFACTOR workflow**
- **Exact file references** (corrected for repo structure)
- **Measurable acceptance criteria** with specific commands
- **Parallelization strategy** for efficient execution
- **Must NOT do** guardrails

---

## 🎯 Next Steps

**To begin execution, run:**
```bash
/start-work
```

This will:
1. Register the plan as your active boulder
2. Begin systematic execution of TODOs
3. Track progress across the 8 phases
4. Ensure 95%+ test coverage via TDD workflow

---

## 🏆 Quality Assurance

The plan follows **Momus high-accuracy standards**:
- ✅ Complete TODO list (no truncation)
- ✅ Valid file references (matched to repo structure)
- ✅ Executable verification procedures
- ✅ Clear guardrails and scope boundaries
- ✅ User decisions incorporated (TDD, Mailgun, Balanced UI/UX)

---

---

## 📝 EXECUTABLE TODO LIST

### **Phase 1: Testing Infrastructure Setup** (Tasks 1-3)

- [x] **1. Setup Backend Testing Framework**
  - **RED**: Write failing test `tests/test_auth.test.py` for JWT token refresh
  - **GREEN**: Implement `src/utils/token_manager.py` with refresh logic
  - **REFACTOR**: Extract validation into `src/validators/auth_validators.py`
  - **Verification**: `pytest tests/ -v --cov=src` → 95% coverage
  - **Files**: `tests/test_auth.test.py`, `src/utils/token_manager.py`, `src/validators/auth_validators.py`
  - **Parallelizable**: YES (independent from frontend tasks)
  - **MUST NOT**: Break existing login flow

- [x] **2. Setup Frontend Testing Framework**
  - **RED**: Write failing test `src/components/__tests__/Button.test.tsx` for UI component
  - **GREEN**: Implement `src/components/Button.tsx` with proper TypeScript types
  - **REFACTOR**: Extract styling to `src/styles/components/Button.module.css`
  - **Verification**: `npm test -- --coverage --watchAll=false` → 90% frontend coverage
  - **Files**: `src/components/Button.test.tsx`, `src/components/Button.tsx`, `src/styles/components/Button.module.css`
  - **Parallelizable**: YES (with Task 1)
  - **MUST NOT**: Use `any` types or suppress TypeScript errors

- [x] **3. Configure Test Coverage and CI**
  - **RED**: Test coverage command fails
  - **GREEN**: Update `package.json` with test scripts, configure `vitest.config.ts`
  - **REFACTOR**: Extract common test utilities to `src/test-utils/setup.ts`
  - **Verification**: `npm run test:coverage` → Generates coverage report
  - **Files**: `package.json`, `vitest.config.ts`, `src/test-utils/setup.ts`
  - **Parallelizable**: NO (depends on Tasks 1-2)
  - **MUST NOT**: Skip coverage for critical auth paths

### **Phase 2: Authentication System Completion** (Tasks 4-6)

- [x] **4. Enhance JWT Security**
  - **RED**: Security test fails for token expiration
  - **GREEN**: Update `src/auth/jwt_handler.py` with secure token handling
  - **REFACTOR**: Extract rate limiting to `src/middleware/rate_limiter.py`
  - **Verification**: `pytest tests/test_jwt_security.py -v` → 9/9 pass
  - **Files**: `src/middleware/rate_limiter.py`, `tests/test_jwt_security.py`
  - **Parallelizable**: YES (independent feature)
  - **MUST NOT**: Log out existing valid sessions

- [x] **5. Complete Frontend Auth UI**
  - **RED**: Component test fails for protected routes
  - **GREEN**: Enhance `src/pages/Login.tsx` with form validation
  - **REFACTOR**: Extract auth context to `src/contexts/AuthContext.tsx`
  - **Verification**: `npx vitest run src/contexts/__tests__/AuthContext.test.tsx` → 4/4 pass
  - **Files**: `src/pages/Login.tsx`, `src/contexts/AuthContext.tsx`
  - **Parallelizable**: YES (with Task 4)
  - **MUST NOT**: Break existing auth state management

- [x] **6. Add Auth Error Handling**
  - **RED**: Error test fails for network failures
  - **GREEN**: Implement error boundaries in `src/components/ErrorBoundary.tsx`
  - **REFACTOR**: Extract error types to `src/types/errors.ts`
  - **Verification**: `npx vitest run src/components/__tests__/ErrorHandling.test.tsx` → 25/25 pass
  - **Files**: `src/components/ErrorBoundary.tsx`, `src/types/errors.ts`
  - **Parallelizable**: NO (depends on Task 5)
  - **MUST NOT**: Expose sensitive error details to users

### **Phase 3: Email Notification System** (Tasks 7-12)

- [x] **7. Setup Mailgun Integration**
  - **RED**: Email service test fails
  - **GREEN**: Implement `src/services/mailgun_client.py` with API integration
  - **REFACTOR**: Extract config to `src/config/email_config.py`
  - **Verification**: `pytest tests/test_mailgun_client.py -v` → 16/16 pass
  - **Files**: `src/services/mailgun_client.py`, `src/config.py` (updated)
  - **Parallelizable**: YES (independent service)
  - **MUST NOT**: Hardcode API keys or credentials

- [x] **8. Create Email Templates**
  - **RED**: Template rendering test fails
  - **GREEN**: Implement `src/services/email_templates.py` with 6 templates
  - **REFACTOR**: Extract template assets to `src/templates/assets/`
  - **Verification**: `pytest tests/test_email_templates.py -v` → 15/15 pass
  - **Files**: `src/services/email_templates.py` (6 templates: follow_up, status_check, interview_prep, password_reset, application_confirmation, welcome)
  - **Parallelizable**: YES (with Task 7)
  - **MUST NOT**: Allow template injection attacks

- [x] **9. Backend Notification Endpoints**
  - **RED**: API endpoint test fails
  - **GREEN**: Add `/api/v1/notifications/email` endpoint in `src/api/v1/notifications.py`
  - **REFACTOR**: Extract validation to `src/validators/notification_validators.py`
  - **Verification**: `pytest tests/test_notifications.py -v` → 16/16 pass
  - **Files**: `src/api/v1/notifications.py`, `src/validators/notification_validators.py`
  - **Parallelizable**: YES (with Tasks 7-8)
  - **MUST NOT**: Allow unauthenticated email sending

- [x] **10. Frontend Email Settings UI**
  - **RED**: Component test fails for email preferences
  - **GREEN**: Create `src/pages/Settings.tsx` with email notification controls
  - **REFACTOR**: Extract form to `src/components/EmailSettingsForm.tsx`
  - **Verification**: UI updates email preferences successfully
  - **Files**: `src/pages/Settings.tsx`, `src/components/EmailSettingsForm.tsx`
  - **Parallelizable**: YES (with Task 9)
  - **MUST NOT**: Allow invalid email addresses

- [x] **11. Web Push Notifications**
  - **RED**: Push notification test fails
  - **GREEN**: Implement `src/services/push_service.py` with Web Push Protocol
  - **REFACTOR**: Extract subscription management to `src/models/push_subscription.py`
  - **Verification**: Browser receives push notification
  - **Files**: `src/services/push_service.py`, `src/models/push_subscription.py`
  - **Parallelizable**: YES (with Tasks 7-10)
  - **MUST NOT**: Send push to unsubscribed users

- [x] **12. Notification Integration Tests**
  - **RED**: Integration test fails for full email+push flow
  - **GREEN**: Add `tests/test_notification_integration.py` with end-to-end tests
  - **REFACTOR**: Extract test fixtures to `tests/fixtures/notification_fixtures.py`
  - **Verification**: `pytest tests/test_notification_integration.py -v` → All pass
  - **Files**: `tests/test_notification_integration.py`, `tests/fixtures/notification_fixtures.py`
  - **Parallelizable**: NO (depends on Tasks 7-11)
  - **MUST NOT**: Send real notifications in unit tests

### **Phase 4: Advanced Analytics Dashboard** (Tasks 13-16)

- [x] **13. Upgrade Analytics Backend with AI**
  - **RED**: AI analytics test fails
  - **GREEN**: Replace hardcoded logic in `src/api/v1/analytics.py` with Gemini API
  - **REFACTOR**: Extract AI service to `src/services/gemini_client.py`
  - **Verification**: `/api/v1/skills-gap-analysis` returns AI-powered insights
  - **Files**: `src/api/v1/analytics.py`, `src/services/gemini_client.py`
  - **Parallelizable**: YES (independent service)
  - **MUST NOT**: Expose API keys in client-side code

- [x] **14. ML Statistical Trends**
  - **RED**: ML model test fails
  - **GREEN**: Implement `src/services/analytics_ml.py` with statistical analysis
  - **REFACTOR**: Extract data processing to `src/utils/data_processor.py`
  - **Verification**: Returns meaningful trend predictions
  - **Files**: `src/services/analytics_ml.py`, `src/utils/data_processor.py`
  - **Parallelizable**: YES (with Task 13)
  - **MUST NOT**: Process sensitive personal data without consent

- [ ] **15. Frontend Analytics Dashboard**
  - **RED**: Dashboard test fails
  - **GREEN**: Replace mock data in `src/pages/Analytics.tsx` with real API calls
  - **REFACTOR**: Extract charts to `src/components/charts/`
  - **Verification**: Dashboard displays real-time analytics data
  - **Files**: `src/pages/Analytics.tsx`, `src/components/charts/SkillsChart.tsx`
  - **Parallelizable**: YES (with Tasks 13-14)
  - **MUST NOT**: Show mock data in production

- [x] **16. Analytics Performance Optimization**
  - **RED**: Performance test fails (>2s load time)
  - **GREEN**: Add caching and optimization to analytics queries
  - **REFACTOR**: Extract caching logic to `src/services/cache_service.py`
  - **Verification**: Analytics dashboard loads in <500ms
  - **Files**: `src/services/cache_service.py`, optimized analytics queries
  - **Parallelizable**: NO (depends on Task 15)
  - **MUST NOT**: Cache sensitive user analytics data

### **Phase 5: UI/UX Component Enhancements** (Tasks 17-25)

- [x] **17. Design System Foundation**
  - **RED**: Design tokens test fails
  - **GREEN**: Create `src/styles/design-tokens.ts` with theme variables
  - **REFACTOR**: Extract theme to `src/styles/themes/light.ts`
  - **Verification**: Storybook displays consistent design system
  - **Files**: `src/styles/design-tokens.ts`, `src/styles/themes/light.ts`
  - **Parallelizable**: YES (independent styling)
  - **MUST NOT**: Break existing component styles

- [x] **18. Enhanced Typography**
  - **RED**: Typography test fails for consistency
  - **GREEN**: Update typography system in `src/styles/typography.css`
  - **REFACTOR**: Extract font loading to `src/styles/fonts.css`
  - **Verification**: All text uses consistent typography hierarchy
  - **Files**: `src/styles/typography.css`, `src/styles/fonts.css`
  - **Parallelizable**: YES (with Task 17)
  - **MUST NOT**: Load too many font variants affecting performance

- [x] **19. Component Library with Storybook**
  - **RED**: Storybook test fails
  - **GREEN**: Setup Storybook with component documentation
  - **REFACTOR**: Extract component stories to `src/components/.storybook/`
  - **Verification**: `npm run storybook` → All components documented
  - **Files**: Storybook configuration, component stories
  - **Parallelizable**: YES (with Tasks 17-18)
  - **MUST NOT**: Include sensitive data in Storybook

- [x] **20. Enhanced Navigation**
  - **RED**: Navigation test fails for accessibility
  - **GREEN**: Improve `src/components/Navigation.tsx` with ARIA labels
  - **REFACTOR**: Extract navigation logic to `src/hooks/useNavigation.ts`
  - **Verification**: Navigation is fully keyboard accessible
  - **Files**: `src/components/layout/Sidebar.tsx`, `src/hooks/useNavigation.ts`
  - **Parallelizable**: YES (with Tasks 17-19)
  - **MUST NOT**: Break existing navigation patterns

- [x] **21. Improved Forms**
  - **RED**: Form validation test fails
  - **GREEN**: Enhance forms in `src/components/Forms/` with Zod validation
  - **REFACTOR**: Extract validation schemas to `src/schemas/`
  - **Verification**: Forms show real-time validation feedback
  - **Files**: Enhanced form components, validation schemas
  - **Parallelizable**: YES (with Task 20)
  - **MUST NOT**: Allow form submission with invalid data

- [x] **22. Loading States & Skeletons**
  - **RED**: Loading state test fails
  - **GREEN**: Add skeleton components to `src/components/Skeletons/`
  - **REFACTOR**: Extract loading logic to `src/hooks/useLoadingState.ts`
  - **Verification**: Loading states appear consistently across the app
  - **Files**: Skeleton components, loading hooks
  - **Parallelizable**: YES (with Task 21)
  - **MUST NOT**: Show loading for <100ms requests

- [x] **23. Error State Improvements**
  - **RED**: Error state test fails
  - **GREEN**: Enhance error components in `src/components/Errors/`
  - **REFACTOR**: Extract error handling to `src/hooks/useErrorHandler.ts`
  - **Verification**: Error states are informative and actionable
  - **Files**: Error components, error handling hooks
  - **Parallelizable**: YES (with Task 22)
  - **MUST NOT**: Expose stack traces to users

- [x] **24. Interactive Elements**
  - **RED**: Interactive test fails
  - **GREEN**: Add Framer Motion animations to `src/components/Interactive/`
  - **REFACTOR**: Extract animations to `src/styles/animations.css`
  - **Verification**: Animations are smooth and performant
  - **Files**: Interactive components, animation definitions
  - **Parallelizable**: YES (with Task 23)
  - **MUST NOT**: Use animations that cause motion sickness

- [x] **25. Accessibility Audit**
  - **RED**: Accessibility test fails (WCAG < AA)
  - **GREEN**: Fix accessibility issues across all components
  - **REFACTOR**: Extract accessibility utilities to `src/utils/accessibility.ts`
  - **Verification**: `npm run test:a11y` → Passes WCAG AA standards
  - **Files**: Accessibility fixes, utility functions
  - **Parallelizable**: NO (depends on Tasks 17-24)
  - **MUST NOT**: Ignore any critical accessibility issues

### **Phase 6: Mobile Experience Optimization** (Tasks 26-30)

- [ ] **26. PWA Manifest Configuration**
  - **RED**: PWA test fails
  - **GREEN**: Create `public/manifest.json` with app metadata
  - **REFACTOR**: Extract PWA utilities to `src/utils/pwa.ts`
  - **Verification**: App can be installed to home screen
  - **Files**: `public/manifest.json`, `src/utils/pwa.ts`
  - **Parallelizable**: YES (independent mobile feature)
  - **MUST NOT**: Break existing mobile responsiveness

- [ ] **27. Service Worker for Offline**
  - **RED**: Offline test fails
  - **GREEN**: Implement `public/sw.js` with caching strategy
  - **REFACTOR**: Extract service worker logic to `src/services/worker.ts`
  - **Verification**: App works offline with cached content
  - **Files**: `public/sw.js`, `src/services/worker.ts`
  - **Parallelizable**: YES (with Task 26)
  - **MUST NOT**: Cache sensitive user data

- [ ] **28. Responsive Design Improvements**
  - **RED**: Responsive test fails on mobile devices
  - **GREEN**: Update responsive breakpoints in `src/styles/breakpoints.css`
  - **REFACTOR**: Extract responsive utilities to `src/utils/responsive.ts`
  - **Verification**: App works perfectly on devices 320px-2560px
  - **Files**: Updated responsive styles, utility functions
  - **Parallelizable**: YES (with Tasks 26-27)
  - **MUST NOT**: Use fixed pixels for mobile layouts

- [ ] **29. Touch Interactions**
  - **RED**: Touch interaction test fails
  - **GREEN**: Add touch gestures to mobile interactions
  - **REFACTOR**: Extract gesture logic to `src/hooks/useGestures.ts`
  - **Verification**: Touch interactions feel native on mobile
  - **Files**: Touch-enabled components, gesture hooks
  - **Parallelizable**: YES (with Task 28)
  - **MUST NOT**: Conflict with existing desktop interactions

- [ ] **30. Performance Optimization**
  - **RED**: Mobile performance test fails (>3s load time)
  - **GREEN**: Optimize assets, lazy load components, implement code splitting
  - **REFACTOR**: Extract optimization logic to `src/utils/performance.ts`
  - **Verification**: Lighthouse mobile score >90
  - **Files**: Optimized bundles, performance utilities
  - **Parallelizable**: NO (depends on Tasks 26-29)
  - **MUST NOT**: Defer critical above-the-fold content

### **Phase 7: Critical Component Testing** (Tasks 31-32)

- [ ] **31. Core Feature End-to-End Tests**
  - **RED**: E2E test fails for critical user flows
  - **GREEN**: Add Playwright tests for login, analytics, settings
  - **REFACTOR**: Extract test utilities to `tests/e2e/utils/`
  - **Verification**: `npm run test:e2e` → All critical flows pass
  - **Files**: E2E test suite, test utilities
  - **Parallelizable**: YES (independent testing phase)
  - **MUST NOT**: Skip testing any user-facing feature

- [ ] **32. Integration Test Coverage**
  - **RED**: Integration test coverage < 80%
  - **GREEN**: Add comprehensive integration tests
  - **REFACTOR**: Extract test data to `tests/fixtures/`
  - **Verification**: Overall test coverage > 95%
  - **Files**: Integration test suite, test fixtures
  - **Parallelizable**: YES (with Task 31)
  - **MUST NOT**: Use production data for testing

### **Phase 8: Final Integration & Quality Assurance** (Tasks 33-35)

- [ ] **33. Security Audit & Hardening**
  - **RED**: Security scan finds vulnerabilities
  - **GREEN**: Fix all security issues (XSS, CSRF, SQL injection)
  - **REFACTOR**: Extract security middleware to `src/middleware/security.py`
  - **Verification**: Security scan passes with zero critical issues
  - **Files**: Security fixes, security middleware
  - **Parallelizable**: YES (independent security focus)
  - **MUST NOT**: Ignore any security vulnerabilities

- [ ] **34. Performance & SEO Optimization**
  - **RED**: Performance score < 90, SEO score < 80
  - **GREEN**: Optimize bundle sizes, meta tags, semantic HTML
  - **REFACTOR**: Extract SEO utilities to `src/utils/seo.ts`
  - **Verification**: Lighthouse scores: Performance >90, SEO >90
  - **Files**: Optimized assets, SEO utilities, meta tags
  - **Parallelizable**: YES (with Task 33)
  - **MUST NOT**: Sacrifice accessibility for performance

- [ ] **35. Production Deployment & Monitoring**
  - **RED**: Production deployment fails
  - **GREEN**: Setup production deployment pipeline with monitoring
  - **REFACTOR**: Extract deployment config to `.github/workflows/`
  - **Verification**: Production deployment succeeds with monitoring
  - **Files**: Deployment pipeline, monitoring setup
  - **Parallelizable**: NO (final integration, depends on all tasks)
  - **MUST NOT**: Deploy without proper monitoring in place

---

**Status: READY FOR EXECUTION** ✅

---

*Generated: 2026-01-19*  
*Last updated by Momus review*  
*Quality: High Accuracy Mode Approved*  
*TODO Structure Added: Complete 35-item checklist*
