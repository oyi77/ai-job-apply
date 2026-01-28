import { test, expect } from '@playwright/test';

test.describe('Dashboard', () => {
  test.describe('Unauthenticated', () => {
    test.use({ storageState: { cookies: [], origins: [] } });

    test('should redirect to login when not authenticated', async ({ page }) => {
      await page.goto('/');
      await expect(page).toHaveURL(/.*login/);
    });
  });

  test('should display dashboard when authenticated', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByRole('heading', { name: 'Dashboard', level: 1 })).toBeVisible();
  });
});

