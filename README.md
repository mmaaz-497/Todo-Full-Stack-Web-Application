# Todo Full-Stack Web Application (Phase V)

A **cloud-native, event-driven Todo application** built with a Next.js frontend and multiple backend microservices. Phase V evolves the project into a Kubernetes + Dapr + Kafka architecture with real-time sync, recurring tasks, reminders, and audit logging.

## Repository Layout (Root Folders)

- `backend/` — Backend services source code (FastAPI + Node)
  - `backend/api-service/` (FastAPI) — main REST API
  - `backend/auth-service/` (Node/Better Auth) — auth service
  - `backend/recurring-task-service/` (FastAPI) — recurring tasks processor
  - `backend/notification-service/` (FastAPI) — SMTP notifications
  - `backend/audit-service/` (FastAPI) — audit log consumer/query API
  - `backend/websocket-sync-service/` (Node) — real-time sync service
  - `backend/reminder-agent/` — reminder agent implementation (legacy/alternative)
- `frontend/` — Next.js frontend (`npm run dev`)
- `phase-v/` — Phase V Kubernetes manifests, Dapr components, and deployment scripts
- `charts/` — Helm charts (multiple variants)
- `kubernetes/` — cluster-wide configs (monitoring, dapr-config)
- `docs/` — extra documentation (e.g., cloud deployment)
- `specs/` — Spec-Driven Development artifacts (spec/plan/tasks)
- `history/` — ADRs + Prompt History Records (PHRs)

## Architecture (Phase V)

**Core stack:**
- **Frontend:** Next.js (`frontend/`)
- **Backend:** microservices (FastAPI + Node)
- **Orchestration:** Kubernetes
- **Service runtime:** Dapr (pub/sub, state, secrets, jobs, invocation)
- **Event backbone:** Kafka (Strimzi locally; cloud Kafka supported)
- **Database:** PostgreSQL

High-level flow (see `phase-v/PHASE_V_COMPLETE.md:24`):
- API Service publishes events (task-events, reminders, task-updates)
- Worker services consume events (recurring generation, notifications, audit)
- WebSocket service broadcasts real-time updates

## Quick Start (Local)

### Option A — Fast Local Dev (Docker Compose)

Runs **PostgreSQL + api-service + auth-service + reminder-agent** locally.

```bash
cd backend
# configure env vars in backend/.env or export them
docker-compose up -d
```

Services:
- API: http://localhost:8000 (docs: /docs)
- Auth: http://localhost:3001

### Option B — Phase V Local Kubernetes (Minikube)

This deploys **Kafka + PostgreSQL + Dapr + all microservices**.

```bash
# from repo root
bash phase-v/deploy-local.sh
```

After install, see the script output for hosts-file entries and URLs.

## Deployment

### DigitalOcean (Paid)

- Full guide: `DIGITALOCEAN_DEPLOYMENT.md`
- Quick start: `DEPLOYMENT_QUICKSTART.md`
- Script: `deploy-digitalocean.sh`

### Multi-cloud Kubernetes (AKS/GKE/OKE)

See `docs/CLOUD_DEPLOYMENT.md` and the spec tasks in:
- `specs/002-phase-v-cloud-deployment/tasks.md`

## Environment Variables

See `.env.example` for the current full set. Common ones include:
- `DATABASE_URL`
- `JWT_SECRET_KEY`
- `BETTER_AUTH_SECRET`
- `OPENAI_API_KEY`
- `SMTP_*`
- `KAFKA_BOOTSTRAP_SERVERS`

## Helm Charts

Charts live in `charts/`:
- `charts/todo-app/` — consolidated app chart
- `charts/todo-chatbot-backend/` — backend-focused chart
- `charts/todo-chatbot-frontend/` — frontend chart

## Specs & History

- Specs: `specs/` (Phase II, IV, V, and other features)
- ADRs: `history/adr/`
- Prompt History Records (PHR): `history/prompts/`

## Notes / Known Inconsistencies

- `phase-v/services/` contains service templates/docs; the active service implementations live under `backend/`.
- Some docs may describe earlier phases; Phase V is the current target for Kubernetes/cloud deployment.

## License

TBD
