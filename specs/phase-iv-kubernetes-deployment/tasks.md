# Phase IV: Local Kubernetes Deployment - Task Breakdown

**Feature**: phase-iv-kubernetes-deployment
**Created**: 2025-12-30
**Status**: Ready for Implementation

---

## Phase 0: Environment Setup & Tooling Validation

### Objective
Establish local Kubernetes environment, validate Docker tooling, and document AI DevOps tool availability.

### Tasks

- [ ] T001 Verify Docker Desktop installation and running status
- [ ] T002 Check Gordon AI agent availability in Docker Desktop or document manual fallback strategy
- [ ] T003 Start Minikube cluster with 2 CPUs and 4GB RAM using Docker driver via `minikube start --cpus=2 --memory=4096 --driver=docker`
- [ ] T004 Verify Minikube cluster accessibility via `kubectl cluster-info`
- [ ] T005 Enable Minikube metrics-server addon via `minikube addons enable metrics-server`
- [ ] T006 Enable Minikube registry addon via `minikube addons enable registry`
- [ ] T007 Create todo-app namespace via `kubectl create namespace todo-app`
- [ ] T008 Verify kubectl command-line tool installation and version compatibility
- [ ] T009 Check kubectl-ai plugin availability or document standard kubectl fallback approach
- [ ] T010 Check Kagent tool availability or document manual cluster analysis fallback approach
- [ ] T011 Point Docker CLI to Minikube's Docker daemon via `eval $(minikube docker-env)`
- [ ] T012 Document current Phase III environment variables from .env files for migration to Kubernetes Secrets
- [ ] T013 Verify external Neon PostgreSQL connectivity from local machine

---

## Phase 1: Frontend Containerization

### Objective
Create optimized multi-stage Docker image for Next.js frontend application.

### Tasks

- [ ] T014 Create frontend/.dockerignore file excluding node_modules, .next, .git, *.md, .env
- [ ] T015 Create frontend/Dockerfile with multi-stage build (deps → builder → runner stages)
- [ ] T016 Configure Dockerfile Stage 1 (deps): Install production dependencies using node:18-alpine base
- [ ] T017 Configure Dockerfile Stage 2 (builder): Copy dependencies and run `next build`
- [ ] T018 Configure Dockerfile Stage 3 (runner): Copy build artifacts, set non-root user, expose port 3000
- [ ] T019 Add ARG NEXT_PUBLIC_API_URL to Dockerfile for build-time API URL injection
- [ ] T020 Build frontend Docker image via `docker build -t todo-chatbot-frontend:v1.0.0 ./frontend`
- [ ] T021 Verify frontend image size is under 200MB via `docker images todo-chatbot-frontend:v1.0.0`
- [ ] T022 Test frontend container locally via `docker run -p 3000:3000 todo-chatbot-frontend:v1.0.0`
- [ ] T023 Verify frontend container serves homepage at http://localhost:3000

---

## Phase 2: Backend Containerization - Auth Service

### Objective
Optimize existing auth-service Dockerfile with multi-stage production build.

### Tasks

- [ ] T024 Create backend/auth-service/.dockerignore file excluding node_modules, dist, *.log, .env
- [ ] T025 Update backend/auth-service/Dockerfile with optimized multi-stage build (deps → builder → runner)
- [ ] T026 Configure Dockerfile Stage 1 (deps): Install production dependencies using node:18-alpine
- [ ] T027 Configure Dockerfile Stage 2 (builder): Compile TypeScript via `npm run build`
- [ ] T028 Configure Dockerfile Stage 3 (runner): Copy compiled dist/ and production node_modules, set non-root user, expose port 3001
- [ ] T029 Build auth-service Docker image via `docker build -t todo-chatbot-auth:v1.0.0 ./backend/auth-service`
- [ ] T030 Verify auth-service image size is under 150MB via `docker images todo-chatbot-auth:v1.0.0`
- [ ] T031 Test auth-service container locally via `docker run -p 3001:3001 todo-chatbot-auth:v1.0.0`
- [ ] T032 Verify auth-service health endpoint returns 200 OK at http://localhost:3001/health

