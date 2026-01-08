# Implementation Plan: Phase IV - Local Kubernetes Deployment

**Branch**: `phase-iv-kubernetes-deployment` | **Date**: 2025-12-30 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/phase-iv-kubernetes-deployment/spec.md`

---

## 1. Plan Overview

### 1.1 Purpose of This Execution Plan

Transform the existing Phase III application (Next.js frontend, Node.js auth-service, Python FastAPI backend, reminder-agent) into containerized microservices and deploy them to a local Minikube Kubernetes cluster with AI-assisted DevOps tooling integration.

This plan orchestrates the transition from local development deployment to Kubernetes-native infrastructure without modifying application logic.

### 1.2 Scope Alignment with Phase IV

**In Scope:**
- Containerization of all application components (frontend, backend services)
- Helm chart packaging for repeatable deployments
- Local Kubernetes cluster setup and configuration
- AI-assisted operations (Gordon for Docker, kubectl-ai for operations, Kagent for analysis)
- Service exposure and inter-service communication
- Health monitoring and basic observability

**Out of Scope:**
- Application code modifications
- Cloud provider deployments
- Production security hardening (mTLS, network policies, RBAC)
- Advanced Kubernetes features (HPA, VPA, Ingress, Service Mesh)
- Monitoring stacks (Prometheus, Grafana)
- CI/CD pipeline integration

---

## 2. Execution Sequence

### Phase 0: Environment & Tooling Readiness

**Objective:** Establish local Kubernetes environment and validate AI DevOps tooling availability.

**Execution Steps:**

1. **Minikube Cluster Provisioning**
   - Validate Docker Desktop installation and driver availability
   - Initialize Minikube cluster with resource constraints (2 CPUs, 4GB RAM)
   - Enable required addons (metrics-server, registry)
   - Create application namespace (`todo-app`)

2. **AI DevOps Tooling Validation**
   - Verify Docker Desktop with Gordon AI agent availability
   - Install kubectl-ai plugin (via krew or direct installation)
   - Install Kagent for cluster analysis
   - Document fallback strategies if tools unavailable

3. **Prerequisites Verification**
   - Validate Phase III application components are functional locally
   - Identify health endpoint availability (frontend `/api/health`, backend `/health`)
   - Document current environment variable configuration
   - Determine database strategy (external Neon vs in-cluster PostgreSQL)

**Readiness Milestone:**
- Minikube cluster running and accessible via `kubectl`
- Application namespace created
- AI tooling installed or fallback strategy documented
- Phase III application state captured

---

### Phase 1: Containerization Readiness

**Objective:** Transform application components into optimized Docker containers.

**Execution Steps:**

1. **Frontend Containerization (Next.js)**
   - Design multi-stage Dockerfile (deps → builder → runner)
   - Configure `.dockerignore` for layer caching optimization
   - Define build-time ARGs for `NEXT_PUBLIC_API_URL`
   - Set non-root user and security contexts
   - Target image size <200MB

2. **Backend Containerization (Node.js auth-service)**
   - Design multi-stage Dockerfile for TypeScript compilation
   - Configure production dependency isolation
   - Define runtime environment variable injection points
   - Set non-root user and security contexts
   - Target image size <150MB

3. **Backend Containerization (Python FastAPI - if exists)**
   - Design multi-stage Dockerfile with virtual environment
   - Configure slim base image (python:3.11-slim)
   - Define requirements.txt integration
   - Set non-root user and security contexts
   - Target image size <300MB

4. **Backend Containerization (Reminder Agent)**
   - Identify technology stack (Node.js or Python)
   - Apply appropriate containerization strategy
   - Define health check endpoints
   - Configure environment variable requirements

5. **Gordon AI Assistance Integration**
   - Use Gordon to generate initial Dockerfiles
   - Request optimization suggestions for multi-stage builds
   - Validate security recommendations
   - Document Gordon-generated vs manual Dockerfile decisions

6. **Image Build Validation**
   - Build all images using Minikube's Docker daemon (`eval $(minikube docker-env)`)
   - Validate image sizes meet targets
   - Test container startup locally (`docker run`)
   - Scan for vulnerabilities (basic `docker scan` if available)

**Readiness Milestone:**
- All application components have validated Dockerfiles
- Images build successfully without errors
- Images run locally and serve expected endpoints
- Image sizes within specified targets
- Non-root users configured for all images

---

### Phase 2: Helm-Based Packaging Readiness

**Objective:** Package containerized applications into parameterized Helm charts for repeatable deployments.

**Execution Steps:**

1. **Helm Chart Structure Design**
   - Define chart directory layout (`charts/todo-chatbot-frontend`, `charts/todo-chatbot-backend`)
   - Create Chart.yaml with metadata (apiVersion, name, version, appVersion)
   - Design values.yaml parameter hierarchy (image, service, resources, env, healthCheck)
   - Plan _helpers.tpl for reusable labels and selectors

2. **Frontend Helm Chart Creation**
   - Template Deployment manifest (replicas, image, ports, env, probes, resources)
   - Template Service manifest (NodePort type, static nodePort 30080)
   - Template ConfigMap for non-sensitive configuration
   - Define health probes (liveness: `/api/health`, readiness: `/api/health`)
   - Configure resource limits (512Mi RAM, 500m CPU)

3. **Backend Helm Chart Creation (Per Service)**
   - Template Deployment manifests for auth-service, FastAPI, reminder-agent
   - Template Service manifests (NodePort 30081+ or ClusterIP for internal services)
   - Template Secret manifest for DATABASE_URL, AUTH_SECRET, GEMINI_API_KEY
   - Template ConfigMap for NODE_ENV, LOG_LEVEL
   - Define health probes per service
   - Configure resource limits per service

4. **Inter-Service Communication Design**
   - Define Service DNS naming convention (e.g., `backend-service.todo-app.svc.cluster.local`)
   - Plan frontend-to-backend connectivity strategy:
     - **Option A:** Client-side NodePort access (browser → `http://<minikube-ip>:30081`)
     - **Option B:** Server-side proxy via Next.js API routes
   - Plan backend-to-database connectivity (external Neon or in-cluster)

