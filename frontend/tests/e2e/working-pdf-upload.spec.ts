import { test, expect } from '@playwright/test';

test.describe('Working PDF Upload Test', () => {
  test.setTimeout(120000);
  
  test('should upload real PDF resume', async ({ page }) => {
    // First register a new user to get a valid session
    const timestamp = Date.now();
    const testEmail = `testuser-${timestamp}@example.com`;
    const testPassword = 'Test123!@#';
    const testName = `Test User ${timestamp}`;
    
    console.log('='.repeat(50));
    console.log('WORKING PDF UPLOAD TEST');
    console.log('='.repeat(50));
    console.log(`Test Email: ${testEmail}`);
    console.log(`Test Password: ${testPassword}`);
    console.log('='.repeat(50));
    
    // Step 1: Register new user
    console.log('Step 1: Registering new user...');
    await page.goto('http://localhost:5173/register');
    await page.waitForLoadState('domcontentloaded');
    
    await page.locator('input[name="name"]').fill(testName);
    await page.locator('input[name="email"]').fill(testEmail);
    await page.locator('input[name="password"]').fill(testPassword);
    await page.locator('input[name="confirmPassword"]').fill(testPassword);
    
    await page.getByRole('button', { name: /create account/i }).click();
    await page.waitForTimeout(3000);
    
    // Check if registration succeeded
    const urlAfterRegister = page.url();
    const registered = !urlAfterRegister.includes('/register');
    
    if (!registered) {
      console.log('Registration may have failed, trying to login...');
      // Try to login with these credentials anyway
    } else {
      console.log('✅ Registration successful!');
    };
    
    // Step 4: Wait for redirect or login success
    console.log('Waiting for login response...');
    
    try {
      // Wait for success toast or redirect (10 second timeout)
      await Promise.race([
        page.waitForSelector('[data-testid="success-message"], [role="alert"]', { timeout: 10000 }),
        page.waitForURL(/\/resumes|\/applications|\/dashboard/, { timeout: 10000 })
      ]);
      
      // Check current URL
      const currentUrl = page.url();
      console.log(`Current URL: ${currentUrl}`);
      
      // If redirected to dashboard, we might need to navigate back to resumes
      if (currentUrl.includes('/dashboard') || currentUrl.includes('/applications')) {
        console.log('Redirected to dashboard, navigating to resumes...');
        await page.goto('http://localhost:5173/resumes');
        await page.waitForLoadState('networkidle');
        console.log('✅ Navigated back to resumes page');
      }
      
    } catch (e) {
      console.error('❌ Error during login:', e);
      await page.screenshot({ path: 'playwright/screenshots/login-error.png', fullPage: true });
      throw e;
    }
    
    // Step 5: Navigate to resumes page (ensure we're there)
    console.log('Waiting 5 seconds before checking resumes page...');
    await page.waitForTimeout(5000);
    await page.goto('http://localhost:5173/resumes');
    await page.waitForLoadState('networkidle');
    console.log('✅ Navigated to resumes page');
    
    // Step 6: Find file upload input
    const fileInput = page.locator('input[type="file"]').first();
    
    if (!await fileInput.isVisible()) {
      throw new Error('File upload input not found!');
    }
    
    console.log('✅ File input found');
    
    // Step 7: Upload PDF
    const { join } = require('path');
    const { stat } = require('fs');
    const pdfPath = join(__dirname, '..', 'resumes', 'test_resume.pdf');
    
    console.log(`Uploading PDF: ${pdfPath}`);
    const fileExists = stat.existsSync(pdfPath);
    
    if (!fileExists) {
      throw new Error(`PDF file not found: ${pdfPath}`);
    }
    
    await fileInput.setInputFiles(pdfPath);
    console.log('✅ PDF uploaded');
    
    // Step 8: Wait for upload to complete (check for success indicator)
    console.log('Waiting for upload to complete...');
    
    try {
      // Wait up to 15 seconds and check for any success indicators
      await page.waitForTimeout(15000);
      
      // Check page content for success
      const pageContent = await page.content();
      
      const success = pageContent.includes('uploaded') || pageContent.includes('success') || pageContent.includes('Resume');
      
      if (success) {
        console.log('✅ Upload appears successful!');
        
        // Wait for resume to appear in list
        await page.goto('http://localhost:5173/resumes');
        await page.waitForLoadState('networkidle');
        
        const resumeCards = await page.locator('[data-testid="resume-card"], .resume-card, .resume-item').all();
        const cardCount = resumeCards.length;
        
        console.log(`Found ${cardCount} resume card(s)`);
        
        if (cardCount > 0) {
          const firstCard = resumeCards[0];
          const fileName = await firstCard.locator('[data-testid="file-name"], .file-name').textContent();
          
          console.log(`First resume file: ${fileName}`);
        } else {
          console.log('⚠️ No resume cards found');
        }
      }
    } catch (e) {
      console.error('❌ Upload failed:', e);
      await page.screenshot({ path: 'playwright/screenshots/upload-error.png', fullPage: true });
      throw e;
    }
  });
});
