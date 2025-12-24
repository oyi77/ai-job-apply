## ADDED Requirements

### Requirement: Rate Limiting for Auth Endpoints
The system SHALL implement rate limiting for authentication endpoints to prevent brute force attacks.

#### Scenario: Rate limit login attempts
- **WHEN** a user attempts to login more than 5 times in 15 minutes from same IP
- **THEN** the system SHALL return 429 (Too Many Requests)
- **AND** the system SHALL include Retry-After header
- **AND** the system SHALL log the rate limit violation

#### Scenario: Rate limit registration attempts
- **WHEN** a user attempts to register more than 3 times in 1 hour from same IP
- **THEN** the system SHALL return 429 (Too Many Requests)
- **AND** the system SHALL include Retry-After header

#### Scenario: Rate limit password reset
- **WHEN** a user requests password reset more than 3 times in 1 hour for same email
- **THEN** the system SHALL return 429 (Too Many Requests)
- **AND** the system SHALL NOT send reset email

### Requirement: Rate Limiting for API Endpoints
The system SHALL implement rate limiting for general API endpoints.

#### Scenario: Rate limit API requests
- **WHEN** a user makes more than 100 requests per minute
- **THEN** the system SHALL return 429 (Too Many Requests)
- **AND** the system SHALL include Retry-After header

#### Scenario: Rate limit AI endpoints
- **WHEN** a user makes more than 10 AI requests per minute
- **THEN** the system SHALL return 429 (Too Many Requests)
- **AND** the system SHALL include Retry-After header