---

## Phase 3: Backend Containerization - API Service

### Objective
Create optimized multi-stage Docker image for Python FastAPI backend.

### Tasks

- [ ] T033 Create backend/api-service/.dockerignore file excluding __pycache__, *.pyc, venv, .env
- [ ] T034 Create backend/api-service/Dockerfile with multi-stage build (builder → runner stages)
- [ ] T035 Configure Dockerfile Stage 1 (builder): Create virtual environment and install dependencies from requirements.txt using python:3.11-slim
- [ ] T036 Configure Dockerfile Stage 2 (runner): Copy virtual environment, set non-root user appuser, expose port 8000
- [ ] T037 Build api-service Docker image via `docker build -t todo-chatbot-api:v1.0.0 ./backend/api-service`
- [ ] T038 Verify api-service image size is under 300MB via `docker images todo-chatbot-api:v1.0.0`
- [ ] T039 Test api-service container locally via `docker run -p 8000:8000 todo-chatbot-api:v1.0.0`
- [ ] T040 Verify api-service health endpoint returns 200 OK at http://localhost:8000/health

---

## Phase 4: Backend Containerization - Reminder Agent

### Objective
Create Docker image for Python AsyncIOScheduler background job processor.

### Tasks

- [ ] T041 Create backend/reminder-agent/.dockerignore file excluding __pycache__, *.pyc, venv, .env
- [ ] T042 Create backend/reminder-agent/Dockerfile with multi-stage build (builder → runner stages)
- [ ] T043 Configure Dockerfile Stage 1 (builder): Create virtual environment and install dependencies from requirements.txt using python:3.11-slim
- [ ] T044 Configure Dockerfile Stage 2 (runner): Copy virtual environment, set non-root user appuser, no port exposure (background job)
- [ ] T045 Build reminder-agent Docker image via `docker build -t todo-chatbot-reminder:v1.0.0 ./backend/reminder-agent`
- [ ] T046 Verify reminder-agent image size is under 300MB via `docker images todo-chatbot-reminder:v1.0.0`
- [ ] T047 Test reminder-agent container locally via `docker run todo-chatbot-reminder:v1.0.0` and verify startup logs

---

## Phase 5: Helm Chart Creation - Frontend

### Objective
Create parameterized Helm chart for frontend deployment.

### Tasks

- [ ] T048 Create charts/todo-chatbot-frontend directory structure
- [ ] T049 Create charts/todo-chatbot-frontend/Chart.yaml with metadata (name, version 1.0.0, appVersion 1.0.0)
- [ ] T050 Create charts/todo-chatbot-frontend/.helmignore file
- [ ] T051 Create charts/todo-chatbot-frontend/values.yaml with image, service, resources, env, healthCheck configuration
- [ ] T052 Set values.yaml defaults: replicaCount=1, image.repository=todo-chatbot-frontend, image.tag=v1.0.0, image.pullPolicy=IfNotPresent
- [ ] T053 Set values.yaml service: type=NodePort, port=3000, nodePort=30080
- [ ] T054 Set values.yaml resources: limits (cpu=500m, memory=512Mi), requests (cpu=250m, memory=256Mi)
- [ ] T055 Create charts/todo-chatbot-frontend/templates/_helpers.tpl with label and selector helper functions
- [ ] T056 Create charts/todo-chatbot-frontend/templates/deployment.yaml with Deployment manifest
- [ ] T057 Configure deployment.yaml with liveness probe (httpGet path=/, port=3000, initialDelaySeconds=10)
- [ ] T058 Configure deployment.yaml with readiness probe (httpGet path=/, port=3000, initialDelaySeconds=5)
- [ ] T059 Create charts/todo-chatbot-frontend/templates/service.yaml with NodePort Service manifest
- [ ] T060 Create charts/todo-chatbot-frontend/templates/configmap.yaml for non-sensitive configuration
- [ ] T061 Create charts/todo-chatbot-frontend/templates/NOTES.txt with post-install access instructions
- [ ] T062 Lint frontend Helm chart via `helm lint charts/todo-chatbot-frontend`
- [ ] T063 Dry-run frontend chart install via `helm install frontend charts/todo-chatbot-frontend --dry-run --debug -n todo-app`

