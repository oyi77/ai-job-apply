/**Error types for the application.

This module defines error types used throughout the application
for consistent error handling and user-friendly error messages.
*/

// Network-related errors
export class NetworkError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public endpoint?: string
  ) {
    super(message);
    this.name = 'NetworkError';
  }
}

export class AuthenticationError extends Error {
  constructor(
    message: string = 'Authentication failed',
    public statusCode: number = 401
  ) {
    super(message);
    this.name = 'AuthenticationError';
  }
}

export class AuthorizationError extends Error {
  constructor(
    message: string = 'You do not have permission to access this resource',
    public statusCode: number = 403
  ) {
    super(message);
    this.name = 'AuthorizationError';
  }
}

export class ValidationError extends Error {
  constructor(
    message: string,
    public field?: string,
    public errors?: string[]
  ) {
    super(message);
    this.name = 'ValidationError';
  }
}

export class NotFoundError extends Error {
  constructor(
    message: string = 'The requested resource was not found',
    public resourceType?: string,
    public resourceId?: string
  ) {
    super(message);
    this.name = 'NotFoundError';
  }
}

export class ServerError extends Error {
  constructor(
    message: string = 'An internal server error occurred',
    public statusCode: number = 500
  ) {
    super(message);
    this.name = 'ServerError';
  }
}

// API Error factory
export function createApiError(statusCode: number, message: string, endpoint?: string): Error {
  switch (statusCode) {
    case 401:
      return new AuthenticationError(message, statusCode);
    case 403:
      return new AuthorizationError(message, statusCode);
    case 404:
      return new NotFoundError(message, undefined, undefined);
    case 422:
      return new ValidationError(message);
    case 500:
    case 502:
    case 503:
    case 504:
      return new ServerError(message, statusCode);
    default:
      return new NetworkError(message, statusCode, endpoint);
  }
}

// Error response from API
export interface ApiErrorResponse {
  detail?: string;
  errors?: Record<string, string[]>;
  message?: string;
}

// Parse API error response
export function parseApiError(response: ApiErrorResponse): string {
  if (response.detail) {
    return response.detail;
  }
  if (response.message) {
    return response.message;
  }
  if (response.errors) {
    const firstError = Object.values(response.errors)[0];
    if (firstError && firstError.length > 0) {
      return firstError[0];
    }
  }
  return 'An unexpected error occurred';
}

// User-friendly error messages (no sensitive details)
export function getUserFriendlyErrorMessage(error: Error): string {
  if (error instanceof NetworkError) {
    if (error.statusCode === 0 || !error.statusCode) {
      return 'Unable to connect to the server. Please check your internet connection.';
    }
    return 'A network error occurred. Please try again later.';
  }
  
  if (error instanceof AuthenticationError) {
    return 'Your session has expired. Please log in again.';
  }
  
  if (error instanceof AuthorizationError) {
    return 'You do not have permission to perform this action.';
  }
  
  if (error instanceof ValidationError) {
    return error.message || 'Please check your input and try again.';
  }
  
  if (error instanceof NotFoundError) {
    return 'The requested resource was not found.';
  }
  
  if (error instanceof ServerError) {
    return 'A server error occurred. Please try again later.';
  }
  
  // Generic error - don't expose technical details
  return 'An unexpected error occurred. Please try again.';
}

// Error boundary error info
export interface ErrorInfo {
  componentStack?: string;
  timestamp: Date;
  userAgent?: string;
  url?: string;
}

// Create error info for reporting
export function createErrorInfo(error: Error, componentStack?: string): ErrorInfo {
  return {
    componentStack,
    timestamp: new Date(),
    userAgent: typeof navigator !== 'undefined' ? navigator.userAgent : undefined,
    url: typeof window !== 'undefined' ? window.location.href : undefined,
  };
}
