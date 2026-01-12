/**
 * Page helper utilities for E2E tests
 */

import { Page, expect } from '@playwright/test';

/**
 * Wait for page to be fully loaded
 */
export async function waitForPageLoad(page: Page): Promise<void> {
  await page.waitForLoadState('networkidle');
  await page.waitForLoadState('domcontentloaded');
}

/**
 * Wait for API response
 */
export async function waitForAPIResponse(
  page: Page,
  urlPattern: string | RegExp,
  timeout = 10000
): Promise<void> {
  await page.waitForResponse(
    (response) => {
      const url = response.url();
      if (typeof urlPattern === 'string') {
        return url.includes(urlPattern);
      }
      return urlPattern.test(url);
    },
    { timeout }
  );
}

/**
 * Wait for element to be visible and stable
 */
export async function waitForStableElement(
  page: Page,
  selector: string,
  timeout = 5000
): Promise<void> {
  const element = page.locator(selector);
  await element.waitFor({ state: 'visible', timeout });
  
  // Wait for element to be stable (not moving)
  await page.waitForTimeout(500);
}

/**
 * Fill form field with retry
 */
export async function fillFieldWithRetry(
  page: Page,
  selector: string,
  value: string,
  retries = 3
): Promise<void> {
  for (let i = 0; i < retries; i++) {
    try {
      await page.fill(selector, value);
      const actualValue = await page.inputValue(selector);
      if (actualValue === value) {
        return;
      }
    } catch (error) {
      if (i === retries - 1) {
        throw error;
      }
      await page.waitForTimeout(500);
    }
  }
}

/**
 * Click element with retry
 */
export async function clickWithRetry(
  page: Page,
  selector: string,
  retries = 3
): Promise<void> {
  for (let i = 0; i < retries; i++) {
    try {
      await page.click(selector);
      return;
    } catch (error) {
      if (i === retries - 1) {
        throw error;
      }
      await page.waitForTimeout(500);
    }
  }
}

/**
 * Wait for toast/notification to appear
 */
export async function waitForToast(
  page: Page,
  message?: string,
  timeout = 5000
): Promise<void> {
  const toastSelectors = [
    '[role="alert"]',
    '.toast',
    '.notification',
    '[data-testid="toast"]',
  ];

  for (const selector of toastSelectors) {
    try {
      const element = page.locator(selector).first();
      await element.waitFor({ state: 'visible', timeout });
      if (message) {
        await expect(element).toContainText(message);
      }
      return;
    } catch {
      // Continue to next selector
    }
  }
}

/**
 * Wait for loading spinner to disappear
 */
export async function waitForLoadingToComplete(
  page: Page,
  timeout = 10000
): Promise<void> {
  const loadingSelectors = [
    '[data-testid="loading"]',
    '.spinner',
    '.loading',
    '[aria-busy="true"]',
  ];

  for (const selector of loadingSelectors) {
    try {
      await page.waitForSelector(selector, { state: 'hidden', timeout });
    } catch {
      // Continue to next selector
    }
  }

  // Also wait for network to be idle
  await page.waitForLoadState('networkidle');
}

/**
 * Take screenshot with timestamp
 */
export async function takeScreenshot(
  page: Page,
  name: string
): Promise<void> {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  await page.screenshot({
    path: `tests/e2e/screenshots/${name}-${timestamp}.png`,
    fullPage: true,
  });
}

/**
 * Check if element exists (non-throwing)
 */
export async function elementExists(
  page: Page,
  selector: string
): Promise<boolean> {
  try {
    const element = page.locator(selector).first();
    await element.waitFor({ state: 'attached', timeout: 1000 });
    return true;
  } catch {
    return false;
  }
}

/**
 * Get text content safely
 */
export async function getTextContent(
  page: Page,
  selector: string
): Promise<string | null> {
  try {
    const element = page.locator(selector).first();
    await element.waitFor({ state: 'visible', timeout: 5000 });
    return await element.textContent();
  } catch {
    return null;
  }
}
