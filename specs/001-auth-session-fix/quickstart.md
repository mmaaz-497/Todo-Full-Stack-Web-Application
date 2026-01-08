# Quickstart: Authentication Session & Sign-Up Validation Implementation

**Feature**: 001-auth-session-fix
**Date**: 2025-12-23
**Audience**: Developers implementing the session endpoint and validation improvements

## Overview

This guide provides step-by-step instructions for implementing the authentication session endpoint and sign-up validation improvements. The implementation touches two services:

1. **Auth Service** (Node.js/TypeScript): Add validation error handling middleware
2. **Backend Service** (Python/FastAPI): Already implements token validation (no changes needed)

## Prerequisites

- Auth service running on http://localhost:3001
- PostgreSQL database configured and migrated
- Environment variables set (see `.env.example` in auth-service)
- Node.js 22.x and Python 3.11+ installed

## Implementation Steps

### Step 1: Verify Better Auth Session Endpoint

The session endpoint already exists via Better Auth. Verify it's working:

```bash
# Sign in first to get a token
curl -X POST http://localhost:3001/api/auth/signin/email \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Extract token from response and test session endpoint
TOKEN="<token from signin response>"
curl -X GET http://localhost:3001/api/auth/session \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response** (200 OK):
```json
{
  "user": {
    "id": "uuid-here",
    "email": "test@example.com",
    "name": "Test User",
    "emailVerified": false
  }
}
```

If this works, the session endpoint is already functional. Skip to Step 2.

If it returns 404, check:
- Better Auth is properly initialized in `auth-service/src/lib/auth.ts`
- Route handler is registered in `auth-service/src/index.ts`
- Bearer plugin is enabled

### Step 2: Create Validation Error Handler Middleware

Create `auth-service/src/middleware/validation-errors.ts`:

```typescript
import { Context, MiddlewareHandler } from 'hono';

/**
 * Middleware to transform Better Auth validation errors into specific,
 * actionable error messages for users.
 */
export const validationErrorHandler = (): MiddlewareHandler => {
  return async (c: Context, next) => {
    await next();

    // Only intercept error responses
    if (c.res.status >= 400) {
      const body = await c.res.clone().json().catch(() => null);

      if (!body) return;

      // Transform generic Better Auth errors into specific messages
      const transformedError = transformValidationError(c.res.status, body);

      if (transformedError) {
        return c.json(transformedError, c.res.status as any);
      }
    }
  };
};

/**
 * Transform error based on status code and error content
 */
function transformValidationError(
  status: number,
  body: any
): { error: string } | null {
  const errorMessage = body.error || body.message || '';

  // Password validation errors (400)
  if (status === 400) {
    if (errorMessage.includes('password') && errorMessage.includes('short')) {
      return { error: 'Password must be at least 8 characters long' };
    }
    if (errorMessage.includes('password') && errorMessage.includes('long')) {
      return { error: 'Password must not exceed 128 characters' };
    }
    if (errorMessage.includes('email') && errorMessage.includes('invalid')) {
      return { error: 'Invalid email address format' };
    }
    if (errorMessage.includes('email') && errorMessage.includes('required')) {
      return { error: 'Email is required' };
    }
    if (errorMessage.includes('password') && errorMessage.includes('required')) {
      return { error: 'Password is required' };
    }
  }

  // Duplicate email error (should be 409, might come as 400)
  if (errorMessage.includes('unique') || errorMessage.includes('duplicate') ||
      errorMessage.includes('already exists')) {
    // Change status to 409 for duplicate email
    return { error: 'An account with this email already exists' };
  }

  // Authentication errors (401)
  if (status === 401) {
    if (!errorMessage || errorMessage.includes('token') || errorMessage.includes('auth')) {
      return { error: 'Invalid or expired token' };
    }
    if (errorMessage.includes('authorization')) {
      return { error: 'Authorization header is required' };
    }
  }

  // Return null to use original error
  return null;
}
```

### Step 3: Register Validation Middleware

Update `auth-service/src/index.ts` to add validation error handler:

```typescript
import { validationErrorHandler } from './middleware/validation-errors';

// Add after existing middleware, before auth routes
app.use('/api/auth/*', validationErrorHandler());
```

**Important**: Place this middleware BEFORE the auth.handler() route so it can intercept responses.

### Step 4: Test Sign-Up Validation

Test all validation error scenarios:

```bash
# Test 1: Password too short (expect 400 with specific message)
curl -X POST http://localhost:3001/api/auth/signup/email \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"short"}'

# Expected: {"error":"Password must be at least 8 characters long"}

# Test 2: Invalid email format (expect 400)
curl -X POST http://localhost:3001/api/auth/signup/email \
  -H "Content-Type: application/json" \
  -d '{"email":"notanemail","password":"validpass123"}'

# Expected: {"error":"Invalid email address format"}

# Test 3: Duplicate email (expect 409)
# First create user:
curl -X POST http://localhost:3001/api/auth/signup/email \
  -H "Content-Type: application/json" \
  -d '{"email":"duplicate@example.com","password":"password123"}'