---

## Phase 6: Helm Chart Creation - Backend

### Objective
Create umbrella Helm chart for all backend services (auth, api, reminder-agent).

### Tasks

- [ ] T064 Create charts/todo-chatbot-backend directory structure
- [ ] T065 Create charts/todo-chatbot-backend/Chart.yaml with metadata (name, version 1.0.0, appVersion 1.0.0)
- [ ] T066 Create charts/todo-chatbot-backend/.helmignore file
- [ ] T067 Create charts/todo-chatbot-backend/values.yaml with separate sections for auth, api, reminder services
- [ ] T068 Set values.yaml auth service: replicaCount=1, image.repository=todo-chatbot-auth, image.tag=v1.0.0, service.type=ClusterIP, service.port=3001
- [ ] T069 Set values.yaml api service: replicaCount=1, image.repository=todo-chatbot-api, image.tag=v1.0.0, service.type=NodePort, service.port=8000, service.nodePort=30081
- [ ] T070 Set values.yaml reminder service: replicaCount=1, image.repository=todo-chatbot-reminder, image.tag=v1.0.0, no service (background job)
- [ ] T071 Create charts/todo-chatbot-backend/templates/_helpers.tpl with label helper functions
- [ ] T072 Create charts/todo-chatbot-backend/templates/auth-deployment.yaml with Deployment manifest for auth-service
- [ ] T073 Configure auth-deployment.yaml with liveness probe (httpGet path=/health, port=3001, initialDelaySeconds=10)
- [ ] T074 Configure auth-deployment.yaml with readiness probe (httpGet path=/health, port=3001, initialDelaySeconds=5)
- [ ] T075 Create charts/todo-chatbot-backend/templates/auth-service.yaml with ClusterIP Service manifest for auth-service
- [ ] T076 Create charts/todo-chatbot-backend/templates/api-deployment.yaml with Deployment manifest for api-service
- [ ] T077 Configure api-deployment.yaml with liveness probe (httpGet path=/health, port=8000, initialDelaySeconds=15)
- [ ] T078 Configure api-deployment.yaml with readiness probe (httpGet path=/health, port=8000, initialDelaySeconds=10)
- [ ] T079 Create charts/todo-chatbot-backend/templates/api-service.yaml with NodePort Service manifest for api-service
- [ ] T080 Create charts/todo-chatbot-backend/templates/reminder-deployment.yaml with Deployment manifest for reminder-agent (no probes)
- [ ] T081 Create charts/todo-chatbot-backend/templates/secret.yaml with Secret manifest for DATABASE_URL, AUTH_SECRET, GEMINI_API_KEY (values from external input)
- [ ] T082 Create charts/todo-chatbot-backend/templates/configmap.yaml for non-sensitive config (NODE_ENV, LOG_LEVEL)
- [ ] T083 Create charts/todo-chatbot-backend/templates/NOTES.txt with post-install instructions
- [ ] T084 Lint backend Helm chart via `helm lint charts/todo-chatbot-backend`
- [ ] T085 Dry-run backend chart install via `helm install backend charts/todo-chatbot-backend --dry-run --debug -n todo-app`

---

## Phase 7: Kubernetes Secrets Management

### Objective
Create Kubernetes Secrets for sensitive configuration outside of Helm charts.

### Tasks

