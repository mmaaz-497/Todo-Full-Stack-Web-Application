---
id: 004
title: Clarify auth database schema reconfiguration
stage: constitution
date: 2025-12-18
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: developer
command: /sp.constitution (amendment)
labels: ["constitution", "authentication", "database-schema", "customization", "clarification"]
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

This "Database schema already defined (users, session, account tables)" schema is from my previous project. Set up the schema according to this project's requirements.

## Response snapshot

Updated constitution (v1.2.0 → v1.3.0) to clarify that auth-service database schema is from **previous project** (Physical AI Humanoid Robotics) and requires **mandatory reconfiguration** for Todo app.

### Key Changes

**1. Product Scope → User Entity Clarification**
- Added warning note that current schema is from previous project
- Listed custom fields that MUST be removed: experienceLevel, professionalRole, roleOther, organization
- Defined final User fields after customization: id, email, name, emailVerified, image, createdAt, updatedAt

**2. Security & Authentication → Detailed Customization Guide**

Added comprehensive reconfiguration steps with **exact file paths and line numbers**:

**Database Schema (auth-service/src/db/schema.ts)**:
- Remove lines 3-9: experienceLevels and professionalRoles enums
- Remove lines 21-25: Custom fields from user table
  ```typescript
  experienceLevel: text('experience_level').notNull().$type<ExperienceLevel>(),
  professionalRole: text('professional_role').notNull().$type<ProfessionalRole>(),
  roleOther: text('role_other'),
  organization: text('organization'),
  ```
- Keep only Better Auth core fields
- Keep session, account, verification tables unchanged

**Better Auth Config (auth-service/src/lib/auth.ts)**:
- Remove user.additionalFields section (lines 18-44):
  ```typescript
  user: {
    additionalFields: {
      experienceLevel: { ... },
      professionalRole: { ... },
      roleOther: { ... },
      organization: { ... },
    },
  }
  ```

**Migration Commands**:
```bash
cd auth-service
npm run migrate          # Generate new migrations
npm run migrate:push     # Apply to Neon PostgreSQL
```

**Environment Configuration**:
- Share BETTER_AUTH_SECRET across auth-service/.env, frontend/.env.local, backend/.env
- Configure CORS_ORIGINS: http://localhost:3000,http://localhost:8000
- Ensure same DATABASE_URL for auth-service and backend

**3. Sync Impact Report Updated**
- Changed from "Database schema already defined" to "Schema from previous project - MUST reconfigure"
- Added critical follow-up TODOs (7 tasks) that MUST complete before CRUD implementation
- Updated templates requiring updates section with specific customization tasks

### Current vs. Required State

**Current (Physical AI Humanoid Robotics):**
```typescript
user {
  id, email, name, emailVerified, createdAt, updatedAt, image,
  experienceLevel,      // ❌ Remove
  professionalRole,     // ❌ Remove
  roleOther,           // ❌ Remove
  organization         // ❌ Remove
}
```

**Required (Todo App):**
```typescript
user {
  id, email, name, emailVerified, createdAt, updatedAt, image
  // Simple user profile - no custom fields
}
```

## Outcome

- ✅ Impact: Constitution now explicitly states schema reconfiguration is MANDATORY prerequisite before CRUD implementation
- 🧪 Tests: None (documentation artifact)
- 📁 Files: Updated .specify/memory/constitution.md (v1.3.0, 487 lines)
- 🔁 Next prompts: /sp.specify must include auth customization as Phase 0 (prerequisite) before Phase II CRUD
- 🧠 Reflection: Critical clarification prevents incorrect assumption that auth is ready to use. Customization tasks will be first priority in specification and task breakdown.

## Evaluation notes (flywheel)

- Failure modes observed: Assumption that pre-built = ready to use (false)
- Graders run and results (PASS/FAIL): PASS - Schema reconfiguration now explicit with exact line numbers and commands
- Prompt variant (if applicable): N/A (constitution clarification)
- Next experiment (smallest change to try): Create spec with Phase 0 (Auth Customization) as blocking prerequisite before Phase 1 (CRUD Implementation)
