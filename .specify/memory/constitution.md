# Todo AI Chatbot Constitution

<!--
SYNC IMPACT REPORT - Version 1.0.0 (Initial Constitution)
==========================================================
Version Change: None → 1.0.0
Change Type: INITIAL - First constitution for new project
Modified Principles: N/A (new project)
Added Sections:
  - Core Principles (7 principles)
  - Technology Stack Requirements
  - Development Workflow
  - Governance
Templates Status:
  - ✅ plan-template.md (aligned with stateless architecture principle)
  - ✅ spec-template.md (aligned with MCP-first and DB persistence principles)
  - ✅ tasks-template.md (aligned with TDD and integration testing principles)
Follow-up TODOs: None
Rationale: Initial constitution establishing foundational principles for stateless AI chatbot with MCP-based task management
-->

## Core Principles

### I. Stateless-First Architecture

**MUST enforce zero in-memory state across all backend services.**

- Every HTTP request MUST load required state from the database
- Conversation history MUST be persisted and retrieved from database per request
- No session state, cache, or in-memory storage for user data
- All services MUST be horizontally scalable without shared state
- Database is the single source of truth for all application state

**Rationale**: Ensures predictable behavior, eliminates race conditions, enables seamless horizontal scaling, and guarantees data consistency across distributed deployments.

### II. MCP-First Tool Integration

**All AI task operations MUST be executed exclusively through MCP tools.**

- OpenAI Agent MUST NOT directly access database or business logic
- Every task operation (add, list, complete, delete, update) MUST use defined MCP tool
- MCP tools are the only interface between AI agent and data layer
- No hardcoded task logic in agent prompts or FastAPI handlers
- MCP tools MUST be stateless and persist all changes to database immediately

**Rationale**: Enforces separation of concerns, enables independent testing of AI and data layers, allows MCP tool reuse across different AI frameworks, and provides clear audit trail of AI actions.

### III. Database Persistence Guarantee

**Every user interaction and AI action MUST be persisted to Neon PostgreSQL.**

- Messages (user and assistant) MUST be stored before response is returned
- Task operations MUST commit to database before returning success
- Conversation metadata (created_at, updated_at) MUST be maintained accurately
- Failed operations MUST NOT leave partial state in database (transactional integrity)
- All timestamps MUST use UTC and be stored consistently

**Rationale**: Guarantees data durability, enables conversation replay and debugging, supports compliance and audit requirements, and ensures no data loss on server restart.

### IV. Test-First Development (NON-NEGOTIABLE)

**TDD cycle is mandatory for all features: Test → Approve → Red → Green → Refactor.**

- Integration tests MUST be written and user-approved BEFORE implementation
- Tests MUST fail initially (red phase validation)
- Implementation proceeds only after red phase confirmed
- All tests MUST pass before PR approval (green phase)
- Refactoring MUST maintain passing tests

**Focus areas requiring tests**:
- MCP tool contracts (inputs, outputs, error cases)
- FastAPI endpoint behavior (request validation, response format, error handling)
- Agent intent detection and tool selection
- Database model constraints and relationships
- Stateless conversation flow (load history, append, persist, return)

**Rationale**: Prevents regression, documents expected behavior, enables confident refactoring, and ensures all edge cases are covered before deployment.

### V. Conversational Error Handling

**All error responses MUST be user-friendly and non-technical.**

- Database errors → "I'm having trouble saving that right now. Please try again."
- Task not found → "I couldn't find that task. Would you like to see your current tasks?"
- Invalid input → "I didn't quite understand. Could you rephrase that?"
- Unauthorized access → "I can only show tasks for your account."
- Empty task list → "You don't have any tasks yet. Would you like to add one?"

**Required error context (logged, not shown to user)**:
- Request ID for tracing
- User ID and conversation ID
- MCP tool invoked and parameters
- Database query executed
- Stack trace for 500-level errors

**Rationale**: Maintains conversational UX, prevents information leakage, reduces user frustration, while preserving debugging capability through comprehensive logging.

### VI. Natural Language Intent Mapping

**Agent MUST detect user intent and invoke correct MCP tool without explicit commands.**

**Intent → Tool mapping**:
- "Add", "Create", "Remember", "Note" → `add_task`
- "Show", "List", "What are", "Display" → `list_tasks`
- "Done", "Complete", "Finish", "Mark" → `complete_task`
- "Delete", "Remove", "Cancel", "Drop" → `delete_task`
- "Change", "Update", "Edit", "Modify" → `update_task`

