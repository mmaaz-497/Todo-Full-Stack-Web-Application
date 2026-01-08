# Phase IV Research & Decisions

**Feature:** phase-iv-kubernetes-deployment
**Date:** 2025-12-30
**Stage:** Phase 0 - Research

---

## Overview

This document captures research findings and architectural decisions made during Phase IV planning. All decisions resolve open questions from the specification phase and provide rationale for implementation choices.

---

## 1. Database Deployment Strategy

### Decision
**Use external Neon Serverless PostgreSQL (no in-cluster deployment)**

### Rationale
- Phase III already uses Neon Serverless PostgreSQL successfully
- External database eliminates resource consumption within 4GB Minikube RAM limit
- Avoids complexity of StatefulSets, persistent volumes, and database initialization
- Maintains production-like external dependency pattern
- Simplifies disaster recovery (database state persists independently of Kubernetes cluster)

### Implementation Implications
- Backend services connect to Neon via `DATABASE_URL` environment variable
- `DATABASE_URL` stored in Kubernetes Secret (not ConfigMap)
- No PostgreSQL Deployment/StatefulSet required in Helm charts
- Network connectivity: Backend pods → Internet → Neon (requires Minikube DNS and egress)
- Connection pooling configuration remains in application code (no PgBouncer sidecar needed)

### Alternatives Considered
- **In-cluster PostgreSQL StatefulSet:** Rejected due to resource constraints (1GB+ RAM for PostgreSQL), added complexity of persistent storage, and lack of learning value (external database more production-like)
- **PostgreSQL Docker container outside Kubernetes:** Rejected due to network complexity (Minikube → host networking)

---

## 2. Frontend-Backend Communication Strategy

### Decision
**NodePort from browser (client-side API calls)**

### Rationale
- Simplest approach for local development/learning environment
- Frontend JavaScript makes HTTP requests directly to `http://<minikube-ip>:30081` (backend NodePort)
- Avoids complexity of Ingress controllers or server-side proxying
- Aligns with Phase IV scope (basic deployment, not production hardening)
- Explicit about Minikube networking concepts (NodePort service exposure)

### Implementation Implications
- **Frontend environment variable:** `NEXT_PUBLIC_API_URL=http://<minikube-ip>:30081`
  - Must be injected at Docker build time (ARG in Dockerfile)
  - Or dynamically loaded via Next.js runtime config
- **Backend Service:** NodePort type, static nodePort 30081
- **CORS configuration:** Backend must allow requests from `http://<minikube-ip>:30080` (frontend NodePort)
- **Browser access:** Users access frontend at `http://<minikube-ip>:30080`

### Alternatives Considered
- **Server-side proxy (Next.js API routes):** Rejected for Phase IV simplicity. Would require:
  - Next.js API route: `/pages/api/proxy/[...path].ts`
  - Server-side fetch to `http://backend-service:3001` (Service DNS)
  - More production-like but adds complexity
  - Can be implemented in future phase if needed
- **Ingress controller:** Out of scope for Phase IV (requires NGINX Ingress, cert-manager for TLS)

### Known Limitations
- Not production-ready (Ingress with TLS would be used in production)
- Minikube IP changes on cluster restart (requires frontend rebuild or runtime config)
- CORS must be explicitly configured (browser security)

---

## 3. Health Endpoint Availability

### Decision
**Backend API service has `/health` endpoint; Frontend will use default Next.js behavior**

### Research Findings

**Backend API Service (Python FastAPI):**
- **Endpoint:** `GET /health`
- **Location:** `backend/api-service/routes/health.py`
- **Behavior:**
  - Tests database connection with `SELECT 1` query
  - Returns `200 OK` with `{"status": "healthy", "message": "..."}` if healthy
  - Returns `503 Service Unavailable` if database connection fails
- **Status:** ✅ EXISTS - Ready for Kubernetes health probes

**Auth Service (Node.js/Hono):**
- **Endpoint:** `GET /health`
- **Location:** `backend/auth-service/dist/index.js:23-25`
- **Behavior:**
  - Returns `200 OK` with `{"status": "ok", "service": "auth-service", "timestamp": "..."}`
  - Simple availability check (no database connection test)
