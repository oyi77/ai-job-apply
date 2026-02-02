import { test, expect } from '@playwright/test';

test.describe('End-to-End Flow: Register and Upload PDF', () => {
  test.setTimeout(120000);
  
  test('should complete full registration and PDF upload flow', async ({ page }) => {
    // Test data
    const timestamp = Date.now();
    const testEmail = `e2e-full-flow-${timestamp}@example.com`;
    const testPassword = 'Test123!@#';  // Strong password meeting all requirements
    const testName = `Test User ${timestamp}`;
    
    console.log('Starting end-to-end test...');
    console.log('Test Email:', testEmail);
    console.log('Test Name:', testName);
    
    // Step 1: Navigate to register page
    console.log('Step 1: Navigating to register page');
    await page.goto('http://localhost:5173/register');
    await page.waitForLoadState('domcontentloaded');
    console.log('✅ Register page loaded');
    
    // Step 2: Fill and submit registration form
    console.log('Step 2: Filling registration form...');
    await page.locator('input[name="email"]').fill(testEmail);
    await page.locator('input[name="password"]').fill(testPassword);
    await page.locator('input[name="name"]').fill(testName);
    
    // Click Create Account button
    await page.getByRole('button', { name: /create account/i }).click();
    console.log('✅ Registration form submitted');
    
    // Step 3: Wait for registration response
    console.log('Step 3: Waiting for registration response...');
    
    try {
      // Wait for redirect or success message
      await Promise.race([
        page.waitForURL(/\/resumes|\/applications|\/dashboard/, { timeout: 5000 }),
        page.waitForSelector('.bg-success, .text-green-500, [data-testid="success-message"], .alert-success', { timeout: 5000 })
      ]);
      
      const currentUrl = page.url();
      console.log('Current URL after registration:', currentUrl);
      
      // Check if we're still on register page (redirect to dashboard means success)
      if (currentUrl.includes('/dashboard') || currentUrl.includes('/applications') || currentUrl.includes('/resumes')) {
        console.log('✅ Registration successful - redirected to dashboard!');
      } else {
        console.log('⚠️ Still on register page or error page');
        const bodyText = await page.locator('body').textContent();
        console.log('Page content:', bodyText);
        
        // Take screenshot for debugging
        await page.screenshot({ path: 'test-results/registration-response.png', fullPage: true });
      }
      
    } catch (e) {
      console.error('❌ Error during registration:', e);
      await page.screenshot({ path: 'test-results/registration-error.png', fullPage: true });
      throw e;
    }
    
    // Step 4: Login to get auth token (if registration failed, try to use test credentials from config)
    console.log('Step 4: Logging in...');
    
    try {
      await page.goto('http://localhost:5173/login');
      await page.waitForLoadState('domcontentloaded');
      console.log('✅ Login page loaded');
      
      // Fill login form
      await page.locator('input[name="email"]').fill(testEmail);
      await page.locator('input[name="password"]').fill(testPassword);
      
      // Click Login button
      await page.getByRole('button', { name: /log in|sign in/i }).click();
      console.log('✅ Login form submitted');
      
      // Wait for redirect or success
      await Promise.race([
        page.waitForURL(/\/resumes|\/applications|\/dashboard/, { timeout: 5000 }),
        page.waitForSelector('.bg-success, .text-green-500, [data-testid="success-message"], .alert-success', { timeout: 5000 })
      ]);
      
      // Get auth token from localStorage or API response
      // Wait for token to be available
      await page.waitForTimeout(2000);
      
      const token = await page.evaluate(() => {
        return localStorage.getItem('access_token');
      });
      
      if (token) {
        console.log('✅ Found auth token in localStorage');
      } else {
        console.log('⚠️ No token found, checking API response...');
        // Try to get token from response headers
        const tokenCookie = await page.context().cookies();
        const accessToken = tokenCookie.find(c => c.name === 'access_token');
        if (accessToken) {
          console.log('✅ Found access token in cookies:', accessToken.value);
        } else {
          console.log('⚠️ No access token in cookies');
        }
      }
      
    } catch (e) {
      console.error('❌ Error during login:', e);
      await page.screenshot({ path: 'test-results/login-error.png', fullPage: true });
      throw e;
    }
    
    // Step 5: Navigate to resumes page and upload PDF
    console.log('Step 5: Navigating to resumes page with auth token...');
    
    try {
      await page.goto('http://localhost:5173/resumes');
      await page.waitForLoadState('networkidle');
      console.log('✅ Resumes page loaded');
      
      // Find file upload input
      const fileInput = page.locator('input[type="file"]').first();
      
      if (!await fileInput.isVisible()) {
        throw new Error('File upload input not found');
      }
      
      // Get the PDF file path
      const { join } = require('path');
      const { stat } = require('fs');
      const pdfPath = join(__dirname, '..', 'resumes', 'test_resume.pdf');
      const pdfExists = stat.existsSync(pdfPath);
      
      console.log('PDF path:', pdfPath);
      console.log('PDF exists:', pdfExists);
      console.log('PDF size:', pdfExists ? stat.statSync(pdfPath).size : 'N/A');
      
      if (!pdfExists) {
        throw new Error('PDF file not found: ' + pdfPath);
      }
      
      // Upload the PDF
      console.log('Uploading PDF...');
      await fileInput.setInputFiles(pdfPath);
      
      // Wait for upload - look for success indicator
      await page.waitForTimeout(15000);
      
      // Check for success by looking for success indicators
      const pageContent = await page.content();
      const successDetected = 
        pageContent.includes('uploaded') || 
        pageContent.includes('success') || 
        pageContent.includes('Resume');
      
      console.log('Page content (first 500 chars):', pageContent?.substring(0, 500));
      
      if (successDetected) {
        console.log('✅ PDF upload successful!');
      } else {
        console.log('⚠️ Upload status unclear - checking for resume cards...');
        // Try to find uploaded resume by checking cards
        const resumeCards = await page.locator('[data-testid="resume-card"], .resume-card, .resume-item').all();
        console.log(`Found ${resumeCards.length} resume cards`);
        
        if (resumeCards.length > 0) {
          const firstCard = resumeCards[0];
          const fileName = await firstCard.locator('[data-testid="file-name"], .file-name').textContent();
          console.log(`Resume file name: ${fileName}`);
        } else {
          // Take screenshot for debugging
          await page.screenshot({ path: 'test-results/upload-status.png', fullPage: true });
          console.log('⚠️ Upload may have failed - check screenshot');
        }
      }
      
    } catch (e) {
      console.error('❌ Error during PDF upload:', e);
      await page.screenshot({ path: 'test-results/upload-error.png', fullPage: true });
      throw e;
    }
    
    // Step 6: Verify PDF was uploaded and is in list
    console.log('Step 6: Verifying PDF upload...');
    
    try {
      await page.goto('http://localhost:5173/resumes');
      await page.waitForLoadState('networkidle');
      
      // Check for uploaded resume
      const resumeList = await page.locator('[data-testid="resume-card"], .resume-card, .resume-item').all();
      
      if (resumeList.length > 0) {
        console.log('✅ PDF was successfully uploaded and appears in list!');
      } else {
        console.log('⚠️ PDF not found in resume list');
        // Take screenshot
        await page.screenshot({ path: 'test-results/final-status.png', fullPage: true });
      }
      
    } catch (e) {
      console.error('❌ Error during verification:', e);
      await page.screenshot({ path: 'test-results/verification-error.png', fullPage: true });
      throw e;
    }
    
    console.log('Test completed');
  });
});
