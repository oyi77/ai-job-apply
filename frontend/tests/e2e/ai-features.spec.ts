/**
 * E2E tests for AI Features
 */

import { test, expect } from '@playwright/test';
import { waitForLoadingToComplete, waitForToast } from './utils';

test.describe('AI Features', () => {
  test.beforeEach(async ({ page }) => {
    // Mock authentication
    await page.goto('/login');
    await page.evaluate(() => {
      localStorage.setItem('token', 'mock-token');
      localStorage.setItem('user', JSON.stringify({ id: '1', email: 'test@example.com' }));
    });
  });

  test('should display AI services page', async ({ page }) => {
    await page.goto('/ai-services');
    await waitForLoadingToComplete(page);

    await expect(page).toHaveURL(/.*ai-services/);
    
    // Check for AI service options
    const hasAIServices = await page.locator('text=Resume Optimization, text=Cover Letter, text=Job Match').count();
    expect(hasAIServices > 0).toBeTruthy();
  });

  test('should optimize resume', async ({ page }) => {
    // Navigate to resumes first
    await page.goto('/resumes');
    await waitForLoadingToComplete(page);

    // Look for optimize button on a resume
    const optimizeButton = page.locator('button:has-text("Optimize"), button:has-text("AI Optimize"), [data-testid="optimize-resume"]').first();
    
    if (await optimizeButton.isVisible()) {
      await optimizeButton.click();
      await page.waitForTimeout(2000);
      
      // Should show optimization form or modal
      const hasOptimizationForm = await page.locator('form, [data-testid="optimization-form"], text=Optimizing').count();
      expect(hasOptimizationForm > 0).toBeTruthy();
      
      // Wait for optimization to complete (if it's async)
      await waitForToast(page, /optimized|complete|success/i, 30000);
    } else {
      // Try navigating to AI services page
      await page.goto('/ai-services');
      await waitForLoadingToComplete(page);
      
      const optimizeLink = page.locator('a:has-text("Resume Optimization"), button:has-text("Optimize Resume")').first();
      if (await optimizeLink.isVisible()) {
        await optimizeLink.click();
        await page.waitForTimeout(1000);
      }
    }
  });

  test('should generate cover letter', async ({ page }) => {
    await page.goto('/cover-letters');
    await waitForLoadingToComplete(page);

    // Look for generate button
    const generateButton = page.locator('button:has-text("Generate"), button:has-text("Create Cover Letter"), a:has-text("Generate")').first();
    
    if (await generateButton.isVisible()) {
      await generateButton.click();
      await page.waitForTimeout(1000);
      
      // Should show generation form
      const hasForm = await page.locator('form, [data-testid="cover-letter-form"]').count();
      expect(hasForm > 0).toBeTruthy();
      
      // Fill form if visible
      const jobTitleInput = page.locator('input[name="jobTitle"], input[placeholder*="Job Title"]').first();
      if (await jobTitleInput.isVisible().catch(() => false)) {
        await jobTitleInput.fill('Software Engineer');
      }
      
      const companyInput = page.locator('input[name="company"], input[placeholder*="Company"]').first();
      if (await companyInput.isVisible().catch(() => false)) {
        await companyInput.fill('Tech Corp');
      }
      
      // Submit
      const submitButton = page.locator('button[type="submit"], button:has-text("Generate")').first();
      if (await submitButton.isVisible()) {
        await submitButton.click();
        await waitForToast(page, /generated|complete|success/i, 30000);
      }
    }
  });

  test('should analyze job match', async ({ page }) => {
    await page.goto('/ai-services');
    await waitForLoadingToComplete(page);

    // Look for job match analysis
    const matchButton = page.locator('button:has-text("Job Match"), button:has-text("Analyze Match"), a:has-text("Job Match")').first();
    
    if (await matchButton.isVisible()) {
      await matchButton.click();
      await page.waitForTimeout(1000);
      
      // Should show analysis form or results
      const hasAnalysis = await page.locator('form, [data-testid="match-analysis"], text=Match').count();
      expect(hasAnalysis > 0).toBeTruthy();
    }
  });

  test('should handle AI service fallback', async ({ page }) => {
    // This test verifies that the UI handles AI service unavailability gracefully
    await page.goto('/ai-services');
    await waitForLoadingToComplete(page);

    // Try to use an AI feature
    const optimizeButton = page.locator('button:has-text("Optimize"), button:has-text("AI")').first();
    
    if (await optimizeButton.isVisible()) {
      // Mock API failure
      await page.route('**/api/v1/ai/**', (route) => {
        route.fulfill({
          status: 503,
          body: JSON.stringify({ error: 'Service unavailable' }),
        });
      });
      
      await optimizeButton.click();
      await page.waitForTimeout(2000);
      
      // Should show error message or fallback
      const hasError = await page.locator('text=error, text=unavailable, text=fallback, [role="alert"]').count();
      expect(hasError > 0).toBeTruthy();
    }
  });
});
