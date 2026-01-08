---
id: 003
title: Phase IV Kubernetes Task Breakdown
stage: tasks
date: 2025-12-30
surface: agent
model: claude-sonnet-4-5-20250929
feature: phase-iv-kubernetes-deployment
branch: 001-auth-session-fix
user: Developer
command: /sp.tasks
labels: ["kubernetes", "docker", "helm", "minikube", "tasks", "implementation", "containerization", "deployment"]
links:
  spec: specs/phase-iv-kubernetes-deployment/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/phase-iv-kubernetes-deployment/tasks.md
tests:
  - N/A (task breakdown phase, testing occurs during implementation)
---

## Prompt

You are a Senior Spec-Kit Plus Task Decomposition Expert and AI DevOps Execution Architect.

Your task is to generate a COMPLETE, ORDERED, and ATOMIC `/sp.tasks` file
for **Phase IV: Local Kubernetes Deployment** of the Cloud-Native Todo Chatbot.

STRICT RULES (NON-NEGOTIABLE):
- Use ONLY the approved `/sp.specs` and `/sp.plan`
- Do NOT add new features, requirements, tools, or architecture
- Do NOT modify application logic from Phase III
- Do NOT restate plans or specs
- Do NOT include explanations, commentary, or summaries
- Do NOT include high-level steps — tasks must be atomic and executable
- Do NOT merge multiple actions into a single task
- Each task must represent ONE concrete action

TASK FORMAT REQUIREMENTS:
- Tasks must be numbered in strict execution order
- Each task must:
  - Be small enough to execute in one focused action
  - Have a clear start and completion condition
  - Depend only on previously completed tasks
- Tasks must be suitable for direct use in `/sp.implement`

PROJECT CONTEXT:
- Application: Cloud-Native Todo Chatbot
- Previous Phase: Phase III (frontend + backend already implemented)
- Current Phase: Phase IV
- Deployment Target: Local Kubernetes (Minikube)
- Tooling: Docker Desktop, Minikube, Helm, kubectl (AI tools unavailable)
- Development Methodology: Spec-Driven Development (Spec-Kit Plus)

REQUIRED TASK COVERAGE (ALL INCLUDED):
1. Environment Preparation (Minikube, namespace, Docker daemon)
2. Containerization (frontend, auth, api, reminder-agent)
3. Helm Charts (frontend chart, backend umbrella chart)
4. Secrets Management (manual kubectl create secret)
5. Deployment (backend then frontend via Helm)
6. Validation (health probes, connectivity, resource monitoring)
7. Manual Operations (kubectl commands, cluster health analysis)
8. Failure Scenarios (ImagePullBackOff, database failures, pod restarts)
9. E2E Testing (Phase III functionality preservation)
10. Documentation (quickstart, README, DEPLOYMENT.md)

OUTPUT REQUIREMENTS:
- Output ONLY the ordered list of tasks
- No prose, no explanations, no headers beyond task titles
- Each task must be explicit, unambiguous, and minimal
- The final task must clearly signal Phase IV completion readiness

This `/sp.tasks` output will be executed verbatim during `/sp.implement`.

## Response snapshot

Generated comprehensive 200-task breakdown for Phase IV: Local Kubernetes Deployment organized into 18 sequential phases:

**Phase 0: Environment Setup (T001-T013)**
- Docker Desktop verification
- Minikube cluster initialization (2 CPUs, 4GB RAM, Docker driver)
- Namespace creation (todo-app)
- AI tool availability check (Gordon, kubectl-ai, Kagent - all unavailable, fallback documented)
- Docker daemon configuration (eval $(minikube docker-env))
- Phase III environment variable documentation
- External Neon PostgreSQL connectivity verification

**Phase 1: Frontend Containerization (T014-T023)**
- Create .dockerignore
- Multi-stage Dockerfile (deps → builder → runner, node:18-alpine)
- Build-time ARG for NEXT_PUBLIC_API_URL
- Non-root user configuration
- Image build and size validation (<200MB)
- Local container testing

**Phase 2: Auth Service Containerization (T024-T032)**
- Optimize existing Dockerfile with multi-stage build
- TypeScript compilation stage
- Production dependency isolation
- Image build and size validation (<150MB)
- Health endpoint verification (/health)

**Phase 3: API Service Containerization (T033-T040)**
- Python FastAPI Dockerfile (python:3.11-slim)
- Virtual environment isolation
- Non-root appuser configuration
- Image build and size validation (<300MB)
- Health endpoint verification (/health with database test)

**Phase 4: Reminder Agent Containerization (T041-T047)**
- Python AsyncIOScheduler Dockerfile
- Background job configuration (no port exposure)
- Image build and validation
- Startup log verification

**Phase 5: Frontend Helm Chart (T048-T063)**
- Chart structure and metadata (Chart.yaml, values.yaml, .helmignore)
- _helpers.tpl with label functions
- Deployment manifest with liveness/readiness probes
- NodePort Service (30080)
- ConfigMap for non-sensitive config
- NOTES.txt with access instructions
- Lint and dry-run validation

**Phase 6: Backend Helm Chart (T064-T085)**
- Umbrella chart for auth, api, reminder services
- Separate Deployment manifests for each service
- Auth: ClusterIP Service (internal only)
- API: NodePort Service (30081)
- Reminder: No service (background job)
- Secret manifest for DATABASE_URL, AUTH_SECRET, GEMINI_API_KEY
- ConfigMap for NODE_ENV, LOG_LEVEL
- Lint and dry-run validation

