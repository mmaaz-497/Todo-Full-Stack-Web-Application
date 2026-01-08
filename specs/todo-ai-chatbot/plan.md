# Implementation Plan: Todo AI Chatbot

## Metadata
```yaml
feature: todo-ai-chatbot
version: 1.0.0
stage: planning
created: 2025-12-27
llm_provider: Google Gemini
orchestration: OpenAI Agents SDK
status: ready-for-tasks
```

## Overview

This plan translates the `/sp.constituent` specification into a deterministic, agent-executable implementation sequence. The system is stateless, with Google Gemini as the primary LLM for natural language understanding and OpenAI Agents SDK as the orchestration framework.

**Core Architectural Principles (from Constitution v1.0.0):**
- **Stateless-First Architecture**: Zero in-memory state, database as single source of truth
- **MCP-First Tool Integration**: All AI task operations via MCP tools exclusively
- **Database Persistence Guarantee**: Every interaction persisted to Neon PostgreSQL
- **Test-First Development (NON-NEGOTIABLE)**: TDD cycle mandatory for all features (Test → Approve → Red → Green → Refactor)
- **Conversational Error Handling**: User-friendly errors, comprehensive logging
- **Natural Language Intent Mapping**: Detect intent, invoke correct MCP tool, support chaining
- **Security and User Isolation**: Strict user_id validation at every layer

**TDD Workflow (CRITICAL):**
Every implementation phase MUST follow this sequence:
1. Write integration tests FIRST (before any implementation code)
2. Get user approval on tests
3. Run tests - VERIFY THEY FAIL (red phase)
4. Implement code to make tests pass (green phase)
5. Refactor while keeping tests green
6. NEVER proceed to next task until tests pass

---

## Phase 1: Foundation Setup

### Objective
Establish project structure, dependencies, and environment configuration framework.

### Inputs
- Specification document (`specs/todo-ai-chatbot/spec.md`)
- Existing project directory structure

### Tasks

#### 1.1 Directory Structure Initialization
**Goal:** Create standard project layout

**Directories to create:**
```
backend/
├── app/
│   ├── __init__.py
│   ├── models.py          # SQLModel definitions
│   ├── database.py        # Database connection & session management
│   ├── auth.py            # Better Auth JWT validation
│   ├── agent.py           # Gemini + OpenAI Agents SDK configuration
│   ├── mcp_server.py      # MCP tool implementations
│   └── main.py            # FastAPI app & endpoints
├── migrations/            # Alembic migrations
├── tests/
│   ├── test_mcp_tools.py
│   ├── test_api.py
│   └── test_stateless.py
├── requirements.txt
├── .env.example
└── README.md

frontend/
├── index.html
├── app.js
└── styles.css
```

**Success Criteria:**
- All directories exist
- `__init__.py` files present in Python packages
- Structure matches Appendix C of specification

#### 1.2 Dependency Management
**Goal:** Define all Python and JavaScript dependencies

**Python Dependencies (requirements.txt):**
```
fastapi==0.100+
uvicorn[standard]
sqlmodel
psycopg2-binary
alembic
python-jose[cryptography]
python-multipart
pydantic-settings
google-generativeai  # Google Gemini SDK
openai-agents-sdk    # Agent orchestration
mcp-python-sdk       # MCP server implementation
python-dotenv
```

**Frontend Dependencies:**
- OpenAI ChatKit (CDN or npm)
- No bundler required (simple HTML/JS)

**Success Criteria:**
- `requirements.txt` lists all backend dependencies with version constraints
- No conflicting dependency versions
- All packages support Python 3.10+

#### 1.3 Environment Configuration
**Goal:** Define environment variable schema and validation

**Variables Required:**
```bash
# Database
DATABASE_URL=postgresql://user:pass@host:port/dbname

# Google Gemini
GOOGLE_API_KEY=AIza...
GEMINI_MODEL_NAME=gemini-1.5-pro
GEMINI_TEMPERATURE=0.7
GEMINI_MAX_TOKENS=2048

# Better Auth
AUTH_SECRET=...
AUTH_ISSUER=https://auth.example.com

# Server
MCP_SERVER_PORT=3000
LOG_LEVEL=INFO
ENVIRONMENT=development
SYSTEM_ENABLED=true
```

**Implementation Strategy:**
- Use `pydantic-settings` for type-safe configuration
- Create `Settings` class with validation
- NO hardcoded secrets or model names
- Fail fast on missing required variables

**Success Criteria:**
- `.env.example` documents all variables
- `Settings` class validates types and presence
- Server refuses to start with missing required vars

### Outputs
- Complete project directory structure
- `requirements.txt` with all dependencies
- `.env.example` template
- `Settings` class in `app/config.py`

### Success Criteria
- Directory structure matches specification Appendix C
- All dependencies documented and version-pinned
- Environment variables validated at startup
- No hardcoded configuration values

---

## Phase 2: Database Layer

### Objective
Implement SQLModel schemas, database connection management, and migration system.

### Inputs
- Database model specifications (Section 5 of spec)
- Neon PostgreSQL connection string
- Stateless guarantees (Section 3)

### TDD Requirement (MUST DO FIRST)
**BEFORE any implementation, create test file: `backend/tests/test_database.py`**

Test cases to write FIRST:
- [ ] Test Task model creation with all fields
- [ ] Test Task model constraints (title not empty, user_id required)
- [ ] Test Conversation model creation
- [ ] Test Message model creation with role validation
- [ ] Test database connection pooling (concurrent sessions)
- [ ] Test foreign key cascade (delete conversation → delete messages)
- [ ] Test indexes exist on user_id fields
- [ ] Test stateless session management (no leaks)

**Verify tests FAIL before implementing models.**

### Tasks

#### 2.1 SQLModel Schema Definitions
**Goal:** Implement Task, Conversation, Message models

**File:** `backend/app/models.py`

