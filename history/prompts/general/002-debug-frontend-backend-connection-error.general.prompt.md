---
id: 002
title: Debug Frontend Backend Connection Error
stage: general
date: 2025-12-21
surface: agent
model: claude-sonnet-4-5
feature: none
branch: master
user: user
command: debugging
labels: ["debugging", "frontend", "backend", "network-error", "connection", "port-configuration"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - frontend/.env.local
  - backend/.env
  - backend/main.py
  - frontend/lib/api.ts
tests:
  - none
---

## Prompt

When I try to create a task, it shows: "localhost says: Failed to create task: Network Error." I think my frontend is not connected to the backend, because I even tried to connect it myself and it still gave a connection error.

## Response snapshot

**Problem Identified:**
The backend server was not running. Port 8000 was not in use, causing the frontend to get "Network Error" when attempting API calls.

**Diagnosis Process:**
1. Explored codebase to understand frontend-backend configuration
2. Found frontend runs on port 3000, backend on port 8000
3. Verified frontend .env.local exists with correct API URL: http://localhost:8000
4. Verified backend .env exists with correct CORS settings
5. Checked port 8000 usage - confirmed nothing listening on the port

**Solution Provided:**
Start the backend server using either:
- `python main.py` from backend directory
- `uvicorn main:app --reload` from backend directory (recommended)

**Configuration Summary:**
- Frontend: Next.js on port 3000, configured to connect to http://localhost:8000
- Backend: FastAPI on port 8000, CORS allows http://localhost:3000
- Auth: JWT tokens stored in localStorage, automatically attached via Axios interceptors
- All task endpoints require authentication and use path `/api/{user_id}/tasks`

## Outcome

- ✅ Impact: Identified root cause (backend not running) and provided clear startup instructions
- 🧪 Tests: No tests run (diagnostic session)
- 📁 Files: Read 4 configuration files to diagnose issue
- 🔁 Next prompts: User should start backend server and verify connection
- 🧠 Reflection: Simple connectivity issue - configuration was correct, service just needed to be started

## Evaluation notes (flywheel)

- Failure modes observed: Network errors often caused by service not running rather than misconfiguration
- Graders run and results (PASS/FAIL): N/A (diagnostic session)
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): User should run `uvicorn main:app --reload` and test task creation
