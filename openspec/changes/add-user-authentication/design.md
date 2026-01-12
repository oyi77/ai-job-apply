# User Authentication System - Technical Design

## Overview
This document outlines the technical design decisions for implementing a comprehensive user authentication system for the AI Job Apply application, including JWT-based authentication, secure password management, email verification, and role-based access control (RBAC).

## 1. JWT Token Implementation

### 1.1 Token Structure
- **Algorithm**: HS256 (HMAC with SHA-256) for symmetric signing
- **Token Type**: Bearer tokens for HTTP Authorization header
- **Payload Claims**:
  - `sub` (subject): User ID (UUID)
  - `email`: User email address
  - `roles`: Array of assigned roles
  - `iat` (issued at): Token creation timestamp
  - `exp` (expiration): Token expiration timestamp
  - `iss` (issuer): Application identifier
  - `aud` (audience): Token audience (API)

### 1.2 Token Lifecycle
- **Access Token**:
  - Validity: 15 minutes
  - Used for API request authentication
  - Stored in memory or secure HTTP-only cookies
  
- **Refresh Token**:
  - Validity: 7 days
  - Used to obtain new access tokens
  - Stored in HTTP-only, Secure cookies only
  - Single-use or rotation-based revocation

### 1.3 Token Validation
- Verify signature using secret key
- Check expiration (`exp` claim)
- Validate issuer (`iss` claim)
- Verify audience (`aud` claim)
- Ensure required claims are present

### 1.4 Token Revocation Strategy
- **Blacklist Approach** (for logout):
  - Store revoked token JTIs (JWT ID) in Redis with TTL matching token expiration
  - Check blacklist during token validation
  - Alternative: Use token versioning with user session tracking
  
## 2. Password Security

### 2.1 Hashing Algorithm
- **Algorithm**: bcrypt with configurable cost factor
- **Cost Factor**: 12 (provides ~250ms hashing on modern hardware)
- **Salt**: Automatically generated and stored with hash

### 2.2 Password Requirements
- Minimum 12 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit
- At least one special character (!@#$%^&*)
- No common patterns or dictionary words

### 2.3 Password Management
- Never store plaintext passwords
- Hash before database storage
- Implement password change functionality with old password verification
- Support password reset via email token
- Enforce password reset on first login
- Implement rate limiting on login attempts (5 attempts in 15 minutes)

### 2.4 Secure Password Reset
- Generate cryptographically secure token (32 bytes minimum)
- Token validity: 24 hours
- Single-use enforcement: Invalidate after use
- Verify token hasn't expired before allowing password change
- Log password change events

## 3. Email Verification

### 3.1 Verification Flow
1. User registers with email
2. Send verification email with signed token
3. User clicks verification link
4. Backend verifies token signature and expiration
5. Mark email as verified
6. User account activated

### 3.2 Verification Token Design
- **Token Type**: JWT-based verification token (separate from auth tokens)
- **Validity**: 48 hours
- **Payload**: User ID, email address, token type
- **Signature**: HS256 with separate secret key

### 3.3 Email Verification Workflow
- Resend capability: Allow token refresh after 15 minutes
- Maximum resend attempts: 5 per day
- Unverified account restrictions:
  - Cannot create job applications
  - Can update profile
  - Receive email reminder after 24 hours

### 3.4 Email Service Integration
- **Provider**: SendGrid or AWS SES for production
- **Template**: HTML email with verification link and fallback token
- **Retry Logic**: Exponential backoff for failed sends
- **Webhook Integration**: Handle bounce/complaint notifications

## 4. Role-Based Access Control (RBAC)

### 4.1 Role Hierarchy
```
System Admin
├── Content Admin
├── Support Admin
└── User Manager

Recruiter
├── Team Lead
└── Team Member

Job Seeker (default)
└── Premium Job Seeker
```

### 4.2 Role Permissions Matrix

#### System Admin
- Manage all users
- View system logs and analytics
- Configure system settings
- Manage roles and permissions
- Access audit trails

#### Content Admin
- Manage job postings
- Manage company profiles
- Moderate user content
- Create announcements

#### Support Admin
- Access support tickets
- Contact users
- Manage support categories
- View support analytics

#### Recruiter
- Post job listings
- View applications
- Contact candidates
- Manage team members (if Team Lead)

#### Job Seeker
- Create profile
- Apply for jobs
- Save job listings
- View application history
- Basic resume building

#### Premium Job Seeker
- All Job Seeker permissions
- Advanced resume building
- Application tracking
- Job alerts
- Priority support

### 4.3 Permission Management
- Permissions stored in database with versioning
- Roles assigned to users with timestamps
- Support role expiration dates
- Audit trail for permission changes

### 4.4 Access Control Implementation
- Middleware for route protection
- Attribute-based decorators (e.g., `@RequireRole('admin')`)
- Granular resource-level checks
- Implicit deny by default

## 5. Security Considerations

### 5.1 Cryptography & Secrets
- Use environment variables for sensitive configuration
- Rotate secret keys quarterly
- Use different secrets for different token types
- Generate cryptographically secure random values using OS-level CSPRNG

### 5.2 Transport Security
- Enforce HTTPS/TLS for all endpoints
- Use HSTS headers with 1-year max-age
- Disable insecure cipher suites
- Certificate pinning in mobile apps (if applicable)

### 5.3 Session Management
- HTTP-only, Secure, SameSite=Strict cookies for refresh tokens
- No sensitive data in JWT payload (use opaque tokens if needed)
- Session timeout on server idle (30 minutes)
- Force re-authentication for sensitive operations (password change, payment)

### 5.4 Brute Force Protection
- Rate limiting:
  - Login endpoint: 5 attempts per 15 minutes per IP
  - Email verification: 5 attempts per 24 hours per email
  - Password reset: 3 attempts per 24 hours per email
- Progressive delays after failed attempts
- CAPTCHA on repeated failures
- Log all failed attempts for monitoring

### 5.5 Input Validation & Sanitization
- Validate email format (RFC 5322 compliant)
- Sanitize all user inputs
- Implement CSRF tokens for state-changing requests
- Validate Content-Type headers
- Size limits on file uploads and request bodies

### 5.6 Data Protection
- Encrypt sensitive data at rest (PII, auth tokens in database)
- Use AES-256-GCM for encryption
- Hash emails before using in URLs
- Mask user IDs when possible
- Implement data retention policies

### 5.7 Logging & Monitoring
- Log authentication events (successful/failed logins)
- Log authorization failures
- Log sensitive operations (role changes, password resets)
- Never log passwords or tokens
- Centralized logging with timestamp and user context
- Alert on suspicious patterns:
  - Multiple failed logins
  - Access from unusual locations
  - Privilege escalations

### 5.8 API Security Headers
```
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Content-Security-Policy: default-src 'self'
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=(), camera=()
```

### 5.9 OAuth2 & Social Login (Future)
- Support third-party providers (Google, GitHub, LinkedIn)
- Use authorization code flow
- Validate redirect URIs
- Verify ID tokens if supported by provider
- Map external user IDs securely

### 5.10 Incident Response
- Procedure for compromised credentials
- Token invalidation mechanism for security breaches
- User notification protocol
- Post-incident analysis and logging

## 6. Database Schema

### Users Table
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  email_verified BOOLEAN DEFAULT FALSE,
  email_verified_at TIMESTAMP,
  first_name VARCHAR(100),
  last_name VARCHAR(100),
  profile_picture_url TEXT,
  is_active BOOLEAN DEFAULT TRUE,
  last_login_at TIMESTAMP,
  password_changed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP
);
```

### User Roles Table
```sql
CREATE TABLE user_roles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  role_id UUID NOT NULL REFERENCES roles(id),
  assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  expires_at TIMESTAMP,
  assigned_by UUID REFERENCES users(id),
  UNIQUE(user_id, role_id)
);
```

### Roles Table
```sql
CREATE TABLE roles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(50) UNIQUE NOT NULL,
  description TEXT,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Role Permissions Table
