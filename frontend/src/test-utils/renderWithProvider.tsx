import React, { ReactElement } from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { AuthProvider } from '../contexts/AuthContext';
import { vi } from 'vitest';
import { authService } from '../services/api';
import type { User } from '../types';

/**
 * Custom render function that wraps components with AuthProvider context.
 * Use this instead of render() for tests that use useAuth() hook.
 *
 * Sets up localStorage tokens and ensures authService.getProfile is properly
 * mocked so AuthProvider can initialize in tests.
 *
 * @param ui - The component to render
 * @param options - Additional render options
 * @returns Render result from React Testing Library
 */
const renderWithProvider = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => {
  // Create a default mock user
  const mockUser: User = {
    id: 'test-user',
    email: 'test@example.com',
    name: 'Test User',
    preferences: {
      theme: 'system',
      notifications: {
        email: true,
        push: true,
        follow_up_reminders: true,
        interview_reminders: true,
        application_updates: true,
      },
      privacy: {
        profile_visibility: 'private',
        data_sharing: false,
        analytics_tracking: true,
      },
      ai: {
        provider_preference: 'gemini',
      },
    },
    created_at: '2024-01-01T00:00:00',
    updated_at: '2024-01-01T00:00:00',
  };

  // Ensure authService.getProfile returns the mock user
  // The test file should have already mocked authService via vi.mock()
  // We just need to set the return value
  if (vi.isMockFunction(authService.getProfile)) {
    (authService.getProfile as any).mockResolvedValue(mockUser);
  }

  // Set a mock token so AuthProvider thinks there's a session
  localStorage.setItem('auth_token', 'mock-token');
  localStorage.setItem('refresh_token', 'mock-refresh-token');

  const Wrapper = ({ children }: { children: React.ReactNode }) => (
    <AuthProvider>{children}</AuthProvider>
  );

  return render(ui, { wrapper: Wrapper, ...options });
};

export { renderWithProvider };
