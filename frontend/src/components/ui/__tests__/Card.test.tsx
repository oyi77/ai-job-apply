import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { Card, CardHeader, CardBody } from '../Card';

describe('Card', () => {
  it('renders Card with children', () => {
    render(<Card>Card content</Card>);
    expect(screen.getByText('Card content')).toBeInTheDocument();
  });

  it('renders Card with custom className', () => {
    render(<Card className="custom-card">Content</Card>);
    const card = screen.getByText('Content').closest('div');
    expect(card).toHaveClass('custom-card');
  });

  it('renders CardHeader with title and description', () => {
    render(
      <CardHeader title="Card Title" description="Card description">
        Header content
      </CardHeader>
    );
    
    expect(screen.getByText('Card Title')).toBeInTheDocument();
    expect(screen.getByText('Card description')).toBeInTheDocument();
    expect(screen.getByText('Header content')).toBeInTheDocument();
  });

  it('renders CardHeader with custom className', () => {
    render(
      <CardHeader title="Title" className="custom-header">
        Content
      </CardHeader>
    );
    
    const header = screen.getByText('Title').closest('div');
    expect(header).toHaveClass('custom-header');
  });

  it('renders CardBody with children', () => {
    render(<CardBody>Body content</CardBody>);
    expect(screen.getByText('Body content')).toBeInTheDocument();
  });

  it('renders CardBody with custom className', () => {
    render(<CardBody className="custom-body">Content</CardBody>);
    const body = screen.getByText('Content').closest('div');
    expect(body).toHaveClass('custom-body');
  });

  it('renders complete Card structure', () => {
    render(
      <Card>
        <CardHeader title="Test Card" description="A test card">
          <button>Action</button>
        </CardHeader>
        <CardBody>
          <p>Card body content</p>
        </CardBody>
      </Card>
    );
    
    expect(screen.getByText('Test Card')).toBeInTheDocument();
    expect(screen.getByText('A test card')).toBeInTheDocument();
    expect(screen.getByText('Action')).toBeInTheDocument();
    expect(screen.getByText('Card body content')).toBeInTheDocument();
  });
});