5. **Secrets Management Strategy**
   - Design Kubernetes Secret creation approach (manual `kubectl create secret` vs Helm-managed)
   - Document secret key names (DATABASE_URL, AUTH_SECRET, GEMINI_API_KEY, etc.)
   - Plan `.env` to Kubernetes Secret migration
   - Ensure no secrets in Helm chart values (use `--set` overrides or separate secret file)

6. **Helm Chart Validation**
   - Lint charts with `helm lint`
   - Dry-run install to validate manifests (`helm install --dry-run --debug`)
   - Validate templating with different values overrides
   - Ensure NOTES.txt provides post-install instructions

**Readiness Milestone:**
- All application components have complete Helm charts
- Charts pass `helm lint` validation
- Dry-run installs generate valid Kubernetes manifests
- Secrets management strategy documented and tested
- Service communication architecture defined

---

### Phase 3: Deployment Orchestration Readiness

**Objective:** Deploy Helm-packaged applications to Minikube and establish service connectivity.

**Execution Steps:**

1. **Pre-Deployment Configuration**
   - Create Kubernetes Secrets from `.env` values
   - Validate ConfigMaps for non-sensitive configuration
   - Document environment variable mapping (Phase III `.env` → Kubernetes ConfigMap/Secret)
   - Verify database accessibility (Neon connection string or in-cluster PostgreSQL)

2. **Helm Chart Installation Sequence**
   - Install backend services first (dependency order: database → auth → api → reminder)
   - Install frontend last (depends on backend services)
   - Use namespace isolation (`-n todo-app`)
   - Apply consistent labeling (app, component, managed-by)

