## ADDED Requirements

### Requirement: Email Notification Service
The system SHALL provide an email notification service for sending emails to users.

#### Scenario: Send application status change notification
- **WHEN** an application status changes
- **AND** the user has email notifications enabled for application updates
- **THEN** the system SHALL send an email notification
- **AND** the email SHALL include the application details (job title, company, new status)
- **AND** the email SHALL include a link to view the application
- **AND** the email SHALL be logged in the email_logs table
- **AND** the email SHALL be sent asynchronously (non-blocking)

#### Scenario: Send notification with disabled preferences
- **WHEN** an application status changes
- **AND** the user has email notifications disabled for application updates
- **THEN** the system SHALL NOT send an email notification
- **AND** the system SHALL log that notification was skipped due to preferences

#### Scenario: Email delivery failure
- **WHEN** an email fails to send
- **THEN** the system SHALL log the error in email_logs
- **AND** the system SHALL retry sending up to 3 times with exponential backoff
- **AND** the system SHALL log each retry attempt
- **AND** if all retries fail, the system SHALL log the final failure

### Requirement: Follow-up Reminders
The system SHALL send email reminders for scheduled follow-ups.

#### Scenario: Send follow-up reminder
- **WHEN** a follow-up date is reached
- **AND** the user has follow-up reminders enabled
- **THEN** the system SHALL send an email reminder
- **AND** the email SHALL include the application details
- **AND** the email SHALL include the original follow-up date
- **AND** the email SHALL include suggested follow-up actions

#### Scenario: Follow-up reminder for past date
- **WHEN** a follow-up date has passed
- **AND** the user has follow-up reminders enabled
- **THEN** the system SHALL send an overdue reminder email
- **AND** the email SHALL indicate that the follow-up is overdue
- **AND** the email SHALL suggest updating the follow-up date

### Requirement: Weekly Summary Emails
The system SHALL send weekly summary emails to users.

#### Scenario: Send weekly summary
- **WHEN** it is the scheduled weekly summary day (e.g., Monday)
- **AND** the user has weekly summary enabled
- **THEN** the system SHALL send a weekly summary email
- **AND** the email SHALL include application statistics for the week
- **AND** the email SHALL include new applications submitted
- **AND** the email SHALL include status changes
- **AND** the email SHALL include upcoming follow-ups
- **AND** the email SHALL include insights and recommendations

#### Scenario: Weekly summary with no activity
- **WHEN** it is the scheduled weekly summary day
- **AND** the user has weekly summary enabled
- **AND** there was no activity during the week
- **THEN** the system SHALL send a summary email
- **AND** the email SHALL indicate no activity
- **AND** the email SHALL include motivational content or suggestions

### Requirement: Email Templates
The system SHALL use HTML email templates with personalization.

#### Scenario: Render email template
- **WHEN** an email needs to be sent
- **THEN** the system SHALL load the appropriate email template
- **AND** the system SHALL render the template with user and application data
- **AND** the system SHALL generate both HTML and plain text versions
- **AND** the system SHALL include proper email headers (From, To, Subject)

#### Scenario: Template personalization
- **WHEN** rendering an email template
- **THEN** the system SHALL replace template variables with actual data
- **AND** the system SHALL include user's name
- **AND** the system SHALL include application-specific details
- **AND** the system SHALL include personalized recommendations when available

### Requirement: Notification Preferences
The system SHALL allow users to configure email notification preferences.

#### Scenario: View notification preferences
- **WHEN** a user requests their notification preferences
- **THEN** the system SHALL return current preferences
- **AND** the preferences SHALL include email_enabled flag
- **AND** the preferences SHALL include application_updates flag
- **AND** the preferences SHALL include follow_up_reminders flag
- **AND** the preferences SHALL include weekly_summary flag

#### Scenario: Update notification preferences
- **WHEN** a user updates their notification preferences
- **THEN** the system SHALL validate the preferences
- **AND** the system SHALL save the preferences to the database
- **AND** the system SHALL return the updated preferences
- **AND** the system SHALL apply preferences immediately to future notifications

#### Scenario: Test email notification
- **WHEN** a user requests a test email
- **THEN** the system SHALL send a test email to the user's email address
- **AND** the email SHALL indicate it is a test email
- **AND** the email SHALL include current notification preferences
- **AND** the email SHALL be logged in email_logs

### Requirement: Email Logging
The system SHALL log all email operations for monitoring and debugging.

#### Scenario: Log successful email
- **WHEN** an email is successfully sent
- **THEN** the system SHALL create an email_log entry
- **AND** the log SHALL include user_id, email_type, recipient, subject
- **AND** the log SHALL include status as "sent"
- **AND** the log SHALL include sent_at timestamp

#### Scenario: Log failed email
- **WHEN** an email fails to send
- **THEN** the system SHALL create an email_log entry
- **AND** the log SHALL include status as "failed"
- **AND** the log SHALL include error_message
- **AND** the log SHALL include retry count

#### Scenario: Query email logs
- **WHEN** a user requests their email logs
- **THEN** the system SHALL return email logs for that user
- **AND** the logs SHALL be paginated
- **AND** the logs SHALL be sorted by most recent first
- **AND** the logs SHALL include email type, status, and timestamp

