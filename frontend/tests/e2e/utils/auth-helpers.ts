/**
 * Authentication helper utilities for E2E tests
 */

import { Page } from '@playwright/test';
import { testUsers } from '../fixtures/test-data';

/**
 * Login as a test user
 */
export async function loginAsUser(
  page: Page,
  user: 'valid' | 'invalid' | 'new' = 'valid'
): Promise<void> {
  const userData = testUsers[user];

  await page.goto('/login');
  await page.getByLabel('Email address').fill(userData.email);
  await page.getByLabel('Password').fill(userData.password);
  await page.getByRole('button', { name: 'Sign in' }).click();

  await page.waitForLoadState('networkidle');
}

/**
 * Logout current user
 */
export async function logout(page: Page): Promise<void> {
  const logoutButton = page
    .getByRole('button', { name: /logout|sign out/i })
    .or(page.getByRole('link', { name: /logout|sign out/i }))
    .or(page.getByTestId('logout'));

  if (await logoutButton.first().isVisible().catch(() => false)) {
    await logoutButton.first().click();
    await page.waitForLoadState('networkidle');
    return;
  }

  await page.evaluate(() => {
    localStorage.clear();
    sessionStorage.clear();
  });
}

/**
 * Check if user is authenticated
 */
export async function isAuthenticated(page: Page): Promise<boolean> {
  const token = await page.evaluate(() => localStorage.getItem('auth_token'));
  return !!token;
}

/**
 * Set authentication token directly (for testing protected routes)
 */
export async function setAuthToken(page: Page, token: string, user?: any): Promise<void> {
  await page.evaluate(
    ({ token, user }) => {
      localStorage.setItem('auth_token', token);
      localStorage.setItem('refresh_token', token);
      if (user) {
        localStorage.setItem(
          'ai-job-apply-store',
          JSON.stringify({
            state: {
              user,
              isAuthenticated: true,
              theme: 'system',
              searchFilters: {},
              sortOptions: { field: 'created_at', direction: 'desc' },
              aiSettings: { provider_preference: 'openai' },
            },
            version: 0,
          })
        );
      }
    },
    { token, user }
  );
}

/**
 * Clear authentication
 */
export async function clearAuth(page: Page): Promise<void> {
  await page.evaluate(() => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('ai-job-apply-store');
    sessionStorage.clear();
  });
}

/**
 * Wait for authentication to complete
 */
export async function waitForAuth(page: Page, timeout = 5000): Promise<void> {
  await page.waitForFunction(
    () => {
      return !!localStorage.getItem('auth_token');
    },
    { timeout }
  );
}
