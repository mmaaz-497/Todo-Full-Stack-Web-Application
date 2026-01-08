# /sp.constituent: Todo AI Chatbot Specification

## Metadata
```yaml
feature: todo-ai-chatbot
version: 1.1.0
stage: specification
created: 2025-12-27
updated: 2025-12-27
surface: agent
development_method: Agentic Dev Stack (Spec → Plan → Tasks → Implementation)
llm_provider: Google Gemini
status: draft
```

## 1. System Overview

### Purpose
Build a stateless AI-powered chatbot that enables users to manage Todo tasks through natural language conversation. The system uses MCP (Model Context Protocol) tools for all task operations and persists all state in a PostgreSQL database.

### Core Principles
1. **Stateless Architecture**: Zero in-memory state; all conversation and task data persists in database
2. **MCP-First Operations**: All task operations MUST route through MCP tools
3. **Natural Language Interface**: Users interact conversationally; AI detects intent and executes operations
4. **Agentic Development**: Implementation via Claude Code following Spec → Plan → Tasks workflow

### Success Criteria
- User can manage todos via natural conversation
- All operations persist correctly in database
- Server maintains zero stateful session data
- MCP tools handle 100% of task operations
- Conversation history loads per-request from database
- System handles concurrent requests safely

## 2. Technology Stack

### Frontend
- **Framework**: OpenAI ChatKit
- **Purpose**: Pre-built conversational UI
- **Responsibility**: Message display, user input, HTTP client

### Backend
- **Framework**: Python FastAPI
- **Version**: 0.100+
- **Purpose**: HTTP API server, request orchestration
- **Responsibility**: Auth validation, conversation loading, agent invocation, response formatting

### AI Layer
- **Framework**: OpenAI Agents SDK
- **LLM Provider**: Google Gemini
- **Purpose**: Intent detection, tool orchestration, response generation
- **Responsibility**: Parse natural language, call MCP tools, generate conversational responses

#### LLM Configuration
- **Provider**: Google (Gemini API)
- **Model Family**: Gemini (configurable via environment variable)
- **Recommended Models**: `gemini-1.5-pro`, `gemini-1.5-flash`, or latest stable release
- **Configuration Parameters**:
  - Temperature: Configurable (default: 0.7)
  - Max Tokens: Configurable (default: 2048)
  - Top-P, Top-K: Configurable per deployment needs
- **Architecture Role**:
  - OpenAI Agents SDK provides orchestration layer ONLY
  - Google Gemini performs all natural language reasoning and generation
  - MCP tool selection is driven by Gemini outputs
  - Tool call decisions are made by Gemini based on conversation context

### MCP Server
- **SDK**: Official MCP Python SDK
- **Purpose**: Tool execution layer
- **Responsibility**: Database operations, task CRUD, stateless tool implementations

### Database
- **Provider**: Neon Serverless PostgreSQL
- **ORM**: SQLModel (Pydantic + SQLAlchemy)
- **Purpose**: Single source of truth for all state
- **Responsibility**: Task storage, conversation history, message persistence

### Authentication
- **Provider**: Better Auth
- **Purpose**: User identity and session management
- **Responsibility**: User authentication, user_id provisioning, JWT validation

## 3. Architecture

### High-Level Flow
```
ChatKit UI
    ↓ HTTP POST /api/{user_id}/chat
FastAPI Endpoint
    ↓ Load conversation history from DB
    ↓ Append new user message
    ↓ Store user message to DB
OpenAI Agent
    ↓ Analyze intent
    ↓ Call MCP tools (add_task, list_tasks, etc.)
MCP Server
    ↓ Execute database operations
Neon PostgreSQL
    ↑ Return results
OpenAI Agent
    ↑ Generate conversational response
FastAPI Endpoint
    ↑ Store assistant message to DB
    ↑ Return response JSON
ChatKit UI
```

### Stateless Guarantees
1. No in-memory conversation state
2. No session caching
3. No persistent agent instances
4. Every request loads full context from database
5. Conversation history reconstructed per-request
6. MCP tools have no state between calls

