import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Register from '../Register';
import { useAppStore } from '../../stores/appStore';
import { authService } from '../../services/api';

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

describe('Register', () => {
  const mockSetUser = vi.fn();
  const mockSetAuthenticated = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    (useAppStore as any).mockReturnValue({
      setUser: mockSetUser,
      setAuthenticated: mockSetAuthenticated,
    });
  });

  const renderRegister = () => {
    return render(
      <BrowserRouter>
        <Register />
      </BrowserRouter>
    );
  };

  it('renders registration form', () => {
    renderRegister();

    expect(screen.getByText('Create your account')).toBeInTheDocument();
    expect(screen.getByLabelText(/full name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/email address/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^password/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/confirm password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /create account/i })).toBeInTheDocument();
  });

  it('shows link to login page', () => {
    renderRegister();

    const loginLink = screen.getByRole('link', { name: /sign in/i });
    expect(loginLink).toBeInTheDocument();
    expect(loginLink).toHaveAttribute('href', '/login');
  });

  it('handles form submission with valid data', async () => {
    const mockTokens = {
      access_token: 'test-access-token',
      refresh_token: 'test-refresh-token',
      token_type: 'bearer',
      expires_in: 1800,
    };

    const mockProfile = {
      id: 'test-user-id',
      email: 'newuser@example.com',
      name: 'New User',
      is_active: true,
      created_at: '2024-01-01T00:00:00',
      updated_at: '2024-01-01T00:00:00',
    };

    (authService.register as any).mockResolvedValue(mockTokens);
    (authService.getProfile as any).mockResolvedValue(mockProfile);

    renderRegister();

    const nameInput = screen.getByLabelText(/full name/i);
    const emailInput = screen.getByLabelText(/email address/i);
    const passwordInput = screen.getByLabelText(/^password/i);
    const confirmPasswordInput = screen.getByLabelText(/confirm password/i);
    const submitButton = screen.getByRole('button', { name: /create account/i });

    fireEvent.change(nameInput, { target: { value: 'New User' } });
    fireEvent.change(emailInput, { target: { value: 'newuser@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'Password123' } });
    fireEvent.change(confirmPasswordInput, { target: { value: 'Password123' } });
    fireEvent.submit(screen.getByRole('form'));

    await waitFor(() => {
      expect(authService.register).toHaveBeenCalledWith({
        email: 'newuser@example.com',
        password: 'Password123',
        name: 'New User',
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

  it('validates password match', async () => {
    renderRegister();

    const passwordInput = screen.getByLabelText(/^password/i);
    const confirmPasswordInput = screen.getByLabelText(/confirm password/i);
    const submitButton = screen.getByRole('button', { name: /create account/i });

    fireEvent.change(passwordInput, { target: { value: 'Password123' } });
    fireEvent.change(confirmPasswordInput, { target: { value: 'DifferentPassword123' } });
    fireEvent.submit(screen.getByRole('form'));

    expect(await screen.findByText(/passwords do not match/i)).toBeInTheDocument();

    expect(authService.register).not.toHaveBeenCalled();
  });

  it('validates password length', async () => {
    renderRegister();

    const passwordInput = screen.getByLabelText(/^password/i);
    const confirmPasswordInput = screen.getByLabelText(/confirm password/i);
    const submitButton = screen.getByRole('button', { name: /create account/i });

    fireEvent.change(passwordInput, { target: { value: 'Short1' } });
    fireEvent.change(confirmPasswordInput, { target: { value: 'Short1' } });
    fireEvent.submit(screen.getByRole('form'));

    expect(await screen.findByText(/password must be at least 8 characters/i)).toBeInTheDocument();

    expect(authService.register).not.toHaveBeenCalled();
  });

  it('displays error message on registration failure', async () => {
    const errorMessage = 'Email already registered';
    (authService.register as any).mockRejectedValue({
      response: {
        data: {
          detail: errorMessage,
        },
      },
    });

    renderRegister();

    const emailInput = screen.getByLabelText(/email address/i);
    const passwordInput = screen.getByLabelText(/^password/i);
    const confirmPasswordInput = screen.getByLabelText(/confirm password/i);
    const submitButton = screen.getByRole('button', { name: /create account/i });

    fireEvent.change(emailInput, { target: { value: 'existing@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'Password123' } });
    fireEvent.change(confirmPasswordInput, { target: { value: 'Password123' } });
    fireEvent.submit(screen.getByRole('form'));

    expect(await screen.findByText(errorMessage)).toBeInTheDocument();
  });

  it('clears field errors when user starts typing', async () => {
    renderRegister();

    const passwordInput = screen.getByLabelText(/^password/i);
    const confirmPasswordInput = screen.getByLabelText(/confirm password/i);
    const submitButton = screen.getByRole('button', { name: /create account/i });

    // Trigger validation error
    fireEvent.change(passwordInput, { target: { value: 'Password123' } });
    fireEvent.change(confirmPasswordInput, { target: { value: 'DifferentPassword123' } });
    fireEvent.submit(screen.getByRole('form'));

    expect(await screen.findByText(/passwords do not match/i)).toBeInTheDocument();

    // Fix the password - error should clear
    fireEvent.change(confirmPasswordInput, { target: { value: 'Password123' } });

    await waitFor(() => {
      expect(screen.queryByText(/passwords do not match/i)).not.toBeInTheDocument();
    });
  });
});
