# Phase II: Todo Full-Stack Web Application - Implementation Plan

**Project**: Todo Full-Stack Web Application
**Phase**: II - Web Application with Authentication
**Plan Version**: 1.0.0
**Date**: 2025-12-19
**Based on**: Specification v1.0.0, Constitution v1.3.0
**Status**: Ready for Task Breakdown

---

## 1. Implementation Phases

### Phase 0: Environment Setup & Configuration

**Purpose**: Establish development environment, configure external services, and customize Better Auth service.

**Entry Criteria:**
- Neon PostgreSQL database account created
- Better Auth service present in `/auth-service` directory
- Development machine has Node.js 18+, Python 3.13+, UV package manager

**Exit Criteria:**
- ✅ Neon database provisioned with connection string
- ✅ Better Auth schema customized (Physical AI Robotics fields removed)
- ✅ Auth service migrations applied successfully
- ✅ Environment files configured (`.env`, `.env.local`, `.env.example`)
- ✅ `BETTER_AUTH_SECRET` shared across auth-service and backend
- ✅ All services start without errors (auth:3001, backend:8000, frontend:3000)

**Key Activities:**
1. Database provisioning
2. Better Auth customization
3. Environment configuration
4. Service startup verification

---

### Phase 1: Backend Core Infrastructure

**Purpose**: Build FastAPI backend foundation with database models, authentication middleware, and core infrastructure.

**Entry Criteria:**
- Phase 0 completed
- Database connection string available
- Better Auth service running and verified

**Exit Criteria:**
- ✅ FastAPI application skeleton created (`/backend/main.py`)
- ✅ SQLModel database models defined (`Task`, `User` reference)
- ✅ Database connection and session management configured
- ✅ JWT verification middleware implemented and tested
- ✅ CORS middleware configured with explicit origins
- ✅ Health check endpoint responds successfully
- ✅ Database tables created via SQLModel `create_all()`

**Key Activities:**
1. Project structure setup
2. Database models and ORM configuration
3. Authentication middleware development
4. Infrastructure utilities (logging, error handling)

---

### Phase 2: Backend API Implementation

**Purpose**: Implement all 6 REST API endpoints for task management with authentication and authorization.

**Entry Criteria:**
- Phase 1 completed
- JWT middleware functional
- Database models and tables exist

**Exit Criteria:**
- ✅ All 6 endpoints implemented and tested:
  - `GET /api/{user_id}/tasks`
  - `POST /api/{user_id}/tasks`
  - `GET /api/{user_id}/tasks/{id}`
  - `PUT /api/{user_id}/tasks/{id}`
  - `DELETE /api/{user_id}/tasks/{id}`
  - `PATCH /api/{user_id}/tasks/{id}/complete`
- ✅ Request validation via Pydantic models
- ✅ User data isolation enforced (ownership checks)
- ✅ Error responses structured and standardized
- ✅ OpenAPI/Swagger documentation auto-generated
- ✅ Unit tests pass with ≥80% coverage

**Key Activities:**
1. Route handler implementation
2. Request/response Pydantic models
3. Database query logic with user_id filtering
4. Error handling and validation
5. Unit and integration tests

---

### Phase 3: Frontend Foundation

**Purpose**: Build Next.js frontend application structure with authentication integration and API client.

**Entry Criteria:**
- Phase 2 completed (backend API functional)
- Better Auth service accessible

**Exit Criteria:**
- ✅ Next.js 16+ App Router project initialized
- ✅ TypeScript and Tailwind CSS configured
- ✅ API client created (`/lib/api.ts`) with token management
- ✅ Authentication pages functional (signup, signin, signout)
- ✅ Better Auth integration working (JWT token flow)
- ✅ Protected route middleware implemented
- ✅ Layout and navigation components created
- ✅ Environment variables configured

**Key Activities:**
1. Next.js project setup
2. Better Auth client integration
3. API client development
4. Authentication flow implementation
5. Layout and navigation structure

---

### Phase 4: Frontend UI Implementation

**Purpose**: Build task management user interface with all CRUD operations.

**Entry Criteria:**
- Phase 3 completed (auth and API client working)
- Backend API endpoints tested and verified

**Exit Criteria:**
- ✅ Task list page displays all user tasks
- ✅ Create task form functional
- ✅ Update task inline editing working
- ✅ Delete task confirmation and execution
- ✅ Mark complete/incomplete checkbox functional
- ✅ Empty state displayed when no tasks
- ✅ Loading states and error handling implemented
- ✅ Responsive design (320px to 1920px)
- ✅ Accessibility requirements met (keyboard navigation, semantic HTML)

**Key Activities:**
1. Task list component development
2. Task form components (create, edit)
3. State management (React state/hooks)
4. UI/UX polish (loading, errors, empty states)
5. Responsive design implementation

---

### Phase 5: Integration Testing & Quality Assurance

**Purpose**: Verify end-to-end functionality, security, and performance.

**Entry Criteria:**
- Phase 4 completed (all features implemented)
- All unit tests passing

**Exit Criteria:**
- ✅ End-to-end user flows tested (signup → create task → update → delete)
- ✅ Multi-user data isolation verified
- ✅ Authentication edge cases tested (expired token, invalid credentials)
- ✅ Performance benchmarks met (API <500ms p95, page load <2s)
- ✅ Security audit passed (no secrets in repo, CORS configured, JWT verified)
- ✅ Cross-browser testing completed (Chrome, Firefox, Safari, Edge)
- ✅ Integration test suite passes
- ✅ Code quality checks pass (ESLint, Pylint)

**Key Activities:**
1. Integration test development
2. Security audit
3. Performance testing
4. Browser compatibility testing
5. Code quality validation

---

### Phase 6: Deployment Preparation

**Purpose**: Deploy application to production environments (Vercel for frontend, hosting for backend).

**Entry Criteria:**
- Phase 5 completed (all tests passing)
- Production environment variables prepared

**Exit Criteria:**
- ✅ Frontend deployed to Vercel
- ✅ Backend deployed to hosting platform (Render/Railway/DigitalOcean)
- ✅ Auth service deployed and accessible
- ✅ Production database migrations applied
- ✅ HTTPS enforced on all services
- ✅ Environment variables configured in deployment platforms
- ✅ Health checks passing in production
- ✅ Smoke tests passed on production URLs

**Key Activities:**
1. Production environment setup
2. Deployment configuration
3. Database migration execution
4. Production verification testing

---

## 2. Component Breakdown

### 2.1 Auth Service (Pre-Built, Requires Customization)

**Location**: `/auth-service`

**Responsibility**:
- User signup and signin
- Password hashing and verification
- JWT token generation and signing
- Session management
- User account CRUD in `users` table

**Customization Required**:
1. Remove custom schema fields from `src/db/schema.ts`:
   - Remove lines 3-9: `experienceLevels` and `professionalRoles` enums
   - Remove lines 21-25 from `user` table: `experienceLevel`, `professionalRole`, `roleOther`, `organization`