- **Status:** ✅ EXISTS - Ready for Kubernetes health probes
- **Note:** Already has a Dockerfile (basic, needs optimization for multi-stage production build)

**Reminder Agent (Python Background Job):**
- **Type:** AsyncIOScheduler background processor (NOT a web server)
- **Architecture:** Periodic job that polls database for due reminders
- **No HTTP Server:** Does not expose HTTP endpoints
- **Status:** ⚠️ NO HEALTH ENDPOINT (not applicable)
- **Kubernetes Deployment Strategy:**
  - Deploy as Kubernetes Job or CronJob (not Deployment with HTTP probes)
  - Use startup success as health indicator
  - Monitor job completion status via `kubectl get jobs`
  - No liveness/readiness probes needed (job-based workload)
- **Alternative:** If HTTP health check required, add minimal FastAPI server on separate port:
  ```python
  # Optional: Add to main.py if HTTP health check needed
  from fastapi import FastAPI
  import uvicorn

  health_app = FastAPI()

  @health_app.get("/health")
  async def health():
      return {"status": "ok"}

  # Run on port 8000 in separate thread
  ```
  **Decision:** NOT adding HTTP server for Phase IV (keep as background job)

**Frontend (Next.js):**
- **Status:** ❌ NO CUSTOM ENDPOINT
- **Decision:** Use default Next.js root path `/` for health checks
- **Rationale:** Next.js automatically serves pages, no custom health endpoint needed for basic deployment
- **Kubernetes Probe Configuration:**
  ```yaml
  livenessProbe:
    httpGet:
      path: /
      port: 3000
  readinessProbe:
    httpGet:
      path: /
      port: 3000
  ```
- **Alternative (if needed):** Create `/pages/api/health.ts` returning `{status: "ok"}`

### Implementation Implications

**Backend API Service (FastAPI):**
- Liveness probe: `GET /health` (tests database connection)
- Readiness probe: `GET /health` (same endpoint)
- Initial delay: 15 seconds (allow database connection pool initialization)
- Period: 10 seconds

**Auth Service:**
- If endpoint exists: Use existing endpoint
- If missing: Create minimal endpoint before containerization
- Liveness/readiness: `GET /health`

**Reminder Agent:**
- If endpoint exists: Use existing endpoint
- If missing: Create minimal endpoint before containerization
- Liveness/readiness: `GET /health`

**Frontend:**
- Liveness probe: `GET /` (default Next.js page)
- Readiness probe: `GET /` (same)
- Initial delay: 10 seconds (allow Next.js server startup)
- Period: 10 seconds

---

## 4. Reminder Agent Technology Stack

### Decision
**Python (consistent with backend API service)**

### Rationale
- Aligns with existing backend API service (Python FastAPI)
- Simplifies Docker base image strategy (same `python:3.11-slim` base)
- Consistent dependency management (requirements.txt)
- Same containerization patterns as API service

### Implementation Implications

**Dockerfile Strategy:**
- Multi-stage build: `deps → builder → runner`
- Base image: `python:3.11-slim`
- Virtual environment: `/opt/venv`
- Non-root user: `appuser`
- Target size: <300MB (similar to FastAPI service)

**Helm Chart Configuration:**
- Group with backend services in umbrella chart
- Resource limits: 512Mi RAM, 500m CPU (same as other backend services)
- Health probe: `GET /health` endpoint
- Environment variables: From ConfigMap and Secrets

**Dependencies:**
- `requirements.txt` for Python packages
- Potential shared dependencies with API service (FastAPI, SQLModel, httpx)

---

## 5. AI DevOps Tooling Availability

### Decision
**AI tools (Gordon, kubectl-ai, Kagent) NOT currently available - Use manual fallback strategy**

### Implications

**Gordon (Docker Desktop AI):**
- **Status:** ❌ NOT AVAILABLE
- **Fallback Strategy:**
  1. Author Dockerfiles manually using official Docker best practices
  2. Reference official Next.js, Node.js, Python Docker examples
  3. Use `hadolint` (Dockerfile linter) for static analysis: `docker run --rm -i hadolint/hadolint < Dockerfile`
  4. Validate with `docker build` and `docker run` locally
  5. Scan for vulnerabilities: `docker scan <image>` or `trivy image <image>`