**Task Model:**
```python
class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    title: str = Field(nullable=False, max_length=500)
    description: Optional[str] = Field(default=None, max_length=5000)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Indexes:**
- `user_id` (secondary)
- `(user_id, completed)` (composite)

**Conversation Model:**
```python
class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Message Model:**
```python
class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", nullable=False)
    user_id: str = Field(index=True, nullable=False)
    role: str = Field(nullable=False)  # Literal["user", "assistant"]
    content: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

**Constraints:**
- Message `role` must be "user" or "assistant" (validate with Pydantic)
- Foreign key cascade: Delete conversation → delete messages
- Composite index: `(conversation_id, created_at)` for ordered retrieval

**Success Criteria:**
- All models defined with correct types
- Indexes match specification
- Foreign key relationships configured
- No default values in models (stateless)

#### 2.2 Database Connection Management
**Goal:** Implement stateless connection pooling

**File:** `backend/app/database.py`

**Strategy:**
- Use SQLModel `create_engine` with Neon connection string
- Connection pool: `pool_size=5`, `max_overflow=15`
- Each request gets new session from pool
- Sessions never persist between requests
- Use context manager for automatic cleanup

**Connection Lifecycle:**
```python
def get_session():
    """Dependency injection for FastAPI routes"""
    with Session(engine) as session:
        yield session
    # Session auto-closes, connection returns to pool
```

**Success Criteria:**
- Engine created with correct pool settings
- `get_session()` dependency for FastAPI routes
- No session leaks (verified with connection monitoring)
- Concurrent requests use separate sessions

#### 2.3 Database Migrations
**Goal:** Set up Alembic for schema versioning

**Migration Strategy:**
- Initialize Alembic in `backend/migrations/`
- Create initial migration with all three tables
- Indexes and constraints included in migration
- Migration idempotent (can run multiple times)

**Commands:**
```bash
alembic init migrations
alembic revision --autogenerate -m "Initial schema: tasks, conversations, messages"
alembic upgrade head
```

**Success Criteria:**
- Alembic configured for SQLModel
- Initial migration creates all tables and indexes
- `alembic upgrade head` succeeds on empty database
- `alembic downgrade base` cleanly removes tables

### Outputs
- `models.py` with Task, Conversation, Message schemas
- `database.py` with connection management
- Alembic migration files
- Database ready for queries

### Success Criteria
- All models match specification exactly
- Database connection pool configured for concurrency
- Migrations apply cleanly to Neon PostgreSQL
- No stateful session management

---

## Phase 3: MCP Server Implementation

### Objective
Implement 5 MCP tools as stateless, database-backed operations.

### Inputs
- MCP Tool Specifications (Section 6)
- SQLModel schemas from Phase 2
- Database session management

### TDD Requirement (MUST DO FIRST)
**BEFORE any MCP tool implementation, create test file: `backend/tests/test_mcp_tools.py`**

Test cases to write FIRST (as specified in Constitution):
- [ ] **add_task**: Creates task with valid inputs, rejects empty title, validates length limits, returns correct response
- [ ] **list_tasks**: Returns all tasks for user, filters by status (pending/completed), orders by created_at DESC, returns empty list gracefully, enforces user_id isolation
- [ ] **complete_task**: Marks task as completed, idempotent (no error if already completed), returns 404 for non-existent task, enforces user_id ownership
- [ ] **delete_task**: Deletes task from database, returns confirmation, returns 404 for non-existent task, enforces user_id ownership
- [ ] **update_task**: Updates title only, updates description only, updates both, rejects empty title, enforces user_id ownership, returns updated task
- [ ] **User Isolation**: Verify User A cannot access User B's tasks for ALL tools
- [ ] **SQL Injection**: Test parameterized queries prevent injection for ALL tools

**Run tests - VERIFY ALL FAIL (red phase) before implementing any MCP tool.**

### Tasks

#### 3.1 MCP Server Initialization
**Goal:** Set up MCP server with tool registration framework

**File:** `backend/app/mcp_server.py`

**Architecture:**
- Use official MCP Python SDK
- Server runs on configurable port (default 3000)
- Tools registered with JSON schemas
- All tools are stateless functions
- Database session injected per tool call

**Success Criteria:**
- MCP server initializes without errors
- Port configurable via `MCP_SERVER_PORT` env var
- Ready to register tools

#### 3.2 Tool: add_task
**Goal:** Create new task in database

**Input Schema:**
```json
{
  "user_id": "string (required)",
  "title": "string (required, max 500 chars)",
  "description": "string (optional, max 5000 chars)"
}
```

**Implementation Logic:**
1. Validate `title` not empty
2. Validate `title` <= 500 chars, `description` <= 5000 chars
3. Create `Task` object with `completed=False`
4. Set `created_at`, `updated_at` to current UTC time
5. Insert into database (parameterized query)
6. Return `{task_id, status: "pending", title}`

**Error Handling:**
- Empty title → "Task title cannot be empty"
- Database error → "Failed to create task"
- Validation error → Specific field error message

**Success Criteria:**
- Task persists to database with correct fields
- Returns task_id for new task
- Handles empty title validation
- Thread-safe (no race conditions)

#### 3.3 Tool: list_tasks
**Goal:** Retrieve tasks with status filtering

**Input Schema:**
```json
{
  "user_id": "string (required)",
  "status": "enum[all, pending, completed] (default: all)"
}
```

**Implementation Logic:**
1. Query `tasks` table: `WHERE user_id = :user_id`
2. If `status="pending"`: add `AND completed = false`
3. If `status="completed"`: add `AND completed = true`
4. Order by `created_at DESC`
5. Return array of tasks with count

**Output Schema:**
```json
{
  "tasks": [
    {
      "task_id": 123,
      "title": "...",
      "description": "...",
      "status": "pending",
      "created_at": "ISO8601"
    }
  ],
  "count": 1
}
```

**Success Criteria:**
- Filters correctly by status
- Returns tasks ordered by creation date (newest first)
- Only returns tasks for specified user_id
- Empty list handled gracefully

#### 3.4 Tool: complete_task
**Goal:** Mark task as completed

**Input Schema:**
```json
{
  "user_id": "string (required)",
  "task_id": "integer (required)"
}
```

**Implementation Logic:**
1. Query task: `WHERE id = :task_id AND user_id = :user_id`
2. If not found → "Task not found"
3. Update: `completed = true`, `updated_at = now()`
4. Return updated task

**Idempotency:**
- If already completed, return success (no error)
- Same result on repeated calls

**Success Criteria:**
- Updates task in database
- Enforces user_id ownership
- Idempotent operation
- Returns updated task details

#### 3.5 Tool: delete_task
**Goal:** Permanently delete task

**Input Schema:**
```json
{
  "user_id": "string (required)",
  "task_id": "integer (required)"
}
```

**Implementation Logic:**
1. Query task: `WHERE id = :task_id AND user_id = :user_id`
2. If not found → "Task not found"
3. Delete row from database
4. Return `{task_id, status: "deleted", title}`

**Success Criteria:**
- Task removed from database
- Enforces user_id ownership
- Returns confirmation with task details
- Handle non-existent task gracefully

#### 3.6 Tool: update_task
**Goal:** Modify task title or description

**Input Schema:**
```json
{
  "user_id": "string (required)",
  "task_id": "integer (required)",
  "title": "string (optional)",
  "description": "string (optional)"
}
```

**Implementation Logic:**
1. Validate at least one field (title or description) provided
2. Query task: `WHERE id = :task_id AND user_id = :user_id`
3. If not found → "Task not found"
4. Validate title not empty if provided
5. Update specified fields only
6. Set `updated_at = now()`
7. Return updated task

**Success Criteria:**
- Updates only specified fields
- Validates title not empty
- Enforces user_id ownership
- Unspecified fields remain unchanged

### Outputs
- `mcp_server.py` with 5 registered tools
- All tools stateless and database-backed
- JSON schemas for each tool
- Error handling for all edge cases

### Success Criteria
- MCP server starts and registers all 5 tools
- All tools pass unit tests
- Database queries use parameterized statements (no SQL injection)
- User_id enforced on all operations
- Tools have no state between calls

---

## Phase 4: AI Agent Layer (Gemini + OpenAI Agents SDK)

### Objective
Configure Google Gemini LLM with OpenAI Agents SDK orchestration for intent detection and tool execution.

### Inputs
- MCP tool schemas from Phase 3
- Agent behavior rules (Section 7)
- Gemini configuration (Section 2)

### TDD Requirement (MUST DO FIRST)
**BEFORE any agent implementation, create test file: `backend/tests/test_agent.py`**

Test cases to write FIRST (as specified in Constitution):
- [ ] **Intent Detection**: "Add task to buy milk" → calls add_task, "Show my tasks" → calls list_tasks, "Mark X as done" → calls complete_task, "Delete task X" → calls delete_task, "Change task X to Y" → calls update_task
- [ ] **Tool Chaining**: "Mark grocery task as done" → list_tasks then complete_task, asks clarification for multiple matches
- [ ] **Context Awareness**: "Add task to buy milk" then "make it organic" → update_task (uses conversation history)
- [ ] **Error Handling**: Translates "Task not found" to friendly message, handles database errors gracefully, never hallucinates task data
- [ ] **Gemini Configuration**: Model name configurable via environment, temperature and max tokens configurable
- [ ] **Agent Stateless**: Agent created per request (no persistence between requests)

**Run tests - VERIFY ALL FAIL (red phase) before implementing agent.**

### Tasks

#### 4.1 Gemini Client Configuration
**Goal:** Initialize Google Gemini API client

**File:** `backend/app/agent.py`

**Configuration:**
```python
import google.generativeai as genai