3. **Pod Startup Validation**
   - Monitor pod status (`kubectl get pods -n todo-app --watch`)
   - Verify readiness probes succeed (1/1 READY state)
   - Check pod events for errors (`kubectl describe pod`)
   - Validate container logs for successful startup (`kubectl logs`)

4. **Service Exposure Configuration**
   - Validate NodePort assignments (frontend: 30080, backend: 30081)
   - Test Service DNS resolution within cluster
   - Configure port-forwarding as alternative access method
   - Document external access URLs (`http://<minikube-ip>:<nodePort>`)

5. **Inter-Service Connectivity Testing**
   - Verify frontend can reach backend (HTTP request success)
   - Verify backend can reach database (connection pool initialized)
   - Test Service DNS resolution (exec into pod, `nslookup backend-service`)
   - Validate environment variable injection (check pod env)

6. **Application Functionality Validation**
   - Access frontend via browser
   - Test user authentication (Better Auth login flow)
   - Test todo CRUD operations
   - Test AI chatbot interaction
   - Verify all Phase III features work identically

**Readiness Milestone:**
- All pods reach Running state with 1/1 ready
- Services expose correct ports (NodePort or ClusterIP)
- Frontend accessible via browser
- Backend health endpoints return 200 OK
- All Phase III functionality preserved
- Inter-service communication validated

---

### Phase 4: AI-Assisted Operational Readiness

**Objective:** Integrate AI DevOps tools for assisted operations, diagnostics, and optimization.

**Execution Steps:**

1. **kubectl-ai Integration**
   - Validate kubectl-ai installation and configuration
   - Test natural language queries:
     - "Show me all pods in todo-app namespace"
     - "Why is frontend pod failing?" (simulated failure scenario)
     - "Scale backend deployment to 2 replicas"
     - "Show logs for the backend pod"
   - Document generated kubectl commands for common operations
   - Establish confirmation workflow (review command before execution)

2. **Kagent Integration**
   - Validate Kagent installation and cluster connection
   - Run cluster health analysis (`kagent analyze cluster`)
   - Request deployment recommendations (`kagent recommend deployment`)
   - Diagnose pod issues (`kagent diagnose pod`)
   - Document actionable insights and recommendations

3. **AI-Assisted Troubleshooting Workflows**
   - Define common failure scenarios (ImagePullBackOff, CrashLoopBackOff, Pending)
   - Document kubectl-ai queries for each scenario
   - Establish Kagent analysis patterns for performance issues
   - Create troubleshooting decision tree (manual kubectl → kubectl-ai → Kagent)

4. **Safety Guardrails Implementation**
   - Configure kubectl-ai confirmation mode (KUBECTL_AI_CONFIRM=true)
   - Define prohibited operations (cluster-wide deletes, RBAC changes)
   - Establish namespace scoping for all AI-assisted commands
   - Document fallback to manual kubectl for destructive operations

5. **Learning Validation**
   - Verify Gordon provided useful Dockerfile suggestions
   - Verify kubectl-ai reduces manual command lookup
   - Verify Kagent identifies configuration improvement opportunities
   - Document AI tool effectiveness and limitations

**Readiness Milestone:**
- kubectl-ai executes at least 3 successful queries
- Kagent analyzes cluster and provides recommendations
- AI tool safety guardrails validated
- Troubleshooting workflows documented
- Learning objectives achieved (AI-assisted operations reduce manual effort)

---

### Phase 5: Observability & Validation Readiness

**Objective:** Establish health monitoring, failure diagnostics, and deployment validation patterns.

**Execution Steps:**

1. **Health Probe Validation**
   - Verify liveness probes trigger pod restarts on failure (simulate crash)
   - Verify readiness probes remove unhealthy pods from Service endpoints
   - Test probe timing configurations (initialDelaySeconds, periodSeconds)
   - Document probe behavior and tuning recommendations

2. **Resource Monitoring Setup**
   - Enable Minikube metrics-server addon
   - Validate `kubectl top` commands (nodes and pods)
   - Monitor resource usage against limits (512Mi RAM, 500m CPU)
   - Identify potential OOMKilled or CPU throttling scenarios