### LLM Provider Guarantees
1. **Provider Independence**: Swapping Google Gemini for another LLM requires ONLY environment variable changes
2. **No MCP Tool Changes**: MCP tool schemas, implementations, and contracts remain unchanged regardless of LLM provider
3. **No Database Changes**: Database schema, queries, and migrations are LLM-agnostic
4. **No API Contract Changes**: HTTP endpoints, request/response formats unchanged
5. **Orchestration Layer Stability**: OpenAI Agents SDK orchestration layer is LLM-agnostic

### Component Boundaries

**Frontend (ChatKit)**
- IN SCOPE: Message rendering, user input, HTTP requests
- OUT OF SCOPE: Business logic, state management, authentication logic

**Backend (FastAPI)**
- IN SCOPE: API endpoints, conversation loading, agent orchestration, persistence
- OUT OF SCOPE: AI logic, tool implementations, UI rendering

**AI Layer (OpenAI Agent + Gemini LLM)**
- IN SCOPE: Intent detection, tool selection, response generation, LLM orchestration
- OUT OF SCOPE: Database operations, HTTP handling, authentication
- **LLM Role**: Google Gemini performs all natural language understanding and generation; OpenAI Agents SDK orchestrates tool calls

**MCP Server**
- IN SCOPE: Task CRUD tools, database operations, tool schemas
- OUT OF SCOPE: AI decisions, conversation management, authentication

**Database (Neon)**
- IN SCOPE: Data persistence, queries, transactions
- OUT OF SCOPE: Business logic, tool definitions, AI operations

## 4. API Contracts

### Primary Endpoint

**POST /api/{user_id}/chat**

**Path Parameters:**
- `user_id` (string, required): Authenticated user identifier from Better Auth

**Request Body:**
```json
{
  "conversation_id": 123,  // Optional integer, omit for new conversation
  "message": "Add a task to buy groceries"  // Required string
}
```

**Response (Success - 200 OK):**
```json
{
  "conversation_id": 123,
  "response": "I've added the task 'Buy groceries' to your list.",
  "tool_calls": [
    {
      "tool": "add_task",
      "args": {
        "user_id": "user_123",
        "title": "Buy groceries",
        "description": null
      },
      "result": {
        "task_id": 456,
        "status": "pending",
        "title": "Buy groceries"
      }
    }
  ]
}
```

**Response (Error - 400 Bad Request):**
```json
{
  "error": "message field is required"
}
```

**Response (Error - 404 Not Found):**
```json
{
  "error": "Conversation not found"
}
```

**Response (Error - 401 Unauthorized):**
```json
{
  "error": "Invalid or missing authentication"
}
```

**Response (Error - 500 Internal Server Error):**
```json
{
  "error": "Internal server error",
  "details": "Optional error context for debugging"
}
```

### Authentication Headers
All requests must include:
```
Authorization: Bearer <jwt_token>
```

Better Auth validates token and extracts user_id.

## 5. Database Models (SQLModel)

### Task
```python
class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    title: str = Field(nullable=False)
    description: Optional[str] = Field(default=None)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Indexes:**
- Primary: `id`
- Secondary: `user_id`
- Composite: `(user_id, completed)` for filtered queries

**Constraints:**
- `title` cannot be empty string
- `user_id` must match authenticated user

### Conversation
```python
class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Indexes:**
- Primary: `id`
- Secondary: `user_id`

**Constraints:**
- `user_id` must match authenticated user
- `updated_at` updates on new message

