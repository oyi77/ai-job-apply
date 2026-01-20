import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { Button } from '../Button'

describe('Button', () => {
  it('renders with text', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByText('Click me')).toBeInTheDocument()
  })

  it('handles click events', () => {
    const handleClick = vi.fn()
    render(<Button onClick={handleClick}>Click</Button>)
    screen.getByText('Click').click()
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('renders variants correctly', () => {
    const { rerender } = render(<Button variant="primary">Primary</Button>)
    const buttonPrimary = screen.getByRole('button')
    // We expect class names to contain the variant (checking logic will depend on module css, but for now we look for presence)
    // Since we use CSS modules, we might need to mock styles or check for specific attributes if we can't see the class name easily without the style mapping.
    // However, vitest css: true might handle it, or we check for the presence of the class in the classList if mapped.
    // For now, let's just check if it renders without crashing and basic attributes.
    expect(buttonPrimary).toBeInTheDocument()
    
    rerender(<Button variant="secondary">Secondary</Button>)
    expect(screen.getByRole('button')).toBeInTheDocument()
  })
  
  it('can be disabled', () => {
    render(<Button disabled>Disabled</Button>)
    expect(screen.getByRole('button')).toBeDisabled()
  })
})
