## ADDED Requirements

### Requirement: CSRF Protection
The system SHALL protect state-changing operations from CSRF attacks.

#### Scenario: CSRF token validation
- **WHEN** a user makes a state-changing request (POST, PUT, DELETE)
- **THEN** the system SHALL validate CSRF token
- **AND** if token is missing or invalid, the system SHALL return 403 (Forbidden)
- **AND** the system SHALL log the CSRF violation

#### Scenario: CSRF token generation
- **WHEN** a user loads a page with forms
- **THEN** the system SHALL provide a CSRF token
- **AND** the system SHALL store token in httpOnly cookie
- **AND** the system SHALL include token in response header

#### Scenario: CSRF token refresh
- **WHEN** a CSRF token expires
- **THEN** the system SHALL allow token refresh
- **AND** the system SHALL generate new token
- **AND** the system SHALL update cookie

