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
  await page.fill('input[type="email"], input[name="email"]', userData.email);
  await page.fill('input[type="password"], input[name="password"]', userData.password);
  await page.click('button[type="submit"], button:has-text("Sign In"), button:has-text("Login")');
  
  // Wait for navigation or error message
  await page.waitForTimeout(1000);
}

/**
 * Logout current user
 */
export async function logout(page: Page): Promise<void> {
  // Try to find logout button/link
  const logoutSelectors = [
    'button:has-text("Logout")',
    'button:has-text("Sign Out")',
    'a:has-text("Logout")',
    'a:has-text("Sign Out")',
    '[data-testid="logout"]',
  ];
  
  for (const selector of logoutSelectors) {
    const element = page.locator(selector).first();
    if (await element.isVisible().catch(() => false)) {
      await element.click();
      await page.waitForTimeout(500);
      return;
    }
  }
  
  // Fallback: clear localStorage
  await page.evaluate(() => {
    localStorage.clear();
    sessionStorage.clear();
  });
}

/**
 * Check if user is authenticated
 */
export async function isAuthenticated(page: Page): Promise<boolean> {
  const token = await page.evaluate(() => localStorage.getItem('token'));
  return !!token;
}

/**
 * Set authentication token directly (for testing protected routes)
 */
export async function setAuthToken(page: Page, token: string, user?: any): Promise<void> {
  await page.evaluate(
    ({ token, user }) => {
      localStorage.setItem('token', token);
      if (user) {
        localStorage.setItem('user', JSON.stringify(user));
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
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    sessionStorage.clear();
  });
}

/**
 * Wait for authentication to complete
 */
export async function waitForAuth(page: Page, timeout = 5000): Promise<void> {
  await page.waitForFunction(
    () => {
      return !!localStorage.getItem('token');
    },
    { timeout }
  );
}