2. Remove `user.additionalFields` from `src/lib/auth.ts` (lines 18-44)
3. Regenerate migrations: `npm run migrate && npm run migrate:push`

**Interfaces**:
- **Outbound**: Neon PostgreSQL database (via Drizzle ORM)
- **Inbound**: HTTP REST endpoints (`/api/auth/*`)
- **Exports**: JWT tokens signed with `BETTER_AUTH_SECRET`

**Dependencies**:
- External: Better Auth v1.0.9, Hono framework, Drizzle ORM, Neon PostgreSQL
- Configuration: `BETTER_AUTH_SECRET`, `DATABASE_URL`, `CORS_ORIGINS`

---

### 2.2 Backend API (FastAPI)

**Location**: `/backend`

**Responsibility**:
- Verify JWT tokens for all protected endpoints
- Enforce user data isolation (path parameter vs token validation)
- Execute task CRUD operations with database
- Validate request payloads
- Return structured JSON responses
- Handle errors gracefully

**Internal Modules**:

#### Module: `main.py`
- FastAPI application instance
- CORS middleware configuration
- Router registration
- Startup/shutdown events (database initialization)

#### Module: `models.py`
- SQLModel definitions for `Task` entity
- Database relationship to `User` (foreign key)
- Field validation constraints

#### Module: `db.py`
- Database engine creation
- Session management (dependency injection)
- Connection pooling configuration

#### Module: `auth.py`
- JWT token verification middleware
- Token signature validation using `BETTER_AUTH_SECRET`
- User ID extraction from token claims
- Path parameter vs token user_id comparison

#### Module: `routes/tasks.py`
- 6 endpoint handlers (list, create, get, update, delete, toggle complete)
- Pydantic request/response models (`TaskCreate`, `TaskUpdate`, `TaskResponse`)
- Database queries with user_id filtering
- Ownership verification logic

#### Module: `routes/health.py`
- Health check endpoint
- Database connectivity verification

**Interfaces**:
- **Inbound**: HTTP REST API (`/api/*`)
- **Outbound**: Neon PostgreSQL (via SQLModel)
- **Exports**: JSON responses, OpenAPI schema

**Dependencies**:
- External: FastAPI, SQLModel, Pydantic, Neon PostgreSQL
- Internal: Auth service (JWT verification only, not called directly)
- Configuration: `DATABASE_URL`, `BETTER_AUTH_SECRET`, `CORS_ORIGINS`

---

### 2.3 Frontend (Next.js)

**Location**: `/frontend`

**Responsibility**:
- Render user interface
- Handle user interactions (forms, buttons, navigation)
- Call backend API via centralized client
- Manage JWT token storage and attachment
- Display error messages and loading states
- Redirect unauthenticated users to signin

**Internal Modules**:

#### Module: `app/` (App Router Pages)
- `app/layout.tsx`: Root layout with navigation
- `app/page.tsx`: Landing page (redirect to tasks if authenticated)
- `app/signup/page.tsx`: Signup form
- `app/signin/page.tsx`: Signin form
- `app/tasks/page.tsx`: Task list and management (protected route)

#### Module: `components/`
- `TaskList.tsx`: Displays array of tasks
- `TaskItem.tsx`: Individual task with edit/delete/complete actions
- `TaskForm.tsx`: Create/edit task form with validation
- `EmptyState.tsx`: Shown when no tasks exist
- `LoadingSpinner.tsx`: Loading indicator
- `ErrorMessage.tsx`: Error display component
- `Navigation.tsx`: Header with signout button

#### Module: `lib/api.ts`
- Centralized API client (fetch or axios wrapper)
- Automatic JWT token attachment to headers
- Request/response interceptors
- Error handling and transformation
- Type-safe API methods:
  - `getTasks(userId: string): Promise<Task[]>`
  - `createTask(userId: string, data: TaskCreate): Promise<Task>`
  - `updateTask(userId: string, id: number, data: TaskUpdate): Promise<Task>`
  - `deleteTask(userId: string, id: number): Promise<void>`
  - `toggleComplete(userId: string, id: number): Promise<Task>`

#### Module: `lib/auth.ts`
- Better Auth client initialization
- Token storage (localStorage or cookie)
- Authentication state management
- Signup/signin/signout functions

#### Module: `middleware.ts`
- Protected route middleware
- Redirect to signin if no token
- Token validation before page render

**Interfaces**:
- **Inbound**: User browser interactions
- **Outbound**: Better Auth service (`/api/auth/*`), Backend API (`/api/*`)
- **Exports**: HTML/CSS/JavaScript to browser

**Dependencies**:
- External: Next.js 16+, React, Tailwind CSS, Better Auth client, TypeScript
- Internal: Backend API, Auth service
- Configuration: `NEXT_PUBLIC_AUTH_URL`, `NEXT_PUBLIC_API_URL`

---

### 2.4 Database (Neon PostgreSQL)

**Location**: Remote (Neon cloud)

**Responsibility**:
- Persist user accounts and tasks
- Enforce foreign key constraints
- Provide ACID transaction guarantees
- Auto-generate IDs and timestamps

**Schema**:

**Table: `users`** (managed by Better Auth)
- `id` (string, PK)
- `email` (string, unique)
- `name` (string, nullable)
- `emailVerified` (boolean)
- `image` (string, nullable)
- `createdAt` (timestamp)
- `updatedAt` (timestamp)

**Table: `tasks`**
- `id` (integer, PK, auto-increment)
- `user_id` (string, FK → users.id, NOT NULL)
- `title` (string, max 200, NOT NULL)
- `description` (string, max 1000, nullable)
- `completed` (boolean, default false)
- `created_at` (timestamp, auto-generated)
- `updated_at` (timestamp, auto-updated)

**Indexes**:
- `tasks.user_id` (for user-scoped queries)
- `tasks.id` (primary key, automatic)

**Constraints**:
- Foreign key: `tasks.user_id → users.id`
- Cascade behavior: ON DELETE CASCADE (recommended)

**Interfaces**:
- **Inbound**: SQL queries from auth-service (Drizzle ORM) and backend (SQLModel)
- **Outbound**: None
- **Exports**: Query results

**Dependencies**:
- External: Neon PostgreSQL cloud service
- Configuration: `DATABASE_URL` connection string

---

## 3. Data & State Handling Plan

### 3.1 User Account Lifecycle

**Creation (Signup Flow)**:
1. User submits signup form on frontend
2. Frontend validates email format and password strength (client-side)
3. Frontend sends POST to auth-service `/api/auth/signup/email`
4. Auth-service validates uniqueness of email (database query)
5. Auth-service hashes password using bcrypt/argon2
6. Auth-service inserts record into `users` table
7. Auth-service generates JWT token with claims: `{ user_id, email, exp }`
8. Auth-service returns token to frontend
9. Frontend stores token in localStorage/cookie
10. Frontend redirects to `/tasks` page

