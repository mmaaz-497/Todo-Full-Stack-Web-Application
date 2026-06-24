# Deploy the Backend to Hugging Face Spaces (Free)

This guide deploys the full working backend — **authentication, the API, and the
email-reminder system** — free on Hugging Face Spaces, connected to your existing
Vercel frontend and a Neon Postgres database.

The Phase V Kafka/Dapr/Kubernetes services are intentionally **out of scope** (they
need paid infra). Everything users actually touch — login, tasks, AI chat, and
scheduled reminder emails — works without them.

---

## Architecture

A Hugging Face Space = **one Docker container, one web port**. So you create **two
Spaces** (auth is Node, API is Python — different runtimes):

```
  Vercel frontend ──► Space #1  auth-service   (Node,   port 3001)
        │         └─► Space #2  api-service    (Python, port 8000)
        │                         └─ reminder worker (polls Neon ─► SMTP)
        └──────────────────────────► both Spaces send Bearer tokens
                 Neon Postgres  ◄── shared by both Spaces
```

- **Reminders run inside Space #2** as a second process (`start.sh` launches the
  API and the reminder worker together). Hugging Face free Spaces stay **awake**,
  so the 5-minute polling loop keeps running — that's why we use HF, not Render
  (whose free tier sleeps).
- **Auth is Bearer-token based**, so the three different domains (Vercel + 2×hf.space)
  do **not** hit cross-site cookie problems.

---

## Prerequisites

