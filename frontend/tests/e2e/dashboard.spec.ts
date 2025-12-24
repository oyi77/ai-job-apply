import { test, expect } from '@playwright/test';

test.describe('Dashboard', () => {
  test('should redirect to login when not authenticated', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveURL(/.*login/);
  });

  test('should display dashboard when authenticated', async ({ page }) => {
    // Mock authentication by setting token in localStorage
    await page.goto('/login');
    await page.evaluate(() => {
      localStorage.setItem('token', 'mock-token');
      localStorage.setItem('user', JSON.stringify({ id: '1', email: 'test@example.com' }));
    });
    
    await page.goto('/');
    await expect(page.getByText(/dashboard/i)).toBeVisible();
  });
});

