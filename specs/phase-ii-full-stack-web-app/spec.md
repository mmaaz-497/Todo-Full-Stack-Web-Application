# Phase II: Todo Full-Stack Web Application - Specification

**Project**: Todo Full-Stack Web Application
**Phase**: II - Web Application with Authentication
**Version**: 1.0.0
**Last Updated**: 2025-12-19
**Status**: Draft
**Alignment**: Constitution v1.3.0

---

## 1. Project Overview

### 1.1 Problem Statement

The existing Phase I in-memory console application stores data temporarily and supports only single-user interaction. Users need a persistent, accessible web-based todo application with multi-user support where each user can manage their own isolated task lists through a modern web interface.

### 1.2 Goals

**Primary Goals:**
1. Transform the todo application into a production-ready web application
2. Implement persistent data storage using PostgreSQL (Neon Serverless)
3. Add user authentication and authorization with Better Auth
4. Provide a responsive web interface built with Next.js
5. Create a secure RESTful API backend using FastAPI
6. Enforce strict user data isolation (multi-tenant architecture)
7. **Implement Intermediate features** (priorities, tags, search, filtering, sorting)
8. **Implement Advanced features** (recurring tasks, due dates, reminders)

**Non-Goals (Explicitly Out of Scope):**
- AI chatbot integration with natural language processing
- Kubernetes deployment
- Event-driven architecture with Kafka
- Real-time collaboration or WebSocket connections
- Mobile applications (native iOS/Android)
- Third-party integrations (Google Calendar, Slack, etc.)

### 1.3 Target Users

**Primary User Persona:**
- **Name**: Individual Task Manager
- **Profile**: Anyone who needs to organize personal tasks
- **Technical Level**: Basic web user (no technical knowledge required)
- **Access Pattern**: Web browser on desktop or mobile device
- **Use Cases**:
  - Personal task management
  - Daily to-do lists
  - Work/home task separation via individual accounts

**User Journey (High-Level):**
1. User visits application URL
2. Signs up for new account or signs in to existing account
3. Views their personal task list (empty for new users)
4. Creates, updates, completes, or deletes tasks
5. Signs out when finished

### 1.4 Constraints and Assumptions

**Technical Constraints:**
- MUST use Next.js 16+ with App Router (no Pages Router)
- MUST use FastAPI for backend (Python 3.13+)
- MUST use SQLModel as ORM (no raw SQL queries)
- MUST use Neon Serverless PostgreSQL (no other database providers)
- MUST use Better Auth for authentication (pre-built microservice at `/auth-service`)
- MUST implement all code via Claude Code using Spec-Driven Development
- MUST NOT write code manually (specs must be refined until Claude Code generates correct output)

**Business Constraints:**
- Each user MUST only access their own data (strict isolation)
- Application MUST be deployable on Vercel (frontend) and standard hosting (backend)
- All API endpoints MUST require authentication (except signup/signin)
- Application MUST work on modern browsers (Chrome, Firefox, Safari, Edge)

**Operational Assumptions:**
- Neon PostgreSQL database is available and accessible
- Better Auth service runs on port 3001 (separate from main backend)
- Frontend runs on port 3000
- Backend API runs on port 8000
- Users have internet connectivity
- HTTPS will be enforced in production (HTTP allowed in local development)

---

## 2. Functional Requirements

### 2.1 User Authentication (FR-AUTH)

**FR-AUTH-01: User Signup**
- System MUST provide email/password signup via Better Auth integration
- Email MUST be unique across all users
- Password MUST meet minimum security requirements (defined by Better Auth)
- Upon successful signup, user account is created in `users` table
- User receives session cookie or JWT token for subsequent API calls
- **Acceptance Criteria:**
  - New user can sign up with valid email and password
  - Duplicate email returns error `409 Conflict`
  - Weak password returns error `400 Bad Request`
  - Successful signup returns `201 Created` with user object

**FR-AUTH-02: User Signin**
- System MUST provide email/password signin via Better Auth integration
- Signin MUST validate credentials against `users` table
- Successful signin returns session cookie or JWT token
- Failed signin returns generic error (to prevent user enumeration)
- **Acceptance Criteria:**
  - Existing user can sign in with correct credentials
  - Incorrect credentials return error `401 Unauthorized`
  - Successful signin returns `200 OK` with JWT token

**FR-AUTH-03: User Signout**
- System MUST provide signout functionality via Better Auth
- Signout MUST invalidate session/token on server side
- User MUST be redirected to signin page after signout
- **Acceptance Criteria:**
  - Signed-in user can sign out
  - Subsequent API calls with old token return `401 Unauthorized`
  - User redirected to signin page

**FR-AUTH-04: Session Persistence**
- User session MUST persist across page refreshes
- Session expiration MUST be configurable (default: 7 days)
- Expired sessions MUST require re-authentication
- **Acceptance Criteria:**
  - User remains signed in after browser refresh (within session window)
  - Expired token returns `401 Unauthorized`

**FR-AUTH-05: Auth Service Customization**
- Better Auth service schema MUST be customized to remove Physical AI Robotics fields
- MUST remove: `experienceLevel`, `professionalRole`, `roleOther`, `organization`
- MUST retain only: `id`, `email`, `name`, `emailVerified`, `image`, `createdAt`, `updatedAt`
- Database migrations MUST be regenerated after schema changes
- **Acceptance Criteria:**
  - Auth database schema matches simplified User entity
  - No custom fields from previous project remain
  - User table has exactly 7 columns as specified

### 2.2 Task Management (FR-TASK)

**FR-TASK-01: Create Task**
- User MUST be able to create a new task with title and optional description
- Title MUST be required (1-200 characters)
- Description is optional (max 1000 characters)
- Task MUST be automatically associated with authenticated user (`user_id`)
- New tasks default to `completed: false`
- System MUST auto-generate `id`, `created_at`, `updated_at` timestamps
- **Acceptance Criteria:**
  - Authenticated user can create task with valid title
  - Task appears in user's task list immediately
  - Empty title returns `400 Bad Request`
  - Title exceeding 200 chars returns `400 Bad Request`
  - Response returns `201 Created` with full task object

