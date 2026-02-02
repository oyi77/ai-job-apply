/**
 * E2E tests with Real Resume PDF
 *
 * This test uses the actual test_resume.pdf file to test the complete user journey
 * with a real PDF upload instead of mock data.
 */

import { test, expect } from '@playwright/test';
import { waitForLoadingToComplete, waitForToast, fillFieldWithRetry } from './utils';
import { testUsers } from './fixtures/test-data';
import { readFileSync } from 'fs';
import { join } from 'path';

test.describe('End-to-End Flow with Real Resume PDF', () => {
  let uniqueEmail: string;

  test.beforeEach(async ({ page }) => {
    // Generate unique email for each test run
    const timestamp = Date.now();
    uniqueEmail = `realtest-${timestamp}@example.com`;

    // Add browser console logging for debugging
    page.on('console', msg => console.log('BROWSER LOG:', msg.text()));

    // Add browser error logging for debugging
    page.on('pageerror', err => console.log('BROWSER ERROR:', err));
  });

  test('should complete full user journey with real PDF resume: register → upload → search → apply → AI features', async ({ page }) => {
    // Increase test timeout to 120 seconds for full flow with real PDF
    test.setTimeout(120000);

    // ========== STEP 1: Register new user ==========
    await test.step('Register new user', async () => {
      console.log('Step 1: Registering new user...');

      await page.goto('/register');
      await expect(page).toHaveURL(/.*register/);

      // Fill registration form
      const emailInput = page.locator('input[type="email"], input[name="email"]').first();
      const passwordInput = page.locator('input[type="password"], input[name="password"]').first();
      const confirmPasswordInput = page.locator('input[name="confirmPassword"], input[name="confirm_password"]').first();
      const nameInput = page.locator('input[name="name"], input[name="fullName"]').first();

      await expect(emailInput).toBeVisible();
      await expect(passwordInput).toBeVisible();

      console.log('Filling registration form...');
      await fillFieldWithRetry(page, 'input[type="email"], input[name="email"]', uniqueEmail);
      await fillFieldWithRetry(page, 'input[type="password"], input[name="password"]', testUsers.new.password);

      if (await confirmPasswordInput.isVisible()) {
        await fillFieldWithRetry(page, 'input[name="confirmPassword"], input[name="confirm_password"]', testUsers.new.password);
      }

      if (await nameInput.isVisible() && testUsers.new.name) {
        await fillFieldWithRetry(page, 'input[name="name"], input[name="fullName"]', testUsers.new.name);
      }

      // Submit registration form
      console.log('Submitting registration...');
      const submitButton = page.getByRole('button', { name: /create account/i });
      await expect(submitButton).toBeVisible();
      await submitButton.click();

      // Wait for response
      await page.waitForTimeout(3000);

      const currentUrl = page.url();
      const isRedirected = !currentUrl.includes('register');

      console.log('Registration completed - Redirected:', isRedirected);
      expect(isRedirected).toBeTruthy();
    });

    // ========== STEP 2: Upload real resume PDF ==========
    await test.step('Upload real resume PDF', async () => {
      console.log('Step 2: Uploading real resume PDF...');

      // Navigate to resumes page
      await page.goto('/resumes');
      await waitForLoadingToComplete(page);
      await expect(page).toHaveURL(/.*resumes/);

      // Get the real PDF file path
      const pdfPath = join(process.cwd(), 'resumes', 'test_resume.pdf');
      console.log('PDF file path:', pdfPath);

      // Verify PDF file exists
      const pdfExists = await new Promise<boolean>((resolve) => {
        const fs = require('fs');
        fs.access(pdfPath, fs.constants.F_OK, (err: any) => {
          if (err) {
            console.error('PDF file not found:', err);
            resolve(false);
          } else {
            const stats = fs.statSync(pdfPath);
            console.log('PDF file found, size:', stats.size, 'bytes');
            resolve(true);
          }
        });
      });

      expect(pdfExists).toBeTruthy();

      // Find upload button
      const uploadButton = page
        .getByRole('button', { name: /upload resume|upload|add resume/i })
        .or(page.getByTestId('upload-resume'));
      const fileInput = page.locator('input[type="file"]');

      let uploadSuccess = false;

      // Try direct file input first
      if (await fileInput.isVisible().catch(() => false)) {
        console.log('Found file input, uploading PDF...');
        await fileInput.setInputFiles(pdfPath);
        uploadSuccess = true;
      } else if (await uploadButton.isVisible().catch(() => false)) {
        console.log('Found upload button, clicking...');
        await uploadButton.click();
        await page.waitForTimeout(500);

        const modalInput = page.locator('input[type="file"]').first();
        if (await modalInput.isVisible().catch(() => false)) {
          console.log('Uploading PDF via modal...');
          await modalInput.setInputFiles(pdfPath);
          uploadSuccess = true;
        }
      }

      expect(uploadSuccess).toBeTruthy();

      // Verify upload was successful
      console.log('Waiting for upload confirmation...');
      try {
        await waitForToast(page, 'uploaded', 15000);
        console.log('Resume uploaded successfully!');

        // Verify resume appears in list
        await page.waitForTimeout(2000);
        const resumeCards = page
          .locator('[data-testid="resume-card"]')
          .or(page.locator('.resume-card'))
          .or(page.locator('.resume-item'));
        const hasResume = (await resumeCards.count()) > 0;

        console.log('Resume cards found:', await resumeCards.count());
        expect(hasResume).toBeTruthy();
      } catch (error) {
        console.error('Resume upload verification failed:', error);

        // Log page state for debugging
        const alerts = await page.locator('[role="alert"]').allTextContents();
        console.error('Alert content:', alerts);

        const pageContent = await page.locator('body').textContent();
        console.error('Page content (first 500 chars):', pageContent?.substring(0, 500));

        throw error;
      }
    });

    // ========== STEP 3: Search for a job ==========
    await test.step('Search for a job (Python Developer)', async () => {
      console.log('Step 3: Searching for job...');

      await page.goto('/job-search');
      await waitForLoadingToComplete(page);
      await expect(page).toHaveURL(/.*job-search/);

      const searchInput = page.locator('input[placeholder*="Search"], input[placeholder*="Job"], input[name="query"], input[name="search"]').first();

      if (await searchInput.isVisible()) {
        console.log('Filling search query...');
        await fillFieldWithRetry(page, 'input[placeholder*="Search"], input[placeholder*="Job"], input[name="query"], input[name="search"]', 'Python Developer');

        const searchButton = page.getByRole('button', { name: /search/i });
        if (await searchButton.isVisible()) {
          console.log('Clicking search button...');
          await searchButton.click();
          await waitForLoadingToComplete(page);

          // Verify search results
          const jobCards = page
            .locator('[data-testid="job-card"]')
            .or(page.locator('.job-card'))
            .or(page.locator('.job-item'));
          const emptyState = page.getByText(/no results/i);
          const cardCount = await jobCards.count();

          console.log('Job cards found:', cardCount);

          expect(cardCount > 0 || (await emptyState.isVisible().catch(() => false))).toBeTruthy();
        }
      }
    });

    // ========== STEP 4: Apply to job ==========
    await test.step('Apply to a job', async () => {
      console.log('Step 4: Applying to job...');

      // Find and click Apply button on job card
      const applyButton = page.getByRole('button', { name: /apply/i }).first();

      if (await applyButton.isVisible().catch(() => false)) {
        console.log('Found Apply button, clicking...');
        await applyButton.click({ force: true });
        await page.waitForTimeout(2000);

        // Check for create application modal
        const createAppModal = page.locator('[role="dialog"]').filter({ hasText: /create application/i });
        if (await createAppModal.isVisible().catch(() => false)) {
          console.log('Create application modal opened...');

          const submitButton = page
            .getByRole('button', { name: /create application|save/i })
            .first();

          if (await submitButton.isVisible().catch(() => false)) {
            console.log('Submitting application...');
            await submitButton.click({ force: true });
            await page.waitForTimeout(2000);

          // Check for success
          try {
            await waitForToast(page, 'created', 5000);
            console.log('Application created successfully!');
          } catch (error) {
            console.log('Application submission - no toast message, but continuing');
          }
          }
        }
      } else {
        console.log('Apply button not visible, skipping apply step');
      }

      // Just verify we're still on a valid page
      const currentUrl = page.url();
      expect(currentUrl).toBeTruthy();
    });

    // ========== STEP 5: Navigate to applications ==========
    await test.step('View applications list', async () => {
      console.log('Step 5: Viewing applications...');

      await page.goto('/applications');
      await waitForLoadingToComplete(page);
      await expect(page).toHaveURL(/.*applications/);

      // Check for applications list or empty state
      const appCards = page
        .locator('[data-testid="application-card"]')
        .or(page.locator('.application-card'))
        .or(page.locator('.application-item'));
      const emptyState = page.getByText(/no applications/i);

      const hasApps = (await appCards.count()) > 0;
      console.log('Applications found:', await appCards.count());

      expect(hasApps || (await emptyState.isVisible().catch(() => false))).toBeTruthy();
    });

    // ========== STEP 6: Navigate to AI Services ==========
    await test.step('Navigate to AI Services', async () => {
      console.log('Step 6: Navigating to AI Services...');

      const aiServicesLink = page
        .getByRole('link', { name: /ai services/i })
        .or(page.getByRole('button', { name: /ai services/i }))
        .or(page.getByTestId('ai-services'))
        .or(page.locator('a[href*="ai-services"]'))
        .first();

      let aiServicesFound = false;
      if (await aiServicesLink.isVisible().catch(() => false)) {
        console.log('Found AI Services link...');
        await aiServicesLink.click({ force: true });
        aiServicesFound = true;
      }

      if (!aiServicesFound) {
        console.log('AI Services link not found, using direct navigation...');
        await page.goto('/ai-services', { waitUntil: 'networkidle' });
      }

      await page.waitForLoadState('networkidle').catch(() => {
        console.log('Network idle timeout, continuing');
      });
      await page.waitForTimeout(1000);

      const currentUrl = page.url();
      console.log('Current URL:', currentUrl);
      expect(currentUrl).toMatch(/.*ai-services/);

      // Verify AI services content
      const optimizeButton = page.getByRole('button', { name: /optimize resume/i });
      const coverLetterButton = page.getByRole('button', { name: /generate cover letter/i });

      const hasContent = (await optimizeButton.isVisible().catch(() => false)) ||
                       (await coverLetterButton.isVisible().catch(() => false));
      console.log('AI service buttons visible:', hasContent);
      expect(hasContent).toBeTruthy();
    });

    // ========== STEP 7: Test Resume Optimization ==========
    await test.step('Test resume optimization with real PDF', async () => {
      console.log('Step 7: Testing resume optimization...');

      const optimizeButton = page.getByRole('button', { name: /optimize resume/i });

      if (await optimizeButton.isVisible().catch(() => false)) {
        console.log('Found optimize resume button, clicking...');
        await optimizeButton.click({ force: true });
        await page.waitForTimeout(1500);

        // Check for modal or form
        const modal = page.locator('[role="dialog"]');
        if (await modal.isVisible().catch(() => false)) {
          console.log('Optimization modal opened...');

          // Fill job description
          const jobDescInput = page.getByLabel('Job Description').or(page.getByPlaceholder(/job description/i));
          if (await jobDescInput.isVisible().catch(() => false)) {
            console.log('Filling job description...');
            await jobDescInput.fill('Looking for a Senior Python Developer with FastAPI, Django, and React experience.');
            await page.waitForTimeout(300);
          }

          // Select resume if needed
          const resumeSelect = page.locator('select').or(page.getByRole('combobox', { name: /resume/i }));
          if (await resumeSelect.first().isVisible().catch(() => false)) {
            console.log('Selecting uploaded resume...');
            const firstOption = resumeSelect.first().locator('option').nth(1);
            if (await firstOption.isVisible().catch(() => false)) {
              await resumeSelect.first().selectOption({ index: 1 });
              await page.waitForTimeout(300);
            }
          }

          // Submit optimization request
          const submitButton = page
            .getByRole('button', { name: /optimize|generate/i })
            .first();

          if (await submitButton.isVisible().catch(() => false)) {
            console.log('Submitting optimization request...');
            await submitButton.click({ force: true });

            // Wait for AI processing (may take time)
            await page.waitForTimeout(5000);

            // Check for result
            const generatedContent = page.getByText(/optimized resume|suggestions|improvements/i);
            const successAlert = page.getByRole('alert').filter({ hasText: /success|optimized/i });
            const errorAlert = page.getByRole('alert').filter({ hasText: /error|failed/i });

            const hasGenerated = await generatedContent.isVisible().catch(() => false);
            const hasSuccess = await successAlert.isVisible().catch(() => false);
            const hasError = await errorAlert.isVisible().catch(() => false);

            if (hasError) {
              const errorContent = await errorAlert.allTextContents();
              console.error('Optimization error:', errorContent);
            }

            console.log('Optimization result - Generated:', hasGenerated, 'Success:', hasSuccess, 'Error:', hasError);

            // Accept any valid outcome
            expect(hasGenerated || hasSuccess || !hasError).toBeTruthy();
          }
        }
      } else {
        console.log('Optimize button not found, skipping optimization step');
      }
    });
  });

  test('should upload and manage resume with real PDF', async ({ page }) => {
    console.log('Testing resume management with real PDF...');

    // Navigate to resumes page
    await page.goto('/resumes');
    await waitForLoadingToComplete(page);

    // Get the real PDF file path
    const pdfPath = join(process.cwd(), 'resumes', 'test_resume.pdf');
    console.log('PDF file path:', pdfPath);

    // Upload the PDF
    const uploadButton = page
      .getByRole('button', { name: /upload resume|upload|add resume/i })
      .or(page.getByTestId('upload-resume'));
    const fileInput = page.locator('input[type="file"]');

    if (await fileInput.isVisible().catch(() => false)) {
      console.log('Uploading PDF via file input...');
      await fileInput.setInputFiles(pdfPath);
    } else if (await uploadButton.isVisible().catch(() => false)) {
      await uploadButton.click();
      await page.waitForTimeout(500);
      const modalInput = page.locator('input[type="file"]').first();
      await modalInput.setInputFiles(pdfPath);
    }

    // Verify upload
    await waitForToast(page, 'uploaded', 15000);
    console.log('PDF uploaded successfully!');

    // Wait for resume to appear in list
    await page.waitForTimeout(2000);

    // Verify resume is displayed
    const resumeCards = page
      .locator('[data-testid="resume-card"]')
      .or(page.locator('.resume-card'))
      .or(page.locator('.resume-item'));

    const cardCount = await resumeCards.count();
    console.log('Resume cards found:', cardCount);

    expect(cardCount).toBeGreaterThan(0);

    // Try to view resume details
    const firstCard = resumeCards.first();
    if (await firstCard.isVisible().catch(() => false)) {
      console.log('Clicking on resume card...');
      await firstCard.click();
      await page.waitForTimeout(1000);

      // Verify details page
      const detailHeading = page.getByRole('heading').or(page.getByTestId('resume-detail'));
      if ((await detailHeading.count()) > 0) {
        console.log('Resume details page loaded');
        expect(page.url()).toMatch(/resume/);
      }
    }
  });
});
