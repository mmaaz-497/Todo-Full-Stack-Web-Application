---
id: 011
title: Bundle reminder worker into API for Hugging Face
stage: general
date: 2026-06-24
surface: agent
model: claude-opus-4-8
feature: none
branch: main
user: Muhammad Maaz
command: general
labels: [deployment, huggingface, reminders, auth, backend]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - backend/api-service/reminder_worker/ (created — copied reminder-agent runtime)
 - backend/api-service/start.sh (created — runs API + reminder worker)
 - backend/api-service/requirements.txt (added apscheduler, aiosmtplib, jinja2, tenacity)
 - backend/api-service/Dockerfile (prod CMD -> sh start.sh)
 - backend/api-service/README_HF_SPACE.md (api Space config + reminder/auth env)
 - backend/auth-service/README_HF_SPACE.md (created — auth Space config)
 - docs/HUGGINGFACE_DEPLOYMENT.md (rewritten — two-Space + reminders walkthrough)
tests:
 - python -m compileall reminder_worker (PASS)
---

## Prompt

Currently, my backend is not deployed; only the frontend is live. Even on the frontend, the authentication service is not working because it has not been deployed yet. I want the API services, authentication, and the email reminder system (sends reminders at the scheduled time) to work correctly, deployed free on Hugging Face. I don't know how to deploy on Hugging Face — guide me through the entire process.

## Response snapshot

Decided architecture: two HF Docker Spaces (auth-service Node:3001, api-service Python:8000) + shared Neon + Vercel frontend. Reminders bundled into the API Space as a second process.

Verification before building:
- Auth is **Bearer-token based** (frontend stores token, sends to auth + API) → no cross-domain cookie problem. auth-service config is env-driven (PORT, BETTER_AUTH_URL, CORS_ORIGINS/trustedOrigins); ships compiled `dist/` only (verified complete).
- api-service's built-in reminder path is Dapr-Jobs+Kafka and inert without them. Real engine is `reminder-agent` (APScheduler poll + SMTP + Gemini, no Kafka/Dapr).
- Confirmed alignment: API persists `tasks.reminder_time`; `to_utc()` keeps Pakistan-local-naive (NOT real UTC), matching the agent's `Asia/Karachi` comparison; agent reads emails from the Better Auth `user` table — all same Neon DB.

Built (Option A — second process, chosen by user): copied reminder-agent runtime to `backend/api-service/reminder_worker/`; added `start.sh` (worker in background + uvicorn on `$PORT`, --workers 1); added deps; prod Dockerfile CMD -> `sh start.sh`; created HF Space README configs for both services; rewrote the HF guide into a full two-Space + reminder walkthrough. Worker compiles clean.

## Outcome

- ✅ Impact: One API Space now serves tasks + AI + reminders; auth is a second Space; full free path documented.
- 🧪 Tests: `compileall` on reminder_worker passed; runtime not yet deployed.
- 📁 Files: see front-matter.
- 🔁 Next prompts: user creates the two Spaces and pushes; verify login + a live reminder email.
- 🧠 Reflection: verified data/timezone alignment before committing to the bundle so reminders actually fire.

## Evaluation notes (flywheel)

- Failure modes observed: none yet (pre-deploy).
- Graders run and results (PASS/FAIL): compileall PASS.
- Prompt variant (if applicable): N/A.
- Next experiment (smallest change to try): live reminder end-to-end test on HF.
