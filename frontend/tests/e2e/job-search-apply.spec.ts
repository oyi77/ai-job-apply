import { test, expect } from '@playwright/test';

test.describe('Job Search & Apply Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/job-search');
  });

  test('should search for jobs and apply', async ({ page }) => {
    // 1. Enter search criteria
    await page.getByPlaceholder(/software engineer/i).fill('Python Developer');
    await page.getByPlaceholder(/san francisco/i).fill('Remote');

    // 2. Click Search
    await page.getByRole('button', { name: /search jobs/i }).click();

    // 3. Verify results
    // Wait for at least one job card
    await expect(page.getByText(/search results/i)).toBeVisible();
    
    // 4. Click Apply on the first job result
    // Assuming the first apply button corresponds to the first job
    await page.getByRole('button', { name: /apply/i }).first().click();

    // 5. Verify Create Application modal
    const modal = page.getByRole('dialog', { name: /create application/i });
    await expect(modal).toBeVisible();

    // 6. Fill application notes
    await modal.getByLabel('Application Notes').fill('Applying via job search feature.');

    // 7. Submit application
    await modal.getByRole('button', { name: /create application/i }).click();

    // 8. Verify success and modal close
    await expect(modal).not.toBeVisible();

    // 9. Navigate to Applications page to verify
    await page.goto('/applications');
    await expect(page.getByText('Python Developer')).toBeVisible();
    await expect(page.getByText('submitted')).toBeVisible();
  });
});
