# API Reference

This document provides a detailed reference for the AI Job Application Assistant API.

**Base URL**: `/api`

**API Version**: v1

## Authentication

The API uses JSON Web Tokens (JWT) for authentication. To access protected endpoints, you must include an `Authorization` header with a valid JWT.

**Example:**

```
Authorization: Bearer <your_jwt>
```

### Authentication Flow

1. **Register**: Create a new user account via `POST /api/v1/auth/register`
2. **Login**: Authenticate and receive access + refresh tokens via `POST /api/v1/auth/login`
3. **Access Protected Endpoints**: Include `Authorization: Bearer <access_token>` header
4. **Refresh Token**: When access token expires, use `POST /api/v1/auth/refresh` with refresh token
5. **Logout**: Invalidate refresh token via `POST /api/v1/auth/logout`

### Token Details

- **Access Token**: Expires in 15 minutes (configurable)
- **Refresh Token**: Expires in 7 days (configurable)
- **Token Storage**: Store tokens securely (localStorage recommended for web apps)
- **Token Refresh**: Automatically refresh access token before expiration

### Security Features

- **Rate Limiting**: Auth endpoints limited to 10 requests/minute per IP
- **Account Lockout**: Account locked after 5 failed login attempts for 30 minutes
- **CSRF Protection**: CSRF tokens required for state-changing operations
- **Password Requirements**: Minimum 8 characters with complexity requirements
- **Password Hashing**: Passwords hashed with bcrypt (cost factor 12)

## API Versioning

The API version is specified in the URL. For example, to access version 1 of the API, you would use the following URL:

```
/api/v1
```

## Error Responses

The API uses standard HTTP status codes to indicate the success or failure of a request. In addition, the response body will contain a JSON object with more information about the error.

**Example:**

```json
{
  "detail": "Invalid credentials"
}
```

### Common Error Codes

| Status Code | Description |
| --- | --- |
| `400 Bad Request` | The request was malformed or contained invalid data. |
| `401 Unauthorized` | The request did not include a valid JWT. |
| `403 Forbidden` | The client does not have permission to access the requested resource. |
| `404 Not Found` | The requested resource could not be found. |
| `500 Internal Server Error` | An unexpected error occurred on the server. |

## Endpoints

### Auth

#### `POST /api/v1/auth/register`

Register a new user account.

**Rate Limit**: 10 requests per minute per IP

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "name": "John Doe"
}
```

**Password Requirements:**
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit
- At least one special character

**Response (201 Created):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900
}
```

**Error Responses:**
- `400 Bad Request`: Email already exists or validation failed
- `422 Unprocessable Entity`: Invalid request format
- `429 Too Many Requests`: Rate limit exceeded

#### `POST /api/v1/auth/login`

Authenticate a user and receive JWT tokens.

**Rate Limit**: 10 requests per minute per IP

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response (200 OK):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900
}
```

**Error Responses:**
- `400 Bad Request`: Invalid email or password (does not reveal if email exists)
- `400 Bad Request`: Account is locked (after 5 failed attempts)
- `400 Bad Request`: Account is disabled
- `422 Unprocessable Entity`: Invalid request format
- `429 Too Many Requests`: Rate limit exceeded

**Account Lockout:**
- Account locked after 5 failed login attempts
- Lockout duration: 30 minutes (configurable)
- Lockout automatically expires after duration

#### `POST /api/v1/auth/refresh`

Refresh an expired access token using a refresh token.

**Authentication**: Not required (uses refresh token)

**Request Body:**

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200 OK):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900
}
```

**Note**: Refresh token is rotated (new refresh token issued)

**Error Responses:**
- `401 Unauthorized`: Invalid or expired refresh token
- `422 Unprocessable Entity`: Invalid request format

#### `POST /api/v1/auth/logout`

Logout a user by invalidating their refresh token.

**Authentication**: Not required (allows logout with expired tokens)

**Request Body:**

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200 OK):**

```json
{
  "message": "Logged out successfully"
}
```