### Message
```python
class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", nullable=False)
    user_id: str = Field(index=True, nullable=False)
    role: str = Field(nullable=False)  # "user" | "assistant"
    content: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

**Indexes:**
- Primary: `id`
- Secondary: `conversation_id`
- Composite: `(conversation_id, created_at)` for ordered retrieval

**Constraints:**
- `role` must be exactly "user" or "assistant"
- `conversation_id` must exist in conversations table
- `user_id` must match conversation owner
- `content` cannot be empty string

**Cascade Rules:**
- Delete conversation → cascade delete all messages

## 6. MCP Tool Specifications

All tools MUST be stateless and persist data via database operations.

### add_task

**Purpose:** Create a new task for the user

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "user_id": {"type": "string", "description": "Authenticated user ID"},
    "title": {"type": "string", "description": "Task title"},
    "description": {"type": "string", "description": "Optional task details"}
  },
  "required": ["user_id", "title"]
}
```

**Output Schema:**
```json
{
  "task_id": 123,
  "status": "pending",
  "title": "Buy groceries"
}
```

**Error Cases:**
- Empty title → "Task title cannot be empty"
- Database failure → "Failed to create task"

**Side Effects:**
- Inserts row into `tasks` table
- Sets `completed=false`, `created_at=now()`, `updated_at=now()`

---

### list_tasks

**Purpose:** Retrieve tasks for the user

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "user_id": {"type": "string", "description": "Authenticated user ID"},
    "status": {
      "type": "string",
      "enum": ["all", "pending", "completed"],
      "default": "all",
      "description": "Filter by task status"
    }
  },
  "required": ["user_id"]
}
```

**Output Schema:**
```json
{
  "tasks": [
    {
      "task_id": 123,
      "title": "Buy groceries",
      "description": null,
      "status": "pending",
      "created_at": "2025-12-27T10:00:00Z"
    }
  ],
  "count": 1
}
```

**Error Cases:**
- Invalid status value → "Status must be 'all', 'pending', or 'completed'"
- Database failure → "Failed to retrieve tasks"

**Side Effects:**
- None (read-only)

**Query Logic:**
- `status="all"` → return all tasks for user_id
- `status="pending"` → return tasks where `completed=false`
- `status="completed"` → return tasks where `completed=true`
- Order by `created_at DESC`

---

### complete_task

**Purpose:** Mark a task as completed

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "user_id": {"type": "string", "description": "Authenticated user ID"},
    "task_id": {"type": "integer", "description": "Task to complete"}
  },
  "required": ["user_id", "task_id"]
}
```

**Output Schema:**
```json
{
  "task_id": 123,
  "status": "completed",
  "title": "Buy groceries"
}
```

**Error Cases:**
- Task not found → "Task not found"
- Task belongs to different user → "Unauthorized access to task"
- Already completed → Return success (idempotent)

**Side Effects:**
- Updates `completed=true`, `updated_at=now()`
- Returns updated task

---

### delete_task

**Purpose:** Permanently delete a task

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "user_id": {"type": "string", "description": "Authenticated user ID"},
    "task_id": {"type": "integer", "description": "Task to delete"}
  },
  "required": ["user_id", "task_id"]
}
```

**Output Schema:**
```json
{
  "task_id": 123,
  "status": "deleted",
  "title": "Buy groceries"
}
```

**Error Cases:**
- Task not found → "Task not found"
- Task belongs to different user → "Unauthorized access to task"

**Side Effects:**
- Deletes row from `tasks` table
- Operation is idempotent (deleting non-existent task returns error)

---

### update_task

**Purpose:** Modify task title or description

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "user_id": {"type": "string", "description": "Authenticated user ID"},
    "task_id": {"type": "integer", "description": "Task to update"},
    "title": {"type": "string", "description": "New title (optional)"},
    "description": {"type": "string", "description": "New description (optional)"}
  },
  "required": ["user_id", "task_id"]
}
```

**Output Schema:**
```json
{
  "task_id": 123,
  "status": "pending",
  "title": "Buy organic groceries",
  "description": "Include fruits and vegetables"
}
```

**Error Cases:**
- Task not found → "Task not found"
- Task belongs to different user → "Unauthorized access to task"
- No fields provided → "At least one field (title or description) must be provided"
- Empty title → "Task title cannot be empty"

**Side Effects:**
- Updates specified fields
- Updates `updated_at=now()`
- Unspecified fields remain unchanged

