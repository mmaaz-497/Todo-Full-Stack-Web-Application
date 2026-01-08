---
id: 005
title: Initial Todo AI Chatbot Constitution
stage: constitution
date: 2025-12-27
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: 001-auth-session-fix
user: Claude Code
command: /sp.constitution
labels: ["constitution", "mcp", "stateless-architecture", "ai-chatbot", "openai-agents-sdk"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - N/A (constitution document, no tests required)
---

## Prompt

You are a Senior AI Systems Architect and Spec-Kit Plus authority.

Your task is to generate a COMPLETE, PRODUCTION-GRADE `/sp.constituent` specification using the Agentic Dev Stack workflow.

STRICT RULES:
- Follow Spec-Kit Plus format exactly
- Do NOT write implementation code
- Do NOT skip any section
- The spec must be sufficient for Claude Code to implement the system end-to-end with ZERO human coding
- Output ONLY the /sp.constituent content

────────────────────────────────────────
PROJECT: Todo AI Chatbot using MCP + OpenAI Agents SDK
────────────────────────────────────────

OBJECTIVE:
Build a stateless AI-powered chatbot that manages Todo tasks through natural language. All state must persist in the database. The AI must use MCP tools for every task operation.

DEVELOPMENT METHOD (MANDATORY):
Agentic Dev Stack:
1) Spec
2) Plan
3) Tasks
4) Claude Code implementation
No manual coding allowed.

────────────────────────────────────────
TECHNOLOGY STACK
────────────────────────────────────────
Frontend: OpenAI ChatKit
Backend: Python FastAPI
AI Framework: OpenAI Agents SDK
MCP Server: Official MCP SDK
ORM: SQLModel
Database: Neon Serverless PostgreSQL
Authentication: Better Auth

────────────────────────────────────────
ARCHITECTURE
────────────────────────────────────────
ChatKit UI → FastAPI Chat Endpoint → OpenAI Agent → MCP Server → Neon PostgreSQL

Server is 100% stateless. Conversation history is loaded from DB per request.

────────────────────────────────────────
API CONTRACT
────────────────────────────────────────
POST /api/{user_id}/chat

Request:
- conversation_id (optional, integer)
- message (required, string)

Response:
- conversation_id (integer)
- response (string)
- tool_calls (array)

────────────────────────────────────────
DATABASE MODELS (SQLModel)
────────────────────────────────────────
Task:
- id
- user_id
- title
- description
- completed
- created_at
- updated_at

Conversation:
- id
- user_id
- created_at
- updated_at

Message:
- id
- conversation_id
- user_id
- role (user | assistant)
- content
- created_at

────────────────────────────────────────
MCP TOOLS (REQUIRED)
────────────────────────────────────────

add_task
- user_id (string, required)
- title (string, required)
- description (string, optional)
Returns: task_id, status, title

list_tasks
- user_id (string, required)
- status ("all" | "pending" | "completed", optional)
Returns: array of tasks

complete_task
- user_id (string, required)
- task_id (integer, required)
Returns: task_id, status, title

delete_task
- user_id (string, required)
- task_id (integer, required)
Returns: task_id, status, title

update_task
- user_id (string, required)
- task_id (integer, required)
- title (optional)
- description (optional)
Returns: task_id, status, title

All MCP tools must be stateless and persist data via the database.

────────────────────────────────────────
AGENT BEHAVIOR RULES
────────────────────────────────────────
- Detect user intent from natural language
- Invoke correct MCP tool
- Chain tools when required
- Always confirm actions conversationally
- Gracefully handle errors

Intent Mapping:
- Add / Remember → add_task
- Show / List → list_tasks
- Done / Complete → complete_task
- Delete / Remove → delete_task
- Change / Update → update_task

────────────────────────────────────────
STATELESS CONVERSATION FLOW
────────────────────────────────────────
1. Receive user message
2. Load conversation history from DB
3. Append new message
4. Store user message
5. Run OpenAI Agent
6. Agent calls MCP tools
7. Store assistant response
8. Return response

No in-memory state allowed.

────────────────────────────────────────
ERROR HANDLING
────────────────────────────────────────
- Task not found
- Invalid task ID
- Empty task list
- Unauthorized access

Responses must be friendly and non-technical.

────────────────────────────────────────
DELIVERABLES
────────────────────────────────────────
The /sp.constituent must define:
- System overview
- Architecture description
- API contracts
- MCP tool specs
- Agent behavior constraints
- Stateless guarantees
- Error strategy
- Security assumptions
- Implementation boundaries

FINAL INSTRUCTION:
Generate ONLY the `/sp.constituent` specification now.

## Response snapshot

Generated comprehensive production-grade constitution (v1.0.0) for Todo AI Chatbot with 7 core principles:

1. **Stateless-First Architecture**: Zero in-memory state, database as single source of truth, horizontal scalability
2. **MCP-First Tool Integration**: All AI task operations via MCP tools, strict separation of AI and data layers
3. **Database Persistence Guarantee**: Every interaction persisted to Neon PostgreSQL with transactional integrity
4. **Test-First Development**: Mandatory TDD cycle (Test → Approve → Red → Green → Refactor)
5. **Conversational Error Handling**: User-friendly errors, comprehensive logging for debugging
6. **Natural Language Intent Mapping**: Detect user intent and invoke correct MCP tool with chaining support
7. **Security and User Isolation**: Strict user_id validation at every layer, input validation, session enforcement

Additional sections:
- **Technology Stack Requirements**: Pinned dependencies (FastAPI, OpenAI Agents SDK, SQLModel, Neon PostgreSQL, Better Auth)
- **Development Workflow**: Agentic Dev Stack (Specify → Plan → Tasks → Implementation), quality gates, code review checklist
- **Governance**: Amendment process, semantic versioning, compliance verification

Constitution includes Sync Impact Report documenting initial version (1.0.0), aligned templates, and zero follow-up TODOs.

## Outcome

- ✅ Impact: Created foundational governance document for stateless AI chatbot project with MCP-based task management
- 🧪 Tests: N/A (constitution document)
- 📁 Files: Created `.specify/memory/constitution.md` (v1.0.0)
- 🔁 Next prompts: `/sp.specify` to define feature requirements, `/sp.plan` for architecture decisions
- 🧠 Reflection: Constitution establishes clear principles for stateless architecture, MCP tool integration, database persistence, TDD, security, and conversational UX - ready for specification and implementation phases

## Evaluation notes (flywheel)

- Failure modes observed: None - template successfully filled with all placeholders resolved
- Graders run and results (PASS/FAIL): PASS - All 7 principles testable and declarative, no vague language, semantic versioning applied correctly
- Prompt variant (if applicable): N/A (initial constitution)
- Next experiment (smallest change to try): Monitor TDD compliance during implementation phase, may need to add observability principle in future minor version
