import { test, expect } from '@playwright/test';

test.describe('AI Services Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/ai-services');
  });

  test('should optimize a resume', async ({ page }) => {
    // 1. Click "Optimize Resume"
    await page.getByRole('button', { name: /optimize resume/i }).click();

    // 2. Wait for modal
    const modal = page.getByRole('dialog', { name: /resume optimization/i });
    await expect(modal).toBeVisible();

    // 3. Fill form
    // Select resume
    await modal.getByText('Choose a resume to optimize').click();
    const resumeOptions = page.getByRole('option');
    if ((await resumeOptions.count()) === 0) {
      test.skip();
    }
    await resumeOptions.first().click();

    await modal.getByLabel('Job Description').fill('Looking for a Python expert with Flask experience.');

    // 4. Submit
    await modal.getByRole('button', { name: /optimize resume/i }).click();

    // 5. Verify result
    await expect(page.getByText(/optimization result/i)).toBeVisible();
    await expect(page.getByText(/optimization completed successfully/i)).toBeVisible();
  });

  test('should prepare for interview', async ({ page }) => {
    // 1. Click "Prepare for Interview"
    await page.getByRole('button', { name: /prepare for interview/i }).click();

    // 2. Wait for modal
    const modal = page.getByRole('dialog', { name: /interview preparation/i });
    await expect(modal).toBeVisible();

    // 3. Select job application (this is the key trigger in the UI logic)
    await modal.getByText('Select a job application').click();
    const applicationOptions = page.getByRole('option');
    if ((await applicationOptions.count()) === 0) {
      test.skip();
    }
    await applicationOptions.first().click();

    // 4. Verify loading state
    await expect(page.getByText(/preparing interview questions/i)).toBeVisible();

    // 5. Verify results appear
    await expect(page.getByText(/interview questions/i)).toBeVisible();
    await expect(page.getByText(/technical questions/i)).toBeVisible();
  });
});