**Note**: Always returns 200 to allow frontend cleanup, even if token is invalid

---

#### `GET /api/v1/auth/me`

Get the profile of the currently authenticated user.

**Authentication**: Required (Bearer token)

**Response (200 OK):**

```json
{
  "id": "user-uuid",
  "email": "user@example.com",
  "name": "John Doe",
  "is_active": true,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or missing token

---

#### `PUT /api/v1/auth/me`

Update the profile of the currently authenticated user.

**Authentication**: Required (Bearer token)

**Request Body:**

```json
{
  "name": "Updated Name",
  "email": "newemail@example.com"
}
```

**Response (200 OK):**

```json
{
  "id": "user-uuid",
  "email": "newemail@example.com",
  "name": "Updated Name",
  "is_active": true,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T12:00:00Z"
}
```

**Error Responses:**
- `400 Bad Request`: Email already in use
- `401 Unauthorized`: Invalid or missing token
- `422 Unprocessable Entity`: Invalid request format

---

#### `POST /api/v1/auth/change-password`

Change the password for the currently authenticated user.

**Authentication**: Required (Bearer token)

**Request Body:**

```json
{
  "current_password": "OldPassword123!",
  "new_password": "NewPassword456!"
}
```

**Response (200 OK):**

```json
{
  "message": "Password changed successfully"
}
```

**Error Responses:**
- `400 Bad Request`: Current password is incorrect
- `400 Bad Request`: New password doesn't meet requirements
- `401 Unauthorized`: Invalid or missing token
- `422 Unprocessable Entity`: Invalid request format

---

#### `POST /api/v1/auth/request-password-reset`

Request a password reset email.

**Rate Limit**: 3 requests per hour per email

**Request Body:**

```json
{
  "email": "user@example.com"
}
```

**Response (200 OK):**

```json
{
  "message": "If the email exists, a password reset link has been sent"
}
```

**Note**: Always returns success message (does not reveal if email exists)

**Error Responses:**
- `422 Unprocessable Entity`: Invalid request format
- `429 Too Many Requests`: Rate limit exceeded

---

#### `POST /api/v1/auth/reset-password`

Reset password using a reset token.

**Request Body:**

```json
{
  "token": "reset-token-from-email",
  "new_password": "NewPassword456!"
}
```

**Response (200 OK):**

```json
{
  "message": "Password reset successfully"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid or expired reset token
- `400 Bad Request`: New password doesn't meet requirements
- `422 Unprocessable Entity`: Invalid request format

---

#### `DELETE /api/v1/auth/account/{user_id}`

Delete user account (requires password confirmation).

**Authentication**: Required (Bearer token)

**Request Body:**

```json
{
  "password": "CurrentPassword123!"
}
```

**Response (200 OK):**

```json
{
  "message": "Account deleted successfully"
}
```

**Error Responses:**
- `400 Bad Request`: Incorrect password
- `403 Forbidden`: Can only delete your own account
- `401 Unauthorized`: Invalid or missing token

### Jobs

#### `POST /api/v1/jobs/search`

Search for jobs on various job boards.

**Request Body:**

```json
{
  "keywords": ["Software Engineer"],
  "location": "San Francisco, CA"
}
```

**Response:**

```json
{
  "jobs": {
    "linkedin": [
      {
        "title": "Software Engineer",
        "company": "Google",
        "location": "San Francisco, CA",
        "url": "..."
      }
    ]
  }
}
```

### Resumes

#### `POST /api/v1/resumes/upload`

Upload a resume.

**Request:**

The request must be a `multipart/form-data` request with a `file` field containing the resume file.

**Response:**

```json
{
  "id": "...",
  "name": "My Resume.pdf",
  "path": "..."
}
```

#### `GET /api/v1/resumes`

Get a list of all resumes for the currently authenticated user.

**Response:**

```json
[
  {
    "id": "...",
    "name": "My Resume.pdf",
    "path": "..."
  }
]
```