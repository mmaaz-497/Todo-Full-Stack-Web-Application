# Phase II: Todo Full-Stack Web Application - Task Breakdown

**Project**: Todo Full-Stack Web Application
**Phase**: II - Web Application with Authentication
**Tasks Version**: 1.0.0
**Date**: 2025-12-19
**Based on**: Specification v1.0.0, Plan v1.0.0, Constitution v1.3.0
**Status**: Ready for Implementation

---

## Task Overview

**Total Tasks**: 95 atomic tasks
**Task Categories**: 7 categories
**Critical Path Length**: ~95 tasks (sequential dependencies)
**Parallel Opportunities**: Limited (frontend design during backend dev)

---

## 1. Environment & Project Setup Tasks

### Task T-001: Provision Neon PostgreSQL Database

**Purpose**: Create cloud PostgreSQL database for application data storage.

**Inputs**:
- Neon account credentials
- Internet connectivity

**Outputs**:
- Neon PostgreSQL database instance
- `DATABASE_URL` connection string in format: `postgresql://user:password@host/database?sslmode=require`

**Validation Criteria**:
- ✅ Database appears in Neon dashboard
- ✅ Connection string obtained and copied
- ✅ Test connection successful using `psql` or database client

**Dependencies**: None

**Failure Considerations**:
- Account creation fails → Create new account or contact Neon support
- Connection string not generated → Refresh dashboard or recreate database

---

### Task T-002: Generate BETTER_AUTH_SECRET

**Purpose**: Create shared secret for JWT token signing and verification between auth-service and backend.

**Inputs**:
- OpenSSL command-line tool or equivalent

**Outputs**:
- 64-character hexadecimal secret string

**Validation Criteria**:
- ✅ Secret is exactly 64 hex characters (32 bytes)
- ✅ Secret generated using cryptographically secure method
- ✅ Secret copied to secure temporary location (not committed to git)

**Command**:
```bash
openssl rand -hex 32
```

**Dependencies**: None

**Failure Considerations**:
- OpenSSL not installed → Install OpenSSL or use online secure random generator
- Weak secret generated → Regenerate using proper tool

---

### Task T-003: Customize Better Auth Schema (Remove Custom Fields from schema.ts)

**Purpose**: Remove Physical AI Humanoid Robotics project custom fields from Better Auth database schema to match Todo app requirements.

**Inputs**:
- Better Auth service codebase at `/auth-service`
- File: `auth-service/src/db/schema.ts`

**Outputs**:
- Modified `schema.ts` with custom fields removed
- User table contains only: `id`, `email`, `name`, `emailVerified`, `image`, `createdAt`, `updatedAt`

**Validation Criteria**:
- ✅ Lines 3-9 removed: `experienceLevels` and `professionalRoles` enum definitions
- ✅ Lines 21-25 removed from `user` table: `experienceLevel`, `professionalRole`, `roleOther`, `organization` fields
- ✅ User table has exactly 7 columns
- ✅ File saves without syntax errors

**Dependencies**: None

**Failure Considerations**:
- Line numbers don't match → Search for field names and remove manually
- Syntax errors after removal → Check for trailing commas, missing closing braces

---

### Task T-004: Customize Better Auth Configuration (Remove additionalFields from auth.ts)

**Purpose**: Remove custom user fields from Better Auth configuration to align with simplified schema.

**Inputs**:
- File: `auth-service/src/lib/auth.ts`

**Outputs**:
- Modified `auth.ts` with `user.additionalFields` section removed

**Validation Criteria**:
- ✅ Lines 18-44 removed: Entire `user.additionalFields` object
- ✅ Better Auth configuration valid (no syntax errors)
- ✅ File saves successfully

**Dependencies**: T-003 (schema customization must be done first for consistency)

**Failure Considerations**:
- Line numbers don't match → Search for `additionalFields` and remove entire block
- Configuration errors → Verify Better Auth documentation for correct structure

---

### Task T-005: Create Auth Service Environment File

**Purpose**: Configure auth-service environment variables for database connection and JWT secret.

**Inputs**:
- `DATABASE_URL` from T-001
- `BETTER_AUTH_SECRET` from T-002
- Auth service directory at `/auth-service`

**Outputs**:
- File: `auth-service/.env` with configuration:
  ```env
  DATABASE_URL=postgresql://...
  BETTER_AUTH_SECRET=<64-char-secret>
  CORS_ORIGINS=http://localhost:3000,http://localhost:8000
  SESSION_EXPIRES_IN=7d
  NODE_ENV=development
  PORT=3001
  ```

**Validation Criteria**:
- ✅ `.env` file exists in `auth-service/` directory
- ✅ All required variables present
- ✅ `DATABASE_URL` matches Neon connection string
- ✅ `BETTER_AUTH_SECRET` matches value from T-002
- ✅ File NOT committed to git (listed in `.gitignore`)

**Dependencies**: T-001, T-002

**Failure Considerations**:
- Typo in variable names → Check Better Auth documentation for exact names
- Secret exposed in git → Verify `.gitignore` includes `.env`

---

### Task T-006: Install Auth Service Dependencies

**Purpose**: Install Node.js dependencies for Better Auth service.

**Inputs**:
- Auth service directory with `package.json`
- Node.js 18+ installed

**Outputs**:
- `node_modules/` directory populated
- `package-lock.json` generated

**Validation Criteria**:
- ✅ `npm install` completes without errors
- ✅ All dependencies installed (Better Auth, Hono, Drizzle ORM, etc.)
- ✅ No security vulnerabilities reported (or documented if present)

**Command**:
```bash
cd auth-service
npm install
```

**Dependencies**: None

**Failure Considerations**:
- npm install fails → Check Node.js version, clear npm cache, retry
- Dependency conflicts → Update package.json versions as needed

---

### Task T-007: Generate and Apply Auth Service Database Migrations

**Purpose**: Create database tables for Better Auth (users, session, account, verification) with customized schema.

**Inputs**:
- Modified `schema.ts` from T-003
- Modified `auth.ts` from T-004
- `.env` file from T-005
- Dependencies installed from T-006

**Outputs**:
- Drizzle migration files in `auth-service/migrations/`
- Database tables created in Neon PostgreSQL

**Validation Criteria**:
- ✅ `npm run migrate` completes without errors
- ✅ `npm run migrate:push` applies migrations successfully
- ✅ Neon dashboard shows tables: `users`, `session`, `account`, `verification`
- ✅ `users` table has 7 columns (no custom fields)

**Commands**:
```bash
cd auth-service
npm run migrate
npm run migrate:push
```

**Dependencies**: T-003, T-004, T-005, T-006

**Failure Considerations**:
- Migration generation fails → Check schema.ts syntax, fix errors
- Migration push fails → Verify DATABASE_URL correct, check network connection
- Tables already exist → Drop tables or use fresh database

---

### Task T-008: Start and Verify Auth Service

**Purpose**: Ensure auth-service starts successfully and health check endpoint responds.

**Inputs**:
- Migrations applied from T-007
- `.env` configured from T-005

**Outputs**:
- Auth service running on port 3001
- Health check endpoint accessible

**Validation Criteria**:
- ✅ `npm run dev` starts without errors
- ✅ Logs show "Server running on port 3001" or similar
- ✅ `GET http://localhost:3001/health` returns 200 OK
- ✅ No database connection errors in logs

**Command**:
```bash
cd auth-service
npm run dev
```

**Dependencies**: T-007

**Failure Considerations**:
- Port 3001 already in use → Kill existing process or change port
- Database connection fails → Verify DATABASE_URL, check network
- Auth service crashes on startup → Check logs for specific error

---

### Task T-009: Create Backend Project Directory Structure

**Purpose**: Initialize backend project folder hierarchy for FastAPI application.

**Inputs**:
- Project root directory

**Outputs**:
- Directory structure:
  ```
  backend/
  ├── main.py
  ├── models.py
  ├── db.py
  ├── auth.py
  ├── routes/
  │   ├── __init__.py
  │   ├── tasks.py
  │   └── health.py
  ├── tests/
  │   ├── __init__.py
  │   ├── test_models.py
  │   ├── test_auth_middleware.py
  │   └── test_routes_tasks.py
  ├── .env
  ├── .env.example
  ├── requirements.txt
  └── README.md
  ```

**Validation Criteria**:
- ✅ All directories created
- ✅ `__init__.py` files present in package directories
- ✅ Structure matches plan specification

**Dependencies**: None

**Failure Considerations**:
- None (simple directory creation)

---

### Task T-010: Create Backend Environment File

**Purpose**: Configure backend environment variables for database connection and JWT verification.

**Inputs**:
- `DATABASE_URL` from T-001
- `BETTER_AUTH_SECRET` from T-002

**Outputs**:
- File: `backend/.env` with configuration:
  ```env
  DATABASE_URL=postgresql://...
  BETTER_AUTH_SECRET=<64-char-secret>
  CORS_ORIGINS=http://localhost:3000
  ENVIRONMENT=development
  ```

**Validation Criteria**:
- ✅ `.env` file exists in `backend/` directory
- ✅ `DATABASE_URL` matches Neon connection string (same as auth-service)
- ✅ `BETTER_AUTH_SECRET` exactly matches auth-service secret
- ✅ File NOT committed to git

**Dependencies**: T-001, T-002

**Failure Considerations**:
- Secret mismatch → Verify both services use identical BETTER_AUTH_SECRET
- Wrong DATABASE_URL → Copy exact string from Neon dashboard

---

### Task T-011: Create Backend Environment Example File

**Purpose**: Provide template for environment variables without exposing secrets.

**Inputs**:
- `.env` file structure from T-010

**Outputs**:
- File: `backend/.env.example` with placeholder values:
  ```env
  DATABASE_URL=postgresql://user:password@host/database?sslmode=require
  BETTER_AUTH_SECRET=your-64-char-hex-secret-here
  CORS_ORIGINS=http://localhost:3000
  ENVIRONMENT=development
  ```

**Validation Criteria**:
- ✅ `.env.example` file exists
- ✅ No actual secrets present (only placeholders)
- ✅ File can be committed to git safely

**Dependencies**: T-010

**Failure Considerations**:
- Accidentally include real secrets → Replace with placeholders before commit

---

### Task T-012: Create Backend Requirements File

**Purpose**: Define Python dependencies for FastAPI backend.

**Inputs**:
- Backend project structure from T-009

**Outputs**:
- File: `backend/requirements.txt` with dependencies:
  ```
  fastapi==0.104.1
  uvicorn[standard]==0.24.0
  sqlmodel==0.0.14
  psycopg2-binary==2.9.9
  python-jose[cryptography]==3.3.0
  pydantic==2.5.0
  python-dotenv==1.0.0
  pytest==7.4.3
  pytest-cov==4.1.0
  httpx==0.25.2
  ```

**Validation Criteria**:
- ✅ `requirements.txt` file exists
- ✅ All required dependencies listed with versions
- ✅ No missing critical dependencies

**Dependencies**: T-009

**Failure Considerations**:
- Version conflicts → Update versions to compatible set
- Missing dependency → Add to list before installation

---

### Task T-013: Install Backend Python Dependencies

**Purpose**: Install Python packages required for FastAPI backend using UV package manager.

**Inputs**:
- `requirements.txt` from T-012
- UV package manager installed
- Python 3.13+ installed

**Outputs**:
- Python packages installed in virtual environment or global environment

**Validation Criteria**:
- ✅ `uv pip install -r requirements.txt` completes without errors
- ✅ All packages installed successfully
- ✅ `python -m fastapi --version` shows FastAPI installed

**Command**:
```bash
cd backend
uv pip install -r requirements.txt
```

**Dependencies**: T-012

