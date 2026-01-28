import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Login from '../Login';
import { useAppStore } from '../../stores/appStore';
import { authService } from '../../services/api';
import { renderWithProvider } from '../../test-utils/renderWithProvider';

// Mock the dependencies
vi.mock('../../services/api');
vi.mock('../../stores/appStore');
vi.mock('../../components/ui/Notification', () => ({
  useNotifications: () => ({
    showError: vi.fn(),
    showSuccess: vi.fn(),
  }),
}));

const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

describe('Login', () => {
  const mockSetUser = vi.fn();
  const mockSetAuthenticated = vi.fn();
  const mockSetLoading = vi.fn();
  const mockSetError = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    // Mock useAppStore to handle selector functions
    (useAppStore as any).mockImplementation((selector: any) => {
      const store = {
        // AuthProvider extracts these from the store
        setUser: mockSetUser,
        setAuthenticated: mockSetAuthenticated,
        // Login page uses these
        setLoading: mockSetLoading,
        setError: mockSetError,
      };
      // If a selector function is provided, call it with the store
      if (typeof selector === 'function') {
        return selector(store);
      }
      // Otherwise return the whole store
      return store;
    });
  });

  const renderLogin = () => {
    return renderWithProvider(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    );
  };

  it('renders login form', () => {
    renderLogin();

    expect(screen.getByText('Sign in to your account')).toBeInTheDocument();
    expect(screen.getByLabelText(/email address/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
  });

  it('shows link to register page', () => {
    renderLogin();

    const registerLink = screen.getByRole('link', { name: /sign up/i });
    expect(registerLink).toBeInTheDocument();
    expect(registerLink).toHaveAttribute('href', '/register');
  });

  it('handles form submission with valid credentials', async () => {
    const mockTokens = {
      access_token: 'test-access-token',
      refresh_token: 'test-refresh-token',
      token_type: 'bearer',
      expires_in: 1800,
    };

    const mockProfile = {
      id: 'test-user-id',
      email: 'test@example.com',
      name: 'Test User',
      is_active: true,
      created_at: '2024-01-01T00:00:00',
      updated_at: '2024-01-01T00:00:00',
    };

    (authService.login as any).mockResolvedValue(mockTokens);
    (authService.getProfile as any).mockResolvedValue(mockProfile);

    renderLogin();

    const emailInput = screen.getByLabelText(/email address/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /sign in/i });

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(authService.login).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password123',
      });
    });

    await waitFor(() => {
      expect(authService.getProfile).toHaveBeenCalled();
    });

    await waitFor(() => {
      expect(mockSetUser).toHaveBeenCalled();
      expect(mockSetAuthenticated).toHaveBeenCalledWith(true);
      expect(mockNavigate).toHaveBeenCalled();
    });
  });

  it('displays error message on login failure', async () => {
    const errorMessage = 'Invalid email or password';
    (authService.login as any).mockRejectedValue({
      response: {
        data: {
          detail: errorMessage,
        },
      },
    });

    renderLogin();

    const emailInput = screen.getByLabelText(/email address/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /sign in/i });

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'wrongpassword' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(errorMessage)).toBeInTheDocument();
    });
  });

  it('validates required fields', async () => {
    renderLogin();

    const submitButton = screen.getByRole('button', { name: /sign in/i });
    fireEvent.click(submitButton);

    // HTML5 validation should prevent submission
    await waitFor(() => {
      expect(authService.login).not.toHaveBeenCalled();
    });
  });

  it('shows loading state during submission', async () => {
    (authService.login as any).mockImplementation(
      () => new Promise((resolve) => setTimeout(resolve, 100))
    );

    renderLogin();

    const emailInput = screen.getByLabelText(/email address/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /sign in/i });

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(submitButton);

    // Button should be disabled during loading
    expect(submitButton).toBeDisabled();
  });
});

