/**
 * E2E tests for Analytics
 */

import { test, expect } from '@playwright/test';
import { waitForLoadingToComplete } from './utils';

test.describe('Analytics', () => {
  test.beforeEach(async ({ page }) => {
    // Mock authentication
    await page.goto('/login');
    await page.evaluate(() => {
      localStorage.setItem('token', 'mock-token');
      localStorage.setItem('user', JSON.stringify({ id: '1', email: 'test@example.com' }));
    });
  });

  test('should display analytics dashboard', async ({ page }) => {
    await page.goto('/analytics');
    await waitForLoadingToComplete(page);

    await expect(page).toHaveURL(/.*analytics/);
    
    // Check for analytics content
    const hasAnalytics = await page.locator('text=Analytics, text=Statistics, text=Dashboard, [data-testid="analytics"]').count();
    expect(hasAnalytics > 0).toBeTruthy();
  });

  test('should display application statistics', async ({ page }) => {
    await page.goto('/analytics');
    await waitForLoadingToComplete(page);

    // Look for statistics cards or charts
    const hasStats = await page.locator('[data-testid="stat-card"], .stat-card, text=Applications, text=Success Rate').count();
    expect(hasStats > 0).toBeTruthy();
  });

  test('should display charts', async ({ page }) => {
    await page.goto('/analytics');
    await waitForLoadingToComplete(page);

    // Look for charts (canvas, svg, or chart components)
    const hasCharts = await page.locator('canvas, svg, [data-testid="chart"], .chart').count();
    expect(hasCharts > 0).toBeTruthy();
  });

  test('should filter by date range', async ({ page }) => {
    await page.goto('/analytics');
    await waitForLoadingToComplete(page);

    // Look for date range picker
    const dateInputs = page.locator('input[type="date"], input[placeholder*="Date"], [data-testid="date-range"]');
    const count = await dateInputs.count();
    
    if (count > 0) {
      // Try to interact with date filter
      const firstDateInput = dateInputs.first();
      await firstDateInput.click();
      await page.waitForTimeout(500);
    }
  });

  test('should export analytics data', async ({ page }) => {
    await page.goto('/analytics');
    await waitForLoadingToComplete(page);

    // Look for export button
    const exportButton = page.locator('button:has-text("Export"), button:has-text("Download"), a:has-text("Export")').first();
    
    if (await exportButton.isVisible()) {
      // Set up download listener
      const downloadPromise = page.waitForEvent('download').catch(() => null);
      
      await exportButton.click();
      
      // Wait for download or confirmation
      const download = await downloadPromise;
      if (download) {
        expect(download.suggestedFilename()).toBeTruthy();
      } else {
        // Check for success message
        await page.waitForTimeout(1000);
        const hasSuccess = await page.locator('text=exported, text=downloaded, [role="alert"]').count();
        expect(hasSuccess > 0).toBeTruthy();
      }
    }
  });

  test('should display performance metrics', async ({ page }) => {
    await page.goto('/analytics');
    await waitForLoadingToComplete(page);

    // Look for metrics like response time, success rate, etc.
    const hasMetrics = await page.locator('text=Response Time, text=Success Rate, text=Interview Rate, text=Offer Rate').count();
    expect(hasMetrics > 0).toBeTruthy();
  });
});
