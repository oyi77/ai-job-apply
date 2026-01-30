/**
 * Auto-Apply End-to-End Test Suite Configuration
 * 
 * Playwright test suite for validating complete user workflows
 * including job search, application submission, and failure handling
 */

// REMOVED: import { test, expect } from '@playwright/test';

// Test configuration for auto-apply testing
export const autoApplyTestConfig = {
  // Base URL for application
  baseURL: process.env.BASE_URL || 'http://localhost:3000',

  // Test timeout (ms) - long enough for full cycle
  testTimeout: 120000, // 2 minutes per test

  // Retry configuration
  retries: 3,
  // retryDelay: 5000, // 5 seconds between retries

  // Browser configuration
  useHeadless: true,
  slowMo: 500, // Record video on failures (slow motion)
// REMOVED:   // viewport: { width: 1280, height: 720 },

  // Test data
  testUser: {
    email: 'test@example.com',
    password: 'testPassword123!',
// REMOVED:   },

  // Auto-apply configuration
  autoApply: {
    enabled: true,
    platforms: ['linkedin', 'indeed'],
    dailyLimit: {
      linkedin: 50,
      indeed: 100,
// REMOVED:     },
    hourlyLimit: {
      linkedin: 5,
      indeed: 10,
// REMOVED:     },
    jobSearchCriteria: {
      keywords: ['python', 'developer'],
      location: 'remote',
      experienceLevel: 'mid',
// REMOVED:     },
    maxApplications: 10, // Limit to prevent spam during testing
    expectSuccess: true, // Should succeed (no platform errors)
    expectRateLimitHit: false, // Don't expect rate limit during test
// REMOVED:   },
// REMOVED: };

// Test utilities
export const goToAutoApplyPage = async (page: Page) => {
  await page.goto(`${autoApplyTestConfig.baseURL}/auto-apply`);
  await page.waitForLoadState('networkidle');
  return page;
// REMOVED: };

export const loginAsTestUser = async (page: Page) => {
  await page.goto(`${autoApplyTestConfig.baseURL}/auth/login`);
  await page.fill('input[name="email"]', autoApplyTestConfig.testUser.email);
  await page.fill('input[name="password"]', autoApplyTestConfig.testUser.password);
  await page.click('button[type="submit"]');
  await page.waitForURL(`${autoApplyTestConfig.baseURL}/auto-apply`);
  return page;
// REMOVED: };

export const configureAutoApply = async (page: Page, config: typeof autoApplyTestConfig.autoApply) => {
  // Navigate to auto-apply configuration page
  await goToAutoApplyPage(page);

  // Enable auto-apply
  await page.check('input[type="checkbox"][name="enabled"]');
  await page.click('button[type="checkbox"][name="enabled"]');

  // Select platforms
  for (const platform of config.platforms) {
// REMOVED:     await page.check(`input[type="checkbox"][value="${platform}"]`);
// REMOVED:   }

  // Set job search criteria
  await page.fill('input[name="keywords"]', config.jobSearchCriteria.keywords.join(', '));
  await page.select('select[name="experienceLevel"]', config.jobSearchCriteria.experienceLevel);
  await page.fill('input[name="location"]', config.jobSearchCriteria.location);

  // Set application limits
  await page.fill('input[name="dailyLimit"][name="linkedin"]', String(config.dailyLimit.linkedin));
  await page.fill('input[name="hourlyLimit"][name="linkedin"]', String(config.hourlyLimit.linkedin));
  await page.fill('input[name="maxApplications"]', String(config.maxApplications));

  // Save configuration
  await page.click('button[type="submit"]');
  await page.waitForLoadState('networkidle');
// REMOVED: };

export const startAutoApplyCycle = async (page: Page) => {
  // Navigate to auto-apply page
  await goToAutoApplyPage(page);

  // Start auto-apply
  await page.click('button[type="submit"][value="start"]');

  // Wait for cycle to complete
  await page.waitForSelector('text="Cycle Complete"', { timeout: autoApplyTestConfig.testTimeout });

  return page;
// REMOVED: };

export const stopAutoApplyCycle = async (page: Page) => {
  // Navigate to auto-apply page
  await goToAutoApplyPage(page);

  // Stop auto-apply
  await page.click('button[type="submit"][value="stop"]');

  await page.waitForLoadState('networkidle');
// REMOVED: };

export const checkAutoApplyStatus = async (page: Page) => {
  // Navigate to auto-apply page
  await goToAutoApplyPage(page);

  // Check status
  const status = await page.locator('.auto-apply-status').textContent();
  const isActive = status.includes('Active');

  return {
    isActive,
    status,
// REMOVED:   };
// REMOVED: };

export const checkAppliedJobs = async (page: Page) => {
  // Navigate to auto-apply page
  await goToAutoApplyPage(page);

  // Get applied jobs list
  const jobs = await page.locator('.applied-jobs .job-item').all();

  return jobs;
// REMOVED: };

export const checkActivityLogs = async (page: Page) => {
  // Navigate to auto-apply page
  await goToAutoApplyPage(page);

  // Get activity logs
  const logs = await page.locator('.activity-logs .log-item').all();

  return logs;
// REMOVED: };

export const checkFailureLogs = async (page: Page) => {
  // Navigate to auto-apply page
  await goToAutoApplyPage(page);

  // Get failure logs
  const logs = await page.locator('.failure-logs .log-item').all();

  return logs;
// REMOVED: };

export const cleanupAfterTest = async (page: Page) => {
  // Logout
  await page.click('button[type="submit"][value="logout"]');

  // Clear browser state
  await page.context().clearCookies();
  await page.evaluate(() => {
    localStorage.clear();
    sessionStorage.clear();
// REMOVED:   });
// REMOVED: };

// Test helpers
export const waitForAutoApplyCycleComplete = async (page: Page, timeout: number = autoApplyTestConfig.testTimeout) => {
// REMOVED:   await expect(page.locator('.cycle-status')).toHaveText(/completed|stopped/i, { timeout });
// REMOVED: };

export const verifyJobApplied = async (page: Page, jobTitle: string) => {
// REMOVED:   await expect(page.locator(`.job-item:has-text("${jobTitle}")`).toBeVisible({ timeout });
// REMOVED: };

export const verifyApplicationCount = async (page: Page, expectedCount: number) => {
  const jobItems = await page.locator('.applied-jobs .job-item').count();
  await expect(jobItems).toBeGreaterThanOrEqual(expectedCount);
// REMOVED: };

export const verifyNoPlatformErrors = async (page: Page) => {
  const errorMessages = await page.locator('.error-message').all();
  await expect(errorMessages).toHaveLength(0);
// REMOVED: };

export const verifyRateLimitNotHit = async (page: Page, platform: string) => {
// REMOVED:   const rateLimitMessage = await page.locator(`.rate-limit-message:has-text("${platform}")`).count();
  await expect(rateLimitMessage).toBe(0);
// REMOVED: };

export const verifyActivityLogExists = async (page: Page, logMessage: string) => {
  const logItems = await page.locator('.activity-logs').all();
  const hasLog = logItems.some(item => 
    item.textContent().includes(logMessage)
  );

  await expect(hasLog).toBe(true);
// REMOVED: };

export const verifyFailureLogExists = async (page: Page, errorMessage: string) => {
  const logItems = await page.locator('.failure-logs').all();
  const hasLog = logItems.some(item => 
    item.textContent().includes(errorMessage)
  );

  await expect(hasLog).toBe(true);
// REMOVED: };

export const verifyAutoApplyConfig = async (page: Page, config: typeof autoApplyTestConfig.autoApply) => {
  await page.goto(`${autoApplyTestConfig.baseURL}/auto-apply`);

  // Verify auto-apply is enabled
// REMOVED:   await expect(page.locator('input[type="checkbox"][name="enabled"]')).toBeChecked({ timeout });

  // Verify platforms are selected
  for (const platform of config.platforms) {
// REMOVED:     await expect(page.locator(`input[type="checkbox"][value="${platform}"]`)).toBeChecked({ timeout });
// REMOVED:   }

  // Verify job search criteria
  await expect(page.locator('input[name="keywords"]')).toHaveValue(config.jobSearchCriteria.keywords.join(', '));
  await expect(page.locator('select[name="experienceLevel"]')).toHaveValue(config.jobSearchCriteria.experienceLevel);
  await expect(page.locator('input[name="location"]')).toHaveValue(config.jobSearchCriteria.location);

  // Verify application limits
  await expect(page.locator(`input[name="dailyLimit"][name="linkedin"]`)).toHaveValue(String(config.dailyLimit.linkedin));
  await expect(page.locator(`input[name="hourlyLimit"][name="linkedin"]`)).toHaveValue(String(config.hourlyLimit.linkedin));
  await expect(page.locator('input[name="maxApplications"]')).toHaveValue(String(config.maxApplications));

  // Save and reload
  const currentValue = await page.locator('input[name="maxApplications"]').inputValue();
  await page.click('button[type="submit"]');
  await page.waitForLoadState('networkidle');
  await expect(page.locator('input[name="maxApplications"]')).toHaveValue(currentValue);
// REMOVED: };

/**
 * Main test suite
 */
test.describe('Auto-Apply E2E Tests', () => {
// REMOVED:   test.beforeEach(async ({ page }) => {
    // Login as test user
    await loginAsTestUser(page);

    // Navigate to auto-apply page
    await goToAutoApplyPage(page);

    // Configure auto-apply for testing
    await configureAutoApply(page, autoApplyTestConfig.autoApply);
// REMOVED:   });

// REMOVED:   test.afterEach(async ({ page }) => {
    // Logout and cleanup
    await cleanupAfterTest(page);
// REMOVED:   });

// REMOVED:   test('Happy Path: User enables auto-apply and jobs applied successfully', async ({ page }) => {
    await configureAutoApply(page, autoApplyTestConfig.autoApply);

    // Start auto-apply cycle
    await startAutoApplyCycle(page);

    // Wait for cycle to complete
    await waitForAutoApplyCycleComplete(page);

    // Verify jobs were applied
    const jobs = await checkAppliedJobs(page);
    await expect(jobs.length).toBeGreaterThan(0);

    // Verify no errors
    await verifyNoPlatformErrors(page);

    // Verify rate limit not hit (for configured platforms)
    for (const platform of autoApplyTestConfig.autoApply.platforms) {
      await verifyRateLimitNotHit(page, platform);
// REMOVED:     }

    // Verify activity log created
    await verifyActivityLogExists(page, 'Auto-apply cycle completed');

    // Verify applied job count matches expected
    await verifyApplicationCount(page, autoApplyTestConfig.autoApply.maxApplications);
// REMOVED:   });

// REMOVED:   test('Rate Limit: Daily limit reached, applications blocked', async ({ page }) => {
    await loginAsTestUser(page);

    // Configure with aggressive limits
    const aggressiveConfig = {
      ...autoApplyTestConfig.autoApply,
// REMOVED:       dailyLimit: { linkedin: 2 }, // Very low limit to test rate limiting
// REMOVED:       hourlyLimit: { linkedin: 1 }, // Very low limit
      maxApplications: 100, // High number to trigger limit quickly
      expectRateLimitHit: true,
      expectSuccess: false, // Expect to hit rate limit
// REMOVED:     };

    await configureAutoApply(page, aggressiveConfig.autoApply);

    // Start auto-apply
    await startAutoApplyCycle(page);

    // Wait for cycle to stop (rate limit)
// REMOVED:     await expect(page.locator('.cycle-status')).toHaveText(/stopped|daily limit/i, { timeout: 30000 });

    // Verify rate limit message appears
// REMOVED:     await expect(page.locator('.rate-limit-message:has-text("daily limit")')).toBeVisible({ timeout });

    // Verify no jobs applied (blocked)
    const jobs = await checkAppliedJobs(page);
    await expect(jobs.length).toBe(0);

    // Verify activity log created
    await verifyActivityLogExists(page, 'Daily limit reached');

    // Verify failure log exists
    await verifyFailureLogExists(page, 'Daily limit reached');
// REMOVED:   });

// REMOVED:   test('Rate Limit: Hourly limit reached, applications blocked', async ({ page }) => {
    await loginAsTestUser(page);

    // Configure with aggressive hourly limit
    const aggressiveConfig = {
      ...autoApplyTestConfig.autoApply,
// REMOVED:       hourlyLimit: { linkedin: 1 }, // Very low limit
// REMOVED:       dailyLimit: { linkedin: 100 }, // High daily limit
      maxApplications: 100,
      expectRateLimitHit: true,
      expectSuccess: false,
// REMOVED:     };

    await configureAutoApply(page, aggressiveConfig.autoApply);

    // Start auto-apply multiple times (more than hourly limit)
    await startAutoApplyCycle(page);
    await startAutoApplyCycle(page); // Exceeds limit

    // Wait for cycle to stop (hourly limit)
// REMOVED:     await expect(page.locator('.cycle-status')).toHaveText(/stopped|hourly limit/i, { timeout: 30000 });

    // Verify rate limit message appears
// REMOVED:     await expect(page.locator('.rate-limit-message:has-text("hourly limit")')).toBeVisible({ timeout });
// REMOVED:   });

// REMOVED:   test('Platform Error: LinkedIn account banned (403 Forbidden)', async ({ page }) => {
    await loginAsTestUser(page);

    // Configure auto-apply
    await configureAutoApply(page, autoApplyTestConfig.autoApply);

    // Start auto-apply
    await startAutoApplyCycle(page);

    // Wait for error (simulate ban by API error)
// REMOVED:     await expect(page.locator('.error-message:has-text("403")')).toBeVisible({ timeout: 30000 });

    // Verify auto-apply disabled automatically
    const isEnabled = await page.locator('input[type="checkbox"][name="enabled"]').isChecked();
    await expect(isEnabled).toBe(false);

    // Verify failure log created
    await verifyFailureLogExists(page, 'Account banned');

    // Verify no jobs applied due to ban
    const jobs = await checkAppliedJobs(page);
    await expect(jobs.length).toBe(0);
// REMOVED:   });

// REMOVED:   test('Duplicate Detection: Same job not applied twice', async ({ page }) => {
    await loginAsTestUser(page);

    // Configure auto-apply
    await configureAutoApply(page, autoApplyTestConfig.autoApply);

    // Start auto-apply cycle
    await startAutoApplyCycle(page);

    // Wait for first cycle to complete
    await waitForAutoApplyCycleComplete(page);

    // Get applied jobs from first cycle
    const jobs = await checkAppliedJobs(page);
    const firstJobTitle = jobs.length > 0 ? await jobs[0].locator('.job-title').textContent() : '';

    // Start second cycle (should detect duplicate)
    await startAutoApplyCycle(page);

    // Wait for second cycle to complete
// REMOVED:     await waitForAutoApplyCycleComplete(page, { timeout: 30000 });

    // Verify job wasn't applied again
    const jobsAfterSecondCycle = await checkAppliedJobs(page);
    await expect(jobsAfterSecondCycle.length).toBe(jobs.length);

    // Verify activity log mentions duplicate detection
    await verifyActivityLogExists(page, 'Duplicate job detected');
// REMOVED:   });

// REMOVED:   test('Job Search Integration: Jobs found and filtered correctly', async ({ page }) => {
    await loginAsTestUser(page);

    // Navigate to auto-apply page
    await goToAutoApplyPage(page);

    // Verify job search results displayed
    const searchResults = await page.locator('.search-results .job-item').all();
    await expect(searchResults.length).toBeGreaterThan(0);

    // Verify jobs match search criteria
    for (const job of searchResults) {
      const jobTitle = await job.locator('.job-title').textContent();
      const jobLocation = await job.locator('.job-location').textContent();
      const jobExperience = await job.locator('.job-experience').textContent();

      expect(autoApplyTestConfig.jobSearchCriteria.keywords.some(kw => jobTitle.toLowerCase().includes(kw.toLowerCase()))).toBe(true);
      expect(jobLocation).toContain(autoApplyTestConfig.jobSearchCriteria.location.toLowerCase());
      expect(['entry', 'junior', 'mid', 'senior', 'lead']).toContain(jobExperience.toLowerCase());
// REMOVED:     }
// REMOVED:   });

// REMOVED:   test('Configuration Management: User updates auto-apply settings', async ({ page }) => {
    await loginAsTestUser(page);

    // Navigate to auto-apply page
    await goToAutoApplyPage(page);

    // Update configuration
    const newConfig = {
      ...autoApplyTestConfig.autoApply,
      platforms: ['linkedin', 'indeed', 'glassdoor'], // Add Glassdoor
      maxApplications: 20, // Increase limit
      jobSearchCriteria: {
        keywords: ['javascript', 'full-stack'], // Update keywords
        location: 'on-site', // Update location
        experienceLevel: 'senior', // Update experience
// REMOVED:       },
// REMOVED:     };

    await configureAutoApply(page, newConfig);

    // Save configuration
    await page.click('button[type="submit"]');
    await page.waitForLoadState('networkidle');

    // Navigate away and back to verify persistence
    await page.goto(`${autoApplyTestConfig.baseURL}/dashboard`);
    await page.goto(`${autoApplyTestConfig.baseURL}/auto-apply`);

    // Verify settings persisted
// REMOVED:     await expect(page.locator('input[type="checkbox"][value="glassdoor"]')).toBeChecked({ timeout });

    // Verify max applications updated
    await expect(page.locator('input[name="maxApplications"]')).toHaveValue(String(newConfig.maxApplications));
// REMOVED:   });

// REMOVED:   test('Failure Handling: Application fails and is retried correctly', async ({ page }) => {
    await loginAsTestUser(page);

    // Configure auto-apply
    await configureAutoApply(page, autoApplyTestConfig.autoApply);

    // Start auto-apply cycle
    await startAutoApplyCycle(page);

    // Wait for failure (simulate by bad session)
// REMOVED:     await expect(page.locator('.error-message:has-text("Invalid session")')).toBeVisible({ timeout: 15000 });

    // Verify auto-apply retry mechanism
    await page.waitForTimeout(3000); // Wait for retry delay
    await expect(page.locator('.error-message')).not.toBeVisible(); // Error should be cleared

    // Verify retry count in activity log
    await verifyActivityLogExists(page, 'Application retried');
// REMOVED:   });

// REMOVED:   test('Screenshot Capture: Failure screenshots saved to database', async ({ page }) => {
    await loginAsTestUser(page);

    // Configure auto-apply
    await configureAutoApply(page, autoApplyTestConfig.autoApply);

    // Force a failure (invalid credentials)
    await page.click('button[type="submit"][value="start"]'); // Start without valid session

    // Wait for error
// REMOVED:     await expect(page.locator('.error-message')).toBeVisible({ timeout: 10000 });

    // Verify screenshot was captured (check for screenshot in failure logs)
    await verifyActivityLogExists(page, 'Screenshot captured for error');

    // Verify screenshot file exists (if accessible via API)
    const logs = await checkFailureLogs(page);
    const hasScreenshot = logs.some(log => log.textContent().includes('.png'));
    await expect(hasScreenshot).toBe(true);
// REMOVED:   });

// REMOVED:   test('Clean State: New user with no history starts with empty auto-apply', async ({ page }) => {
    await loginAsTestUser(page);

    // Navigate to auto-apply page
    await goToAutoApplyPage(page);

    // Verify auto-apply is disabled by default
// REMOVED:     await expect(page.locator('input[type="checkbox"][name="enabled"]').not.toBeChecked({ timeout });

    // Verify no applied jobs
    const jobs = await checkAppliedJobs(page);
    await expect(jobs.length).toBe(0);

    // Verify no activity logs
    const logs = await checkActivityLogs(page);
    await expect(logs.length).toBe(0);

    // Verify failure logs
    const failures = await checkFailureLogs(page);
    await expect(failures.length).toBe(0);

    // Enable auto-apply and verify clean state
    await page.check('input[type="checkbox"][name="enabled"]');
    await page.click('button[type="submit"]');
    await page.waitForLoadState('networkidle');

    // Verify settings persisted
    await page.goto(`${autoApplyTestConfig.baseURL}/auto-apply`);
// REMOVED:     await expect(page.locator('input[type="checkbox"][name="enabled"]')).toBeChecked({ timeout });
// REMOVED:   });
// REMOVED: });

// Export for use in other test files
export { test, expect, autoApplyTestConfig };

/**
 * Main test suite
 */
test.describe('Auto-Apply E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Login as test user
    await loginAsTestUser(page);

    // Navigate to auto-apply page
    await goToAutoApplyPage(page);

    // Configure auto-apply for testing
    await configureAutoApply(page, autoApplyTestConfig.autoApply);
  });

  test.afterEach(async ({ page }) => {
    // Logout and cleanup
    await cleanupAfterTest(page);
  });

  test('Happy Path: User enables auto-apply and jobs applied successfully', async ({ page }) => {
    await configureAutoApply(page, autoApplyTestConfig.autoApply);

    // Start auto-apply cycle
    await startAutoApplyCycle(page);

    // Wait for cycle to complete
    await waitForAutoApplyCycleComplete(page);

    // Verify jobs were applied
    const jobs = await checkAppliedJobs(page);
    await expect(jobs.length).toBeGreaterThan(0);

    // Verify no errors
    await verifyNoPlatformErrors(page);

    // Verify rate limit not hit (for configured platforms)
    for (const platform of autoApplyTestConfig.autoApply.platforms) {
      await verifyRateLimitNotHit(page, platform);
    }

    // Verify activity log created
    await verifyActivityLogExists(page, 'Auto-apply cycle completed');

    // Verify applied job count matches expected
    await verifyApplicationCount(page, autoApplyTestConfig.autoApply.maxApplications);
  });
});

// Export for use in other test files
export { test, expect, autoApplyTestConfig };

  test('Rate Limit: Daily limit reached, applications blocked', async ({ page }) => {
    // Login as test user
    await loginAsTestUser(page);

    // Configure aggressive daily limit
    const aggressiveConfig = {
      ...autoApplyTestConfig.autoApply,
      dailyLimit: { linkedin: 2 }, // Very low limit to test rate limiting
      hourlyLimit: { linkedin: 100 }, // High hourly limit
      maxApplications: 100,
      expectRateLimitHit: true,
      expectSuccess: false, // Expect to hit rate limit
    };

    await configureAutoApply(page, aggressiveConfig);

    // Start auto-apply
    await startAutoApplyCycle(page);

    // Wait for error (simulate ban by API error)
    await expect(page.locator('.error-message:has-text("daily limit")')).toBeVisible({ timeout: 30000 });

    // Verify auto-apply disabled automatically
    const isEnabled = await page.locator('input[type="checkbox"][name="enabled"]').isChecked();
    await expect(isEnabled).toBe(false);

    // Verify no jobs applied (blocked)
    const jobs = await checkAppliedJobs(page);
    await expect(jobs.length).toBe(0);

    // Verify activity log created
    await verifyActivityLogExists(page, 'Daily limit reached');

    // Verify failure log exists
    await verifyFailureLogExists(page, 'Daily limit reached');
  });

  test('Duplicate Detection: Same job not applied twice', async ({ page }) => {
    // Configure auto-apply
    await configureAutoApply(page, autoApplyTestConfig.autoApply);

    // Start first auto-apply cycle
    await startAutoApplyCycle(page);

    // Wait for first cycle to complete
    await waitForAutoApplyCycleComplete(page, { timeout: autoApplyTestConfig.testTimeout });

    // Get applied jobs from first cycle
    const jobs = await checkAppliedJobs(page);
    const firstJobTitle = jobs.length > 0 ? await jobs[0].locator('.job-title').textContent() : '';

    // Verify job list has one job
    await expect(jobs.length).toBe(1);

    // Store job details for second cycle
    const jobId = await jobs[0].locator('.job-id').textContent();
    const jobTitle = firstJobTitle;

    // Start second cycle (should detect duplicate)
    await startAutoApplyCycle(page);

    // Wait for second cycle to complete (or stop due to duplicate detection)
    await page.waitForTimeout(10000); // 10 seconds

    // Verify job list still has one job (not applied twice)
    const jobsAfterSecondCycle = await checkAppliedJobs(page);
    await expect(jobsAfterSecondCycle.length).toBe(1);

    // Verify activity log mentions duplicate detection
    await verifyActivityLogExists(page, 'Duplicate job detected');

    // Verify applied job count matches expected
    await verifyApplicationCount(page, 1); // Still 1 job, not 2
  });

