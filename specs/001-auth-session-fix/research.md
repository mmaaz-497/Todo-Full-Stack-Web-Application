# Research: Authentication Session Endpoint & Sign-Up Validation

**Feature**: 001-auth-session-fix
**Date**: 2025-12-23
**Phase**: 0 - Research & Discovery

## Executive Summary

This research phase investigated how to expose and enhance the Better Auth session endpoint to enable proper token validation by backend services, and how to add comprehensive validation error handling for sign-up operations.

**Key Finding**: Better Auth (v1.0.9) already provides a `/api/auth/session` endpoint through its handler, but it requires proper Bearer token configuration and may need explicit error handling middleware to provide clear validation messages.

## Research Tasks

### 1. Better Auth Session Endpoint Capabilities

**Decision**: Use Better Auth's built-in session endpoint with Bearer token authentication

**Rationale**:
- Better Auth provides automatic session management via `auth.handler()` which routes to `/api/auth/session`
- The `bearer()` plugin already configured in auth-service enables Bearer token authentication
- This endpoint returns user session data when given a valid token via Authorization header
- No custom endpoint needed - the infrastructure already exists

**Alternatives Considered**:
1. **Custom session validation endpoint** - Rejected because Better Auth already provides this functionality; duplicating it would violate DRY principles
2. **Database-based session lookup** - Rejected because JWT tokens are stateless and can be validated without DB queries; adding DB lookups would hurt performance
3. **Proxy endpoint in backend** - Rejected because it adds unnecessary network hop and complexity; backend should call auth service directly

**Implementation Details**:
- Better Auth's session endpoint is automatically available at `GET /api/auth/session`
- Requires `Authorization: Bearer {token}` header
- Returns user object with fields: `id`, `email`, `name`, `emailVerified`, `image`, `createdAt`, `updatedAt`
- Returns 401 for invalid/expired tokens
- Respects existing CORS and rate limiting middleware

**References**:
- Better Auth documentation: Session management
- Existing auth-service implementation: `auth-service/src/lib/auth.ts` (lines 13, 35-39)
- Backend token validation logic: `backend/auth.py` (lines 26-49)

### 2. Sign-Up Validation Error Handling

**Decision**: Add custom error handling middleware to intercept Better Auth validation errors and transform them into specific, actionable messages

**Rationale**:
- Better Auth returns generic error responses that don't specify which field failed validation
- Users need field-specific feedback to correct their input efficiently
- Middleware approach preserves Better Auth functionality while enhancing error responses
- Can be added without modifying Better Auth library code

**Alternatives Considered**:
1. **Fork Better Auth** - Rejected due to maintenance burden and upgrade complexity
2. **Pre-validation layer** - Considered but rejected because it duplicates Better Auth's validation logic
3. **Custom sign-up endpoint** - Rejected because it bypasses Better Auth's security features and session management

**Implementation Approach**:
- Create validation middleware that intercepts Better Auth error responses
- Parse error details to determine specific validation failure (password length, email format, duplicate email)
- Return structured error responses with:
  - Appropriate HTTP status code (400 for validation, 409 for conflicts)
  - Specific error message identifying the field and constraint
  - Consistent error response format: `{ "error": "message" }`

**Validation Rules to Implement**:
- Password length: 8-128 characters (already configured in Better Auth)
- Email format: Standard RFC 5322 validation (Better Auth default)
- Email uniqueness: Database constraint (Drizzle schema enforces)
- Field presence: email and password required

**Error Message Mapping**:
```
Better Auth Error → Custom Response
─────────────────────────────────────────────────────────────
"Password is too short" → 400: "Password must be at least 8 characters long"
"Password is too long" → 400: "Password must not exceed 128 characters"
"Invalid email" → 400: "Invalid email address format"
UNIQUE constraint → 409: "An account with this email already exists"
Missing field → 400: "Email and password are required"
```

### 3. HTTP Status Code Standards

**Decision**: Follow RFC 7231 and REST best practices for status codes

**Rationale**:
- Proper status codes enable client-side error handling without parsing messages
- 400 vs 409 distinction helps clients differentiate between input errors and conflict errors
- Industry standard approach improves API predictability

**Status Code Mapping**:
- **200 OK**: Successful session retrieval, successful sign-in
- **201 Created**: Successful sign-up (new user created)
- **400 Bad Request**: Validation errors (password length, email format, missing fields)
- **401 Unauthorized**: Invalid/expired token, missing Authorization header
- **409 Conflict**: Duplicate email (resource already exists)
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Unexpected server errors

