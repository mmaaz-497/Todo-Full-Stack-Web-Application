---
id: 001
title: Create initial project constitution
stage: constitution
date: 2025-12-18
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: developer
command: /sp.constitution
labels: ["constitution", "foundational", "phase-2", "setup", "hackathon"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - none
---

## Prompt

@HACKATHON.md This is my hackathon file. From it, I need to build **Phase II: "Todo Full-Stack Web Application."**
All the details about which technologies to use and how to build it are already included in this file. For now, you only need to implement **up to Phase II**.

For this, first you need to create the **/sp.constitution** file, then—according to the hierarchy—create **/sp.spec**, **/sp.plan**, and continue running the next commands in the same way to design my entire project. Along with each command, you must also provide the prompt so that you can clearly understand and implement it properly.

You do **not** need to build the UI right now. I will tell you later how the UI should be created.

## Response snapshot

Created comprehensive constitution (v1.0.0) for Todo Full-Stack Web Application with 7 core principles:

1. **Spec-Driven Development (NON-NEGOTIABLE)** - All code via Claude Code from explicit specs
2. **API-First Design** - Backend REST API before frontend
3. **Test-First Development** - Red-Green-Refactor cycle mandatory
4. **Security by Default** - JWT authentication, input validation, user isolation
5. **User Data Isolation (NON-NEGOTIABLE)** - Each user accesses only their own data
6. **Stateless Architecture** - Horizontal scaling via JWT and database persistence
7. **Clean Code & Simplicity** - YAGNI, DRY, clear naming conventions

Additional sections defined:
- **Technology Stack & Constraints**: Mandatory stack (Next.js 16+, FastAPI, SQLModel, Neon PostgreSQL, Better Auth)
- **Security & Authentication Requirements**: JWT flow, security controls, API security contract
- **Development Workflow**: 5-phase SDD cycle (Specify → Plan → Tasks → Implement → Analyze)
- **Governance**: Amendment process, compliance requirements, versioning policy

Monorepo structure defined with frontend/, backend/, specs/, history/, and .specify/ directories.

## Outcome

- ✅ Impact: Constitution established as highest authority for all technical/process decisions
- 🧪 Tests: None (foundational documentation artifact)
- 📁 Files: Created .specify/memory/constitution.md (299 lines)
- 🔁 Next prompts: /sp.specify to create feature specification for Phase II Todo CRUD operations
- 🧠 Reflection: Constitution provides clear, testable principles aligned with hackathon Phase II requirements. Emphasizes security (JWT, user isolation), spec-driven workflow, and API-first design. Ready for feature specification phase.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS - All placeholders filled, no manual coding constraint enforced, security requirements explicit
- Prompt variant (if applicable): N/A (initial constitution)
- Next experiment (smallest change to try): Proceed with /sp.specify to validate constitution guides feature specification effectively
