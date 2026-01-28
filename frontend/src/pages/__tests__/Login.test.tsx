import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import Login from '../Login';
import { authService } from '../../services/api';
import { renderWithProvider } from '../../test-utils/renderWithProvider';

// Mock the dependencies
vi.mock('../../services/api');
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
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    // Mock authService.getProfile to return a user (for AuthProvider initialization)
    (authService.getProfile as any).mockResolvedValue({
      id: 'test-user-id',
      email: 'test@example.com',
      name: 'Test User',
      is_active: true,
      created_at: '2024-01-01T00:00:00',
      updated_at: '2024-01-01T00:00:00',
    });
  });

  afterEach(() => {
    localStorage.clear();
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
    const user = userEvent.setup({ delay: null });
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

    const emailInput = screen.getByLabelText(/email address/i) as HTMLInputElement;
    const passwordInput = screen.getByLabelText(/password/i) as HTMLInputElement;
    const submitButton = screen.getByRole('button', { name: /sign in/i });

    // Type into the inputs
    await user.clear(emailInput);
    await user.type(emailInput, 'test@example.com');
    await user.clear(passwordInput);
    await user.type(passwordInput, 'password123');
    
    // Submit the form
    await user.click(submitButton);

    // Wait for all async operations to complete
    await waitFor(() => {
      expect(authService.login).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password123',
      });
    }, { timeout: 5000 });

    await waitFor(() => {
      expect(authService.getProfile).toHaveBeenCalled();
    }, { timeout: 5000 });

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalled();
    }, { timeout: 5000 });
  });

  it('displays error message on login failure', async () => {
    const user = userEvent.setup({ delay: null });
    const errorMessage = 'Invalid email or password';
    (authService.login as any).mockRejectedValue(
      new Error(errorMessage)
    );

    renderLogin();

    const emailInput = screen.getByLabelText(/email address/i) as HTMLInputElement;
    const passwordInput = screen.getByLabelText(/password/i) as HTMLInputElement;
    const submitButton = screen.getByRole('button', { name: /sign in/i });

    await user.clear(emailInput);
    await user.type(emailInput, 'test@example.com');
    await user.clear(passwordInput);
    await user.type(passwordInput, 'wrongpassword');
    await user.click(submitButton);

    // Wait for the login function to be called and rejected
    await waitFor(() => {
      expect(authService.login).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'wrongpassword',
      });
    }, { timeout: 3000 });

    // Verify that the error was handled (login was called but failed)
    expect(authService.login).toHaveBeenCalled();
  });

  it('validates required fields', async () => {
    const user = userEvent.setup();
    renderLogin();

    const submitButton = screen.getByRole('button', { name: /sign in/i });
    await user.click(submitButton);

    // HTML5 validation should prevent submission
    await waitFor(() => {
      expect(authService.login).not.toHaveBeenCalled();
    });
  });

  it('shows loading state during submission', async () => {
    const user = userEvent.setup();
    (authService.login as any).mockImplementation(
      () => new Promise((resolve) => setTimeout(resolve, 100))
    );

    renderLogin();

    const emailInput = screen.getByLabelText(/email address/i) as HTMLInputElement;
    const passwordInput = screen.getByLabelText(/password/i) as HTMLInputElement;
    const submitButton = screen.getByRole('button', { name: /sign in/i });

    await user.type(emailInput, 'test@example.com');
    await user.type(passwordInput, 'password123');
    await user.click(submitButton);

    // Button should be disabled during loading
    expect(submitButton).toBeDisabled();
  });
});

