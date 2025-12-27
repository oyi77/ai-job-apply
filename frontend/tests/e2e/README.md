# E2E Testing Guide

This directory contains end-to-end (E2E) tests for the AI Job Application Assistant using Playwright.

## Overview

E2E tests verify complete user workflows from frontend to backend, ensuring:
- Complete user journeys work end-to-end
- Frontend-backend integration is correct
- User experience is validated
- Regression prevention

## Test Structure

```
tests/e2e/
├── fixtures/          # Test data and fixtures
│   └── test-data.ts   # Test users, applications, resumes, jobs
├── utils/             # Test utilities and helpers
│   ├── auth-helpers.ts    # Authentication utilities
│   ├── api-helpers.ts     # API request helpers
│   ├── page-helpers.ts    # Page interaction helpers
│   └── index.ts          # Utility exports
├── auth.spec.ts        # Authentication flow tests
├── applications.spec.ts # Application management tests
├── resumes.spec.ts     # Resume management tests
├── job-search.spec.ts  # Job search tests
├── ai-features.spec.ts # AI features tests
├── analytics.spec.ts   # Analytics tests
├── dashboard.spec.ts   # Dashboard tests
├── navigation.spec.ts  # Navigation tests
├── global-setup.ts     # Global test setup
└── global-teardown.ts  # Global test teardown
```

## Running Tests

### Run all E2E tests
```bash
cd frontend
npm run test:e2e
```

### Run tests in UI mode
```bash
npm run test:e2e:ui
```

### Run tests in headed mode (see browser)
```bash
npm run test:e2e:headed
```

### Run specific test file
```bash
npx playwright test tests/e2e/auth.spec.ts
```

### Run tests in specific browser
```bash
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit
```

## Test Environment

### Prerequisites
- Backend server running on port 8000
- Frontend server running on port 5173
- Test database configured

### Environment Variables
- `BACKEND_URL`: Backend API URL (default: http://localhost:8000)
- `FRONTEND_URL`: Frontend URL (default: http://localhost:5173)
- `TEST_DATABASE_URL`: Test database URL
- `CI`: Set to 'true' in CI environment

### Automatic Server Startup
Playwright config automatically starts both backend and frontend servers for testing. In CI, servers are always started. Locally, existing servers are reused if available.

## Test Coverage

### Authentication Flow
- ✅ Login page display
- ✅ User registration
- ✅ Login with valid/invalid credentials
- ✅ Logout functionality
- ✅ Protected route access
- ✅ Token refresh (if implemented)

### Application Management
- ✅ View applications list
- ✅ Create new application
- ✅ View application details
- ✅ Update application
- ✅ Delete application
- ✅ Filter and search applications
- ✅ Update application status

### Resume Management
- ✅ View resumes list
- ✅ Upload resume
- ✅ View resume details
- ✅ Set default resume
- ✅ Delete resume

### Job Search
- ✅ Search for jobs
- ✅ Filter jobs by location
- ✅ View job details
- ✅ Save job
- ✅ Create application from job

### AI Features
- ✅ Resume optimization
- ✅ Cover letter generation
- ✅ Job match analysis
- ✅ AI service fallback handling

### Analytics
- ✅ View analytics dashboard
- ✅ Display statistics
- ✅ Display charts
- ✅ Filter by date range
- ✅ Export functionality

## Writing Tests

### Test Structure
```typescript
import { test, expect } from '@playwright/test';
import { loginAsUser, waitForLoadingToComplete } from './utils';

test.describe('Feature Name', () => {
  test.beforeEach(async ({ page }) => {
    // Setup: Mock authentication, navigate to page
    await page.goto('/login');
    await page.evaluate(() => {
      localStorage.setItem('token', 'mock-token');
    });
  });

  test('should do something', async ({ page }) => {
    // Arrange
    await page.goto('/feature');
    
    // Act
    await page.click('button');
    
    // Assert
    await expect(page).toHaveURL(/.*success/);
  });
});
```

### Using Test Utilities

#### Authentication Helpers
```typescript
import { loginAsUser, logout, setAuthToken } from './utils';

// Login as test user
await loginAsUser(page, 'valid');

// Logout
await logout(page);

// Set auth token directly
await setAuthToken(page, 'token', { id: '1', email: 'test@example.com' });
```

#### Page Helpers
```typescript
import { waitForLoadingToComplete, waitForToast, fillFieldWithRetry } from './utils';

// Wait for page to load
await waitForLoadingToComplete(page);

// Wait for toast notification
await waitForToast(page, /success/i);

// Fill field with retry
await fillFieldWithRetry(page, 'input[name="email"]', 'test@example.com');
```

#### API Helpers
```typescript
import { apiRequest, getAuthToken } from './utils';

// Make API request
const response = await apiRequest(request, 'GET', '/api/v1/applications', {
  token: 'auth-token'
});

// Get auth token
const token = await getAuthToken(request, 'email@example.com', 'password');
```

### Best Practices

1. **Use test fixtures**: Import test data from `fixtures/test-data.ts`
2. **Wait for elements**: Always wait for elements to be visible before interacting
3. **Handle async operations**: Use `waitForLoadingToComplete` after actions
4. **Check for errors**: Verify error handling and user feedback
5. **Use selectors carefully**: Prefer data-testid, role, or text over CSS classes
6. **Clean up**: Clear authentication and test data after tests
7. **Handle flakiness**: Use retries and timeouts appropriately

## Debugging Tests

### View Test Report
```bash
npx playwright show-report
```

### Debug Mode
```bash
npx playwright test --debug
```

### Screenshots
Screenshots are automatically taken on failure. Check `tests/e2e/screenshots/` directory.

### Videos
Videos are recorded for failed tests. Check `test-results/` directory.

### Trace Viewer
```bash
npx playwright show-trace trace.zip
```

## CI/CD Integration

E2E tests run automatically in CI/CD pipeline:
- On push to main/develop branches
- On pull requests
- On manual workflow dispatch

Test results are uploaded as artifacts:
- Playwright HTML report
- Screenshots (on failure)
- Test videos (on failure)

## Troubleshooting

### Tests fail in CI but pass locally
- Check environment variables
- Verify backend/frontend servers start correctly
- Check test database setup
- Review CI logs for errors

### Tests are flaky
- Increase timeouts
- Add proper waits for async operations
- Use `waitForLoadingToComplete` after actions
- Check for race conditions

### Backend not starting
- Verify Python dependencies installed
- Check database connection
- Review backend logs
- Ensure port 8000 is available

### Frontend not starting
- Verify Node.js dependencies installed
- Check for build errors
- Review frontend logs
- Ensure port 5173 is available

## Maintenance

### Adding New Tests
1. Create test file in `tests/e2e/`
2. Follow existing test patterns
3. Use test utilities from `utils/`
4. Add test data to `fixtures/test-data.ts` if needed
5. Update this README

### Updating Test Data
Edit `fixtures/test-data.ts` to add or modify test data.

### Updating Utilities
Edit files in `utils/` directory. Ensure changes are backward compatible.

## Resources

- [Playwright Documentation](https://playwright.dev/)
- [Playwright Best Practices](https://playwright.dev/docs/best-practices)
- [Test Generator](https://playwright.dev/docs/codegen)
