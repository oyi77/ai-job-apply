# Design: Security Enhancements

## Context

Need to add production-grade security measures beyond basic authentication.

## Decisions

### Decision: Rate Limiting with slowapi
**What**: Use slowapi for FastAPI-compatible rate limiting
**Why**:
- FastAPI-native
- Easy configuration
- Per-endpoint and per-IP limits

**Configuration**:
```python
# Auth endpoints
login: 5 requests / 15 minutes / IP
register: 3 requests / hour / IP
password_reset: 3 requests / hour / email

# API endpoints
general: 100 requests / minute / user
ai_endpoints: 10 requests / minute / user
```

### Decision: CSRF Protection with Double Submit Cookie
**What**: Use double submit cookie pattern for CSRF protection
**Why**:
- Stateless (no server-side storage)
- Works with JWT authentication
- Simple implementation

**Implementation**:
- Generate CSRF token on GET requests
- Store in httpOnly cookie
- Include in request header for state-changing operations
- Validate token matches cookie

### Decision: Account Lockout Strategy
**What**: Lock account after 5 failed attempts for 30 minutes
**Why**:
- Prevents brute force attacks
- Reasonable lockout duration
- Automatic unlock

**Storage**: Track in database (user table or separate table)

### Decision: Password History
**What**: Prevent reuse of last 5 passwords
**Why**:
- Security best practice
- Prevents password cycling
- Reasonable history size

**Storage**: Encrypted password hashes in password_history table

## Risks / Trade-offs

### Risk: Rate Limiting False Positives
**Mitigation**: Configurable limits, IP whitelist, user feedback

### Risk: CSRF Complexity
**Mitigation**: Use proven patterns, comprehensive testing

### Risk: Account Lockout User Friction
**Mitigation**: Clear error messages, reasonable lockout duration

