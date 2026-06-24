# Backend Deployment (Free Tier)

This guide deploys the **API service** (`backend/api-service`) as a single FastAPI
web service on a free host. The frontend is already deployed (Vercel); this
connects the backend to it.

The API runs fine as a **monolith** without Kafka/Dapr/Kubernetes — event
publishing degrades gracefully (it just logs and continues). You only need:

- A **Neon Postgres** database (free) — `DATABASE_URL`
- An **OpenAI API key** — `OPENAI_API_KEY`
- Better Auth secrets shared with the frontend — `AUTH_SECRET`, `AUTH_ISSUER`

---

## Recommended: Hugging Face Spaces (free, always-on)

Hugging Face builds the existing `backend/api-service/Dockerfile` and keeps the
service **awake** on the free tier (no cold-start sleep). It's the best default
for a demo you want reachable at any time.

➡️ **Full walkthrough: [Hugging Face Deployment Guide](HUGGINGFACE_DEPLOYMENT.md)**

A ready-made Space config (with the required `sdk: docker` / `app_port: 8000`
frontmatter) ships at `backend/api-service/README_HF_SPACE.md` — rename it to
`README.md` inside the Space repo.

---

## Alternatives

- **Koyeb** (free nano service, Docker): create a service from this repo, set the
  work dir to `backend/api-service`, the run command to
  `uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1`, and add the same env
  vars. Does not sleep aggressively.
- **Render** (free Docker web service): also works, but the free tier spins down
  after ~15 min idle and cold-starts in ~30–60s. Same start command and env vars.
- **Fly.io / Railway**: capable but require a credit card / consume trial credits.

All of them need the same env vars and the same start command. Only Hugging Face
has a checked-in config (`README_HF_SPACE.md`); the others are
dashboard-configured.

---

## Database notes

- On startup the app calls `create_db_and_tables()`, which **creates missing
  tables** in your Neon DB automatically.
- It does **not** run `ALTER`-style migrations. If you reuse an existing DB that
  predates the advanced-feature columns, apply the SQL in
  `backend/api-service/migrations/` once (e.g. `psql "$DATABASE_URL" -f <file>`).
- Use a **pooled** Neon connection string and keep `?sslmode=require`.

## Connect the frontend

In Vercel, set `NEXT_PUBLIC_API_URL` to the deployed backend URL and redeploy.
Make sure `CORS_ORIGINS` on the backend exactly matches the frontend origin
(scheme + host, no trailing slash). Multiple origins are comma-separated.

## Required env vars (reference)

These are read by `backend/api-service/app/config.py` and `main.py`:

| Variable            | Required | Default        | Notes                                  |
|---------------------|----------|----------------|----------------------------------------|
| `DATABASE_URL`      | yes      | —              | Neon Postgres URL                      |
| `OPENAI_API_KEY`    | yes      | —              | Used by the AI chat agent              |
| `AUTH_SECRET`       | yes      | —              | Must match the frontend                |
| `AUTH_ISSUER`       | yes      | —              | Better Auth issuer                     |
| `CORS_ORIGINS`      | no\*     | `http://localhost:3000` | \*Set to your frontend origin |
| `OPENAI_MODEL_NAME` | no       | `gpt-4o-mini`  | Chat model                             |
| `ENVIRONMENT`       | no       | `development`  | Set to `production`                    |