genai.configure(api_key=settings.GOOGLE_API_KEY)

model = genai.GenerativeModel(
    model_name=settings.GEMINI_MODEL_NAME,
    generation_config={
        "temperature": settings.GEMINI_TEMPERATURE,
        "max_output_tokens": settings.GEMINI_MAX_TOKENS,
    }
)
```

**Model Selection:**
- Use `GEMINI_MODEL_NAME` from environment (no hardcoding)
- Default: `gemini-1.5-pro`
- Support for `gemini-1.5-flash` (faster, lower cost)

**Success Criteria:**
- Gemini client initializes with API key
- Model name configurable via environment
- Temperature and max tokens configurable
- API connection verified on startup

#### 4.2 System Prompt Design
**Goal:** Create system prompt for intent detection and tool usage

**Prompt Structure:**
```
You are a helpful task management assistant. You help users manage their todo tasks through natural conversation.

CAPABILITIES:
- Add new tasks
- List tasks (all, pending, or completed)
- Mark tasks as completed
- Delete tasks
- Update task details

TOOLS AVAILABLE:
1. add_task(user_id, title, description?)
2. list_tasks(user_id, status?)
3. complete_task(user_id, task_id)
4. delete_task(user_id, task_id)
5. update_task(user_id, task_id, title?, description?)

BEHAVIOR RULES:
- Detect user intent from natural language
- Call the appropriate tool(s) to fulfill requests
- Provide friendly confirmation messages
- Ask clarifying questions when intent is ambiguous
- Chain multiple tools when needed (e.g., list then complete)
- Reference conversation history for context

INTENT MAPPING:
- "Add task to..." → add_task
- "Show my tasks" → list_tasks
- "Mark X as done" → complete_task (may need list_tasks first)
- "Delete task X" → delete_task
- "Change task X to Y" → update_task

RESPONSE STYLE:
- Conversational and friendly
- Confirm actions: "I've added 'Buy milk' to your list"
- Translate errors: "I couldn't find that task" (not "Task not found")
- Ask follow-ups: "Which task did you mean: 1) X, 2) Y?"

CONTEXT AWARENESS:
- Track recently mentioned tasks
- Use conversation history to resolve ambiguous references
- Example: User says "make it organic" after adding "buy milk" → update_task
```

**Success Criteria:**
- System prompt clearly defines capabilities
- Intent mapping examples provided
- Friendly response style enforced
- Context awareness instructions included

#### 4.3 OpenAI Agents SDK Integration
**Goal:** Set up agent orchestration with tool calling

**Architecture:**
- OpenAI Agents SDK manages tool execution flow
- Gemini provides reasoning and tool selection
- SDK handles tool call/result loop
- Agent reconstructed per request (stateless)

**Agent Configuration:**
```python
from openai_agents import Agent