**Failure Considerations**:
- UV not installed → Install UV first or use `pip install -r requirements.txt`
- Package installation fails → Check Python version, update pip, retry
- Dependency conflicts → Resolve version incompatibilities

---

### Task T-014: Create Frontend Project with Next.js

**Purpose**: Initialize Next.js 16+ project with TypeScript and Tailwind CSS.

**Inputs**:
- Node.js 18+ installed
- Project root directory

**Outputs**:
- Frontend project at `/frontend` with Next.js App Router structure

**Validation Criteria**:
- ✅ `npx create-next-app@latest frontend --typescript --tailwind --app` completes successfully
- ✅ App Router enabled (not Pages Router)
- ✅ TypeScript configured
- ✅ Tailwind CSS configured
- ✅ Project structure includes `app/` directory

**Command**:
```bash
npx create-next-app@latest frontend --typescript --tailwind --app --no-src-dir --import-alias "@/*"
```

**Dependencies**: None

**Failure Considerations**:
- Next.js version < 16 → Update to latest stable version
- TypeScript not configured → Manually add tsconfig.json
- Pages Router created instead → Delete project and recreate with --app flag

---

### Task T-015: Install Frontend Dependencies

**Purpose**: Install additional frontend dependencies for API client, authentication, and validation.

**Inputs**:
- Frontend project from T-014
- `package.json` in frontend directory

**Outputs**:
- Additional packages installed:
  - `better-auth` (Better Auth client)
  - `axios` (HTTP client)
  - `zod` (schema validation)

**Validation Criteria**:
- ✅ `npm install better-auth axios zod` completes without errors
- ✅ Packages appear in `package.json` dependencies
- ✅ `node_modules/` updated with new packages

**Command**:
```bash
cd frontend
npm install better-auth axios zod
```

**Dependencies**: T-014

**Failure Considerations**:
- Installation fails → Check npm registry connectivity, retry
- Version conflicts → Update package.json to compatible versions

---

### Task T-016: Create Frontend Environment File

**Purpose**: Configure frontend environment variables for API endpoints.

**Inputs**:
- Auth service running on port 3001
- Backend API will run on port 8000 (planned)

**Outputs**:
- File: `frontend/.env.local` with configuration:
  ```env
  NEXT_PUBLIC_AUTH_URL=http://localhost:3001
  NEXT_PUBLIC_API_URL=http://localhost:8000
  ```

**Validation Criteria**:
- ✅ `.env.local` file exists in `frontend/` directory
- ✅ Both URLs correct for local development
- ✅ File NOT committed to git (Next.js .gitignore includes .env.local by default)

**Dependencies**: None

**Failure Considerations**:
- Wrong URLs → Verify port numbers match service configurations
- File committed to git → Check .gitignore

---

### Task T-017: Create Frontend Environment Example File

**Purpose**: Provide template for frontend environment variables.

**Inputs**:
- `.env.local` structure from T-016

**Outputs**:
- File: `frontend/.env.example` with placeholder values:
  ```env
  NEXT_PUBLIC_AUTH_URL=http://localhost:3001
  NEXT_PUBLIC_API_URL=http://localhost:8000
  ```

**Validation Criteria**:
- ✅ `.env.example` file exists
- ✅ Values represent development defaults
- ✅ File can be committed to git safely

**Dependencies**: T-016

**Failure Considerations**:
- None (simple file creation)

---

## 2. Core Logic Tasks - Backend

### Task T-018: Implement Database Connection Module (db.py)

**Purpose**: Create database engine and session management for SQLModel ORM.

**Inputs**:
- `DATABASE_URL` from environment (.env file)
- SQLModel and psycopg2 installed from T-013

**Outputs**:
- File: `backend/db.py` with:
  - Database engine creation
  - Session factory (dependency injection)
  - Connection pool configuration

**Validation Criteria**:
- ✅ `create_engine()` uses DATABASE_URL from environment
- ✅ Connection pooling configured (pool_size, max_overflow)
- ✅ `get_session()` function provides database sessions
- ✅ File imports without errors

**Test Coverage**:
- Database connection succeeds with valid URL
- Connection fails gracefully with invalid URL

**Dependencies**: T-010, T-013

**Failure Considerations**:
- Import errors → Verify SQLModel installed correctly
- Connection fails → Check DATABASE_URL format, network connectivity
- Pool configuration wrong → Adjust based on Neon limits

---

### Task T-019: Implement Task Database Model (models.py)

**Purpose**: Define SQLModel Task entity with validation constraints.

**Inputs**:
- SQLModel installed from T-013
- Database schema from specification (Section 5.1)

**Outputs**:
- File: `backend/models.py` with `Task` model:
  - Fields: `id`, `user_id`, `title`, `description`, `completed`, `created_at`, `updated_at`
  - Field validation: title 1-200 chars, description max 1000 chars
  - Foreign key: `user_id` references `users.id`

**Validation Criteria**:
- ✅ Task model inherits from `SQLModel, table=True`
- ✅ All fields have correct types and constraints
- ✅ `created_at` and `updated_at` auto-generate timestamps
- ✅ Model can be imported without errors

**Test Coverage**:
- Task model instantiation succeeds with valid data
- Empty title raises validation error
- Title >200 chars raises validation error
- Description >1000 chars raises validation error

**Dependencies**: T-013

**Failure Considerations**:
- Validation not enforced → Add Pydantic validators
- Foreign key constraint missing → Add relationship configuration

---

### Task T-020: Implement JWT Verification Middleware (auth.py)

**Purpose**: Create middleware to verify JWT tokens and extract user_id claim.

**Inputs**:
- `BETTER_AUTH_SECRET` from environment
- python-jose installed from T-013

**Outputs**:
- File: `backend/auth.py` with:
  - `verify_jwt_token()` function: Decodes and validates JWT signature
  - `get_current_user()` dependency: Extracts user_id from token
  - `verify_user_id_match()` function: Compares token user_id with path parameter

**Validation Criteria**:
- ✅ Token verification uses HS256 algorithm with BETTER_AUTH_SECRET
- ✅ Expired tokens raise HTTPException 401
- ✅ Invalid signatures raise HTTPException 401
- ✅ Missing user_id claim raises HTTPException 401
- ✅ User ID mismatch raises HTTPException 403

**Test Coverage**:
- Valid token decodes successfully
- Expired token rejected
- Tampered token rejected
- Token without user_id rejected
- Path user_id mismatch returns 403

**Dependencies**: T-010, T-013

**Failure Considerations**:
- Wrong algorithm → Verify Better Auth uses HS256
- Secret mismatch → Ensure BETTER_AUTH_SECRET matches auth-service
- Token structure unknown → Check Better Auth JWT payload format

---

### Task T-021: Implement FastAPI Application Skeleton (main.py)

**Purpose**: Create FastAPI application instance with CORS middleware and router registration.

**Inputs**:
- FastAPI installed from T-013
- `db.py` from T-018
- CORS_ORIGINS from environment

**Outputs**:
- File: `backend/main.py` with:
  - FastAPI app instance
  - CORS middleware configured with explicit origins
  - Startup event: Create database tables via SQLModel
  - Router registration (tasks, health)

**Validation Criteria**:
- ✅ FastAPI app created with title, version, docs_url
- ✅ CORS middleware allows origins from CORS_ORIGINS env var
- ✅ Startup event calls `SQLModel.metadata.create_all(engine)`
- ✅ Application starts without errors

**Test Coverage**:
- App startup succeeds
- CORS headers present in responses
- Database tables created on startup

**Dependencies**: T-010, T-013, T-018

**Failure Considerations**:
- CORS not configured → Frontend API calls blocked by browser
- Tables not created → Check database connection, verify models imported
- App startup fails → Check logs for specific error

---

### Task T-022: Implement Health Check Endpoint (routes/health.py)

**Purpose**: Provide health check endpoint for monitoring and deployment verification.

**Inputs**:
- FastAPI app from T-021
- Database session from T-018

**Outputs**:
- File: `backend/routes/health.py` with:
  - `GET /health` endpoint
  - Database connectivity check
  - Response: `{ "status": "healthy", "database": "connected" }`

**Validation Criteria**:
- ✅ Endpoint responds with 200 OK when database connected
- ✅ Endpoint responds with 503 Service Unavailable when database down
- ✅ Response includes status and database fields

**Test Coverage**:
- Health check succeeds with database up
- Health check fails gracefully with database down

**Dependencies**: T-018, T-021

**Failure Considerations**:
- Database check too slow → Add timeout to database ping
- Endpoint not registered → Verify router added to main.py

---

### Task T-023: Implement Pydantic Request/Response Models for Tasks

**Purpose**: Define request and response schemas for task API endpoints.

**Inputs**:
- Pydantic installed from T-013
- API specifications from spec (Section 6.1)

**Outputs**:
- File: `backend/routes/tasks.py` (partial) with Pydantic models:
  - `TaskCreate`: title (str), description (str | None)
  - `TaskUpdate`: title (str | None), description (str | None)
  - `TaskResponse`: All task fields including id, user_id, timestamps

**Validation Criteria**:
- ✅ TaskCreate validates title 1-200 chars, description max 1000 chars
- ✅ TaskUpdate allows partial updates (both fields optional)
- ✅ TaskResponse includes all database fields
- ✅ Models use Pydantic validators for string length

**Test Coverage**:
- TaskCreate with valid data passes validation
- TaskCreate with empty title fails validation
- TaskUpdate with only title passes validation

**Dependencies**: T-013

**Failure Considerations**:
- Validation not enforced → Add Field() constraints
- Response model missing fields → Include all Task entity fields

---

### Task T-024: Implement Create Task Endpoint (POST /api/{user_id}/tasks)

**Purpose**: Allow authenticated users to create new tasks.

**Inputs**:
- FastAPI app from T-021
- Task model from T-019
- JWT middleware from T-020
- Pydantic models from T-023
- Database session from T-018

**Outputs**:
- Endpoint: `POST /api/{user_id}/tasks`
- Handler function in `backend/routes/tasks.py`

**Validation Criteria**:
- ✅ Endpoint requires valid JWT token (Authorization header)
- ✅ Verifies token user_id matches path {user_id}
- ✅ Validates request body via TaskCreate model
- ✅ Creates Task in database with user_id from token
- ✅ Returns 201 Created with task object
- ✅ Returns 400 Bad Request for invalid data
- ✅ Returns 401 Unauthorized for missing/invalid token
- ✅ Returns 403 Forbidden for user_id mismatch

**Test Coverage**:
- Authenticated user creates task successfully
- Empty title returns 400
- Title >200 chars returns 400
- Missing token returns 401
- Token user_id mismatch returns 403

**Dependencies**: T-018, T-019, T-020, T-021, T-023

**Failure Considerations**:
- Database insert fails → Return 500 with generic error, log details
- Ownership not enforced → Verify user_id set from token, not request body

---

### Task T-025: Implement List Tasks Endpoint (GET /api/{user_id}/tasks)

**Purpose**: Allow authenticated users to retrieve all their tasks.

**Inputs**:
- FastAPI app from T-021
- Task model from T-019
- JWT middleware from T-020
- Database session from T-018

**Outputs**:
- Endpoint: `GET /api/{user_id}/tasks`
- Handler function in `backend/routes/tasks.py`

**Validation Criteria**:
- ✅ Endpoint requires valid JWT token
- ✅ Verifies token user_id matches path {user_id}
- ✅ Queries database: `SELECT * FROM tasks WHERE user_id = ?`
- ✅ Returns 200 OK with JSON array of tasks
- ✅ Returns empty array `[]` for user with no tasks
- ✅ Returns 401 Unauthorized for missing/invalid token
- ✅ Returns 403 Forbidden for user_id mismatch