3. **Failure Scenario Testing**
   - Simulate pod crash (kill process)
   - Simulate ImagePullBackOff (wrong image tag)
   - Simulate database connection failure (invalid DATABASE_URL)
   - Simulate resource exhaustion (remove resource limits)
   - Document failure diagnosis and recovery procedures

4. **Logging Strategy**
   - Establish pod log retrieval patterns (`kubectl logs -f`)
   - Document log aggregation limitations (no centralized logging)
   - Define log retention expectations (Kubernetes default)
   - Plan future centralized logging integration (out of scope for Phase IV)

5. **Deployment Validation Checklist**
   - All acceptance criteria from spec.md validated
   - All pods healthy and serving traffic
   - All Phase III features functional
   - Resource usage within constraints
   - AI tooling providing value
   - Documentation complete

**Readiness Milestone:**
- Health probes configured and validated
- Resource monitoring operational
- Failure scenarios tested and documented
- Deployment validation checklist complete
- System ready for handoff to `/sp.tasks` execution

---

## 3. AI-Assisted DevOps Integration Flow

### 3.1 Gordon (Docker AI) Integration Points

**Phase 1 - Containerization Readiness:**
- **Entry Point:** Dockerfile creation for each component
- **Use Cases:**
  - Generate initial Dockerfile scaffolding
  - Suggest multi-stage build optimizations
  - Recommend security improvements (non-root users, vulnerability fixes)
  - Diagnose build errors
- **Progression:** Manual Dockerfiles → Gordon-assisted optimization → Validated production Dockerfiles

### 3.2 kubectl-ai Integration Points

**Phase 3 - Deployment Orchestration:**
- **Entry Point:** Post-deployment validation and operations
- **Use Cases:**
  - Natural language pod inspection
  - Log retrieval without memorizing kubectl syntax
  - Deployment scaling operations
  - Failure diagnosis (ImagePullBackOff, CrashLoopBackOff)
- **Progression:** Manual kubectl commands → kubectl-ai queries → Confirmed execution

**Phase 4 - AI-Assisted Operations:**
- **Entry Point:** Operational troubleshooting
- **Use Cases:**
  - Debug failed deployments
  - Investigate resource constraints
  - Understand Service networking
  - Execute scaling operations
- **Progression:** kubectl-ai suggestions → Human review → Manual execution fallback if needed

### 3.3 Kagent Integration Points

**Phase 4 - AI-Assisted Operations:**
- **Entry Point:** Cluster health analysis
- **Use Cases:**
  - Cluster-wide health assessment
  - Resource optimization recommendations
  - Deployment best practice validation
  - Performance bottleneck identification
- **Progression:** Manual cluster inspection → Kagent analysis → Actionable recommendations → Human-approved implementation

**Phase 5 - Observability & Validation:**
- **Entry Point:** Pre-production validation
- **Use Cases:**
  - Final deployment validation
  - Configuration review (security, resources, health checks)
  - Identify missing best practices
  - Generate optimization roadmap for future phases
- **Progression:** Manual checklist → Kagent analysis → Gap identification → Documentation of future improvements

### 3.4 AI Tool Progression Summary

```
Manual Operations (Baseline)
    ↓
Gordon-Assisted Dockerfiles (Phase 1)
    ↓
kubectl-ai Queries (Phase 3+)
    ↓
Kagent Analysis (Phase 4+)
    ↓
Human-in-the-Loop Confirmation (All Phases)
    ↓
Validated Kubernetes Deployment
```

**Safety Boundaries:**
- All AI-generated commands reviewed before execution
- Destructive operations require manual confirmation
- Namespace scoping enforced for all operations
- Fallback to official documentation for ambiguous recommendations

---

## 4. Validation & Readiness Milestones

