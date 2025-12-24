## ADDED Requirements

### Requirement: Password Reset Request
The system SHALL allow users to request a password reset via email.

#### Scenario: Request password reset
- **WHEN** a user requests password reset with valid email
- **THEN** the system SHALL generate a secure reset token
- **AND** the system SHALL store the token with expiration time
- **AND** the system SHALL send reset email to user
- **AND** the system SHALL return success message (don't reveal if email exists)

#### Scenario: Request password reset with invalid email
- **WHEN** a user requests password reset with invalid email
- **THEN** the system SHALL return success message (don't reveal if email exists)
- **AND** the system SHALL NOT generate a token

#### Scenario: Rate limit password reset requests
- **WHEN** a user requests password reset more than 3 times per hour
- **THEN** the system SHALL return rate limit error
- **AND** the system SHALL NOT generate a new token

### Requirement: Password Reset
The system SHALL allow users to reset their password using a valid token.

#### Scenario: Reset password with valid token
- **WHEN** a user submits password reset with valid token and new password
- **THEN** the system SHALL validate the token
- **AND** the system SHALL validate password strength
- **AND** the system SHALL update user password
- **AND** the system SHALL invalidate the token
- **AND** the system SHALL invalidate all user sessions
- **AND** the system SHALL return success message

#### Scenario: Reset password with expired token
- **WHEN** a user submits password reset with expired token
- **THEN** the system SHALL return error message
- **AND** the system SHALL NOT update password

#### Scenario: Reset password with invalid token
- **WHEN** a user submits password reset with invalid token
- **THEN** the system SHALL return error message
- **AND** the system SHALL NOT update password

#### Scenario: Reset password with weak password
- **WHEN** a user submits password reset with weak password
- **THEN** the system SHALL return validation error
- **AND** the system SHALL NOT update password