**FR-TASK-02: View Task List**
- User MUST be able to view all their tasks (and ONLY their tasks)
- Tasks MUST be filtered by authenticated user's `user_id`
- Response MUST include: `id`, `title`, `description`, `completed`, `created_at`, `updated_at`
- Empty list returns `200 OK` with empty array `[]`
- **Acceptance Criteria:**
  - User sees only their own tasks
  - Other users' tasks are never visible
  - List displays all task fields correctly
  - Response is valid JSON array

**FR-TASK-03: View Single Task**
- User MUST be able to view details of a specific task by ID
- System MUST verify task belongs to authenticated user (ownership check)
- Attempting to access another user's task returns `403 Forbidden`
- Non-existent task ID returns `404 Not Found`
- **Acceptance Criteria:**
  - User can view their own task details
  - Accessing another user's task is blocked
  - Valid task returns `200 OK` with task object

**FR-TASK-04: Update Task**
- User MUST be able to update title and/or description of their task
- System MUST verify task ownership before allowing update
- `updated_at` timestamp MUST be automatically updated
- Partial updates are allowed (can update only title or only description)
- Cannot update `id`, `user_id`, `completed`, `created_at` via this endpoint
- **Acceptance Criteria:**
  - User can update their own task's title/description
  - Ownership violation returns `403 Forbidden`
  - Valid update returns `200 OK` with updated task object
  - `updated_at` reflects current timestamp

**FR-TASK-05: Delete Task**
- User MUST be able to delete their task by ID
- System MUST verify task ownership before allowing deletion
- Deleted task MUST be permanently removed from database
- Subsequent requests for deleted task return `404 Not Found`
- **Acceptance Criteria:**
  - User can delete their own task
  - Ownership violation returns `403 Forbidden`
  - Successful deletion returns `204 No Content`
  - Task no longer appears in task list

**FR-TASK-06: Mark Task as Complete/Incomplete**
- User MUST be able to toggle task completion status
- System MUST verify task ownership before allowing status change
- `updated_at` timestamp MUST be automatically updated
- Endpoint accepts PATCH request to toggle `completed` boolean
- **Acceptance Criteria:**
  - User can mark their task as complete (`completed: true`)
  - User can mark their task as incomplete (`completed: false`)
  - Ownership violation returns `403 Forbidden`
  - Valid toggle returns `200 OK` with updated task object

### 2.3 User Data Isolation (FR-ISOLATION)

**FR-ISOLATION-01: Path Parameter Enforcement**
- All API routes MUST include `{user_id}` path parameter
- Backend MUST extract `user_id` from JWT token
- Backend MUST compare token `user_id` with path `{user_id}`
- Mismatch returns `403 Forbidden` with error message
- **Acceptance Criteria:**
  - User can only access `/api/{their_user_id}/tasks` endpoints
  - Attempting `/api/{other_user_id}/tasks` returns `403 Forbidden`

**FR-ISOLATION-02: Database Query Filtering**
- All database queries MUST filter by `user_id`
- No endpoint returns tasks without `user_id` filter
- Backend MUST use parameterized queries via SQLModel (no raw SQL)
- **Acceptance Criteria:**
  - List tasks query includes `WHERE user_id = ?`
  - Single task query includes `WHERE id = ? AND user_id = ?`
  - Update/delete operations verify ownership before executing

**FR-ISOLATION-03: Error Message Security**
- Error messages MUST NOT leak existence of other users' data
- Use `404 Not Found` for both non-existent and unauthorized resources
- Never return "Task exists but belongs to another user"
- **Acceptance Criteria:**
  - Accessing non-existent task: `404 Not Found`
  - Accessing another user's task: `403 Forbidden` (or `404` if preferred for security)

---

## 3. Non-Functional Requirements

### 3.1 Performance

**NFR-PERF-01: Response Time**
- API endpoints MUST respond within 500ms for p95 latency (database query + serialization)
- Page load time MUST be under 2 seconds on 3G connection (Next.js frontend)
- Task list with 100 tasks MUST render within 1 second

**NFR-PERF-02: Throughput**
- Backend MUST handle at least 100 concurrent requests
- Database connection pool MUST be configured to prevent exhaustion

**NFR-PERF-03: Resource Usage**
- Backend memory footprint MUST stay under 512MB per instance
- Frontend bundle size MUST be under 500KB (gzipped)

### 3.2 Security

**NFR-SEC-01: Authentication & Authorization**
- All API endpoints (except `/api/auth/*`) MUST require valid JWT token
- JWT tokens MUST be signed with `BETTER_AUTH_SECRET`
- Token expiration MUST be enforced (default: 7 days)
- Unauthorized requests return `401 Unauthorized`

**NFR-SEC-02: Input Validation**
- All user inputs MUST be validated via Pydantic models (backend) and Zod schemas (frontend)
- SQL injection MUST be prevented via SQLModel ORM (no raw SQL)
- Cross-Site Scripting (XSS) MUST be mitigated by React's default escaping
- CORS MUST be configured with explicit allowed origins (no `*` wildcard)

**NFR-SEC-03: Secrets Management**
- API keys, database credentials, JWT secrets MUST be stored in `.env` files
- `.env` files MUST be listed in `.gitignore` (never committed)
- `.env.example` templates MUST be provided in repository
- Production secrets MUST use environment variable injection (Vercel/hosting platform)

**NFR-SEC-04: HTTPS Enforcement**
- Production deployments MUST use HTTPS (enforced by Vercel)
- Development allows HTTP on `localhost`

**NFR-SEC-05: Password Security**
- Passwords MUST be hashed (handled by Better Auth)
- Never log or expose passwords in API responses

### 3.3 Reliability

