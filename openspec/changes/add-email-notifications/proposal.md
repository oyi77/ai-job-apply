# Change: Add Email Notifications

## Why

Users need to be notified about important events in their job search journey, such as application status changes, follow-up reminders, and weekly summaries. Currently, users must manually check the application for updates. Email notifications will improve user engagement and ensure users don't miss important opportunities.

## What Changes

- **Email Service Integration**: SMTP-based email service with template support
- **Application Status Notifications**: Email alerts when application status changes
- **Follow-up Reminders**: Automated email reminders for scheduled follow-ups
- **Weekly Summary Emails**: Weekly digest of application activity and insights
- **Email Preferences**: User-configurable notification preferences
- **Email Templates**: Reusable HTML email templates with personalization
- **Notification Queue**: Background job processing for email delivery

## Impact

- **Affected specs**: notifications, user-preferences, email-service
- **Affected code**:
  - `backend/src/services/email_service.py` (new)
  - `backend/src/core/email_service.py` (new interface)
  - `backend/src/api/v1/notifications.py` (new)
  - `backend/src/database/models.py` (add notification_preferences, email_logs)
  - `frontend/src/pages/Settings.tsx` (enhance notification preferences)
  - `frontend/src/services/api.ts` (add notification endpoints)
  - Background job processing system (new)

