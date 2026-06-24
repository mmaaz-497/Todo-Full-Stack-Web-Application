---
title: TaskFlow Auth
emoji: 🔐
colorFrom: green
colorTo: blue
sdk: docker
app_port: 3001
pinned: false
---

# TaskFlow Auth Service (Better Auth + Hono)

Authentication backend for TaskFlow. Issues and validates Bearer tokens
(Better Auth `bearer()` plugin). The frontend signs in here; the API service
validates sessions against `/api/auth/get-session`.

Runs the compiled `dist/` (Node 20). Listens on `$PORT` (Hugging Face sets it),
falling back to 3001.

- Health: `/health`
- Auth routes: `/api/auth/*`

## Configuration (Space → Settings → Variables and secrets)

| Secret               | Notes                                                              |
|----------------------|--------------------------------------------------------------------|
| `DATABASE_URL`       | Same Neon Postgres URL as the API (`...?sslmode=require`)          |
| `BETTER_AUTH_SECRET` | Shared secret. The API's `AUTH_SECRET` must equal this.            |
| `BETTER_AUTH_URL`    | This Space's own public URL (e.g. `https://you-taskflow-auth.hf.space`) |
| `CORS_ORIGINS`       | Comma-separated allowed origins = your Vercel frontend URL. Also used as `trustedOrigins`. |
| `NODE_ENV`           | `production` (enables secure cookies)                              |

> **Usage note:** When deploying this folder to a Space, rename this file to
> `README.md` in the Space repo. Push the whole `auth-service` folder, including
> the committed `dist/` (the Dockerfile runs `node dist/index.js`).