```sql
CREATE TABLE role_permissions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
  permission_id UUID NOT NULL REFERENCES permissions(id),
  UNIQUE(role_id, permission_id)
);
```

### Permissions Table
```sql
CREATE TABLE permissions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(100) UNIQUE NOT NULL,
  description TEXT,
  resource VARCHAR(50),
  action VARCHAR(50),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Token Blacklist Table (Redis-backed)
```
Key: blacklist:{jti}
Value: true
TTL: token_expiration_time
```

## 7. API Endpoints

### Authentication Endpoints
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/logout` - Logout (invalidate refresh token)
- `POST /api/auth/verify-email` - Verify email with token

### Password Management
- `POST /api/auth/forgot-password` - Request password reset
- `POST /api/auth/reset-password` - Reset password with token
- `POST /api/auth/change-password` - Change password (authenticated)

### User Management (Admin)
- `GET /api/admin/users` - List users with filters
- `GET /api/admin/users/{id}` - Get user details
- `POST /api/admin/users/{id}/roles` - Assign role to user
- `DELETE /api/admin/users/{id}/roles/{roleId}` - Revoke role
- `PUT /api/admin/users/{id}` - Update user status

## 8. Testing Strategy

### Unit Tests
- Password hashing and verification
- JWT token generation and validation
- Email verification token creation
- Permission checking logic

### Integration Tests
- Complete authentication flow
- Token refresh mechanism
- Email sending and verification
- RBAC enforcement

### Security Tests
- Brute force protection
- SQL injection prevention
- XSS vulnerability scanning
- JWT token tampering
- CORS configuration

### Load Tests
- Token validation performance
- Permission checking overhead
- Database connection pooling

## 9. Deployment Considerations

### Environment Configuration
```
JWT_SECRET_KEY=<strong-random-key>
JWT_REFRESH_SECRET=<different-strong-random-key>
EMAIL_VERIFICATION_SECRET=<another-strong-random-key>
BCRYPT_COST_FACTOR=12
TOKEN_EXPIRY_MINUTES=15
REFRESH_TOKEN_EXPIRY_DAYS=7
EMAIL_VERIFICATION_EXPIRY_HOURS=48
```

### Infrastructure
- Use secrets management (AWS Secrets Manager, HashiCorp Vault)
- Implement network policies and firewalls
- Use VPC and private subnets
- Enable VPC Flow Logs for monitoring
- Implement DDoS protection

### Monitoring & Alerting
- Track authentication metrics (success/failure rates)
- Monitor failed login attempts per user
- Alert on unusual access patterns
- Track token validation performance
- Monitor email delivery success rates

## 10. Migration & Rollout Plan

1. **Phase 1**: Deploy authentication service with new database schema
2. **Phase 2**: Implement JWT token generation for new users
3. **Phase 3**: Add email verification flow
4. **Phase 4**: Implement RBAC and permissions
5. **Phase 5**: Enable authentication middleware on API routes
6. **Phase 6**: Migrate existing users with password reset flow
7. **Phase 7**: Full enforcement of authentication on all endpoints

## 11. Future Enhancements

- Two-Factor Authentication (2FA) support
- Biometric authentication
- Hardware security keys (FIDO2/WebAuthn)
- Service-to-service authentication (OAuth2 Client Credentials)
- Session management with concurrent device limits
- Passwordless authentication
- Risk-based authentication with anomaly detection

---

**Document Version**: 1.0  
**Last Updated**: 2025-12-27  
**Status**: Design Phase