**Read (Session Verification)**:
1. Frontend attaches JWT token to API request headers
2. Backend middleware extracts token from `Authorization: Bearer <token>`
3. Backend verifies token signature using `BETTER_AUTH_SECRET`
4. Backend decodes token to get `user_id` claim
5. Backend compares token `user_id` with path parameter `{user_id}`
6. If match: proceed to endpoint logic
7. If mismatch: return `403 Forbidden`

**Update**:
- Out of scope for Phase II (user profile updates not required)

**Delete**:
- Out of scope for Phase II (account deletion not required)

---

### 3.2 Task Lifecycle

**Creation**:
1. User fills task form on frontend (title, optional description)
2. Frontend validates: title 1-200 chars, description max 1000 chars
3. Frontend sends POST to backend `/api/{user_id}/tasks` with JWT token
4. Backend middleware verifies JWT and user_id match
5. Backend validates request body via Pydantic `TaskCreate` model
6. Backend creates new `Task` object with:
   - `user_id` = extracted from JWT token
   - `title` = request body
   - `description` = request body (nullable)
   - `completed` = False (default)
   - `created_at` = NOW() (auto-generated)
   - `updated_at` = NOW() (auto-generated)
7. Backend inserts record into database via SQLModel session
8. Backend commits transaction
9. Backend returns task object with auto-generated `id`
10. Frontend adds task to local state and re-renders list

**Read (List All Tasks)**:
1. Frontend sends GET to backend `/api/{user_id}/tasks` with JWT token
2. Backend verifies JWT and user_id
3. Backend executes query: `SELECT * FROM tasks WHERE user_id = ?` (parameterized)
4. Database returns result set
5. Backend serializes to JSON array of task objects
6. Frontend receives array and renders `TaskList` component
7. If empty: display `EmptyState` component

**Read (Single Task)**:
1. Frontend sends GET to backend `/api/{user_id}/tasks/{id}` with JWT token
2. Backend verifies JWT and user_id
3. Backend executes query: `SELECT * FROM tasks WHERE id = ? AND user_id = ?`
4. If not found: return `404 Not Found`
5. If found: return task object
6. Frontend displays task details

**Update**:
1. User edits task inline or in modal
2. Frontend sends PUT to backend `/api/{user_id}/tasks/{id}` with updated fields
3. Backend verifies JWT and user_id
4. Backend validates request body via Pydantic `TaskUpdate` model
5. Backend executes query: `SELECT * FROM tasks WHERE id = ? AND user_id = ?`
6. If not found or ownership mismatch: return `403 Forbidden` or `404 Not Found`
7. Backend updates record fields (title, description)
8. Backend sets `updated_at = NOW()`
9. Backend commits transaction
10. Backend returns updated task object
11. Frontend updates local state and re-renders

**Delete**:
1. User clicks delete button (confirmation dialog recommended)
2. Frontend sends DELETE to backend `/api/{user_id}/tasks/{id}` with JWT token
3. Backend verifies JWT and user_id
4. Backend executes query: `SELECT * FROM tasks WHERE id = ? AND user_id = ?`
5. If not found or ownership mismatch: return `403 Forbidden` or `404 Not Found`
6. Backend deletes record: `DELETE FROM tasks WHERE id = ?`
7. Backend commits transaction
8. Backend returns `204 No Content`
9. Frontend removes task from local state and re-renders

**Toggle Completion**:
1. User clicks checkbox
2. Frontend sends PATCH to backend `/api/{user_id}/tasks/{id}/complete` with JWT token
3. Backend verifies JWT and user_id
4. Backend executes query: `SELECT * FROM tasks WHERE id = ? AND user_id = ?`
5. Backend toggles `completed` boolean: `NOT completed`
6. Backend sets `updated_at = NOW()`
7. Backend commits transaction
8. Backend returns updated task object
9. Frontend updates local state and re-renders (checkbox reflects new state)

---

### 3.3 In-Memory vs Persistent Strategy

**Persistent (Database)**:
- User accounts (`users` table)
- Tasks (`tasks` table)
- Authentication sessions (managed by Better Auth in `session` table)

**In-Memory (Transient)**:
- JWT tokens (validated cryptographically, not stored server-side)
- Frontend React component state (task list cache)
- Backend request/response cycles (stateless)

**Validation Strategy**:
- **Client-side (Frontend)**: Zod schemas for immediate feedback (title length, description length)
- **Server-side (Backend)**: Pydantic models for security and consistency (reject invalid data)
- **Database-level**: Foreign key constraints, NOT NULL constraints, unique constraints

**Consistency Strategy**:
- **Single Source of Truth**: Database is authoritative
- **Optimistic Updates**: Frontend updates UI immediately, rolls back on API error
- **Error Handling**: Backend returns structured errors, frontend displays user-friendly messages
- **Transaction Isolation**: Use database transactions for create/update/delete to ensure ACID properties

---

## 4. Control Flow & User Flow

### 4.1 Happy Path: Complete User Journey

**Step 1: User Visits Application**
1. Browser navigates to frontend URL (`http://localhost:3000` or production)
2. Frontend checks for JWT token in localStorage/cookie
3. If token exists: redirect to `/tasks`
4. If no token: display landing page with "Sign Up" and "Sign In" buttons

**Step 2: User Signs Up**
1. User clicks "Sign Up"
2. Frontend renders signup form (email, password, name fields)
3. User fills form and submits
4. Frontend validates:
   - Email format (regex)
   - Password strength (min 8 chars)
5. Frontend sends POST to auth-service `/api/auth/signup/email`
6. Auth-service validates:
   - Email uniqueness (database query)
   - Password meets requirements
7. Auth-service hashes password
8. Auth-service inserts user into `users` table
9. Auth-service generates JWT token
10. Auth-service returns `{ user, token }` in response
11. Frontend stores token
12. Frontend redirects to `/tasks`

**Step 3: User Views Task List**
1. Frontend middleware checks for token (exists from signup)
2. Frontend extracts `user_id` from token
3. Frontend sends GET to backend `/api/{user_id}/tasks`
4. Backend verifies JWT signature
5. Backend compares token `user_id` with path `{user_id}` (match)
6. Backend queries database: `SELECT * FROM tasks WHERE user_id = ?`
7. Database returns empty array (new user)
8. Backend returns `[]`
9. Frontend renders `EmptyState` component: "No tasks yet. Create your first task!"

**Step 4: User Creates First Task**
1. User clicks "Add Task" button
2. Frontend displays task form modal/inline
3. User types: Title = "Buy groceries", Description = "Milk, eggs, bread"
4. User submits form
5. Frontend validates title length (within 1-200 chars)
6. Frontend sends POST to backend `/api/{user_id}/tasks` with `{ title, description }`
7. Backend verifies JWT
8. Backend validates via Pydantic `TaskCreate` model
9. Backend creates `Task` object with `user_id` from token
10. Backend inserts into database
11. Database auto-generates `id = 1`, `created_at`, `updated_at`
12. Backend returns task object
13. Frontend adds task to local state
14. Frontend re-renders list with new task