## 7. Agent Behavior Rules

### Intent Detection
The AI Agent (powered by Google Gemini) MUST analyze natural language and map to correct MCP tools:

**Intent Mapping:**
| User Intent | Examples | Tool |
|-------------|----------|------|
| Add/Create | "Add task to...", "Remember to...", "Create a task for..." | `add_task` |
| List/Show | "Show my tasks", "What do I need to do?", "List pending tasks" | `list_tasks` |
| Complete/Finish | "Mark X as done", "I finished Y", "Complete task Z" | `complete_task` |
| Delete/Remove | "Delete task X", "Remove Y from my list", "Cancel task Z" | `delete_task` |
| Update/Change | "Change task X to Y", "Update description of Z", "Rename task..." | `update_task` |

### Multi-Step Operations
Agent MUST chain tools when required:

**Example 1: Ambiguous Reference**
- User: "Mark the grocery task as done"
- Agent:
  1. Call `list_tasks(status="pending")`
  2. If multiple matches, ask clarification
  3. Call `complete_task(task_id=X)`

**Example 2: Bulk Operations**
- User: "Mark all shopping tasks as done"
- Agent:
  1. Call `list_tasks(status="pending")`
  2. Filter tasks containing "shopping"
  3. Call `complete_task` for each match
  4. Summarize results

### Conversational Confirmations
Agent MUST confirm actions with friendly language:

**Examples:**
- After `add_task`: "I've added 'Buy groceries' to your task list."
- After `complete_task`: "Great! I've marked 'Buy groceries' as completed."
- After `delete_task`: "I've removed 'Old task' from your list."
- After `list_tasks` (empty): "You don't have any tasks right now. Want to add one?"

### Error Handling
Agent MUST translate technical errors into friendly messages:

**Error Translation:**
- "Task not found" → "I couldn't find that task. Could you describe it differently?"
- "Unauthorized access" → "That task doesn't seem to belong to you."
- "Database failure" → "I'm having trouble accessing your tasks right now. Please try again."
- "Empty title" → "Task titles can't be empty. What would you like to call this task?"

### Disambiguation
When intent is unclear, agent MUST ask clarifying questions:

**Examples:**
- Multiple matching tasks → "I found 3 tasks about groceries. Which one did you mean: 1) Buy groceries, 2) Organize groceries, 3) Plan grocery list?"
- Ambiguous action → "Did you want me to complete the task or delete it?"
- Missing information → "What would you like the task to be called?"

### Context Awareness
Agent MUST reference conversation history:

**Examples:**
- User: "Add a task to buy milk"
- Agent: "Added 'Buy milk' to your list."
- User: "Actually, make it organic milk"
- Agent: *Uses context to identify task_id* "I've updated the task to 'Buy organic milk'."

## 8. Stateless Conversation Flow

### Per-Request Execution
Every HTTP request follows this exact sequence:

**Step 1: Receive Request**
- Validate JWT token (Better Auth)
- Extract `user_id` from token
- Parse request body (`conversation_id`, `message`)

**Step 2: Load Conversation History**
- If `conversation_id` provided:
  - Query `conversations` table for `id=conversation_id AND user_id=user_id`
  - If not found → 404 error
  - Query `messages` table for `conversation_id=conversation_id ORDER BY created_at ASC`
- If `conversation_id` omitted:
  - Create new conversation in database
  - Initialize empty message list

**Step 3: Append User Message**
- Create message object: `{role: "user", content: message}`
- Append to conversation history (in-memory only)

**Step 4: Persist User Message**
- Insert into `messages` table:
  - `conversation_id`, `user_id`, `role="user"`, `content=message`, `created_at=now()`
- Update conversation `updated_at=now()`

**Step 5: Invoke AI Agent**
- Pass full conversation history to agent (OpenAI Agents SDK orchestration)
- Google Gemini analyzes intent from conversation context
- Gemini determines which MCP tools to call and with what parameters
- Agent orchestrator calls MCP tools via MCP server
- Gemini generates conversational response based on tool results

