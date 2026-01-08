---
id: 003
title: Integrate pre-built Better Auth service
stage: constitution
date: 2025-12-18
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: developer
command: /sp.constitution (amendment)
labels: ["constitution", "authentication", "better-auth", "integration", "pre-built-service"]
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

And yes, I have already provided a fully built **Better Auth** under the service name **/Todo-Full-Stack-Web-Application/auth-service**, so customize and use it according to the project's requirements. Then, accordingly, update the **Better Auth** section in the **constitution** file as well.

## Response snapshot

Updated constitution (v1.1.0 → v1.2.0) to document pre-built Better Auth microservice:

### Key Changes

**1. Technology Stack → Authentication Section Updated**
- Pre-built Better Auth microservice at `/auth-service` (port 3001)
- Better Auth v1.0.9 with Hono framework + Drizzle ORM
- Session-based authentication with JWT support
- Integration: Frontend → auth service, Backend verifies JWT with `BETTER_AUTH_SECRET`

**2. Security & Authentication Requirements → Pre-Built Service Details**
- Auth service location and configuration documented
- Endpoints: `/api/auth/signup/email`, `/api/auth/signin/email`, `/api/auth/signout`, `/api/auth/session`, `/health`
- Authentication flow revised to use existing service
- Customization requirements:
  * Remove custom fields (experienceLevel, professionalRole, organization)
  * Keep only: id, email, name, createdAt, updatedAt
  * Share BETTER_AUTH_SECRET across services
  * Configure CORS for frontend (3000) and backend (8000)

**3. Monorepo Structure → auth-service/ Directory Added**
- Port allocation defined: Frontend (3000), Auth (3001), Backend (8000)
- Backend auth.py middleware for JWT verification
- Auth service runs on same Neon PostgreSQL database

### Auth Service Details Discovered
- Uses Drizzle ORM with PostgreSQL
- Email/password authentication
- Session expiration: 7 days (configurable)
- Hono web framework
- Health check endpoint available
- Database schema: `users`, `session`, `account`, `verification` tables

### Follow-up TODOs in Constitution
1. Customize `auth-service/src/lib/auth.ts` to remove unnecessary custom fields
2. Ensure `BETTER_AUTH_SECRET` shared across all services
3. Update `CORS_ORIGINS` to include frontend and backend URLs
4. Implement JWT verification middleware in `backend/auth.py`

## Outcome

- ✅ Impact: Constitution now documents pre-built auth service integration, eliminating need to build auth from scratch
- 🧪 Tests: None (documentation artifact)
- 📁 Files: Updated .specify/memory/constitution.md (v1.2.0, 428 lines)
- 🔁 Next prompts: /sp.specify with auth service integration requirements
- 🧠 Reflection: Pre-built auth service significantly reduces Phase II implementation scope. Focus shifts from building auth to integrating existing service and implementing JWT verification middleware in backend.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS - Pre-built service properly documented, customization steps clear, port allocation explicit
- Prompt variant (if applicable): N/A (constitution amendment)
- Next experiment (smallest change to try): Create spec that includes auth customization tasks as prerequisite before main CRUD implementation