**Test Coverage**:
- User retrieves their own tasks
- User with no tasks receives empty array
- User A cannot see User B's tasks (query filtered by user_id)
- Missing token returns 401
- User_id mismatch returns 403

**Dependencies**: T-018, T-019, T-020, T-021

**Failure Considerations**:
- Query not filtered → CRITICAL: Ensure WHERE user_id = ? present
- Database query fails → Return 500, log error

---

### Task T-026: Implement Get Single Task Endpoint (GET /api/{user_id}/tasks/{id})

**Purpose**: Allow authenticated users to retrieve a specific task by ID.

**Inputs**:
- FastAPI app from T-021
- Task model from T-019
- JWT middleware from T-020
- Database session from T-018

**Outputs**:
- Endpoint: `GET /api/{user_id}/tasks/{id}`
- Handler function in `backend/routes/tasks.py`

**Validation Criteria**:
- ✅ Endpoint requires valid JWT token
- ✅ Verifies token user_id matches path {user_id}
- ✅ Queries database: `SELECT * FROM tasks WHERE id = ? AND user_id = ?`
- ✅ Returns 200 OK with task object if found and owned by user
- ✅ Returns 404 Not Found if task doesn't exist
- ✅ Returns 403 Forbidden if task belongs to different user
- ✅ Returns 401 Unauthorized for missing/invalid token

**Test Coverage**:
- User retrieves their own task successfully
- Non-existent task returns 404
- User A cannot retrieve User B's task (returns 403)
- Missing token returns 401

**Dependencies**: T-018, T-019, T-020, T-021

**Failure Considerations**:
- Ownership check missing → CRITICAL: Verify user_id in WHERE clause
- 403 vs 404 distinction → Decide on security approach (spec suggests 403 for ownership)

---

### Task T-027: Implement Update Task Endpoint (PUT /api/{user_id}/tasks/{id})

**Purpose**: Allow authenticated users to update their task's title and description.

**Inputs**:
- FastAPI app from T-021
- Task model from T-019
- JWT middleware from T-020
- Pydantic TaskUpdate model from T-023
- Database session from T-018

**Outputs**:
- Endpoint: `PUT /api/{user_id}/tasks/{id}`
- Handler function in `backend/routes/tasks.py`

**Validation Criteria**:
- ✅ Endpoint requires valid JWT token
- ✅ Verifies token user_id matches path {user_id}
- ✅ Validates request body via TaskUpdate model
- ✅ Queries database to verify task exists and is owned by user
- ✅ Updates only provided fields (title, description)
- ✅ Sets `updated_at` to current timestamp
- ✅ Returns 200 OK with updated task object
- ✅ Returns 404 Not Found if task doesn't exist
- ✅ Returns 403 Forbidden if task belongs to different user
- ✅ Returns 400 Bad Request for invalid data
- ✅ Returns 401 Unauthorized for missing/invalid token

**Test Coverage**:
- User updates their own task title successfully
- User updates description only (partial update)
- User updates both title and description
- `updated_at` timestamp changes after update
- Non-existent task returns 404
- User A cannot update User B's task (returns 403)

**Dependencies**: T-018, T-019, T-020, T-021, T-023

**Failure Considerations**:
- Partial update not working → Verify only non-None fields updated
- `updated_at` not changing → Ensure timestamp updated in database operation

---

### Task T-028: Implement Delete Task Endpoint (DELETE /api/{user_id}/tasks/{id})

**Purpose**: Allow authenticated users to permanently delete their tasks.

**Inputs**:
- FastAPI app from T-021
- Task model from T-019
- JWT middleware from T-020
- Database session from T-018

**Outputs**:
- Endpoint: `DELETE /api/{user_id}/tasks/{id}`
- Handler function in `backend/routes/tasks.py`

**Validation Criteria**:
- ✅ Endpoint requires valid JWT token
- ✅ Verifies token user_id matches path {user_id}
- ✅ Queries database to verify task exists and is owned by user
- ✅ Deletes task from database
- ✅ Returns 204 No Content on successful deletion
- ✅ Returns 404 Not Found if task doesn't exist
- ✅ Returns 403 Forbidden if task belongs to different user
- ✅ Returns 401 Unauthorized for missing/invalid token

**Test Coverage**:
- User deletes their own task successfully
- Deleted task no longer appears in list
- Subsequent GET for deleted task returns 404
- Non-existent task returns 404
- User A cannot delete User B's task (returns 403)

**Dependencies**: T-018, T-019, T-020, T-021

**Failure Considerations**:
- Task not actually deleted → Verify DELETE SQL executed
- Ownership check missing → CRITICAL: Verify user_id in WHERE clause

---

### Task T-029: Implement Toggle Complete Endpoint (PATCH /api/{user_id}/tasks/{id}/complete)

**Purpose**: Allow authenticated users to toggle task completion status.

**Inputs**:
- FastAPI app from T-021
- Task model from T-019
- JWT middleware from T-020
- Database session from T-018

**Outputs**:
- Endpoint: `PATCH /api/{user_id}/tasks/{id}/complete`
- Handler function in `backend/routes/tasks.py`

**Validation Criteria**:
- ✅ Endpoint requires valid JWT token
- ✅ Verifies token user_id matches path {user_id}
- ✅ Queries database to verify task exists and is owned by user
- ✅ Toggles `completed` boolean (true → false or false → true)
- ✅ Sets `updated_at` to current timestamp
- ✅ Returns 200 OK with updated task object
- ✅ Returns 404 Not Found if task doesn't exist
- ✅ Returns 403 Forbidden if task belongs to different user
- ✅ Returns 401 Unauthorized for missing/invalid token

**Test Coverage**:
- User toggles task from incomplete to complete
- User toggles task from complete to incomplete
- `updated_at` timestamp changes after toggle
- Non-existent task returns 404
- User A cannot toggle User B's task (returns 403)

**Dependencies**: T-018, T-019, T-020, T-021

**Failure Considerations**:
- Toggle logic incorrect → Use `NOT completed` in SQL or fetch, flip, save
- `updated_at` not changing → Ensure timestamp updated

---

### Task T-030: Register Task Routes in Main Application

**Purpose**: Add task router to FastAPI application to make endpoints accessible.

**Inputs**:
- `main.py` from T-021
- Task routes from T-024 through T-029

**Outputs**:
- Updated `backend/main.py` with task router included

**Validation Criteria**:
- ✅ Task router imported in main.py
- ✅ Router registered with `app.include_router(tasks_router)`
- ✅ All 6 endpoints accessible at `/api/{user_id}/tasks` paths
- ✅ OpenAPI docs at `/docs` show all task endpoints

**Test Coverage**:
- All endpoints appear in OpenAPI schema
- Endpoints respond correctly (verified in subsequent tests)

**Dependencies**: T-021, T-024, T-025, T-026, T-027, T-028, T-029

**Failure Considerations**:
- Routes not accessible → Verify router registered with correct prefix
- OpenAPI docs missing endpoints → Check router tags and metadata

---

## 3. Core Logic Tasks - Frontend

### Task T-031: Implement Better Auth Client (lib/auth.ts)

**Purpose**: Create Better Auth client for signup, signin, and signout functionality.

**Inputs**:
- Better Auth client library from T-015
- `NEXT_PUBLIC_AUTH_URL` from T-016

**Outputs**:
- File: `frontend/lib/auth.ts` with:
  - Better Auth client initialization
  - `signup()` function: Creates new user account
  - `signin()` function: Authenticates existing user
  - `signout()` function: Ends user session
  - `getSession()` function: Retrieves current user session
  - Token storage in localStorage

**Validation Criteria**:
- ✅ Client configured with auth URL from environment
- ✅ All auth functions call corresponding Better Auth endpoints
- ✅ Tokens stored in localStorage with key `auth_token`
- ✅ Functions handle errors and return meaningful messages

**Test Coverage**:
- Signup with valid data succeeds
- Signup with duplicate email returns error
- Signin with correct credentials succeeds
- Signin with wrong credentials returns error
- Signout clears token from storage

**Dependencies**: T-015, T-016

**Failure Considerations**:
- Token not persisting → Verify localStorage API usage
- CORS errors → Ensure auth-service CORS_ORIGINS includes frontend URL

---

### Task T-032: Implement API Client (lib/api.ts)

**Purpose**: Create centralized API client for backend task operations with JWT token attachment.

**Inputs**:
- axios from T-015
- `NEXT_PUBLIC_API_URL` from T-016
- Auth token from localStorage (T-031)

**Outputs**:
- File: `frontend/lib/api.ts` with:
  - API client instance configured with base URL
  - Request interceptor: Attaches JWT token to Authorization header
  - Response interceptor: Handles errors (401 redirects to signin)
  - API methods:
    - `getTasks(userId: string): Promise<Task[]>`
    - `getTask(userId: string, id: number): Promise<Task>`
    - `createTask(userId: string, data: TaskCreate): Promise<Task>`
    - `updateTask(userId: string, id: number, data: TaskUpdate): Promise<Task>`
    - `deleteTask(userId: string, id: number): Promise<void>`
    - `toggleComplete(userId: string, id: number): Promise<Task>`

**Validation Criteria**:
- ✅ Base URL set to NEXT_PUBLIC_API_URL
- ✅ Authorization header includes `Bearer <token>`
- ✅ 401 responses trigger redirect to signin
- ✅ All API methods typed with TypeScript interfaces
- ✅ Errors handled gracefully with user-friendly messages

**Test Coverage**:
- API calls include Authorization header
- 401 response redirects to signin
- Network errors handled gracefully

**Dependencies**: T-015, T-016, T-031

**Failure Considerations**:
- Token not attached → Verify interceptor reads from localStorage
- CORS errors → Ensure backend CORS_ORIGINS includes frontend URL
- Type errors → Define Task, TaskCreate, TaskUpdate interfaces

---

### Task T-033: Implement Protected Route Middleware (middleware.ts)

**Purpose**: Redirect unauthenticated users to signin page when accessing protected routes.

**Inputs**:
- Next.js middleware capability
- Auth token from localStorage (T-031)

**Outputs**:
- File: `frontend/middleware.ts` with:
  - Route matcher for protected paths (`/tasks`)
  - Token verification logic
  - Redirect to `/signin` if no token present

**Validation Criteria**:
- ✅ Accessing `/tasks` without token redirects to `/signin`
- ✅ Accessing `/tasks` with token allows page to load
- ✅ Public routes (`/`, `/signin`, `/signup`) always accessible

**Test Coverage**:
- Unauthenticated access to /tasks redirects to /signin
- Authenticated access to /tasks proceeds
- Public pages accessible without token

**Dependencies**: T-031

**Failure Considerations**:
- Redirect loop → Ensure signin/signup pages not protected
- Token validation too strict → Allow expired tokens through (let API handle)

---

### Task T-034: Implement Root Layout (app/layout.tsx)

**Purpose**: Create root layout with navigation and metadata.

**Inputs**:
- Next.js App Router structure from T-014

**Outputs**:
- File: `frontend/app/layout.tsx` with:
  - HTML structure (html, body tags)
  - Metadata (title, description)
  - Navigation component (conditional based on auth state)

**Validation Criteria**:
- ✅ Layout wraps all pages
- ✅ Metadata includes app title "Todo App"
- ✅ Navigation shows "Sign Out" when authenticated
- ✅ Navigation shows "Sign In" / "Sign Up" when not authenticated

**Test Coverage**:
- Layout renders without errors
- Navigation reflects auth state correctly

**Dependencies**: T-014

**Failure Considerations**:
- Layout not applied → Verify file in correct location (app/layout.tsx)
- Metadata not displayed → Check Next.js metadata API usage

---

### Task T-035: Implement Navigation Component (components/Navigation.tsx)

**Purpose**: Create navigation header with auth-conditional links.