**Step 6: Persist Assistant Message**
- Insert into `messages` table:
  - `conversation_id`, `user_id`, `role="assistant"`, `content=agent_response`, `created_at=now()`
- Update conversation `updated_at=now()`

**Step 7: Return Response**
- Format JSON response with `conversation_id`, `response`, `tool_calls`
- Clear all in-memory state
- End request

### No State Retention
- Server retains ZERO state between requests
- No agent instances persist
- No conversation objects cached
- No user sessions in memory
- Every request is independent and complete

### Concurrency Safety
- Database handles concurrent writes via transactions
- No race conditions from stateless design
- Multiple users can interact simultaneously
- Same user can have multiple concurrent conversations

## 9. Error Handling Strategy

### Error Taxonomy

**Client Errors (4xx):**
- `400 Bad Request`: Malformed request body, missing required fields
- `401 Unauthorized`: Invalid/missing JWT token
- `403 Forbidden`: Valid token but insufficient permissions
- `404 Not Found`: Conversation or task doesn't exist
- `422 Unprocessable Entity`: Valid request but business rule violation (e.g., empty title)

**Server Errors (5xx):**
- `500 Internal Server Error`: Database failures, unexpected exceptions
- `503 Service Unavailable`: Database connection failure, Google Gemini API down

### User-Facing Error Messages
All errors returned to agent MUST be translated to friendly language:

**Technical → Friendly Mapping:**
- "foreign key constraint violation" → "That conversation doesn't exist anymore"
- "connection timeout" → "I'm having trouble connecting right now, please try again"
- "invalid json" → "I didn't understand that request format"
- "rate limit exceeded" → "I'm getting too many requests right now, please wait a moment"

### Logging Requirements
All errors MUST be logged with:
- Timestamp
- User ID
- Conversation ID
- Error type
- Stack trace (for 5xx errors)
- Request payload (sanitized)

### Retry Logic
- Database transient errors: Retry up to 3 times with exponential backoff
- Google Gemini API errors: Retry once after 1 second
- MCP tool failures: No retry, return error to agent

### Graceful Degradation
- If `list_tasks` fails → Agent responds "I can't check your tasks right now"
- If `add_task` fails → Agent responds "I couldn't add that task, please try again"
- If database is down → Return 503 with friendly message
- Agent MUST NOT hallucinate task data when tools fail

## 10. Security & Authorization

### Authentication Model
- **Provider:** Better Auth
- **Mechanism:** JWT tokens in `Authorization: Bearer <token>` header
- **Validation:** FastAPI middleware validates token before processing request
- **User Identity:** Extract `user_id` from validated token claims

### Authorization Rules
1. Users can ONLY access their own conversations and tasks
2. All database queries MUST filter by `user_id`
3. Conversations without matching `user_id` return 404 (not 403 to avoid leaking existence)
4. Tasks without matching `user_id` return "Task not found" (not "Unauthorized")

### Data Isolation
- **Query Pattern:** All SQL queries MUST include `WHERE user_id = :user_id`
- **No Cross-User Access:** Agent cannot access other users' data under any circumstance
- **MCP Tools:** All tools require `user_id` parameter and enforce ownership checks

### Input Validation
- **Message Content:** Sanitize for SQL injection (use parameterized queries)
- **Task Titles:** Max 500 characters
- **Task Descriptions:** Max 5000 characters
- **No HTML/Script Tags:** Strip or escape all HTML from user input

### Secrets Management
- Database connection string in environment variable `DATABASE_URL`
- Google Gemini API key in environment variable `GOOGLE_API_KEY`
- Better Auth secrets in environment variable `AUTH_SECRET`
- Never log secrets or include in error messages

## 11. Non-Functional Requirements

### Performance
- **Latency:** p95 response time < 3 seconds (including AI + database)
- **Throughput:** Support 100 concurrent requests per server instance
- **Database Queries:** Maximum 5 queries per request (load history, save messages)
- **Connection Pooling:** Maintain database connection pool (min=5, max=20)