**NFR-REL-01: Error Handling**
- All API errors MUST return structured JSON: `{ "error": "message", "code": "ERROR_CODE" }`
- Database connection failures MUST return `503 Service Unavailable`
- Uncaught exceptions MUST be logged server-side, return generic `500 Internal Server Error` to client

**NFR-REL-02: Data Integrity**
- Database transactions MUST ensure atomicity (task creation/update/deletion)
- Foreign key constraints MUST enforce `tasks.user_id -> users.id` relationship
- Cascade deletion: if user deleted, their tasks MUST also be deleted (or prevent user deletion)

**NFR-REL-03: Availability**
- Application MUST gracefully degrade if database is temporarily unavailable
- Frontend MUST display user-friendly error messages (not stack traces)

### 3.4 Scalability

**NFR-SCALE-01: Stateless Backend**
- Backend MUST NOT store session state in memory (use JWT for authentication)
- Each API request MUST be independent (no server-side session affinity)
- Enables horizontal scaling in future phases

**NFR-SCALE-02: Database Scaling**
- Use Neon Serverless PostgreSQL autoscaling
- Database queries MUST use indexes on `user_id` and `id` columns

### 3.5 Maintainability

**NFR-MAINT-01: Code Quality**
- Python code MUST follow PEP 8 style guide
- TypeScript/JavaScript MUST follow ESLint standard configuration
- Functions MUST be pure where possible (no side effects)
- Maximum function length: 50 lines (refactor if longer)

**NFR-MAINT-02: Documentation**
- API endpoints MUST be documented with OpenAPI/Swagger (FastAPI automatic docs)
- README MUST include setup instructions, environment variables, running instructions
- CLAUDE.md MUST contain Claude Code-specific guidance

**NFR-MAINT-03: Testing**
- Minimum 80% code coverage for task CRUD operations
- Unit tests for business logic
- Integration tests for API endpoints
- Test files co-located with source code

### 3.6 Accessibility

**NFR-ACCESS-01: Web Standards**
- Frontend MUST use semantic HTML (e.g., `<button>`, `<form>`, `<input>`)
- Forms MUST have proper `<label>` associations
- Interactive elements MUST be keyboard-accessible (tab navigation, Enter/Space activation)

**NFR-ACCESS-02: Responsive Design**
- Application MUST be usable on mobile (320px width) to desktop (1920px width)
- Touch targets MUST be at least 44x44px (WCAG 2.1 AA)

---

## 4. System Architecture (Conceptual)

### 4.1 High-Level Components

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER BROWSER                             │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │             Next.js Frontend (Port 3000)                   │ │
│  │  - App Router Pages                                        │ │
│  │  - React Server Components (default)                       │ │
│  │  - Client Components (forms, interactive UI)              │ │
│  │  - Tailwind CSS Styling                                    │ │
│  │  - API Client (/lib/api.ts)                               │ │
│  └────────────────────────────────────────────────────────────┘ │
│                           │                                      │
└───────────────────────────┼──────────────────────────────────────┘
                            │ HTTPS (REST API)
                            │ Authorization: Bearer <JWT>
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                 Better Auth Service (Port 3001)                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Better Auth v1.0.9 + Hono Framework                       │ │
│  │  - /api/auth/signup/email                                  │ │
│  │  - /api/auth/signin/email                                  │ │
│  │  - /api/auth/signout                                       │ │
│  │  - /api/auth/session                                       │ │
│  └────────────────────────────────────────────────────────────┘ │
│                           │                                      │
└───────────────────────────┼──────────────────────────────────────┘
                            │ JWT Token Verification
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                  FastAPI Backend (Port 8000)                     │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  /main.py - FastAPI Application                            │ │
│  │  /models.py - SQLModel Database Models (Task, User)        │ │
│  │  /routes/tasks.py - Task CRUD Endpoints                    │ │
│  │  /auth.py - JWT Verification Middleware                    │ │
│  │  /db.py - Database Connection & Session Management         │ │
│  └────────────────────────────────────────────────────────────┘ │
│                           │                                      │
└───────────────────────────┼──────────────────────────────────────┘
                            │ SQL Queries (SQLModel ORM)
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              Neon Serverless PostgreSQL (Remote)                 │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Tables:                                                    │ │
│  │  - users (id, email, name, emailVerified, image, ...)      │ │
│  │  - tasks (id, user_id, title, description, completed, ...) │ │
│  │  - session, account, verification (Better Auth managed)    │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Data Flow Description

**User Signup Flow:**
1. User submits signup form on frontend (`/signup` page)
2. Frontend sends POST to Better Auth `/api/auth/signup/email`
3. Better Auth validates email/password, creates user in `users` table
4. Better Auth returns JWT token or session cookie
5. Frontend stores token, redirects to dashboard (`/tasks`)

**User Signin Flow:**
1. User submits signin form on frontend (`/signin` page)
2. Frontend sends POST to Better Auth `/api/auth/signin/email`
3. Better Auth validates credentials, returns JWT token
4. Frontend stores token in localStorage or cookie
5. Frontend redirects to dashboard

**Create Task Flow:**
1. User fills task form on frontend (`/tasks` page)
2. Frontend sends POST to `/api/{user_id}/tasks` with JWT token in header
3. Backend middleware verifies JWT signature, extracts `user_id`
4. Backend compares token `user_id` with path `{user_id}` (must match)
5. Backend creates new `Task` record in database with `user_id`
6. Backend returns task object, frontend updates UI

**View Task List Flow:**
1. Frontend sends GET to `/api/{user_id}/tasks` with JWT token
2. Backend verifies JWT, extracts `user_id`
3. Backend queries database: `SELECT * FROM tasks WHERE user_id = ?`
4. Backend returns JSON array of tasks
5. Frontend renders task list

**Update Task Flow:**
1. User edits task on frontend
2. Frontend sends PUT to `/api/{user_id}/tasks/{id}` with updated data
3. Backend verifies JWT, verifies ownership (`task.user_id == token.user_id`)
4. Backend updates record, sets `updated_at = NOW()`
5. Backend returns updated task object