**Inputs**:
- Auth state from T-031
- Tailwind CSS from T-014

**Outputs**:
- File: `frontend/components/Navigation.tsx` with:
  - Header with app title
  - Conditional rendering:
    - Authenticated: "My Tasks" link, "Sign Out" button
    - Unauthenticated: "Sign In" / "Sign Up" links
  - Signout handler calls `signout()` from lib/auth.ts

**Validation Criteria**:
- ✅ Navigation displays at top of all pages
- ✅ Sign Out button triggers signout and redirects to home
- ✅ Sign In/Sign Up links navigate to respective pages
- ✅ Responsive design (mobile and desktop)

**Test Coverage**:
- Sign Out button clears token and redirects
- Links navigate correctly

**Dependencies**: T-014, T-031

**Failure Considerations**:
- Auth state not reactive → Use React state/context to track auth status
- Signout doesn't redirect → Call router.push('/') after signout

---

### Task T-036: Implement Signup Page (app/signup/page.tsx)

**Purpose**: Create user signup form with email/password fields.

**Inputs**:
- Better Auth client from T-031
- Tailwind CSS from T-014

**Outputs**:
- File: `frontend/app/signup/page.tsx` with:
  - Form fields: email, password, name (optional)
  - Client-side validation (email format, password min length)
  - Submit handler calls `signup()` from lib/auth.ts
  - Error message display
  - Success: redirect to `/tasks`

**Validation Criteria**:
- ✅ Form validates email format before submission
- ✅ Form validates password minimum 8 characters
- ✅ Successful signup stores token and redirects to /tasks
- ✅ Duplicate email displays error message
- ✅ Network errors handled gracefully

**Test Coverage**:
- Valid signup succeeds and redirects
- Invalid email shows error
- Weak password shows error
- Duplicate email shows error from backend

**Dependencies**: T-014, T-031

**Failure Considerations**:
- Form doesn't submit → Check event.preventDefault(), async handler
- Token not stored → Verify signup() saves token to localStorage
- Redirect doesn't work → Use Next.js router.push()

---

### Task T-037: Implement Signin Page (app/signin/page.tsx)

**Purpose**: Create user signin form with email/password fields.

**Inputs**:
- Better Auth client from T-031
- Tailwind CSS from T-014

**Outputs**:
- File: `frontend/app/signin/page.tsx` with:
  - Form fields: email, password
  - Client-side validation (email format)
  - Submit handler calls `signin()` from lib/auth.ts
  - Error message display
  - Success: redirect to `/tasks`

**Validation Criteria**:
- ✅ Form validates email format before submission
- ✅ Successful signin stores token and redirects to /tasks
- ✅ Incorrect credentials display error message
- ✅ Network errors handled gracefully
- ✅ Link to signup page for new users

**Test Coverage**:
- Valid signin succeeds and redirects
- Invalid credentials show error
- Network errors handled

**Dependencies**: T-014, T-031

**Failure Considerations**:
- Token not stored → Verify signin() saves token to localStorage
- Error message too specific → Use generic "Invalid email or password"

---

### Task T-038: Implement Task List Component (components/TaskList.tsx)

**Purpose**: Display array of tasks with filtering and rendering logic.

**Inputs**:
- Task array from parent component
- Tailwind CSS from T-014

**Outputs**:
- File: `frontend/components/TaskList.tsx` with:
  - Renders array of TaskItem components
  - Shows EmptyState when no tasks
  - Props: tasks, onUpdate, onDelete, onToggleComplete

**Validation Criteria**:
- ✅ Renders all tasks in array
- ✅ Shows EmptyState when array empty
- ✅ Passes callbacks to TaskItem components
- ✅ Responsive grid layout

**Test Coverage**:
- Renders tasks correctly
- Shows empty state when no tasks
- Callbacks triggered when child components call them

**Dependencies**: T-014

**Failure Considerations**:
- Tasks not rendering → Verify map() function correct, keys unique

---

### Task T-039: Implement Task Item Component (components/TaskItem.tsx)

**Purpose**: Display individual task with actions (edit, delete, toggle complete).

**Inputs**:
- Task object (id, title, description, completed, etc.)
- Callback functions (onUpdate, onDelete, onToggleComplete)
- Tailwind CSS from T-014

**Outputs**:
- File: `frontend/components/TaskItem.tsx` with:
  - Task title (strikethrough if completed)
  - Task description (if present)
  - Checkbox for completion status
  - Edit button (shows inline edit form)
  - Delete button (shows confirmation dialog)
  - Completion status indicator

**Validation Criteria**:
- ✅ Checkbox checked state reflects task.completed
- ✅ Checkbox onChange triggers onToggleComplete callback
- ✅ Edit button shows inline edit form
- ✅ Delete button shows confirmation before calling onDelete
- ✅ Strikethrough applied to completed tasks
- ✅ Accessible (keyboard navigation, ARIA labels)

**Test Coverage**:
- Checkbox toggle triggers callback
- Edit button shows edit form
- Delete button shows confirmation, then deletes

**Dependencies**: T-014

**Failure Considerations**:
- Checkbox state not synced → Use controlled component (checked={task.completed})
- Delete without confirmation → Add confirmation dialog

---

### Task T-040: Implement Task Form Component (components/TaskForm.tsx)

**Purpose**: Create/edit task form with validation.

**Inputs**:
- Optional existing task (for edit mode)
- Callback function (onSubmit)
- Tailwind CSS from T-014
- Zod validation from T-015

**Outputs**:
- File: `frontend/components/TaskForm.tsx` with:
  - Form fields: title (required), description (optional)
  - Client-side validation (Zod schema)
  - Character count display (title: 200 max, description: 1000 max)
  - Submit button (disabled when invalid)
  - Cancel button (clears form or hides modal)
  - Error message display

**Validation Criteria**:
- ✅ Title field required, 1-200 characters
- ✅ Description field optional, max 1000 characters
- ✅ Form validates before submission
- ✅ Submit button disabled when validation fails
- ✅ Character count updates in real-time
- ✅ Errors displayed inline

**Test Coverage**:
- Valid submission triggers onSubmit callback
- Empty title shows error
- Title >200 chars shows error
- Description >1000 chars shows error

**Dependencies**: T-014, T-015

**Failure Considerations**:
- Validation not enforced → Ensure Zod schema applied before submit
- Character count wrong → Verify length calculation includes all characters

---

### Task T-041: Implement Empty State Component (components/EmptyState.tsx)

**Purpose**: Display message when user has no tasks.

**Inputs**:
- Tailwind CSS from T-014

**Outputs**:
- File: `frontend/components/EmptyState.tsx` with:
  - Icon or illustration (optional)
  - Message: "No tasks yet. Create your first task!"
  - Call-to-action (implicit, form is already on page)

**Validation Criteria**:
- ✅ Component renders centered message
- ✅ Styling matches app theme
- ✅ Accessible (semantic HTML)

**Test Coverage**:
- Component renders without errors

**Dependencies**: T-014

**Failure Considerations**:
- None (simple presentational component)

---

### Task T-042: Implement Loading Spinner Component (components/LoadingSpinner.tsx)

**Purpose**: Display loading indicator during async operations.

**Inputs**:
- Tailwind CSS from T-014

**Outputs**:
- File: `frontend/components/LoadingSpinner.tsx` with:
  - Animated spinner (CSS or SVG)
  - Optional message prop
  - Accessible (aria-label)

**Validation Criteria**:
- ✅ Spinner animates smoothly
- ✅ Accessible to screen readers
- ✅ Centered on page/container

**Test Coverage**:
- Component renders without errors

**Dependencies**: T-014

**Failure Considerations**:
- Animation not smooth → Use CSS keyframes or Tailwind animate class

---

### Task T-043: Implement Error Message Component (components/ErrorMessage.tsx)

**Purpose**: Display error messages to users.

**Inputs**:
- Error message string
- Tailwind CSS from T-014

**Outputs**:
- File: `frontend/components/ErrorMessage.tsx` with:
  - Error icon
  - Error message text
  - Dismiss button (optional)
  - Props: message (string), onDismiss (optional callback)

**Validation Criteria**:
- ✅ Error styling (red border, red text)
- ✅ Accessible (role="alert")
- ✅ Dismissible if onDismiss provided

**Test Coverage**:
- Component renders error message
- Dismiss button triggers callback

**Dependencies**: T-014

**Failure Considerations**:
- None (simple presentational component)

---

### Task T-044: Implement Tasks Page (app/tasks/page.tsx)

**Purpose**: Main task management page with CRUD operations.

**Inputs**:
- API client from T-032
- Auth state from T-031
- All task components from T-038 through T-043

**Outputs**:
- File: `frontend/app/tasks/page.tsx` with:
  - Fetch tasks on page load
  - TaskForm for creating new tasks
  - TaskList displaying all tasks
  - Loading state during fetch
  - Error handling for API failures
  - CRUD operation handlers:
    - handleCreate: Calls createTask API, adds to list
    - handleUpdate: Calls updateTask API, updates in list
    - handleDelete: Calls deleteTask API, removes from list
    - handleToggleComplete: Calls toggleComplete API, updates in list

**Validation Criteria**:
- ✅ Tasks loaded and displayed on page mount
- ✅ Create task adds to list immediately (optimistic update)
- ✅ Update task reflects changes immediately
- ✅ Delete task removes from list immediately
- ✅ Toggle complete updates checkbox immediately
- ✅ Loading spinner shown during initial fetch
- ✅ Error messages displayed for API failures
- ✅ Protected route (requires authentication)

**Test Coverage**:
- Page loads tasks on mount
- Create task adds to list
- Update task modifies list
- Delete task removes from list
- Toggle complete updates list
- API errors display error message

**Dependencies**: T-014, T-031, T-032, T-033, T-038, T-039, T-040, T-041, T-042, T-043

**Failure Considerations**:
- Optimistic update not rolled back on error → Add error handler to revert state
- Task list not refreshing → Ensure state updates trigger re-render
- Protected route not enforced → Verify middleware.ts covers /tasks route

---

### Task T-045: Implement Landing Page (app/page.tsx)

**Purpose**: Application home page with navigation to signin/signup.

**Inputs**:
- Auth state from T-031
- Tailwind CSS from T-014

**Outputs**:
- File: `frontend/app/page.tsx` with:
  - App title and description
  - If authenticated: redirect to /tasks
  - If not authenticated: Links to /signin and /signup

**Validation Criteria**:
- ✅ Authenticated users redirected to /tasks automatically
- ✅ Unauthenticated users see welcome message and auth links
- ✅ Responsive design

**Test Coverage**:
- Authenticated user redirected to /tasks
- Unauthenticated user sees landing page

**Dependencies**: T-014, T-031

**Failure Considerations**:
- Redirect loop → Ensure redirect only happens once, not on every render

---

## 4. Testing Tasks - Backend

### Task T-046: Write Unit Tests for Task Model (tests/test_models.py)

**Purpose**: Verify Task model validation and behavior.

**Inputs**:
- Task model from T-019
- pytest from T-013

**Outputs**:
- File: `backend/tests/test_models.py` with test cases:
  - `test_task_creation_success()`: Valid task instantiation
  - `test_task_title_required()`: Missing title raises error
  - `test_task_title_empty_string()`: Empty title raises error
  - `test_task_title_max_length_200()`: Title with 200 chars succeeds
  - `test_task_title_max_length_201()`: Title with 201 chars raises error
  - `test_task_description_optional()`: Task without description succeeds
  - `test_task_description_max_length_1000()`: Description with 1000 chars succeeds
  - `test_task_description_max_length_1001()`: Description with 1001 chars raises error
  - `test_task_completed_default_false()`: New task has completed=false
  - `test_task_timestamps_auto_generated()`: created_at and updated_at set automatically

