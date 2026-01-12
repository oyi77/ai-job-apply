import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { PasswordResetRequest } from '../PasswordResetRequest';
import { vi } from 'vitest';

// Mock fetch
global.fetch = vi.fn();

const renderComponent = () => {
    render(
        <BrowserRouter>
            <PasswordResetRequest />
        </BrowserRouter>
    );
};

describe('PasswordResetRequest', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    test('renders email input and submit button', () => {
        renderComponent();
        expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /send reset link/i })).toBeInTheDocument();
    });

    test('handles successful submission', async () => {
        (global.fetch as any).mockResolvedValueOnce({
            ok: true,
            json: async () => ({ message: 'Email sent' }),
        });

        renderComponent();

        fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'test@example.com' } });
        fireEvent.click(screen.getByRole('button', { name: /send reset link/i }));

        await waitFor(() => {
            expect(screen.getByText(/check your email/i)).toBeInTheDocument();
        });
    });

    test('handles API error', async () => {
        (global.fetch as any).mockResolvedValueOnce({
            ok: false,
        });

        renderComponent();

        fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'test@example.com' } });
        fireEvent.click(screen.getByRole('button', { name: /send reset link/i }));

        await waitFor(() => {
            expect(screen.getByText(/an error occurred/i)).toBeInTheDocument();
        });
    });
});
