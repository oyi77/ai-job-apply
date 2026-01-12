/**
 * API helper utilities for E2E tests
 */

import { Page, APIRequestContext } from '@playwright/test';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

/**
 * Make API request from test
 */
export async function apiRequest(
  request: APIRequestContext,
  method: 'GET' | 'POST' | 'PUT' | 'DELETE',
  endpoint: string,
  options?: {
    data?: any;
    token?: string;
    headers?: Record<string, string>;
  }
): Promise<any> {
  const url = `${BACKEND_URL}${endpoint}`;
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...options?.headers,
  };

  if (options?.token) {
    headers['Authorization'] = `Bearer ${options.token}`;
  }

  const response = await request.fetch(url, {
    method,
    headers,
    data: options?.data ? JSON.stringify(options.data) : undefined,
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`API request failed: ${response.status} ${errorText}`);
  }

  return response.json();
}

/**
 * Get authentication token from API
 */
export async function getAuthToken(
  request: APIRequestContext,
  email: string,
  password: string
): Promise<string> {
  const response = await apiRequest(request, 'POST', '/api/v1/auth/login', {
    data: { email, password },
  });
  return response.token || response.access_token;
}

/**
 * Create test application via API
 */
export async function createTestApplication(
  request: APIRequestContext,
  token: string,
  application: any
): Promise<any> {
  return apiRequest(request, 'POST', '/api/v1/applications', {
    data: application,
    token,
  });
}

/**
 * Get applications via API
 */
export async function getApplications(
  request: APIRequestContext,
  token: string
): Promise<any[]> {
  const response = await apiRequest(request, 'GET', '/api/v1/applications', {
    token,
  });
  return response.data || response;
}

/**
 * Upload resume via API
 */
export async function uploadResume(
  request: APIRequestContext,
  token: string,
  filePath: string,
  fileName: string
): Promise<any> {
  const formData = new FormData();
  const file = await request.storageState();
  // Note: This is a simplified version. In real tests, you'd need to handle file uploads properly
  return apiRequest(request, 'POST', '/api/v1/resumes/upload', {
    token,
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
}

/**
 * Search jobs via API
 */
export async function searchJobs(
  request: APIRequestContext,
  query: string,
  location?: string
): Promise<any> {
  const params = new URLSearchParams({ query });
  if (location) {
    params.append('location', location);
  }
  return apiRequest(request, 'GET', `/api/v1/jobs/search?${params.toString()}`);
}

/**
 * Check backend health
 */
export async function checkBackendHealth(request: APIRequestContext): Promise<boolean> {
  try {
    const response = await request.get(`${BACKEND_URL}/health`);
    return response.ok();
  } catch {
    return false;
  }
}