### Milestone 1: Environment Ready
**When:** End of Phase 0
**Signals:**
- ✅ Minikube cluster accessible (`kubectl cluster-info`)
- ✅ Namespace `todo-app` created
- ✅ AI tooling installed or fallback documented
- ✅ Phase III application state captured

### Milestone 2: Containers Ready
**When:** End of Phase 1
**Signals:**
- ✅ All Dockerfiles build without errors
- ✅ Images pushed to Minikube registry or available in Minikube Docker daemon
- ✅ Images run locally and serve expected endpoints
- ✅ Image sizes meet targets (<200MB frontend, <150MB backend)
- ✅ Security scans pass (non-root users, no critical vulnerabilities)

### Milestone 3: Charts Ready
**When:** End of Phase 2
**Signals:**
- ✅ All Helm charts pass `helm lint`
- ✅ Dry-run installs generate valid manifests
- ✅ Secrets management strategy validated
- ✅ Service communication architecture defined
- ✅ NOTES.txt provides clear post-install instructions

### Milestone 4: Deployment Ready
**When:** End of Phase 3
**Signals:**
- ✅ All pods reach Running state (1/1 ready)
- ✅ All Services expose correct ports
- ✅ Frontend accessible via browser (`http://<minikube-ip>:30080`)
- ✅ Backend health endpoints return 200 OK
- ✅ Inter-service communication validated
- ✅ All Phase III features functional

### Milestone 5: Operations Ready
**When:** End of Phase 4
**Signals:**
- ✅ kubectl-ai executes successful queries
- ✅ Kagent provides cluster analysis
- ✅ AI tool safety guardrails validated
- ✅ Troubleshooting workflows documented
- ✅ Learning objectives achieved

### Milestone 6: Production-Like Ready
**When:** End of Phase 5
**Signals:**
- ✅ Health probes validated
- ✅ Resource monitoring operational
- ✅ Failure scenarios tested
- ✅ Deployment validation checklist complete
- ✅ Documentation complete (README, DEPLOYMENT.md)
- ✅ Ready for `/sp.tasks` execution

---

## 5. Plan Completion Criteria

### 5.1 Functional Completion

**Application Functionality:**
- [ ] All pods running and healthy (frontend, auth-service, FastAPI, reminder-agent)
- [ ] User can access frontend via browser
- [ ] User can authenticate via Better Auth
- [ ] User can perform all todo operations (create, read, update, delete, complete)
- [ ] AI chatbot responds to user messages
- [ ] All Phase III features work identically to local development

**Infrastructure Functionality:**
- [ ] Minikube cluster operational
- [ ] All Helm charts installed successfully
- [ ] Services expose correct ports (NodePort or ClusterIP)
- [ ] ConfigMaps and Secrets correctly inject environment variables
- [ ] Database connectivity established (Neon or in-cluster)

### 5.2 Technical Completion

**Containerization:**
- [ ] All Dockerfiles follow multi-stage build pattern
- [ ] All images use non-root users
- [ ] Image sizes meet targets
- [ ] `.dockerignore` optimizes layer caching
- [ ] No hardcoded secrets in images

**Helm Charts:**
- [ ] All charts parameterized (values.yaml)
- [ ] All charts pass linting
- [ ] Health probes configured (liveness, readiness)
- [ ] Resource limits defined (CPU, memory)
- [ ] Labels and selectors consistent

**Operations:**
- [ ] kubectl-ai installed and functional
- [ ] Kagent installed and functional
- [ ] Troubleshooting workflows documented
- [ ] Safety guardrails validated

### 5.3 Validation Completion

**Testing:**
- [ ] Pod crash recovery validated (liveness probe restarts)
- [ ] Service endpoint removal validated (readiness probe)
- [ ] Resource constraints validated (kubectl top)
- [ ] Failure scenarios tested (ImagePullBackOff, CrashLoopBackOff, database failure)