- [ ] T086 Extract DATABASE_URL value from Phase III .env file
- [ ] T087 Extract AUTH_SECRET value from Phase III .env file
- [ ] T088 Extract GEMINI_API_KEY value from Phase III .env file
- [ ] T089 Extract OPENAI_API_KEY value from Phase III .env file (if exists)
- [ ] T090 Create Kubernetes Secret via `kubectl create secret generic backend-secrets --from-literal=DATABASE_URL=<value> --from-literal=AUTH_SECRET=<value> --from-literal=GEMINI_API_KEY=<value> -n todo-app`
- [ ] T091 Verify secret creation via `kubectl get secret backend-secrets -n todo-app`
- [ ] T092 Document secret creation command in specs/phase-iv-kubernetes-deployment/quickstart.md

---

## Phase 8: Helm Chart Deployment - Backend

### Objective
Deploy backend services to Minikube cluster via Helm.

### Tasks

- [ ] T093 Install backend Helm chart via `helm install backend charts/todo-chatbot-backend -n todo-app`
- [ ] T094 Wait for auth-service pod to reach Running state via `kubectl wait --for=condition=Ready pod -l app=auth-service -n todo-app --timeout=60s`
- [ ] T095 Wait for api-service pod to reach Running state via `kubectl wait --for=condition=Ready pod -l app=api-service -n todo-app --timeout=60s`
- [ ] T096 Wait for reminder-agent pod to reach Running state via `kubectl wait --for=condition=Ready pod -l app=reminder-agent -n todo-app --timeout=60s` (no probes, just Running)
- [ ] T097 Verify all backend pods show 1/1 READY via `kubectl get pods -n todo-app`
- [ ] T098 Check auth-service logs for successful startup via `kubectl logs -l app=auth-service -n todo-app --tail=20`
- [ ] T099 Check api-service logs for successful database connection via `kubectl logs -l app=api-service -n todo-app --tail=20`
- [ ] T100 Check reminder-agent logs for successful scheduler startup via `kubectl logs -l app=reminder-agent -n todo-app --tail=20`

---

## Phase 9: Helm Chart Deployment - Frontend

### Objective
Deploy frontend to Minikube cluster via Helm with backend connectivity.

### Tasks

- [ ] T101 Get Minikube IP address via `minikube ip` and store for frontend API URL
- [ ] T102 Update frontend Helm values or Dockerfile ARG with NEXT_PUBLIC_API_URL=http://<minikube-ip>:30081
- [ ] T103 Rebuild frontend Docker image with correct API URL if using build-time ARG
- [ ] T104 Install frontend Helm chart via `helm install frontend charts/todo-chatbot-frontend -n todo-app`
- [ ] T105 Wait for frontend pod to reach Running state via `kubectl wait --for=condition=Ready pod -l app=frontend -n todo-app --timeout=60s`
- [ ] T106 Verify frontend pod shows 1/1 READY via `kubectl get pods -n todo-app`
- [ ] T107 Check frontend logs for successful Next.js server startup via `kubectl logs -l app=frontend -n todo-app --tail=20`

---

## Phase 10: Service Connectivity Validation

### Objective
Verify inter-service communication and external access.

### Tasks

- [ ] T108 Get frontend NodePort service details via `kubectl get svc frontend-service -n todo-app`
- [ ] T109 Get backend API NodePort service details via `kubectl get svc api-service -n todo-app`
- [ ] T110 Verify frontend accessible from browser at http://<minikube-ip>:30080
- [ ] T111 Verify backend API accessible from browser at http://<minikube-ip>:30081/health
- [ ] T112 Test frontend-to-backend connectivity by loading homepage and checking browser network tab for API calls
- [ ] T113 Test auth-service internal connectivity via `kubectl exec -it <api-pod> -n todo-app -- curl http://auth-service:3001/health`
- [ ] T114 Verify backend-to-database connectivity by checking API service health endpoint includes database status

---

## Phase 11: Health Probe Validation

### Objective
Validate Kubernetes liveness and readiness probes function correctly.

### Tasks

