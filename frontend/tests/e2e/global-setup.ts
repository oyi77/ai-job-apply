/**
 * Global setup for E2E tests
 * Runs once before all tests
 */

import { chromium, FullConfig } from '@playwright/test';
import fs from 'fs/promises';
import path from 'path';
import { testUsers } from './fixtures/test-data';

async function globalSetup(config: FullConfig) {
  console.log('🔧 Setting up E2E test environment...');

  const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
  const frontendUrl = process.env.FRONTEND_URL || 'http://localhost:5173';
  console.log(`🔍 Checking backend health at ${backendUrl}...`);

  // Check if backend is available
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const request = context.request;

  let retries = 10;
  let backendHealthy = false;
  while (retries > 0) {
    try {
      const response = await request.get(`${backendUrl}/health`);
      if (response.ok()) {
        console.log('✅ Backend is healthy');
        backendHealthy = true;
        break;
      }
    } catch (error) {
      // Backend not ready yet
    }

    console.log(`⏳ Backend not ready, retrying... (${retries} attempts left)`);
    await new Promise((resolve) => setTimeout(resolve, 2000));
    retries--;
  }

  if (!backendHealthy) {
    await browser.close();
    throw new Error('Backend server is not available after multiple attempts');
  }

  const authDir = path.resolve(process.cwd(), 'playwright/.auth');
  const authFile = path.join(authDir, 'user.json');
  const user = testUsers.valid;

  await fs.mkdir(authDir, { recursive: true });

  const ensureAuthTokens = async () => {
    const loginResponse = await request.post(`${backendUrl}/api/v1/auth/login`, {
      data: { email: user.email, password: user.password },
    });

    if (loginResponse.ok()) {
      return loginResponse.json();
    }

    const registerResponse = await request.post(`${backendUrl}/api/v1/auth/register`, {
      data: { email: user.email, password: user.password, name: user.name },
    });

    if (!registerResponse.ok()) {
      const fallbackLogin = await request.post(`${backendUrl}/api/v1/auth/login`, {
        data: { email: user.email, password: user.password },
      });

      if (!fallbackLogin.ok()) {
        const errorText = await fallbackLogin.text();
        throw new Error(`Unable to authenticate test user: ${errorText}`);
      }

      return fallbackLogin.json();
    }

    return registerResponse.json();
  };

  const tokenResponse = await ensureAuthTokens();
  const accessToken = tokenResponse.access_token || tokenResponse.token;
  const refreshToken = tokenResponse.refresh_token;

  const profileResponse = await request.get(`${backendUrl}/api/v1/auth/me`, {
    headers: { Authorization: `Bearer ${accessToken}` },
  });

  if (!profileResponse.ok()) {
    const errorText = await profileResponse.text();
    throw new Error(`Unable to fetch profile: ${errorText}`);
  }

  const profile = await profileResponse.json();

  const page = await context.newPage();
  await page.addInitScript(
    ({ token, refresh, userProfile }) => {
      localStorage.setItem('auth_token', token);
      localStorage.setItem('refresh_token', refresh);
      localStorage.setItem(
        'ai-job-apply-store',
        JSON.stringify({
          state: {
            user: userProfile,
            isAuthenticated: true,
            theme: 'system',
            searchFilters: {},
            sortOptions: { field: 'created_at', direction: 'desc' },
            aiSettings: { provider_preference: 'openai' },
          },
          version: 0,
        })
      );
    },
    { token: accessToken, refresh: refreshToken, userProfile: profile }
  );

  await page.goto(frontendUrl, { waitUntil: 'domcontentloaded' });
  await context.storageState({ path: authFile });
  await browser.close();
}

export default globalSetup;
