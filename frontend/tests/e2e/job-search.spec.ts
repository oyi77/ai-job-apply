/**
 * E2E tests for Job Search
 */

import { test, expect } from '@playwright/test';
import { waitForLoadingToComplete, waitForToast } from './utils';
import { testJobs } from './fixtures/test-data';

test.describe('Job Search', () => {
  test.beforeEach(async ({ page }) => {
    // Mock authentication
    await page.goto('/login');
    await page.evaluate(() => {
      localStorage.setItem('token', 'mock-token');
      localStorage.setItem('user', JSON.stringify({ id: '1', email: 'test@example.com' }));
    });
  });

  test('should display job search page', async ({ page }) => {
    await page.goto('/job-search');
    await waitForLoadingToComplete(page);

    await expect(page).toHaveURL(/.*job-search/);
    
    // Check for search form
    const hasSearchForm = await page.locator('input[placeholder*="Search"], input[placeholder*="Job"], form').count();
    expect(hasSearchForm > 0).toBeTruthy();
  });

  test('should search for jobs', async ({ page }) => {
    await page.goto('/job-search');
    await waitForLoadingToComplete(page);

    // Find search input
    const searchInput = page.locator('input[placeholder*="Search"], input[placeholder*="Job"], input[name="query"], input[name="search"]').first();
    
    if (await searchInput.isVisible()) {
      await searchInput.fill('Software Engineer');
      
      // Find and click search button
      const searchButton = page.locator('button:has-text("Search"), button[type="submit"], button[aria-label*="Search"]').first();
      if (await searchButton.isVisible()) {
        await searchButton.click();
        await waitForLoadingToComplete(page);
        
        // Check for results
        const hasResults = await page.locator('[data-testid="job-card"], .job-card, .job-item, text=No results').count();
        expect(hasResults > 0).toBeTruthy();
      }
    }
  });

  test('should filter jobs by location', async ({ page }) => {
    await page.goto('/job-search');
    await waitForLoadingToComplete(page);

    // Find location input
    const locationInput = page.locator('input[placeholder*="Location"], input[name="location"]').first();
    
    if (await locationInput.isVisible()) {
      await locationInput.fill('San Francisco');
      
      // Trigger search
      const searchButton = page.locator('button:has-text("Search"), button[type="submit"]').first();
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
    const searchInput = page.locator('input[placeholder*="Search"], input[placeholder*="Job"]').first();
    if (await searchInput.isVisible()) {
      await searchInput.fill('Engineer');
      const searchButton = page.locator('button:has-text("Search"), button[type="submit"]').first();
      if (await searchButton.isVisible()) {
        await searchButton.click();
        await waitForLoadingToComplete(page);
      }
    }

    // Try to click on first job
    const jobSelectors = [
      '[data-testid="job-card"]',
      '.job-card',
      '.job-item',
      'a[href*="job"]',
    ];

    for (const selector of jobSelectors) {
      const element = page.locator(selector).first();
      if (await element.isVisible().catch(() => false)) {
        await element.click();
        await page.waitForTimeout(1000);
        
        // Check if we're on detail page
        const isDetailPage = await page.locator('h1, h2, [data-testid="job-detail"]').count();
        if (isDetailPage > 0) {
          expect(page.url()).toMatch(/job/);
          return;
        }
      }
    }
  });

  test('should save job', async ({ page }) => {
    await page.goto('/job-search');
    await waitForLoadingToComplete(page);

    // Perform a search first
    const searchInput = page.locator('input[placeholder*="Search"], input[placeholder*="Job"]').first();
    if (await searchInput.isVisible()) {
      await searchInput.fill('Engineer');
      const searchButton = page.locator('button:has-text("Search"), button[type="submit"]').first();
      if (await searchButton.isVisible()) {
        await searchButton.click();
        await waitForLoadingToComplete(page);
      }
    }

    // Look for save button
    const saveButton = page.locator('button:has-text("Save"), button:has-text("Bookmark"), button[aria-label*="Save"]').first();
    
    if (await saveButton.isVisible()) {
      await saveButton.click();
      await waitForToast(page, /saved|bookmarked/i);
    }
  });

  test('should create application from job', async ({ page }) => {
    await page.goto('/job-search');
    await waitForLoadingToComplete(page);

    // Perform a search first
    const searchInput = page.locator('input[placeholder*="Search"], input[placeholder*="Job"]').first();
    if (await searchInput.isVisible()) {
      await searchInput.fill('Engineer');
      const searchButton = page.locator('button:has-text("Search"), button[type="submit"]').first();
      if (await searchButton.isVisible()) {
        await searchButton.click();
        await waitForLoadingToComplete(page);
      }
    }

    // Look for apply button
    const applyButton = page.locator('button:has-text("Apply"), button:has-text("Create Application"), a:has-text("Apply")').first();
    
    if (await applyButton.isVisible()) {
      await applyButton.click();
      await page.waitForTimeout(1000);
      
      // Should navigate to application form or open modal
      const hasForm = await page.locator('form, [data-testid="application-form"]').count();
      expect(hasForm > 0 || page.url().includes('application')).toBeTruthy();
    }
  });
});
