import { screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { PasswordReset } from '../PasswordReset';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { renderWithProvider } from '../../test-utils/renderWithProvider';
import { useAppStore } from '../../stores/appStore';

// Mock dependencies
vi.mock('../../stores/appStore');
vi.mock('react-router-dom', async () => {
    const actual = await vi.importActual('react-router-dom');
    return {
        ...actual,
        useSearchParams: () => [new URLSearchParams({ token: 'valid-token' })],
        useNavigate: () => vi.fn(),
    };
});

// Create a mock fetch function
const mockFetch = vi.fn();
global.fetch = mockFetch as any;

const renderComponent = () => {
    renderWithProvider(
        <BrowserRouter>
            <PasswordReset />
        </BrowserRouter>
    );
};

describe('PasswordReset', () => {
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

     it('renders password inputs and submit button', () => {
         renderComponent();
         const inputs = screen.getAllByDisplayValue('');
         expect(inputs.length).toBe(2);
         expect(screen.getByRole('button', { name: /reset password/i })).toBeInTheDocument();
     });

     it('validates password mismatch', async () => {
         renderComponent();

         const inputs = screen.getAllByDisplayValue('');
         fireEvent.change(inputs[0], { target: { value: 'Password123' } });
         fireEvent.change(inputs[1], { target: { value: 'DifferentPassword' } });
         fireEvent.click(screen.getByRole('button', { name: /reset password/i }));

         expect(await screen.findByText(/passwords do not match/i)).toBeInTheDocument();
     });

     it('handles successful reset', async () => {
         mockFetch.mockResolvedValueOnce({
             ok: true,
             json: async () => ({ message: 'Password reset' }),
         } as Response);

         renderComponent();

         const inputs = screen.getAllByDisplayValue('');
         fireEvent.change(inputs[0], { target: { value: 'Password123' } });
         fireEvent.change(inputs[1], { target: { value: 'Password123' } });
         fireEvent.click(screen.getByRole('button', { name: /reset password/i }));

         await waitFor(() => {
             expect(screen.getByText(/password reset successful/i)).toBeInTheDocument();
         });
     });
});