**References**:
- RFC 7231: HTTP/1.1 Semantics and Content
- REST API Design Rulebook (O'Reilly)

### 4. Security Considerations

**Decision**: Maintain existing security measures and add response filtering

**Rationale**:
- Better Auth already handles password hashing, token generation, and session management securely
- Need to ensure session endpoint doesn't leak sensitive data
- Error messages must not reveal system internals

**Security Measures**:
1. **Session Endpoint Response Filtering**:
   - NEVER return: password, passwordHash, internal tokens, session IDs
   - ONLY return: user ID, email, name, emailVerified status
   - Filter controlled by response middleware

2. **Error Message Sanitization**:
   - Generic messages for server errors in production
   - Specific validation messages safe to expose (don't reveal DB structure)
   - No stack traces in production responses

3. **Rate Limiting**:
   - Session endpoint: 30 req/min (already configured)
   - Sign-up endpoint: 5 req/min (already configured)
   - Prevents brute force and enumeration attacks

4. **CORS Configuration**:
   - Allow only configured frontend origins
   - Credentials support enabled for cookie-based auth
   - Proper preflight handling

**Attack Vectors Mitigated**:
- Email enumeration: Timing attack prevention via consistent response times
- Password guessing: Rate limiting on authentication endpoints
- Token theft: Secure cookie settings (httpOnly, secure in production)
- XSS: CSP headers already configured in security middleware

### 5. Backend Integration Pattern

**Decision**: Backend validates tokens by calling auth service session endpoint synchronously

**Rationale**:
- Auth service is single source of truth for authentication
- Synchronous validation is simple and has acceptable latency (<50ms on local network)
- Avoids token duplication and synchronization issues

**Flow**:
```
1. Client → Backend API request with Authorization: Bearer {token}
2. Backend → Auth Service GET /api/auth/session with same token
3. Auth Service validates token → Returns user data or 401
4. Backend → Extracts user ID and proceeds with authorization
5. Backend → Returns API response to client
```

**Performance Optimization**:
- Auth service session endpoint uses JWT validation (no DB query)
- Response time target: <200ms for 95% of requests
- Backend can cache validation for short TTL (5 minutes) if needed (not implemented initially)

**Error Handling**:
- Auth service unavailable → Backend returns 503 Service Unavailable
- Invalid token → Backend returns 401 Unauthorized
- Network timeout → Backend returns 503 with retry-after header

### 6. Testing Strategy

**Decision**: Implement contract tests and integration tests

**Test Types**:

1. **Contract Tests** (auth-service):
   - Session endpoint returns correct user data for valid token
   - Session endpoint returns 401 for invalid token
   - Session endpoint returns 401 for missing Authorization header
   - Sign-up returns 400 with specific message for short password
   - Sign-up returns 400 with specific message for invalid email
   - Sign-up returns 409 for duplicate email
   - Sign-up returns 201 with token for valid input

2. **Integration Tests** (backend):
   - Token validation succeeds for valid Better Auth token
   - Token validation fails for expired token
   - Backend correctly extracts user ID from session response
   - Backend handles auth service unavailability gracefully

3. **Manual Testing**:
   - Use provided test script in API_TESTING.md
   - Verify error messages are user-friendly
   - Check CORS headers in browser

**Testing Tools**:
- Vitest (auth-service unit/integration tests)
- Pytest (backend unit/integration tests)
- curl/httpx for manual API testing

## Technology Stack Confirmation

### Auth Service
- **Runtime**: Node.js 22.x
- **Language**: TypeScript 5.7.2
- **Framework**: Hono 4.7.11 (lightweight, fast HTTP framework)
- **Auth Library**: Better Auth 1.0.9 (comprehensive auth solution)
- **Database ORM**: Drizzle 0.41.0
- **Database**: PostgreSQL 16+
- **Testing**: Vitest 2.1.8

### Backend Service
- **Runtime**: Python 3.11+
- **Framework**: FastAPI 0.104.1
- **Database**: PostgreSQL via SQLModel 0.0.14
- **Testing**: Pytest 7.4.3
- **HTTP Client**: httpx 0.25.2 (for calling auth service)

## Open Questions Resolved

1. **Q: Does Better Auth support Bearer token authentication?**
   A: Yes, via the `bearer()` plugin already configured

2. **Q: Can we customize error responses without forking Better Auth?**
   A: Yes, via middleware that intercepts and transforms error responses

3. **Q: How should backend validate tokens?**
   A: Call auth service session endpoint - it's the authoritative source

4. **Q: What HTTP status code for duplicate email?**
   A: 409 Conflict (not 400) to distinguish from validation errors

5. **Q: Should we implement token caching in backend?**
   A: Not initially - JWT validation is fast enough; can add later if needed

## Next Steps

Phase 1 will use these research findings to:
1. Define data model for session and validation error responses
2. Create API contracts (OpenAPI specs) for session and sign-up endpoints
3. Document implementation quickstart guide
4. Generate task breakdown for implementation

## References

- Better Auth Documentation: https://better-auth.com
- Hono Framework: https://hono.dev
- FastAPI Documentation: https://fastapi.tiangolo.com
- RFC 7231 (HTTP Status Codes): https://tools.ietf.org/html/rfc7231
- JWT Best Practices: RFC 8725
