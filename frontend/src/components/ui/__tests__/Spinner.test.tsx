import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import Spinner from '../Spinner';

describe('Spinner', () => {
  it('renders spinner with default props', () => {
    render(<Spinner />);
    const spinner = screen.getByRole('status');
    expect(spinner).toBeInTheDocument();
    expect(spinner).toHaveAttribute('aria-label', 'Loading');
  });

  it('renders small spinner', () => {
    render(<Spinner size="sm" />);
    const spinner = screen.getByRole('status');
    expect(spinner.querySelector('svg')).toHaveClass('h-4', 'w-4');
  });

  it('renders large spinner', () => {
    render(<Spinner size="lg" />);
    const spinner = screen.getByRole('status');
    expect(spinner.querySelector('svg')).toHaveClass('h-8', 'w-8');
  });

  it('renders with primary color', () => {
    render(<Spinner color="primary" />);
    const spinner = screen.getByRole('status');
    expect(spinner.querySelector('svg')).toHaveClass('text-primary-600');
  });

  it('renders with white color', () => {
    render(<Spinner color="white" />);
    const spinner = screen.getByRole('status');
    expect(spinner.querySelector('svg')).toHaveClass('text-white');
  });

  it('applies custom className', () => {
    render(<Spinner className="custom-class" />);
    const spinner = screen.getByRole('status');
    expect(spinner).toHaveClass('custom-class');
  });
});

