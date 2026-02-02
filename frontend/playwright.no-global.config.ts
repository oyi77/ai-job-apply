import { defineConfig, devices } from '@playwright/test';

import path from 'path';

// Backend URL from environment or default
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';
const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:5173';

export default defineConfig({
  // NOTE: No globalSetup for standalone tests
  testDir: './tests/e2e',
  fullyParallel: false, // Disable parallel to avoid conflicts
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: 1,
  timeout: 60 * 1000, // 60 seconds per test
  expect: {
    timeout: 10000, // 10 seconds for assertions
  },
  reporter: process.env.CI
    ? [['html'], ['junit', { outputFile: 'test-results/junit.xml' }]]
    : 'html',
  use: {
    baseURL: FRONTEND_URL,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    actionTimeout: 10000, // 10 seconds for actions
    navigationTimeout: 30000, // 30 seconds for navigation
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  webServer: [
    // Backend server
    {
      command: 'cd ../backend && python -m uvicorn src.api.app:app --host 0.0.0.0 --port 8000',
      url: `${BACKEND_URL}/health`,
      reuseExistingServer: !process.env.CI,
      timeout: 120 * 1000,
      env: {
        ...process.env,
        DATABASE_URL: process.env.TEST_DATABASE_URL || 'sqlite+aiosqlite:///./test.db',
        ENVIRONMENT: 'test',
        RATE_LIMIT_ENABLED: 'false',
      },
    },
    // Frontend server
    {
      command: 'npm run dev',
      url: FRONTEND_URL,
      reuseExistingServer: !process.env.CI,
      timeout: 120 * 1000,
    },
  ],
});
