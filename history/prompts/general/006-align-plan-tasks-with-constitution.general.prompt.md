---
id: 006
title: Align Plan and Tasks with Constitution
stage: general
date: 2025-12-27
surface: agent
model: claude-sonnet-4-5-20250929
feature: todo-ai-chatbot
branch: 001-auth-session-fix
user: Claude Code
command: /update-artifacts
labels: ["constitution-alignment", "tdd-enforcement", "plan-update", "tasks-creation"]
links:
  spec: specs/todo-ai-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/todo-ai-chatbot/plan.md
  - specs/todo-ai-chatbot/tasks.md
tests:
  - N/A (artifact alignment, no code changes)
---

## Prompt

I have already generated sp.plan and sp.tasks earlier, so check if anything needs to be updated in these files according to the constitution, and update them accordingly.

## Response snapshot

**Critical Constitution Violation Identified:**
The existing plan.md had testing in Phase 7 (after implementation), which **violates Constitution v1.0.0 Principle IV: Test-First Development (NON-NEGOTIABLE)**.

**Updates Made:**

### 1. plan.md Updates
- **Added Constitution Principles Section**: Referenced all 7 principles from Constitution v1.0.0 at the beginning
- **Added TDD Workflow**: Explicit 6-step TDD mandate (Write tests → Approve → Verify RED → Implement GREEN → Refactor → Pass)
- **Phase 2 (Database)**: Added TDD requirement section - tests MUST be written FIRST before models
- **Phase 3 (MCP Server)**: Added TDD requirement section - all 5 tool tests MUST be written FIRST
- **Phase 4 (AI Agent)**: Added TDD requirement section - intent detection, tool chaining, error handling tests FIRST
- **Phase 5 (FastAPI)**: Added TDD requirement section - authentication, stateless flow, security tests FIRST
- **Phase 7 Restructured**: Changed from "Testing & Validation" to "Final Validation & Acceptance" - now focuses on verifying all tests are GREEN and validating constitution compliance
- **Added Constitution Compliance Summary**: Final section documenting alignment with all 7 principles

### 2. tasks.md Created (New File)
- **38 Total Tasks**: Comprehensive breakdown aligned with plan phases
- **22 TDD Tasks (58%)**: Explicit RED-GREEN-REFACTOR workflow for all implementation tasks
- **Constitution Metadata**: Version tracking (constitution_version: 1.0.0, tdd_enforced: true)
- **TDD Task Pattern**:
  - Task X.1: Write tests FIRST (RED phase)
  - Task X.2-X.N: Implement features (GREEN phase)
  - Each task references constitution principles
  - Acceptance criteria tied to test passage

**Key TDD Enforcement Examples:**
- Task 2.1: Write database tests FIRST, verify they FAIL
- Task 2.2: Implement models to make tests PASS
- Task 3.1: Write ALL 5 MCP tool tests FIRST
- Task 3.3-3.7: Implement each tool individually (GREEN phase)
- Task 4.1: Write agent tests FIRST
- Task 5.1: Write API tests FIRST

**Constitution Compliance:**
All 7 principles enforced throughout:
1. ✅ Stateless-First Architecture - Database persistence, no in-memory state
2. ✅ MCP-First Tool Integration - All task ops via MCP tools only
3. ✅ Database Persistence Guarantee - Every interaction persisted
4. ✅ Test-First Development - TDD cycle mandatory (RED → GREEN → REFACTOR)
5. ✅ Conversational Error Handling - Friendly errors, logging
6. ✅ Natural Language Intent Mapping - Intent detection tests
7. ✅ Security and User Isolation - user_id validation at every layer

## Outcome

- ✅ Impact: Critical fix - plan.md now enforces TDD throughout (was violating constitution), tasks.md created with 38 testable tasks
- 🧪 Tests: TDD workflow embedded in 22 tasks across 5 phases, all tests must be written BEFORE implementation
- 📁 Files: Updated `specs/todo-ai-chatbot/plan.md`, created `specs/todo-ai-chatbot/tasks.md`
- 🔁 Next prompts: `/sp.implement` to execute tasks following strict TDD discipline
- 🧠 Reflection: Plan was non-compliant with Constitution Principle IV (Test-First Development). Restructured to enforce RED-GREEN-REFACTOR cycle, ensuring no implementation code written until tests exist and fail. tasks.md provides deterministic execution path.

## Evaluation notes (flywheel)

- Failure modes observed: Original plan had testing as Phase 7 (post-implementation) instead of integrated TDD - major constitution violation
- Graders run and results (PASS/FAIL): PASS - Constitution compliance now 7/7 principles, TDD workflow explicitly enforced
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Monitor TDD compliance during implementation - may need to add git hook to enforce test-first commits
