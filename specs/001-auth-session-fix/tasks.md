# Tasks: Authentication Session Endpoint & Sign-Up Validation Improvements

**Input**: Design documents from `/specs/001-auth-session-fix/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests NOT included - specification does not explicitly request TDD approach. Manual testing using quickstart.md will validate implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Auth service**: `auth-service/src/`, `auth-service/tests/`
- **Backend**: `backend/` (NO CHANGES NEEDED - already complete)
- **Frontend**: `frontend/` (NO CHANGES NEEDED - already complete)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify project structure and dependencies are ready for implementation

- [X] T001 Verify auth-service is on branch 001-auth-session-fix
- [X] T002 [P] Verify auth-service dependencies are installed (npm install in auth-service/)
- [X] T003 [P] Verify database is running and auth-service can connect (check DATABASE_URL in .env)
- [X] T004 [P] Verify Better Auth configuration is correct in auth-service/src/lib/auth.ts (bearer plugin enabled, JWT secret set)
- [X] T005 Create tests/contract/ directory in auth-service/ if it doesn't exist

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Verify existing infrastructure that user stories depend on

**⚠️ CRITICAL**: Confirm these are working before ANY user story implementation begins

- [X] T006 Verify session endpoint is accessible via Better Auth in auth-service/src/index.ts (app.use('/api/auth/*', auth.handler))
- [X] T007 [P] Verify rate limiting is configured correctly in auth-service/src/index.ts (session: 30 req/min, sign-up: 5 req/min)
- [X] T008 [P] Verify CORS middleware is configured in auth-service/src/middleware/cors.ts
- [ ] T009 Test sign-in endpoint works and returns JWT token (manual test with curl per quickstart.md)

**Checkpoint**: Foundation verified - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Backend Service Token Validation (Priority: P1) 🎯 MVP

**Goal**: Enable backend services to validate JWT tokens by calling the session endpoint and receiving user information

**Independent Test**: Call session endpoint with valid Bearer token and verify it returns user data (id, email, name). Call with invalid token and verify 401 error.

### Implementation for User Story 1

- [ ] T010 [US1] Verify session endpoint returns user data for valid token in auth-service (manual test: sign in, extract token, call GET /api/auth/session with Authorization: Bearer {token})
- [ ] T011 [US1] Verify session endpoint returns 401 for invalid token in auth-service (manual test: call session endpoint with "Bearer invalid_token")
- [ ] T012 [US1] Verify session endpoint returns 401 for missing Authorization header in auth-service (manual test: call session endpoint without Authorization header)
- [ ] T013 [US1] Verify backend token validation works in backend/auth.py by calling auth service session endpoint (run backend, make authenticated API request, check logs)
- [ ] T014 [US1] Document session endpoint behavior in API_TESTING.md with curl examples for all scenarios (valid token, invalid token, missing header)

**Checkpoint**: At this point, User Story 1 should be fully functional - backend can validate tokens via session endpoint

---

## Phase 4: User Story 2 - Clear Sign-Up Validation Feedback (Priority: P1)

**Goal**: Provide users with specific, actionable error messages when sign-up validation fails (password length, email format, duplicate email)

**Independent Test**: Attempt sign-ups with invalid inputs (short password, invalid email, duplicate email) and verify each returns a specific error message with correct HTTP status code.

### Implementation for User Story 2

- [X] T015 [P] [US2] Create validation error handler middleware in auth-service/src/middleware/validation-errors.ts (intercept error responses, transform Better Auth errors into specific messages)
- [X] T016 [US2] Register validation error middleware in auth-service/src/index.ts before auth.handler route (app.use('/api/auth/*', validationErrorHandler()))
- [X] T017 [P] [US2] Add error transformation logic for password too short (<8 chars) to return 400 with "Password must be at least 8 characters long" in validation-errors.ts
- [X] T018 [P] [US2] Add error transformation logic for password too long (>128 chars) to return 400 with "Password must not exceed 128 characters" in validation-errors.ts
- [X] T019 [P] [US2] Add error transformation logic for invalid email format to return 400 with "Invalid email address format" in validation-errors.ts
- [X] T020 [P] [US2] Add error transformation logic for duplicate email (UNIQUE constraint) to return 409 with "An account with this email already exists" in validation-errors.ts
- [X] T021 [P] [US2] Add error transformation logic for missing email to return 400 with "Email is required" in validation-errors.ts
- [X] T022 [P] [US2] Add error transformation logic for missing password to return 400 with "Password is required" in validation-errors.ts
- [X] T023 [P] [US2] Add error transformation logic for invalid/expired token to return 401 with "Invalid or expired token" in validation-errors.ts
- [X] T024 [P] [US2] Add error transformation logic for missing Authorization header to return 401 with "Authorization header is required" in validation-errors.ts
- [ ] T025 [US2] Test sign-up validation: password too short (manual test per quickstart.md step 4 test 1)
- [ ] T026 [US2] Test sign-up validation: invalid email format (manual test per quickstart.md step 4 test 2)
- [ ] T027 [US2] Test sign-up validation: duplicate email returns 409 (manual test per quickstart.md step 4 test 3)
- [ ] T028 [US2] Test sign-up validation: valid sign-up returns 201 with token (manual test per quickstart.md step 4 test 4)
- [ ] T029 [US2] Document sign-up validation errors in API_TESTING.md with curl examples for all validation scenarios

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - session validation and sign-up error messages are clear

---

## Phase 5: User Story 3 - Frontend Authentication Status Check (Priority: P2)

**Goal**: Enable frontend to check authentication status by calling session endpoint after login or page refresh

**Independent Test**: Store token after login, refresh page, call session endpoint, verify user remains authenticated. Test with expired token and verify 401 response.

### Implementation for User Story 3

- [ ] T030 [US3] Verify frontend can call session endpoint with stored token after page refresh (manual test: sign in via frontend, refresh page, check if user remains authenticated)
- [ ] T031 [US3] Verify frontend handles 401 response from session endpoint by redirecting to login (manual test: use expired/invalid token, verify frontend redirects)
- [ ] T032 [US3] Verify frontend can display user information (name, email) from session endpoint response without additional API calls (manual test: check frontend UI shows user data from session call)
- [ ] T033 [US3] Document frontend authentication flow in API_TESTING.md including session endpoint usage for authentication status checks

**Checkpoint**: All user stories should now be independently functional - session validation, sign-up errors, and frontend auth status all working

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, documentation, and quality improvements

- [ ] T034 [P] Run complete manual testing checklist from quickstart.md (all 12 items)
- [ ] T035 [P] Verify all HTTP status codes are correct (200 session success, 201 sign-up success, 400 validation, 401 auth, 409 duplicate, 429 rate limit)
- [ ] T036 [P] Verify rate limiting works correctly (test session endpoint 30 req/min, sign-up 5 req/min, confirm 429 response)
- [ ] T037 [P] Verify CORS headers are present in all responses (check Access-Control-Allow-Origin header)
- [ ] T038 [P] Verify no sensitive data is exposed in session endpoint response (no password hashes, no internal tokens beyond user fields)
- [ ] T039 [P] Verify error messages don't reveal system internals in production mode (check NODE_ENV=production behavior)
- [ ] T040 [P] Run auth-service in development mode and verify it starts without errors (npm run dev in auth-service/)
- [X] T041 [P] Build auth-service for production and verify no TypeScript errors (npm run build in auth-service/)
- [X] T042 Update IMPLEMENTATION_SUMMARY.md with validation error middleware details and session endpoint documentation
- [X] T043 Review and update API_TESTING.md to ensure all new error scenarios are documented with curl examples
- [ ] T044 Verify quickstart.md troubleshooting section covers common issues found during implementation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3, 4, 5)**: All depend on Foundational phase completion
  - User stories CAN proceed in parallel (US1, US2, US3 are independent)
  - Or sequentially in priority order: US1 (P1) → US2 (P1) → US3 (P2)
- **Polish (Phase 6)**: Depends on US1 and US2 completion minimum (US3 optional for MVP)

### User Story Dependencies

- **User Story 1 (P1 - Backend Token Validation)**: Can start after Foundational (Phase 2) - No dependencies on other stories, CRITICAL for MVP
- **User Story 2 (P1 - Sign-Up Validation)**: Can start after Foundational (Phase 2) - Independent of US1, CRITICAL for MVP
- **User Story 3 (P2 - Frontend Auth Status)**: Can start after Foundational (Phase 2) - Independent but benefits from US1 working, OPTIONAL for MVP

### Within Each User Story

**User Story 1**:
- T010-T013 can run in any order (all are verification tasks)
- T014 should be last (documentation)

**User Story 2**:
- T015 must complete before T016 (create middleware before registering it)
- T017-T024 are all [P] and can run in parallel (all modify same file but different functions)
- T025-T028 must run after T016 completes (tests depend on middleware being registered)
- T029 should be last (documentation)

**User Story 3**:
- T030-T032 can run in any order (all are verification tasks)
- T033 should be last (documentation)

### Parallel Opportunities

- All Setup tasks marked [P] (T002, T003, T004) can run in parallel
- All Foundational tasks marked [P] (T007, T008) can run in parallel
- Once Foundational completes, all three user stories can start in parallel:
  - Developer A: US1 (T010-T014)
  - Developer B: US2 (T015-T029)
  - Developer C: US3 (T030-T033)
- Within US2: T017-T024 (error transformations) can all run in parallel
- All Polish tasks marked [P] (T034-T041) can run in parallel after user stories complete

---

## Parallel Example: User Story 2 (Sign-Up Validation)

```bash
# After T015 and T016 are complete, launch all error transformation tasks together:
Task T017: "Add password too short error transformation"
Task T018: "Add password too long error transformation"
Task T019: "Add invalid email error transformation"
Task T020: "Add duplicate email error transformation"
Task T021: "Add missing email error transformation"
Task T022: "Add missing password error transformation"
Task T023: "Add invalid token error transformation"
Task T024: "Add missing Authorization header error transformation"