- [ ] T115 Verify frontend liveness probe status via `kubectl describe pod <frontend-pod> -n todo-app | grep -A 5 Liveness`
- [ ] T116 Verify frontend readiness probe status via `kubectl describe pod <frontend-pod> -n todo-app | grep -A 5 Readiness`
- [ ] T117 Verify auth-service liveness probe status via `kubectl describe pod <auth-pod> -n todo-app | grep -A 5 Liveness`
- [ ] T118 Verify api-service liveness probe status via `kubectl describe pod <api-pod> -n todo-app | grep -A 5 Liveness`
- [ ] T119 Simulate pod failure by killing frontend process via `kubectl exec <frontend-pod> -n todo-app -- kill 1`
- [ ] T120 Verify Kubernetes automatically restarts failed frontend pod via `kubectl get events -n todo-app --sort-by='.lastTimestamp' | grep Killing`
- [ ] T121 Verify readiness probe removes unhealthy pod from service endpoints (simulate by temporarily breaking health endpoint if possible)

---

## Phase 12: Resource Monitoring

### Objective
Monitor pod resource usage and validate against defined limits.

### Tasks

- [ ] T122 Check node resource usage via `kubectl top node`
- [ ] T123 Check pod resource usage via `kubectl top pods -n todo-app`
- [ ] T124 Verify total pod memory usage is under 2Gi (4 pods × 512Mi limits)
- [ ] T125 Verify total pod CPU usage is under 2000m (4 pods × 500m limits)
- [ ] T126 Check for OOMKilled events via `kubectl get events -n todo-app | grep OOM`
- [ ] T127 Check for CPU throttling warnings via `kubectl describe pods -n todo-app | grep -i throttl`

---

## Phase 13: Manual kubectl Operations (AI Tools Unavailable)

### Objective
Execute manual kubectl operations and document common commands (kubectl-ai unavailable per research.md).

### Tasks

- [ ] T128 Scale frontend deployment to 2 replicas via `kubectl scale deployment frontend-deployment --replicas=2 -n todo-app`
- [ ] T129 Verify 2 frontend pods running via `kubectl get pods -l app=frontend -n todo-app`
- [ ] T130 Scale frontend back to 1 replica via `kubectl scale deployment frontend-deployment --replicas=1 -n todo-app`
- [ ] T131 Get detailed pod information via `kubectl describe pod <pod-name> -n todo-app`
- [ ] T132 Stream frontend logs via `kubectl logs -f <frontend-pod> -n todo-app`
- [ ] T133 Get all resources in namespace via `kubectl get all -n todo-app`
- [ ] T134 Get recent events sorted by timestamp via `kubectl get events -n todo-app --sort-by='.lastTimestamp'`
- [ ] T135 Execute shell in frontend pod via `kubectl exec -it <frontend-pod> -n todo-app -- /bin/sh`
- [ ] T136 Test Service DNS resolution from within pod via `kubectl exec -it <frontend-pod> -n todo-app -- nslookup api-service`
- [ ] T137 Document all useful kubectl commands in specs/phase-iv-kubernetes-deployment/quickstart.md

---

## Phase 14: Manual Cluster Health Analysis (Kagent Unavailable)

### Objective
Perform manual cluster health checks and identify optimization opportunities (Kagent unavailable per research.md).

### Tasks

- [ ] T138 Check cluster component status via `kubectl get componentstatuses` (deprecated but useful)
- [ ] T139 Check all system pods status via `kubectl get pods -n kube-system`
- [ ] T140 Verify metrics-server is running via `kubectl get pods -n kube-system -l k8s-app=metrics-server`
- [ ] T141 Review pod resource requests vs limits via `kubectl describe pods -n todo-app | grep -A 2 "Requests\|Limits"`
- [ ] T142 Identify pods without resource limits via `kubectl get pods -n todo-app -o json | jq '.items[] | select(.spec.containers[].resources.limits == null) | .metadata.name'`
- [ ] T143 Check for pending pods via `kubectl get pods -n todo-app | grep Pending`
- [ ] T144 Review pod restart counts via `kubectl get pods -n todo-app -o wide` and check RESTARTS column
- [ ] T145 Identify configuration improvements: non-root users, readonly filesystems, security contexts via `kubectl get pods -n todo-app -o yaml | grep -A 5 securityContext`
- [ ] T146 Document cluster health findings and optimization opportunities in specs/phase-iv-kubernetes-deployment/quickstart.md

