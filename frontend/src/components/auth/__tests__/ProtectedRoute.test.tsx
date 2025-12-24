import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import ProtectedRoute from '../ProtectedRoute';
import { useAppStore } from '../../../stores/appStore';

// Mock the store
vi.mock('../../../stores/appStore');

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
    },
    created_at: '2024-01-01T00:00:00',
    updated_at: '2024-01-01T00:00:00',
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  const TestComponent = () => <div>Protected Content</div>;

  const renderWithRouter = (isAuthenticated: boolean, user: typeof mockUser | null) => {
    (useAppStore as any).mockReturnValue({
      isAuthenticated,
      user,
    });

    return render(
      <BrowserRouter>
        <Routes>
          <Route element={<ProtectedRoute />}>
            <Route path="/protected" element={<TestComponent />} />
          </Route>
          <Route path="/login" element={<div>Login Page</div>} />
        </Routes>
      </BrowserRouter>
    );
  };

  it('renders protected content when authenticated', () => {
    renderWithRouter(true, mockUser);
    
    expect(screen.getByText('Protected Content')).toBeInTheDocument();
  });

  it('redirects to login when not authenticated', () => {
    renderWithRouter(false, null);
    
    expect(screen.getByText('Login Page')).toBeInTheDocument();
    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
  });

  it('redirects to login when user is null', () => {
    renderWithRouter(true, null);
    
    expect(screen.getByText('Login Page')).toBeInTheDocument();
    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
  });

  it('redirects to login when authenticated but user data not loaded', () => {
    renderWithRouter(true, null);
    
    expect(screen.getByText('Login Page')).toBeInTheDocument();
    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
  });
});

