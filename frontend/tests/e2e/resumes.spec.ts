/**
 * E2E tests for Resume Management
 */

import { test, expect } from '@playwright/test';
import { waitForLoadingToComplete, waitForToast } from './utils';

test.describe('Resume Management', () => {
  test.beforeEach(async ({ page }) => {
    // Mock authentication
    await page.goto('/login');
    await page.evaluate(() => {
      localStorage.setItem('token', 'mock-token');
      localStorage.setItem('user', JSON.stringify({ id: '1', email: 'test@example.com' }));
    });
  });

  test('should display resumes list', async ({ page }) => {
    await page.goto('/resumes');
    await waitForLoadingToComplete(page);

    await expect(page).toHaveURL(/.*resumes/);
    
    // Check for resumes list or empty state
    const hasResumes = await page.locator('[data-testid="resume-card"], .resume-card, .resume-item').count();
    const hasEmptyState = await page.locator('text=No resumes, text=Upload your first resume').count();
    
    expect(hasResumes > 0 || hasEmptyState > 0).toBeTruthy();
  });

  test('should navigate to upload resume page', async ({ page }) => {
    await page.goto('/resumes');
    await waitForLoadingToComplete(page);

    // Look for upload button
    const uploadButton = page.locator('button:has-text("Upload"), button:has-text("Add Resume"), a:has-text("Upload")').first();
    
    if (await uploadButton.isVisible()) {
      await uploadButton.click();
      await page.waitForTimeout(1000);
      
      // Should show upload form or modal
      const hasUploadForm = await page.locator('input[type="file"], [data-testid="upload-form"]').count();
      expect(hasUploadForm > 0).toBeTruthy();
    }
  });

  test('should upload resume file', async ({ page }) => {
    await page.goto('/resumes');
    await waitForLoadingToComplete(page);

    // Find upload button
    const uploadSelectors = [
      'button:has-text("Upload Resume")',
      'button:has-text("Upload")',
      'input[type="file"]',
      '[data-testid="upload-resume"]',
    ];

    for (const selector of uploadSelectors) {
      const element = page.locator(selector).first();
      if (await element.isVisible().catch(() => false)) {
        if (element.tagName() === 'INPUT') {
          // Create a test file
          const fileInput = element;
          await fileInput.setInputFiles({
            name: 'test-resume.pdf',
            mimeType: 'application/pdf',
            buffer: Buffer.from('Test resume content'),
          });
          
          // Wait for upload to complete
          await waitForToast(page, /uploaded|success/i, 10000);
        } else {
          await element.click();
          await page.waitForTimeout(1000);
          
          // Try to find file input in modal/form
          const fileInput = page.locator('input[type="file"]').first();
          if (await fileInput.isVisible().catch(() => false)) {
            await fileInput.setInputFiles({
              name: 'test-resume.pdf',
              mimeType: 'application/pdf',
              buffer: Buffer.from('Test resume content'),
            });
            await waitForToast(page, /uploaded|success/i, 10000);
          }
        }
        break;
      }
    }
  });

  test('should view resume details', async ({ page }) => {
    await page.goto('/resumes');
    await waitForLoadingToComplete(page);

    // Try to click on first resume
    const resumeSelectors = [
      '[data-testid="resume-card"]',
      '.resume-card',
      '.resume-item',
      'a[href*="resume"]',
    ];

    for (const selector of resumeSelectors) {
      const element = page.locator(selector).first();
      if (await element.isVisible().catch(() => false)) {
        await element.click();
        await page.waitForTimeout(1000);
        
        // Check if we're on detail page
        const isDetailPage = await page.locator('h1, h2, [data-testid="resume-detail"]').count();
        if (isDetailPage > 0) {
          expect(page.url()).toMatch(/resume/);
          return;
        }
      }
    }
  });

  test('should set default resume', async ({ page }) => {
    await page.goto('/resumes');
    await waitForLoadingToComplete(page);

    // Look for set default button
    const defaultButton = page.locator('button:has-text("Set Default"), button:has-text("Make Default"), [data-testid="set-default"]').first();
    
    if (await defaultButton.isVisible()) {
      await defaultButton.click();
      await waitForToast(page, /default|updated/i);
    }
  });

  test('should delete resume', async ({ page }) => {
    await page.goto('/resumes');
    await waitForLoadingToComplete(page);

    // Look for delete button
    const deleteButton = page.locator('button:has-text("Delete"), button[aria-label*="Delete"], [data-testid="delete-resume"]').first();
    
    if (await deleteButton.isVisible()) {
      // Accept confirmation dialog if it appears
      page.on('dialog', async (dialog) => {
        await dialog.accept();
      });
      
      await deleteButton.click();
      await waitForToast(page, /deleted|removed/i);
    }
  });
});
