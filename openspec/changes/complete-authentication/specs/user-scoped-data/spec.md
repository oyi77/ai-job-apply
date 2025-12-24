## ADDED Requirements

### Requirement: User-Scoped Data Access
The system SHALL ensure users can only access their own data.

#### Scenario: User accesses own applications
- **WHEN** a user requests their applications
- **THEN** the system SHALL return only applications belonging to that user
- **AND** the system SHALL filter by user_id from JWT token
- **AND** the system SHALL NOT return other users' applications

#### Scenario: User attempts to access another user's application
- **WHEN** a user requests an application by ID that belongs to another user
- **THEN** the system SHALL return 404 (Not Found)
- **AND** the system SHALL NOT reveal that the application exists
- **AND** the system SHALL log the access attempt

#### Scenario: User creates application
- **WHEN** a user creates a new application
- **THEN** the system SHALL automatically associate it with the user's ID
- **AND** the system SHALL store the user_id in the database
- **AND** the system SHALL return the created application with user_id

#### Scenario: User updates application
- **WHEN** a user attempts to update an application
- **THEN** the system SHALL verify the application belongs to the user
- **AND** if not, the system SHALL return 404
- **AND** if yes, the system SHALL update the application

#### Scenario: User deletes application
- **WHEN** a user attempts to delete an application
- **THEN** the system SHALL verify the application belongs to the user
- **AND** if not, the system SHALL return 404
- **AND** if yes, the system SHALL delete the application

### Requirement: User-Scoped Data Filtering in Services
All services SHALL filter data by user_id automatically.

#### Scenario: Service filters by user_id
- **WHEN** a service method is called with user_id
- **THEN** the service SHALL filter all queries by user_id
- **AND** the service SHALL NOT return data from other users
- **AND** the service SHALL apply user_id filter at repository level

#### Scenario: Repository filters by user_id
- **WHEN** a repository query is executed with user_id
- **THEN** the repository SHALL add user_id filter to SQL query
- **AND** the repository SHALL use parameterized queries
- **AND** the repository SHALL ensure data isolation