**Documentation:**
- [ ] README.md updated with Kubernetes deployment instructions
- [ ] DEPLOYMENT.md created with detailed setup guide
- [ ] Helm chart NOTES.txt provides post-install instructions
- [ ] Troubleshooting section documents common issues
- [ ] AI tool usage documented

### 5.4 Learning Objectives Completion

- [ ] Successfully deployed multi-container application to Kubernetes
- [ ] Understood Docker multi-stage builds
- [ ] Created parameterized Helm charts
- [ ] Used NodePort for service exposure
- [ ] Configured health probes for automatic restarts
- [ ] Managed secrets securely with Kubernetes Secrets
- [ ] Used AI tools to assist with Kubernetes operations
- [ ] Diagnosed and fixed at least 1 pod failure scenario

### 5.5 Readiness for `/sp.tasks` Execution

**Prerequisites Met:**
- [ ] Plan approved by human reviewer
- [x] Open questions from spec.md resolved (see `research.md`):
  - ✅ Database strategy: External Neon Serverless PostgreSQL
  - ✅ Frontend-backend communication: NodePort from browser (client-side)
  - ✅ Health endpoints: API service has `/health`, frontend uses `/`
  - ✅ Reminder agent stack: Python 3.11+
  - ✅ AI tool availability: NOT available, manual fallback strategies documented
- [ ] Constitution compliance verified (no violations or justified)
- [ ] Complexity tracking completed (if violations exist)

**Artifacts Ready:**
- [x] `specs/phase-iv-kubernetes-deployment/plan.md` (this file) complete
- [x] `specs/phase-iv-kubernetes-deployment/research.md` populated with all decisions
- [ ] `specs/phase-iv-kubernetes-deployment/data-model.md` N/A (infrastructure, no data models)
- [ ] `specs/phase-iv-kubernetes-deployment/contracts/` N/A (infrastructure, no API contracts)
- [ ] `specs/phase-iv-kubernetes-deployment/quickstart.md` will be created during `/sp.tasks` execution

**Next Command:**
- Run `/sp.tasks` to generate dependency-ordered task breakdown from this plan

---

## Summary

This plan orchestrates the transformation of Phase III application components into Kubernetes-native deployments through 5 progressive phases:

1. **Phase 0:** Establish Minikube cluster and validate AI tooling
2. **Phase 1:** Containerize all application components with Docker
3. **Phase 2:** Package containers into parameterized Helm charts
4. **Phase 3:** Deploy charts to Minikube and validate connectivity
5. **Phase 4:** Integrate AI-assisted operations (kubectl-ai, Kagent)
6. **Phase 5:** Validate observability, health monitoring, and failure recovery

AI DevOps tooling (Gordon, kubectl-ai, Kagent) is layered progressively:
- **Gordon:** Dockerfile creation and optimization (Phase 1)
- **kubectl-ai:** Operational commands and troubleshooting (Phase 3-5)
- **Kagent:** Cluster analysis and optimization recommendations (Phase 4-5)

All operations maintain human-in-the-loop confirmation with namespace scoping and safety guardrails.

The plan explicitly excludes application code changes, cloud deployments, and production hardening features per Phase IV scope boundaries.

Upon completion, the system will be a fully functional local Kubernetes deployment with AI-assisted operational tooling, ready for learning and development purposes at zero cloud cost.

---

## Technical Context

**Languages/Versions:**
- Frontend: TypeScript/JavaScript (Next.js 16.x, React 19.x, Node.js 18+)
- Backend Auth Service: TypeScript/JavaScript (Node.js 18+, Better Auth)
- Backend API: Python 3.11+ (FastAPI, SQLModel) - if exists
- Reminder Agent: Python 3.11+ (consistent with API service)

**Primary Dependencies:**
- Docker Desktop 24.x+ (or Docker Engine)
- Minikube 1.30.0+ (Kubernetes 1.28.x+)
- Helm 3.10.0+
- kubectl 1.28.x+
- hadolint (Dockerfile linter) - optional but recommended
- trivy or docker scan (vulnerability scanning) - optional