### Reliability
- **Uptime SLO:** 99.5% availability
- **Error Budget:** 0.5% of requests may fail
- **Database Transactions:** All multi-step operations use ACID transactions
- **Idempotency:** Tool operations are idempotent where possible (e.g., complete_task)

### Observability
- **Logging:** Structured JSON logs with correlation IDs
- **Metrics:** Track request count, latency, error rate, tool usage
- **Tracing:** Distributed traces for request → agent → MCP → database flow
- **Alerts:** Trigger on error rate > 5%, p95 latency > 5s, database connection failures

### Scalability
- **Horizontal Scaling:** Stateless design allows unlimited server replicas
- **Database:** Neon serverless PostgreSQL auto-scales
- **No Bottlenecks:** No single-threaded components or shared locks
- **LLM Provider Independence:** Google Gemini can be swapped for another LLM without affecting MCP tools, database schema, or API contracts

## 12. Implementation Boundaries

### In Scope
- FastAPI HTTP server with single `/api/{user_id}/chat` endpoint
- SQLModel models for Task, Conversation, Message
- Database migrations (Alembic)
- MCP server with 5 tools (add_task, list_tasks, complete_task, delete_task, update_task)
- OpenAI Agent configuration with tool schemas
- Better Auth integration (JWT validation)
- Error handling and logging
- Basic ChatKit frontend integration
- Environment configuration (.env file)
- Database connection management
- Request/response validation (Pydantic)

### Out of Scope (Explicitly Excluded)
- User registration/login UI (Better Auth handles this)
- Task due dates, priorities, categories, tags
- Task reminders or notifications
- Multi-user collaboration (task sharing)
- File attachments on tasks
- Task search/filtering beyond status
- Real-time websocket updates
- Mobile app (ChatKit web only)
- Admin panel or analytics dashboard
- Rate limiting (assume handled by infrastructure)
- Caching layer (stateless design)
- Internationalization (English only)
- Dark mode or UI customization

### External Dependencies
- **Neon PostgreSQL:** Must be provisioned and accessible
- **Google Gemini API:** Must have valid API key with sufficient quota
- **Better Auth:** Must be configured with JWT issuer
- **MCP SDK:** Python package must be installed
- **OpenAI Agents SDK:** Python package must be installed (for orchestration layer only)
- **ChatKit:** Frontend library must be configured

### Assumptions
- Neon database is accessible via connection string
- Better Auth provides valid JWT tokens with `user_id` claim
- Google Gemini API is reachable and operational
- ChatKit sends correct HTTP request format
- Network latency between components is reasonable (<100ms)
- Database schema migrations are applied before deployment

## 13. Development Workflow (Agentic Dev Stack)

### Phase 1: Specification (Current Document)
- **Owner:** Human + Claude Code
- **Artifact:** This `/sp.constituent` document
- **Acceptance:** Complete specification with all sections filled

### Phase 2: Planning (`/sp.plan`)
- **Owner:** Claude Code (architect mode)
- **Input:** This specification
- **Output:** `specs/todo-ai-chatbot/plan.md`
- **Contents:**
  - Architecture decisions (e.g., FastAPI vs Flask, SQLModel vs raw SQLAlchemy)
  - MCP tool implementation approach
  - Database schema design details
  - OpenAI Agent configuration strategy
  - Error handling patterns
  - Deployment strategy

### Phase 3: Task Breakdown (`/sp.tasks`)
- **Owner:** Claude Code
- **Input:** Specification + Plan
- **Output:** `specs/todo-ai-chatbot/tasks.md`
- **Contents:**
  - Numbered, dependency-ordered tasks
  - Acceptance criteria for each task
  - Test cases where applicable
  - File paths to create/modify

### Phase 4: Implementation
- **Owner:** Claude Code (executor mode)
- **Input:** Specification + Plan + Tasks
- **Process:**
  - Execute tasks sequentially
  - Write code following specifications
  - Run tests after each task
  - Create PHR (Prompt History Record) after completion
  - Suggest ADR for architectural decisions

