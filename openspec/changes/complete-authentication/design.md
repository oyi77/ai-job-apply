# Design: Complete Authentication Implementation

## Context

Authentication is 75% complete. Need to finish endpoint protection, user-scoped filtering, testing, and password reset.

## Decisions

### Decision: User-Scoped Data Filtering in Services
**What**: Filter all data by user_id at service layer
**Why**: 
- Centralized filtering logic
- Consistent security model
- Easy to test and maintain

**Implementation**:
- All service methods accept user_id parameter
- Repository queries automatically filter by user_id
- API endpoints extract user_id from JWT token

### Decision: Password Reset with Email Tokens
**What**: Use time-limited tokens sent via email
**Why**:
- Secure and standard approach
- No password in email
- Time-limited for security

**Token Storage**: Database table (password_reset_tokens)
**Token Expiry**: 1 hour
**Token Format**: Cryptographically secure random string

### Decision: Rate Limiting with slowapi
**What**: Use slowapi library for rate limiting
**Why**:
- FastAPI-compatible
- Easy to configure
- Per-endpoint and per-user limits

**Limits**:
- Login: 5 attempts per 15 minutes per IP
- Register: 3 attempts per hour per IP
- Password reset: 3 attempts per hour per email

### Decision: Database Migration Strategy
**What**: Use Alembic for user table migration
**Why**:
- Already in use for other migrations
- Version controlled
- Rollback support

**Migration Steps**:
1. Create users table
2. Create user_sessions table
3. Add user_id foreign keys to existing tables
4. Add indexes
5. Data migration (if needed)

## Risks / Trade-offs

### Risk: Breaking Existing Functionality
**Mitigation**: Comprehensive testing, gradual rollout

### Risk: Performance Impact of User Filtering
**Mitigation**: Proper indexing, query optimization

### Risk: Email Service Dependency
**Mitigation**: Mock email service for development, graceful degradation

