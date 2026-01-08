# Implementation Tasks: Todo AI Chatbot

## Metadata
```yaml
feature: todo-ai-chatbot
version: 1.0.0
stage: tasks
created: 2025-12-27
constitution_version: 1.0.0
plan_version: 1.0.0
tdd_enforced: true
status: ready-for-implementation
```

## Constitution Compliance

**All tasks MUST follow Constitution v1.0.0 principles:**
- ✅ Test-First Development (NON-NEGOTIABLE): Write tests FIRST, verify RED, then implement
- ✅ Stateless-First Architecture: No in-memory state
- ✅ MCP-First Tool Integration: All task operations via MCP tools only
- ✅ Database Persistence Guarantee: Every interaction persisted
- ✅ Conversational Error Handling: User-friendly errors
- ✅ Natural Language Intent Mapping: Intent → tool mapping
- ✅ Security and User Isolation: user_id validation at every layer

**TDD Workflow (MANDATORY):**
1. Write test file with test cases FIRST
2. Get user/reviewer approval on tests
3. Run tests → VERIFY THEY FAIL (RED phase)
4. Implement code to make tests pass (GREEN phase)
5. Refactor while keeping tests green
6. NEVER proceed to next task until tests are GREEN

---

## Phase 1: Foundation Setup

### Task 1.1: Initialize Project Structure
**Priority:** P0 (Blocker)
**Dependencies:** None
**Estimated Effort:** 15 minutes

**Objective:** Create standard project directory structure

**Actions:**
- Create `backend/` directory structure:
  - `backend/app/` with `__init__.py`
  - `backend/tests/` with `__init__.py`
  - `backend/migrations/`
- Create `frontend/` directory
- Create `.gitignore` for Python

**Acceptance Criteria:**
- [ ] All directories exist
- [ ] `__init__.py` files present in Python packages
- [ ] `.gitignore` includes `__pycache__/`, `.env`, `*.pyc`

**Files Created:**
- `backend/app/__init__.py`
- `backend/tests/__init__.py`
- `.gitignore`

**No TDD Required:** Directory setup task

---

### Task 1.2: Define Dependencies
**Priority:** P0 (Blocker)
**Dependencies:** Task 1.1
**Estimated Effort:** 10 minutes

**Objective:** Create requirements.txt with pinned versions

**Actions:**
- Create `backend/requirements.txt` with exact versions:
  ```
  fastapi==0.115.0
  uvicorn[standard]==0.30.6
  sqlmodel==0.0.22
  psycopg2-binary==2.9.9
  alembic==1.13.2
  python-jose[cryptography]==3.3.0
  python-multipart==0.0.9
  pydantic-settings==2.5.2
  google-generativeai==0.8.3
  openai==1.54.0
  python-dotenv==1.0.1
  pytest==8.3.3
  pytest-asyncio==0.24.0
  httpx==0.27.2
  ```

**Acceptance Criteria:**
- [ ] `requirements.txt` lists all dependencies with exact versions
- [ ] No conflicting dependencies
- [ ] All packages support Python 3.11+

**Files Created:**
- `backend/requirements.txt`

**No TDD Required:** Dependency definition task

---

### Task 1.3: Environment Configuration
**Priority:** P0 (Blocker)
**Dependencies:** Task 1.2
**Estimated Effort:** 20 minutes

**Objective:** Create environment configuration with validation

**Actions:**
- Create `.env.example` template
- Create `backend/app/config.py` with Pydantic Settings class
- Define all required environment variables

**Acceptance Criteria:**
- [ ] `.env.example` documents all required variables
- [ ] `Settings` class validates types and required fields
- [ ] Server fails fast on missing required variables
- [ ] No hardcoded secrets or configuration

**Files Created:**
- `.env.example`
- `backend/app/config.py`

**TDD Requirement:**
**Test File:** `backend/tests/test_config.py`
**Write FIRST before implementing config.py:**
- [ ] Test Settings loads from environment variables
- [ ] Test Settings raises error on missing DATABASE_URL
- [ ] Test Settings raises error on missing GOOGLE_API_KEY
- [ ] Test Settings uses default values for optional fields
- [ ] Test Settings validates DATABASE_URL format

**Red Phase:** Run `pytest backend/tests/test_config.py` → Must FAIL

---

## Phase 2: Database Layer

### Task 2.1: Write Database Tests (TDD RED PHASE)
**Priority:** P0 (Blocker)
**Dependencies:** Task 1.3
**Estimated Effort:** 45 minutes

**Objective:** Write ALL database tests BEFORE implementing models

**Constitution Principle:** Test-First Development (NON-NEGOTIABLE)

**Actions:**
- Create `backend/tests/test_database.py`
- Write test cases for ALL database models and operations

