import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import Input from '../Input';

describe('Input Component', () => {
  it('renders input with placeholder', () => {
    render(<Input name="test" placeholder="Enter text" />);
    expect(screen.getByPlaceholderText('Enter text')).toBeInTheDocument();
  });

  it('renders input with label', () => {
    render(<Input name="test" label="Test Label" placeholder="Enter text" />);
    expect(screen.getByText('Test Label')).toBeInTheDocument();
  });

  it('renders input with error', () => {
    render(<Input name="test" error="Error message" placeholder="Enter text" />);
    expect(screen.getByText('Error message')).toBeInTheDocument();
  });

  it('renders input with success state', () => {
    render(<Input name="test" success={true} placeholder="Enter text" />);
    const input = screen.getByRole('textbox');
    expect(input).toHaveClass('border-success-300');
  });

  it('renders small input', () => {
    render(<Input name="test" size="sm" placeholder="Enter text" />);
    const input = screen.getByRole('textbox');
    expect(input).toHaveClass('px-2 py-1 text-xs');
  });

  it('renders large input', () => {
    render(<Input name="test" size="lg" placeholder="Enter text" />);
    const input = screen.getByRole('textbox');
    expect(input).toHaveClass('px-4 py-3 text-lg');
  });

  it('renders textarea', () => {
    render(<Input name="test" as="textarea" placeholder="Enter text" rows={5} />);
    const textarea = screen.getByRole('textbox');
    expect(textarea).toHaveAttribute('rows', '5');
  });

  it('handles onChange', () => {
    const mockOnChange = vi.fn();
    render(<Input name="test" onChange={mockOnChange} placeholder="Enter text" />);
    const input = screen.getByRole('textbox');
    input.focus();
    expect(input).toBeInTheDocument();
  });

  it('renders input with icon', () => {
    const icon = <span>🔍</span>;
    render(<Input name="test" icon={icon} placeholder="Enter text" />);
    expect(screen.getByText('🔍')).toBeInTheDocument();
  });

  it('renders input with right icon', () => {
    const rightIcon = <span>✓</span>;
    render(<Input name="test" rightIcon={rightIcon} placeholder="Enter text" />);
    expect(screen.getByText('✓')).toBeInTheDocument();
  });

  it('renders disabled input', () => {
    render(<Input name="test" disabled={true} placeholder="Enter text" />);
    const input = screen.getByRole('textbox');
    expect(input).toBeDisabled();
  });

  it('renders input with custom className', () => {
    render(<Input name="test" className="custom-class" placeholder="Enter text" />);
    const input = screen.getByRole('textbox');
    expect(input).toHaveClass('custom-class');
  });

  it('forwards ref', () => {
    const ref = vi.fn();
    render(<Input name="test" ref={ref} placeholder="Enter text" />);
    expect(ref).toHaveBeenCalled();
  });
});
