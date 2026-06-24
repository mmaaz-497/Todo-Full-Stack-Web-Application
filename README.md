# TaskFlow - AI-Powered Todo Application

Welcome to TaskFlow, an innovative AI-powered todo application that transforms how you manage your tasks. Simply talk to the chatbot in natural language, and watch as your tasks are created, managed, and organized automatically.

A multi-phase Todo project (Phase II → Phase IV → Phase V) that can run as:

- **Workflow A: Docker Compose (local dev)** — quick start using `backend/docker-compose.yml`
- **Workflow B: Kubernetes (Phase V microservices)** — event-driven stack using `k8s/`, `charts/`, and `services/`

## Table of contents

- [What’s included](#whats-included)
- [Repository structure (folders only)](#repository-structure-folders-only)
- [Architecture summary](#architecture-summary)
- [Services](#services)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Deployment](#deployment)
- [Workflow A: Run locally (Docker Compose)](#workflow-a-run-locally-docker-compose)
- [Workflow B: Run locally (Minikube / Phase V)](#workflow-b-run-locally-minikube--phase-v)
- [Cloud deployments](#cloud-deployments)
- [Environment configuration](#environment-configuration)
- [Specs (Phase II / IV / V)](#specs-phase-ii--iv--v)
- [Security notes](#security-notes)

---

## Features

- 🤖 **Natural Language Processing**: Talk to the AI chatbot in plain English to create and manage tasks
- 🔐 **Secure Authentication**: Powered by Better Auth for secure user management
- 💬 **Smart Chat Interface**: Intuitive chat interface that understands your requests
- 📱 **Responsive Design**: Works seamlessly across desktop and mobile devices
- 🎨 **Modern UI**: Built with Tailwind CSS for a beautiful, responsive interface
- 🚀 **Fast Performance**: Optimized for speed and reliability
- 🔄 **Event-Driven Architecture**: Built with Kafka for asynchronous processing
- 🏗️ **Dapr Integration**: Distributed Application Runtime for portability
- ☸️ **Kubernetes Deployment**: Scalable container orchestration
- 📊 **Advanced Features**: Recurring tasks, priorities, tags, search & filtering

## Tech Stack

- **Frontend**: Next.js 14, React, TypeScript
- **Backend**: FastAPI, Python, Model Context Protocol (MCP)
- **Database**: Neon PostgreSQL
- **Authentication**: Better Auth
- **AI Integration**: OpenAI GPT
- **Message Queue**: Apache Kafka (via Strimzi/Redpanda)
- **Distributed Runtime**: Dapr (Distributed Application Runtime)
- **Orchestration**: Kubernetes (Minikube/AKS/GKE/OKE)
- **Styling**: Tailwind CSS
- **Deployment**: Vercel (Frontend), Container Orchestration (Backend)

## Deployment

### Backend (free tier — Hugging Face Spaces)
See [Backend Deployment Guide](docs/BACKEND_DEPLOYMENT.md) and the step-by-step
[Hugging Face Deployment Guide](docs/HUGGINGFACE_DEPLOYMENT.md). A ready-made Space
config ships at `backend/api-service/README_HF_SPACE.md`. Koyeb/Render work too
(see the guides).

### Frontend
Deployed on Vercel. Set `NEXT_PUBLIC_API_URL` to your deployed backend URL.

### Local Development (Minikube)
See [Minikube Deployment Guide](docs/MINIKUBE_DEPLOYMENT.md)

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
- Kubernetes manifests in `k8s/` (deployments, Dapr components, Kafka, production)
- Kafka consumer services in `services/`
- Helm chart in `charts/todo-app/`

### Docs + SDD
- Cloud deployment guide in `docs/`
- SDD artifacts per phase in `specs/`
- ADRs + prompt history in `history/`

---

## Repository structure (folders only)

- `backend/` — backend services + `docker-compose.yml` for local dev
- `frontend/` — Next.js frontend
- `k8s/` — Kubernetes manifests (deployments, Dapr components, Kafka, production)
- `services/` — Kafka consumer services (recurring-task, notification, audit)
- `charts/` — Helm chart (`todo-app`)
- `docs/` — documentation (backend + Minikube deployment guides)
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
- Advanced features: recurring tasks, priorities, tags, search & filtering
- Consumer services: recurring task, notification, audit services
- Event-driven architecture with real-time processing

---

## Advanced Features (Phase V)

### 1. Recurring Tasks
- Create recurring tasks with daily, weekly, or monthly patterns
- Automatic generation of next occurrence when completed
- Parent-child relationship tracking

### 2. Task Priorities
- Set task priorities: low, medium, high, urgent
- Priority-based filtering and sorting

### 3. Tags System
- Add multiple tags to tasks for categorization
- Search and filter by tags
- Tag-based organization

### 4. Advanced Search & Filtering
- Search by text in title/description
- Filter by status, priority, tags, due date
- Sort by creation date, due date, priority
- Combined filter operations

### 5. Event-Driven Architecture
- All task operations publish events to Kafka
- Consumer services process events asynchronously
- Real-time updates via WebSocket service
- Audit trail for all operations

### 6. Dapr Integration
- Pub/Sub for Kafka abstraction
- State management for conversation history
- Service invocation for inter-service communication
- Secrets management for credentials
- Jobs API for scheduled reminders

## Services

### Backend (`backend/`)
- `backend/api-service/` — FastAPI REST API (tasks + chat + search/filter)
- `backend/auth-service/` — Better Auth (Node) for authentication/sessions
- `backend/recurring-task-service/` — recurring task processing (Phase V)
- `backend/notification-service/` — SMTP notifications (Phase V)
- `backend/audit-service/` — audit logging (Phase V)
- `backend/websocket-sync-service/` — real-time sync (Phase V)
- `backend/reminder-agent/` — reminder worker (legacy/alternative)

### Consumer Services (`services/`)
- `services/recurring-task-service/` — Kafka consumer for recurring task processing
- `services/notification-service/` — Kafka consumer for sending email notifications
- `services/audit-service/` — Kafka consumer for audit logging

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

Kubernetes manifests live in `k8s/` and the Helm chart in `charts/todo-app/`.
See the Minikube guide for the full local cluster walkthrough.

References:
- Minikube guide: `docs/MINIKUBE_DEPLOYMENT.md`
- Helm chart: `charts/todo-app/`

---

## Cloud deployments

### Backend (free tier)
For a quick, free backend deploy (no Kubernetes) on Hugging Face Spaces, see the
[Hugging Face Deployment Guide](docs/HUGGINGFACE_DEPLOYMENT.md) (overview in the
[Backend Deployment Guide](docs/BACKEND_DEPLOYMENT.md)).

### Local Kubernetes (Minikube)
Use:
- [Minikube Deployment Guide](docs/MINIKUBE_DEPLOYMENT.md)

It covers:
- Local cluster setup
- Kafka deployment with Strimzi
- Dapr configuration
- Service deployment and testing

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

## Roadmap

- [x] Natural language task management (Phase I-IV)
- [x] Event-driven architecture with Kafka (Phase V)
- [x] Dapr integration for portability (Phase V)
- [x] Kubernetes deployment with Minikube (Phase V)
- [x] Cloud deployment (Phase V)
- [x] Advanced features: recurring tasks, priorities, tags (Phase V)
- [x] Consumer services: recurring task, notification, audit (Phase V)
- [ ] Real-time WebSocket synchronization
- [ ] Advanced analytics and insights
- [ ] Mobile app development
- [ ] Integration with calendar apps
- [ ] Voice input support
- [ ] Machine learning for task recommendations

## License

TBD
