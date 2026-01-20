import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import { AuthProvider, useAuth } from '../AuthContext';
import { authService } from '../../services/api';

// Mock the auth service
vi.mock('../../services/api', () => ({
  authService: {
    login: vi.fn(),
    logout: vi.fn(),
    register: vi.fn(),
    getProfile: vi.fn(),
  },
}));

// Test component that uses useAuth
const TestComponent: React.FC<{ onAuthChange?: (auth: any) => void }> = ({ onAuthChange }) => {
  const auth = useAuth();
  React.useEffect(() => {
    if (onAuthChange) {
      onAuthChange(auth);
    }
  }, [auth, onAuthChange]);

  if (auth.isLoading) {
    return <div data-testid="loading">Loading...</div>;
  }

  return (
    <div>
      <div data-testid="authenticated">{auth.isAuthenticated ? 'true' : 'false'}</div>
      <div data-testid="user-email">{auth.user?.email || 'no-user'}</div>
      <button onClick={() => auth.login('test@example.com', 'password')}>Login</button>
      <button onClick={() => auth.logout()}>Logout</button>
    </div>
  );
};

describe('AuthContext', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    vi.spyOn(localStorage, 'setItem');
    vi.spyOn(localStorage, 'removeItem');
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('provides initial unauthenticated state', () => {
    const handleAuthChange = vi.fn();
    
    render(
      <AuthProvider>
        <TestComponent onAuthChange={handleAuthChange} />
      </AuthProvider>
    );

    expect(handleAuthChange).toHaveBeenCalled();
    const lastCall = handleAuthChange.mock.calls[handleAuthChange.mock.calls.length - 1][0];
    expect(lastCall.isAuthenticated).toBe(false);
    expect(lastCall.user).toBe(null);
    expect(lastCall.isLoading).toBe(false);
  });

  it('logs in user successfully', async () => {
    const mockUser = {
      id: 'user-123',
      email: 'test@example.com',
      name: 'Test User',
      preferences: {
        theme: 'system' as const,
        notifications: {
          email: true,
          push: true,
          follow_up_reminders: true,
          interview_reminders: true,
          application_updates: true,
        },
        privacy: {
          profile_visibility: 'private' as const,
          data_sharing: false,
          analytics_tracking: true,
        },
        ai: {
          provider_preference: 'openai' as const,
        },
      },
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    };

    (authService.login as vi.Mock).mockResolvedValue({
      access_token: 'test-access-token',
      refresh_token: 'test-refresh-token',
    });
    (authService.getProfile as vi.Mock).mockResolvedValue(mockUser);

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    // Click login button
    const loginButton = screen.getByText('Login');
    await userEvent.click(loginButton);

    // Wait for login to complete and state to update
    await waitFor(() => {
      expect(screen.getByTestId('authenticated')).toHaveTextContent('true');
    });

    await waitFor(() => {
      expect(screen.getByTestId('user-email')).toHaveTextContent('test@example.com');
    });

    // Verify service calls
    await waitFor(() => {
      expect(authService.login).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password',
      });
    });
  });

  it('logs out user successfully', async () => {
    const mockUser = {
      id: 'user-123',
      email: 'test@example.com',
      name: 'Test User',
      preferences: {
        theme: 'system' as const,
        notifications: {
          email: true,
          push: true,
          follow_up_reminders: true,
          interview_reminders: true,
          application_updates: true,
        },
        privacy: {
          profile_visibility: 'private' as const,
          data_sharing: false,
          analytics_tracking: true,
        },
        ai: {
          provider_preference: 'openai' as const,
        },
      },
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    };

    // Setup logged in state by manually setting localStorage and state
    (authService.login as vi.Mock).mockResolvedValue({
      access_token: 'test-access-token',
      refresh_token: 'test-refresh-token',
    });
    (authService.getProfile as vi.Mock).mockResolvedValue(mockUser);
    (authService.logout as vi.Mock).mockResolvedValue({});

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    // First login
    const loginButton = screen.getByText('Login');
    await userEvent.click(loginButton);

    await waitFor(() => {
      expect(screen.getByTestId('authenticated')).toHaveTextContent('true');
    });

    // Verify user is logged in
    expect(screen.getByTestId('user-email')).toHaveTextContent('test@example.com');

    // Now logout - the logout function should clear state
    const logoutButton = screen.getByText('Logout');
    await userEvent.click(logoutButton);

    // The state should be cleared after logout
    await waitFor(() => {
      expect(screen.getByTestId('authenticated')).toHaveTextContent('false');
    });
    await waitFor(() => {
      expect(screen.getByTestId('user-email')).toHaveTextContent('no-user');
    });
  });

  it('throws error when useAuth used outside provider', () => {
    const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {});
    
    expect(() => {
      render(<TestComponent />);
    }).toThrow('useAuth must be used within an AuthProvider');
    
    consoleError.mockRestore();
  });
});
