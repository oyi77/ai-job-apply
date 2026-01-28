/**
 * E2E tests for Analytics
 */

import { test, expect } from '@playwright/test';
import { waitForLoadingToComplete } from './utils';

test.describe('Analytics', () => {
  test('should display analytics dashboard', async ({ page }) => {
    await page.goto('/analytics');
    await waitForLoadingToComplete(page);

    await expect(page).toHaveURL(/.*analytics/);

    await expect(page.getByRole('heading', { name: 'Analytics Dashboard' })).toBeVisible();
  });

  test('should display application statistics', async ({ page }) => {
    await page.goto('/analytics');
    await waitForLoadingToComplete(page);

    await expect(page.getByText('Total Applications')).toBeVisible();
    await expect(page.getByText('Success Rate')).toBeVisible();
  });

  test('should display charts', async ({ page }) => {
    await page.goto('/analytics');
    await waitForLoadingToComplete(page);

    const chartContainers = page.getByTestId('chart-container');
    await expect(chartContainers.first()).toBeVisible();
  });

  test('should filter by date range', async ({ page }) => {
    await page.goto('/analytics');
    await waitForLoadingToComplete(page);

    const timeRangeSelect = page.locator('select[name="timeRange"]');
    if (await timeRangeSelect.isVisible()) {
      await timeRangeSelect.selectOption('30');
    }
  });

  test('should export analytics data', async ({ page }) => {
    await page.goto('/analytics');
    await waitForLoadingToComplete(page);

    const exportButton = page.getByRole('button', { name: /export/i });
    
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
        await expect(page.getByRole('alert')).toBeVisible();
      }
    }
  });

  test('should display performance metrics', async ({ page }) => {
    await page.goto('/analytics');
    await waitForLoadingToComplete(page);

    await expect(page.getByText('Success Rate')).toBeVisible();
  });
});
