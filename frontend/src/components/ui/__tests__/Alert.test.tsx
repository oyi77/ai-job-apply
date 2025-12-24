import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import Alert from '../Alert';

describe('Alert', () => {
  it('renders alert with message', () => {
    render(<Alert message="Test alert message" />);
    expect(screen.getByText('Test alert message')).toBeInTheDocument();
    expect(screen.getByRole('alert')).toBeInTheDocument();
  });

  it('renders alert with title', () => {
    render(<Alert title="Alert Title" message="Alert message" />);
    expect(screen.getByText('Alert Title')).toBeInTheDocument();
    expect(screen.getByText('Alert message')).toBeInTheDocument();
  });

  it('renders success alert', () => {
    render(<Alert type="success" message="Success message" />);
    const alert = screen.getByRole('alert');
    expect(alert).toHaveClass('bg-success-50', 'border-success-200');
  });

  it('renders warning alert', () => {
    render(<Alert type="warning" message="Warning message" />);
    const alert = screen.getByRole('alert');
    expect(alert).toHaveClass('bg-warning-50', 'border-warning-200');
  });

  it('renders error alert', () => {
    render(<Alert type="error" message="Error message" />);
    const alert = screen.getByRole('alert');
    expect(alert).toHaveClass('bg-danger-50', 'border-danger-200');
  });

  it('renders info alert', () => {
    render(<Alert type="info" message="Info message" />);
    const alert = screen.getByRole('alert');
    expect(alert).toHaveClass('bg-primary-50', 'border-primary-200');
  });

  it('shows dismiss button when dismissible', () => {
    const onDismiss = vi.fn();
    render(<Alert message="Dismissible alert" dismissible onDismiss={onDismiss} />);
    const dismissButton = screen.getByRole('button', { name: /dismiss/i });
    expect(dismissButton).toBeInTheDocument();
  });

  it('calls onDismiss when dismiss button clicked', () => {
    const onDismiss = vi.fn();
    render(<Alert message="Dismissible alert" dismissible onDismiss={onDismiss} />);
    const dismissButton = screen.getByRole('button', { name: /dismiss/i });
    fireEvent.click(dismissButton);
    expect(onDismiss).toHaveBeenCalledTimes(1);
  });

  it('does not show dismiss button when not dismissible', () => {
    render(<Alert message="Non-dismissible alert" />);
    expect(screen.queryByRole('button')).not.toBeInTheDocument();
  });

  it('applies custom className', () => {
    render(<Alert message="Custom alert" className="custom-class" />);
    const alert = screen.getByRole('alert');
    expect(alert).toHaveClass('custom-class');
  });
});