---

## Phase 15: Failure Scenario Testing

### Objective
Test common failure scenarios and recovery mechanisms.

### Tasks

- [ ] T147 Simulate ImagePullBackOff by temporarily changing frontend image tag to non-existent version via `kubectl set image deployment/frontend-deployment frontend=todo-chatbot-frontend:nonexistent -n todo-app`
- [ ] T148 Verify pod enters ImagePullBackOff state via `kubectl get pods -n todo-app`
- [ ] T149 Check events for image pull error via `kubectl describe pod <failing-pod> -n todo-app | grep -A 5 Events`
- [ ] T150 Restore correct image tag via `kubectl set image deployment/frontend-deployment frontend=todo-chatbot-frontend:v1.0.0 -n todo-app`
- [ ] T151 Simulate database connection failure by temporarily providing invalid DATABASE_URL in secret
- [ ] T152 Verify api-service health endpoint returns 503 Service Unavailable
- [ ] T153 Verify api-service readiness probe fails and pod removed from service endpoints
- [ ] T154 Restore correct DATABASE_URL and verify api-service recovers
- [ ] T155 Simulate pod deletion via `kubectl delete pod <frontend-pod> -n todo-app`
- [ ] T156 Verify Deployment controller automatically creates replacement pod
- [ ] T157 Document failure scenarios and recovery procedures in specs/phase-iv-kubernetes-deployment/quickstart.md

---

## Phase 16: End-to-End Application Validation

### Objective
Verify all Phase III functionality works identically in Kubernetes deployment.

### Tasks

- [ ] T158 Access frontend at http://<minikube-ip>:30080 via browser
- [ ] T159 Test user registration flow via Better Auth
- [ ] T160 Test user login flow via Better Auth
- [ ] T161 Test todo creation via frontend UI
- [ ] T162 Test todo listing via frontend UI
- [ ] T163 Test todo completion via frontend UI
- [ ] T164 Test todo deletion via frontend UI
- [ ] T165 Test AI chatbot interaction via frontend UI
- [ ] T166 Verify all Phase III features work identically to local development
- [ ] T167 Test concurrent user sessions by opening multiple browser windows
- [ ] T168 Verify session persistence across pod restarts (test by deleting frontend pod during active session)

---

## Phase 17: Documentation & Cleanup

### Objective
Create comprehensive deployment documentation and validate completion criteria.

### Tasks

- [ ] T169 Create specs/phase-iv-kubernetes-deployment/quickstart.md with Minikube setup instructions
- [ ] T170 Document Docker image build commands in quickstart.md
- [ ] T171 Document Helm chart installation commands in quickstart.md
- [ ] T172 Document secret creation commands in quickstart.md
- [ ] T173 Document common kubectl troubleshooting commands in quickstart.md
- [ ] T174 Document access URLs (frontend, backend API, Swagger docs) in quickstart.md
- [ ] T175 Update root README.md with Phase IV Kubernetes deployment section
- [ ] T176 Create DEPLOYMENT.md in project root with detailed Minikube deployment guide
- [ ] T177 Document Minikube cluster teardown procedure via `minikube delete`
- [ ] T178 Document how to preserve data across cluster restarts (external Neon database persists automatically)
- [ ] T179 List all Helm chart templates files in quickstart.md for reference
- [ ] T180 Document environment variable to Kubernetes Secret/ConfigMap mapping

---

## Phase 18: Completion Validation

