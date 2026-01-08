# Data Model: Authentication Session & Sign-Up Validation

**Feature**: 001-auth-session-fix
**Date**: 2025-12-23
**Phase**: 1 - Design

## Overview

This document defines the data structures for session responses and validation error handling. These models are technology-agnostic representations that will be implemented in both TypeScript (auth-service) and Python (backend).

## Core Entities

### User Session

Represents an authenticated user's identity information returned by the session endpoint.

**Purpose**: Provide backend services with the minimum user data needed for authorization decisions

**Attributes**:
- `id` (string, required): Unique user identifier (UUID format)
- `email` (string, required): User's email address
- `name` (string, optional): User's display name
- `emailVerified` (boolean, required): Whether email has been verified (always false per requirements)

**Validation Rules**:
- `id`: Must be valid UUID v4 format
- `email`: Must be valid email format (RFC 5322)
- `name`: Maximum 100 characters if present
- `emailVerified`: Currently always false (email verification out of scope)

**Relationships**:
- Derived from database User entity via JWT token
- No direct database query - extracted from token claims

**State Transitions**: None (read-only snapshot)

**Example**:
```json
{
  "user": {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "email": "user@example.com",
    "name": "John Doe",
    "emailVerified": false
  }
}
```

---

### Sign-Up Request

Represents user registration input data.

**Purpose**: Capture user credentials and optional profile information for account creation

**Attributes**:
- `email` (string, required): User's email address for login and identification
- `password` (string, required): User's password (will be hashed before storage)
- `name` (string, optional): User's display name

**Validation Rules**:
- `email`:
  - Required (must not be null or empty)
  - Must match email format regex
  - Must be unique in database
  - Maximum 255 characters
- `password`:
  - Required (must not be null or empty)
  - Minimum 8 characters
  - Maximum 128 characters
  - Will be hashed using bcrypt before storage (not stored in plain text)
- `name`:
  - Optional (can be null or empty)
  - Maximum 100 characters if provided
  - Trimmed of leading/trailing whitespace

**Constraints**:
- Email uniqueness enforced by database UNIQUE constraint
- Password never stored in plain text
- Password never returned in any API response

**Example**:
```json
{
  "email": "newuser@example.com",
  "password": "SecurePassword123",
  "name": "Jane Smith"
}
```

---

### Sign-Up Success Response

Returned when user successfully creates an account.

**Purpose**: Provide authentication token and user profile to newly registered user

**Attributes**:
- `token` (string, required): JWT authentication token for subsequent API requests
- `user` (object, required): User profile information (same structure as User Session)

