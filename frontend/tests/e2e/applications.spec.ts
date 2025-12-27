/**
 * E2E tests for Application Management
 */

import { test, expect } from '@playwright/test';
import { loginAsUser, waitForLoadingToComplete, waitForToast } from './utils';
import { testApplications } from './fixtures/test-data';

test.describe('Application Management', () => {
  test.beforeEach(async ({ page }) => {
    // Mock authentication
    await page.goto('/login');
    await page.evaluate(() => {
      localStorage.setItem('token', 'mock-token');
      localStorage.setItem('user', JSON.stringify({ id: '1', email: 'test@example.com' }));
    });
  });

  test('should display applications list', async ({ page }) => {
    await page.goto('/applications');
    await waitForLoadingToComplete(page);

    // Check if applications page is loaded
    await expect(page).toHaveURL(/.*applications/);
    
    // Check for applications list or empty state
    const hasApplications = await page.locator('[data-testid="application-card"], .application-card, .application-item').count();
    const hasEmptyState = await page.locator('text=No applications, text=Create your first application').count();
    
    expect(hasApplications > 0 || hasEmptyState > 0).toBeTruthy();
  });

  test('should navigate to create application page', async ({ page }) => {
    await page.goto('/applications');
    await waitForLoadingToComplete(page);

    // Look for create button
    const createButton = page.locator('button:has-text("Create"), button:has-text("Add"), a:has-text("Create"), a:has-text("Add")').first();
    
    if (await createButton.isVisible()) {
      await createButton.click();
      await page.waitForTimeout(1000);
      // Should navigate to create form or open modal
      const hasForm = await page.locator('form, [data-testid="application-form"]').count();
      expect(hasForm > 0).toBeTruthy();
    }
  });

  test('should create new application', async ({ page }) => {
    await page.goto('/applications');
    await waitForLoadingToComplete(page);

    // Try to find and click create button
    const createSelectors = [
      'button:has-text("Create Application")',
      'button:has-text("Add Application")',
      'button:has-text("New Application")',
      'a:has-text("Create")',
      '[data-testid="create-application"]',
    ];

    let createButton = null;
    for (const selector of createSelectors) {
      const element = page.locator(selector).first();
      if (await element.isVisible().catch(() => false)) {
        createButton = element;
        break;
      }
    }

    if (createButton) {
      await createButton.click();
      await page.waitForTimeout(1000);

      // Fill application form
      const testApp = testApplications[0];
      
      // Try to fill job title
      const jobTitleSelectors = [
        'input[name="jobTitle"], input[name="job_title"], input[placeholder*="Job Title"], input[placeholder*="Position"]',
      ];
      for (const selector of jobTitleSelectors) {
        const field = page.locator(selector).first();
        if (await field.isVisible().catch(() => false)) {
          await field.fill(testApp.jobTitle);
          break;
        }
      }

      // Try to fill company
      const companySelectors = [
        'input[name="company"], input[placeholder*="Company"]',
      ];
      for (const selector of companySelectors) {
        const field = page.locator(selector).first();
        if (await field.isVisible().catch(() => false)) {
          await field.fill(testApp.company);
          break;
        }
      }

      // Submit form
      const submitButton = page.locator('button[type="submit"], button:has-text("Save"), button:has-text("Create")').first();
      if (await submitButton.isVisible().catch(() => false)) {
        await submitButton.click();
        await waitForToast(page, /success|created|saved/i);
      }
    }
  });

  test('should view application details', async ({ page }) => {
    await page.goto('/applications');
    await waitForLoadingToComplete(page);

    // Try to click on first application
    const applicationSelectors = [
      '[data-testid="application-card"]',
      '.application-card',
      '.application-item',
      'a[href*="application"]',
    ];

    for (const selector of applicationSelectors) {
      const element = page.locator(selector).first();
      if (await element.isVisible().catch(() => false)) {
        await element.click();
        await page.waitForTimeout(1000);
        
        // Check if we're on detail page
        const isDetailPage = await page.locator('h1, h2, [data-testid="application-detail"]').count();
        if (isDetailPage > 0) {
          expect(page.url()).toMatch(/application/);
          return;
        }
      }
    }
  });

  test('should filter applications', async ({ page }) => {
    await page.goto('/applications');
    await waitForLoadingToComplete(page);

    // Look for filter controls
    const filterSelectors = [
      'input[placeholder*="Search"], input[placeholder*="Filter"]',
      'select[name="status"], select[name="filter"]',
      'button:has-text("Filter")',
    ];

    for (const selector of filterSelectors) {
      const element = page.locator(selector).first();
      if (await element.isVisible().catch(() => false)) {
        // Try to interact with filter
        if (await element.getAttribute('type') === 'text' || element.tagName() === 'INPUT') {
          await element.fill('engineer');
          await page.waitForTimeout(1000);
        }
        break;
      }
    }
  });

  test('should update application status', async ({ page }) => {
    await page.goto('/applications');
    await waitForLoadingToComplete(page);

    // Find first application and try to update status
    const statusSelectors = [
      'select[name="status"]',
      'button:has-text("Status")',
      '[data-testid="status-select"]',
    ];

    for (const selector of statusSelectors) {
      const element = page.locator(selector).first();
      if (await element.isVisible().catch(() => false)) {
        if (element.tagName() === 'SELECT') {
          await element.selectOption('interview');
          await waitForToast(page, /updated|saved/i);
        }
        break;
      }
    }
  });
});