**Step 5: User Marks Task Complete**
1. User clicks checkbox next to "Buy groceries"
2. Frontend sends PATCH to backend `/api/{user_id}/tasks/1/complete`
3. Backend verifies JWT and ownership
4. Backend toggles `completed` from `false` to `true`
5. Backend updates `updated_at` timestamp
6. Backend returns updated task object
7. Frontend updates local state
8. Frontend re-renders: checkbox checked, task title may have strikethrough styling

**Step 6: User Updates Task**
1. User clicks "Edit" on task
2. Frontend displays edit form pre-filled with current title/description
3. User changes title to "Buy groceries and fruits"
4. User submits
5. Frontend sends PUT to backend `/api/{user_id}/tasks/1` with `{ title: "Buy groceries and fruits" }`
6. Backend verifies JWT and ownership
7. Backend updates record, sets `updated_at`
8. Backend returns updated task
9. Frontend updates local state and re-renders

**Step 7: User Deletes Task**
1. User clicks "Delete" button
2. Frontend shows confirmation dialog: "Are you sure?"
3. User confirms
4. Frontend sends DELETE to backend `/api/{user_id}/tasks/1`
5. Backend verifies JWT and ownership
6. Backend deletes record from database
7. Backend returns `204 No Content`
8. Frontend removes task from local state
9. Frontend re-renders: task list empty again

**Step 8: User Signs Out**
1. User clicks "Sign Out" button in navigation
2. Frontend sends POST to auth-service `/api/auth/signout`
3. Auth-service invalidates session (if using session-based auth)
4. Frontend clears JWT token from localStorage/cookie
5. Frontend redirects to landing page or signin page

---

### 4.2 Error Paths

**Error Path 1: Signup with Duplicate Email**
1. User submits signup form with existing email
2. Auth-service checks database: email already exists
3. Auth-service returns `409 Conflict` with error message
4. Frontend displays error: "Email already registered. Please sign in."

**Error Path 2: Signin with Wrong Password**
1. User submits signin form with incorrect password
2. Auth-service verifies email exists, compares hashed password
3. Password mismatch detected
4. Auth-service returns `401 Unauthorized` with generic message
5. Frontend displays error: "Invalid email or password."

**Error Path 3: Expired JWT Token**
1. User returns to app after 7 days (token expired)
2. Frontend sends API request with expired token
3. Backend verifies token signature: valid
4. Backend checks expiration claim: expired
5. Backend returns `401 Unauthorized`
6. Frontend catches error, clears token, redirects to signin

**Error Path 4: User ID Mismatch (Attempted Unauthorized Access)**
1. Malicious user modifies frontend code to access `/api/other-user-id/tasks`
2. Frontend sends request with their valid JWT but wrong user_id in path
3. Backend verifies JWT: valid signature
4. Backend compares token `user_id` with path `{user_id}`: mismatch
5. Backend returns `403 Forbidden` with error message
6. Frontend displays error: "Unauthorized access."

**Error Path 5: Create Task with Empty Title**
1. User submits task form with empty title
2. Frontend validation catches error before API call
3. Frontend displays inline error: "Title is required."
4. If validation bypassed (direct API call):
   - Backend Pydantic validation fails
   - Backend returns `400 Bad Request` with validation errors
   - Frontend displays error message

**Error Path 6: Database Connection Failure**
1. Backend receives API request
2. Backend attempts database query
3. Database connection fails (network issue, Neon downtime)
4. SQLModel raises exception
5. Backend catches exception in global error handler
6. Backend logs detailed error server-side
7. Backend returns `503 Service Unavailable` with generic message to client
8. Frontend displays error: "Service temporarily unavailable. Please try again."

**Error Path 7: Task Not Found**
1. User attempts to view task with non-existent ID
2. Backend queries database: no results
3. Backend returns `404 Not Found`
4. Frontend displays error: "Task not found."

---

### 4.3 Edge-Case Handling Strategy

**Edge Case: Concurrent Updates to Same Task**
- **Scenario**: User has app open in two browser tabs, edits same task in both
- **Strategy**: Last write wins (timestamp-based)
- **Handling**: Both updates succeed sequentially, `updated_at` reflects actual last update time
- **No conflict resolution**: Accept eventual consistency

**Edge Case: Long Titles/Descriptions**
- **Scenario**: User pastes 500-character title
- **Client Validation**: Truncate or show error before API call
- **Server Validation**: Pydantic rejects, returns `400 Bad Request`
- **Handling**: Display character count in form, disable submit when limit exceeded

**Edge Case: Special Characters in Input**
- **Scenario**: User enters SQL injection attempt: `'; DROP TABLE tasks;--`
- **Handling**: SQLModel uses parameterized queries, input is safely escaped
- **Validation**: Pydantic accepts as regular string, no special processing needed
- **Storage**: Stored as-is in database, rendered safely by React (auto-escaped)

**Edge Case: Network Timeout**
- **Scenario**: API request takes >30 seconds (slow network)
- **Client Handling**: Implement request timeout (e.g., 10 seconds)
- **Server Handling**: FastAPI default timeout enforced
- **User Feedback**: Display "Request timed out. Please try again."

**Edge Case: Malformed JWT**
- **Scenario**: Token tampered with or corrupted
- **Handling**: Backend JWT verification fails (signature mismatch)
- **Response**: `401 Unauthorized`
- **Frontend Action**: Clear token, redirect to signin

**Edge Case: User Deletes Task Being Viewed**
- **Scenario**: User deletes task, then tries to edit it
- **Handling**: Backend returns `404 Not Found` on subsequent edit request
- **Frontend Action**: Redirect to task list, show message "Task no longer exists"

**Edge Case: Rapid Create Requests (Spam)**
- **Scenario**: User clicks "Create Task" button rapidly
- **Client Prevention**: Disable button after first click until response received
- **Server Handling**: Each request processed independently (no rate limiting in Phase II)
- **Database**: Foreign key constraint ensures all tasks have valid user_id

---

## 5. Testing Strategy Plan

### 5.1 Phase 0 Testing: Environment Verification

**What to Test**:
- Auth service starts without errors
- Database connection succeeds
- Migrations apply successfully
- Environment variables loaded correctly

**How to Test**:
- Manual verification: Start each service, check logs
- Health check endpoints respond with 200 OK
- Database query via Drizzle/SQLModel succeeds

**Validation**:
- All services running on correct ports
- No error logs on startup
- Database tables exist and match schema

---

### 5.2 Phase 1 Testing: Backend Infrastructure

**Unit Tests**:

