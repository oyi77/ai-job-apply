# Security Guide

This document outlines security best practices, features, and configuration for the AI Job Application Assistant.

## Table of Contents

1. [Authentication & Authorization](#authentication--authorization)
2. [Password Security](#password-security)
3. [Token Management](#token-management)
4. [Rate Limiting](#rate-limiting)
5. [CSRF Protection](#csrf-protection)
6. [Account Lockout](#account-lockout)
7. [Input Validation](#input-validation)
8. [File Upload Security](#file-upload-security)
9. [API Security](#api-security)
10. [Database Security](#database-security)
11. [Production Security](#production-security)

---

## Authentication & Authorization

### JWT Token Structure

The application uses JSON Web Tokens (JWT) for authentication:

- **Algorithm**: HS256
- **Access Token Expiration**: 15 minutes (configurable)
- **Refresh Token Expiration**: 7 days (configurable)
- **Token Storage**: localStorage (frontend) - Note: Consider httpOnly cookies for enhanced security

### Token Lifecycle

1. **Registration/Login**: User receives access token and refresh token
2. **API Requests**: Include access token in `Authorization: Bearer <token>` header
3. **Token Refresh**: Use refresh token to get new access token before expiration
4. **Logout**: Invalidate refresh token (access token expires naturally)

### Protected Endpoints

All API endpoints except the following require authentication:
- `GET /health` - Health check
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Token refresh
- `POST /api/v1/auth/logout` - User logout
- `POST /api/v1/auth/request-password-reset` - Password reset request
- `POST /api/v1/auth/reset-password` - Password reset

### User-Scoped Data

All user data is automatically filtered by `user_id`:
- Applications
- Resumes
- Cover Letters
- Job Searches
- AI Activities

Users can only access their own data, enforced at:
1. **Repository Level**: All queries filter by `user_id`
2. **Service Level**: Services validate user ownership
3. **API Level**: User ID extracted from JWT token

---

## Password Security

### Password Requirements

- **Minimum Length**: 8 characters
- **Complexity**: Must contain:
  - At least one uppercase letter
  - At least one lowercase letter
  - At least one digit
  - At least one special character

### Password Hashing

- **Algorithm**: bcrypt
- **Cost Factor**: 12 (configurable)
- **Salt**: Automatically generated per password
- **Storage**: Never stored in plain text

### Password Reset

- **Token Expiration**: 1 hour
- **Token Format**: Cryptographically secure random string
- **Rate Limiting**: 3 requests per hour per email
- **Email Delivery**: Token sent via email (requires email service)

### Password Change

- **Verification**: Current password required
- **Session Invalidation**: All sessions invalidated on password change
- **Validation**: New password must meet requirements

---

## Token Management

### Access Tokens

- **Purpose**: Short-lived tokens for API access
- **Expiration**: 15 minutes
- **Storage**: localStorage (frontend)
- **Refresh**: Automatic refresh before expiration

### Refresh Tokens

- **Purpose**: Long-lived tokens for obtaining new access tokens
- **Expiration**: 7 days
- **Storage**: Database (server-side)
- **Rotation**: New refresh token issued on each refresh
- **Invalidation**: On logout or password change

### Token Security Best Practices

1. **Storage**: Use httpOnly cookies in production (more secure than localStorage)
2. **Transmission**: Always use HTTPS in production
3. **Expiration**: Keep access token expiration short (15 minutes)
4. **Refresh**: Implement automatic token refresh
5. **Invalidation**: Properly invalidate tokens on logout

---

## Rate Limiting

### Configuration

Rate limiting is enabled by default and can be configured via environment variables:

```bash
RATE_LIMIT_ENABLED=true
RATE_LIMIT_AUTH_PER_MINUTE=10
RATE_LIMIT_API_PER_MINUTE=60
```

### Auth Endpoints

- **Register**: 10 requests per minute per IP
- **Login**: 10 requests per minute per IP
- **Password Reset**: 3 requests per hour per email

### API Endpoints

- **General**: 60 requests per minute per user
- **AI Endpoints**: Lower limits (configurable)

### Rate Limit Response

When rate limit is exceeded:

```json
{
  "detail": "Rate limit exceeded: 10 per 1 minute"
}
```

**Status Code**: 429 Too Many Requests

---

## CSRF Protection

### Implementation

CSRF protection is implemented via middleware:

- **Token Generation**: CSRF token generated on GET requests
- **Token Storage**: Stored in httpOnly cookie
- **Token Validation**: Required for state-changing operations (POST, PUT, DELETE)
- **Exempt Methods**: GET, HEAD, OPTIONS
- **Exempt Paths**: Health check, auth endpoints

### CSRF Token Header

Include CSRF token in request headers:

```
X-CSRF-Token: <csrf-token>
```

Token is automatically included in response headers for subsequent requests.

---

## Account Lockout

### Configuration

Account lockout is enabled by default:

```bash
ACCOUNT_LOCKOUT_ENABLED=true
MAX_FAILED_LOGIN_ATTEMPTS=5
ACCOUNT_LOCKOUT_DURATION_MINUTES=30
```

### Lockout Behavior

- **Trigger**: 5 failed login attempts
- **Duration**: 30 minutes
- **Automatic Unlock**: Account unlocks after duration
- **Reset**: Failed attempts reset on successful login

### Lockout Response

When account is locked:

```json
{
  "detail": "Account is locked. Please try again in 30 minutes."
}
```

**Status Code**: 400 Bad Request

---

## Input Validation

### Request Validation

All API requests are validated using Pydantic models:

- **Type Validation**: Automatic type checking
- **Required Fields**: Enforced at model level
- **Format Validation**: Email, URL, date formats
- **Range Validation**: Numeric ranges, string lengths

### Sanitization

- **SQL Injection**: Prevented via ORM (parameterized queries)
- **XSS**: Input sanitization for user-generated content
- **Path Traversal**: File paths validated and sanitized
- **Command Injection**: No shell command execution

---

## File Upload Security

### File Validation

- **File Types**: PDF, DOCX, TXT only
- **File Size**: Maximum 10MB (configurable)
- **MIME Type**: Validated against file extension
- **Content Scanning**: Basic content validation

### File Storage

- **Path Sanitization**: Filenames sanitized
- **Directory Isolation**: Files stored in user-specific directories
- **Permissions**: Proper file permissions set
- **Access Control**: Files only accessible by owner

---

## API Security

### CORS Configuration

CORS is configured for specific origins:

```bash
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

**Production**: Configure with actual frontend domain

### Security Headers

Recommended security headers (configure in reverse proxy):

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- `Content-Security-Policy: default-src 'self'`

### Error Handling

- **Error Messages**: Generic messages (no sensitive info)
- **Stack Traces**: Only in development mode
- **Logging**: Comprehensive logging without sensitive data

---

## Database Security

### Connection Security

- **Encryption**: Use SSL/TLS in production
- **Connection Pooling**: Proper connection management
- **Credentials**: Stored in environment variables

### Query Security

- **ORM Usage**: SQLAlchemy ORM prevents SQL injection
- **Parameterized Queries**: All queries use parameters
- **User Filtering**: All queries filter by user_id

### Data Protection

- **Encryption at Rest**: Consider database-level encryption
- **Backups**: Encrypted backups
- **Access Control**: Database user with minimal privileges

---

## Production Security

### Environment Variables

Never commit sensitive data. Use environment variables:

```bash
SECRET_KEY=<strong-random-secret>
JWT_SECRET_KEY=<strong-random-secret>
DATABASE_URL=<database-connection-string>
GEMINI_API_KEY=<api-key>
```

### HTTPS

- **SSL/TLS**: Required in production
- **Certificate**: Valid SSL certificate
- **Redirect**: HTTP to HTTPS redirect

### Monitoring

- **Security Logging**: Log all authentication attempts
- **Failed Login Tracking**: Monitor failed login attempts
- **Rate Limit Monitoring**: Track rate limit violations
- **Error Tracking**: Monitor security-related errors

### Regular Security Audits

- **Code Review**: Regular security code reviews
- **Dependency Updates**: Keep dependencies updated
- **Vulnerability Scanning**: Regular security scans
- **Penetration Testing**: Periodic security testing

---

## Security Checklist

### Development

- [ ] All passwords hashed with bcrypt
- [ ] JWT tokens properly configured
- [ ] Rate limiting enabled
- [ ] CSRF protection enabled
- [ ] Account lockout enabled
- [ ] Input validation on all endpoints
- [ ] File upload validation
- [ ] CORS properly configured

### Production

- [ ] HTTPS enabled
- [ ] Security headers configured
- [ ] Environment variables secured
- [ ] Database encryption enabled
- [ ] Regular backups configured
- [ ] Monitoring and alerting set up
- [ ] Security logging enabled
- [ ] Regular security audits scheduled

---

## Reporting Security Issues

If you discover a security vulnerability, please report it responsibly:

1. **Do not** create a public GitHub issue
2. Email security concerns to: [security-email]
3. Include detailed information about the vulnerability
4. Allow time for the issue to be addressed before public disclosure

---

**Last Updated**: 2025-01-27  
**Version**: 1.0.0

