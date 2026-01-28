import { screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { PasswordResetRequest } from '../PasswordResetRequest';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { renderWithProvider } from '../../test-utils/renderWithProvider';
import { useAppStore } from '../../stores/appStore';

// Mock dependencies
vi.mock('../../stores/appStore');

// Create a mock fetch function
const mockFetch = vi.fn();
global.fetch = mockFetch as any;

const renderComponent = () => {
     renderWithProvider(
         <BrowserRouter>
             <PasswordResetRequest />
         </BrowserRouter>
     );
 };

 describe('PasswordResetRequest', () => {
     beforeEach(() => {
         vi.clearAllMocks();
         mockFetch.mockClear();
         // Mock useAppStore for AuthProvider
         (useAppStore as any).mockImplementation((selector: any) => {
             const store = {
                 setUser: vi.fn(),
                 setAuthenticated: vi.fn(),
             };
             if (typeof selector === 'function') {
                 return selector(store);
             }
             return store;
         });
     });

     it('renders email input and submit button', () => {
         renderComponent();
         expect(screen.getByPlaceholderText(/name@example.com/i)).toBeInTheDocument();
         expect(screen.getByRole('button', { name: /send reset link/i })).toBeInTheDocument();
     });

     it('handles successful submission', async () => {
         mockFetch.mockResolvedValueOnce({
             ok: true,
             json: async () => ({ message: 'Email sent' }),
         } as Response);

         renderComponent();

         fireEvent.change(screen.getByPlaceholderText(/name@example.com/i), { target: { value: 'test@example.com' } });
         fireEvent.click(screen.getByRole('button', { name: /send reset link/i }));

         await waitFor(() => {
             expect(screen.getByText(/check your email/i)).toBeInTheDocument();
         });
     });

     it('handles API error', async () => {
         mockFetch.mockResolvedValueOnce({
             ok: false,
         } as Response);

         renderComponent();

         fireEvent.change(screen.getByPlaceholderText(/name@example.com/i), { target: { value: 'test@example.com' } });
         fireEvent.click(screen.getByRole('button', { name: /send reset link/i }));

         await waitFor(() => {
             expect(screen.getByText(/an error occurred/i)).toBeInTheDocument();
         });
     });
});