**Test Suite: `tests/test_models.py`**
- `test_task_model_creation()`: Task object initializes with defaults
- `test_task_title_required()`: Missing title raises validation error
- `test_task_title_max_length()`: Title >200 chars raises error
- `test_task_description_nullable()`: Description can be None
- `test_task_user_id_required()`: Missing user_id raises error

**Test Suite: `tests/test_auth_middleware.py`**
- `test_verify_jwt_valid_token()`: Valid token decodes successfully
- `test_verify_jwt_expired_token()`: Expired token raises exception
- `test_verify_jwt_invalid_signature()`: Tampered token rejected
- `test_verify_jwt_missing_user_id()`: Token without user_id claim rejected
- `test_user_id_path_mismatch()`: Token user_id != path user_id returns 403

**Integration Tests**:
- Database connection pool creates sessions
- SQLModel `create_all()` creates tables
- Health check endpoint returns 200 OK

**Acceptance Criteria**:
- All unit tests pass
- Database tables created successfully
- JWT middleware correctly validates/rejects tokens

---

### 5.3 Phase 2 Testing: Backend API Endpoints

**Unit Tests**:

**Test Suite: `tests/test_routes_tasks.py`**
- `test_list_tasks_empty()`: GET returns [] for user with no tasks
- `test_list_tasks_filters_by_user()`: User A sees only their tasks, not User B's
- `test_create_task_success()`: POST with valid data returns 201 and task object
- `test_create_task_empty_title()`: POST with empty title returns 400
- `test_create_task_title_too_long()`: POST with 201-char title returns 400
- `test_get_task_success()`: GET /tasks/{id} returns task for owner
- `test_get_task_not_found()`: GET non-existent task returns 404
- `test_get_task_wrong_user()`: User B accessing User A's task returns 403
- `test_update_task_success()`: PUT with valid data returns updated task
- `test_update_task_partial()`: PUT with only title updates title only
- `test_update_task_ownership()`: User B cannot update User A's task
- `test_delete_task_success()`: DELETE returns 204, task removed from DB
- `test_delete_task_not_found()`: DELETE non-existent task returns 404
- `test_toggle_complete_true()`: PATCH sets completed=true
- `test_toggle_complete_false()`: PATCH toggles back to completed=false

**Integration Tests**:
- Full CRUD cycle: Create → Read → Update → Delete
- Multi-user isolation: Create users A and B, verify data separation
- Authentication flow: Invalid token returns 401, valid token succeeds

**Acceptance Criteria**:
- All 6 endpoints functional
- ≥80% code coverage
- All tests pass
- OpenAPI docs accessible at `/docs`

---

### 5.4 Phase 3 Testing: Frontend Authentication

**Unit Tests**:

**Test Suite: `frontend/__tests__/lib/auth.test.ts`**
- `test_signup_stores_token()`: Successful signup saves JWT to storage
- `test_signin_redirects_to_tasks()`: Successful signin redirects
- `test_signout_clears_token()`: Signout removes token from storage

**Integration Tests**:
- Signup → Signin → Access protected route → Signout flow
- Protected route redirects to signin when no token
- Invalid credentials display error message

**Acceptance Criteria**:
- Authentication flows work end-to-end
- Token persists across page refreshes
- Expired token triggers re-authentication

---

### 5.5 Phase 4 Testing: Frontend UI

**Unit Tests**:

**Test Suite: `frontend/__tests__/components/TaskList.test.tsx`**
- `test_renders_empty_state()`: Shows "No tasks" when list empty
- `test_renders_task_items()`: Displays tasks with title and description
- `test_delete_button_calls_handler()`: Clicking delete triggers callback

**Test Suite: `frontend/__tests__/components/TaskForm.test.tsx`**
- `test_submits_valid_task()`: Form submission calls onCreate
- `test_validates_empty_title()`: Empty title shows error
- `test_validates_title_length()`: Title >200 chars shows error

**Integration Tests**:
- Create task → Appears in list immediately
- Update task → UI reflects changes
- Delete task → Removed from list
- Toggle complete → Checkbox state updates

**Acceptance Criteria**:
- All UI components render correctly
- CRUD operations work end-to-end
- Form validation prevents invalid submissions
- Responsive design works on mobile and desktop

---

### 5.6 Phase 5 Testing: End-to-End & Quality

**End-to-End Tests**:

**Test Scenario: New User Complete Flow**
1. Visit app → See landing page
2. Sign up with email/password → Account created
3. Redirected to empty task list → See "No tasks" message
4. Create task "Buy groceries" → Task appears
5. Mark task complete → Checkbox checked
6. Update task title → Title changes
7. Delete task → Task removed
8. Sign out → Redirected to landing page

**Test Scenario: Multi-User Isolation**
1. Create User A, create task
2. Create User B, create task
3. User A cannot see User B's task
4. User B cannot access User A's task endpoint (403 error)

**Performance Tests**:
- API response time: Measure p95 latency for list tasks (should be <500ms)
- Page load time: Measure initial render (should be <2s on 3G)
- Load test: 100 concurrent users creating tasks (backend handles gracefully)

**Security Tests**:
- Secrets audit: `git grep -i 'password\|secret\|api_key'` returns no hardcoded values
- CORS test: Cross-origin request from unauthorized domain blocked
- SQL injection test: Malicious input safely escaped
- JWT tampering test: Modified token rejected

**Browser Compatibility**:
- Chrome: All features work
- Firefox: All features work
- Safari: All features work
- Edge: All features work

**Acceptance Criteria**:
- All end-to-end scenarios pass
- Performance benchmarks met
- Security audit clean
- Cross-browser compatibility verified

---

### 5.7 Phase 6 Testing: Production Verification

**Smoke Tests** (Run on production URLs):
- Frontend loads without errors
- Signup creates account successfully
- Signin authenticates and redirects
- Create task persists to database
- HTTPS enforced (HTTP redirects)

**Health Checks**:
- Backend `/health` endpoint returns 200 OK
- Auth service `/health` endpoint returns 200 OK
- Database connection successful

**Acceptance Criteria**:
- All smoke tests pass in production
- No console errors in browser
- Services accessible via HTTPS

---

## 6. Risk & Complexity Management

### 6.1 High-Risk Areas

**Risk 1: Better Auth Schema Customization**

**Risk Level**: High
**Impact**: If customization fails, auth service won't match spec (extra fields remain)
**Likelihood**: Medium

**Mitigation**:
1. Follow constitution's step-by-step guide exactly (lines 266-299)
2. Test on development database first (not production)
3. Back up current schema before modifications
4. Verify schema changes with: `npx drizzle-kit studio` (visual inspection)
5. Test signup/signin after migration to confirm no breaking changes

**Rollback Plan**:
- Restore original schema files from git
- Drop and recreate database tables if needed

---

**Risk 2: JWT Secret Mismatch**

**Risk Level**: High
**Impact**: All API calls fail authentication (backend cannot verify tokens)
**Likelihood**: Low (with proper setup)

