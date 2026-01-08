# Todo Full-Stack Web Application

A multi-phase Todo project (Phase II → Phase IV → Phase V) that can run as:

- **Workflow A: Docker Compose (local dev)** — quick start using `backend/docker-compose.yml`
- **Workflow B: Kubernetes (Phase V microservices)** — event-driven stack using `phase-v/`, `charts/`, and `kubernetes/`

## Table of contents

- [What’s included](#whats-included)
- [Repository structure (folders only)](#repository-structure-folders-only)
- [Architecture summary](#architecture-summary)
- [Services](#services)
- [Workflow A: Run locally (Docker Compose)](#workflow-a-run-locally-docker-compose)
- [Workflow B: Run locally (Minikube / Phase V)](#workflow-b-run-locally-minikube--phase-v)
- [Cloud deployments](#cloud-deployments)
- [Environment configuration](#environment-configuration)
- [Specs (Phase II / IV / V)](#specs-phase-ii--iv--v)
- [Security notes](#security-notes)

---

## What’s included

### Frontend
- **Next.js + TypeScript + Tailwind** UI in `frontend/`

### Backend
Multiple backend services in `backend/`:
- FastAPI services (Python)
- Better Auth service (Node)
- Worker services (Python/Node)

### Kubernetes / Cloud assets
- Phase V deployment assets in `phase-v/`
- Helm charts in `charts/`
- Cluster-wide add-ons/configs in `kubernetes/`

### Docs + SDD
- Cloud deployment guide in `docs/`
- SDD artifacts per phase in `specs/`
- ADRs + prompt history in `history/`

---

## Repository structure (folders only)

- `backend/` — backend services + `docker-compose.yml` for local dev
- `frontend/` — Next.js frontend
- `phase-v/` — Phase V scripts, Kubernetes manifests, Dapr components, and phase docs
- `charts/` — Helm charts (backend/frontend and consolidated)
- `kubernetes/` — monitoring + dapr-config (cluster-wide)
- `docs/` — documentation (cloud Kubernetes guide)
- `specs/` — phase specs/plans/tasks
- `history/` — ADRs + prompt history records

---

## Architecture summary

### Workflow A (Docker Compose)
A fast local dev stack:
- PostgreSQL
- API service (FastAPI)
- Auth service (Better Auth)
- Reminder agent (worker)

### Workflow B (Phase V / Kubernetes)
An event-driven microservices architecture:
- Kubernetes (Minikube locally, AKS/GKE/OKE in cloud)
- Dapr (pub/sub, state, secrets, jobs, invocation)
- Kafka (Strimzi locally; cloud Kafka supported)
- PostgreSQL

---

## Services

### Backend (`backend/`)
- `backend/api-service/` — FastAPI REST API (tasks + chat + search/filter)
- `backend/auth-service/` — Better Auth (Node) for authentication/sessions
- `backend/recurring-task-service/` — recurring task processing (Phase V)
- `backend/notification-service/` — SMTP notifications (Phase V)
- `backend/audit-service/` — audit logging (Phase V)
- `backend/websocket-sync-service/` — real-time sync (Phase V)
- `backend/reminder-agent/` — reminder worker (legacy/alternative)

### Frontend (`frontend/`)
- Next.js app with auth screens + tasks UI

---

## Workflow A: Run locally (Docker Compose)

### Prerequisites
- Docker Desktop
- Node.js 18+

### 1) Start backend

```bash
cd backend
cp .env.example .env
# edit backend/.env with your real values

docker-compose up -d
```

Expected endpoints:
- API health: http://localhost:8000/health
- API docs: http://localhost:8000/docs
- Auth: http://localhost:3001

### 2) Start frontend

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

Open: http://localhost:3000

---

## Workflow B: Run locally (Minikube / Phase V)

### Prerequisites
- Docker Desktop
- kubectl
- helm
- minikube
- dapr CLI

### Deploy

```bash
bash phase-v/deploy-local.sh
```

References:
- Phase V Kubernetes guide: `phase-v/KUBERNETES_DEPLOYMENT_GUIDE.md`
- Phase V summary: `phase-v/PHASE_V_COMPLETE.md`

---

## Cloud deployments

### Cloud Kubernetes (AKS / GKE / OKE)
Use:
- `docs/CLOUD_DEPLOYMENT.md`

It covers:
- Cluster creation
- Kafka (Redpanda Cloud) setup
- Dapr install (mTLS)
- Helm deployment + ingress + TLS

### DigitalOcean (Paid)
- `DIGITALOCEAN_DEPLOYMENT.md`
- `DEPLOYMENT_QUICKSTART.md`
- `deploy-digitalocean.sh`

---

## Environment configuration

Templates:
- Root template: `.env.example`
- Backend template: `backend/.env.example`
- Frontend template: `frontend/.env.example`

Typical local values (example):
- Frontend: `NEXT_PUBLIC_API_URL=http://localhost:8000`, `NEXT_PUBLIC_AUTH_URL=http://localhost:3001`
- Backend: `DATABASE_URL`, auth secrets, SMTP, AI keys (if enabled)

---

## Specs (Phase II / IV / V)

This repo keeps requirements and plans in `specs/`:

- Phase II: `specs/phase-ii-full-stack-web-app/`
- Phase IV: `specs/phase-iv-kubernetes-deployment/`
- Phase V: `specs/002-phase-v-cloud-deployment/`

---

## Security notes

- Do **not** commit secrets (API keys, DB URLs, SMTP passwords).
- Store secrets in `.env` / `.env.local` (ignored by git) or Kubernetes Secret templates.

## License

TBD
