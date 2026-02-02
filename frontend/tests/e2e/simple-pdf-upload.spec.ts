/**
 * Simple E2E test for resume upload with real PDF
 * Bypasses global setup and handles authentication inline
 */

import { test, expect } from '@playwright/test';
import { join } from 'path';

test.describe('Simple Resume Upload Test', () => {
  let uniqueEmail: string;

  test.beforeEach(async () => {
    // Generate unique email for each test run
    const timestamp = Date.now();
    uniqueEmail = `pdfuser-${timestamp}@example.com`;
  });

  test('should upload real PDF resume from file system', async ({ page }) => {
    // Increase timeout for full flow
    test.setTimeout(60000);

    console.log('Starting resume upload test...');

    // ========== STEP 1: Register new user ==========
    console.log('Step 1: Registering user...');
    await page.goto('/register');
    await expect(page).toHaveURL(/.*register/);

    // Wait for page to fully load
    await page.waitForLoadState('domcontentloaded').catch(() => {});
    await page.waitForTimeout(1000);

    // Fill registration form - use name attribute for precise selection
    const nameInput = page.locator('input[name="name"]');
    const emailInput = page.locator('input[name="email"]');
    const passwordInput = page.locator('input[name="password"]');
    const confirmPasswordInput = page.locator('input[name="confirmPassword"]');

    // Wait for form to be ready
    await expect(emailInput).toBeVisible({ timeout: 5000 });

    console.log('Filling registration form...');
    await nameInput.fill('Test User');
    await emailInput.fill(uniqueEmail);
    await passwordInput.fill('Test123!@#');
    await confirmPasswordInput.fill('Test123!@#');

    // Submit registration
    const submitButton = page.getByRole('button', { name: 'Create Account' });
    await expect(submitButton).toBeVisible({ timeout: 5000 });
    await submitButton.click();

    // Wait for redirect or error
    await page.waitForTimeout(5000);

    // Check if registration succeeded
    const currentUrl = page.url();
    const isRedirected = !currentUrl.includes('register');

    if (isRedirected) {
      console.log('✅ Registration successful');
    } else {
      // Check for error messages - look for the error div
      const errorDiv = page.locator('.bg-danger-50').or(page.locator('.text-red'));
      const errorVisible = await errorDiv.isVisible().catch(() => false);

      if (errorVisible) {
        const errorText = await errorDiv.textContent();
        console.error('❌ Registration failed with error:', errorText);
        await page.screenshot({ path: 'playwright/registration-error.png' });
        throw new Error(`Registration failed: ${errorText}`);
      } else {
        // Check for field validation errors
        const nameError = page.locator('input[name="name"] + div, input[name="name"] + span').locator('text=/is required/i');
        const emailError = page.locator('input[name="email"] + div, input[name="email"] + span').locator('text=/required|invalid/i');
        const passwordError = page.locator('input[name="password"] + div, input[name="password"] + span').locator('text=/required|least 8|uppercase|lowercase|number/i');

        const hasErrors = await Promise.all([
          nameError.isVisible().catch(() => false),
          emailError.isVisible().catch(() => false),
          passwordError.isVisible().catch(() => false),
        ]);

        if (hasErrors.some(Boolean)) {
          console.error('❌ Registration form validation errors present');
          await page.screenshot({ path: 'playwright/validation-errors.png', fullPage: true });
          throw new Error('Form has validation errors');
        } else {
          console.error('❌ Registration failed for unknown reason. URL:', currentUrl);
          await page.screenshot({ path: 'playwright/unknown-error.png', fullPage: true });
          throw new Error('Registration failed - check screenshot');
        }
      }
    }

    // ========== STEP 2: Navigate to resumes page ==========
    console.log('Step 2: Navigating to resumes...');
    await page.goto('/resumes');
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(1000);

    // ========== STEP 3: Upload real PDF ==========
    console.log('Step 3: Uploading real PDF...');
    const pdfPath = join(process.cwd(), 'resumes', 'test_resume.pdf');
    console.log('PDF file path:', pdfPath);

    // Find file input
    const fileInput = page.locator('input[type="file"]');
    const uploadButton = page
      .getByRole('button', { name: /upload|add resume/i })
      .or(page.getByTestId('upload-resume'));

    let uploadAttempted = false;

    if (await fileInput.isVisible().catch(() => false)) {
      console.log('Found file input, uploading PDF...');
      await fileInput.setInputFiles(pdfPath);
      uploadAttempted = true;
    } else if (await uploadButton.isVisible().catch(() => false)) {
      console.log('Found upload button, clicking...');
      await uploadButton.click();
      await page.waitForTimeout(500);

      const modalInput = page.locator('input[type="file"]').first();
      if (await modalInput.isVisible().catch(() => false)) {
        console.log('Uploading PDF via modal...');
        await modalInput.setInputFiles(pdfPath);
        uploadAttempted = true;
      }
    }

    if (!uploadAttempted) {
      console.error('❌ Could not find upload mechanism');
      // Take screenshot for debugging
      await page.screenshot({ path: 'playwright/upload-failed.png' });
      throw new Error('Upload mechanism not found');
    }

    // Wait for upload to complete
    console.log('Waiting for upload to complete...');
    await page.waitForTimeout(5000);

    // Verify upload succeeded
    const successToast = page.getByRole('alert').filter({ hasText: /success|uploaded/i });
    const resumeCards = page
      .locator('[data-testid="resume-card"]')
      .or(page.locator('.resume-card'))
      .or(page.locator('.resume-item'));

    const hasToast = await successToast.isVisible().catch(() => false);
    const cardCount = await resumeCards.count();

    console.log('Upload result - Toast:', hasToast, 'Cards:', cardCount);

    if (hasToast || cardCount > 0) {
      console.log('✅ Resume uploaded successfully!');
      expect(true).toBeTruthy();
    } else {
      console.error('❌ Upload verification failed');
      await page.screenshot({ path: 'playwright/upload-verification-failed.png' });

      const pageContent = await page.locator('body').textContent();
      console.error('Page content (first 500 chars):', pageContent?.substring(0, 500));

      // Check for error alerts
      const errorAlerts = await page.getByRole('alert').filter({ hasText: /error|failed/i }).allTextContents();
      if (errorAlerts.length > 0) {
        console.error('Error alerts:', errorAlerts);
      }

      throw new Error('Resume upload verification failed');
    }
  });
});
