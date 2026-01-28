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

// Mock fetch
global.fetch = vi.fn();

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
        expect(screen.getByLabelText(/^new password$/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/confirm password/i)).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /reset password/i })).toBeInTheDocument();
    });

    it('validates password mismatch', async () => {
        renderComponent();

        fireEvent.change(screen.getByLabelText(/^new password$/i), { target: { value: 'Password123' } });
        fireEvent.change(screen.getByLabelText(/confirm password/i), { target: { value: 'DifferentPassword' } });
        fireEvent.click(screen.getByRole('button', { name: /reset password/i }));

        expect(await screen.findByText(/passwords do not match/i)).toBeInTheDocument();
    });

    it('handles successful reset', async () => {
        (global.fetch as any).mockResolvedValueOnce({
            ok: true,
            json: async () => ({ message: 'Password reset' }),
        });

        renderComponent();

        fireEvent.change(screen.getByLabelText(/^new password$/i), { target: { value: 'Password123' } });
        fireEvent.change(screen.getByLabelText(/confirm password/i), { target: { value: 'Password123' } });
        fireEvent.click(screen.getByRole('button', { name: /reset password/i }));

        await waitFor(() => {
            expect(screen.getByText(/password reset successful/i)).toBeInTheDocument();
        });
    });
});