**Validation Criteria**:
- ✅ All 10 tests pass
- ✅ Tests cover validation edge cases
- ✅ Tests use pytest fixtures for setup

**Dependencies**: T-013, T-019

**Failure Considerations**:
- Tests fail → Fix model validation logic
- Coverage <100% for models.py → Add missing test cases

---

### Task T-047: Write Unit Tests for JWT Middleware (tests/test_auth_middleware.py)

**Purpose**: Verify JWT token verification logic.

**Inputs**:
- Auth middleware from T-020
- pytest from T-013
- python-jose for token generation

**Outputs**:
- File: `backend/tests/test_auth_middleware.py` with test cases:
  - `test_verify_jwt_valid_token()`: Valid token decodes successfully
  - `test_verify_jwt_expired_token()`: Expired token raises 401
  - `test_verify_jwt_invalid_signature()`: Tampered token raises 401
  - `test_verify_jwt_missing_user_id()`: Token without user_id claim raises 401
  - `test_verify_jwt_wrong_algorithm()`: Token with wrong algorithm raises 401
  - `test_user_id_path_match()`: Matching user_id passes
  - `test_user_id_path_mismatch()`: Mismatched user_id raises 403

**Validation Criteria**:
- ✅ All 7 tests pass
- ✅ Tests use mock tokens with various scenarios
- ✅ Tests verify HTTP status codes

**Dependencies**: T-013, T-020

**Failure Considerations**:
- Token generation in tests fails → Use python-jose to create test tokens
- Tests fail → Fix middleware logic

---

### Task T-048: Write Unit Tests for Create Task Endpoint (tests/test_routes_tasks.py - Part 1)

**Purpose**: Verify create task endpoint behavior.

**Inputs**:
- Create task endpoint from T-024
- pytest from T-013
- TestClient from FastAPI

**Outputs**:
- Test cases in `backend/tests/test_routes_tasks.py`:
  - `test_create_task_success()`: Valid request returns 201 with task object
  - `test_create_task_empty_title()`: Empty title returns 400
  - `test_create_task_title_too_long()`: Title >200 chars returns 400
  - `test_create_task_description_too_long()`: Description >1000 chars returns 400
  - `test_create_task_missing_token()`: No Authorization header returns 401
  - `test_create_task_invalid_token()`: Invalid token returns 401
  - `test_create_task_user_id_mismatch()`: Token user_id != path user_id returns 403

**Validation Criteria**:
- ✅ All 7 tests pass
- ✅ Tests use mock database (in-memory or test database)
- ✅ Tests verify response status codes and body structure

**Dependencies**: T-013, T-024

**Failure Considerations**:
- Database state not isolated → Use pytest fixtures to reset DB between tests
- Tests fail → Fix endpoint logic or validation

---

### Task T-049: Write Unit Tests for List Tasks Endpoint (tests/test_routes_tasks.py - Part 2)

**Purpose**: Verify list tasks endpoint behavior and data isolation.

**Inputs**:
- List tasks endpoint from T-025
- pytest from T-013

**Outputs**:
- Additional test cases in `backend/tests/test_routes_tasks.py`:
  - `test_list_tasks_empty()`: User with no tasks returns []
  - `test_list_tasks_returns_user_tasks()`: Returns all user's tasks
  - `test_list_tasks_filters_by_user()`: User A sees only their tasks, not User B's
  - `test_list_tasks_missing_token()`: No token returns 401
  - `test_list_tasks_user_id_mismatch()`: Token user_id != path user_id returns 403

**Validation Criteria**:
- ✅ All 5 tests pass
- ✅ Multi-user test creates tasks for User A and User B, verifies isolation
- ✅ Tests verify response is JSON array

**Dependencies**: T-013, T-025

**Failure Considerations**:
- Data isolation test fails → CRITICAL: Fix query filtering
- Tests fail → Fix endpoint logic

---

### Task T-050: Write Unit Tests for Get Single Task Endpoint (tests/test_routes_tasks.py - Part 3)

**Purpose**: Verify get single task endpoint behavior.

**Inputs**:
- Get task endpoint from T-026
- pytest from T-013

**Outputs**:
- Additional test cases in `backend/tests/test_routes_tasks.py`:
  - `test_get_task_success()`: User retrieves their own task
  - `test_get_task_not_found()`: Non-existent task returns 404
  - `test_get_task_wrong_user()`: User B accessing User A's task returns 403
  - `test_get_task_missing_token()`: No token returns 401

**Validation Criteria**:
- ✅ All 4 tests pass
- ✅ Tests verify ownership check enforced

**Dependencies**: T-013, T-026

**Failure Considerations**:
- Ownership test fails → CRITICAL: Fix endpoint to check user_id
- Tests fail → Fix endpoint logic

---

### Task T-051: Write Unit Tests for Update Task Endpoint (tests/test_routes_tasks.py - Part 4)

**Purpose**: Verify update task endpoint behavior.

**Inputs**:
- Update task endpoint from T-027
- pytest from T-013

**Outputs**:
- Additional test cases in `backend/tests/test_routes_tasks.py`:
  - `test_update_task_title_success()`: Updating title succeeds
  - `test_update_task_description_success()`: Updating description succeeds
  - `test_update_task_partial_update()`: Updating only title succeeds
  - `test_update_task_updated_at_changes()`: updated_at timestamp changes
  - `test_update_task_not_found()`: Non-existent task returns 404
  - `test_update_task_wrong_user()`: User B cannot update User A's task
  - `test_update_task_invalid_data()`: Invalid title returns 400

**Validation Criteria**:
- ✅ All 7 tests pass
- ✅ Timestamp test verifies updated_at > created_at after update

**Dependencies**: T-013, T-027

**Failure Considerations**:
- Partial update fails → Fix endpoint to handle optional fields
- Timestamp not updating → Fix database update logic

---

### Task T-052: Write Unit Tests for Delete Task Endpoint (tests/test_routes_tasks.py - Part 5)

**Purpose**: Verify delete task endpoint behavior.

**Inputs**:
- Delete task endpoint from T-028
- pytest from T-013

**Outputs**:
- Additional test cases in `backend/tests/test_routes_tasks.py`:
  - `test_delete_task_success()`: Deleting task returns 204
  - `test_delete_task_removes_from_database()`: Task no longer in database after delete
  - `test_delete_task_not_found()`: Non-existent task returns 404
  - `test_delete_task_wrong_user()`: User B cannot delete User A's task

**Validation Criteria**:
- ✅ All 4 tests pass
- ✅ Database verification test confirms task deleted

**Dependencies**: T-013, T-028

**Failure Considerations**:
- Task not deleted → Fix DELETE SQL logic
- Ownership test fails → CRITICAL: Fix user_id check

---

### Task T-053: Write Unit Tests for Toggle Complete Endpoint (tests/test_routes_tasks.py - Part 6)

**Purpose**: Verify toggle complete endpoint behavior.

**Inputs**:
- Toggle complete endpoint from T-029
- pytest from T-013

**Outputs**:
- Additional test cases in `backend/tests/test_routes_tasks.py`:
  - `test_toggle_complete_true_to_false()`: completed=true toggles to false
  - `test_toggle_complete_false_to_true()`: completed=false toggles to true
  - `test_toggle_complete_updated_at_changes()`: updated_at timestamp changes
  - `test_toggle_complete_not_found()`: Non-existent task returns 404
  - `test_toggle_complete_wrong_user()`: User B cannot toggle User A's task

**Validation Criteria**:
- ✅ All 5 tests pass
- ✅ Toggle logic verified (both directions)

**Dependencies**: T-013, T-029

**Failure Considerations**:
- Toggle doesn't work both ways → Fix boolean flip logic
- Timestamp not updating → Fix database update logic

---

### Task T-054: Run Backend Unit Tests and Verify Coverage

**Purpose**: Execute all backend unit tests and ensure ≥80% code coverage.

**Inputs**:
- All test files from T-046 through T-053
- pytest and pytest-cov from T-013

**Outputs**:
- Test execution report
- Code coverage report

**Validation Criteria**:
- ✅ All tests pass (50+ tests)
- ✅ Code coverage ≥80% for models.py, auth.py, routes/tasks.py
- ✅ No failing tests

**Command**:
```bash
cd backend
pytest tests/ -v --cov=. --cov-report=term-missing
```

**Dependencies**: T-046, T-047, T-048, T-049, T-050, T-051, T-052, T-053

**Failure Considerations**:
- Tests fail → Fix failing tests or code
- Coverage <80% → Add missing test cases
- Coverage report not generated → Install pytest-cov

---

## 5. Testing Tasks - Frontend

### Task T-055: Write Unit Tests for Task List Component (frontend/__tests__/components/TaskList.test.tsx)

**Purpose**: Verify TaskList component rendering logic.

**Inputs**:
- TaskList component from T-038
- React Testing Library (install if needed)

**Outputs**:
- File: `frontend/__tests__/components/TaskList.test.tsx` with test cases:
  - `test_renders_tasks()`: Component renders array of tasks
  - `test_renders_empty_state()`: Shows EmptyState when tasks array empty
  - `test_passes_callbacks_to_items()`: TaskItem receives callback props

**Validation Criteria**:
- ✅ All 3 tests pass
- ✅ Tests use @testing-library/react

**Dependencies**: T-014, T-038

**Failure Considerations**:
- Tests fail → Fix component rendering logic
- Testing library not installed → Run `npm install --save-dev @testing-library/react @testing-library/jest-dom`

---

### Task T-056: Write Unit Tests for Task Form Component (frontend/__tests__/components/TaskForm.test.tsx)

**Purpose**: Verify TaskForm validation and submission logic.

**Inputs**:
- TaskForm component from T-040
- React Testing Library

**Outputs**:
- File: `frontend/__tests__/components/TaskForm.test.tsx` with test cases:
  - `test_submits_valid_task()`: Form submission calls onSubmit callback
  - `test_validates_empty_title()`: Empty title shows error
  - `test_validates_title_length()`: Title >200 chars shows error
  - `test_validates_description_length()`: Description >1000 chars shows error
  - `test_character_count_updates()`: Character count displays correctly

**Validation Criteria**:
- ✅ All 5 tests pass
- ✅ Tests verify form validation works

**Dependencies**: T-014, T-040

**Failure Considerations**:
- Validation tests fail → Fix Zod schema or validation logic
- Tests fail → Fix component logic

---

### Task T-057: Write Unit Tests for Auth Client (frontend/__tests__/lib/auth.test.ts)

**Purpose**: Verify auth client functions.

**Inputs**:
- Auth client from T-031
- Jest or Vitest

**Outputs**:
- File: `frontend/__tests__/lib/auth.test.ts` with test cases:
  - `test_signup_stores_token()`: Successful signup saves token to localStorage
  - `test_signin_stores_token()`: Successful signin saves token to localStorage
  - `test_signout_clears_token()`: Signout removes token from localStorage
  - `test_getSession_returns_user()`: getSession retrieves user data

**Validation Criteria**:
- ✅ All 4 tests pass
- ✅ Tests use mocked Better Auth API responses

**Dependencies**: T-014, T-031

**Failure Considerations**:
- localStorage not mocked → Mock localStorage in test setup
- API calls not mocked → Use MSW (Mock Service Worker) or jest.mock

---

### Task T-058: Run Frontend Unit Tests

**Purpose**: Execute all frontend unit tests and verify they pass.

**Inputs**:
- All test files from T-055, T-056, T-057
- Jest or Vitest configured by Next.js

**Outputs**:
- Test execution report

**Validation Criteria**:
- ✅ All tests pass
- ✅ No failing tests

**Command**:
```bash
cd frontend
npm test
```

