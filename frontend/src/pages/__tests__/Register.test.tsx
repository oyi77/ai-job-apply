import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
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
     const user = userEvent.setup({ delay: null });
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

     const nameInput = screen.getByLabelText(/full name/i) as HTMLInputElement;
     const emailInput = screen.getByLabelText(/email address/i) as HTMLInputElement;
     const passwordInput = screen.getByLabelText(/^password/i) as HTMLInputElement;
     const confirmPasswordInput = screen.getByLabelText(/confirm password/i) as HTMLInputElement;
     const submitButton = screen.getByRole('button', { name: /create account/i });

     await user.type(nameInput, 'New User');
     await user.type(emailInput, 'newuser@example.com');
     await user.type(passwordInput, 'Password123');
     await user.type(confirmPasswordInput, 'Password123');
     await user.click(submitButton);

     await waitFor(() => {
       expect(authService.register).toHaveBeenCalledWith({
         email: 'newuser@example.com',
         password: 'Password123',
         name: 'New User',
       });
     }, { timeout: 5000 });

     await waitFor(() => {
       expect(authService.getProfile).toHaveBeenCalled();
     }, { timeout: 5000 });

     await waitFor(() => {
       expect(mockSetUser).toHaveBeenCalled();
       expect(mockSetAuthenticated).toHaveBeenCalledWith(true);
       expect(mockNavigate).toHaveBeenCalled();
     }, { timeout: 5000 });
   });

   it('validates password match', async () => {
     const user = userEvent.setup({ delay: null });
     renderRegister();

     const emailInput = screen.getByLabelText(/email address/i) as HTMLInputElement;
     const passwordInput = screen.getByLabelText(/^password/i) as HTMLInputElement;
     const confirmPasswordInput = screen.getByLabelText(/confirm password/i) as HTMLInputElement;
     const submitButton = screen.getByRole('button', { name: /create account/i });

     await user.type(emailInput, 'test@example.com');
     await user.type(passwordInput, 'Password123');
     await user.type(confirmPasswordInput, 'DifferentPassword123');
     await user.click(submitButton);

     // Wait for the error message to appear
     await waitFor(() => {
       expect(screen.getByText('Passwords do not match')).toBeInTheDocument();
     }, { timeout: 3000 });

     expect(authService.register).not.toHaveBeenCalled();
   });

   it('validates password length', async () => {
     const user = userEvent.setup({ delay: null });
     renderRegister();

     const emailInput = screen.getByLabelText(/email address/i) as HTMLInputElement;
     const passwordInput = screen.getByLabelText(/^password/i) as HTMLInputElement;
     const confirmPasswordInput = screen.getByLabelText(/confirm password/i) as HTMLInputElement;
     const submitButton = screen.getByRole('button', { name: /create account/i });

     await user.type(emailInput, 'test@example.com');
     await user.type(passwordInput, 'Short1');
     await user.type(confirmPasswordInput, 'Short1');
     await user.click(submitButton);

     // Wait for the error message to appear
     await waitFor(() => {
       expect(screen.getByText('Password must be at least 8 characters long')).toBeInTheDocument();
     }, { timeout: 3000 });

     expect(authService.register).not.toHaveBeenCalled();
   });

   it('displays error message on registration failure', async () => {
     const user = userEvent.setup({ delay: null });
     const errorMessage = 'Email already registered';
     (authService.register as any).mockRejectedValue({
       response: {
         data: {
           detail: errorMessage,
         },
       },
     });

     renderRegister();

     const emailInput = screen.getByLabelText(/email address/i) as HTMLInputElement;
     const passwordInput = screen.getByLabelText(/^password/i) as HTMLInputElement;
     const confirmPasswordInput = screen.getByLabelText(/confirm password/i) as HTMLInputElement;
     const submitButton = screen.getByRole('button', { name: /create account/i });

     await user.type(emailInput, 'existing@example.com');
     await user.type(passwordInput, 'Password123');
     await user.type(confirmPasswordInput, 'Password123');
     await user.click(submitButton);

     expect(await screen.findByText(errorMessage)).toBeInTheDocument();
   });

   it('clears field errors when user starts typing', async () => {
     const user = userEvent.setup({ delay: null });
     renderRegister();

     const emailInput = screen.getByLabelText(/email address/i) as HTMLInputElement;
     const passwordInput = screen.getByLabelText(/^password/i) as HTMLInputElement;
     const confirmPasswordInput = screen.getByLabelText(/confirm password/i) as HTMLInputElement;
     const submitButton = screen.getByRole('button', { name: /create account/i });

     // Trigger validation error
     await user.type(emailInput, 'test@example.com');
     await user.type(passwordInput, 'Password123');
     await user.type(confirmPasswordInput, 'DifferentPassword123');
     await user.click(submitButton);

     // Wait for error to appear
     await waitFor(() => {
       expect(screen.getByText('Passwords do not match')).toBeInTheDocument();
     }, { timeout: 3000 });

     // Fix the password - error should clear
     await user.clear(confirmPasswordInput);
     await user.type(confirmPasswordInput, 'Password123');

     await waitFor(() => {
       expect(screen.queryByText('Passwords do not match')).not.toBeInTheDocument();
     }, { timeout: 3000 });
   });
});