**Example**:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "email": "newuser@example.com",
    "name": "Jane Smith",
    "emailVerified": false
  }
}
```

**Additional Headers**:
- `set-auth-token`: Contains the same token (for cross-origin compatibility)

---

### Validation Error Response

Represents structured error information for validation failures.

**Purpose**: Provide specific, actionable feedback to users when input fails validation

**Attributes**:
- `error` (string, required): Human-readable error message describing what went wrong

**Validation Error Types**:

| Type | HTTP Status | Error Message |
|------|-------------|---------------|
| Password too short | 400 | "Password must be at least 8 characters long" |
| Password too long | 400 | "Password must not exceed 128 characters" |
| Invalid email format | 400 | "Invalid email address format" |
| Duplicate email | 409 | "An account with this email already exists" |
| Missing email | 400 | "Email is required" |
| Missing password | 400 | "Password is required" |
| Invalid token | 401 | "Invalid or expired token" |
| Missing authorization | 401 | "Authorization header is required" |

**Example**:
```json
{
  "error": "Password must be at least 8 characters long"
}
```

---

### Authentication Token (JWT)

Internal token structure (not directly visible to clients except as opaque string).

**Purpose**: Stateless authentication mechanism for verifying user identity

**Claims** (JWT payload):
- `sub` (string): User ID (subject)
- `email` (string): User's email
- `iat` (number): Issued at timestamp
- `exp` (number): Expiration timestamp (7 days from issuance)

**Validation**:
- Signature verified using `BETTER_AUTH_SECRET`
- Expiration checked on each request
- Issuer validation (Better Auth)

**Security**:
- Signed with HS256 algorithm
- Secret stored in environment variable (never in code)
- Cannot be tampered with without secret
- Stateless (no database lookup required for validation)

---

## Database Schema (Reference Only)

This section documents existing database structure from `auth-service/src/db/schema.ts`.

### User Table

```sql
CREATE TABLE user (
  id TEXT PRIMARY KEY,           -- UUID
  email TEXT UNIQUE NOT NULL,
  emailVerified BOOLEAN DEFAULT FALSE,
  name TEXT,
  createdAt TIMESTAMP NOT NULL,
  updatedAt TIMESTAMP NOT NULL,
  image TEXT
);
```

**Indexes**:
- Primary key on `id`
- Unique index on `email`

### Session Table

```sql
CREATE TABLE session (
  id TEXT PRIMARY KEY,
  expiresAt TIMESTAMP NOT NULL,
  token TEXT UNIQUE NOT NULL,
  ipAddress TEXT,
  userAgent TEXT,
  userId TEXT NOT NULL,
  activeOrganizationId TEXT,
  impersonatedBy TEXT,
  createdAt TIMESTAMP NOT NULL,
  updatedAt TIMESTAMP NOT NULL,
  FOREIGN KEY (userId) REFERENCES user(id)
);
```

**Note**: Sessions table used for cookie-based sessions. JWT tokens are stateless and don't require session table lookups for validation.

---

## Error Handling Flow

```
Request → Validation → Error?
                        ├─ YES → Classify Error Type
                        │         ├─ Validation → 400 + specific message
                        │         ├─ Duplicate → 409 + conflict message
                        │         ├─ Auth → 401 + auth message
                        │         └─ Server → 500 + generic message (production)
                        └─ NO → Process Request → Success Response
```

---

## Data Flow Diagrams

### Session Validation Flow

```
Client Request (with Bearer token)
    ↓
Auth Service Hono Middleware
    ↓
Better Auth Handler
    ↓
JWT Validation (signature, expiration)
    ↓
    ├─ Valid → Extract user claims → Return User Session
    └─ Invalid → Return 401 + Validation Error
```

### Sign-Up Flow

```
Client Sign-Up Request
    ↓
Auth Service Hono Middleware
    ↓
Rate Limit Check (5 req/min)
    ↓
Better Auth Sign-Up Handler
    ↓
Validation (email format, password length)
    ├─ Fail → Return 400 + Validation Error
    └─ Pass ↓
Database Unique Check (email)
    ├─ Duplicate → Return 409 + Validation Error
    └─ Unique ↓
Hash Password (bcrypt)
    ↓
Insert User Record
    ↓
Generate JWT Token
    ↓
Return 201 + Sign-Up Success Response
```

---

## Consistency Rules

1. **Error Message Format**: All errors return JSON with single `error` field
2. **User ID Format**: Always UUID v4 (e.g., `123e4567-e89b-12d3-a456-426614174000`)
3. **Email Normalization**: Emails stored and compared in lowercase
4. **Timestamp Format**: ISO 8601 UTC (e.g., `2025-12-23T10:30:00Z`)
5. **Token Header**: Always use `Authorization: Bearer {token}` format
6. **Response Wrapping**: Session data always wrapped in `user` object for consistency

---

## Security Constraints

1. **Never Return**:
   - Password hashes
   - Internal session IDs (unless necessary)
   - Database internal IDs beyond user ID
   - JWT secrets or signing keys

2. **Always Validate**:
   - Token signature before trusting claims
   - Token expiration before granting access
   - Email uniqueness before insert
   - Input lengths to prevent buffer overflows

3. **Rate Limiting**:
   - Session endpoint: Max 30 requests/minute per IP
   - Sign-up endpoint: Max 5 requests/minute per IP

---

## Future Considerations (Out of Scope)

- Email verification flow (User Session.emailVerified currently always false)
- Password complexity requirements (uppercase, numbers, special chars)
- Account deletion or deactivation status
- Session revocation or blacklisting
- Multi-factor authentication (MFA)
- OAuth/social provider data
