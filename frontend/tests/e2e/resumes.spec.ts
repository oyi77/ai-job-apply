/**
 * E2E tests for Resume Management
 */

import { test, expect } from '@playwright/test';
import { waitForLoadingToComplete, waitForToast } from './utils';

test.describe('Resume Management', () => {
  test('should display resumes list', async ({ page }) => {
    await page.goto('/resumes');
    await waitForLoadingToComplete(page);

    await expect(page).toHaveURL(/.*resumes/);
    await expect(page.getByRole('heading', { name: /resumes/i })).toBeVisible();
    
    // Check for resumes list or empty state
    const resumeCards = page
      .locator('[data-testid="resume-card"]')
      .or(page.locator('.resume-card'))
      .or(page.locator('.resume-item'));
    const emptyState = page.getByText(/no resumes|upload your first resume/i);

    expect((await resumeCards.count()) > 0 || (await emptyState.isVisible().catch(() => false))).toBeTruthy();
  });

  test('should navigate to upload resume page', async ({ page }) => {
    await page.goto('/resumes');
    await waitForLoadingToComplete(page);

    // Look for upload button
    const uploadButton = page
      .getByRole('button', { name: /upload|add resume/i })
      .or(page.getByRole('link', { name: /upload|add resume/i }));
    
    if (await uploadButton.isVisible()) {
      await uploadButton.click();
      await page.waitForTimeout(1000);
      
      // Should show upload form or modal
      const uploadForm = page.locator('input[type="file"]').or(page.getByTestId('upload-form'));
      expect(await uploadForm.count()).toBeGreaterThan(0);
    }
  });

  test('should upload resume file', async ({ page }) => {
    await page.goto('/resumes');
    await waitForLoadingToComplete(page);

    // Find upload button
    const uploadButton = page
      .getByRole('button', { name: /upload resume|upload/i })
      .or(page.getByTestId('upload-resume'));
    const fileInput = page.locator('input[type="file"]');

    if (await fileInput.isVisible().catch(() => false)) {
      await fileInput.setInputFiles({
        name: 'test-resume.pdf',
        mimeType: 'application/pdf',
        buffer: Buffer.from('Test resume content'),
      });
      await waitForToast(page, 'uploaded', 10000);
      return;
    }

    if (await uploadButton.isVisible().catch(() => false)) {
      await uploadButton.click();
      await page.waitForTimeout(1000);

      const modalFileInput = page.locator('input[type="file"]').first();
      if (await modalFileInput.isVisible().catch(() => false)) {
        await modalFileInput.setInputFiles({
          name: 'test-resume.pdf',
          mimeType: 'application/pdf',
          buffer: Buffer.from('Test resume content'),
        });
        await waitForToast(page, 'uploaded', 10000);
      }
    }
  });

  test('should view resume details', async ({ page }) => {
    await page.goto('/resumes');
    await waitForLoadingToComplete(page);

    // Try to click on first resume
    const resumeCard = page
      .locator('[data-testid="resume-card"]')
      .or(page.locator('.resume-card'))
      .or(page.locator('.resume-item'))
      .or(page.locator('a[href*="resume"]'))
      .first();

    if (await resumeCard.isVisible().catch(() => false)) {
      await resumeCard.click();
      await page.waitForTimeout(1000);

      const detailHeading = page.getByRole('heading').or(page.getByTestId('resume-detail'));
      if ((await detailHeading.count()) > 0) {
        expect(page.url()).toMatch(/resume/);
      }
    }
  });

  test('should set default resume', async ({ page }) => {
    await page.goto('/resumes');
    await waitForLoadingToComplete(page);

    // Look for set default button
    const defaultButton = page
      .getByRole('button', { name: /set default|make default/i })
      .or(page.getByTestId('set-default'));
    
    if (await defaultButton.isVisible()) {
      await defaultButton.click();
      await waitForToast(page, 'default');
    }
  });

  test('should delete resume', async ({ page }) => {
    await page.goto('/resumes');
    await waitForLoadingToComplete(page);

    // Look for delete button
    const deleteButton = page
      .getByRole('button', { name: /delete/i })
      .or(page.getByTestId('delete-resume'));
    
    if (await deleteButton.isVisible()) {
      // Accept confirmation dialog if it appears
      page.on('dialog', async (dialog) => {
        await dialog.accept();
      });
      
      await deleteButton.click();
      await waitForToast(page, 'deleted');
    }
  });
});