- **Learning Impact:** Manual Dockerfile authoring teaches fundamentals more deeply than AI generation

**kubectl-ai:**
- **Status:** ❌ NOT AVAILABLE
- **Fallback Strategy:**
  1. Use standard `kubectl` commands with official documentation
  2. Reference Kubernetes cheat sheet: https://kubernetes.io/docs/reference/kubectl/cheatsheet/
  3. Use `kubectl explain` for built-in documentation: `kubectl explain deployment.spec`
  4. Bookmark common commands:
     - Logs: `kubectl logs -f <pod> -n todo-app`
     - Describe: `kubectl describe pod <pod> -n todo-app`
     - Events: `kubectl get events -n todo-app --sort-by='.lastTimestamp'`
     - Exec: `kubectl exec -it <pod> -n todo-app -- /bin/sh`
- **Learning Impact:** Manual kubectl usage builds stronger Kubernetes command literacy

**Kagent:**
- **Status:** ❌ NOT AVAILABLE
- **Fallback Strategy:**
  1. Manual cluster health checks:
     - Node status: `kubectl get nodes`
     - Pod status: `kubectl get pods -A`
     - Resource usage: `kubectl top nodes && kubectl top pods -n todo-app`
     - Events: `kubectl get events -A --sort-by='.lastTimestamp'`
  2. Manual deployment review:
     - Get deployment YAML: `kubectl get deployment <name> -n todo-app -o yaml`
     - Check best practices manually (non-root user, resource limits, probes)
  3. Manual performance diagnostics:
     - Pod logs for errors: `kubectl logs <pod> -n todo-app --tail=100`
     - Describe pod for events: `kubectl describe pod <pod> -n todo-app`
- **Learning Impact:** Manual analysis develops troubleshooting intuition

### Updated Plan Sections

**Phase 1 (Containerization):**
- ~~Use Gordon to generate Dockerfiles~~ → Author Dockerfiles manually using best practices
- ~~Request Gordon optimization~~ → Use `hadolint` and official Docker documentation
- ~~Gordon security recommendations~~ → Manual security checklist (non-root, no secrets, minimal layers)

**Phase 4 (Operations):**
- ~~kubectl-ai natural language queries~~ → Learn standard kubectl commands
- ~~Kagent cluster analysis~~ → Manual health checks and event inspection
- ~~AI-assisted troubleshooting~~ → Manual troubleshooting with kubectl and logs

**Learning Objectives (Updated):**
- ~~Used AI tools to assist operations~~ → Mastered core kubectl commands for operations
- ~~Validated AI tool effectiveness~~ → Built strong manual Kubernetes troubleshooting skills

### Benefits of Manual Approach
- Deeper understanding of Docker and Kubernetes fundamentals
- No dependency on external AI services (fully offline-capable)
- Transferable skills to any Kubernetes environment
- Stronger troubleshooting abilities (not reliant on AI suggestions)

---

## 6. Component Inventory & Health Endpoint Status

Based on codebase exploration, the following components need containerization:

| Component | Technology | Health Endpoint | Status | Kubernetes Workload Type |
|-----------|-----------|-----------------|--------|--------------------------|
| Frontend | Next.js 16 (TypeScript) | `/` (default) | ✅ Ready | Deployment (HTTP probes) |
| Auth Service | Node.js 18 + Hono + Better Auth | `/health` ✅ | ✅ Ready | Deployment (HTTP probes) |
| API Service | Python 3.11 + FastAPI | `/health` ✅ | ✅ Ready | Deployment (HTTP probes) |
| Reminder Agent | Python 3.11 + AsyncIOScheduler | N/A (background job) | ⚠️ Different approach | CronJob or Deployment (no probes) |

**Health Endpoint Summary:**
- ✅ **Auth Service:** `GET /health` exists (returns `{status: "ok", service: "auth-service", timestamp}`)
- ✅ **API Service:** `GET /health` exists (tests database connection, returns `{status: "healthy"}`)
- ✅ **Frontend:** Will use default Next.js `/` route (serves homepage)
- ⚠️ **Reminder Agent:** Background job, no HTTP endpoints (uses CronJob or Deployment without probes)

