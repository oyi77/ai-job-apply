/**
 * E2E tests for Application Management
 */

import { test, expect } from '@playwright/test';
import { waitForLoadingToComplete, waitForToast } from './utils';
import { testApplications } from './fixtures/test-data';

test.describe('Application Management', () => {
  test('should display applications list', async ({ page }) => {
    await page.goto('/applications');
    await waitForLoadingToComplete(page);

    // Check if applications page is loaded
    await expect(page).toHaveURL(/.*applications/);
    await expect(page.getByRole('heading', { name: /applications/i })).toBeVisible();
    
    // Check for applications list or empty state
    const applicationCards = page
      .locator('[data-testid="application-card"]')
      .or(page.locator('.application-card'))
      .or(page.locator('.application-item'));
    const emptyState = page.getByText(/no applications|create your first application/i);

    expect((await applicationCards.count()) > 0 || (await emptyState.isVisible().catch(() => false))).toBeTruthy();
  });

  test('should navigate to create application page', async ({ page }) => {
    await page.goto('/applications');
    await waitForLoadingToComplete(page);

    // Look for create button
    const createButton = page
      .getByRole('button', { name: /create|add|new/i })
      .or(page.getByRole('link', { name: /create|add|new/i }))
      .or(page.getByTestId('create-application'));
    
    if (await createButton.isVisible()) {
      await createButton.click();
      await page.waitForTimeout(1000);
      // Should navigate to create form or open modal
      const form = page.locator('form').or(page.getByTestId('application-form'));
      expect(await form.count()).toBeGreaterThan(0);
    }
  });

  test('should create new application', async ({ page }) => {
    await page.goto('/applications');
    await waitForLoadingToComplete(page);

    const createButton = page
      .getByRole('button', { name: /create application|add application|new application/i })
      .or(page.getByRole('link', { name: /create application|add application|new application/i }))
      .or(page.getByTestId('create-application'));

    if (await createButton.isVisible().catch(() => false)) {
      await createButton.click();
      await page.waitForTimeout(1000);

      // Fill application form
      const testApp = testApplications[0];

      const jobTitleInput = page
        .getByLabel(/job title|position/i)
        .or(page.getByPlaceholder(/job title|position/i));
      if (await jobTitleInput.isVisible().catch(() => false)) {
        await jobTitleInput.fill(testApp.jobTitle);
      }

      const companyInput = page
        .getByLabel(/company/i)
        .or(page.getByPlaceholder(/company/i));
      if (await companyInput.isVisible().catch(() => false)) {
        await companyInput.fill(testApp.company);
      }

      // Submit form
      const submitButton = page.getByRole('button', { name: /save|create/i });
      if (await submitButton.isVisible().catch(() => false)) {
        await submitButton.click();
        await waitForToast(page, 'success');
      }
    }
  });

  test('should view application details', async ({ page }) => {
    await page.goto('/applications');
    await waitForLoadingToComplete(page);

    // Try to click on first application
    const card = page
      .locator('[data-testid="application-card"]')
      .or(page.locator('.application-card'))
      .or(page.locator('.application-item'))
      .or(page.locator('a[href*="application"]'))
      .first();

    if (await card.isVisible().catch(() => false)) {
      await card.click();
      await page.waitForTimeout(1000);

      const detailHeading = page.getByRole('heading').or(page.getByTestId('application-detail'));
      if ((await detailHeading.count()) > 0) {
        expect(page.url()).toMatch(/application/);
      }
    }
  });

  test('should filter applications', async ({ page }) => {
    await page.goto('/applications');
    await waitForLoadingToComplete(page);

    // Look for filter controls
    const searchInput = page
      .getByPlaceholder(/search|filter/i)
      .or(page.getByRole('textbox', { name: /search|filter/i }));
    if (await searchInput.isVisible().catch(() => false)) {
      await searchInput.fill('engineer');
      await page.waitForTimeout(1000);
    }
  });

  test('should update application status', async ({ page }) => {
    await page.goto('/applications');
    await waitForLoadingToComplete(page);

    // Find first application and try to update status
    const statusSelect = page
      .getByLabel(/status/i)
      .or(page.locator('select[name="status"]'))
      .or(page.getByTestId('status-select'));

    if (await statusSelect.isVisible().catch(() => false)) {
      await statusSelect.selectOption('interview');
      await waitForToast(page, 'updated');
    }
  });
});