# Then run manual tests sequentially:
Task T025: "Test password too short"
Task T026: "Test invalid email"
Task T027: "Test duplicate email"
Task T028: "Test valid sign-up"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 Only)

**Recommended approach for fastest time to value:**

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T009) - CRITICAL checkpoint
3. Complete Phase 3: User Story 1 (T010-T014) - Backend token validation
4. Complete Phase 4: User Story 2 (T015-T029) - Sign-up validation errors
5. **STOP and VALIDATE**: Test both user stories independently using quickstart.md
6. Complete Phase 6: Polish (T034-T044) for MVP deployment
7. Deploy MVP with working session validation and clear sign-up errors

**US3 (Frontend Auth Status) can be added later as enhancement**

### Incremental Delivery

1. Complete Setup + Foundational → Foundation verified (T001-T009)
2. Add User Story 1 → Test independently → Deploy/Demo (Backend can validate tokens!)
3. Add User Story 2 → Test independently → Deploy/Demo (Users get clear sign-up errors!)
4. Add User Story 3 → Test independently → Deploy/Demo (Frontend can check auth status!)
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T009)
2. Once Foundational is verified (Phase 2 checkpoint):
   - **Developer A**: User Story 1 (T010-T014) - ~1-2 hours
   - **Developer B**: User Story 2 (T015-T029) - ~4-6 hours (largest story)
   - **Developer C**: User Story 3 (T030-T033) - ~1-2 hours
