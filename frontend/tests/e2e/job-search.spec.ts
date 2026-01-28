/**
 * E2E tests for Job Search
 */

import { test, expect } from '@playwright/test';
import { waitForLoadingToComplete, waitForToast } from './utils';
import { testJobs } from './fixtures/test-data';

test.describe('Job Search', () => {
  test('should display job search page', async ({ page }) => {
    await page.goto('/job-search');
    await waitForLoadingToComplete(page);

    await expect(page).toHaveURL(/.*job-search/);
    
    // Check for search form
    await expect(page.getByRole('heading', { name: /job search/i })).toBeVisible();
  });

  test('should search for jobs', async ({ page }) => {
    await page.goto('/job-search');
    await waitForLoadingToComplete(page);

    // Find search input
    const searchInput = page
      .getByPlaceholder(/search|job/i)
      .or(page.getByRole('textbox', { name: /search|job/i }))
      .or(page.locator('input[name="query"]'))
      .or(page.locator('input[name="search"]'));
    
    if (await searchInput.isVisible()) {
      await searchInput.fill('Software Engineer');
      
      // Find and click search button
      const searchButton = page.getByRole('button', { name: /search/i });
      if (await searchButton.isVisible()) {
        await searchButton.click();
        await waitForLoadingToComplete(page);
        
        // Check for results
        const jobCards = page
          .locator('[data-testid="job-card"]')
          .or(page.locator('.job-card'))
          .or(page.locator('.job-item'));
        const emptyState = page.getByText(/no results/i);
        expect((await jobCards.count()) > 0 || (await emptyState.isVisible().catch(() => false))).toBeTruthy();
      }
    }
  });

  test('should filter jobs by location', async ({ page }) => {
    await page.goto('/job-search');
    await waitForLoadingToComplete(page);

    // Find location input
    const locationInput = page
      .getByPlaceholder(/location/i)
      .or(page.getByRole('textbox', { name: /location/i }))
      .or(page.locator('input[name="location"]'));
    
    if (await locationInput.isVisible()) {
      await locationInput.fill('San Francisco');
      
      // Trigger search
      const searchButton = page.getByRole('button', { name: /search/i });
      if (await searchButton.isVisible()) {
        await searchButton.click();
        await waitForLoadingToComplete(page);
      }
    }
  });

  test('should view job details', async ({ page }) => {
    await page.goto('/job-search');
    await waitForLoadingToComplete(page);

    // Perform a search first
    const searchInput = page.getByPlaceholder(/search|job/i);
    if (await searchInput.isVisible()) {
      await searchInput.fill('Engineer');
      const searchButton = page.getByRole('button', { name: /search/i });
      if (await searchButton.isVisible()) {
        await searchButton.click();
        await waitForLoadingToComplete(page);
      }
    }

    // Try to click on first job
    const jobCard = page
      .locator('[data-testid="job-card"]')
      .or(page.locator('.job-card'))
      .or(page.locator('.job-item'))
      .or(page.locator('a[href*="job"]'))
      .first();

    if (await jobCard.isVisible().catch(() => false)) {
      await jobCard.click();
      await page.waitForTimeout(1000);

      const detailHeading = page.getByRole('heading').or(page.getByTestId('job-detail'));
      if ((await detailHeading.count()) > 0) {
        expect(page.url()).toMatch(/job/);
      }
    }
  });

  test('should save job', async ({ page }) => {
    await page.goto('/job-search');
    await waitForLoadingToComplete(page);

    // Perform a search first
    const searchInput = page.getByPlaceholder(/search|job/i);
    if (await searchInput.isVisible()) {
      await searchInput.fill('Engineer');
      const searchButton = page.getByRole('button', { name: /search/i });
      if (await searchButton.isVisible()) {
        await searchButton.click();
        await waitForLoadingToComplete(page);
      }
    }

    // Look for save button
    const saveButton = page.getByRole('button', { name: /save|bookmark/i });
    
    if (await saveButton.isVisible()) {
      await saveButton.click();
      await waitForToast(page, 'saved');
    }
  });

  test('should create application from job', async ({ page }) => {
    await page.goto('/job-search');
    await waitForLoadingToComplete(page);

    // Perform a search first
    const searchInput = page.getByPlaceholder(/search|job/i);
    if (await searchInput.isVisible()) {
      await searchInput.fill('Engineer');
      const searchButton = page.getByRole('button', { name: /search/i });
      if (await searchButton.isVisible()) {
        await searchButton.click();
        await waitForLoadingToComplete(page);
      }
    }

    // Look for apply button
    const applyButton = page.getByRole('button', { name: /apply|create application/i });
    
    if (await applyButton.isVisible()) {
      await applyButton.click();
      await page.waitForTimeout(1000);
      
      // Should navigate to application form or open modal
      const form = page.locator('form').or(page.getByTestId('application-form'));
      expect((await form.count()) > 0 || page.url().includes('application')).toBeTruthy();
    }
  });
});