**Delete Task Flow:**
1. User clicks delete button on frontend
2. Frontend sends DELETE to `/api/{user_id}/tasks/{id}`
3. Backend verifies JWT, verifies ownership
4. Backend deletes record from database
5. Backend returns `204 No Content`, frontend removes task from UI

**Mark Complete Flow:**
1. User clicks checkbox on frontend
2. Frontend sends PATCH to `/api/{user_id}/tasks/{id}/complete`
3. Backend verifies JWT, verifies ownership
4. Backend toggles `completed` boolean, updates `updated_at`
5. Backend returns updated task object

### 4.3 Responsibility Boundaries

**Frontend Responsibilities:**
- Render UI components
- Handle user interactions (forms, buttons, navigation)
- Manage client-side state (task list cache, form state)
- Call backend API via centralized API client
- Store and attach JWT tokens to requests
- Display error messages from backend
- Redirect unauthenticated users to signin page

**Better Auth Service Responsibilities:**
- User signup and signin
- Password hashing and verification
- Session/JWT token generation and validation
- Manage `users`, `session`, `account`, `verification` tables
- Provide session info endpoint

**Backend API Responsibilities:**
- Verify JWT tokens on all protected endpoints
- Enforce user data isolation (ownership checks)
- Validate request payloads (Pydantic models)
- Execute database operations via SQLModel
- Return structured JSON responses
- Handle errors gracefully

**Database Responsibilities:**
- Store persistent data (users, tasks)
- Enforce foreign key constraints
- Provide ACID transaction guarantees
- Auto-generate timestamps and IDs

### 4.4 In-Memory vs Persistent Decisions

**Persistent (Database):**
- User accounts (`users` table)
- Tasks (`tasks` table)
- Authentication sessions (`session` table managed by Better Auth)

**In-Memory (No Persistence):**
- JWT tokens (stateless, validated cryptographically)
- Frontend UI state (React component state)
- API request/response cycles (stateless backend)

**Rationale:**
- Database persistence required for multi-user data durability
- Stateless JWT authentication enables horizontal scaling (NFR-SCALE-01)
- No server-side session storage simplifies deployment

---

## 5. Data Model & State

### 5.1 Entities and Attributes

**Entity: User (Managed by Better Auth)**

| Attribute       | Type      | Constraints                          | Description                          |
|-----------------|-----------|--------------------------------------|--------------------------------------|
| `id`            | `string`  | Primary Key, UUID, Auto-generated    | Unique user identifier               |
| `email`         | `string`  | Unique, Not Null                     | User email address                   |
| `name`          | `string`  | Nullable                             | User display name                    |
| `emailVerified` | `boolean` | Default: `false`                     | Email verification status            |
| `image`         | `string`  | Nullable                             | Profile picture URL                  |
| `createdAt`     | `datetime`| Auto-generated                       | Account creation timestamp           |
| `updatedAt`     | `datetime`| Auto-updated                         | Last account update timestamp        |

**Custom Fields Removed (from previous project):**
- ❌ `experienceLevel` (enum)
- ❌ `professionalRole` (enum)
- ❌ `roleOther` (string)
- ❌ `organization` (string)

**Entity: Task**

| Attribute     | Type      | Constraints                               | Description                          |
|---------------|-----------|-------------------------------------------|--------------------------------------|
| `id`          | `integer` | Primary Key, Auto-increment               | Unique task identifier               |
| `user_id`     | `string`  | Foreign Key → `users.id`, Not Null        | Owner of the task                    |
| `title`       | `string`  | Not Null, Max Length: 200                 | Task title                           |
| `description` | `string`  | Nullable, Max Length: 1000                | Task description (optional)          |
| `completed`   | `boolean` | Default: `false`, Not Null                | Completion status                    |
| `created_at`  | `datetime`| Auto-generated (server timestamp)         | Task creation timestamp              |
| `updated_at`  | `datetime`| Auto-updated on modification              | Last update timestamp                |

### 5.2 Relationships

**User → Tasks (One-to-Many):**
- One user can have zero or many tasks
- Each task belongs to exactly one user
- Foreign key: `tasks.user_id → users.id`
- Cascade behavior (recommended): `ON DELETE CASCADE` (if user deleted, delete their tasks)

**Diagram:**
```
┌─────────────────┐           ┌─────────────────┐
│     users       │           │     tasks       │
├─────────────────┤           ├─────────────────┤
│ id (PK)         │◄──────────│ id (PK)         │
│ email           │    1:N    │ user_id (FK)    │
│ name            │           │ title           │
│ emailVerified   │           │ description     │
│ image           │           │ completed       │
│ createdAt       │           │ created_at      │
│ updatedAt       │           │ updated_at      │
└─────────────────┘           └─────────────────┘
```

### 5.3 State Transitions

**Task Completion Status:**
```
┌──────────────┐   PATCH /complete    ┌──────────────┐
│              │─────────────────────▶ │              │
│  Incomplete  │                       │   Complete   │
│ completed=F  │ ◄─────────────────────│ completed=T  │
└──────────────┘   PATCH /complete    └──────────────┘
```

**State Rules:**
- New task starts in `Incomplete` state (`completed: false`)
- User can toggle between `Incomplete` and `Complete` states
- No other states exist (task is either done or not done)

**Authentication State (Frontend):**
```
┌──────────────┐   Signup/Signin      ┌──────────────┐
│              │─────────────────────▶ │              │
│ Unauthenticated                      │ Authenticated│
│ (no token)   │ ◄─────────────────────│ (has JWT)    │
└──────────────┘   Signout/Expire     └──────────────┘
```

### 5.4 Validation Rules

**User Entity (Better Auth Managed):**
- `email`: Must match RFC 5322 email format, unique across database
- `password` (during signup): Minimum 8 characters (configurable)

**Task Entity:**
- `title`: Required, 1-200 characters, non-empty after trimming whitespace
- `description`: Optional, max 1000 characters
- `completed`: Boolean only (`true` or `false`)
- `user_id`: Must exist in `users` table (foreign key constraint)