3. Stories complete independently and can be deployed individually

---

## Task Summary

- **Total Tasks**: 44
- **Setup Phase**: 5 tasks
- **Foundational Phase**: 4 tasks (BLOCKING)
- **User Story 1 (P1)**: 5 tasks (Backend token validation - MVP CRITICAL)
- **User Story 2 (P1)**: 15 tasks (Sign-up validation errors - MVP CRITICAL)
- **User Story 3 (P2)**: 4 tasks (Frontend auth status - Optional for MVP)
- **Polish Phase**: 11 tasks (Final validation and documentation)

### Parallel Opportunities

- **Maximum parallelism**: 19 tasks can run in parallel (all [P] tasks)
- **User stories in parallel**: All 3 user stories can start simultaneously after Foundation
- **Minimum completion time**: ~6-8 hours with 3 developers working in parallel
- **Single developer**: ~12-16 hours working sequentially in priority order

### Independent Test Criteria

**User Story 1 (Backend Token Validation)**:
- ✅ Session endpoint returns 200 + user data for valid token
- ✅ Session endpoint returns 401 for invalid token
- ✅ Session endpoint returns 401 for missing Authorization header
- ✅ Backend can validate tokens and enforce authorization

**User Story 2 (Sign-Up Validation)**:
- ✅ Password <8 chars returns 400 with specific message
- ✅ Password >128 chars returns 400 with specific message
- ✅ Invalid email returns 400 with specific message
- ✅ Duplicate email returns 409 with specific message
- ✅ Valid sign-up returns 201 with token

**User Story 3 (Frontend Auth Status)**:
- ✅ Frontend can check auth status after login
- ✅ Frontend can restore session after page refresh
- ✅ Frontend handles 401 (expired token) correctly
- ✅ Frontend displays user info from session response

### Suggested MVP Scope

**Minimum Viable Product includes**:
- User Story 1 (P1): Backend token validation - CRITICAL
- User Story 2 (P1): Sign-up validation errors - CRITICAL
- Polish tasks (subset): T034, T035, T040, T041, T042, T043

**Can be deferred to v2**:
- User Story 3 (P2): Frontend auth status checks (nice-to-have, not blocking)
- Polish tasks: T036-T039, T044 (thorough validation, can be done post-MVP)

---

## Notes

- [P] tasks = different files or different functions in same file, no dependencies
- [Story] label (US1, US2, US3) maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Manual testing using quickstart.md validates implementation (no automated tests in this feature)
- Commit after each task or logical group of related tasks
- Stop at any checkpoint to validate story independently
- Backend and frontend require NO CHANGES - only auth-service is modified
- All file paths use auth-service/ prefix since that's the only service being modified
