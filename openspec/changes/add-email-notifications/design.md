## Context

The application currently has no email notification system. Users must manually check the application for updates, which leads to missed opportunities and reduced engagement. This change introduces a comprehensive email notification system to keep users informed about their job search progress.

## Goals / Non-Goals

### Goals
- Email notifications for application status changes
- Automated follow-up reminders
- Weekly summary emails
- User-configurable notification preferences
- Reliable email delivery with retry logic
- HTML email templates with personalization

### Non-Goals
- SMS notifications (future)
- Push notifications (future)
- Real-time notifications (future)
- Email marketing campaigns (future)
- Multi-language email support (future)

## Decisions

### Decision: SMTP-based Email Service
**What**: Use SMTP protocol for email delivery via aiosmtplib or similar
**Why**:
- Standard protocol, widely supported
- Works with any SMTP provider (Gmail, SendGrid, AWS SES, etc.)
- Simple implementation
- No vendor lock-in

**Alternatives considered**:
- SendGrid API: Vendor lock-in, additional cost
- AWS SES API: More complex, AWS-specific
- Mailgun API: Vendor lock-in, additional cost

### Decision: Jinja2 for Email Templates
**What**: Use Jinja2 templating engine for email templates
**Why**:
- Already used in project (FastAPI/Jinja2)
- Powerful templating with variables and conditionals
- Supports HTML and text versions
- Easy to maintain and test

**Alternatives considered**:
- String formatting: Limited functionality
- Custom templating: Unnecessary complexity

### Decision: Background Job Processing
**What**: Use async background tasks for email sending
**Why**:
- Non-blocking API responses
- Better error handling and retry logic
- Can process email queue efficiently
- Scalable for high volume

**Alternatives considered**:
- Synchronous email sending: Blocks API, poor user experience
- Celery: More complex setup, requires Redis/RabbitMQ
- Simple async tasks: Sufficient for MVP, can upgrade later

### Decision: Email Queue in Database
**What**: Store email queue in database table
**Why**:
- Simple implementation
- Persistent queue (survives restarts)
- Easy to monitor and debug
- Can query email status

**Alternatives considered**:
- Redis queue: Requires additional infrastructure
- In-memory queue: Lost on restart, not suitable for production

## Risks / Trade-offs

### Risk: Email Delivery Failures
**Mitigation**:
- Retry logic with exponential backoff
- Email logging for debugging
- Fallback to in-app notifications
- Monitor email delivery rates

### Risk: Email Spam/Blacklisting
**Mitigation**:
- Use reputable SMTP provider
- Implement rate limiting
- Follow email best practices
- Monitor bounce rates

### Risk: Background Job Failures
**Mitigation**:
- Comprehensive error logging
- Job retry mechanism
- Health monitoring
- Alert on job failures

### Risk: User Email Preferences Not Respected
**Mitigation**:
- Check preferences before sending
- Log preference checks
- Provide clear UI for preferences
- Test preference enforcement

## Migration Plan

### Steps
1. Add email service configuration (non-breaking)
2. Create database tables for preferences and logs (non-breaking)
3. Implement email service (non-breaking)
4. Add notification triggers (non-breaking, opt-in)
5. Enable notifications by default for new users
6. Send welcome email to existing users (optional)

### Rollback
- Disable notification triggers
- Keep email service for future use
- Users can disable notifications via preferences

## Open Questions

- Which SMTP provider should we use by default? (Gmail, SendGrid, AWS SES)
- Should we support email attachments? (resumes, cover letters)
- What should be the default notification preferences?
- Should we implement email batching for multiple notifications?
- What should be the weekly summary schedule? (Monday morning?)

