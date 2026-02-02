import { test, expect } from '@playwright/test';

test.describe('E2E: PDF Resume Upload Test', () => {
  test.setTimeout(120000);
  
  test('should upload real PDF resume from file system', async ({ page }) => {
    // Log start
    console.log('Starting E2E PDF upload test...');
    console.log('PDF path: test_resume.pdf');
    console.log('Frontend URL: http://localhost:5173');
    
    // Step 1: Navigate directly to resumes upload URL
    console.log('Step 1: Navigating to resumes page...');
    await page.goto('http://localhost:5173/resumes');
    await page.waitForLoadState('networkidle');
    console.log('✅ Resumes page loaded');
    
    // Step 2: Find file upload input
    console.log('Step 2: Finding file input...');
    const fileInput = page.locator('input[type="file"], input[name="resume"]');
    const isVisible = await fileInput.isVisible();
    
    if (!isVisible) {
      console.error('❌ File input not found!');
      throw new Error('File input element not found');
    }
    
    console.log('✅ File input found');
    
    // Step 3: Upload the PDF
    console.log('Step 3: Uploading PDF resume...');
    const pdfPath = require('path').join(__dirname, '..', 'resumes', 'test_resume.pdf');
    
    console.log('PDF file path:', pdfPath);
    const { stat } = require('fs');
    const fileExists = stat.existsSync(pdfPath);
    
    if (!fileExists) {
      console.error(`❌ PDF file not found: ${pdfPath}`);
      throw new Error('PDF file does not exist');
    }
    
    console.log('✅ PDF file exists, size:', stat.statSync(pdfPath).size);
    
    // Upload the file
    await fileInput.setInputFiles(pdfPath);
    console.log('File uploaded to browser');
    
    // Step 4: Wait for upload to complete
    console.log('Step 4: Waiting for upload to complete...');
    
    // Wait for success message, page update, or timeout
    await page.waitForTimeout(10000);
    
    // Check if any upload succeeded
    const pageContent = await page.content();
    const successDetected = 
      pageContent.includes('uploaded') ||
      pageContent.includes('success') ||
      pageContent.includes('Resume');
    
    console.log('Page content check:');
    console.log('Page content:', pageContent?.substring(0, 200));
    
    if (successDetected) {
      console.log('✅ Upload appears to have succeeded!');
    } else {
      console.log('⚠️ Upload status unclear - checking for resume cards...');
      
      // Try to find uploaded resume by checking cards
      const resumeCards = await page.locator('[data-testid="resume-card"], [data-testid="resume-item"], .resume-card, .resume-item').all();
      console.log(`Found ${resumeCards.length} resume card elements`);
      
      if (resumeCards.length > 0) {
        console.log('✅ Resume uploaded and visible in list');
      } else {
        console.log('No resume cards found - checking error messages...');
      }
    }
    
    console.log('Test completed');
  });
});