### Objective
Verify all Phase IV completion criteria from spec.md are met.

### Tasks

- [ ] T181 Verify frontend container builds successfully (checked via T020)
- [ ] T182 Verify backend containers build successfully (checked via T029, T037, T045)
- [ ] T183 Verify Helm charts install without errors (checked via T093, T104)
- [ ] T184 Verify frontend pod reaches Running 1/1 ready (checked via T105-T106)
- [ ] T185 Verify backend pods reach Running 1/1 ready (checked via T094-T096)
- [ ] T186 Verify frontend communicates with backend (checked via T112)
- [ ] T187 Verify application accessible from host machine (checked via T110, T158)
- [ ] T188 Verify Phase III functionality works identically (checked via T158-T166)
- [ ] T189 Verify environment variables correctly injected (checked via secret creation T090 and pod logs)
- [ ] T190 Verify Docker images use multi-stage builds (checked via Dockerfiles T015, T025, T034, T042)
- [ ] T191 Verify Helm charts are parameterized (checked via values.yaml creation T051, T067)
- [ ] T192 Verify health probes configured (checked via T057-T058, T073-T074, T077-T078)
- [ ] T193 Verify pods restart automatically on failure (checked via T119-T120)
- [ ] T194 Verify all components run locally with no cloud costs (confirmed via Minikube)
- [ ] T195 Verify Minikube cluster resource usage under 4GB RAM (checked via T122-T124)
- [ ] T196 Document AI tool unavailability and manual fallback strategies used (Gordon, kubectl-ai, Kagent unavailable per research.md)
- [ ] T197 Verify manual kubectl operations reduce command lookup needs (documented in T137)
- [ ] T198 Verify manual cluster analysis identified configuration improvements (documented in T146)
- [ ] T199 Confirm Phase IV deployment is production-like and ready for learning objectives
- [ ] T200 Mark Phase IV as COMPLETE and ready for handoff or next phase

---

## Task Summary

**Total Tasks**: 200
**Estimated Completion Time**: 8-12 hours (manual execution with AI tool fallbacks)

**Task Distribution by Phase**:
- Phase 0 (Environment Setup): 13 tasks
- Phase 1 (Frontend Containerization): 10 tasks
- Phase 2 (Auth Service): 9 tasks
- Phase 3 (API Service): 8 tasks
- Phase 4 (Reminder Agent): 7 tasks
- Phase 5 (Frontend Helm Chart): 16 tasks
- Phase 6 (Backend Helm Chart): 22 tasks
- Phase 7 (Secrets Management): 7 tasks
- Phase 8 (Backend Deployment): 8 tasks
- Phase 9 (Frontend Deployment): 7 tasks
- Phase 10 (Connectivity): 7 tasks
- Phase 11 (Health Probes): 7 tasks
- Phase 12 (Resource Monitoring): 6 tasks
- Phase 13 (Manual kubectl): 10 tasks
- Phase 14 (Manual Cluster Health): 9 tasks
- Phase 15 (Failure Scenarios): 11 tasks
- Phase 16 (E2E Validation): 11 tasks
- Phase 17 (Documentation): 12 tasks
- Phase 18 (Completion): 20 tasks

**Dependencies**:
- All phases must execute sequentially (each phase depends on previous phase completion)
- Within each phase, tasks are ordered by dependency
- Some tasks within phases can be parallelized (e.g., T014-T023 frontend containerization is independent of T024-T032 auth-service containerization in separate phases)

**Critical Path**:
Environment Setup → Containerization (all images) → Helm Charts (all charts) → Secrets → Deployment (backend then frontend) → Validation

**Notes**:
- AI DevOps tools (Gordon, kubectl-ai, Kagent) are unavailable per research.md - all tasks use manual Docker and kubectl commands
- All tasks are atomic and executable without additional context
- Each task has clear completion criteria
- No application code modifications (infrastructure only)
- External Neon PostgreSQL used (no in-cluster database deployment)