# Then try again with same email:
curl -X POST http://localhost:3001/api/auth/signup/email \
  -H "Content-Type: application/json" \
  -d '{"email":"duplicate@example.com","password":"password123"}'

# Expected: {"error":"An account with this email already exists"}

# Test 4: Valid sign-up (expect 201)
curl -X POST http://localhost:3001/api/auth/signup/email \
  -H "Content-Type: application/json" \
  -d '{"email":"newuser@example.com","password":"validpass123","name":"New User"}'

# Expected: {"token":"...","user":{"id":"...","email":"newuser@example.com",...}}
```

### Step 5: Test Session Endpoint (Backend Integration)

The backend already has token validation implemented in `backend/auth.py`. Test the integration:

```bash
# Get a valid token
TOKEN=$(curl -X POST http://localhost:3001/api/auth/signin/email \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}' \
  | jq -r '.token')

# Test backend endpoint with token
curl -X GET http://localhost:8000/api/{user_id}/tasks \
  -H "Authorization: Bearer $TOKEN"
```

The backend's `verify_better_auth_session()` function will call the auth service session endpoint automatically.

### Step 6: Verify Error Responses

Test error scenarios:

```bash
# Test expired/invalid token
curl -X GET http://localhost:3001/api/auth/session \
  -H "Authorization: Bearer invalid_token_here"

# Expected: {"error":"Invalid or expired token"}

# Test missing Authorization header
curl -X GET http://localhost:3001/api/auth/session

# Expected: {"error":"Authorization header is required"}
```

## Configuration

### Environment Variables

Ensure these are set in `auth-service/.env`:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Better Auth
BETTER_AUTH_SECRET=your-secret-key-here  # Min 32 characters
BETTER_AUTH_URL=http://localhost:3001

# Session
SESSION_EXPIRES_IN=604800  # 7 days in seconds

# CORS (optional)
CORS_ORIGINS=http://localhost:3000

# Environment
NODE_ENV=development
```

### Rate Limiting

Rate limits are already configured in `auth-service/src/index.ts`:
- Sign-up: 5 requests/minute per IP
- Session: 30 requests/minute per IP

No changes needed unless requirements change.

## Testing Checklist

- [ ] Session endpoint returns 200 with user data for valid token
- [ ] Session endpoint returns 401 for invalid token
- [ ] Session endpoint returns 401 for missing Authorization header
- [ ] Sign-up returns 400 with "Password must be at least 8 characters long" for short password
- [ ] Sign-up returns 400 with "Password must not exceed 128 characters" for long password
- [ ] Sign-up returns 400 with "Invalid email address format" for invalid email
- [ ] Sign-up returns 409 with "An account with this email already exists" for duplicate email
- [ ] Sign-up returns 201 with token and user data for valid input
- [ ] Backend can validate tokens by calling session endpoint
- [ ] Rate limiting returns 429 after limit exceeded
- [ ] CORS headers present in responses

## Troubleshooting

### Session Endpoint Returns 404

**Problem**: GET /api/auth/session returns 404 Not Found

**Solutions**:
1. Verify Better Auth handler is registered: Check `auth-service/src/index.ts` has `app.use('/api/auth/*', auth.handler)`
2. Verify Bearer plugin is enabled: Check `auth-service/src/lib/auth.ts` has `bearer()` in plugins array
3. Check route order: Ensure auth routes are registered before 404 handler

### Validation Errors Not Specific

**Problem**: Sign-up returns generic errors instead of specific messages

**Solutions**:
1. Verify validation middleware is registered before auth handler
2. Check middleware is on correct route: `/api/auth/*`
3. Add console.log in transformValidationError() to debug error matching
4. Ensure Better Auth version is 1.0.9+ (check package.json)

### Backend Can't Validate Tokens

**Problem**: Backend returns "Auth service unavailable"

**Solutions**:
1. Verify auth service is running on port 3001
2. Check BETTER_AUTH_URL environment variable in backend
3. Test session endpoint directly with curl to verify it works
4. Check network connectivity between services

### Duplicate Email Returns 400 Instead of 409

**Problem**: Duplicate email errors return 400 status code

**Solutions**:
1. Update validation middleware to detect duplicate email errors
2. Modify transformValidationError() to return proper status
3. May need to catch database UNIQUE constraint errors explicitly

## Next Steps

After implementation:
1. Run integration tests: `npm test` in auth-service
2. Run backend tests: `pytest` in backend directory
3. Update API documentation if response formats changed
4. Deploy to staging environment for QA testing
5. Monitor error rates and response times in production

## Reference Files

- Feature Spec: `specs/001-auth-session-fix/spec.md`
- Data Model: `specs/001-auth-session-fix/data-model.md`
- API Contracts: `specs/001-auth-session-fix/contracts/*.openapi.yaml`
- Backend Auth Logic: `backend/auth.py`
- Auth Service Routes: `auth-service/src/index.ts`
- Better Auth Config: `auth-service/src/lib/auth.ts`