**Dependencies**: T-055, T-056, T-057

**Failure Considerations**:
- Tests fail → Fix failing tests or code
- Test runner not configured → Configure Jest/Vitest for Next.js

---

## 6. Integration & End-to-End Testing Tasks

### Task T-059: Write Integration Test - Complete CRUD Flow

**Purpose**: Verify end-to-end task CRUD operations through API.

**Inputs**:
- Backend running from T-021 through T-030
- Auth service running from T-008
- pytest from T-013

**Outputs**:
- File: `backend/tests/test_integration_crud.py` with test:
  - `test_complete_crud_flow()`:
    1. Create user via auth-service
    2. Create task via POST /api/{user_id}/tasks
    3. Verify task in GET /api/{user_id}/tasks
    4. Update task via PUT /api/{user_id}/tasks/{id}
    5. Verify update in GET /api/{user_id}/tasks/{id}
    6. Toggle complete via PATCH /api/{user_id}/tasks/{id}/complete
    7. Delete task via DELETE /api/{user_id}/tasks/{id}
    8. Verify task no longer in GET /api/{user_id}/tasks

**Validation Criteria**:
- ✅ Test passes
- ✅ All 8 steps execute successfully
- ✅ Verifies data persistence at each step

**Dependencies**: T-008, T-021, T-024, T-025, T-026, T-027, T-028, T-029

**Failure Considerations**:
- Any step fails → Debug specific endpoint
- Test flaky → Ensure database reset between tests

---

### Task T-060: Write Integration Test - Multi-User Data Isolation

**Purpose**: Verify users cannot access each other's data.

**Inputs**:
- Backend and auth-service running
- pytest from T-013

**Outputs**:
- File: `backend/tests/test_integration_isolation.py` with test:
  - `test_multi_user_isolation()`:
    1. Create User A and User B via auth-service
    2. User A creates Task 1
    3. User B creates Task 2
    4. Verify User A's GET /api/{user_a_id}/tasks returns only Task 1
    5. Verify User B's GET /api/{user_b_id}/tasks returns only Task 2
    6. User B attempts GET /api/{user_a_id}/tasks/{task_1_id} → Expect 403
    7. User A attempts DELETE /api/{user_b_id}/tasks/{task_2_id} → Expect 403

**Validation Criteria**:
- ✅ Test passes
- ✅ Data isolation enforced (no cross-user access)
- ✅ 403 errors returned for unauthorized access

**Dependencies**: T-008, T-021, T-024, T-025, T-026, T-028

**Failure Considerations**:
- Isolation test fails → CRITICAL: Fix user_id filtering and ownership checks
- 403 not returned → Fix middleware or endpoint logic

---

### Task T-061: Write Integration Test - Authentication Flow

**Purpose**: Verify complete authentication flow (signup, signin, token validation).

**Inputs**:
- Auth-service from T-008
- Backend middleware from T-020
- pytest from T-013

**Outputs**:
- File: `backend/tests/test_integration_auth.py` with test:
  - `test_authentication_flow()`:
    1. Signup new user via auth-service
    2. Verify JWT token returned
    3. Call protected endpoint with token → Expect 200
    4. Call protected endpoint without token → Expect 401
    5. Call protected endpoint with expired token → Expect 401
    6. Signout via auth-service
    7. Call protected endpoint with old token → Expect 401 (if session-based)

**Validation Criteria**:
- ✅ Test passes
- ✅ Token validation working correctly
- ✅ Unauthorized requests blocked

**Dependencies**: T-008, T-020, T-021

**Failure Considerations**:
- Token validation fails → Check BETTER_AUTH_SECRET matches between services
- Expired token not rejected → Fix token expiration check

---

### Task T-062: Write End-to-End Test - New User Complete Journey

**Purpose**: Verify complete user journey from signup to task management.

**Inputs**:
- All services running (auth, backend, frontend)
- Playwright or Cypress (install if needed)

**Outputs**:
- File: `frontend/e2e/complete-journey.spec.ts` with test:
  - `test_new_user_journey()`:
    1. Visit landing page
    2. Click "Sign Up"
    3. Fill signup form, submit
    4. Verify redirect to /tasks
    5. Verify empty state displayed
    6. Create new task "Buy groceries"
    7. Verify task appears in list
    8. Mark task complete
    9. Verify checkbox checked
    10. Update task title to "Buy groceries and fruits"
    11. Verify title updated
    12. Delete task
    13. Verify task removed, empty state shown
    14. Sign out
    15. Verify redirect to landing page

**Validation Criteria**:
- ✅ Test passes
- ✅ All 15 steps execute successfully
- ✅ UI reflects state changes correctly

**Dependencies**: T-008, T-021 through T-045

**Failure Considerations**:
- E2E test flaky → Add explicit waits for async operations
- Test fails → Debug specific step, verify services running

---

### Task T-063: Perform Manual Cross-Browser Testing

**Purpose**: Verify application works on all major browsers.

**Inputs**:
- Frontend deployed or running locally
- Chrome, Firefox, Safari, Edge installed

**Outputs**:
- Test checklist document with results:
  - Chrome: Signup, Signin, Create task, Update, Delete, Toggle complete
  - Firefox: Same tests
  - Safari: Same tests
  - Edge: Same tests

**Validation Criteria**:
- ✅ All features work on all browsers
- ✅ No console errors
- ✅ UI renders correctly (no layout issues)

**Dependencies**: T-044

**Failure Considerations**:
- Browser-specific bug found → Fix CSS or JavaScript compatibility issue
- Feature doesn't work → Debug browser-specific issue

---

## 7. Performance & Security Testing Tasks

### Task T-064: Measure Backend API Response Time

**Purpose**: Verify API endpoints meet performance requirements (p95 <500ms).

**Inputs**:
- Backend running from T-021 through T-030
- Apache Bench or similar load testing tool

**Outputs**:
- Performance test report with metrics:
  - GET /api/{user_id}/tasks p95 latency
  - POST /api/{user_id}/tasks p95 latency
  - Average response times

**Validation Criteria**:
- ✅ p95 latency <500ms for all endpoints
- ✅ API handles 100 concurrent requests without errors

**Command Example**:
```bash
ab -n 1000 -c 10 -H "Authorization: Bearer <token>" http://localhost:8000/api/{user_id}/tasks
```

**Dependencies**: T-021, T-025

**Failure Considerations**:
- Latency >500ms → Optimize database queries, add indexes
- Errors under load → Fix database connection pool configuration

---

### Task T-065: Measure Frontend Page Load Time

**Purpose**: Verify frontend pages load within 2 seconds on 3G connection.

**Inputs**:
- Frontend deployed or running locally
- Lighthouse or WebPageTest

**Outputs**:
- Lighthouse report with metrics:
  - First Contentful Paint (FCP)
  - Largest Contentful Paint (LCP)
  - Time to Interactive (TTI)
  - Total page load time

**Validation Criteria**:
- ✅ Page load time <2s on throttled 3G
- ✅ Lighthouse performance score >80

**Command**:
```bash
lighthouse http://localhost:3000/tasks --throttling-method=devtools --throttling.cpuSlowdownMultiplier=4
```

**Dependencies**: T-044

**Failure Considerations**:
- Page load >2s → Optimize bundle size, use code splitting, optimize images
- Low performance score → Follow Lighthouse recommendations

---

### Task T-066: Perform Security Audit - Secrets in Git

**Purpose**: Verify no secrets committed to version control.

**Inputs**:
- Git repository

**Outputs**:
- Audit report confirming no secrets found

**Validation Criteria**:
- ✅ `git grep -i 'password\|secret\|api_key'` returns no matches in source files
- ✅ `.gitignore` includes `.env`, `.env.local`
- ✅ No `DATABASE_URL` or `BETTER_AUTH_SECRET` in committed files

**Command**:
```bash
git grep -i 'password\|secret\|api_key' -- '*.py' '*.ts' '*.tsx' '*.js' '*.jsx'
```

**Dependencies**: None (can be done anytime)

**Failure Considerations**:
- Secrets found → Remove from git history, update .gitignore
- False positives → Review matches, ensure actual secrets not present

---

### Task T-067: Perform Security Audit - CORS Configuration

**Purpose**: Verify CORS configured correctly to prevent unauthorized origins.

**Inputs**:
- Backend and auth-service running
- Browser DevTools or curl

**Outputs**:
- Audit report confirming CORS headers correct

**Validation Criteria**:
- ✅ Backend CORS allows only `http://localhost:3000` in development
- ✅ Auth-service CORS allows `http://localhost:3000` and `http://localhost:8000`
- ✅ Cross-origin request from unauthorized domain blocked

**Test**:
```bash
curl -H "Origin: http://malicious.com" http://localhost:8000/api/health -v
```

**Dependencies**: T-021, T-008

**Failure Considerations**:
- CORS allows all origins (*) → CRITICAL: Fix to explicit origins
- Unauthorized origin allowed → Fix CORS_ORIGINS configuration

---

### Task T-068: Perform Security Audit - SQL Injection Prevention

**Purpose**: Verify SQLModel prevents SQL injection attacks.

**Inputs**:
- Backend running
- Malicious input test cases

**Outputs**:
- Audit report confirming SQL injection prevented

**Validation Criteria**:
- ✅ Submitting `'; DROP TABLE tasks;--` as title does not execute SQL
- ✅ Task created with literal string `'; DROP TABLE tasks;--` as title
- ✅ Database tables intact after test

**Test**:
- Create task with title `'; DROP TABLE tasks;--`
- Verify task stored as regular string
- Verify `tasks` table still exists

**Dependencies**: T-024

**Failure Considerations**:
- SQL injection succeeds → CRITICAL: Verify SQLModel used for all queries
- Raw SQL found → Replace with SQLModel ORM

---

### Task T-069: Perform Security Audit - JWT Token Verification

**Purpose**: Verify backend correctly validates JWT tokens.

**Inputs**:
- Backend running
- python-jose for token manipulation

**Outputs**:
- Audit report confirming token verification works

**Validation Criteria**:
- ✅ Valid token succeeds
- ✅ Expired token returns 401
- ✅ Tampered token (modified signature) returns 401
- ✅ Token with wrong user_id in path returns 403

**Test**:
- Generate valid token, call API → Expect 200
- Expire token, call API → Expect 401
- Modify token signature, call API → Expect 401
- Use valid token but wrong user_id in path → Expect 403

**Dependencies**: T-020, T-024

**Failure Considerations**:
- Invalid token accepted → Fix JWT verification logic
- User_id mismatch not caught → Fix path parameter comparison

---

## 8. Deployment Tasks

### Task T-070: Create Production Environment File for Backend

**Purpose**: Prepare backend environment configuration for production deployment.

**Inputs**:
- Production Neon DATABASE_URL
- Production BETTER_AUTH_SECRET (same as auth-service)
- Production frontend URL (Vercel)

**Outputs**:
- Environment variables configured in deployment platform (Render/Railway/DigitalOcean):
  ```
  DATABASE_URL=<production-neon-url>
  BETTER_AUTH_SECRET=<same-as-dev>
  CORS_ORIGINS=https://your-app.vercel.app
  ENVIRONMENT=production
  ```

**Validation Criteria**:
- ✅ All required variables set in hosting platform
- ✅ DATABASE_URL points to production Neon database
- ✅ CORS_ORIGINS includes production frontend URL

**Dependencies**: T-001, T-002

**Failure Considerations**:
- Wrong DATABASE_URL → Backend cannot connect to database
- CORS_ORIGINS missing production URL → Frontend API calls blocked

---

### Task T-071: Create Production Environment File for Auth Service

**Purpose**: Prepare auth-service environment configuration for production.

**Inputs**:
- Production Neon DATABASE_URL (same as backend)
- Production BETTER_AUTH_SECRET (same as backend)
- Production frontend and backend URLs

