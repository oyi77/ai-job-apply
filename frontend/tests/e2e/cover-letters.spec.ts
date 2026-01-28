import { test, expect } from '@playwright/test';

test.describe('Cover Letters Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to Cover Letters page
    await page.goto('/cover-letters');
  });

  test('should generate a cover letter using AI', async ({ page }) => {
    // 1. Click "Generate with AI" button
    await page.getByRole('button', { name: /generate with ai/i }).click();

    // 2. Wait for modal to appear
    const modal = page.getByRole('dialog', { name: /generate cover letter with ai/i });
    await expect(modal).toBeVisible();

    // 3. Fill out the form
    // Note: Assuming there are resumes uploaded. If not, this might fail or we need to mock data.
    // For E2E we usually assume seed data or mock API responses.
    // Here we'll try to interact with the form elements.
    
    // Select resume (custom select component interaction might be needed)
    // For standard HTML select:
    // await page.getByLabel(/select resume/i).selectOption({ index: 1 });
    // For custom select, we might need to click trigger then option.
    // Let's assume custom select pattern:
    await modal.getByText(/select a resume/i).click();
    const resumeOptions = page.getByRole('option');
    if ((await resumeOptions.count()) === 0) {
      test.skip();
    }
    await resumeOptions.first().click();

    await modal.getByLabel('Job Title').fill('Senior Software Engineer');
    await modal.getByLabel('Company').fill('Tech Giant Corp');
    await modal.getByLabel('Job Description').fill('We are looking for a skilled engineer with React and Node.js experience.');

    // 4. Submit form
    await modal.getByRole('button', { name: /generate cover letter/i }).click();

    // 5. Verify loading state
    await expect(page.getByText(/generating cover letter/i)).toBeVisible();

    // 6. Verify result
    await expect(page.getByText(/generation complete/i)).toBeVisible();
    await expect(page.getByText(/save cover letter/i)).toBeVisible();

    // 7. Save the cover letter
    await page.getByRole('button', { name: /save cover letter/i }).click();

    // 8. Verify success and modal close
    await expect(modal).not.toBeVisible();
    
    // 9. Verify new cover letter appears in list
    await expect(page.getByText('Senior Software Engineer')).toBeVisible();
    await expect(page.getByText('Tech Giant Corp')).toBeVisible();
  });

  test('should create a manual cover letter', async ({ page }) => {
    // 1. Click "Create New" button
    await page.getByRole('button', { name: /create new/i }).click();

    // 2. Wait for modal
    const modal = page.getByRole('dialog', { name: /create new cover letter/i });
    await expect(modal).toBeVisible();

    // 3. Fill form
    await modal.getByLabel('Job Title').fill('Frontend Developer');
    await modal.getByLabel('Company').fill('Startup Inc');
    await modal.getByLabel('Content').fill('I am writing to express my interest in the Frontend Developer position...');
    
    // 4. Submit
    await modal.getByRole('button', { name: /create cover letter/i }).click();

    // 5. Verify success
    await expect(modal).not.toBeVisible();
    await expect(page.getByText('Frontend Developer')).toBeVisible();
    await expect(page.getByText('Startup Inc')).toBeVisible();
  });
});