**AI DevOps Tools Status:**
- Gordon (Docker AI): ❌ NOT AVAILABLE - Manual Dockerfile authoring required
- kubectl-ai: ❌ NOT AVAILABLE - Standard kubectl commands required
- Kagent: ❌ NOT AVAILABLE - Manual cluster analysis required
- See `research.md` for detailed fallback strategies

**Storage:**
- External: Neon Serverless PostgreSQL (confirmed - existing Phase III database)
- No in-cluster database deployment (preserves 4GB RAM for application pods)

**Testing:**
- Infrastructure validation: `helm lint`, `kubectl describe`, `kubectl logs`
- Functional validation: Manual browser testing, curl commands
- Health validation: Liveness/readiness probe behavior

**Target Platform:**
- Local Kubernetes: Minikube on Docker driver (Windows/macOS/Linux)
- Resource constraints: 2 CPUs, 4GB RAM total

**Project Type:**
- Infrastructure: Multi-component web application (frontend + multiple backend services)

**Performance Goals:**
- Pod startup time: <60 seconds
- Application response time: Similar to Phase III local development
- Resource usage: <4GB total RAM across all pods

**Constraints:**
- Zero cloud costs (local-only deployment)
- Minikube resource limits (4GB RAM, 2 CPUs)
- No persistent storage beyond hostPath/emptyDir
- No external LoadBalancer support

**Scale/Scope:**
- Components: 1 frontend, 3+ backend services
- Replicas: 1 per component (local constraint)
- Namespaces: 1 application namespace (`todo-app`)
- Helm charts: 2 charts (frontend, backend umbrella chart)

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Phase IV Scope vs Constitution Principles:**

### I. Stateless-First Architecture
**Status:** ✅ PRESERVED
**Rationale:** Containerization does not change application architecture. Phase III stateless design carries forward into Kubernetes pods. No in-memory state introduced.

### II. MCP-First Tool Integration
**Status:** ✅ PRESERVED
**Rationale:** Application logic unchanged. MCP tools remain the interface between AI agent and data layer. Containerization is infrastructure-only.

### III. Database Persistence Guarantee
**Status:** ✅ PRESERVED
**Rationale:** Database connection (Neon PostgreSQL) maintained via Kubernetes Secrets. All persistence guarantees from Phase III remain intact.

### IV. Test-First Development
**Status:** ⚠️ ADAPTED FOR INFRASTRUCTURE
**Rationale:** Phase IV is infrastructure deployment, not feature development. Testing focuses on:
- Dockerfile builds successfully (test: `docker build`)
- Helm charts lint successfully (test: `helm lint`)
- Pods reach Running state (test: `kubectl wait`)
- Application functionality preserved (test: manual validation)
**Justification:** Infrastructure validation replaces unit/integration tests. TDD cycle not applicable to Dockerfile/Helm chart authoring.

### V. Conversational Error Handling
**Status:** ✅ PRESERVED
**Rationale:** Application error handling unchanged. Kubernetes adds infrastructure-level errors (pod failures, image pulls), but these are operational concerns, not user-facing.

### VI. Natural Language Intent Mapping
**Status:** ✅ PRESERVED
**Rationale:** AI agent logic unchanged. Intent mapping remains in application code. Kubernetes deployment does not affect agent behavior.

### VII. Security and User Isolation
**Status:** ✅ PRESERVED + ENHANCED
**Rationale:** User isolation maintained at application layer. Kubernetes adds:
- Secrets management for credentials
- Non-root container users
- Namespace isolation
- Resource limits (prevent noisy neighbor issues)

**Overall Constitution Compliance:** ✅ PASS
**Violations:** None
**Adaptations:** Test-First Development adapted for infrastructure validation (justified above)

---

## Project Structure

### Documentation (this feature)