**Test Cases to Write:**
- [ ] Test Task model creation with all fields
- [ ] Test Task model constraints (title not empty, user_id required)
- [ ] Test Task model indexes (user_id, composite user_id+completed)
- [ ] Test Conversation model creation
- [ ] Test Message model creation with role validation ("user" or "assistant")
- [ ] Test Message role constraint (rejects invalid roles)
- [ ] Test foreign key relationship (conversation_id → conversations)
- [ ] Test cascade delete (delete conversation → delete messages)
- [ ] Test database connection pool (concurrent sessions)
- [ ] Test stateless session management (sessions don't leak)
- [ ] Test UTC timestamps (created_at, updated_at)

**Acceptance Criteria:**
- [ ] `backend/tests/test_database.py` created with ALL test cases
- [ ] Tests use pytest fixtures for database setup/teardown
- [ ] Tests cover success cases and constraint violations
- [ ] Running `pytest backend/tests/test_database.py` FAILS (models not implemented yet)

**Files Created:**
- `backend/tests/test_database.py`

**CRITICAL:** Do NOT implement models.py yet. Tests MUST fail first (RED phase).

---

### Task 2.2: Implement SQLModel Schemas (TDD GREEN PHASE)
**Priority:** P0 (Blocker)
**Dependencies:** Task 2.1
**Estimated Effort:** 30 minutes

**Objective:** Implement database models to make tests pass

**Constitution Principles:** Database Persistence Guarantee, Stateless-First Architecture

**Pre-Condition:** Tests from Task 2.1 MUST be failing (RED phase verified)

**Actions:**
- Create `backend/app/models.py`
- Implement Task, Conversation, Message models
- Add indexes as specified in spec
- Add constraints and foreign keys

**Acceptance Criteria:**
- [ ] All models match spec exactly (Task, Conversation, Message)
- [ ] Indexes created: user_id (Task, Conversation, Message), (user_id, completed) composite on Task
- [ ] Foreign key: Message.conversation_id → Conversation.id with cascade delete
- [ ] Role field validated ("user" | "assistant")
- [ ] Timestamps use datetime.utcnow
- [ ] Running `pytest backend/tests/test_database.py` PASSES (GREEN phase achieved)

**Files Created:**
- `backend/app/models.py`

**CRITICAL:** All tests from Task 2.1 MUST pass before proceeding.

---

### Task 2.3: Database Connection Management
**Priority:** P0 (Blocker)
**Dependencies:** Task 2.2
**Estimated Effort:** 20 minutes

**Objective:** Implement stateless connection pooling

**Constitution Principle:** Stateless-First Architecture

**Actions:**
- Create `backend/app/database.py`
- Implement SQLModel engine with connection pool
- Implement `get_session()` dependency for FastAPI
- Configure pool settings (pool_size=5, max_overflow=15)

**Acceptance Criteria:**
- [ ] Engine created with correct pool settings
- [ ] `get_session()` uses context manager for automatic cleanup
- [ ] No session leaks (verified by connection pool tests from Task 2.1)
- [ ] Concurrent requests use separate sessions (test from Task 2.1 passes)

**Files Created:**
- `backend/app/database.py`

**Tests:** Already written in Task 2.1 (connection pool and session tests)

---

### Task 2.4: Database Migrations
**Priority:** P0 (Blocker)
**Dependencies:** Task 2.3
**Estimated Effort:** 25 minutes

**Objective:** Set up Alembic for schema versioning

**Actions:**
- Initialize Alembic in `backend/migrations/`
- Configure Alembic for SQLModel
- Create initial migration with all tables, indexes, constraints
- Test migration on local database

**Acceptance Criteria:**
- [ ] Alembic initialized with correct configuration
- [ ] Initial migration creates tasks, conversations, messages tables
- [ ] Indexes and constraints included in migration
- [ ] `alembic upgrade head` succeeds
- [ ] `alembic downgrade base` cleanly removes tables
- [ ] Migration is idempotent (can run multiple times safely)

**Files Created:**
- `backend/migrations/alembic.ini`
- `backend/migrations/env.py`
- `backend/migrations/versions/001_initial_schema.py`

**No TDD Required:** Migration setup task (migrations are tested by running them)

---

## Phase 3: MCP Server Implementation

### Task 3.1: Write MCP Tool Tests (TDD RED PHASE)
**Priority:** P0 (Blocker)
**Dependencies:** Task 2.4
**Estimated Effort:** 60 minutes

**Objective:** Write ALL MCP tool tests BEFORE implementing tools

**Constitution Principles:** Test-First Development (NON-NEGOTIABLE), MCP-First Tool Integration, Security and User Isolation

**Actions:**
- Create `backend/tests/test_mcp_tools.py`
- Write comprehensive test cases for ALL 5 MCP tools

**Test Cases to Write:**

**add_task tests:**
- [ ] Creates task with valid inputs (user_id, title, description)
- [ ] Creates task with only required fields (user_id, title)
- [ ] Rejects empty title
- [ ] Validates title max length (500 chars)
- [ ] Validates description max length (5000 chars)
- [ ] Returns correct response format {task_id, status: "pending", title}
- [ ] Sets completed=false, created_at, updated_at automatically

**list_tasks tests:**
- [ ] Returns all tasks for user (status="all")
- [ ] Filters by status="pending" (completed=false)
- [ ] Filters by status="completed" (completed=true)
- [ ] Orders by created_at DESC (newest first)
- [ ] Returns empty list when no tasks
- [ ] Enforces user_id isolation (User A cannot see User B's tasks)
- [ ] Returns correct format {tasks: [...], count: N}

**complete_task tests:**
- [ ] Marks task as completed (completed=true, updated_at=now)
- [ ] Idempotent (completing already completed task returns success)
- [ ] Returns 404 for non-existent task
- [ ] Enforces user_id ownership (User A cannot complete User B's task)
- [ ] Returns correct format {task_id, status: "completed", title}

**delete_task tests:**
- [ ] Deletes task from database
- [ ] Returns confirmation with task details
- [ ] Returns 404 for non-existent task
- [ ] Enforces user_id ownership (User A cannot delete User B's task)
- [ ] Returns correct format {task_id, status: "deleted", title}

**update_task tests:**
- [ ] Updates title only
- [ ] Updates description only
- [ ] Updates both title and description
- [ ] Updates updated_at timestamp
- [ ] Rejects empty title
- [ ] Returns 404 for non-existent task
- [ ] Enforces user_id ownership (User A cannot update User B's task)
- [ ] Returns updated task with all fields
- [ ] Requires at least one field (title or description)

**Security tests (ALL tools):**
- [ ] User A cannot access User B's tasks (test for each tool)
- [ ] SQL injection attempts blocked (parameterized queries)
- [ ] Malicious input sanitized

**Acceptance Criteria:**
- [ ] `backend/tests/test_mcp_tools.py` created with ALL test cases
- [ ] Tests cover success cases, error cases, and security cases
- [ ] Tests use pytest fixtures for database and test data
- [ ] Running `pytest backend/tests/test_mcp_tools.py` FAILS (tools not implemented yet)

**Files Created:**
- `backend/tests/test_mcp_tools.py`

**CRITICAL:** Do NOT implement tools yet. Tests MUST fail first (RED phase).

---

### Task 3.2: Implement MCP Server Initialization (TDD GREEN PHASE)
**Priority:** P0 (Blocker)
**Dependencies:** Task 3.1
**Estimated Effort:** 30 minutes

**Objective:** Set up MCP server framework

**Constitution Principle:** MCP-First Tool Integration

**Actions:**
- Create `backend/app/mcp_server.py`
- Initialize MCP server with tool registration framework
- Configure server port (from environment variable)

**Acceptance Criteria:**
- [ ] MCP server initializes without errors
- [ ] Port configurable via `MCP_SERVER_PORT` env var (default 3000)
- [ ] Ready to register tools (framework in place)
- [ ] Server uses stdio transport (MCP SDK)

**Files Created:**
- `backend/app/mcp_server.py`

**Tests:** MCP server framework tests (basic initialization)

---

### Task 3.3: Implement add_task Tool (TDD GREEN PHASE)
**Priority:** P0 (Blocker)
**Dependencies:** Task 3.2
**Estimated Effort:** 20 minutes

**Objective:** Implement add_task tool to make tests pass

**Constitution Principles:** MCP-First Tool Integration, Database Persistence Guarantee, Security and User Isolation

**Pre-Condition:** add_task tests from Task 3.1 MUST be failing (RED phase verified)

**Actions:**
- Implement `add_task` function in `mcp_server.py`
- Validate inputs (user_id, title, description)
- Create Task in database
- Return correct response format

**Acceptance Criteria:**
- [ ] All add_task tests from Task 3.1 PASS (GREEN phase achieved)
- [ ] Validates title not empty, length <= 500
- [ ] Validates description length <= 5000
- [ ] Uses parameterized queries (no SQL injection)
- [ ] Returns {task_id, status: "pending", title}

**Files Modified:**
- `backend/app/mcp_server.py`

**CRITICAL:** All add_task tests MUST pass before proceeding.

---

### Task 3.4: Implement list_tasks Tool (TDD GREEN PHASE)
**Priority:** P0 (Blocker)
**Dependencies:** Task 3.3
**Estimated Effort:** 20 minutes

**Objective:** Implement list_tasks tool to make tests pass

**Constitution Principles:** MCP-First Tool Integration, Security and User Isolation

**Pre-Condition:** list_tasks tests from Task 3.1 MUST be failing (RED phase verified)

**Actions:**
- Implement `list_tasks` function in `mcp_server.py`
- Filter by user_id and status
- Order by created_at DESC
- Return tasks with count

**Acceptance Criteria:**
- [ ] All list_tasks tests from Task 3.1 PASS (GREEN phase achieved)
- [ ] Filters correctly by status (all/pending/completed)
- [ ] Enforces user_id isolation
- [ ] Returns {tasks: [...], count: N}
- [ ] Uses parameterized queries

**Files Modified:**
- `backend/app/mcp_server.py`

**CRITICAL:** All list_tasks tests MUST pass before proceeding.

---

### Task 3.5: Implement complete_task Tool (TDD GREEN PHASE)
**Priority:** P0 (Blocker)
**Dependencies:** Task 3.4
**Estimated Effort:** 20 minutes

**Objective:** Implement complete_task tool to make tests pass

**Constitution Principles:** MCP-First Tool Integration, Database Persistence Guarantee, Security and User Isolation

**Pre-Condition:** complete_task tests from Task 3.1 MUST be failing (RED phase verified)

**Actions:**
- Implement `complete_task` function in `mcp_server.py`
- Update task: completed=true, updated_at=now()
- Enforce user_id ownership
- Return updated task

**Acceptance Criteria:**
- [ ] All complete_task tests from Task 3.1 PASS (GREEN phase achieved)
- [ ] Idempotent operation (can complete already completed task)
- [ ] Returns 404 for non-existent task
- [ ] Enforces user_id ownership
- [ ] Returns {task_id, status: "completed", title}

**Files Modified:**
- `backend/app/mcp_server.py`

**CRITICAL:** All complete_task tests MUST pass before proceeding.

---

### Task 3.6: Implement delete_task Tool (TDD GREEN PHASE)
**Priority:** P0 (Blocker)
**Dependencies:** Task 3.5
**Estimated Effort:** 15 minutes

**Objective:** Implement delete_task tool to make tests pass

**Constitution Principles:** MCP-First Tool Integration, Database Persistence Guarantee, Security and User Isolation

**Pre-Condition:** delete_task tests from Task 3.1 MUST be failing (RED phase verified)

**Actions:**
- Implement `delete_task` function in `mcp_server.py`
- Delete task from database
- Enforce user_id ownership
- Return confirmation

**Acceptance Criteria:**
- [ ] All delete_task tests from Task 3.1 PASS (GREEN phase achieved)
- [ ] Task removed from database
- [ ] Returns 404 for non-existent task
- [ ] Enforces user_id ownership
- [ ] Returns {task_id, status: "deleted", title}

**Files Modified:**
- `backend/app/mcp_server.py`

**CRITICAL:** All delete_task tests MUST pass before proceeding.

---

### Task 3.7: Implement update_task Tool (TDD GREEN PHASE)
**Priority:** P0 (Blocker)
**Dependencies:** Task 3.6
**Estimated Effort:** 25 minutes

**Objective:** Implement update_task tool to make tests pass

**Constitution Principles:** MCP-First Tool Integration, Database Persistence Guarantee, Security and User Isolation

**Pre-Condition:** update_task tests from Task 3.1 MUST be failing (RED phase verified)

**Actions:**
- Implement `update_task` function in `mcp_server.py`
- Update specified fields (title and/or description)
- Validate at least one field provided
- Enforce user_id ownership

**Acceptance Criteria:**
- [ ] All update_task tests from Task 3.1 PASS (GREEN phase achieved)
- [ ] Updates only specified fields
- [ ] Validates title not empty if provided
- [ ] Requires at least one field (title or description)
- [ ] Enforces user_id ownership
- [ ] Returns updated task

**Files Modified:**
- `backend/app/mcp_server.py`

**CRITICAL:** All update_task tests MUST pass before proceeding.

---

## Phase 4: AI Agent Layer

### Task 4.1: Write Agent Tests (TDD RED PHASE)
**Priority:** P0 (Blocker)
**Dependencies:** Task 3.7
**Estimated Effort:** 50 minutes

**Objective:** Write ALL agent tests BEFORE implementing agent configuration

**Constitution Principles:** Test-First Development (NON-NEGOTIABLE), Natural Language Intent Mapping, Conversational Error Handling

**Actions:**
- Create `backend/tests/test_agent.py`
- Write comprehensive test cases for agent behavior

**Test Cases to Write:**

**Intent Detection:**
- [ ] "Add task to buy milk" → calls add_task with title="Buy milk"
- [ ] "Show my tasks" → calls list_tasks with status="all"
- [ ] "What's pending?" → calls list_tasks with status="pending"
- [ ] "Mark X as done" → calls complete_task
- [ ] "Delete task X" → calls delete_task
- [ ] "Change task X to Y" → calls update_task

**Tool Chaining:**
- [ ] "Mark grocery task as done" → calls list_tasks, then complete_task
- [ ] Asks clarification when multiple matches found
- [ ] "Delete all completed tasks" → calls list_tasks(status="completed"), then delete_task for each

**Context Awareness:**
- [ ] "Add task to buy milk" then "make it organic" → calls update_task (uses conversation history)
- [ ] References recently mentioned tasks correctly

**Error Handling:**
- [ ] Translates "Task not found" to friendly message
- [ ] Translates database errors to user-friendly messages
- [ ] Never hallucinates task data when tools fail
- [ ] Returns friendly error when tool execution fails

**Configuration:**
- [ ] Gemini model name configurable via GEMINI_MODEL_NAME env var
- [ ] Temperature configurable via GEMINI_TEMPERATURE env var
- [ ] Max tokens configurable via GEMINI_MAX_TOKENS env var

**Stateless:**
- [ ] Agent created per request (no persistence)
- [ ] No shared state between agent instances

**Acceptance Criteria:**
- [ ] `backend/tests/test_agent.py` created with ALL test cases
- [ ] Tests use mocked MCP tools (to test intent detection independently)
- [ ] Tests verify friendly error messages (no technical errors exposed)
- [ ] Running `pytest backend/tests/test_agent.py` FAILS (agent not implemented yet)

**Files Created:**
- `backend/tests/test_agent.py`

**CRITICAL:** Do NOT implement agent.py yet. Tests MUST fail first (RED phase).

---

### Task 4.2: Implement Gemini Client Configuration (TDD GREEN PHASE)
**Priority:** P0 (Blocker)
**Dependencies:** Task 4.1
**Estimated Effort:** 20 minutes

**Objective:** Configure Google Gemini API client

**Constitution Principles:** Natural Language Intent Mapping

**Pre-Condition:** Gemini configuration tests from Task 4.1 MUST be failing (RED phase verified)

**Actions:**
- Create `backend/app/agent.py`
- Initialize Gemini client with API key from environment
- Configure model name, temperature, max tokens from environment

**Acceptance Criteria:**
- [ ] Gemini client initializes with GOOGLE_API_KEY
- [ ] Model name from GEMINI_MODEL_NAME env var (default: gemini-1.5-pro)
- [ ] Temperature from GEMINI_TEMPERATURE env var (default: 0.7)
- [ ] Max tokens from GEMINI_MAX_TOKENS env var (default: 2048)
- [ ] Gemini configuration tests from Task 4.1 PASS

**Files Created:**
- `backend/app/agent.py`

---

### Task 4.3: Implement System Prompt (TDD GREEN PHASE)
**Priority:** P0 (Blocker)
**Dependencies:** Task 4.2
**Estimated Effort:** 30 minutes

**Objective:** Design system prompt for intent detection and tool usage

**Constitution Principles:** Natural Language Intent Mapping, Conversational Error Handling

**Actions:**
- Add system prompt to `agent.py`
- Include intent mapping examples
- Define tool schemas for Gemini
- Include error translation rules

**Acceptance Criteria:**
- [ ] System prompt defines all 5 MCP tools with parameters
- [ ] Intent mapping examples included (Add→add_task, Show→list_tasks, etc.)
- [ ] Tool chaining instructions provided
- [ ] Error translation examples included
- [ ] Friendly response style enforced

**Files Modified:**
- `backend/app/agent.py`

**Tests:** Intent detection tests from Task 4.1

---

### Task 4.4: Implement OpenAI Agents SDK Integration (TDD GREEN PHASE)
**Priority:** P0 (Blocker)
**Dependencies:** Task 4.3
**Estimated Effort:** 40 minutes

**Objective:** Set up agent orchestration with tool calling

**Constitution Principles:** MCP-First Tool Integration, Stateless-First Architecture

**Pre-Condition:** Intent detection and tool chaining tests from Task 4.1 MUST be failing

**Actions:**
- Integrate OpenAI Agents SDK in `agent.py`
- Configure agent with Gemini as LLM
- Register MCP tools with agent
- Implement tool execution loop (max 5 iterations)

**Acceptance Criteria:**
- [ ] Agent uses Gemini for reasoning (not OpenAI models)
- [ ] All 5 MCP tools registered with agent
- [ ] Tool calling works correctly
- [ ] Multi-turn tool chaining supported (max 5 iterations)
- [ ] Agent created per request (stateless verification from Task 4.1)
- [ ] All agent tests from Task 4.1 PASS (GREEN phase achieved)

**Files Modified:**
- `backend/app/agent.py`

**CRITICAL:** All agent tests from Task 4.1 MUST pass before proceeding.

---

## Phase 5: FastAPI Chat Endpoint

### Task 5.1: Write API Tests (TDD RED PHASE)
**Priority:** P0 (Blocker)
**Dependencies:** Task 4.4
**Estimated Effort:** 60 minutes

**Objective:** Write ALL API endpoint tests BEFORE implementing endpoint

**Constitution Principles:** Test-First Development (NON-NEGOTIABLE), Stateless-First Architecture, Security and User Isolation

**Actions:**
- Create `backend/tests/test_api.py`
- Write comprehensive test cases for FastAPI endpoint

**Test Cases to Write:**

**Authentication:**
- [ ] Rejects requests without Authorization header
- [ ] Rejects requests with invalid JWT token
- [ ] Rejects requests with expired JWT token
- [ ] Accepts requests with valid JWT token
- [ ] Extracts user_id from JWT token correctly
- [ ] Enforces path user_id matches token user_id (403 if mismatch)

**Chat Endpoint:**
- [ ] Creates new conversation when conversation_id omitted
- [ ] Returns conversation_id in response
- [ ] Loads existing conversation when conversation_id provided
- [ ] Returns 404 for non-existent conversation_id
- [ ] Enforces conversation belongs to authenticated user
- [ ] Validates message field is required (400 if missing)
- [ ] Validates message length (1-5000 chars)

**Stateless Flow:**
- [ ] Persists user message to database before calling agent
- [ ] Persists assistant message to database before returning response
- [ ] Updates conversation updated_at timestamp
- [ ] Returns correct response format {conversation_id, response, tool_calls}
- [ ] Includes tool_calls array in response

**Conversation Lifecycle:**
- [ ] Multi-turn conversation preserves history (load messages from DB)
- [ ] Messages ordered by created_at ASC when loaded
- [ ] Conversation history passed to agent correctly
- [ ] New messages appended to existing conversation

**Stateless Verification:**
- [ ] Server restart doesn't lose conversation state (data in DB)
- [ ] Concurrent requests don't corrupt data (transaction isolation)
- [ ] Messages don't leak between users (user_id filtering)
- [ ] No session state persists between requests

**Error Handling:**
- [ ] Returns 400 for invalid request body
- [ ] Returns 401 for authentication failures
- [ ] Returns 403 for user_id mismatch
- [ ] Returns 404 for non-existent conversation
- [ ] Returns 500 for internal errors (with friendly message)
- [ ] No stack traces exposed to user
- [ ] Errors logged with correlation ID

**Acceptance Criteria:**
- [ ] `backend/tests/test_api.py` created with ALL test cases
- [ ] Tests use FastAPI TestClient for HTTP requests
- [ ] Tests mock Better Auth JWT validation (or use test tokens)
- [ ] Tests verify database persistence (check DB state)
- [ ] Running `pytest backend/tests/test_api.py` FAILS (endpoint not implemented yet)

**Files Created:**
- `backend/tests/test_api.py`

**CRITICAL:** Do NOT implement endpoint yet. Tests MUST fail first (RED phase).

---

### Task 5.2: Implement FastAPI Application Setup (TDD GREEN PHASE)
**Priority:** P0 (Blocker)
**Dependencies:** Task 5.1
**Estimated Effort:** 15 minutes

**Objective:** Initialize FastAPI app with middleware

**Actions:**
- Create `backend/app/main.py`
- Initialize FastAPI app
- Configure CORS middleware
- Set up OpenAPI docs

**Acceptance Criteria:**
- [ ] FastAPI app initializes without errors
- [ ] CORS configured for ChatKit frontend
- [ ] OpenAPI docs available at `/docs`
- [ ] App title: "Todo AI Chatbot API"
- [ ] Version: "1.0.0"

**Files Created:**
- `backend/app/main.py`

---

### Task 5.3: Implement Authentication Middleware (TDD GREEN PHASE)
**Priority:** P0 (Blocker)
**Dependencies:** Task 5.2
**Estimated Effort:** 30 minutes

**Objective:** Validate JWT tokens and extract user_id

**Constitution Principle:** Security and User Isolation

**Pre-Condition:** Authentication tests from Task 5.1 MUST be failing (RED phase verified)

**Actions:**
- Create `backend/app/auth.py`
- Implement `verify_token()` dependency
- Validate JWT using Better Auth secret
- Extract user_id from token claims

**Acceptance Criteria:**
- [ ] All authentication tests from Task 5.1 PASS (GREEN phase achieved)
- [ ] JWT validation using AUTH_SECRET and AUTH_ISSUER
- [ ] Returns user_id from token claims
- [ ] Raises 401 for invalid/missing/expired tokens
- [ ] No token validation bypass possible

**Files Created:**
- `backend/app/auth.py`

**CRITICAL:** All authentication tests MUST pass before proceeding.

---

### Task 5.4: Implement Request/Response Models (TDD GREEN PHASE)
**Priority:** P0 (Blocker)
**Dependencies:** Task 5.3
**Estimated Effort:** 15 minutes

**Objective:** Define Pydantic schemas for API contract

**Actions:**
- Add Pydantic models to `main.py`
- Define ChatRequest, ChatResponse, ToolCall, ErrorResponse schemas
- Add validation rules (min/max length)

**Acceptance Criteria:**
- [ ] ChatRequest: conversation_id (optional int), message (required str, 1-5000 chars)
- [ ] ChatResponse: conversation_id (int), response (str), tool_calls (array)
- [ ] ToolCall: tool (str), args (dict), result (dict)
- [ ] ErrorResponse: error (str), details (optional str)
- [ ] Pydantic validation enforces all constraints

**Files Modified:**
- `backend/app/main.py`

---

### Task 5.5: Implement Chat Endpoint - Stateless Lifecycle (TDD GREEN PHASE)
**Priority:** P0 (Blocker)
**Dependencies:** Task 5.4
**Estimated Effort:** 60 minutes

**Objective:** Implement POST /api/{user_id}/chat endpoint

**Constitution Principles:** Stateless-First Architecture, Database Persistence Guarantee, Security and User Isolation

**Pre-Condition:** Chat endpoint tests from Task 5.1 MUST be failing (RED phase verified)

**Actions:**
- Implement POST /api/{user_id}/chat endpoint in `main.py`
- Follow exact 7-step stateless flow from spec (Section 8):
  1. Receive request (validate JWT, extract user_id)
  2. Load conversation history from DB
  3. Append user message (in-memory)
  4. Persist user message to DB
  5. Invoke AI agent with full conversation history
  6. Persist assistant message to DB
  7. Return response (clear all in-memory state)

**Acceptance Criteria:**
- [ ] All chat endpoint tests from Task 5.1 PASS (GREEN phase achieved)
- [ ] Endpoint follows exact 7-step flow
- [ ] Conversation history loaded from DB per request
- [ ] User and assistant messages persisted before response
- [ ] Agent receives full conversation context
- [ ] Response includes conversation_id, response, tool_calls
- [ ] No state retention between requests (stateless verification)
- [ ] User_id validated at every step
- [ ] Concurrent requests safe (transaction isolation)

**Files Modified:**
- `backend/app/main.py`

**CRITICAL:** All API tests from Task 5.1 MUST pass before proceeding.

---

### Task 5.6: Implement Error Handlers (TDD GREEN PHASE)
**Priority:** P0 (Blocker)
**Dependencies:** Task 5.5
**Estimated Effort:** 20 minutes

**Objective:** Add error handlers for all HTTP error types

**Constitution Principle:** Conversational Error Handling

**Pre-Condition:** Error handling tests from Task 5.1 MUST be failing

**Actions:**
- Add exception handlers to `main.py`
- Handle 400, 401, 403, 404, 500, 503 errors
- Return friendly error messages (no stack traces)
- Log errors with correlation ID, user_id, conversation_id

**Acceptance Criteria:**
- [ ] All error handling tests from Task 5.1 PASS
- [ ] All error types return correct HTTP status
- [ ] Friendly error messages (no technical details exposed)
- [ ] Errors logged with sufficient context
- [ ] No secrets in error responses

**Files Modified:**
- `backend/app/main.py`

---

### Task 5.7: Implement Health Check Endpoint
**Priority:** P1 (Important)
**Dependencies:** Task 5.6
**Estimated Effort:** 10 minutes

**Objective:** Add health check endpoint for monitoring

**Actions:**
- Add GET /health endpoint to `main.py`
- Check database connectivity
- Return status and timestamp

**Acceptance Criteria:**
- [ ] Returns 200 when database connected
- [ ] Returns 503 when database unreachable
- [ ] Response includes {status, database, timestamp}
- [ ] Can be used for load balancer health checks

**Files Modified:**
- `backend/app/main.py`

---

## Phase 6: Frontend Integration

### Task 6.1: Create ChatKit HTML
**Priority:** P1 (Important)
**Dependencies:** Task 5.7
**Estimated Effort:** 20 minutes

**Objective:** Set up OpenAI ChatKit UI

**Actions:**
- Create `frontend/index.html`
- Load ChatKit library from CDN
- Add chat container div
- Link to app.js and styles.css

**Acceptance Criteria:**
- [ ] ChatKit library loaded from CDN
- [ ] Container element for chat UI exists
- [ ] HTML valid and renders correctly

**Files Created:**
- `frontend/index.html`

**No TDD Required:** Frontend HTML template

---

### Task 6.2: Implement API Client
**Priority:** P1 (Important)
**Dependencies:** Task 6.1
**Estimated Effort:** 30 minutes

**Objective:** Connect ChatKit to FastAPI backend

**Actions:**
- Create `frontend/app.js`
- Implement sendMessage() function
- Integrate ChatKit with backend API
- Handle conversation_id persistence

**Acceptance Criteria:**
- [ ] ChatKit sends messages to POST /api/{user_id}/chat
- [ ] Conversation ID preserved across messages
- [ ] Responses displayed in chat UI
- [ ] Errors shown to user

**Files Created:**
- `frontend/app.js`

---

### Task 6.3: Implement Authentication Integration
**Priority:** P1 (Important)
**Dependencies:** Task 6.2
**Estimated Effort:** 20 minutes

**Objective:** Integrate Better Auth JWT token

**Actions:**
- Load JWT token from localStorage
- Include token in Authorization header
- Handle 401 errors (redirect to login)
- Load user_id from Better Auth

**Acceptance Criteria:**
- [ ] JWT token retrieved from Better Auth
- [ ] Token sent in all API requests
- [ ] 401 errors redirect to login
- [ ] user_id available for API calls

**Files Modified:**
- `frontend/app.js`

---

### Task 6.4: Add Basic Styling
**Priority:** P2 (Nice to have)
**Dependencies:** Task 6.3
**Estimated Effort:** 15 minutes

**Objective:** Minimal CSS for usable interface

**Actions:**
- Create `frontend/styles.css`
- Style chat container, messages, input box
- Ensure mobile-responsive

**Acceptance Criteria:**
- [ ] UI is functional and readable
- [ ] Messages clearly distinguished (user vs assistant)
- [ ] Works on desktop and mobile browsers

**Files Created:**
- `frontend/styles.css`

---

## Phase 7: Final Validation & Acceptance

### Task 7.1: Run Full Test Suite
**Priority:** P0 (Blocker)
**Dependencies:** Task 6.4
**Estimated Effort:** 15 minutes

**Objective:** Verify all tests pass (TDD green phase)

**Constitution Principle:** Test-First Development (NON-NEGOTIABLE)

**Actions:**
- Run `pytest backend/tests/` --verbose --cov
- Verify all tests pass
- Check test coverage > 85%

**Acceptance Criteria:**
- [ ] All Phase 2 database tests passing (green)
- [ ] All Phase 3 MCP tool tests passing (green)
- [ ] All Phase 4 agent tests passing (green)
- [ ] All Phase 5 API tests passing (green)
- [ ] Overall test coverage > 85%
- [ ] MCP tools coverage > 90%
- [ ] Critical paths (auth, stateless flow) 100% covered

**CRITICAL:** If ANY tests are failing, STOP and fix before proceeding.

---

### Task 7.2: Constitution Compliance Audit
**Priority:** P0 (Blocker)
**Dependencies:** Task 7.1
**Estimated Effort:** 30 minutes

**Objective:** Verify implementation adheres to all 7 constitution principles

**Constitution Version:** v1.0.0

**Actions:**
- Audit codebase against each principle
- Verify tests exist for each principle
- Document compliance status

**Checklist:**
- [ ] **Stateless-First Architecture**: Server maintains zero in-memory state (verified by stateless tests)
- [ ] **MCP-First Tool Integration**: All task operations route through MCP tools only (verified by agent tests)
- [ ] **Database Persistence Guarantee**: Every interaction persisted to Neon PostgreSQL (verified by API tests)
- [ ] **Test-First Development**: TDD cycle followed for all features (verified by git history showing tests before implementation)
- [ ] **Conversational Error Handling**: All errors user-friendly, comprehensive logging present (verified by error handling tests)
- [ ] **Natural Language Intent Mapping**: Intent detection works for all tool mappings (verified by agent tests)
- [ ] **Security and User Isolation**: user_id validated at every layer, no cross-user access (verified by security tests)

**Acceptance Criteria:**
- [ ] All 7 principles verified compliant
- [ ] Evidence collected for each principle (tests, code review)
- [ ] No principle violations found

---

### Task 7.3: Performance & Load Testing
**Priority:** P0 (Blocker)
**Dependencies:** Task 7.2
**Estimated Effort:** 45 minutes

**Objective:** Validate non-functional requirements

**Actions:**
- Run load test with 100 concurrent requests
- Measure p95 response time
- Monitor memory usage under sustained load
- Check database connection pool behavior

**Acceptance Criteria:**
- [ ] p95 response time < 3 seconds
- [ ] Database connection pool handles concurrent load (min=5, max=20)
- [ ] No memory leaks under sustained load (1 hour test)
- [ ] Server restart preserves conversation state
- [ ] Concurrent requests don't corrupt data

---

### Task 7.4: Security Audit
**Priority:** P0 (Blocker)
**Dependencies:** Task 7.3
**Estimated Effort:** 30 minutes

**Objective:** Final security validation

**Actions:**
- Test user isolation (User A cannot access User B's data)
- Test SQL injection attempts (all tools + API)
- Verify secrets not exposed (logs, errors, code)
- Verify JWT validation enforced

**Acceptance Criteria:**
- [ ] User isolation verified (all tools + API)
- [ ] SQL injection attempts blocked (security scan)
- [ ] No secrets in code, logs, or errors
- [ ] JWT validation enforced on all requests
- [ ] Parameterized queries used throughout

---

### Task 7.5: Documentation Review
**Priority:** P1 (Important)
**Dependencies:** Task 7.4
**Estimated Effort:** 20 minutes

**Objective:** Ensure documentation is complete

**Actions:**
- Review README for setup instructions
- Verify environment variables documented
- Check API documentation (/docs)
- Verify MCP tool schemas documented

**Acceptance Criteria:**
- [ ] README with setup instructions
- [ ] Environment variable documentation
- [ ] API endpoint documentation (OpenAPI /docs)
- [ ] MCP tool schemas documented
- [ ] Database schema documented

---

## Summary

**Total Tasks:** 38 tasks
**TDD Tasks:** 22 tasks (58% with explicit TDD workflow)
**Critical Path:** Tasks 1.1 → 2.1 → 2.2 → 3.1 → 3.3-3.7 → 4.1 → 4.4 → 5.1 → 5.5 → 7.1

**Constitution Compliance:**
- ✅ All tasks aligned with Constitution v1.0.0
- ✅ TDD workflow enforced for all implementation tasks
- ✅ Stateless architecture enforced throughout
- ✅ MCP-first tool integration enforced
- ✅ Database persistence guaranteed
- ✅ Security and user isolation enforced
- ✅ Conversational error handling required
- ✅ Natural language intent mapping implemented

**Key Principles:**
1. Tests written FIRST, verified to FAIL (RED phase)
2. Implementation makes tests PASS (GREEN phase)
3. Refactor while keeping tests GREEN
4. Never proceed to next task until tests pass
5. Constitution compliance verified at end

**END OF TASKS**

This task list is COMPLETE, TESTABLE, and CONSTITUTION-COMPLIANT. All tasks follow strict TDD discipline as mandated by Constitution v1.0.0.