**Tool chaining requirements**:
- "Mark my first task as done" MUST chain `list_tasks` → `complete_task`
- "Delete all completed tasks" MUST chain `list_tasks(status=completed)` → multiple `delete_task`
- Agent MUST confirm destructive actions ("About to delete 3 tasks. Confirm?")

**Rationale**: Enables true conversational UX, reduces user cognitive load, supports flexible phrasing, and prevents accidental destructive operations.

### VII. Security and User Isolation

**User data MUST be strictly isolated and validated at every layer.**

- All MCP tools MUST require `user_id` parameter (no defaults)
- Database queries MUST include `user_id` filter (prevent cross-user data leakage)
- FastAPI endpoints MUST validate `user_id` from Better Auth session
- Better Auth MUST enforce session validation before any operation
- Task IDs alone MUST NOT grant access (require user_id match)

**Input validation requirements**:
- Task title: 1-200 characters, no SQL injection patterns
- Task description: 0-2000 characters, sanitized for XSS
- Conversation ID: positive integer, existence validated
- Message content: 1-5000 characters, rate-limited per user

**Rationale**: Prevents unauthorized access, ensures GDPR/privacy compliance, mitigates injection attacks, and protects against enumeration attacks.

## Technology Stack Requirements

**MUST use the following technologies (non-negotiable)**:

- **Frontend**: OpenAI ChatKit (React-based conversational UI)
- **Backend**: Python 3.11+ with FastAPI 0.100+
- **AI Framework**: OpenAI Agents SDK (tool calling, streaming support)
- **MCP Server**: Official MCP Python SDK (stdio transport)
- **ORM**: SQLModel 0.0.14+ (SQLAlchemy 2.0 + Pydantic integration)
- **Database**: Neon Serverless PostgreSQL (connection pooling required)
- **Authentication**: Better Auth (session-based, secure cookie handling)

**Dependencies MUST be pinned** in `requirements.txt` with exact versions for reproducibility.

**Configuration MUST use environment variables** (`.env` for local, secrets manager for production):
- `DATABASE_URL` (Neon connection string)
- `OPENAI_API_KEY` (OpenAI Agents SDK)
- `BETTER_AUTH_SECRET` (session signing key)
- `MCP_SERVER_PATH` (path to MCP server executable)

## Development Workflow

**Agentic Dev Stack (mandatory)**:

1. **Specification** (`/sp.specify`): Define feature requirements, user stories, acceptance criteria
2. **Planning** (`/sp.plan`): Architecture decisions, MCP tool contracts, API design, database schema
3. **Task Breakdown** (`/sp.tasks`): Testable tasks with TDD cases, ordered by dependency
4. **Implementation**: Claude Code executes tasks (NO manual coding)

**Quality gates** (all MUST pass before merge):

- ✅ All integration tests passing (pytest)
- ✅ Type checking passing (mypy strict mode)
- ✅ Linting passing (ruff)
- ✅ No database migrations without rollback script
- ✅ MCP tools validated with `mcp test` command
- ✅ FastAPI OpenAPI schema generated and reviewed

**Code review checklist**:

- [ ] Stateless architecture verified (no in-memory state)
- [ ] MCP tools used for all task operations (no direct DB access in agent)
- [ ] Database persistence confirmed (all messages/tasks stored)
- [ ] Error messages are conversational (no stack traces to user)
- [ ] User isolation enforced (user_id validated at every layer)
- [ ] Tests written first and approved (TDD cycle followed)

## Governance

**This constitution supersedes all other development practices and preferences.**

**Amendment process**:
1. Propose change with justification and impact analysis
2. Document as ADR if architecturally significant
3. Update constitution with version bump (semantic versioning)
4. Propagate changes to dependent templates (`spec`, `plan`, `tasks`)
5. Commit with message: `docs: amend constitution to vX.Y.Z (summary)`

**Version policy**:
- **MAJOR**: Breaking principle removal or redefinition (e.g., removing stateless requirement)
- **MINOR**: New principle added or materially expanded guidance (e.g., adding observability principle)
- **PATCH**: Clarifications, wording improvements, typo fixes (no semantic change)

**Compliance verification**:
- All PRs MUST include constitution compliance checklist
- Architectural decisions MUST reference relevant principles
- Violations MUST be justified in ADR or rejected
- Spec/Plan/Tasks MUST cite applicable constitution sections

**Runtime guidance**: See `CLAUDE.md` for agent-specific development instructions aligned with this constitution.

**Version**: 1.0.0 | **Ratified**: 2025-12-27 | **Last Amended**: 2025-12-27
