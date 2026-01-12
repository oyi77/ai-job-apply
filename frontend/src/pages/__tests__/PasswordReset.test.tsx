import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { PasswordReset } from '../PasswordReset';
import { vi } from 'vitest';

// Mock router hooks
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
    render(
        <BrowserRouter>
            <PasswordReset />
        </BrowserRouter>
    );
};

describe('PasswordReset', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    test('renders password inputs and submit button', () => {
        renderComponent();
        expect(screen.getByLabelText(/^new password$/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/confirm password/i)).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /reset password/i })).toBeInTheDocument();
    });

    test('validates password mismatch', async () => {
        renderComponent();

        fireEvent.change(screen.getByLabelText(/^new password$/i), { target: { value: 'Password123' } });
        fireEvent.change(screen.getByLabelText(/confirm password/i), { target: { value: 'DifferentPassword' } });
        fireEvent.click(screen.getByRole('button', { name: /reset password/i }));

        expect(await screen.findByText(/passwords do not match/i)).toBeInTheDocument();
    });

    test('handles successful reset', async () => {
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