### No Manual Coding
- Human provides requirements and reviews artifacts
- Human approves plan and tasks
- Claude Code writes 100% of implementation code
- Human tests final system

## 14. Acceptance Criteria (Definition of Done)

### Functional Acceptance
- [ ] User can create tasks via natural language ("Add a task to buy milk")
- [ ] User can list tasks via natural language ("Show my tasks", "What's pending?")
- [ ] User can complete tasks via natural language ("Mark X as done")
- [ ] User can delete tasks via natural language ("Remove X")
- [ ] User can update tasks via natural language ("Change X to Y")
- [ ] Conversation history persists across requests
- [ ] Multiple conversations per user work correctly
- [ ] Agent detects intent correctly for all 5 tool operations
- [ ] Agent chains tools when needed (e.g., ambiguous task references)
- [ ] Agent provides friendly error messages for failures

### Technical Acceptance
- [ ] FastAPI server starts without errors
- [ ] MCP server registers 5 tools correctly
- [ ] Database migrations apply cleanly
- [ ] All database queries filter by `user_id`
- [ ] JWT validation rejects invalid tokens
- [ ] Server maintains zero stateful data between requests
- [ ] Concurrent requests don't corrupt data
- [ ] All errors log with required fields
- [ ] p95 response time < 3 seconds

### Security Acceptance
- [ ] Users cannot access other users' tasks
- [ ] Users cannot access other users' conversations
- [ ] SQL injection attempts are safely handled
- [ ] Secrets not exposed in logs or error messages
- [ ] All database queries use parameterized statements

### Testing Acceptance
- [ ] Unit tests for all MCP tools
- [ ] Integration tests for API endpoint
- [ ] Test for conversation history loading
- [ ] Test for stateless request handling
- [ ] Test for authorization checks
- [ ] Test for error cases (task not found, invalid input, etc.)

### Documentation Acceptance
- [ ] README with setup instructions
- [ ] Environment variable documentation
- [ ] API endpoint documentation
- [ ] MCP tool schemas documented
- [ ] Database schema documented

## 15. Risks & Mitigations

### Risk 1: Gemini LLM Intent Detection Failures
- **Impact:** Users get incorrect tool calls or no action
- **Probability:** Medium (natural language is ambiguous)
- **Mitigation:**
  - Provide extensive examples in Gemini system prompt
  - Implement fallback clarification questions
  - Log misdetections for prompt tuning
  - Leverage Gemini's strong reasoning capabilities for complex intent detection

### Risk 2: Database Connection Failures
- **Impact:** All requests fail, system unusable
- **Probability:** Low (Neon is reliable)
- **Mitigation:**
  - Connection pool with retry logic
  - Exponential backoff on transient errors
  - Health check endpoint for monitoring

### Risk 3: Conversation History Too Large
- **Impact:** Agent context window exceeded, slow queries
- **Probability:** Medium (long conversations)
- **Mitigation:**
  - Implement message limit per conversation (e.g., last 50 messages)
  - Summarize old messages before archiving
  - Add pagination if needed

### Kill Switch
- Environment variable `SYSTEM_ENABLED=false` disables chat endpoint
- Returns 503 with maintenance message
- Database remains accessible for inspection

## 16. Future Extensions (Not in Current Scope)

These are explicitly OUT OF SCOPE but may be added later:

1. **Task Due Dates**: Add `due_date` field, reminder notifications
2. **Task Priorities**: High/Medium/Low priority levels
3. **Task Categories**: Tags or folders for organization
4. **Voice Input**: Speech-to-text integration
5. **Multi-User Tasks**: Shared tasks, assignments
6. **Analytics**: Task completion rates, productivity metrics
7. **Integrations**: Calendar sync, email tasks, Slack bot
8. **Mobile App**: Native iOS/Android clients
9. **Offline Support**: Local-first sync

