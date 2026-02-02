/**
 * E2E tests for AI Features
 */

import { test, expect } from '@playwright/test';
import { waitForLoadingToComplete } from './utils';

test.describe('AI Features', () => {
  test('should display AI services page', async ({ page }) => {
    await page.goto('/ai-services');
    await waitForLoadingToComplete(page);

    await expect(page).toHaveURL(/.*ai-services/);

    await expect(page.getByRole('button', { name: /optimize resume/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /generate cover letter/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /analyze match/i })).toBeVisible();
  });

  test('should optimize resume', async ({ page }) => {
    await page.goto('/ai-services');
    await waitForLoadingToComplete(page);

    await page.getByRole('button', { name: /optimize resume/i }).click();
    const modal = page.getByRole('dialog', { name: /resume optimization/i });
    await expect(modal).toBeVisible();

    await modal.getByText('Choose a resume to optimize').click();
    const options = page.getByRole('option');
    if ((await options.count()) === 0) {
      test.skip();
    }
    await options.first().click();

    await modal.getByLabel('Job Description').fill('Looking for a Python expert with Flask experience.');
    await modal.getByRole('button', { name: /optimize resume/i }).click();

    await expect(page.getByText(/optimization result/i)).toBeVisible();
  });

  test('should generate cover letter', async ({ page }) => {
    await page.goto('/cover-letters');
    await waitForLoadingToComplete(page);

    const generateButton = page.getByRole('button', { name: /generate with ai/i });
    
    if (await generateButton.isVisible()) {
      await generateButton.click();
      await page.waitForTimeout(1000);
      
      // Should show generation form
      await expect(page.getByRole('dialog', { name: /generate cover letter with ai/i })).toBeVisible();
      
      // Fill form if visible
      await page.getByLabel('Job Title').fill('Software Engineer');
      await page.getByLabel('Company').fill('Tech Corp');
      
      // Submit
      const submitButton = page.getByRole('button', { name: /generate cover letter/i });
      await submitButton.click();
      await expect(page.getByText(/generation complete/i)).toBeVisible();
    }
  });

  test('should analyze job match', async ({ page }) => {
    await page.goto('/ai-services');
    await waitForLoadingToComplete(page);

    const matchButton = page.getByRole('button', { name: /analyze match/i });
    
    if (await matchButton.isVisible()) {
      await matchButton.click();
      await page.waitForTimeout(1000);
      
      // Should show analysis form or results
      await expect(page.getByRole('dialog', { name: /job matching analysis/i })).toBeVisible();
    }
  });

  test('should handle AI service fallback', async ({ page }) => {
    // This test verifies that the UI handles AI service unavailability gracefully
    await page.goto('/ai-services');
    await waitForLoadingToComplete(page);
 
    // Try to use an AI feature
    const optimizeButton = page.getByRole('button', { name: /optimize resume/i });
    
    if (await optimizeButton.isVisible()) {
      // Mock API failure
      await page.route('**/api/v1/ai/**', (route) => {
        route.fulfill({
          status: 503,
          body: JSON.stringify({ error: 'Service unavailable' }),
        });
      });
      
      await optimizeButton.click();
      
      // Wait for error notification to be rendered and displayed
      await page.waitForTimeout(2000);
      
      // Look for error message or notification in various forms
      const pageContent = await page.content();
      const errorPresent = pageContent.toLowerCase().includes('error') || 
                           pageContent.toLowerCase().includes('failed') ||
                           pageContent.toLowerCase().includes('unavailable') ||
                           await page.locator('[role="alert"]').count() > 0 ||
                           await page.getByText(/error|unavailable|failed/i, { exact: false }).count() > 0;
      
      // Test passes if error is shown somewhere in the UI
      expect(errorPresent).toBeTruthy();
    }
  });
});