**Mitigation**:
1. Generate secret once: `openssl rand -hex 32`
2. Set in `.env` files for both services before first run
3. Add startup validation: Backend logs first 8 chars of secret on startup (verify match)
4. Document secret generation in README

**Validation**:
- Test signup → signin → API call flow before proceeding to Phase 3
- Backend logs should show successful JWT verification

---

**Risk 3: CORS Configuration Errors**

**Risk Level**: Medium
**Impact**: Frontend cannot call backend API (blocked by browser)
**Likelihood**: Medium

**Mitigation**:
1. Set explicit origins in both backend and auth-service `.env`:
   ```
   CORS_ORIGINS=http://localhost:3000,http://localhost:8000
   ```
2. Test cross-origin request early in Phase 2
3. Production: Add Vercel frontend URL to CORS_ORIGINS before deployment

**Testing**:
- Open browser DevTools Network tab
- Look for CORS errors when calling API
- Verify `Access-Control-Allow-Origin` header in response

---

**Risk 4: Database Connection Pool Exhaustion**

**Risk Level**: Low
**Impact**: Backend becomes unresponsive under load
**Likelihood**: Low (in Phase II with limited users)

**Mitigation**:
1. Configure SQLModel connection pool size (default: 20)
2. Monitor Neon dashboard for connection usage
3. Use connection pooling best practices (close sessions after use)

**Monitoring**:
- Neon dashboard shows active connections
- Backend logs should not show "too many connections" errors

---

**Risk 5: Data Isolation Breach (Ownership Bug)**

**Risk Level**: Critical
**Impact**: User can access another user's data (security violation)
**Likelihood**: Low (with thorough testing)

**Mitigation**:
1. Enforce ownership checks in every endpoint handler
2. Write explicit integration tests for multi-user isolation
3. Code review all database queries for `user_id` filtering
4. Never use `SELECT * FROM tasks` without WHERE clause

**Testing**:
- Create two test users, verify neither can access other's tasks
- Attempt API calls with mismatched user_id in path (expect 403)
- Review all SQLModel queries for user_id filter

---

### 6.2 Complexity Areas

**Complex Area 1: JWT Token Flow**

**Complexity**: Medium
**Why**: Token generation (auth-service) vs verification (backend) involves shared secret, expiration handling, and claim extraction

**Strategy**:
1. Implement and test JWT verification middleware first (Phase 1)
2. Use well-tested JWT library (PyJWT for Python)
3. Document token structure and claims clearly
4. Test expired token handling explicitly

---

**Complex Area 2: React State Management**

**Complexity**: Medium
**Why**: Keeping frontend task list in sync with backend requires optimistic updates and error rollback

**Strategy**:
1. Use simple React useState for task list (no Redux/Zustand needed in Phase II)
2. Implement optimistic updates: Update UI immediately, revert on API error
3. Use React Query or SWR for caching (optional, simplifies state management)
4. Test error scenarios explicitly (API failure after optimistic update)

---

**Complex Area 3: Database Migrations**

**Complexity**: Low
**Why**: Better Auth handles migrations automatically, backend uses SQLModel create_all()

**Strategy**:
1. Better Auth: Use `npm run migrate && npm run migrate:push` after schema changes
2. Backend: SQLModel `create_all()` on startup (creates tables if not exist)
3. Production: Run migrations before deploying new code
4. Test migrations on development database first

---

### 6.3 Assumptions That Must Hold

**Assumption 1: Neon Database Availability**

**Must Hold**: Neon PostgreSQL service is available and accessible 99.9% of the time
**Validation**: Monitor Neon status page, configure connection retries
**Fallback**: If Neon fails, application returns 503 Service Unavailable (graceful degradation)

---

**Assumption 2: Better Auth Compatibility**

**Must Hold**: Better Auth v1.0.9 works with our customized schema (removing extra fields)
**Validation**: Test auth flows after schema customization
**Fallback**: If issues arise, keep minimal custom fields or use different auth library

---

**Assumption 3: Stateless Backend**

**Must Hold**: Backend does not rely on in-memory session state
**Validation**: Restart backend mid-session, verify user can still access tasks with valid JWT
**Importance**: Required for horizontal scaling in later phases

---

**Assumption 4: JWT Token Security**

**Must Hold**: `BETTER_AUTH_SECRET` remains secret (not committed to git, not exposed)
**Validation**: Audit git history, check `.gitignore` includes `.env`
**Importance**: Compromised secret allows attacker to forge tokens

---

## 7. Implementation Order

### 7.1 Strict Dependency Order

**Phase 0: Environment Setup** (No dependencies)
1. ✅ Create Neon PostgreSQL database
2. ✅ Obtain `DATABASE_URL` connection string
3. ✅ Customize Better Auth schema (remove custom fields)
4. ✅ Generate `BETTER_AUTH_SECRET` with `openssl rand -hex 32`
5. ✅ Create `.env` files for auth-service, backend, frontend
6. ✅ Run auth-service migrations: `npm run migrate && npm run migrate:push`
7. ✅ Start auth-service, verify `/health` endpoint
8. ✅ Verify auth service database tables created

**Phase 1: Backend Infrastructure** (Depends on: Phase 0 complete)
1. ✅ Create backend directory structure (`/backend/main.py`, `/backend/models.py`, etc.)
2. ✅ Install dependencies: `uv pip install fastapi sqlmodel pyjwt python-jose uvicorn`
3. ✅ Implement `db.py`: Database engine, session management
4. ✅ Implement `models.py`: `Task` SQLModel definition
5. ✅ Implement `main.py`: FastAPI app, CORS middleware, router registration
6. ✅ Implement `auth.py`: JWT verification middleware
7. ✅ Implement `routes/health.py`: Health check endpoint
8. ✅ Write unit tests for models and auth middleware
9. ✅ Run tests, verify all pass
10. ✅ Start backend, verify `/health` responds 200 OK
11. ✅ Verify database `tasks` table created

**Phase 2: Backend API** (Depends on: Phase 1 complete)
1. ✅ Create `routes/tasks.py` with route stubs (empty handlers)
2. ✅ Implement Pydantic models: `TaskCreate`, `TaskUpdate`, `TaskResponse`
3. ✅ Implement `POST /api/{user_id}/tasks` (create task)
4. ✅ Write unit tests for create endpoint
5. ✅ Implement `GET /api/{user_id}/tasks` (list tasks)
6. ✅ Write unit tests for list endpoint
7. ✅ Implement `GET /api/{user_id}/tasks/{id}` (get single task)
8. ✅ Write unit tests for get endpoint
9. ✅ Implement `PUT /api/{user_id}/tasks/{id}` (update task)
10. ✅ Write unit tests for update endpoint
11. ✅ Implement `DELETE /api/{user_id}/tasks/{id}` (delete task)
12. ✅ Write unit tests for delete endpoint
13. ✅ Implement `PATCH /api/{user_id}/tasks/{id}/complete` (toggle complete)
14. ✅ Write unit tests for toggle endpoint
15. ✅ Run all tests, verify ≥80% coverage
16. ✅ Test API endpoints manually with curl/Postman
17. ✅ Verify OpenAPI docs at `/docs`