agent = Agent(
    llm=gemini_model,  # Google Gemini as LLM
    tools=mcp_tools,   # 5 MCP tools from Phase 3
    system_prompt=SYSTEM_PROMPT,
    max_iterations=5,  # Limit tool chains
)
```

**Execution Flow:**
1. Agent receives conversation history
2. Gemini analyzes user message
3. Gemini decides which tool(s) to call
4. SDK executes tools via MCP server
5. Gemini generates response using tool results
6. Return response to FastAPI

**Success Criteria:**
- Agent uses Gemini for reasoning (not OpenAI models)
- Tools registered with agent
- Agent supports multi-turn tool chaining
- Agent stateless (created per request)

#### 4.4 Tool Chaining Logic
**Goal:** Enable multi-step operations

**Scenarios:**
1. **Ambiguous Task Reference:**
   - User: "Mark grocery task as done"
   - Agent: Call `list_tasks(status="pending")`
   - Agent: Find tasks matching "grocery"
   - If multiple: Ask clarification
   - If one: Call `complete_task(task_id=X)`

2. **Bulk Operations:**
   - User: "Mark all shopping tasks as done"
   - Agent: Call `list_tasks(status="pending")`
   - Agent: Filter tasks containing "shopping"
   - Agent: Call `complete_task` for each
   - Agent: Summarize results

3. **Context-Aware Updates:**
   - User: "Add task to buy milk"
   - Agent: Call `add_task(...)`
   - User: "Actually make it organic"
   - Agent: Use conversation history to find task_id
   - Agent: Call `update_task(task_id=X, title="Buy organic milk")`

**Implementation:**
- Max 5 tool calls per request (prevent infinite loops)
- Agent tracks tool call history in current request
- Gemini decides when to stop chaining

**Success Criteria:**
- Agent successfully chains list_tasks → complete_task
- Agent asks clarification for ambiguous references
- Agent uses conversation history for context
- Tool chains limited to prevent runaway execution

#### 4.5 Error Translation
**Goal:** Convert technical errors to friendly messages

**Mapping:**
| Technical Error | Friendly Message |
|-----------------|------------------|
| "Task not found" | "I couldn't find that task. Could you describe it differently?" |
| "Unauthorized access to task" | "That task doesn't seem to belong to you." |
| "Failed to create task" | "I couldn't add that task, please try again." |
| "Database failure" | "I'm having trouble accessing your tasks right now. Please try again." |
| "Task title cannot be empty" | "Task titles can't be empty. What would you like to call this task?" |

**Implementation:**
- System prompt includes error translation rules
- Gemini rephrases technical errors naturally
- Never expose stack traces or internal errors to user

**Success Criteria:**
- All technical errors translated to friendly language
- Responses maintain conversational tone
- No database errors leaked to user

### Outputs
- `agent.py` with Gemini client and agent configuration
- System prompt with intent mapping
- Tool chaining logic implemented
- Error translation in responses

### Success Criteria
- Gemini LLM configurable via environment
- Agent uses Gemini for all reasoning
- OpenAI Agents SDK orchestrates tool calls only
- Agent stateless (no persistence between requests)
- Tool chaining works for multi-step operations
- Errors translated to user-friendly messages

---

## Phase 5: FastAPI Chat Endpoint

### Objective
Implement stateless HTTP API for chat interactions with full conversation lifecycle.

### Inputs
- API contract (Section 4)
- Stateless conversation flow (Section 8)
- Agent from Phase 4
- Database models from Phase 2

### TDD Requirement (MUST DO FIRST)
**BEFORE any endpoint implementation, create test file: `backend/tests/test_api.py`**

Test cases to write FIRST (as specified in Constitution):
- [ ] **Authentication**: Rejects requests without token, rejects invalid tokens, rejects expired tokens, accepts valid tokens, enforces user_id matches token
- [ ] **Chat Endpoint**: Creates new conversation when conversation_id omitted, loads existing conversation when conversation_id provided, returns 404 for non-existent conversation_id, enforces user_id matches token
- [ ] **Stateless Flow**: Persists user message to database, persists assistant message to database, returns correct response format, includes tool_calls in response
- [ ] **Conversation Lifecycle**: Multi-turn conversation preserves history, conversation updated_at changes on new message, messages ordered by created_at
- [ ] **Stateless Verification**: Server restart doesn't lose conversation state, concurrent requests don't corrupt data, messages don't leak between users
- [ ] **Error Handling**: Returns appropriate HTTP status for all error types, friendly error messages (no stack traces exposed)

**Run tests - VERIFY ALL FAIL (red phase) before implementing endpoint.**

### Tasks

#### 5.1 FastAPI Application Setup
**Goal:** Initialize FastAPI app with middleware

**File:** `backend/app/main.py`

**Configuration:**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Todo AI Chatbot API",
    version="1.0.0",
    docs_url="/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_methods=["POST"],
    allow_headers=["Authorization", "Content-Type"],
)
```

**Success Criteria:**
- FastAPI app starts on configurable port
- CORS configured for ChatKit frontend
- OpenAPI docs available at `/docs`

#### 5.2 Request/Response Models
**Goal:** Define Pydantic schemas for API contract

**Request Schema:**
```python
class ChatRequest(BaseModel):
    conversation_id: Optional[int] = None
    message: str = Field(min_length=1, max_length=5000)
```

**Response Schema:**
```python
class ToolCall(BaseModel):
    tool: str
    args: dict
    result: dict

class ChatResponse(BaseModel):
    conversation_id: int
    response: str
    tool_calls: List[ToolCall]
```

**Error Response:**
```python
class ErrorResponse(BaseModel):
    error: str
    details: Optional[str] = None
```

**Success Criteria:**
- Schemas match specification exactly
- Validation enforces required fields
- Max length limits enforced
- Type safety with Pydantic

#### 5.3 Authentication Middleware
**Goal:** Validate JWT tokens and extract user_id

**File:** `backend/app/auth.py`

**Implementation:**
```python
from fastapi import Depends, HTTPException, Header
from jose import jwt, JWTError

def verify_token(authorization: str = Header(...)) -> str:
    """Extract and validate JWT, return user_id"""
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "Invalid authorization header")

    token = authorization.replace("Bearer ", "")

    try:
        payload = jwt.decode(
            token,
            settings.AUTH_SECRET,
            issuer=settings.AUTH_ISSUER,
            algorithms=["HS256"]
        )
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(401, "Invalid token: missing user_id")
        return user_id
    except JWTError:
        raise HTTPException(401, "Invalid or expired token")
```