- A **Hugging Face account** + a **write access token**
  (https://huggingface.co/settings/tokens) — used as the git password when pushing.
- **git** installed locally.
- A **Neon Postgres** database (free) and its pooled connection string
  (`...?sslmode=require`).
- **OpenAI API key** (AI chat) and **Gemini API key** (reminder email text).
- **SMTP** credentials (e.g. a Gmail account + app password) for sending reminders.
- Pick one shared **auth secret** now (any long random string). You'll set it as
  `BETTER_AUTH_SECRET` on auth and `AUTH_SECRET` on the API — they must match.

---

## Step 1 — Deploy the auth-service (Space #1)

1. Create the Space: **https://huggingface.co/new-space** → SDK **Docker** →
   **Blank** → Hardware **CPU basic (free)** → name e.g. `taskflow-auth`.

2. Put the service into the Space repo:
   ```bash
   git clone https://huggingface.co/spaces/<you>/taskflow-auth
   cd taskflow-auth
   cp -r /path/to/Todo-Full-Stack-Web-Application/backend/auth-service/. .
   mv README_HF_SPACE.md README.md      # HF reads this for the Docker config
   ```
   Keep the committed `dist/` folder — the image runs `node dist/index.js`.

3. In the Space UI → **Settings → Variables and secrets**, add:

   | Secret               | Value                                                        |
   |----------------------|--------------------------------------------------------------|
   | `DATABASE_URL`       | your Neon string                                             |
   | `BETTER_AUTH_SECRET` | your chosen shared secret                                    |
   | `CORS_ORIGINS`       | your Vercel URL, e.g. `https://your-app.vercel.app`          |
   | `NODE_ENV`           | `production`                                                 |
   | `BETTER_AUTH_URL`    | leave for now; set after first build (see step 5)            |

4. Push to build:
   ```bash
   git add -A && git commit -m "Deploy TaskFlow auth-service" && git push
   ```

5. When the build finishes, note the Space URL, e.g.
   `https://<you>-taskflow-auth.hf.space`. Set **`BETTER_AUTH_URL`** to that exact
   URL (Settings → secrets), which restarts the Space.

6. Verify: open `https://<you>-taskflow-auth.hf.space/health` → `{"status":"ok",...}`.

---

## Step 2 — Deploy the api-service + reminders (Space #2)

1. Create another Docker/Blank/free Space, e.g. `taskflow-api`.

2. Put the service into the Space repo:
   ```bash
   git clone https://huggingface.co/spaces/<you>/taskflow-api
   cd taskflow-api
   cp -r /path/to/Todo-Full-Stack-Web-Application/backend/api-service/. .
   mv README_HF_SPACE.md README.md
   ```
   This folder already includes `reminder_worker/` and `start.sh` (runs the API +
   reminder worker together).

3. Add secrets (Settings → Variables and secrets):

   **API + auth**
   | Secret                | Value                                                    |
   |-----------------------|----------------------------------------------------------|
   | `DATABASE_URL`        | same Neon string                                         |
   | `OPENAI_API_KEY`      | `sk-...`                                                  |
   | `BETTER_AUTH_URL`     | the auth Space URL from Step 1                            |
   | `USE_DAPR_INVOCATION` | `false`                                                  |
   | `AUTH_SECRET`         | the **same** value as auth's `BETTER_AUTH_SECRET`        |
   | `AUTH_ISSUER`         | the auth Space URL                                       |
   | `CORS_ORIGINS`        | your Vercel URL                                          |
   | `ENVIRONMENT`         | `production`                                             |

   **Reminders**
   | Secret                     | Value                              |
   |----------------------------|------------------------------------|
   | `GEMINI_API_KEY`           | your Gemini key                    |
   | `SMTP_HOST`                | e.g. `smtp.gmail.com`              |
   | `SMTP_PORT`                | `587`                              |
   | `SMTP_USER`                | SMTP username                      |
   | `SMTP_PASSWORD`            | SMTP app password                  |
   | `SENDER_EMAIL`             | from-address                       |
   | `APP_URL`                  | your Vercel URL (for email links)  |
   | `POLLING_INTERVAL_MINUTES` | optional, default `5`              |

4. Push:
   ```bash
   git add -A && git commit -m "Deploy TaskFlow api-service + reminders" && git push
   ```

5. Verify when live (`https://<you>-taskflow-api.hf.space`):
   - `/health` → `{"status":"healthy",...}`
   - `/docs` loads
   - In the **Logs** tab you should see the worker line `⏰ Scheduler started (every 5 min)`.

---

## Step 3 — Wire the frontend (Vercel)

In Vercel → your frontend project → **Settings → Environment Variables**:

```
NEXT_PUBLIC_AUTH_URL = https://<you>-taskflow-auth.hf.space
NEXT_PUBLIC_API_URL  = https://<you>-taskflow-api.hf.space
```

**Redeploy** the frontend (these are build-time vars). Make sure `CORS_ORIGINS` on
both Spaces equals your exact Vercel origin (scheme + host, no trailing slash).

---

## Step 4 — Verify the whole flow

1. **Sign up / log in** on the frontend → should succeed (hits auth Space).
2. **Create a task**, open the chat, create tasks by AI → should persist (API Space).
3. **Reminder test:** create a task with a `due_date` a few minutes out and a
   `reminder_time` within the next few minutes. Within one polling cycle
   (≤ `POLLING_INTERVAL_MINUTES`), the worker emails `SENDER_EMAIL` → the task
   owner. Watch the API Space **Logs** for `✅ Reminder sent`.

---

## Database notes

- Both Spaces use the **same Neon DB**. On startup each creates any missing tables
  it owns (`tasks`, `conversations`, … for the API; `reminder_log`, `agent_state`
  for the worker). The `user` table comes from auth-service.
- No destructive migrations are run. If reusing an older DB, apply the SQL in
  `backend/api-service/migrations/` once.
- Use a **pooled** Neon string with `?sslmode=require`.

---

## Troubleshooting

- **Login fails / 401 on API calls** — `AUTH_SECRET` (API) must equal
  `BETTER_AUTH_SECRET` (auth); `BETTER_AUTH_URL` + `AUTH_ISSUER` on the API must be
  the auth Space URL; `USE_DAPR_INVOCATION=false`.
- **CORS errors in the browser** — `CORS_ORIGINS` on **both** Spaces must match the
  Vercel origin exactly. Redeploy the frontend after changing `NEXT_PUBLIC_*`.
- **No reminder emails** — check the API Space Logs: if the worker process exited,
  a reminder env var is missing (`GEMINI_API_KEY`, `SMTP_*`, `SENDER_EMAIL`,
  `APP_URL`, `DATABASE_URL`). Also confirm the task has a `reminder_time` set and is
  not completed, and that the reminder time is within the polling window.
- **Build fails on auth** — ensure the committed `dist/` folder was pushed (it is not
  git-ignored).

---

## Alternatives

- **Koyeb** (free, Docker): same images and env vars; set the work dir per service.
- **Render** (free, Docker): works, but the free tier **sleeps** after ~15 min idle,
  which stalls the reminder poller — prefer Hugging Face for always-on reminders.