**Outputs**:
- Environment variables configured in auth-service deployment:
  ```
  DATABASE_URL=<production-neon-url>
  BETTER_AUTH_SECRET=<same-as-backend>
  CORS_ORIGINS=https://your-app.vercel.app,https://your-backend.render.com
  SESSION_EXPIRES_IN=7d
  NODE_ENV=production
  PORT=3001
  ```

**Validation Criteria**:
- ✅ All required variables set
- ✅ BETTER_AUTH_SECRET matches backend exactly
- ✅ CORS_ORIGINS includes production frontend and backend

**Dependencies**: T-001, T-002

**Failure Considerations**:
- Secret mismatch → Backend cannot verify tokens
- CORS misconfigured → API calls fail

---

### Task T-072: Create Production Environment File for Frontend

**Purpose**: Prepare frontend environment configuration for Vercel deployment.

**Inputs**:
- Production auth-service URL
- Production backend API URL

**Outputs**:
- Environment variables configured in Vercel:
  ```
  NEXT_PUBLIC_AUTH_URL=https://your-auth.render.com
  NEXT_PUBLIC_API_URL=https://your-backend.render.com
  ```

**Validation Criteria**:
- ✅ URLs point to production services
- ✅ HTTPS enforced

**Dependencies**: None (use production URLs once services deployed)

**Failure Considerations**:
- Wrong URLs → Frontend cannot communicate with backend
- HTTP URLs → Browser blocks mixed content

---

### Task T-073: Run Production Database Migrations

**Purpose**: Apply database migrations to production Neon PostgreSQL.

**Inputs**:
- Production DATABASE_URL
- Auth-service migrations from T-007
- Backend models from T-019

**Outputs**:
- Production database tables created:
  - `users`, `session`, `account`, `verification` (Better Auth)
  - `tasks` (backend)

**Validation Criteria**:
- ✅ Migrations run successfully
- ✅ All tables created in production database
- ✅ No data loss (if migrating existing database)

**Commands**:
```bash
# Auth-service migrations
cd auth-service
DATABASE_URL=<production-url> npm run migrate:push

# Backend will create tasks table on startup via SQLModel
```

**Dependencies**: T-007, T-019

**Failure Considerations**:
- Migration fails → Check DATABASE_URL, verify network access
- Tables already exist → Verify not overwriting production data

---

### Task T-074: Deploy Auth Service to Production

**Purpose**: Deploy Better Auth service to hosting platform.

**Inputs**:
- Auth-service code from T-003 through T-008
- Production environment variables from T-071
- Hosting platform (Render/Railway/DigitalOcean)

**Outputs**:
- Auth-service running at production URL (e.g., `https://todo-auth.render.com`)

**Validation Criteria**:
- ✅ Service deployed successfully
- ✅ Health check endpoint responds: `GET /health`
- ✅ HTTPS enforced
- ✅ Environment variables loaded correctly

**Deployment Steps**:
1. Create new web service on hosting platform
2. Connect GitHub repository
3. Set build command: `npm install && npm run build`
4. Set start command: `npm start`
5. Set environment variables from T-071
6. Deploy

**Dependencies**: T-008, T-071, T-073

**Failure Considerations**:
- Deployment fails → Check build logs for errors
- Service crashes → Check environment variables, database connection
- Health check fails → Verify DATABASE_URL correct

---

### Task T-075: Deploy Backend to Production

**Purpose**: Deploy FastAPI backend to hosting platform.

**Inputs**:
- Backend code from T-018 through T-030
- Production environment variables from T-070
- Hosting platform

**Outputs**:
- Backend running at production URL (e.g., `https://todo-api.render.com`)

**Validation Criteria**:
- ✅ Backend deployed successfully
- ✅ Health check endpoint responds: `GET /health`
- ✅ HTTPS enforced
- ✅ Database connection successful
- ✅ OpenAPI docs accessible: `GET /docs`

**Deployment Steps**:
1. Create new web service on hosting platform
2. Connect GitHub repository (backend directory)
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Set environment variables from T-070
6. Deploy

**Dependencies**: T-030, T-070, T-073

**Failure Considerations**:
- Deployment fails → Check Python version, dependencies
- Database connection fails → Verify DATABASE_URL, check Neon IP allowlist
- CORS errors → Verify CORS_ORIGINS includes frontend URL

---

### Task T-076: Deploy Frontend to Vercel

**Purpose**: Deploy Next.js frontend to Vercel.

**Inputs**:
- Frontend code from T-031 through T-045
- Production environment variables from T-072
- Vercel account

**Outputs**:
- Frontend deployed at Vercel URL (e.g., `https://todo-app.vercel.app`)

**Validation Criteria**:
- ✅ Frontend deployed successfully
- ✅ HTTPS enforced
- ✅ Environment variables loaded correctly
- ✅ Pages render without errors

**Deployment Steps**:
1. Create new project in Vercel
2. Connect GitHub repository (frontend directory)
3. Set framework preset: Next.js
4. Set environment variables from T-072
5. Deploy

**Dependencies**: T-045, T-072

**Failure Considerations**:
- Build fails → Check TypeScript errors, missing dependencies
- API calls fail → Verify NEXT_PUBLIC_API_URL correct
- Auth fails → Verify NEXT_PUBLIC_AUTH_URL correct

---

### Task T-077: Update CORS Origins in Backend and Auth Service

**Purpose**: Add production frontend URL to CORS allowed origins.

**Inputs**:
- Production frontend URL from T-076
- Backend and auth-service deployed from T-074, T-075

**Outputs**:
- Updated CORS_ORIGINS environment variables:
  - Backend: `https://todo-app.vercel.app`
  - Auth-service: `https://todo-app.vercel.app,https://todo-api.render.com`

**Validation Criteria**:
- ✅ CORS_ORIGINS updated in both services
- ✅ Services restarted with new config
- ✅ Frontend API calls succeed (no CORS errors)

**Dependencies**: T-074, T-075, T-076

**Failure Considerations**:
- CORS errors persist → Verify exact URL match (no trailing slash)
- Services not restarted → Manually restart or redeploy

---

### Task T-078: Verify Production Health Checks

**Purpose**: Ensure all production services healthy and responsive.

**Inputs**:
- Production URLs from T-074, T-075, T-076

**Outputs**:
- Health check verification:
  - Auth-service: `GET https://todo-auth.render.com/health` → 200 OK
  - Backend: `GET https://todo-api.render.com/health` → 200 OK
  - Frontend: `GET https://todo-app.vercel.app` → 200 OK

**Validation Criteria**:
- ✅ All health checks return 200 OK
- ✅ Response times acceptable (<2s)
- ✅ No errors in service logs

**Dependencies**: T-074, T-075, T-076

**Failure Considerations**:
- Health check fails → Check service logs, restart if needed
- Slow response → Investigate database connection, hosting platform performance

---

### Task T-079: Run Production Smoke Tests

**Purpose**: Verify core functionality works in production environment.

**Inputs**:
- Production frontend URL
- Production backend and auth-service URLs

**Outputs**:
- Smoke test results:
  1. Signup new user → Success
  2. Signin with credentials → Success
  3. Create task → Task appears in list
  4. Update task → Changes reflected
  5. Delete task → Task removed
  6. Signout → Redirected to home

**Validation Criteria**:
- ✅ All 6 smoke tests pass
- ✅ No console errors in browser
- ✅ No 500 errors from backend

**Dependencies**: T-074, T-075, T-076, T-077, T-078

**Failure Considerations**:
- Any test fails → Debug specific issue, check logs
- Database errors → Verify production DATABASE_URL correct
- Auth errors → Verify BETTER_AUTH_SECRET matches

---

## 9. Documentation & Finalization Tasks

### Task T-080: Write Backend README

**Purpose**: Document backend setup, configuration, and running instructions.

**Inputs**:
- Backend project structure

**Outputs**:
- File: `backend/README.md` with sections:
  - Overview (what the backend does)
  - Prerequisites (Python 3.13+, UV, Neon PostgreSQL)
  - Environment Variables (list with descriptions)
  - Installation (`uv pip install -r requirements.txt`)
  - Running Locally (`uvicorn main:app --reload`)
  - Running Tests (`pytest tests/ -v --cov`)
  - API Documentation (link to `/docs` endpoint)
  - Deployment (production setup instructions)

**Validation Criteria**:
- ✅ README clear and comprehensive
- ✅ Setup instructions tested (follow README, verify app runs)
- ✅ All environment variables documented

**Dependencies**: T-030, T-054

**Failure Considerations**:
- Instructions incomplete → Add missing steps
- Instructions don't work → Test and fix

---

### Task T-081: Write Frontend README

**Purpose**: Document frontend setup, configuration, and running instructions.

**Inputs**:
- Frontend project structure

**Outputs**:
- File: `frontend/README.md` with sections:
  - Overview (what the frontend does)
  - Prerequisites (Node.js 18+)
  - Environment Variables (list with descriptions)
  - Installation (`npm install`)
  - Running Locally (`npm run dev`)
  - Running Tests (`npm test`)
  - Building for Production (`npm run build`)
  - Deployment (Vercel deployment instructions)

**Validation Criteria**:
- ✅ README clear and comprehensive
- ✅ Setup instructions tested
- ✅ All environment variables documented

**Dependencies**: T-045, T-058

**Failure Considerations**:
- Instructions incomplete → Add missing steps
- Instructions don't work → Test and fix

---

### Task T-082: Write Root Project README

**Purpose**: Document overall project structure and setup for all services.

**Inputs**:
- Complete project structure
- Backend and frontend READMEs from T-080, T-081

**Outputs**:
- File: `README.md` (root) with sections:
  - Project Overview (Phase II Todo Full-Stack Web Application)
  - Architecture Diagram (3-service architecture: auth, backend, frontend)
  - Prerequisites (Node.js, Python, UV, Neon PostgreSQL account)
  - Environment Setup:
    - Database provisioning
    - Better Auth customization
    - Environment variable configuration
  - Running All Services:
    - Auth-service: `cd auth-service && npm run dev`
    - Backend: `cd backend && uvicorn main:app --reload`
    - Frontend: `cd frontend && npm run dev`
  - Testing (how to run all test suites)
  - Deployment (links to hosting platforms)
  - Technology Stack (list all technologies used)
  - License and Contributing

**Validation Criteria**:
- ✅ README comprehensive and accurate
- ✅ Setup instructions work end-to-end
- ✅ Architecture diagram clear

**Dependencies**: T-080, T-081

**Failure Considerations**:
- Instructions unclear → Simplify and clarify
- Diagram missing → Add architecture diagram (text or image)

---

### Task T-083: Update CLAUDE.md with Phase II Context

**Purpose**: Document Claude Code-specific guidance for Phase II implementation.

**Inputs**:
- Existing `CLAUDE.md` from project root
- Specification and plan from this phase

**Outputs**:
- Updated `CLAUDE.md` with Phase II sections:
  - Phase II Overview
  - Better Auth Customization Steps
  - Backend Development Guidance
  - Frontend Development Guidance
  - Common Issues and Solutions
  - Testing Strategy

**Validation Criteria**:
- ✅ CLAUDE.md updated with Phase II content
- ✅ Customization steps documented clearly
- ✅ Common issues and solutions included

**Dependencies**: None (documentation task)

**Failure Considerations**:
- None (documentation only)

---

### Task T-084: Create .env.example Files for All Services

**Purpose**: Ensure all services have example environment files committed to git.

**Inputs**:
- Actual `.env` files (not committed)

**Outputs**:
- Files committed to git:
  - `auth-service/.env.example`
  - `backend/.env.example`
  - `frontend/.env.example`