**Phase 3: Frontend Foundation** (Depends on: Phase 2 complete)
1. ✅ Create Next.js project: `npx create-next-app@latest frontend --typescript --tailwind --app`
2. ✅ Install dependencies: `npm install axios zod`
3. ✅ Install Better Auth client: `npm install better-auth`
4. ✅ Create `.env.local` with `NEXT_PUBLIC_AUTH_URL`, `NEXT_PUBLIC_API_URL`
5. ✅ Implement `lib/auth.ts`: Better Auth client initialization, signup/signin/signout functions
6. ✅ Implement `lib/api.ts`: Centralized API client with token attachment
7. ✅ Create `app/layout.tsx`: Root layout with navigation
8. ✅ Create `app/signup/page.tsx`: Signup form
9. ✅ Create `app/signin/page.tsx`: Signin form
10. ✅ Implement `middleware.ts`: Protected route logic
11. ✅ Test authentication flow: Signup → stores token → redirects to /tasks
12. ✅ Test signin flow: Signin → stores token → redirects to /tasks
13. ✅ Test protected route: Access /tasks without token → redirects to signin

**Phase 4: Frontend UI** (Depends on: Phase 3 complete)
1. ✅ Create `components/TaskList.tsx`: Renders array of tasks
2. ✅ Create `components/TaskItem.tsx`: Individual task with actions
3. ✅ Create `components/TaskForm.tsx`: Create/edit form with validation
4. ✅ Create `components/EmptyState.tsx`: "No tasks" message
5. ✅ Create `components/LoadingSpinner.tsx`: Loading indicator
6. ✅ Create `components/ErrorMessage.tsx`: Error display
7. ✅ Implement `app/tasks/page.tsx`: Task management page
8. ✅ Implement create task flow: Form submission → API call → list update
9. ✅ Implement update task flow: Inline edit → API call → list update
10. ✅ Implement delete task flow: Button click → confirmation → API call → list update
11. ✅ Implement toggle complete flow: Checkbox → API call → list update
12. ✅ Implement loading states for all async operations
13. ✅ Implement error handling for all API calls
14. ✅ Test responsive design on mobile (320px) and desktop (1920px)
15. ✅ Test keyboard navigation (tab order, Enter/Space activation)
16. ✅ Write unit tests for components
17. ✅ Run tests, verify all pass

**Phase 5: Integration Testing** (Depends on: Phase 4 complete)
1. ✅ Write end-to-end test: Signup → Create task → Update → Delete → Signout
2. ✅ Write multi-user isolation test: User A and User B have separate data
3. ✅ Run performance tests: API response time, page load time
4. ✅ Run security audit: Check for secrets in git, verify CORS, test SQL injection
5. ✅ Test cross-browser compatibility (Chrome, Firefox, Safari, Edge)
6. ✅ Run code quality checks: ESLint, Pylint
7. ✅ Fix any failing tests or quality issues
8. ✅ Verify all acceptance criteria met

**Phase 6: Deployment** (Depends on: Phase 5 complete)
1. ✅ Create Vercel account, link GitHub repository
2. ✅ Configure Vercel environment variables (`NEXT_PUBLIC_AUTH_URL`, `NEXT_PUBLIC_API_URL`)
3. ✅ Deploy frontend to Vercel
4. ✅ Create Render/Railway/DigitalOcean account
5. ✅ Configure backend environment variables (`DATABASE_URL`, `BETTER_AUTH_SECRET`, `CORS_ORIGINS`)
6. ✅ Deploy backend to hosting platform
7. ✅ Deploy auth-service to hosting platform (or same instance as backend)
8. ✅ Update `CORS_ORIGINS` to include production frontend URL
9. ✅ Run database migrations on production database
10. ✅ Test signup on production URL
11. ✅ Test task creation on production
12. ✅ Verify HTTPS enforced
13. ✅ Run smoke tests on production
14. ✅ Monitor logs for errors
15. ✅ Verify health checks passing

---

### 7.2 Parallel Work Opportunities

**Parallel Stream 1 & 2** (After Phase 0):
- Stream 1: Backend development (Phase 1 → Phase 2)
- Stream 2: Frontend design system (Tailwind components, layout)
- **Sync Point**: Backend API must be functional before frontend can integrate (Phase 2 → Phase 3)

**Parallel Stream 3** (During Phase 4):
- Stream A: Frontend UI implementation
- Stream B: Unit test writing for existing backend code
- **Sync Point**: Both complete before Phase 5 integration testing

