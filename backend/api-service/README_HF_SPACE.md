---
title: TaskFlow API
emoji: 🚀
colorFrom: indigo
colorTo: purple
sdk: docker
app_port: 8000
pinned: false
---

# TaskFlow API (FastAPI) + Reminder Worker

Backend for the TaskFlow AI todo app. This Space runs **two processes** in one
container (see `start.sh`):

1. **API** — the FastAPI app (tasks, AI chat, search) on port 8000.
2. **Reminder worker** — polls Neon for due tasks and emails reminders via SMTP
   (bundled in `reminder_worker/`). No Kafka/Dapr needed.

It talks to the **auth-service** Space for login/session validation, and to
**Neon Postgres** for data.

- Health: `/health`
- Docs:   `/docs`

## Configuration (Space → Settings → Variables and secrets)

**API + auth**
| Secret               | Notes                                                        |
|----------------------|--------------------------------------------------------------|
| `DATABASE_URL`       | Neon Postgres URL (`...?sslmode=require`)                     |
| `OPENAI_API_KEY`     | `sk-...` (AI chat)                                            |
| `BETTER_AUTH_URL`    | URL of the **auth-service Space** (e.g. `https://you-taskflow-auth.hf.space`) |
| `USE_DAPR_INVOCATION`| `false` (no Dapr here — call auth-service over HTTP)          |
| `AUTH_SECRET`        | Same value as the auth-service's `BETTER_AUTH_SECRET`        |
| `AUTH_ISSUER`        | Better Auth issuer (the auth-service Space URL)             |
| `CORS_ORIGINS`       | Your Vercel origin, e.g. `https://your-app.vercel.app`       |

**Reminder worker** (required for reminders to send)
| Secret                     | Notes                                              |
|----------------------------|----------------------------------------------------|
| `GEMINI_API_KEY`           | Used to generate reminder email text               |
| `SMTP_HOST`                | e.g. `smtp.gmail.com`                               |
| `SMTP_PORT`                | e.g. `587`                                          |
| `SMTP_USER`                | SMTP username                                      |
| `SMTP_PASSWORD`            | SMTP app password                                  |
| `SENDER_EMAIL`             | From-address for reminder emails                   |
| `APP_URL`                  | Your frontend URL (used for links in emails)       |
| `POLLING_INTERVAL_MINUTES` | optional, default `5`                              |

**Common**: `ENVIRONMENT=production`, `OPENAI_MODEL_NAME=gpt-4o-mini` (optional).

> If the reminder env vars are missing, the worker exits on startup and the API
> keeps serving normally (you just won't get reminder emails).
>
> **Usage note:** When deploying this folder to a Space, rename this file to
> `README.md` in the Space repo (Hugging Face reads the YAML frontmatter above).
