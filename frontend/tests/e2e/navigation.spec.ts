import { test, expect } from '@playwright/test';

test.describe('Navigation', () => {
  test.beforeEach(async ({ page }) => {
    // Mock authentication
    await page.goto('/login');
    await page.evaluate(() => {
      localStorage.setItem('token', 'mock-token');
      localStorage.setItem('user', JSON.stringify({ id: '1', email: 'test@example.com' }));
    });
  });

  test('should navigate to applications page', async ({ page }) => {
    await page.goto('/');
    await page.getByRole('link', { name: /applications/i }).click();
    await expect(page).toHaveURL(/.*applications/);
  });

  test('should navigate to resumes page', async ({ page }) => {
    await page.goto('/');
    await page.getByRole('link', { name: /resumes/i }).click();
    await expect(page).toHaveURL(/.*resumes/);
  });

  test('should navigate to job search page', async ({ page }) => {
    await page.goto('/');
    await page.getByRole('link', { name: /job search/i }).click();
    await expect(page).toHaveURL(/.*job-search/);
  });
});

