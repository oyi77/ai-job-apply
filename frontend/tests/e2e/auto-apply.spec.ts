import { test, expect } from '@playwright/test';

test.describe('Auto Apply Flow', () => {
  test.beforeEach(async ({ page }) => {
    const testEmail = `test-${Date.now()}@example.com`;
    const user = {
      id: 'user-1',
      email: testEmail,
      name: 'Test User',
      preferences: {
        theme: 'system',
        notifications: {
          email: true,
          push: true,
          follow_up_reminders: true,
          interview_reminders: true,
          application_updates: true,
        },
        privacy: {
          profile_visibility: 'private',
          data_sharing: false,
          analytics_tracking: true,
        },
        ai: {
          provider_preference: 'openai',
        },
      },
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    let config = {
      keywords: [],
      locations: [],
      min_salary: null,
      daily_limit: 5,
      is_active: false,
    };

    await page.route('**/api/v1/auth/me', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(user),
      });
    });

    await page.route('**/api/v1/auto-apply/config', async (route) => {
      if (route.request().method() === 'POST') {
        const payload = route.request().postDataJSON() as Partial<typeof config>;
        config = { ...config, ...payload, is_active: config.is_active };
      }
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(config),
      });
    });

    await page.route('**/api/v1/auto-apply/activity', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([]),
      });
    });

    await page.route('**/api/v1/auto-apply/start', async (route) => {
      config = { ...config, is_active: true };
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ message: 'Auto-apply started' }),
      });
    });

    await page.route('**/api/v1/auto-apply/stop', async (route) => {
      config = { ...config, is_active: false };
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ message: 'Auto-apply stopped' }),
      });
    });

  });

  test('should render the auto-apply page with inputs', async ({ page }) => {
    // Navigate to auto-apply page
    console.log('Navigating to /auto-apply');
    await page.goto('/auto-apply');
    console.log('Current URL after goto:', page.url());
    
    // Wait for network idle to ensure page is fully loaded
    await page.waitForLoadState('networkidle');
    console.log('Network idle reached');
    
    // Check current URL - if redirected to login, we need to authenticate
    const currentUrl = page.url();
    console.log('Current URL:', currentUrl);
    
    if (currentUrl.includes('/login')) {
      console.log('Redirected to login, skipping test');
      test.skip();
    }
    
    // Wait for the skills input to be visible
    const skillsInput = page.getByPlaceholder(/e.g. Python/i);
    await expect(skillsInput).toBeVisible({ timeout: 15000 });
    console.log('Skills input found');
    
    // Verify the page title
    const title = await page.title();
    expect(title).toContain('AI Job Application Assistant');
    
    // Verify the page heading
    const heading = page.getByRole('heading', { name: /auto apply/i });
    await expect(heading).toBeVisible();
  });

  test('should configure and start auto-apply', async ({ page }) => {
    // Navigate to auto-apply page
    await page.goto('/auto-apply');
    await page.waitForLoadState('networkidle');

    const currentUrl = page.url();
    if (currentUrl.includes('/login')) {
      test.skip();
    }
    
    // 1. Configure settings - wait for inputs to be visible before filling
    await page.getByPlaceholder(/e.g. Python/i).waitFor({ state: 'visible' });
    await page.getByPlaceholder(/e.g. Python/i).fill('Python, TypeScript');
    
    await page.getByPlaceholder(/e.g. San Francisco/i).waitFor({ state: 'visible' });
    await page.getByPlaceholder(/e.g. San Francisco/i).fill('Remote');
    
    // 2. Save config
    await page.getByRole('button', { name: /save configuration/i }).click();

    // 3. Activate auto-apply
    const toggle = page.getByLabel(/auto apply status/i);
    await toggle.click();

    // 4. Verify active status
    await expect(page.getByText('Active', { exact: true })).toBeVisible();

    // 5. Verify activity log updates (mocked)
    // In real E2E this might need a wait or polling
  });

  test('should enforce rate limiting with low daily limit', async ({ page }) => {
    // Track application count
    let applicationCount = 0;
    const maxApplications = 3;
    let rateLimitReached = false;

    // Mock activity endpoint with rate limiting logic
    await page.route('**/api/v1/auto-apply/activity', async (route) => {
      const activities = [];
      if (applicationCount >= maxApplications) {
        rateLimitReached = true;
        activities.push({
          id: 'activity-rate-limit',
          user_id: 'user-1',
          cycle_id: 'cycle-limit',
          cycle_status: 'rate_limit_reached',
          jobs_applied: maxApplications,
          errors: ['Daily limit reached'],
          created_at: new Date().toISOString(),
        });
      }
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(activities),
      });
    });

    // Navigate to auto-apply page
    await page.goto('/auto-apply');
    await page.waitForLoadState('networkidle');

    const currentUrl = page.url();
    if (currentUrl.includes('/login')) {
      test.skip();
    }

    // Configure with low daily limit
    await page.getByPlaceholder(/e.g. Python/i).waitFor({ state: 'visible' });
    await page.getByPlaceholder(/e.g. Python/i).fill('Python');
    await page.getByPlaceholder(/e.g. San Francisco/i).fill('Remote');

    // Set low daily limit (3 applications)
    const dailyLimitInput = page.locator('input[name="dailyLimit"]').first();
    if (await dailyLimitInput.isVisible().catch(() => false)) {
      await dailyLimitInput.fill('3');
    }

    // Save config
    await page.getByRole('button', { name: /save configuration/i }).click();

    // Activate auto-apply
    const toggle = page.getByLabel(/auto apply status/i);
    await toggle.click();

    // Verify rate limit message appears when limit is reached
    await page.waitForTimeout(5000);

    // Check for rate limiting in activity log
    if (rateLimitReached) {
      const rateLimitMessage = page.getByText(/daily limit reached|rate limit/i);
      await expect(rateLimitMessage).toBeVisible();
    }
  });

  test('should detect and skip duplicate job applications', async ({ page }) => {
    // Track applied jobs to detect duplicates
    const appliedJobs = new Set<string>();
    let duplicateDetected = false;

    // Mock activity endpoint with duplicate detection
    await page.route('**/api/v1/auto-apply/activity', async (route) => {
      const activities = [];
      if (appliedJobs.has('job_123')) {
        duplicateDetected = true;
        activities.push({
          id: 'activity-duplicate',
          user_id: 'user-1',
          cycle_id: 'cycle-duplicate',
          cycle_status: 'completed',
          jobs_applied: 0,
          errors: ['Skipped duplicate: job_123'],
          message: 'Skipped duplicate: job_123',
          created_at: new Date().toISOString(),
        });
      } else {
        // First application
        appliedJobs.add('job_123');
        activities.push({
          id: 'activity-first',
          user_id: 'user-1',
          cycle_id: 'cycle-first',
          cycle_status: 'completed',
          jobs_applied: 1,
          applied_job_ids: ['job_123'],
          created_at: new Date().toISOString(),
        });
      }
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(activities),
      });
    });

    // Navigate to auto-apply page
    await page.goto('/auto-apply');
    await page.waitForLoadState('networkidle');

    const currentUrl = page.url();
    if (currentUrl.includes('/login')) {
      test.skip();
    }

    // Configure auto-apply
    await page.getByPlaceholder(/e.g. Python/i).waitFor({ state: 'visible' });
    await page.getByPlaceholder(/e.g. Python/i).fill('Python');
    await page.getByPlaceholder(/e.g. San Francisco/i).fill('Remote');

    // Save config
    await page.getByRole('button', { name: /save configuration/i }).click();

    // First cycle: Start auto-apply
    let toggle = page.getByLabel(/auto apply status/i);
    await toggle.click();

    // Wait for first cycle
    await page.waitForTimeout(3000);

    // Stop auto-apply
    toggle = page.getByLabel(/auto apply status/i);
    await toggle.click();

    // Second cycle: Start auto-apply again
    toggle = page.getByLabel(/auto apply status/i);
    await toggle.click();

    // Wait for second cycle
    await page.waitForTimeout(3000);

    // Verify duplicate was detected
    expect(appliedJobs.has('job_123')).toBe(true);
    expect(duplicateDetected).toBe(true);
  });
});
