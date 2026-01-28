import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import ProtectedRoute from '../ProtectedRoute';
import { authService } from '../../../services/api';
import { renderWithProvider } from '../../../test-utils/renderWithProvider';

// Mock authService
vi.mock('../../../services/api');

describe('ProtectedRoute', () => {
  const mockUser = {
    id: 'test-user-id',
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
        provider_preference: 'gemini' as const,
      },
    },
    created_at: '2024-01-01T00:00:00',
    updated_at: '2024-01-01T00:00:00',
  };

  beforeEach(() => {
    vi.clearAllMocks();
    // Clear localStorage between tests
    localStorage.clear();
    // Set up default mock for getProfile to return the mock user
    (authService.getProfile as any).mockResolvedValue(mockUser);
  });

  const TestComponent = () => <div>Protected Content</div>;

  const renderWithRouter = () => {
    return renderWithProvider(
      <MemoryRouter initialEntries={['/protected']}>
        <Routes>
          <Route element={<ProtectedRoute />}>
            <Route path="/protected" element={<TestComponent />} />
          </Route>
          <Route path="/login" element={<div>Login Page</div>} />
        </Routes>
      </MemoryRouter>
    );
  };

  it('renders protected content when authenticated', async () => {
    renderWithRouter();

    // Wait for AuthProvider to initialize and set isLoading to false
    await waitFor(() => {
      expect(screen.getByText('Protected Content')).toBeInTheDocument();
    });
  });

  it('redirects to login when not authenticated', async () => {
    // Mock getProfile to throw error (no token, not authenticated)
    (authService.getProfile as any).mockRejectedValueOnce(new Error('Not authenticated'));
    
    // Don't set tokens - AuthProvider will find no token and not call getProfile
    // Actually, we need to ensure tokens are NOT set
    localStorage.clear();
    
    renderWithRouter();

    // Wait for AuthProvider to initialize
    await waitFor(() => {
      expect(screen.getByText('Login Page')).toBeInTheDocument();
      expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
    });
  });

  it('redirects to login when user is null', async () => {
    // Mock getProfile to return null/throw error
    (authService.getProfile as any).mockRejectedValueOnce(new Error('Not authenticated'));
    
    renderWithRouter();

    // Wait for AuthProvider to initialize
    await waitFor(() => {
      expect(screen.getByText('Login Page')).toBeInTheDocument();
      expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
    });
  });

  it('redirects to login when authenticated but user data not loaded', async () => {
    // Mock getProfile to return null/throw error
    (authService.getProfile as any).mockRejectedValueOnce(new Error('Not authenticated'));
    
    renderWithRouter();

    // Wait for AuthProvider to initialize
    await waitFor(() => {
      expect(screen.getByText('Login Page')).toBeInTheDocument();
      expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
    });
  });
});

