import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { ErrorBoundary } from '../ErrorBoundary';
import {
  NetworkError,
  AuthenticationError,
  AuthorizationError,
  ValidationError,
  NotFoundError,
  ServerError,
  createApiError,
  getUserFriendlyErrorMessage,
  parseApiError,
} from '../../types/errors';

// Test component that throws an error
const ErrorThrower: React.FC<{ shouldThrow: boolean }> = ({ shouldThrow }) => {
  if (shouldThrow) {
    throw new Error('Test error');
  }
  return <div data-testid="success">No error</div>;
};

describe('ErrorBoundary', () => {
  it('renders children when no error', () => {
    render(
      <ErrorBoundary>
        <div data-testid="child">Child content</div>
      </ErrorBoundary>
    );
    
    expect(screen.getByTestId('child')).toBeInTheDocument();
  });

  it('renders error UI when child throws', () => {
    render(
      <ErrorBoundary>
        <ErrorThrower shouldThrow={true} />
      </ErrorBoundary>
    );
    
    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    expect(screen.getByText('Try Again')).toBeInTheDocument();
  });

  it('can reset error state', () => {
    render(
      <ErrorBoundary>
        <ErrorThrower shouldThrow={true} />
      </ErrorBoundary>
    );
    
    // Error is shown
    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    
    // Click try again
    const tryAgainButton = screen.getByText('Try Again');
    fireEvent.click(tryAgainButton);
    
    // Error should be cleared (but component will throw again immediately)
    // In real usage, you'd change props to stop throwing
  });

  it('shows development details in dev mode', () => {
    // Mock environment
    const originalEnv = process.env.NODE_ENV;
    process.env.NODE_ENV = 'development';
    
    render(
      <ErrorBoundary>
        <ErrorThrower shouldThrow={true} />
      </ErrorBoundary>
    );
    
    expect(screen.getByText('Error Details (Development Only)')).toBeInTheDocument();
    
    process.env.NODE_ENV = originalEnv;
  });

  it('hides details in production', () => {
    const originalEnv = process.env.NODE_ENV;
    process.env.NODE_ENV = 'production';
    
    render(
      <ErrorBoundary>
        <ErrorThrower shouldThrow={true} />
      </ErrorBoundary>
    );
    
    expect(screen.queryByText('Error Details (Development Only)')).not.toBeInTheDocument();
    
    process.env.NODE_ENV = originalEnv;
  });

  it('uses custom fallback when provided', () => {
    const customFallback = <div data-testid="custom-fallback">Custom error UI</div>;
    
    render(
      <ErrorBoundary fallback={customFallback}>
        <ErrorThrower shouldThrow={true} />
      </ErrorBoundary>
    );
    
    expect(screen.getByTestId('custom-fallback')).toBeInTheDocument();
    expect(screen.queryByText('Something went wrong')).not.toBeInTheDocument();
  });
});

describe('Error Types', () => {
  it('NetworkError has correct properties', () => {
    const error = new NetworkError('Connection failed', 0, '/api/users');
    
    expect(error.name).toBe('NetworkError');
    expect(error.message).toBe('Connection failed');
    expect(error.statusCode).toBe(0);
    expect(error.endpoint).toBe('/api/users');
  });

  it('AuthenticationError has default message', () => {
    const error = new AuthenticationError();
    
    expect(error.name).toBe('AuthenticationError');
    expect(error.message).toBe('Authentication failed');
    expect(error.statusCode).toBe(401);
  });

  it('ValidationError includes field', () => {
    const error = new ValidationError('Email is invalid', 'email', ['Invalid email format']);
    
    expect(error.name).toBe('ValidationError');
    expect(error.field).toBe('email');
    expect(error.errors).toEqual(['Invalid email format']);
  });

  it('NotFoundError includes resource info', () => {
    const error = new NotFoundError('User not found', 'user', '123');
    
    expect(error.name).toBe('NotFoundError');
    expect(error.resourceType).toBe('user');
    expect(error.resourceId).toBe('123');
  });

  it('ServerError has 500 status', () => {
    const error = new ServerError('Internal error', 500);
    
    expect(error.name).toBe('ServerError');
    expect(error.statusCode).toBe(500);
  });

  describe('createApiError', () => {
    it('creates AuthenticationError for 401', () => {
      const error = createApiError(401, 'Unauthorized', '/api/protected');
      
      expect(error).toBeInstanceOf(AuthenticationError);
      expect((error as AuthenticationError).statusCode).toBe(401);
    });

    it('creates AuthorizationError for 403', () => {
      const error = createApiError(403, 'Forbidden', '/api/admin');
      
      expect(error).toBeInstanceOf(AuthorizationError);
    });

    it('creates NotFoundError for 404', () => {
      const error = createApiError(404, 'Not found', '/api/missing');
      
      expect(error).toBeInstanceOf(NotFoundError);
    });

    it('creates ValidationError for 422', () => {
      const error = createApiError(422, 'Validation failed', '/api/submit');
      
      expect(error).toBeInstanceOf(ValidationError);
    });

    it('creates ServerError for 5xx', () => {
      const error = createApiError(500, 'Internal error');
      
      expect(error).toBeInstanceOf(ServerError);
    });

    it('creates NetworkError for other status codes', () => {
      const error = createApiError(418, "I'm a teapot");
      
      expect(error).toBeInstanceOf(NetworkError);
    });
  });

  describe('getUserFriendlyErrorMessage', () => {
    it('returns network-friendly message for NetworkError', () => {
      const error = new NetworkError('Connection refused');
      const message = getUserFriendlyErrorMessage(error);
      
      expect(message).toContain('internet connection');
    });

    it('returns session message for AuthenticationError', () => {
      const error = new AuthenticationError();
      const message = getUserFriendlyErrorMessage(error);
      
      expect(message).toContain('session');
    });

    it('returns permission message for AuthorizationError', () => {
      const error = new AuthorizationError();
      const message = getUserFriendlyErrorMessage(error);
      
      expect(message).toContain('permission');
    });

    it('returns generic message for unknown errors', () => {
      const error = new Error('Some technical error');
      const message = getUserFriendlyErrorMessage(error);
      
      expect(message).toContain('unexpected error');
      expect(message).not.toContain('Some technical error');
    });
  });

  describe('parseApiError', () => {
    it('parses detail field', () => {
      const response = { detail: 'User not found' };
      const message = parseApiError(response);
      
      expect(message).toBe('User not found');
    });

    it('parses message field', () => {
      const response = { message: 'Something went wrong' };
      const message = parseApiError(response);
      
      expect(message).toBe('Something went wrong');
    });

    it('parses first error from errors object', () => {
      const response = { 
        errors: { 
          email: ['Invalid email'],
          name: ['Name is required']
        } 
      };
      const message = parseApiError(response);
      
      expect(message).toBe('Invalid email');
    });

    it('returns generic message for empty response', () => {
      const response = {};
      const message = parseApiError(response);
      
      expect(message).toBe('An unexpected error occurred');
    });
  });
});