**Action Items Before Containerization:**
1. ✅ **All health endpoints verified** - No additional endpoints needed
2. ⚠️ **Decide reminder-agent deployment strategy:**
   - **Option A (Recommended):** Deploy as Kubernetes CronJob (runs periodically)
   - **Option B:** Deploy as Deployment without health probes (long-running background process)
   - **Decision:** Use Deployment for Phase IV simplicity (scheduler manages its own intervals)
3. ✅ **Auth Service Dockerfile exists** but needs optimization (currently basic, requires multi-stage production build)
4. **Create Dockerfiles for:** Frontend, API Service, Reminder Agent

---

## 7. Minikube Resource Allocation

### Decision
**2 CPUs, 4GB RAM, 20GB disk**

### Resource Distribution Plan

**System Overhead (Kubernetes Control Plane):**
- Estimated: 1GB RAM, 0.5 CPU
- Includes: kube-apiserver, etcd, kube-scheduler, kube-controller-manager, CoreDNS

**Application Pods (Per-Pod Limits):**
- Frontend: 512Mi RAM, 500m CPU (1 replica)
- Auth Service: 512Mi RAM, 500m CPU (1 replica)
- API Service: 512Mi RAM, 500m CPU (1 replica)
- Reminder Agent: 512Mi RAM, 500m CPU (1 replica)

**Total Application Limits:** 2Gi RAM, 2000m CPU (2 cores)

**Available Headroom:** ~1GB RAM, 0.5 CPU (for burst, monitoring, overhead)

### Monitoring Strategy
- Use `kubectl top nodes` to monitor node resource usage
- Use `kubectl top pods -n todo-app` to monitor pod usage
- Watch for OOMKilled events: `kubectl get events -n todo-app | grep OOM`
- Adjust resource limits if needed (reduce to 256Mi per pod if memory pressure occurs)

---

## 8. Networking & Service Exposure

### Cluster Networking

**Service DNS Resolution:**
- Internal services use Kubernetes DNS: `<service-name>.<namespace>.svc.cluster.local`
- Shortened form within same namespace: `<service-name>`
- Example: Auth service calls API service at `http://api-service:8000`

**NodePort Allocations:**
- Frontend: 30080 (static, user-facing)
- Backend API: 30081 (static, user-facing for direct API access)
- Auth Service: ClusterIP only (internal, not exposed externally)
- Reminder Agent: ClusterIP only (internal, not exposed externally)

**External Access:**
```bash
# Get Minikube IP
minikube ip  # Example: 192.168.49.2

# Access frontend
http://192.168.49.2:30080

# Access backend API (for testing)
http://192.168.49.2:30081/health
http://192.168.49.2:30081/docs  # FastAPI Swagger UI
```

### CORS Configuration

**Backend API CORS Settings:**
```python
# Allow frontend NodePort origin
origins = [
    "http://192.168.49.2:30080",  # Minikube IP (will vary)
    "http://localhost:30080",     # If using minikube tunnel
]
```

**Note:** Minikube IP may change on cluster restart. Consider:
- Using wildcard CORS for local dev: `http://192.168.49.*:30080`
- Or using `minikube tunnel` for stable `localhost` access

---

## 9. Secrets Management Strategy

### Kubernetes Secrets Approach

**Secret Creation Method:**
```bash
# Manual creation (one-time setup)
kubectl create secret generic backend-secrets \
  --from-literal=DATABASE_URL='postgresql://user:pass@neon.tech/db' \
  --from-literal=AUTH_SECRET='your-auth-secret' \
  --from-literal=GEMINI_API_KEY='your-gemini-key' \
  --from-literal=OPENAI_API_KEY='your-openai-key' \
  -n todo-app
```

**Alternative: From .env File**
```bash
# Create from existing .env (sanitized)
kubectl create secret generic backend-secrets \
  --from-env-file=.env.production \
  -n todo-app
```

**Secret Keys (Required):**
- `DATABASE_URL`: Neon PostgreSQL connection string
- `AUTH_SECRET`: Better Auth session signing key
- `GEMINI_API_KEY`: Google Gemini API key (for AI chatbot)
- `OPENAI_API_KEY`: OpenAI API key (if used as fallback)