**Success Criteria:**
- JWT validation using Better Auth secret
- User_id extracted from token claims
- 401 error for invalid/missing token
- No token validation bypass

#### 5.4 Chat Endpoint: Stateless Request Lifecycle
**Goal:** Implement POST /api/{user_id}/chat

**Endpoint Definition:**
```python
@app.post("/api/{user_id}/chat", response_model=ChatResponse)
async def chat(
    user_id: str,
    request: ChatRequest,
    authenticated_user_id: str = Depends(verify_token),
    session: Session = Depends(get_session),
):
    # Verify path user_id matches token
    if user_id != authenticated_user_id:
        raise HTTPException(403, "User ID mismatch")

    # Step 1-7 implementation (see below)
```

**Step 1: Receive Request**
- Validate request body (Pydantic automatic)
- Extract user_id from path and token
- Ensure user_id consistency

**Step 2: Load Conversation History**
```python
if request.conversation_id:
    # Load existing conversation
    conversation = session.query(Conversation).filter(
        Conversation.id == request.conversation_id,
        Conversation.user_id == user_id
    ).first()

    if not conversation:
        raise HTTPException(404, "Conversation not found")

    # Load messages ordered by creation time
    messages = session.query(Message).filter(
        Message.conversation_id == request.conversation_id
    ).order_by(Message.created_at.asc()).all()

    history = [{"role": msg.role, "content": msg.content} for msg in messages]
else:
    # Create new conversation
    conversation = Conversation(user_id=user_id)
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    history = []
```

**Step 3: Append User Message**
```python
# In-memory only, not persisted yet
history.append({"role": "user", "content": request.message})
```

**Step 4: Persist User Message**
```python
user_message = Message(
    conversation_id=conversation.id,
    user_id=user_id,
    role="user",
    content=request.message,
)
session.add(user_message)
conversation.updated_at = datetime.utcnow()
session.commit()
```

**Step 5: Invoke AI Agent**
```python
# Pass conversation history to agent
agent_response = await agent.run(
    conversation_history=history,
    user_id=user_id,  # For tool calls
)

# Extract response and tool calls
response_text = agent_response.response
tool_calls = agent_response.tool_calls
```

**Step 6: Persist Assistant Message**
```python
assistant_message = Message(
    conversation_id=conversation.id,
    user_id=user_id,
    role="assistant",
    content=response_text,
)
session.add(assistant_message)
conversation.updated_at = datetime.utcnow()
session.commit()
```

**Step 7: Return Response**
```python
return ChatResponse(
    conversation_id=conversation.id,
    response=response_text,
    tool_calls=[
        ToolCall(
            tool=call.tool_name,
            args=call.arguments,
            result=call.result
        )
        for call in tool_calls
    ]
)
```

**State Cleanup:**
- All local variables cleared after return
- No conversation objects persist
- Database session returned to pool
- Agent instance discarded

**Success Criteria:**
- Endpoint matches specification API contract
- All 7 steps execute in correct order
- Conversation history loaded from database per request
- User and assistant messages persisted
- Agent receives full conversation context
- Response includes tool call details
- No state retention between requests

#### 5.5 Error Handling
**Goal:** Return appropriate HTTP errors with friendly messages

**Error Scenarios:**

**400 Bad Request:**
```python
@app.exception_handler(ValidationError)
async def validation_error_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"error": "Invalid request", "details": str(exc)}
    )
```

**401 Unauthorized:**
- Handled by authentication middleware
- Return: `{"error": "Invalid or missing authentication"}`

**404 Not Found:**
```python
if not conversation:
    raise HTTPException(404, detail="Conversation not found")
```

**500 Internal Server Error:**
```python
@app.exception_handler(Exception)
async def generic_error_handler(request, exc):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )
```

**503 Service Unavailable:**
```python
# Database connection failure
try:
    session.execute("SELECT 1")
except Exception:
    raise HTTPException(503, detail="Service temporarily unavailable")
```

**Logging:**
- All errors logged with correlation ID
- User_id and conversation_id included
- Stack traces for 5xx errors
- Request payload sanitized (no secrets)

**Success Criteria:**
- All error types return correct HTTP status
- Friendly error messages (no stack traces exposed)
- Errors logged with sufficient context
- No secrets in error responses

#### 5.6 Health Check Endpoint
**Goal:** Monitor service availability

**Endpoint:**
```python
@app.get("/health")
async def health_check(session: Session = Depends(get_session)):
    try:
        # Check database connectivity
        session.execute("SELECT 1")

        # Check Gemini API (optional)
        # genai.list_models()  # Quick API check

        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )
```

**Success Criteria:**
- Returns 200 when all services healthy
- Returns 503 when database unreachable
- Can be used for load balancer health checks

### Outputs
- `main.py` with FastAPI app and chat endpoint
- Request/response Pydantic models
- Authentication middleware
- Error handlers for all scenarios
- Health check endpoint

### Success Criteria
- Endpoint implements complete 7-step flow
- Stateless: no data persists between requests
- Authentication validates JWT tokens
- Conversation history loaded from database per request
- All errors handled with appropriate HTTP status
- Health check available for monitoring
- Concurrent requests safe (no race conditions)

---

## Phase 6: Frontend Integration (ChatKit)

### Objective
Build minimal ChatKit UI for user interaction with backend.

### Inputs
- API endpoint from Phase 5
- ChatKit documentation
- Frontend file structure from Phase 1

### Tasks

#### 6.1 ChatKit Configuration
**Goal:** Set up OpenAI ChatKit UI library

**File:** `frontend/index.html`

**HTML Structure:**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Todo AI Chatbot</title>
    <script src="https://cdn.jsdelivr.net/npm/@openai/chatkit@latest"></script>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div id="chat-container"></div>
    <script src="app.js"></script>
</body>
</html>
```

**Success Criteria:**
- ChatKit library loaded from CDN
- Container element for chat UI
- Styles loaded

#### 6.2 API Client Implementation
**Goal:** Connect ChatKit to FastAPI backend

**File:** `frontend/app.js`

**Configuration:**
```javascript
const BACKEND_URL = 'http://localhost:8000';
let conversationId = null;
let authToken = null;  // Set from Better Auth

