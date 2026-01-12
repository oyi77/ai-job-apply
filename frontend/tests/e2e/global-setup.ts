/**
 * Global setup for E2E tests
 * Runs once before all tests
 */

import { chromium, FullConfig } from '@playwright/test';

async function globalSetup(config: FullConfig) {
  console.log('🔧 Setting up E2E test environment...');

  const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
  console.log(`🔍 Checking backend health at ${backendUrl}...`);

  // Check if backend is available
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const request = context.request;

  let retries = 10;
  while (retries > 0) {
    try {
      const response = await request.get(`${backendUrl}/health`);
      if (response.ok()) {
        console.log('✅ Backend is healthy');
        await browser.close();
        return;
      }
    } catch (error) {
      // Backend not ready yet
    }
    
    console.log(`⏳ Backend not ready, retrying... (${retries} attempts left)`);
    await new Promise((resolve) => setTimeout(resolve, 2000));
    retries--;
  }

  await browser.close();
  throw new Error('Backend server is not available after multiple attempts');
}

export default globalSetup;
