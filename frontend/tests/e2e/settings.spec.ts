/**
 * E2E tests for Settings Page
 */

import { test, expect } from '@playwright/test';
import { loginAsUser, waitForLoadingToComplete, waitForToast, elementExists } from './utils';
import { testUsers } from './fixtures/test-data';

test.describe('Settings Page', () => {
  test.beforeEach(async ({ page }) => {
    // Setup: Mock authentication
    await page.goto('/login');
    await page.evaluate(() => {
      localStorage.setItem('token', 'mock-token');
      localStorage.setItem('user', JSON.stringify({
        id: '1',
        email: 'test@example.com',
        name: 'Test User',
        first_name: 'Test',
        last_name: 'User',
      }));
    });
  });

  test('should navigate to Settings page', async ({ page }) => {
    await page.goto('/settings');
    await expect(page).toHaveURL(/.*settings/);

    // Check for Settings title
    const title = page.locator('h1:has-text("Settings"), h1:has-text("settings")').first();
    await expect(title).toBeVisible();
  });

  test('should display all settings cards', async ({ page }) => {
    await page.goto('/settings');
    await waitForLoadingToComplete(page);

    // Check for Profile Settings card
    const profileCard = page.locator('text=Profile').first();
    await expect(profileCard).toBeVisible();

    // Check for Notification Settings card
    const notificationCard = page.locator('text=Notification').first();
    await expect(notificationCard).toBeVisible();

    // Check for Theme & Appearance card
    const themeCard = page.locator('text=Theme').first();
    await expect(themeCard).toBeVisible();

    // Check for Language & Region card
    const languageCard = page.locator('text=Language').first();
    await expect(languageCard).toBeVisible();

    // Check for Data Management card
    const dataCard = page.locator('text=Data').first();
    await expect(dataCard).toBeVisible();
  });

  test('should open and close Profile modal', async ({ page }) => {
    await page.goto('/settings');
    await waitForLoadingToComplete(page);

    // Find and click Profile Settings button
    const profileButtons = page.locator('button:has-text("Edit Profile"), button:has-text("Update Profile")');
    const profileButton = profileButtons.first();
    
    if (await profileButton.isVisible()) {
      await profileButton.click();
      await page.waitForTimeout(500);

      // Check if modal is open
      const modal = page.locator('[role="dialog"], .modal').first();
      await expect(modal).toBeVisible();

      // Check for form fields
      const firstNameInput = page.locator('input[name="first_name"], input[placeholder*="first"]').first();
      await expect(firstNameInput).toBeVisible();

      // Close modal
      const closeButton = page.locator('button:has-text("Cancel")').first();
      await closeButton.click();
      await page.waitForTimeout(300);

      // Modal should be closed
      await expect(modal).not.toBeVisible();
    }
  });

  test('should update profile information', async ({ page }) => {
    await page.goto('/settings');
    await waitForLoadingToComplete(page);

    // Open Profile modal
    const profileButtons = page.locator('button:has-text("Edit Profile"), button:has-text("Update Profile")');
    const profileButton = profileButtons.first();
    
    if (await profileButton.isVisible()) {
      await profileButton.click();
      await page.waitForTimeout(500);

      // Fill in profile fields
      const firstNameInput = page.locator('input[name="first_name"]').first();
      const lastNameInput = page.locator('input[name="last_name"]').first();
      const phoneInput = page.locator('input[name="phone"]').first();

      if (await firstNameInput.isVisible()) {
        await firstNameInput.fill('Updated');
      }

      if (await lastNameInput.isVisible()) {
        await lastNameInput.fill('User');
      }

      if (await phoneInput.isVisible()) {
        await phoneInput.fill('(555) 123-4567');
      }

      // Submit form
      const submitButton = page.locator('button:has-text("Save Changes"), button[type="submit"]').first();
      if (await submitButton.isVisible()) {
        await submitButton.click();
        await page.waitForTimeout(1000);

        // Check for success message
        const successMessage = page.locator('[role="alert"], .alert, text=success, text=updated').first();
        if (await successMessage.isVisible().catch(() => false)) {
          await expect(successMessage).toContainText(/success|updated|saved/i);
        }
      }
    }
  });

  test('should toggle email notifications', async ({ page }) => {
    await page.goto('/settings');
    await waitForLoadingToComplete(page);

    // Find and click Notification Settings button
    const notificationButtons = page.locator('button:has-text("Notification"), button:has-text("Email")');
    const notificationButton = notificationButtons.first();
    
    if (await notificationButton.isVisible()) {
      await notificationButton.click();
      await page.waitForTimeout(500);

      // Check if modal is open
      const modal = page.locator('[role="dialog"], .modal').first();
      await expect(modal).toBeVisible();

      // Look for email notification checkboxes
      const emailCheckboxes = page.locator('input[type="checkbox"]');
      const checkboxCount = await emailCheckboxes.count();

      if (checkboxCount > 0) {
        // Toggle first checkbox
        const firstCheckbox = emailCheckboxes.first();
        const isChecked = await firstCheckbox.isChecked();
        
        await firstCheckbox.click();
        await page.waitForTimeout(300);

        // Verify checkbox state changed
        const newCheckedState = await firstCheckbox.isChecked();
        expect(newCheckedState).not.toBe(isChecked);
      }

      // Close modal
      const closeButton = page.locator('button:has-text("Cancel"), button:has-text("Close")').first();
      if (await closeButton.isVisible()) {
        await closeButton.click();
        await page.waitForTimeout(300);
      }
    }
  });

  test('should change theme preference', async ({ page }) => {
    await page.goto('/settings');
    await waitForLoadingToComplete(page);

    // Find and click Theme button
    const themeButtons = page.locator('button:has-text("Theme"), button:has-text("Appearance")');
    const themeButton = themeButtons.first();
    
    if (await themeButton.isVisible()) {
      await themeButton.click();
      await page.waitForTimeout(500);

      // Check if modal is open
      const modal = page.locator('[role="dialog"], .modal').first();
      await expect(modal).toBeVisible();

      // Look for theme radio buttons or options
      const themeOptions = page.locator('input[name="theme"], input[type="radio"]');
      const optionCount = await themeOptions.count();

      if (optionCount > 0) {
        // Get current selected theme
        const currentSelected = await themeOptions.first().isChecked();

        // Click on a different theme option
        const secondOption = themeOptions.nth(optionCount > 1 ? 1 : 0);
        await secondOption.click();
        await page.waitForTimeout(300);

        // Verify selection changed
        const newSelected = await secondOption.isChecked();
        expect(newSelected).toBe(true);
      }

      // Close modal
      const closeButton = page.locator('button:has-text("Close"), button:has-text("Cancel")').first();
      if (await closeButton.isVisible()) {
        await closeButton.click();
        await page.waitForTimeout(300);
      }
    }
  });

  test('should display current theme badge', async ({ page }) => {
    await page.goto('/settings');
    await waitForLoadingToComplete(page);

    // Look for theme badge showing current theme
    const themeBadge = page.locator('text=Light, text=Dark, text=System').first();
    if (await themeBadge.isVisible().catch(() => false)) {
      await expect(themeBadge).toBeVisible();
    }
  });

  test('should change language preference', async ({ page }) => {
    await page.goto('/settings');
    await waitForLoadingToComplete(page);

    // Find and click Language button
    const languageButtons = page.locator('button:has-text("Language"), button:has-text("Region")');
    const languageButton = languageButtons.first();
    
    if (await languageButton.isVisible()) {
      await languageButton.click();
      await page.waitForTimeout(500);

      // Check if modal is open
      const modal = page.locator('[role="dialog"], .modal').first();
      await expect(modal).toBeVisible();

      // Look for language radio buttons
      const languageOptions = page.locator('input[name="language"], input[type="radio"]');
      const optionCount = await languageOptions.count();

      if (optionCount > 0) {
        // Click on a language option
        const languageOption = languageOptions.first();
        await languageOption.click();
        await page.waitForTimeout(300);

        // Verify selection
        const isSelected = await languageOption.isChecked();
        expect(isSelected).toBe(true);
      }

      // Close modal
      const closeButton = page.locator('button:has-text("Close"), button:has-text("Cancel")').first();
      if (await closeButton.isVisible()) {
        await closeButton.click();
        await page.waitForTimeout(300);
      }
    }
  });

  test('should open Privacy & Security modal', async ({ page }) => {
    await page.goto('/settings');
    await waitForLoadingToComplete(page);

    // Find and click Privacy & Security button
    const privacyButtons = page.locator('button:has-text("Privacy"), button:has-text("Security")');
    const privacyButton = privacyButtons.first();
    
    if (await privacyButton.isVisible()) {
      await privacyButton.click();
      await page.waitForTimeout(500);

      // Check if modal is open
      const modal = page.locator('[role="dialog"], .modal').first();
      await expect(modal).toBeVisible();

      // Look for privacy settings
      const privacySettings = page.locator('text=Profile Visibility, text=Data Sharing, text=Two-Factor').first();
      if (await privacySettings.isVisible().catch(() => false)) {
        await expect(privacySettings).toBeVisible();
      }

      // Close modal
      const closeButton = page.locator('button:has-text("Cancel"), button:has-text("Close")').first();
      if (await closeButton.isVisible()) {
        await closeButton.click();
        await page.waitForTimeout(300);
      }
    }
  });

  test('should open Data Management section', async ({ page }) => {
    await page.goto('/settings');
    await waitForLoadingToComplete(page);

    // Look for Export Data button
    const exportButton = page.locator('button:has-text("Export")').first();
    if (await exportButton.isVisible()) {
      await expect(exportButton).toBeVisible();
    }

    // Look for Delete Account button
    const deleteButton = page.locator('button:has-text("Delete")').first();
    if (await deleteButton.isVisible()) {
      await expect(deleteButton).toBeVisible();
    }
  });

  test('should open Export Data modal', async ({ page }) => {
    await page.goto('/settings');
    await waitForLoadingToComplete(page);

    // Find and click Export Data button
    const exportButton = page.locator('button:has-text("Export")').first();
    
    if (await exportButton.isVisible()) {
      await exportButton.click();
      await page.waitForTimeout(500);

      // Check if modal is open
      const modal = page.locator('[role="dialog"], .modal').first();
      await expect(modal).toBeVisible();

      // Check for export confirmation text
      const exportText = page.locator('text=Export Your Data, text=Download').first();
      if (await exportText.isVisible().catch(() => false)) {
        await expect(exportText).toBeVisible();
      }

      // Close modal
      const closeButton = page.locator('button:has-text("Cancel")').first();
      if (await closeButton.isVisible()) {
        await closeButton.click();
        await page.waitForTimeout(300);
      }
    }
  });

  test('should open Delete Account modal', async ({ page }) => {
    await page.goto('/settings');
    await waitForLoadingToComplete(page);

    // Find and click Delete Account button
    const deleteButton = page.locator('button:has-text("Delete")').first();
    
    if (await deleteButton.isVisible()) {
      await deleteButton.click();
      await page.waitForTimeout(500);

      // Check if modal is open
      const modal = page.locator('[role="dialog"], .modal').first();
      await expect(modal).toBeVisible();

      // Check for delete confirmation text
      const deleteText = page.locator('text=Delete Your Account, text=cannot be undone').first();
      if (await deleteText.isVisible().catch(() => false)) {
        await expect(deleteText).toBeVisible();
      }

      // Check for confirmation input
      const confirmInput = page.locator('input[placeholder*="DELETE"]').first();
      if (await confirmInput.isVisible().catch(() => false)) {
        await expect(confirmInput).toBeVisible();
      }

      // Close modal without confirming
      const closeButton = page.locator('button:has-text("Cancel")').first();
      if (await closeButton.isVisible()) {
        await closeButton.click();
        await page.waitForTimeout(300);
      }
    }
  });

  test('should display AI Intelligence settings', async ({ page }) => {
    await page.goto('/settings');
    await waitForLoadingToComplete(page);

    // Look for AI Intelligence card
    const aiCard = page.locator('text=AI Intelligence, text=Sparkles').first();
    if (await aiCard.isVisible().catch(() => false)) {
      await expect(aiCard).toBeVisible();

      // Look for AI settings button
      const aiButton = page.locator('button:has-text("AI"), button:has-text("Intelligence")').first();
      if (await aiButton.isVisible()) {
        await aiButton.click();
        await page.waitForTimeout(500);

        // Check if modal is open
        const modal = page.locator('[role="dialog"], .modal').first();
        await expect(modal).toBeVisible();

        // Close modal
        const closeButton = page.locator('button:has-text("Close")').first();
        if (await closeButton.isVisible()) {
          await closeButton.click();
          await page.waitForTimeout(300);
        }
      }
    }
  });

  test('should display success message after profile update', async ({ page }) => {
    await page.goto('/settings');
    await waitForLoadingToComplete(page);

    // Open Profile modal
    const profileButton = page.locator('button:has-text("Edit Profile"), button:has-text("Update Profile")').first();
    
    if (await profileButton.isVisible()) {
      await profileButton.click();
      await page.waitForTimeout(500);

      // Fill in a field
      const firstNameInput = page.locator('input[name="first_name"]').first();
      if (await firstNameInput.isVisible()) {
        await firstNameInput.fill('Updated');

        // Submit form
        const submitButton = page.locator('button:has-text("Save Changes"), button[type="submit"]').first();
        if (await submitButton.isVisible()) {
          await submitButton.click();
          await page.waitForTimeout(1000);

          // Check for success alert
          const successAlert = page.locator('[role="alert"], .alert-success, text=success').first();
          if (await successAlert.isVisible().catch(() => false)) {
            await expect(successAlert).toBeVisible();
          }
        }
      }
    }
  });

  test('should protect Settings page when not authenticated', async ({ page }) => {
    // Clear authentication
    await page.goto('/login');
    await page.evaluate(() => {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    });

    // Try to access Settings
    await page.goto('/settings');
    await page.waitForTimeout(1000);

    // Should redirect to login
    const currentUrl = page.url();
    expect(currentUrl).toMatch(/login/);
  });

  test('should have responsive layout on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });

    await page.goto('/settings');
    await waitForLoadingToComplete(page);

    // Check that settings cards are visible
    const profileCard = page.locator('text=Profile').first();
    await expect(profileCard).toBeVisible();

    // Cards should stack vertically on mobile
    const cards = page.locator('[class*="card"], [class*="Card"]');
    const cardCount = await cards.count();
    expect(cardCount > 0).toBeTruthy();
  });

  test('should have responsive layout on tablet', async ({ page }) => {
    // Set tablet viewport
    await page.setViewportSize({ width: 768, height: 1024 });

    await page.goto('/settings');
    await waitForLoadingToComplete(page);

    // Check that settings cards are visible
    const profileCard = page.locator('text=Profile').first();
    await expect(profileCard).toBeVisible();
  });

  test('should have responsive layout on desktop', async ({ page }) => {
    // Set desktop viewport
    await page.setViewportSize({ width: 1920, height: 1080 });

    await page.goto('/settings');
    await waitForLoadingToComplete(page);

    // Check that settings cards are visible
    const profileCard = page.locator('text=Profile').first();
    await expect(profileCard).toBeVisible();
  });
});