async function sendMessage(message) {
    const response = await fetch(`${BACKEND_URL}/api/${userId}/chat`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${authToken}`
        },
        body: JSON.stringify({
            conversation_id: conversationId,
            message: message
        })
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error);
    }

    const data = await response.json();
    conversationId = data.conversation_id;  // Save for next request
    return data.response;
}
```

**ChatKit Integration:**
```javascript
const chat = ChatKit.create({
    container: document.getElementById('chat-container'),
    onSend: async (message) => {
        try {
            const response = await sendMessage(message);
            chat.addMessage({ role: 'assistant', content: response });
        } catch (error) {
            chat.addMessage({
                role: 'system',
                content: `Error: ${error.message}`
            });
        }
    }
});
```

**Success Criteria:**
- ChatKit sends messages to FastAPI endpoint
- Conversation ID preserved across messages
- Responses displayed in chat UI
- Errors shown to user

#### 6.3 Authentication Integration
**Goal:** Integrate Better Auth JWT token

**Strategy:**
- Assume Better Auth provides JWT on login
- Store token in localStorage or sessionStorage
- Include token in Authorization header
- Handle 401 errors (token expired)

**Implementation:**
```javascript
// On page load
authToken = localStorage.getItem('auth_token');
userId = localStorage.getItem('user_id');

if (!authToken || !userId) {
    // Redirect to Better Auth login
    window.location.href = '/auth/login';
}

// Handle 401 errors
if (response.status === 401) {
    localStorage.removeItem('auth_token');
    window.location.href = '/auth/login';
}
```

**Success Criteria:**
- JWT token retrieved from Better Auth
- Token sent in all API requests
- 401 errors redirect to login
- User_id available for API calls

#### 6.4 Basic Styling
**Goal:** Minimal CSS for usable interface

**File:** `frontend/styles.css`

**Requirements:**
- Chat container full height
- Messages clearly distinguished (user vs assistant)
- Input box at bottom
- Scrollable message history
- Mobile-responsive

**Success Criteria:**
- UI is functional and readable
- No styling bugs
- Works on desktop and mobile browsers

### Outputs
- `index.html` with ChatKit integration
- `app.js` with API client
- `styles.css` for basic styling
- Authentication flow integrated

### Success Criteria
- Frontend sends messages to backend
- Responses displayed correctly
- Conversation persists across messages
- JWT authentication working
- UI is usable on desktop and mobile

---

## Phase 7: Final Validation & Acceptance

### Objective
Verify all tests pass (green phase achieved), validate non-functional requirements, and confirm constitution compliance.

### Inputs
- All tests from Phases 2-6 (must be GREEN)
- Acceptance criteria (Section 14 of spec)
- Constitution compliance checklist

### TDD Status Check (CRITICAL)
**Before this phase, verify:**
- [ ] All Phase 2 database tests passing (green)
- [ ] All Phase 3 MCP tool tests passing (green)
- [ ] All Phase 4 agent tests passing (green)
- [ ] All Phase 5 API tests passing (green)
- [ ] All Phase 6 frontend integration tests passing (green)

**If ANY tests are failing, STOP and fix before proceeding.**

### Tasks

#### 7.1 Test Coverage Validation
**Goal:** Ensure comprehensive test coverage

**Success Criteria:**
- Overall test coverage > 85%
- MCP tools coverage > 90%
- Critical paths (auth, stateless flow) 100% covered
- All edge cases from constitution tested

#### 7.2 Constitution Compliance Audit
**Goal:** Verify implementation adheres to all 7 constitution principles

**Checklist:**
- [ ] **Stateless-First Architecture**: Server maintains zero in-memory state verified
- [ ] **MCP-First Tool Integration**: All task operations route through MCP tools only
- [ ] **Database Persistence Guarantee**: Every interaction persisted to Neon PostgreSQL
- [ ] **Test-First Development**: TDD cycle followed for all features (verified by git history)
- [ ] **Conversational Error Handling**: All errors user-friendly, comprehensive logging present
- [ ] **Natural Language Intent Mapping**: Intent detection works for all tool mappings
- [ ] **Security and User Isolation**: user_id validated at every layer, no cross-user access

#### 7.3 Non-Functional Requirements Validation
**Goal:** Verify performance, reliability, and observability

**Performance Tests:**
- [ ] p95 response time < 3 seconds (load test with 100 concurrent requests)
- [ ] Database connection pool handles concurrent load (min=5, max=20)
- [ ] No memory leaks under sustained load (monitor for 1 hour)

**Reliability Tests:**
- [ ] Server restart preserves conversation state (stateless verification)
- [ ] Database transaction rollback on errors (ACID compliance)
- [ ] Idempotent operations work correctly (complete_task repeated calls)

**Observability:**
- [ ] Structured JSON logs with correlation IDs
- [ ] All errors logged with required context (user_id, conversation_id, stack trace)
- [ ] No secrets in logs or error messages

#### 7.4 Security Audit
**Goal:** Final security validation

**Verification:**
- [ ] User isolation: User A cannot access User B's data (all tools + API)
- [ ] SQL injection: Parameterized queries prevent injection (security scan)
- [ ] Secrets management: No secrets in code, logs, or errors
- [ ] Authentication: JWT validation enforced on all requests

### Outputs
- Test coverage report (>85%)
- Constitution compliance sign-off
- Performance benchmark results
- Security audit report

### Success Criteria
- All tests GREEN (TDD green phase achieved)
- Constitution compliance: 7/7 principles verified
- Performance: p95 < 3s, no memory leaks
- Security: All audit checks pass
- Test coverage > 85%

---

## Phase 8: Deployment Preparation

### Objective
Prepare system for production deployment with proper configuration and documentation.

### Inputs
- All implemented components
- Environment configuration from Phase 1
- Deployment assumptions (Section 12 of spec)

### Tasks

#### 8.1 Environment Configuration
**Goal:** Finalize production environment variables

**Production `.env` Template:**
```bash
# Database
DATABASE_URL=postgresql://user:pass@neon-host:5432/dbname?sslmode=require

# Google Gemini
GOOGLE_API_KEY=AIza... (production key)
GEMINI_MODEL_NAME=gemini-1.5-pro
GEMINI_TEMPERATURE=0.7
GEMINI_MAX_TOKENS=2048

# Better Auth
AUTH_SECRET=... (production secret)
AUTH_ISSUER=https://auth.yourdomain.com

# Server
MCP_SERVER_PORT=3000
LOG_LEVEL=INFO
ENVIRONMENT=production
SYSTEM_ENABLED=true

# CORS (production)
ALLOWED_ORIGINS=https://yourdomain.com
```

**Validation:**
- All required variables present
- No placeholder values
- Secrets securely managed (not in git)

**Success Criteria:**
- Production `.env` template documented
- Environment variable validation at startup
- Secrets not committed to repository

#### 8.2 Database Migration Strategy
**Goal:** Plan production database setup

**Steps:**
1. Provision Neon PostgreSQL database
2. Get connection string with SSL required
3. Run migrations: `alembic upgrade head`
4. Verify tables and indexes created
5. Test connection pooling under load

**Rollback Strategy:**
- `alembic downgrade -1` for single migration rollback
- Database backups before migrations
- Test migrations on staging first

**Success Criteria:**
- Migrations run cleanly on Neon
- Rollback strategy documented
- Connection pooling tested

#### 8.3 Logging & Monitoring
**Goal:** Set up structured logging for production

**Implementation:**
```python
import logging
import json

logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(message)s'
)

def log_event(event_type, **kwargs):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "event": event_type,
        **kwargs
    }
    logging.info(json.dumps(log_entry))
```

**Events to Log:**
- Request received (correlation_id, user_id, endpoint)
- Tool called (tool_name, user_id, args)
- Error occurred (error_type, user_id, stack_trace)
- Response sent (conversation_id, response_time)

**Success Criteria:**
- Structured JSON logs
- Correlation IDs for tracing
- No secrets in logs
- Logs parseable by monitoring tools

#### 8.4 README Documentation
**Goal:** Provide setup and usage instructions

**README Sections:**
1. **Overview:** System architecture and components
2. **Prerequisites:** Neon DB, Gemini API key, Better Auth
3. **Installation:**
   ```bash
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your credentials
   alembic upgrade head
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```
4. **Environment Variables:** Complete reference
5. **API Documentation:** Link to `/docs` endpoint
6. **MCP Tools:** List of 5 tools with descriptions
7. **Testing:** How to run test suite
8. **Deployment:** Production setup guide
9. **Troubleshooting:** Common issues and solutions

**Success Criteria:**
- README clear and complete
- Setup instructions accurate
- API documentation linked
- Troubleshooting section included

#### 8.5 Frontend Deployment
**Goal:** Prepare frontend for production hosting

**Steps:**
1. Update `BACKEND_URL` to production API
2. Configure CORS on backend for frontend domain
3. Host static files (index.html, app.js, styles.css)
4. Verify ChatKit CDN loading
5. Test with production API

**Production Checklist:**
- [ ] Backend URL configured
- [ ] CORS allows frontend domain
- [ ] HTTPS enabled
- [ ] Better Auth connected
- [ ] Error handling tested

**Success Criteria:**
- Frontend hosted and accessible
- API calls succeed from frontend
- Authentication flow works
- HTTPS configured

### Outputs
- Production environment configuration
- Database migration plan
- Structured logging implemented
- README documentation
- Frontend deployment guide

### Success Criteria
- Production environment ready
- Database migrations tested
- Logging captures all events
- Documentation complete
- Frontend deployable

---

## Phase 9: Acceptance & Handoff

### Objective
Verify all specification requirements met and system ready for use.

### Tasks

#### 9.1 Functional Acceptance Checklist
**From Specification Section 14:**

- [ ] User can create tasks via natural language
- [ ] User can list tasks (all/pending/completed)
- [ ] User can complete tasks
- [ ] User can delete tasks
- [ ] User can update tasks
- [ ] Conversation history persists across requests
- [ ] Multiple conversations per user work
- [ ] Agent detects intent correctly for all operations
- [ ] Agent chains tools when needed
- [ ] Agent provides friendly error messages

**Verification:**
- Manual testing of each feature
- Example conversations from Appendix A tested
- Edge cases validated

#### 9.2 Technical Acceptance Checklist
**From Specification Section 14:**

- [ ] FastAPI server starts without errors
- [ ] MCP server registers 5 tools correctly
- [ ] Database migrations apply cleanly
- [ ] All queries filter by user_id
- [ ] JWT validation rejects invalid tokens
- [ ] Server maintains zero stateful data
- [ ] Concurrent requests don't corrupt data
- [ ] All errors logged with required fields
- [ ] p95 response time < 3 seconds

**Verification:**
- Server startup test
- Load testing with concurrent requests
- Performance benchmarking

#### 9.3 Security Acceptance Checklist
**From Specification Section 14:**

- [ ] Users cannot access other users' tasks
- [ ] Users cannot access other users' conversations
- [ ] SQL injection attempts blocked
- [ ] Secrets not exposed in logs/errors
- [ ] All queries use parameterized statements

**Verification:**
- Security audit performed
- Penetration testing (basic)
- Code review for security issues

#### 9.4 Documentation Checklist

- [ ] README with setup instructions
- [ ] Environment variable documentation
- [ ] API endpoint documentation (`/docs`)
- [ ] MCP tool schemas documented
- [ ] Database schema documented

**Verification:**
- Documentation reviewed for completeness
- Setup instructions tested by new user

#### 9.5 Known Limitations

**Documented:**
1. Conversation history not paginated (may hit context limits)
2. No rate limiting implemented (assumes infrastructure handles this)
3. Single language support (English only)
4. No task due dates or priorities
5. Better Auth setup assumed (not included)

**Open Questions (from Spec Section 17):**
1. Conversation message limit? (Recommend 50 messages)
2. Rate limiting per user? (Recommend 100 req/hour)
3. Gemini model selection? (Recommend gemini-1.5-pro for production)
4. Message retention? (Recommend keep indefinitely, add archiving later)
5. Better Auth setup? (Assume already configured)

### Outputs
- Complete acceptance checklist
- Known limitations documented
- Open questions answered or delegated
- System ready for deployment

### Success Criteria
- All functional acceptance criteria met
- All technical acceptance criteria met
- All security acceptance criteria met
- Documentation complete and accurate
- Known limitations acknowledged

---

## Architectural Decisions Summary

### Decision 1: Gemini as Primary LLM
**Rationale:**
- Google Gemini provides strong reasoning capabilities
- Configurable via environment variables
- Cost-effective with gemini-1.5-flash option
- Easy to swap for other LLMs (provider independence)

**Alternatives Considered:**
- OpenAI GPT-4: More expensive, similar capabilities
- Anthropic Claude: Excellent reasoning but more complex integration
- Local models: Not production-ready for this use case

**Trade-offs:**
- Dependency on Google API availability
- Requires Gemini API key and quota
- Network latency for API calls

### Decision 2: OpenAI Agents SDK for Orchestration
**Rationale:**
- Well-tested tool calling framework
- Handles tool execution loop
- LLM-agnostic (works with Gemini)
- Simplifies multi-step tool chaining

**Alternatives Considered:**
- LangChain: More complex, unnecessary overhead
- Custom orchestration: Reinventing the wheel
- Direct Gemini API: No built-in tool orchestration

**Trade-offs:**
- Additional dependency
- Learning curve for SDK
- May be overkill for simple use cases

### Decision 3: SQLModel for ORM
**Rationale:**
- Combines Pydantic and SQLAlchemy
- Type-safe models
- Easy migrations with Alembic
- FastAPI native integration

**Alternatives Considered:**
- Raw SQLAlchemy: More verbose, less type safety
- Django ORM: Too heavyweight for FastAPI
- Prisma: Not mature in Python ecosystem

**Trade-offs:**
- Newer library (less battle-tested)
- Learning curve for developers
- Migration tooling less mature than Django

### Decision 4: Stateless Architecture
**Rationale:**
- Enables horizontal scaling
- No session management complexity
- Database as single source of truth
- Safer for concurrent requests

**Alternatives Considered:**
- In-memory sessions: Doesn't scale, state loss on restart
- Redis caching: Adds complexity, not needed initially
- Sticky sessions: Limits scalability

**Trade-offs:**
- Higher database load (conversation history per request)
- Slower responses (database queries on every request)
- Potential for large conversation history queries

### Decision 5: Better Auth for Authentication
**Rationale:**
- Specification requirement
- Modern JWT-based auth
- Easy integration with FastAPI

**Alternatives Considered:**
- Auth0: More expensive
- Firebase Auth: Vendor lock-in
- Custom auth: Reinventing the wheel

**Trade-offs:**
- External dependency
- Requires Better Auth setup
- JWT validation overhead

---

## Risk Mitigation Summary

### Risk 1: Gemini Intent Detection Failures
**Mitigation:**
- Extensive system prompt with examples
- Fallback clarification questions
- Logging for prompt tuning
- Human review of misdetections

### Risk 2: Database Connection Failures
**Mitigation:**
- Connection pooling with retry logic
- Exponential backoff on transient errors
- Health check endpoint
- Neon's built-in reliability

### Risk 3: Large Conversation Histories
**Mitigation:**
- Message limit per conversation (50 messages recommended)
- Summarization for old messages (future enhancement)
- Pagination if needed (future enhancement)
- Monitor context window usage

### Risk 4: Gemini API Rate Limits
**Mitigation:**
- Monitor API quota usage
- Implement retry with backoff
- Consider gemini-1.5-flash for higher throughput
- Add rate limiting at application layer (future enhancement)

---

## Implementation Order

**Strict Dependency Sequence:**
1. Phase 1 → Phase 2 (need structure before database)
2. Phase 2 → Phase 3 (need database before MCP tools)
3. Phase 3 → Phase 4 (need tools before agent)
4. Phase 4 → Phase 5 (need agent before API)
5. Phase 5 → Phase 6 (need API before frontend)
6. Phases 1-6 → Phase 7 (need all components before testing)
7. Phase 7 → Phase 8 (need working system before deployment prep)
8. Phase 8 → Phase 9 (need deployment ready before acceptance)

**Critical Path:**
- Database schema → MCP tools → Agent → API endpoint → Frontend
- Any delay in early phases blocks all downstream phases

---

## Success Metrics

**Technical:**
- All 5 MCP tools functional
- API endpoint returns < 3 seconds (p95)
- Zero stateful data between requests
- 100% user data isolation
- Test coverage > 85%

**Functional:**
- Users can perform all 5 task operations via natural language
- Conversation history persists correctly
- Agent chains tools when needed
- Errors translated to friendly messages

**Security:**
- JWT validation prevents unauthorized access
- SQL injection attempts blocked
- No secrets in logs or errors

---

---

## Constitution Compliance Summary

This plan strictly adheres to **Constitution v1.0.0** principles:

✅ **Stateless-First Architecture**: Enforced through database-first persistence, no in-memory state, stateless verification tests
✅ **MCP-First Tool Integration**: All task operations exclusively through MCP tools, agent never directly accesses database
✅ **Database Persistence Guarantee**: Every interaction persisted before response, transactional integrity enforced
✅ **Test-First Development (NON-NEGOTIABLE)**: TDD requirements added to Phases 2-6, tests written BEFORE implementation, red-green-refactor cycle mandatory
✅ **Conversational Error Handling**: Error translation patterns defined, friendly messages required, comprehensive logging specified
✅ **Natural Language Intent Mapping**: Intent detection mapped to tools, chaining logic defined, disambiguation required
✅ **Security and User Isolation**: user_id validation at every layer, parameterized queries, JWT enforcement, cross-user access tests

**TDD Workflow Enforcement:**
- Phase 2: Database tests BEFORE model implementation
- Phase 3: MCP tool tests BEFORE tool implementation
- Phase 4: Agent tests BEFORE agent configuration
- Phase 5: API tests BEFORE endpoint implementation
- Phase 6: Frontend tests integrated with implementation
- Phase 7: Final validation (all tests must be GREEN)

**Critical Mandate:** NO implementation code may be written until corresponding tests are written, approved, and verified to FAIL (red phase).

---

**END OF PLAN**

This plan is COMPLETE, DETERMINISTIC, and CONSTITUTION-COMPLIANT. Claude Code can execute this plan sequentially to implement the entire Todo AI Chatbot system following strict TDD discipline.