**Backend Validation (Pydantic Models):**
```python
from pydantic import BaseModel, Field, validator

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)

    @validator('title')
    def title_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Title cannot be empty or whitespace')
        return v.strip()

class TaskUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)
```

**Frontend Validation (Zod Schemas):**
```typescript
import { z } from 'zod';

const taskSchema = z.object({
  title: z.string().min(1).max(200).trim(),
  description: z.string().max(1000).optional(),
});
```

---

## 6. Command / Interface Specifications

### 6.1 REST API Endpoints

**Base URL:**
- Development: `http://localhost:8000`
- Production: `https://api.yourdomain.com`

**Authentication Header (All Protected Endpoints):**
```
Authorization: Bearer <JWT_TOKEN>
```

---

#### Endpoint: List All Tasks

**Request:**
```
GET /api/{user_id}/tasks
Authorization: Bearer <JWT_TOKEN>
```

**Path Parameters:**
- `user_id` (string, required): Authenticated user's ID (must match token)

**Query Parameters:**
None (filtering/sorting out of scope for Phase II)

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "user_id": "user-uuid-123",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false,
    "created_at": "2025-12-19T10:00:00Z",
    "updated_at": "2025-12-19T10:00:00Z"
  },
  {
    "id": 2,
    "user_id": "user-uuid-123",
    "title": "Finish project",
    "description": null,
    "completed": true,
    "created_at": "2025-12-18T14:30:00Z",
    "updated_at": "2025-12-19T09:00:00Z"
  }
]
```

**Response (Empty List):**
```json
[]
```

**Error Responses:**
- `401 Unauthorized`: Missing or invalid JWT token
- `403 Forbidden`: Token `user_id` does not match path `{user_id}`

---

#### Endpoint: Create New Task

**Request:**
```
POST /api/{user_id}/tasks
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread"
}
```

**Path Parameters:**
- `user_id` (string, required): Authenticated user's ID

**Request Body (JSON):**
- `title` (string, required): 1-200 characters
- `description` (string, optional): Max 1000 characters

**Response (201 Created):**
```json
{
  "id": 3,
  "user_id": "user-uuid-123",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "created_at": "2025-12-19T11:00:00Z",
  "updated_at": "2025-12-19T11:00:00Z"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid title (empty, too long) or description too long
- `401 Unauthorized`: Missing/invalid JWT
- `403 Forbidden`: User ID mismatch

---

#### Endpoint: Get Single Task

**Request:**
```
GET /api/{user_id}/tasks/{id}
Authorization: Bearer <JWT_TOKEN>
```

**Path Parameters:**
- `user_id` (string, required): Authenticated user's ID
- `id` (integer, required): Task ID

**Response (200 OK):**
```json
{
  "id": 1,
  "user_id": "user-uuid-123",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "created_at": "2025-12-19T10:00:00Z",
  "updated_at": "2025-12-19T10:00:00Z"
}
```

**Error Responses:**
- `401 Unauthorized`: Missing/invalid JWT
- `403 Forbidden`: Task belongs to different user
- `404 Not Found`: Task ID does not exist

---

#### Endpoint: Update Task

**Request:**
```
PUT /api/{user_id}/tasks/{id}
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "title": "Buy groceries and fruits",
  "description": "Milk, eggs, bread, apples"
}
```

**Path Parameters:**
- `user_id` (string, required): Authenticated user's ID
- `id` (integer, required): Task ID

**Request Body (JSON):**
- `title` (string, optional): 1-200 characters (if provided)
- `description` (string, optional): Max 1000 characters (if provided)
- Note: Both fields optional (partial update supported)

**Response (200 OK):**
```json
{
  "id": 1,
  "user_id": "user-uuid-123",
  "title": "Buy groceries and fruits",
  "description": "Milk, eggs, bread, apples",
  "completed": false,
  "created_at": "2025-12-19T10:00:00Z",
  "updated_at": "2025-12-19T11:30:00Z"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid title/description
- `401 Unauthorized`: Missing/invalid JWT
- `403 Forbidden`: Task belongs to different user
- `404 Not Found`: Task ID does not exist

---

#### Endpoint: Delete Task

**Request:**
```
DELETE /api/{user_id}/tasks/{id}
Authorization: Bearer <JWT_TOKEN>
```

**Path Parameters:**
- `user_id` (string, required): Authenticated user's ID
- `id` (integer, required): Task ID

**Response (204 No Content):**
```
(empty body)
```

**Error Responses:**
- `401 Unauthorized`: Missing/invalid JWT
- `403 Forbidden`: Task belongs to different user
- `404 Not Found`: Task ID does not exist

---

#### Endpoint: Toggle Task Completion

**Request:**
```
PATCH /api/{user_id}/tasks/{id}/complete
Authorization: Bearer <JWT_TOKEN>
```

**Path Parameters:**
- `user_id` (string, required): Authenticated user's ID
- `id` (integer, required): Task ID

**Request Body:**
None (endpoint toggles `completed` boolean automatically)

**Response (200 OK):**
```json
{
  "id": 1,
  "user_id": "user-uuid-123",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": true,
  "created_at": "2025-12-19T10:00:00Z",
  "updated_at": "2025-12-19T12:00:00Z"
}
```

**Error Responses:**
- `401 Unauthorized`: Missing/invalid JWT
- `403 Forbidden`: Task belongs to different user
- `404 Not Found`: Task ID does not exist

---

### 6.2 Better Auth Endpoints (Pre-Built)

These endpoints are provided by the Better Auth service (`/auth-service`):

#### Signup
```
POST http://localhost:3001/api/auth/signup/email
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123",
  "name": "John Doe"
}
```

**Response (201 Created):**
```json
{
  "user": {
    "id": "user-uuid-123",
    "email": "user@example.com",
    "name": "John Doe",
    "emailVerified": false,
    "image": null,
    "createdAt": "2025-12-19T10:00:00Z",
    "updatedAt": "2025-12-19T10:00:00Z"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Signin
```
POST http://localhost:3001/api/auth/signin/email
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
  "user": { ... },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Signout
```
POST http://localhost:3001/api/auth/signout
Authorization: Bearer <JWT_TOKEN>
```

**Response (200 OK):**
```json
{
  "success": true
}
```

#### Get Session
```
GET http://localhost:3001/api/auth/session
Authorization: Bearer <JWT_TOKEN>
```

**Response (200 OK):**
```json
{
  "user": {
    "id": "user-uuid-123",
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

---

## 7. Validation & Acceptance Criteria

### 7.1 Feature-Level Acceptance Criteria

**Feature: User Authentication**
- [ ] User can sign up with unique email and password
- [ ] User can sign in with correct credentials
- [ ] User receives JWT token upon successful signin
- [ ] User can sign out (token invalidated)
- [ ] Incorrect credentials return `401 Unauthorized`
- [ ] Duplicate email during signup returns `409 Conflict`

**Feature: Task Creation**
- [ ] Authenticated user can create task with title
- [ ] Task with description is saved correctly
- [ ] Empty title returns `400 Bad Request`
- [ ] Task automatically associated with user's `user_id`
- [ ] New task appears in user's task list immediately

**Feature: Task Viewing**
- [ ] User can view list of all their tasks
- [ ] User cannot see other users' tasks
- [ ] Empty task list returns `[]` (not error)
- [ ] User can view single task details by ID

**Feature: Task Updates**
- [ ] User can update task title
- [ ] User can update task description
- [ ] Partial updates work (only title or only description)
- [ ] `updated_at` timestamp updates correctly
- [ ] Cannot update another user's task (`403 Forbidden`)

**Feature: Task Deletion**
- [ ] User can delete their own task
- [ ] Deleted task no longer appears in list
- [ ] Deleting non-existent task returns `404 Not Found`
- [ ] Cannot delete another user's task (`403 Forbidden`)

**Feature: Task Completion**
- [ ] User can mark task as complete
- [ ] User can mark task as incomplete (toggle back)
- [ ] Completion status persists across page reloads
- [ ] `updated_at` timestamp updates on status change

**Feature: Data Isolation**
- [ ] User A cannot access User B's tasks (any endpoint)
- [ ] Path parameter `{user_id}` must match JWT token `user_id`
- [ ] All database queries filter by `user_id`

### 7.2 Preconditions and Postconditions

**Precondition: Before Any Task Operation**
- User MUST be authenticated (have valid JWT token)
- User account MUST exist in `users` table
- Database connection MUST be active

**Postcondition: After Task Creation**
- New task record exists in database
- Task is associated with authenticated user
- `created_at` and `updated_at` are set to current timestamp
- Task `id` is auto-generated

**Postcondition: After Task Update**
- Task record is modified in database
- `updated_at` timestamp is newer than `created_at`
- Title/description changes are persisted

**Postcondition: After Task Deletion**
- Task record is permanently removed from database
- Subsequent queries for that task ID return `404 Not Found`

---

## 8. Testing Guidance

### 8.1 Unit Test Expectations

**Backend Unit Tests (FastAPI):**

**Test File: `tests/test_auth.py`**
- `test_verify_jwt_valid_token()`: Decodes valid JWT, extracts user_id
- `test_verify_jwt_expired_token()`: Rejects expired token
- `test_verify_jwt_invalid_signature()`: Rejects tampered token
- `test_verify_jwt_missing_user_id()`: Rejects token without user_id claim

**Test File: `tests/test_models.py`**
- `test_task_creation()`: Task model initializes with correct defaults
- `test_task_title_validation()`: Empty title raises validation error
- `test_task_title_max_length()`: Title exceeding 200 chars raises error
- `test_task_description_max_length()`: Description exceeding 1000 chars raises error

**Test File: `tests/test_routes_tasks.py`**
- `test_create_task_success()`: POST /api/{user_id}/tasks returns 201
- `test_create_task_empty_title()`: Returns 400 for empty title
- `test_list_tasks_empty()`: Returns [] for user with no tasks
- `test_list_tasks_filters_by_user()`: User A sees only their tasks
- `test_update_task_ownership()`: User cannot update another user's task
- `test_delete_task_not_found()`: Returns 404 for non-existent task
- `test_toggle_complete_success()`: PATCH toggles completed status

**Frontend Unit Tests (Next.js/React):**

**Test File: `frontend/components/TaskList.test.tsx`**
- `test_renders_empty_state()`: Shows "No tasks" message when list empty
- `test_renders_task_items()`: Displays task title and description
- `test_calls_delete_callback()`: Delete button triggers onDelete callback

**Test File: `frontend/components/TaskForm.test.tsx`**
- `test_submits_valid_task()`: Form submission calls onCreate with title
- `test_validates_empty_title()`: Shows error for empty title
- `test_validates_title_length()`: Shows error for title > 200 chars

### 8.2 Integration Test Scope

**Integration Test: Complete Task CRUD Flow**
1. Authenticate user (get JWT token)
2. Create task via POST `/api/{user_id}/tasks`
3. Verify task appears in GET `/api/{user_id}/tasks`
4. Update task via PUT `/api/{user_id}/tasks/{id}`
5. Verify updates reflected in GET
6. Toggle completion via PATCH `/api/{user_id}/tasks/{id}/complete`
7. Delete task via DELETE `/api/{user_id}/tasks/{id}`
8. Verify task no longer in GET response

**Integration Test: Multi-User Isolation**
1. Create two users (User A, User B)
2. User A creates task
3. User B attempts to GET User A's task → Expect `403 Forbidden`
4. User B attempts to DELETE User A's task → Expect `403 Forbidden`
5. User B creates their own task
6. Verify User A cannot see User B's task

**Integration Test: Authentication Flow**
1. Signup new user → Expect `201 Created` with JWT
2. Signin with correct credentials → Expect `200 OK` with JWT
3. Call protected endpoint with valid JWT → Expect `200 OK`
4. Call protected endpoint without JWT → Expect `401 Unauthorized`
5. Call protected endpoint with expired JWT → Expect `401 Unauthorized`
6. Signout → Expect token invalidated

### 8.3 Edge-Case Testing Guidance

**Edge Case: Extremely Long Strings**
- Title with 200 characters (exact limit): Should succeed
- Title with 201 characters: Should return `400 Bad Request`
- Description with 1000 characters: Should succeed
- Description with 1001 characters: Should return `400 Bad Request`

**Edge Case: Special Characters in Title/Description**
- Title with emoji: `"Buy groceries 🛒"` → Should succeed
- Title with quotes: `"Meeting about \"Project X\""` → Should succeed
- Title with SQL injection attempt: `"'; DROP TABLE tasks;--"` → Should be safely escaped

**Edge Case: Concurrent Updates**
- User A updates task at timestamp T1
- User B (same account, different session) updates same task at timestamp T2
- Last write wins (T2 overwrites T1)
- Both `updated_at` timestamps should reflect actual update time

**Edge Case: Database Connection Failure**
- Database becomes unavailable during request
- Backend should return `503 Service Unavailable`
- Frontend should display user-friendly error message

**Edge Case: Malformed JWT**
- JWT with invalid format (not three dot-separated segments)
- Backend should return `401 Unauthorized` with error message
- Frontend should redirect to signin page

---

## 9. Future Extensions (Optional)

These features are explicitly **out of scope for Phase II** but documented for future phases:

### 9.1 Intermediate Features (Phase III Candidates)

**Priorities:**
- Add `priority` field to Task entity (enum: HIGH, MEDIUM, LOW)
- Filter tasks by priority in API
- Sort tasks by priority in UI

**Tags/Categories:**
- Add `tags` field to Task entity (array of strings: ["work", "home"])
- Filter tasks by tags
- Display tag badges in UI

**Search:**
- Add full-text search on task title/description
- Search endpoint: `GET /api/{user_id}/tasks/search?q=grocery`

**Filtering:**
- Filter by completion status: `?status=completed`
- Filter by date range: `?created_after=2025-12-01`

**Sorting:**
- Sort by due date: `?sort=due_date`
- Sort by priority: `?sort=priority`
- Sort alphabetically: `?sort=title`

### 9.2 Advanced Features (Phase IV+ Candidates)

**Recurring Tasks:**
- Add `recurrence_rule` field (e.g., "weekly", "monthly")
- Auto-create new task when recurring task completed
- Kafka event for task recurrence logic

**Due Dates & Reminders:**
- Add `due_date` and `reminder_time` fields
- Send browser push notifications at reminder time
- Email reminders via notification service

**Natural Language Interface:**
- AI chatbot (Phase III): "Add a task to buy groceries tomorrow at 2pm"
- Parse natural language into structured task

**Real-Time Sync:**
- WebSocket connection for live task list updates
- Multi-device sync (desktop, mobile)

**Collaboration:**
- Share tasks with other users
- Assign tasks to team members

---

## 10. Success Metrics

### 10.1 Technical Metrics

- **Test Coverage**: ≥80% for task CRUD operations
- **API Response Time**: p95 latency <500ms
- **Bundle Size**: Frontend <500KB gzipped
- **Uptime**: ≥99.5% during demo period

### 10.2 Functional Metrics

- **User Authentication**: 100% success rate for valid credentials
- **Data Isolation**: 0 cross-user data leaks (verified via tests)
- **Task Operations**: All 5 basic operations (create, read, update, delete, complete) functional

### 10.3 Quality Metrics

- **Zero Critical Bugs**: No P0/P1 bugs at deployment time
- **Security**: No hardcoded secrets in repository
- **Code Quality**: Passes ESLint/Pylint with 0 errors

---

## 11. Dependencies and Integrations

### 11.1 External Services

**Neon Serverless PostgreSQL:**
- Connection via `DATABASE_URL` environment variable
- Format: `postgresql://user:password@host/database?sslmode=require`
- Used by both auth-service and backend

**Better Auth Service:**
- Pre-built microservice in `/auth-service` directory
- Better Auth v1.0.9 with Hono framework
- Drizzle ORM for database operations
- Runs on port 3001
- Provides JWT tokens for backend verification

### 11.2 Internal Dependencies

**Frontend → Better Auth:**
- Calls `/api/auth/signup/email`, `/api/auth/signin/email`, `/api/auth/signout`
- Stores JWT token in localStorage or HTTP-only cookie
- Attaches token to API requests

**Frontend → Backend API:**
- All task operations go through backend REST API
- Uses centralized API client (`/lib/api.ts`)
- Handles token attachment, error handling, response parsing

**Backend → Database:**
- SQLModel ORM for all database operations
- Connection pooling managed by SQLModel/SQLAlchemy
- Foreign key constraints enforced at database level

**Backend → Better Auth (Verification):**
- Backend verifies JWT signature using shared `BETTER_AUTH_SECRET`
- Does NOT call auth service for every request (stateless verification)
- Decodes token to extract `user_id` claim

### 11.3 Configuration Requirements

**Environment Variables (Frontend `.env.local`):**
```
NEXT_PUBLIC_AUTH_URL=http://localhost:3001
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Environment Variables (Backend `.env`):**
```
DATABASE_URL=postgresql://user:pass@neon.host/database
BETTER_AUTH_SECRET=<shared-secret-with-auth-service>
CORS_ORIGINS=http://localhost:3000
```

**Environment Variables (Auth Service `.env`):**
```
DATABASE_URL=postgresql://user:pass@neon.host/database
BETTER_AUTH_SECRET=<same-secret-as-backend>
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
SESSION_EXPIRES_IN=7d
```

**Shared Secrets:**
- `BETTER_AUTH_SECRET` MUST be identical in both backend and auth-service
- Used for JWT signing (auth-service) and verification (backend)
- Generate with: `openssl rand -hex 32`

---

## 12. Deployment Requirements

### 12.1 Development Environment

**Prerequisites:**
- Node.js 18+ (for frontend and auth-service)
- Python 3.13+ (for backend)
- UV package manager (for Python dependencies)
- Git (for version control)
- Neon PostgreSQL account (free tier)

**Running Locally:**
1. Auth Service: `cd auth-service && npm install && npm run dev` (port 3001)
2. Backend: `cd backend && uv pip install -r requirements.txt && uvicorn main:app --reload` (port 8000)
3. Frontend: `cd frontend && npm install && npm run dev` (port 3000)

**Database Setup:**
1. Create Neon PostgreSQL database
2. Copy `DATABASE_URL` connection string
3. Set in both `auth-service/.env` and `backend/.env`
4. Auth service auto-creates tables on first run (Drizzle migrations)
5. Backend creates `tasks` table via SQLModel `create_all()`

### 12.2 Production Deployment

**Frontend (Vercel):**
- Deploy Next.js app to Vercel
- Set environment variables in Vercel dashboard
- Automatic HTTPS and CDN
- Zero-downtime deployments

**Backend (Options):**
- Render.com (free tier, auto-deploy from Git)
- Railway.app (free tier with usage limits)
- DigitalOcean App Platform (simple PaaS)
- Self-hosted (VPS with Docker)

**Auth Service (Same as Backend):**
- Deploy alongside backend or separately
- Ensure `BETTER_AUTH_SECRET` matches backend

**Database (Neon):**
- Already serverless, no deployment needed
- Use connection pooling in production
- Enable SSL mode (`sslmode=require`)

---

## 13. Open Questions and Risks

### 13.1 Open Questions

**Q1: Should session expiration be configurable per user?**
- **Current**: Global 7-day expiration (Better Auth default)
- **Decision Needed**: If users need "Remember Me" option, requires Better Auth customization

**Q2: Should deleted users' tasks be cascade-deleted or preserved?**
- **Current**: No user deletion endpoint in Phase II
- **Recommendation**: Implement `ON DELETE CASCADE` for future-proofing

**Q3: Should API support pagination for task lists?**
- **Current**: No pagination (all tasks returned)
- **Risk**: Users with >1000 tasks may experience slow response
- **Mitigation**: Add pagination in Phase III if needed

**Q4: Should task IDs be UUIDs instead of auto-incrementing integers?**
- **Current**: Integer IDs (simpler, sequential)
- **Risk**: Enumeration attacks (guessing other task IDs)
- **Mitigation**: Ownership checks prevent unauthorized access

### 13.2 Risks and Mitigation

**Risk 1: Better Auth Customization Complexity**
- **Impact**: Medium
- **Likelihood**: Medium
- **Description**: Removing custom fields from auth-service schema requires manual editing
- **Mitigation**: Follow constitution's step-by-step customization guide (lines 266-299)
- **Mitigation**: Test migrations on development database before production

**Risk 2: CORS Configuration Errors**
- **Impact**: High (blocks frontend-backend communication)
- **Likelihood**: Low
- **Description**: Misconfigured CORS origins prevent API calls
- **Mitigation**: Set `CORS_ORIGINS` explicitly in both auth-service and backend
- **Mitigation**: Test cross-origin requests in development

**Risk 3: JWT Secret Mismatch**
- **Impact**: High (all API calls fail authentication)
- **Likelihood**: Low
- **Description**: Different `BETTER_AUTH_SECRET` in auth-service vs backend
- **Mitigation**: Use environment variable validation on startup
- **Mitigation**: Document secret generation and sharing process

**Risk 4: Database Connection Pool Exhaustion**
- **Impact**: Medium (API becomes unresponsive)
- **Likelihood**: Low (in development/early deployment)
- **Description**: Too many concurrent connections to Neon database
- **Mitigation**: Configure SQLModel connection pool size (default: 20)
- **Mitigation**: Monitor Neon dashboard for connection usage

**Risk 5: Spec-Code Misalignment**
- **Impact**: High (implementation doesn't match spec)
- **Likelihood**: Medium
- **Description**: Claude Code generates code that deviates from spec
- **Mitigation**: Iterative refinement of specs until output matches
- **Mitigation**: Use constitution principles to guide Claude Code
- **Mitigation**: Manual verification of critical paths (authentication, data isolation)

---

## 14. Approval and Sign-Off

This specification document is ready for review and approval before proceeding to the **Plan** phase.

**Reviewers:**
- [ ] Product Owner: Verify alignment with hackathon requirements
- [ ] Security Lead: Confirm authentication and data isolation requirements
- [ ] Tech Lead: Validate architecture and technology stack choices
- [ ] QA Lead: Review acceptance criteria and testing guidance

**Approval Checklist:**
- [ ] All functional requirements clearly defined
- [ ] Non-functional requirements (performance, security, scalability) specified
- [ ] Data model and validation rules documented
- [ ] API contracts defined with request/response examples
- [ ] Acceptance criteria testable and measurable
- [ ] Risks identified with mitigation strategies
- [ ] Constitution alignment verified (v1.3.0)

**Next Steps After Approval:**
1. Generate implementation plan (`/sp.plan`)
2. Break plan into atomic tasks (`/sp.tasks`)
3. Customize Better Auth service (remove custom fields)
4. Implement backend API via Claude Code
5. Implement frontend UI via Claude Code
6. Execute tests and verify acceptance criteria
7. Deploy to staging environment
8. Conduct final review and deploy to production

---

**Document Control:**
- **Created**: 2025-12-19
- **Author**: Claude Code (via Spec-Driven Development)
- **Version**: 1.0.0
- **Status**: Draft - Awaiting Approval
- **Constitution Alignment**: v1.3.0 compliant
- **Related Artifacts**:
  - Constitution: `.specify/memory/constitution.md`
  - Hackathon Requirements: `HACKATHON.md`
  - Next: `specs/phase-ii-full-stack-web-app/plan.md` (to be generated)