**Validation Criteria**:
- ✅ All `.env.example` files exist
- ✅ No actual secrets in example files
- ✅ All required variables documented with placeholders

**Dependencies**: T-005, T-011, T-017

**Failure Considerations**:
- Example files missing → Create from actual .env, replace values with placeholders
- Actual secrets in example → Replace with generic placeholders

---

### Task T-085: Verify .gitignore Excludes Secrets

**Purpose**: Ensure all secret files excluded from version control.

**Inputs**:
- `.gitignore` files in project

**Outputs**:
- Verification that `.gitignore` includes:
  - `.env`
  - `.env.local`
  - `node_modules/`
  - `__pycache__/`
  - `.pytest_cache/`
  - `*.pyc`

**Validation Criteria**:
- ✅ All secret files in `.gitignore`
- ✅ `git status` shows no `.env` files as untracked (if they exist)

**Dependencies**: None

**Failure Considerations**:
- `.env` files tracked → Add to `.gitignore`, remove from git history

---

### Task T-086: Create Git Commit for Phase II Completion

**Purpose**: Commit all Phase II code and documentation to git repository.

**Inputs**:
- All completed tasks
- Clean git status (no uncommitted changes)

**Outputs**:
- Git commit with message:
  ```
  feat: Complete Phase II Full-Stack Web Application

  - Auth-service customized (Physical AI fields removed)
  - Backend FastAPI with 6 task CRUD endpoints
  - Frontend Next.js with authentication and task management
  - 50+ unit tests, integration tests, E2E tests (all passing)
  - Deployed to production (Vercel + Render)
  - Documentation complete (README, CLAUDE.md)

  🤖 Generated with Claude Code (https://claude.com/claude-code)

  Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
  ```

**Validation Criteria**:
- ✅ All files staged and committed
- ✅ Commit message descriptive
- ✅ No uncommitted changes remain

**Command**:
```bash
git add .
git commit -m "feat: Complete Phase II Full-Stack Web Application..."
```

**Dependencies**: T-001 through T-085 (all tasks complete)

**Failure Considerations**:
- Uncommitted files → Stage all changes before commit
- Merge conflicts → Resolve before committing

---

### Task T-087: Create Git Tag for Phase II Release

**Purpose**: Tag Phase II completion for version tracking.

**Inputs**:
- Git commit from T-086

**Outputs**:
- Git tag: `phase-ii-v1.0.0`

**Validation Criteria**:
- ✅ Tag created successfully
- ✅ Tag pushed to remote repository

**Commands**:
```bash
git tag -a phase-ii-v1.0.0 -m "Phase II: Full-Stack Web Application - v1.0.0"
git push origin phase-ii-v1.0.0
```

**Dependencies**: T-086

**Failure Considerations**:
- Tag already exists → Delete old tag or use different version number

---

### Task T-088: Create GitHub Repository (if not exists)

**Purpose**: Host project code on GitHub for collaboration and deployment.

**Inputs**:
- GitHub account
- Project code from T-086

**Outputs**:
- GitHub repository at `https://github.com/username/todo-full-stack-app`

**Validation Criteria**:
- ✅ Repository created
- ✅ Code pushed to repository
- ✅ README displays on repository home page

**Commands**:
```bash
git remote add origin https://github.com/username/todo-full-stack-app.git
git push -u origin master
```

**Dependencies**: T-086

**Failure Considerations**:
- Repository already exists → Use existing repository
- Push fails → Verify SSH keys or HTTPS credentials

---

### Task T-089: Update Constitution with Phase II Completion Status

**Purpose**: Record Phase II completion in project constitution.

**Inputs**:
- Constitution file at `.specify/memory/constitution.md`

**Outputs**:
- Updated constitution with Phase II success criteria marked complete:
  ```
  **Phase II Success Criteria:**
  - [x] RESTful API endpoints functional (6 endpoints)
  - [x] Frontend displays and manages tasks via API
  - [x] User authentication working (signup/signin)
  - [x] Data persists in Neon PostgreSQL database
  - [x] Each user sees only their own tasks
  - [x] Deployed on Vercel (frontend) and accessible backend
  - [x] All tests passing with 80%+ coverage
  ```

**Validation Criteria**:
- ✅ All checkboxes marked complete
- ✅ Constitution version incremented (if needed)

**Dependencies**: T-079 (production deployment verified)

**Failure Considerations**:
- Any criteria not met → Complete missing tasks before marking complete

---

### Task T-090: Prepare Demo Video (90 seconds max)

**Purpose**: Create demo video for hackathon submission showing all Phase II features.

**Inputs**:
- Production application URL
- Screen recording software

**Outputs**:
- Video file (MP4, max 90 seconds) demonstrating:
  1. Landing page (5s)
  2. Signup flow (10s)
  3. Empty task list (5s)
  4. Create task (10s)
  5. Mark complete (5s)
  6. Update task (10s)
  7. Delete task (10s)
  8. Signin flow (10s)
  9. Multi-user isolation (15s - show two users)
  10. Production deployment (10s - show URLs)

**Validation Criteria**:
- ✅ Video under 90 seconds
- ✅ All features demonstrated
- ✅ Audio clear (optional narration)
- ✅ Production URLs shown

**Dependencies**: T-079

**Failure Considerations**:
- Video too long → Edit to fit 90 seconds
- Poor quality → Re-record with better resolution

---

### Task T-091: Submit Phase II to Hackathon

**Purpose**: Submit Phase II project to hackathon evaluation form.

**Inputs**:
- GitHub repository URL from T-088
- Production application URL from T-076
- Demo video from T-090
- WhatsApp number for presentation invitation

**Outputs**:
- Hackathon submission via Google Form: `https://forms.gle/KMKEKaFUD6ZX4UtY8`

**Validation Criteria**:
- ✅ Form submitted successfully
- ✅ All required fields filled
- ✅ Confirmation received

**Dependencies**: T-088, T-090

**Failure Considerations**:
- Form submission fails → Retry or contact hackathon organizers
- Missing information → Gather required data and resubmit

---

## 10. Verification & Quality Assurance Tasks

### Task T-092: Verify All Functional Requirements Met

**Purpose**: Confirm all 14 functional requirements from specification implemented and tested.

**Inputs**:
- Specification document (Section 2)
- Completed implementation

**Outputs**:
- Verification checklist with results:
  - FR-AUTH-01: User Signup ✅
  - FR-AUTH-02: User Signin ✅
  - FR-AUTH-03: User Signout ✅
  - FR-AUTH-04: Session Persistence ✅
  - FR-AUTH-05: Auth Service Customization ✅
  - FR-TASK-01: Create Task ✅
  - FR-TASK-02: View Task List ✅
  - FR-TASK-03: View Single Task ✅
  - FR-TASK-04: Update Task ✅
  - FR-TASK-05: Delete Task ✅
  - FR-TASK-06: Mark Complete ✅
  - FR-ISOLATION-01: Path Parameter Enforcement ✅
  - FR-ISOLATION-02: Query Filtering ✅
  - FR-ISOLATION-03: Error Message Security ✅

**Validation Criteria**:
- ✅ All 14 functional requirements verified
- ✅ Acceptance criteria met for each requirement

**Dependencies**: All implementation and testing tasks

**Failure Considerations**:
- Any requirement not met → Complete missing implementation

---

### Task T-093: Verify All Non-Functional Requirements Met

**Purpose**: Confirm all non-functional requirements (performance, security, etc.) satisfied.

**Inputs**:
- Specification document (Section 3)
- Performance test results from T-064, T-065
- Security audit results from T-066 through T-069

**Outputs**:
- Verification checklist with results:
  - NFR-PERF-01: API <500ms p95 ✅
  - NFR-PERF-01: Page load <2s ✅
  - NFR-SEC-01: Authentication required ✅
  - NFR-SEC-02: Input validation ✅
  - NFR-SEC-03: No secrets in git ✅
  - NFR-SEC-04: HTTPS in production ✅
  - NFR-REL-01: Structured errors ✅
  - NFR-REL-02: Foreign key constraints ✅
  - NFR-SCALE-01: Stateless backend ✅
  - NFR-MAINT-01: Code quality (PEP 8, ESLint) ✅
  - NFR-MAINT-02: README exists ✅
  - NFR-MAINT-03: 80% test coverage ✅
  - NFR-ACCESS-01: Semantic HTML, keyboard accessible ✅
  - NFR-ACCESS-02: Responsive design ✅

**Validation Criteria**:
- ✅ All non-functional requirements verified
- ✅ Test results documented

**Dependencies**: T-064, T-065, T-066, T-067, T-068, T-069

**Failure Considerations**:
- Any requirement not met → Fix issue and re-verify

---

### Task T-094: Verify Definition of Done Checklist Complete

**Purpose**: Ensure all items in plan's Definition of Done (Section 8.1) are checked.

**Inputs**:
- Plan document Definition of Done checklist
- Completed implementation

**Outputs**:
- Fully checked Definition of Done with all items ✅

**Validation Criteria**:
- ✅ All functional requirements checked
- ✅ All non-functional requirements checked
- ✅ All testing items checked
- ✅ All deployment items checked
- ✅ All documentation items checked
- ✅ All constitutional compliance items checked

**Dependencies**: T-092, T-093, all testing and deployment tasks

**Failure Considerations**:
- Any item unchecked → Complete missing work

---

### Task T-095: Final Code Quality Review

**Purpose**: Perform final review of code quality before considering Phase II complete.

**Inputs**:
- All codebase files
- ESLint and Pylint configurations

**Outputs**:
- Code quality report:
  - ESLint frontend: 0 errors, 0 warnings
  - Pylint backend: 0 errors, score >8.0
  - No console.log in production code
  - No commented-out code blocks
  - No TODO comments in critical paths

**Validation Criteria**:
- ✅ ESLint passes with no errors
- ✅ Pylint passes with no errors
- ✅ Code review checklist complete

**Commands**:
```bash
# Frontend
cd frontend
npm run lint

# Backend
cd backend
pylint *.py routes/*.py
```

**Dependencies**: All implementation tasks

**Failure Considerations**:
- Linting errors found → Fix errors and re-run
- Code quality issues → Refactor and improve

---

## Task Summary

**Total Tasks**: 95 atomic tasks

**Task Distribution by Category**:
1. Environment & Project Setup: 17 tasks (T-001 to T-017)
2. Core Logic - Backend: 13 tasks (T-018 to T-030)
3. Core Logic - Frontend: 15 tasks (T-031 to T-045)
4. Testing - Backend: 9 tasks (T-046 to T-054)
5. Testing - Frontend: 4 tasks (T-055 to T-058)
6. Integration & E2E Testing: 5 tasks (T-059 to T-063)
7. Performance & Security: 6 tasks (T-064 to T-069)
8. Deployment: 10 tasks (T-070 to T-079)
9. Documentation & Finalization: 12 tasks (T-080 to T-091)
10. Verification & QA: 4 tasks (T-092 to T-095)

**Critical Path**: T-001 → T-007 → T-018 → T-024 → T-031 → T-044 → T-059 → T-079 → T-095

**Estimated Complexity**: Medium (standard full-stack CRUD with authentication)

**Key Risk Areas**:
- T-003, T-004: Better Auth customization (manual file editing)
- T-020: JWT verification middleware (security critical)
- T-060: Multi-user data isolation testing (CRITICAL for security)
- T-074, T-075, T-076: Production deployment (configuration errors possible)

**Ready for Implementation**: ✅ Yes (all tasks atomic, testable, and dependency-ordered)

---

**Tasks Document Version**: 1.0.0
**Status**: Ready for Implementation via Claude Code
**Next Step**: Begin implementation starting with T-001
**Estimated Completion**: All 95 tasks executable in sequential or limited parallel order