**Phase 7: Secrets Management (T086-T092)**
- Extract sensitive values from Phase III .env
- Create Kubernetes Secret via kubectl create secret
- Verification and documentation in quickstart.md

**Phase 8: Backend Deployment (T093-T100)**
- Helm install backend chart
- Wait for pod readiness (kubectl wait)
- Pod status verification (1/1 READY)
- Log inspection for successful startup

**Phase 9: Frontend Deployment (T101-T107)**
- Get Minikube IP for API URL
- Update frontend with correct NEXT_PUBLIC_API_URL
- Rebuild if using build-time ARG
- Helm install frontend chart
- Pod readiness and log verification

**Phase 10: Service Connectivity (T108-T114)**
- NodePort service details verification
- External access testing (browser)
- Frontend-to-backend connectivity (network tab)
- Internal service DNS testing (curl from pod)
- Database connectivity verification

**Phase 11: Health Probe Validation (T115-T121)**
- Liveness/readiness probe status verification
- Simulated pod failure (kill process)
- Automatic restart validation
- Service endpoint removal testing

**Phase 12: Resource Monitoring (T122-T127)**
- Node and pod resource usage (kubectl top)
- Memory/CPU limit validation
- OOMKilled and throttling detection

**Phase 13: Manual kubectl Operations (T128-T137)**
- Scaling operations (2 replicas → 1 replica)
- Pod inspection (describe, logs streaming)
- Resource listing (get all)
- Event monitoring
- Pod exec and DNS resolution testing
- Command documentation in quickstart.md

**Phase 14: Manual Cluster Health Analysis (T138-T146)**
- Cluster component status checks
- System pod verification
- Metrics-server validation
- Resource requests/limits review
- Configuration improvement identification
- Security context audit
- Documentation of findings

**Phase 15: Failure Scenario Testing (T147-T157)**
- ImagePullBackOff simulation (wrong image tag)
- Database connection failure simulation (invalid DATABASE_URL)
- Health probe failure and service endpoint removal
- Pod deletion and automatic recreation
- Recovery procedure documentation

**Phase 16: E2E Application Validation (T158-T168)**
- Frontend browser access
- Better Auth registration/login flows
- Todo CRUD operations (create, list, complete, delete)
- AI chatbot interaction
- Phase III functionality parity verification
- Concurrent session testing
- Session persistence across pod restarts

**Phase 17: Documentation (T169-T180)**
- Create quickstart.md (setup, build, install, troubleshoot, access URLs)
- Update root README.md (Phase IV section)
- Create DEPLOYMENT.md (detailed Minikube guide)
- Document teardown procedure (minikube delete)
- Data persistence documentation (external Neon)
- File reference and environment variable mapping

**Phase 18: Completion Validation (T181-T200)**
- Verify all spec.md success criteria met:
  - Container builds successful
  - Helm charts install without errors
  - Pods Running and ready
  - Service communication functional
  - Application accessible from host
  - Phase III functionality preserved
  - Multi-stage builds used
  - Health probes configured
  - Automatic pod restarts working
  - Zero cloud costs (local only)
  - Resource usage under 4GB RAM
  - AI tool fallbacks documented and functional
- Mark Phase IV COMPLETE

**Key Task Characteristics:**
- All tasks atomic and executable (single action per task)
- Strict sequential ordering (dependency-aware)
- No application code modifications (infrastructure only)
- AI tools unavailable (Gordon, kubectl-ai, Kagent) - manual fallbacks used
- External Neon PostgreSQL (no in-cluster database)
- Reminder-agent as Deployment (not CronJob, no HTTP probes)
- NodePort service exposure (frontend 30080, API 30081)
- Comprehensive validation and documentation

**Task Format:**
- Standard checklist: `- [ ] TXXX Description with file path`
- No [P] parallelization markers (sequential phases)
- No [Story] labels (infrastructure deployment, not user stories)
- Each task has clear completion criteria

## Outcome

- ✅ Impact: Complete 200-task atomic breakdown for Phase IV Kubernetes deployment. All tasks executable without additional context.
- 🧪 Tests: Integrated into tasks (health probe validation T115-T121, failure scenarios T147-T157, E2E testing T158-T168)
- 📁 Files: Created specs/phase-iv-kubernetes-deployment/tasks.md (18 phases, 200 atomic tasks)
- 🔁 Next prompts: /sp.implement (execute tasks) or manual implementation following task sequence
- 🧠 Reflection: Task breakdown successfully decomposed 5-phase execution plan (from plan.md) into 200 atomic, executable tasks. AI tool unavailability (Gordon, kubectl-ai, Kagent) reflected in manual kubectl/Docker command usage throughout. Reminder-agent treated as Deployment without HTTP probes per research.md findings. All tasks dependency-ordered and suitable for autonomous execution.

## Evaluation notes (flywheel)

- Failure modes observed: None. Task generation completed successfully.
- Graders run and results (PASS/FAIL):
  - Atomicity: PASS (each task is single action with clear completion)
  - Ordering: PASS (strict dependency order, sequential phases)
  - Completeness: PASS (all required coverage areas included)
  - Executability: PASS (no ambiguous tasks, all have file paths or commands)
  - Format: PASS (checkbox format, task IDs T001-T200, no [P]/[Story] markers as appropriate)
- Prompt variant (if applicable): N/A (initial task generation)
- Next experiment (smallest change to try): During /sp.implement, validate task granularity is appropriate (not too small causing overhead, not too large causing blocking). Consider merging trivial verification tasks (e.g., T181-T195 completion criteria checks could be single validation script task).
