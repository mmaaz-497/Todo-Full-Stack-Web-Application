---
id: 002
title: AI Reminder Agent Implementation Plan
stage: plan
date: 2025-12-25
surface: agent
model: claude-sonnet-4-5-20250929
feature: ai-reminder-agent
branch: 001-auth-session-fix
user: Muahmmad Maaz
command: /sp.plan
labels: ["implementation-plan", "architecture", "ai-agent", "phased-approach", "production-ready"]
links:
  spec: specs/ai-reminder-agent/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/ai-reminder-agent/plan.md
  - history/prompts/ai-reminder-agent/002-ai-reminder-agent-plan.plan.prompt.md
tests:
  - Test strategy defined for unit, integration, and end-to-end testing
---

## Prompt

/sp.plan

Create a step-by-step execution plan to build the AI Task Reminder Agent.

The plan must include:
1. Overall system architecture
2. Agent lifecycle (startup → task fetch → decision → email send)
3. Database querying strategy (efficient & safe)
4. Reminder scheduling logic:
   - One-time tasks
   - Daily repeating tasks
   - Weekly repeating tasks
   - Monthly repeating tasks
5. Email delivery flow
6. Handling timezones
7. Avoiding duplicate reminders
8. Logging & monitoring
9. Failure recovery strategy
10. Environment variables & secrets management

Break the plan into:
- Phase 1: Foundation
- Phase 2: Core Agent Logic
- Phase 3: Scheduling & Repeat Logic
- Phase 4: Email System
- Phase 5: Testing & Production Readiness

Output must be:
- Clear
- Structured
- Developer-friendly
- Suitable for real-world deployment

## Response snapshot

Created comprehensive 5-phase implementation plan for AI Task Reminder Agent:

**Phase 1: Foundation Setup**
- Database schema migration (reminder_log, agent_state tables with indexes)
- SQLModel models for new tables
- Project structure (config, models, services, jobs, utils, tests, templates)
- Dependencies management (requirements.txt with 15+ packages)
- Environment configuration with pydantic-settings
- Structured JSON logging infrastructure

**Phase 2: Core Agent Logic**
- Database connection management with pooling and health checks
- TaskReader service for efficient task querying
- In-memory filtering for complex time-based logic
- User email fetching (with Better Auth integration placeholder)

**Phase 3: Scheduling & Repeat Logic**
- ReminderCalculator service with 4 algorithms:
  - One-time: Direct datetime comparison
  - Daily: Time-based repetition with tomorrow rollover
  - Weekly: Weekday-based scheduling
  - Monthly: Day-of-month with edge case handling (Feb 31 → Feb 28/29)
- DuplicateChecker with UNIQUE constraint + 60-second tolerance window
- Timezone utilities for UTC storage and user-local conversion
- Grace period logic (skip if >1 week past due)

**Phase 4: Email System**
- AI Email Generator with Gemini integration via OpenAI SDK
- Template-based fallback for API failures
- Priority-based subject lines with emojis (🔴 URGENT, 🟡 Medium, 📋 Low)
- HTML email template with responsive design
- SMTP sender with tenacity retry logic (3 attempts, exponential backoff)
- Delivery Tracker logging to reminder_log with status tracking

**Phase 5: Testing & Production Readiness**
- ReminderProcessor main job orchestrating all services
- APScheduler-based polling (5-minute intervals)
- Agent state tracking for health monitoring
- Main entry point with startup validation
- Unit tests using pytest + freezegun for time-based scenarios
- 8 comprehensive test cases covering all repeat types and edge cases

**Critical Design Decisions (with ADR-worthy considerations)**:
1. APScheduler vs Celery: Start with APScheduler (simple), migrate to Celery when scaling
2. Gemini API fallback: Template-based fallback to guarantee delivery (reliability > personalization)
3. Timezone handling: UTC storage + user timezone conversion (industry best practice)
4. Duplicate prevention: Database UNIQUE constraint + application tolerance window

**Deployment Strategy**:
- Development: venv + manual startup
- Production: Docker containerization with health checks
- docker-compose orchestration with restart policies
- Environment-based configuration

**Rollback Plan**:
- Stop agent container
- Verify data integrity
- Restore from database backup if needed
- Drop migration tables if necessary

## Outcome

- ✅ Impact: Complete production-ready implementation plan with 5 phases, 20+ code files, database migrations, testing strategy, deployment configs, and rollback procedures
- 🧪 Tests: Unit test framework defined with freezegun for time-based scenarios, 8 test cases covering all repeat types and edge cases
- 📁 Files: Created specs/ai-reminder-agent/plan.md (~1200 lines, 10 sections)
- 🔁 Next prompts: /sp.tasks (generate actionable task breakdown), /sp.adr (document critical architectural decisions)
- 🧠 Reflection: Plan provides clear implementation path with complete code examples, addresses all user requirements including edge cases (Feb 31st, timezone handling, duplicate prevention), and includes production considerations (Docker, monitoring, rollback)

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS - All 10 requirements addressed with detailed implementation steps, code examples, and production deployment strategy
- Prompt variant (if applicable): Standard /sp.plan workflow with phased approach
- Next experiment (smallest change to try): Consider adding webhook-based trigger instead of polling for better real-time responsiveness and reduced database load

**Architectural Decisions Requiring ADRs:**
1. Scheduler choice (APScheduler vs Celery)
2. AI fallback strategy (template vs skip)
3. Timezone handling approach (UTC vs local storage)
4. Duplicate prevention mechanism (DB constraint vs cache)