**Helm Chart Integration:**
- Secrets referenced in Deployment manifests via `secretKeyRef`
- Secrets NOT stored in Helm values.yaml (use `--set` override or pre-create manually)
- Document secret creation in DEPLOYMENT.md

### Security Considerations
- Secrets are base64-encoded (NOT encrypted at rest in etcd)
- Acceptable for local development/learning
- Production would use external secrets management (HashiCorp Vault, AWS Secrets Manager)
- Never commit secrets to git (add to .gitignore)

---

## 10. Docker Build Strategy

### Image Registry Decision
**Use Minikube's Docker daemon directly (no push/pull required)**

### Rationale
- Eliminates need for local Docker registry
- Avoids network overhead of push/pull
- Simplifies image availability (`imagePullPolicy: IfNotPresent`)
- Faster iteration during development

### Implementation
```bash
# Point Docker CLI to Minikube's Docker daemon
eval $(minikube docker-env)

# Build images (now inside Minikube)
docker build -t todo-chatbot-frontend:v1.0.0 ./frontend
docker build -t todo-chatbot-auth:v1.0.0 ./backend/auth-service
docker build -t todo-chatbot-api:v1.0.0 ./backend/api-service
docker build -t todo-chatbot-reminder:v1.0.0 ./backend/reminder-agent

# Verify images visible to Minikube
minikube ssh -- docker images | grep todo-chatbot
```

**Helm Chart Configuration:**
```yaml
# values.yaml
image:
  repository: todo-chatbot-frontend
  tag: v1.0.0
  pullPolicy: IfNotPresent  # Critical: Do not use Always
```

### Image Tagging Convention
- Development: `v1.0.0-dev`, `v1.0.0-<git-sha>`
- Stable: `v1.0.0`
- Latest: `latest` (use sparingly, prefer explicit versions)

---

## Summary of Decisions

| Question | Decision | Rationale |
|----------|----------|-----------|
| Database Strategy | External Neon Serverless | Resource efficiency, production-like pattern |
| Frontend-Backend Communication | NodePort from browser | Simplicity, explicit Minikube networking |
| Health Endpoints | ✅ All verified (auth, api have `/health`; frontend uses `/`; reminder-agent N/A) | Existing endpoints ready, no creation needed |
| Reminder Agent Stack | Python 3.11 + AsyncIOScheduler | Consistency with API service, background job architecture |
| Reminder Agent Deployment | Kubernetes Deployment (no HTTP probes) | Long-running scheduler, not CronJob (manages own intervals) |
| AI Tooling | Manual fallback (tools unavailable) | Deeper learning, no external dependencies |
| Resource Allocation | 2 CPU, 4GB RAM, 512Mi per pod | Balanced distribution, headroom for overhead |
| Service Exposure | Frontend/API NodePort, auth/reminder ClusterIP | User access + internal communication |
| Secrets Management | Manual kubectl create secret | Simple, documented, no Helm complexity |
| Image Registry | Minikube Docker daemon | No push/pull overhead, faster iteration |
| Dockerfiles Status | Auth has basic Dockerfile; need optimized multi-stage for all | Auth needs production optimization; create new for frontend/api/reminder |

---

## Next Steps

1. ✅ **Verify remaining health endpoints** - COMPLETE
   - Auth Service: `/health` endpoint exists
   - API Service: `/health` endpoint exists
   - Frontend: Default `/` route usable
   - Reminder Agent: Background job (no HTTP server, no probes needed)
2. ✅ **Health endpoint creation** - NOT NEEDED (all accounted for)
3. **Proceed to `/sp.tasks`** generation with all decisions resolved
4. **Begin Phase 0 implementation** (Minikube setup, manual Dockerfile authoring)

---

**Research Status:** ✅ COMPLETE (All health endpoints verified)
**Open Questions:** ✅ ALL RESOLVED
**Ready for:** `/sp.tasks` execution
**Key Finding:** Reminder-agent is background job processor (AsyncIOScheduler), deploy as Deployment without HTTP probes
