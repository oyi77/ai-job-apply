## 1. Database Schema
- [ ] 1.1 Create notification_preferences table (user_id, email_enabled, application_updates, follow_up_reminders, weekly_summary, created_at, updated_at)
- [ ] 1.2 Create email_logs table (id, user_id, email_type, recipient, subject, status, sent_at, error_message, created_at)
- [ ] 1.3 Add email field to users table (if not exists from auth proposal)
- [ ] 1.4 Create database migration
- [ ] 1.5 Apply migration and test

## 2. Backend Email Service
- [ ] 2.1 Create email service interface in core/
- [ ] 2.2 Implement SMTP email service (using aiosmtplib or similar)
- [ ] 2.3 Implement email template engine (Jinja2)
- [ ] 2.4 Create email template files (HTML + text versions)
- [ ] 2.5 Implement email queue system (background jobs)
- [ ] 2.6 Implement email sending with retry logic
- [ ] 2.7 Implement email logging
- [ ] 2.8 Register email service in service registry

## 3. Email Templates
- [ ] 3.1 Create application status change template
- [ ] 3.2 Create follow-up reminder template
- [ ] 3.3 Create weekly summary template
- [ ] 3.4 Create interview reminder template
- [ ] 3.5 Create welcome email template
- [ ] 3.6 Create password reset template (if needed for auth)
- [ ] 3.7 Test all templates with sample data

## 4. Notification Triggers
- [ ] 4.1 Add notification trigger on application status change
- [ ] 4.2 Add notification trigger on follow-up date
- [ ] 4.3 Add notification trigger for weekly summary (scheduled job)
- [ ] 4.4 Add notification trigger for interview reminders
- [ ] 4.5 Implement notification preference checking
- [ ] 4.6 Add notification rate limiting

## 5. Backend API Endpoints
- [ ] 5.1 Create notifications router (GET /preferences, PUT /preferences, POST /test-email)
- [ ] 5.2 Implement get notification preferences endpoint
- [ ] 5.3 Implement update notification preferences endpoint
- [ ] 5.4 Implement test email endpoint
- [ ] 5.5 Implement email logs endpoint (GET /logs)
- [ ] 5.6 Add email configuration to settings

## 6. Background Job Processing
- [ ] 6.1 Set up background job queue (Celery or similar, or simple async tasks)
- [ ] 6.2 Implement scheduled job for weekly summaries
- [ ] 6.3 Implement scheduled job for follow-up reminders
- [ ] 6.4 Implement email retry mechanism
- [ ] 6.5 Add job monitoring and logging

## 7. Frontend Integration
- [ ] 7.1 Enhance Settings page notification preferences UI
- [ ] 7.2 Add email preference toggles (application updates, follow-ups, weekly summary)
- [ ] 7.3 Add test email button
- [ ] 7.4 Add email logs view (optional)
- [ ] 7.5 Add API service functions for notifications
- [ ] 7.6 Update user preferences store

## 8. Testing
- [ ] 8.1 Write unit tests for email service
- [ ] 8.2 Write unit tests for email templates
- [ ] 8.3 Write integration tests for notification triggers
- [ ] 8.4 Write integration tests for API endpoints
- [ ] 8.5 Test email delivery in development
- [ ] 8.6 Test notification preferences
- [ ] 8.7 Test background job processing

## 9. Configuration
- [ ] 9.1 Add SMTP configuration to environment variables
- [ ] 9.2 Add email templates directory configuration
- [ ] 9.3 Add notification rate limiting configuration
- [ ] 9.4 Document email service setup
- [ ] 9.5 Add email service health check

