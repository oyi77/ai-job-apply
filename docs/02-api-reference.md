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

Register a new user.

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "password123",
  "full_name": "John Doe"
}
```

**Response:**

```json
{
  "access_token": "...",
  "refresh_token": "..."
}
```

#### `POST /api/v1/auth/login`

Authenticate a user and receive a JWT.

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**

```json
{
  "access_token": "...",
  "refresh_token": "..."
}
```

#### `POST /api/v1/auth/refresh`

Refresh an expired JWT.

**Request Body:**

```json
{
  "refresh_token": "..."
}
```

**Response:**

```json
{
  "access_token": "...",
  "refresh_token": "..."
}
```

#### `GET /api/v1/auth/me`

Get the profile of the currently authenticated user.

**Response:**

```json
{
  "id": "...",
  "email": "user@example.com",
  "full_name": "John Doe"
}
```

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