**Not Parallelizable**:
- Phase 0 must complete first (all services depend on environment setup)
- Phase 3 depends on Phase 2 (frontend needs working API)
- Phase 5 depends on Phase 4 (can't test what's not built)
- Phase 6 depends on Phase 5 (can't deploy failing tests)

---

## 8. Definition of Done

### 8.1 Phase II Completion Checklist

**Functional Requirements (All FR-* from Spec):**
- [ ] FR-AUTH-01: User can sign up with email/password
- [ ] FR-AUTH-02: User can sign in with valid credentials
- [ ] FR-AUTH-03: User can sign out
- [ ] FR-AUTH-04: Session persists across page refreshes (within 7-day window)
- [ ] FR-AUTH-05: Better Auth schema customized (Physical AI fields removed)
- [ ] FR-TASK-01: User can create task with title and optional description
- [ ] FR-TASK-02: User can view list of all their tasks (only their own)
- [ ] FR-TASK-03: User can view single task details
- [ ] FR-TASK-04: User can update task title and description
- [ ] FR-TASK-05: User can delete task
- [ ] FR-TASK-06: User can mark task as complete/incomplete
- [ ] FR-ISOLATION-01: Path parameter user_id enforced (matches JWT token)
- [ ] FR-ISOLATION-02: All database queries filter by user_id
- [ ] FR-ISOLATION-03: Error messages do not leak data

**Non-Functional Requirements:**
- [ ] NFR-PERF-01: API p95 latency <500ms
- [ ] NFR-PERF-01: Page load time <2s on 3G
- [ ] NFR-SEC-01: All API endpoints require authentication (except auth routes)
- [ ] NFR-SEC-02: Input validation via Pydantic (backend) and Zod (frontend)
- [ ] NFR-SEC-03: No secrets in git repository (`.env` in `.gitignore`)
- [ ] NFR-SEC-04: HTTPS enforced in production
- [ ] NFR-REL-01: Structured JSON error responses
- [ ] NFR-REL-02: Foreign key constraints enforced
- [ ] NFR-SCALE-01: Backend is stateless (no in-memory sessions)
- [ ] NFR-MAINT-01: Code follows PEP 8 (Python) and ESLint (TypeScript)
- [ ] NFR-MAINT-02: README with setup instructions exists
- [ ] NFR-MAINT-03: ≥80% test coverage for task CRUD operations
- [ ] NFR-ACCESS-01: Semantic HTML, keyboard accessible
- [ ] NFR-ACCESS-02: Responsive design (320px to 1920px)

**Testing:**
- [ ] All unit tests pass (backend and frontend)
- [ ] All integration tests pass
- [ ] End-to-end user flow tested (signup → create → update → delete → signout)
- [ ] Multi-user data isolation verified
- [ ] Performance benchmarks met
- [ ] Security audit clean (no secrets, CORS configured, SQL injection prevented)
- [ ] Cross-browser compatibility verified (Chrome, Firefox, Safari, Edge)

**Deployment:**
- [ ] Frontend deployed to Vercel and accessible via HTTPS
- [ ] Backend deployed to hosting platform and accessible via HTTPS
- [ ] Auth service deployed and accessible
- [ ] Production database migrations applied
- [ ] Health checks passing in production
- [ ] Smoke tests pass on production URLs

**Documentation:**
- [ ] README.md includes setup instructions
- [ ] README.md documents environment variables
- [ ] README.md includes running instructions (dev and production)
- [ ] CLAUDE.md exists with Claude Code guidance
- [ ] OpenAPI/Swagger docs accessible at `/docs`

**Code Quality:**
- [ ] ESLint passes with 0 errors (frontend)
- [ ] Pylint passes with 0 errors (backend)
- [ ] No console.log statements in production frontend code
- [ ] No commented-out code blocks
- [ ] No TODO comments in critical paths

**Constitutional Compliance:**
- [ ] Spec-Driven Development: All code generated via Claude Code from refined specs
- [ ] API-First Design: Backend endpoints implemented before frontend
- [ ] Test-First Development: Tests written and passing before deployment
- [ ] Security by Default: Authentication, input validation, data isolation enforced
- [ ] User Data Isolation: Verified via multi-user tests
- [ ] Stateless Architecture: Backend restartable without data loss
- [ ] Clean Code: No over-engineering, YAGNI principles followed

---

### 8.2 Acceptance Criteria Verification

**Verification Method: Manual Testing**
1. Create fresh user account
2. Create 3 tasks with different titles
3. Mark 1 task complete
4. Update 1 task title
5. Delete 1 task
6. Sign out and sign back in
7. Verify all changes persisted
8. Create second user account
9. Verify cannot access first user's tasks

**Verification Method: Automated Tests**
1. Run backend test suite: `pytest tests/ -v --cov`
2. Verify coverage ≥80%
3. Run frontend test suite: `npm test`
4. Verify all tests pass
5. Run integration tests
6. Verify multi-user isolation tests pass

**Verification Method: Performance Testing**
1. Use Apache Bench or similar: `ab -n 100 -c 10 http://localhost:8000/api/{user_id}/tasks`
2. Verify p95 latency <500ms
3. Use Lighthouse on frontend: Verify performance score >80

**Verification Method: Security Audit**
1. Run: `git grep -i 'password\|secret\|api_key'` → No matches in source files
2. Check `.gitignore` includes `.env`
3. Test CORS: Attempt request from unauthorized origin → Expect blocked
4. Test SQL injection: Submit `'; DROP TABLE tasks;--` as title → Safely stored
5. Test JWT tampering: Modify token signature → Expect 401

---

### 8.3 Production Readiness Criteria

**Infrastructure:**
- [ ] All services deployed and accessible
- [ ] Environment variables configured in deployment platforms
- [ ] Database connection pooling configured
- [ ] HTTPS certificates valid
- [ ] Health check endpoints monitored

**Monitoring & Logging:**
- [ ] Backend logs structured errors (not console.log)
- [ ] Frontend logs errors to console (dev) or monitoring service (prod)
- [ ] Database connection errors logged
- [ ] API request/response times logged

**Rollback Plan:**
- [ ] Git tags created for each deployment
- [ ] Ability to revert to previous version in <5 minutes
- [ ] Database migrations reversible (or backups available)

**User Communication:**
- [ ] Error messages user-friendly (no stack traces)
- [ ] Loading states prevent user confusion
- [ ] Success confirmations for actions (e.g., "Task created")

---

## 9. Architectural Decision Records (ADRs)

The following architectural decisions should be documented as ADRs after plan approval:

**ADR-001: Use Better Auth for Authentication**
- **Decision**: Use pre-built Better Auth microservice instead of implementing custom auth
- **Context**: Constitution mandates Better Auth, provides JWT tokens for stateless backend
- **Consequences**: Faster development, standardized auth flow, but requires schema customization

**ADR-002: Use JWT Tokens Instead of Session Cookies**
- **Decision**: Backend validates JWT tokens, does not call auth service for every request
- **Context**: Stateless architecture requirement (NFR-SCALE-01)
- **Consequences**: Horizontal scalability enabled, but token revocation harder (expires after 7 days)

**ADR-003: Use SQLModel for Backend ORM**
- **Decision**: SQLModel (combines Pydantic + SQLAlchemy) for database operations
- **Context**: Constitution mandates SQLModel, provides type safety and validation
- **Consequences**: Prevents SQL injection, simplifies queries, but adds ORM abstraction layer

**ADR-004: Use Next.js App Router (Not Pages Router)**
- **Decision**: Next.js 16+ with App Router for frontend
- **Context**: Constitution mandates App Router, enables Server Components
- **Consequences**: Better performance with RSC, but requires learning new patterns

**ADR-005: Use Optimistic UI Updates**
- **Decision**: Frontend updates UI immediately, rolls back on API error
- **Context**: Improves perceived performance, aligns with modern UX patterns
- **Consequences**: Better user experience, but requires error rollback logic

---

## 10. Plan Summary

**Total Estimated Components**: 15 modules (3 auth-service, 6 backend, 6 frontend)
**Total Estimated Endpoints**: 6 backend API endpoints + 4 auth endpoints
**Total Estimated Tests**: ~50 unit tests + ~10 integration tests + 5 E2E scenarios
**Implementation Phases**: 7 phases (0-6)
**Critical Path**: Phase 0 → Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 6
**Parallelization Opportunities**: Backend + Frontend design (limited)

**Key Success Factors**:
1. Successful Better Auth customization in Phase 0
2. JWT token flow working correctly in Phase 1-2
3. User data isolation enforced in all endpoints (Phase 2)
4. Frontend-backend integration smooth (Phase 3-4)
5. All tests passing before deployment (Phase 5)

**Next Step**: Generate task breakdown (`/sp.tasks`) with atomic, testable work items.

---

**Plan Version**: 1.0.0
**Status**: Ready for Task Breakdown
**Approval Required**: Yes (before proceeding to `/sp.tasks`)
**Estimated Complexity**: Medium (well-defined requirements, standard tech stack)
**Estimated Risk**: Low-Medium (auth customization is primary risk)
