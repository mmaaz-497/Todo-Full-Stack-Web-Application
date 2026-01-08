---
id: 008
title: Fix git add nul error
stage: general
date: 2026-01-08
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: 002-phase-v-cloud-deployment
user: Muahmmad Maaz
command: git add .
labels: ["git","windows","reserved-names","repo-hygiene"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/reminder-agent/nul
  - backend/reminder-agent/logs/nul
  - .gitignore
tests:
  - N/A
---

## Prompt

I push my code to github but it occur this error fix this
PS D:\GIAIC\Quater_4_AIDD\Hackathon-2\Todo-Full-Stack-Web-Application> git init
Reinitialized existing Git repository in D:/GIAIC/Quater_4_AIDD/Hackathon-2/Todo-Full-Stack-Web-Application/.git/
PS D:\GIAIC\Quater_4_AIDD\Hackathon-2\Todo-Full-Stack-Web-Application> git add .
error: open("backend/reminder-agent/nul"): No such file or directory
error: unable to index file 'backend/reminder-agent/nul'
fatal: adding files failed
PS D:\GIAIC\Quater_4_AIDD\Hackathon-2\Todo-Full-Stack-Web-Application>

## Response snapshot

- Identified the cause as Windows reserved device-name files (`nul`) inside `backend/reminder-agent/`.
- Deleted the two offending `nul` files:
  - `backend/reminder-agent/nul`
  - `backend/reminder-agent/logs/nul`
- Enabled Git protection for NTFS reserved names: `git config core.protectNTFS true`
- Updated `.gitignore` to ignore Windows reserved device names going forward.
- Re-ran `git add .` successfully.

## Outcome

- ✅ Impact: Git staging works on Windows; repository can now be committed/pushed.
- 🧪 Tests: Not applicable
- 📁 Files: Deleted reserved-name files and updated `.gitignore`.
- 🔁 Next prompts: Commit and push changes; ensure `backend/reminder-agent/venv/` is not committed (recommended to keep ignored).
- 🧠 Reflection: Avoid creating filenames that conflict with Windows device names.

## Evaluation notes (flywheel)

- Failure modes observed: Windows filesystem reserved names causing Git index failures
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Add a CI check that blocks reserved filenames on PR.