```
specs/phase-iv-kubernetes-deployment/
├── spec.md              # Phase IV specification (input)
├── plan.md              # This file (output of /sp.plan)
├── quickstart.md        # Minikube setup, Helm install commands (Phase 1 output)
├── research.md          # Technology decisions, tool validation (Phase 0 output)
└── tasks.md             # Task breakdown (output of /sp.tasks - NOT created by /sp.plan)
```

### Source Code (repository root)

```
Todo-Full-Stack-Web-Application/
├── frontend/                      # Existing Phase III
│   ├── src/                       # (unchanged)
│   ├── Dockerfile                 # NEW: Multi-stage Next.js build
│   ├── .dockerignore              # NEW: Optimize Docker layer caching
│   └── package.json               # (unchanged)
│
├── backend/
│   ├── auth-service/              # Existing Phase III
│   │   ├── src/                   # (unchanged)
│   │   ├── Dockerfile             # NEW: Multi-stage Node.js build
│   │   ├── .dockerignore          # NEW
│   │   └── package.json           # (unchanged)
│   │
│   ├── api/                       # Existing Phase III (FastAPI - if exists)
│   │   ├── app/                   # (unchanged)
│   │   ├── Dockerfile             # NEW: Multi-stage Python build
│   │   ├── .dockerignore          # NEW
│   │   └── requirements.txt       # (unchanged)
│   │
│   └── reminder-agent/            # Existing Phase III
│       ├── src/                   # (unchanged)
│       ├── Dockerfile             # NEW: (Node.js or Python - TBD)
│       ├── .dockerignore          # NEW
│       └── package.json or requirements.txt
│
├── charts/                        # NEW: Helm charts directory
│   ├── todo-chatbot-frontend/
│   │   ├── Chart.yaml
│   │   ├── values.yaml
│   │   ├── templates/
│   │   │   ├── deployment.yaml
│   │   │   ├── service.yaml
│   │   │   ├── configmap.yaml
│   │   │   ├── _helpers.tpl
│   │   │   └── NOTES.txt
│   │   └── .helmignore
│   │
│   └── todo-chatbot-backend/      # Umbrella chart for all backend services
│       ├── Chart.yaml
│       ├── values.yaml
│       ├── templates/
│       │   ├── auth-service/
│       │   │   ├── deployment.yaml
│       │   │   ├── service.yaml
│       │   │   └── secret.yaml
│       │   ├── api/
│       │   │   ├── deployment.yaml
│       │   │   ├── service.yaml
│       │   │   └── secret.yaml
│       │   ├── reminder-agent/
│       │   │   ├── deployment.yaml
│       │   │   ├── service.yaml
│       │   │   └── configmap.yaml
│       │   ├── _helpers.tpl
│       │   └── NOTES.txt
│       └── .helmignore
│
├── k8s/                           # NEW: Optional raw manifests (if not using Helm)
│   ├── namespace.yaml
│   └── secrets/
│       └── .gitkeep               # Secrets NOT committed to git
│
├── .env.example                   # UPDATED: Document Kubernetes Secret mapping
├── README.md                      # UPDATED: Add Kubernetes deployment section
└── DEPLOYMENT.md                  # NEW: Detailed Minikube setup guide
```

**Structure Decision:**
Web application structure with infrastructure additions. Existing Phase III code (`frontend/`, `backend/`) unchanged. New infrastructure artifacts (`charts/`, Dockerfiles, `.dockerignore`) added alongside application code for co-location. Helm charts organized by logical component (frontend, backend umbrella chart with sub-services).

---

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Test-First Development adapted for infrastructure | Infrastructure validation requires different testing approach (build tests, deployment tests, functional validation) | Traditional TDD (unit tests → implementation) does not apply to Dockerfile/Helm chart authoring. Infrastructure correctness validated via builds, lints, and runtime behavior. |

**No other violations.** Constitution principles preserved or enhanced by Kubernetes deployment.

---

**Plan Status:** ✅ COMPLETE (All open questions resolved - see `research.md`)
**Ready for:** `/sp.tasks` execution (human approval pending)