## 17. Open Questions (Requires Clarification)

1. **Conversation Limits**: What's the maximum number of messages per conversation before archiving?
2. **Rate Limiting**: Should we implement per-user rate limits? If yes, what threshold?
3. **Gemini Model Selection**: Which Gemini model (`gemini-1.5-pro`, `gemini-1.5-flash`, or other)? Cost/latency tradeoffs?
4. **Message Retention**: Do we ever delete old messages? If yes, after how long?
5. **Better Auth Setup**: Is Better Auth already configured or do we need setup instructions?

---

## Appendix A: Example Conversations

### Example 1: Simple Task Addition
```
User: "Add a task to buy groceries"
Agent: [Calls add_task(user_id="user_123", title="Buy groceries")]
Agent: "I've added 'Buy groceries' to your task list."
```

### Example 2: List and Complete
```
User: "What do I need to do today?"
Agent: [Calls list_tasks(user_id="user_123", status="pending")]
Agent: "You have 3 pending tasks: 1) Buy groceries, 2) Call dentist, 3) Finish report."

User: "I finished the groceries"
Agent: [Calls complete_task(user_id="user_123", task_id=1)]
Agent: "Great! I've marked 'Buy groceries' as completed."
```

### Example 3: Update with Context
```
User: "Add a task to read a book"
Agent: [Calls add_task(user_id="user_123", title="Read a book")]
Agent: "I've added 'Read a book' to your task list."

User: "Change it to 'Read Dune'"
Agent: [Uses context to identify task_id=5, calls update_task(task_id=5, title="Read Dune")]
Agent: "I've updated the task to 'Read Dune'."
```

### Example 4: Disambiguation
```
User: "Delete the shopping task"
Agent: [Calls list_tasks(status="all")]
Agent: "I found 2 tasks about shopping: 1) Buy groceries, 2) Online shopping. Which one?"

User: "The first one"
Agent: [Calls delete_task(task_id=1)]
Agent: "I've removed 'Buy groceries' from your list."
```

---

## Appendix B: Environment Variables

Required environment variables:

```bash
# Database
DATABASE_URL=postgresql://user:pass@host/dbname

# Google Gemini LLM
GOOGLE_API_KEY=AIza...
GEMINI_MODEL_NAME=gemini-1.5-pro  # Or gemini-1.5-flash, configurable
GEMINI_TEMPERATURE=0.7             # Optional, default 0.7
GEMINI_MAX_TOKENS=2048             # Optional, default 2048

# Better Auth
AUTH_SECRET=...
AUTH_ISSUER=https://auth.example.com

# MCP Server
MCP_SERVER_PORT=3000

# Optional
LOG_LEVEL=INFO
ENVIRONMENT=production
```

**Critical Configuration Notes:**
- `GOOGLE_API_KEY` is REQUIRED for LLM operations
- `GEMINI_MODEL_NAME` allows runtime model selection without code changes
- Temperature and max tokens can be tuned per deployment environment
- NO hardcoded model identifiers in code - always use environment variables

---

## Appendix C: File Structure

Expected project structure after implementation:

```
todo-ai-chatbot/
├── backend/
│   ├── main.py                 # FastAPI app
│   ├── models.py               # SQLModel definitions
│   ├── database.py             # DB connection
│   ├── auth.py                 # Better Auth integration
│   ├── agent.py                # OpenAI Agent setup
│   ├── mcp_server.py           # MCP tool implementations
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── index.html              # ChatKit UI
│   └── app.js
├── migrations/
│   └── alembic/                # Database migrations
├── specs/
│   └── todo-ai-chatbot/
│       ├── spec.md             # This document
│       ├── plan.md             # Generated by /sp.plan
│       └── tasks.md            # Generated by /sp.tasks
└── README.md
```

---

**END OF SPECIFICATION**

This specification is COMPLETE and SUFFICIENT for Claude Code to implement the entire Todo AI Chatbot system through the Agentic Dev Stack workflow (Spec → Plan → Tasks → Implementation).
