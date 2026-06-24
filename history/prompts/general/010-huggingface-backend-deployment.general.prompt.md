---
id: 010
title: Hugging Face backend deployment + dedup
stage: general
date: 2026-06-24
surface: agent
model: claude-opus-4-8
feature: none
branch: main
user: Muhammad Maaz
command: general
labels: [deployment, huggingface, cleanup, dedup]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - docs/HUGGINGFACE_DEPLOYMENT.md (created)
 - docs/BACKEND_DEPLOYMENT.md (rewritten — HF-first, Render demoted to alt)
 - backend/api-service/README_HF_SPACE.md (created — Space Docker frontmatter)
 - backend/api-service/app/models.py (deleted — dead, shadowed by app/models/ package)
 - render.yaml (deleted)
 - README.md (Render refs → Hugging Face)
tests:
 - none (static config/docs + safe dead-code removal)
---

## Prompt

I want to deploy the backend on a free service like Hugging Face so it can be connected to the frontend after deployment. Please set up the deployment for Hugging Face, remove the Render configuration, and merge any duplicate files. Please handle everything carefully.

## Response snapshot

Set up Hugging Face Spaces (Docker SDK) deployment for `backend/api-service`:
- Created `backend/api-service/README_HF_SPACE.md` with the required HF frontmatter
  (`sdk: docker`, `app_port: 8000`) — `app_port` matches the existing Dockerfile
  prod stage, which already runs as non-root uid 1000 (HF requirement). No
  Dockerfile change needed.
- Created `docs/HUGGINGFACE_DEPLOYMENT.md`: Method A (create Space + copy folder)
  and Method B (`git subtree push`), secrets table, frontend wiring
  (`NEXT_PUBLIC_API_URL`), CORS, Neon DB notes.
- Rewrote `docs/BACKEND_DEPLOYMENT.md` to be HF-first; Render/Koyeb demoted to
  alternatives. Removed `render.yaml`. Updated README links (no `render` refs left).

Duplicate handling (careful):
- Deleted `app/models.py` — provably dead: a same-named `app/models/` package
  shadows it, and its `Conversation`/`Message` are defined identically in
  `app/models/conversation.py` (what `from app.models import ...` actually resolves
  to). Zero runtime impact.
- Deliberately did NOT merge `db.py` ↔ `app/database.py` (two live engines used by
  tasks/search/health vs agent/chat) or `auth.py` ↔ `app/auth.py` (different
  verification: BetterAuth HTTP vs local JWT). Those are behavioral, live, and
  risky pre-deploy — flagged as tech debt instead.

## Outcome

- ✅ Impact: Backend has a free, always-on Hugging Face deploy path; Render config
  removed; one real duplicate file eliminated safely.
- 🧪 Tests: none (docs/config + dead-code removal).
- 📁 Files: see front-matter.
- 🔁 Next prompts: create the Space + push; optionally consolidate the dual DB
  engine and the two auth mechanisms in a dedicated refactor with tests.
- 🧠 Reflection: "duplicate" ≠ "mergeable" — verified import resolution before
  deleting; left live, behaviorally-different modules alone.

## Evaluation notes (flywheel)

- Failure modes observed: none.
- Graders run and results (PASS/FAIL): N/A.
- Prompt variant (if applicable): N/A.
- Next experiment (smallest change to try): single-engine refactor behind tests.
