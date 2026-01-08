# Phase IV: Local Kubernetes Deployment - Complete Specification

## Metadata
```yaml
feature: phase-iv-kubernetes-deployment
version: 1.0.0
stage: specification
created: 2025-12-30
updated: 2025-12-30
surface: agent
development_method: Spec-Driven Development (Spec → Plan → Tasks → Implementation)
status: draft
phase: IV
dependencies: [phase-iii-frontend-backend]
```

---

## 1. System Overview Spec

### 1.1 Purpose of Phase IV

Deploy the existing Cloud-Native Todo Chatbot application (from Phase III) to a local Kubernetes environment using Minikube with zero-cost, production-like infrastructure patterns for learning and development purposes.

**Primary Objectives:**
1. Containerize existing frontend and backend applications using Docker
2. Package applications as Helm charts for repeatable deployments
3. Deploy to local Minikube cluster with proper service exposure
4. Leverage AI DevOps tooling (Gordon, kubectl-ai, Kagent) for assisted operations
5. Establish observability patterns for pod health and diagnostics

**Key Principle:**
This is NOT a reimplementation of application logic. Phase IV takes the completed Phase III artifacts (Next.js frontend, Node.js auth service, Python FastAPI backend, PostgreSQL database) and deploys them as-is to Kubernetes infrastructure.

### 1.2 Scope Boundaries

#### IN SCOPE - Infrastructure & Deployment
- Docker image creation for frontend (Next.js) and backend (Node.js auth-service, Python FastAPI,reminder-agent)
- Dockerfile authoring with multi-stage builds for optimization
- Docker AI Agent (Gordon) integration for assisted Docker operations
- Minikube cluster setup and configuration
- Kubernetes manifests for Deployments, Services, ConfigMaps, Secrets
- Helm chart creation for frontend and backend components
- Local service exposure via NodePort or port-forwarding
- Environment configuration via ConfigMaps and Secrets
- AI-assisted Kubernetes operations using kubectl-ai and Kagent
- Pod health checks (liveness, readiness probes)
- Basic troubleshooting and cluster diagnostics
- Local PostgreSQL deployment or external Neon connection configuration

#### IN SCOPE - Technology Stack
- **Containerization:** Docker Desktop with Gordon AI agent
- **Orchestration:** Minikube (local Kubernetes)
- **Package Management:** Helm 3.x
- **AI DevOps Tools:**
  - Gordon (Docker Desktop AI for Dockerfile generation/optimization)
  - kubectl-ai (natural language Kubernetes operations)
  - Kagent (AI-powered cluster analysis and recommendations)
- **Container Registry:** Local Docker registry or Minikube's built-in registry

#### OUT OF SCOPE - Explicitly Excluded
- ❌ Any changes to application source code (frontend/backend logic)
- ❌ New product features or UI modifications
- ❌ Database schema changes or migrations
- ❌ Cloud provider deployments (AWS EKS, GCP GKE, Azure AKS)
- ❌ Production-grade security hardening (mTLS, network policies, RBAC)
- ❌ Horizontal Pod Autoscaling (HPA) or Vertical Pod Autoscaling (VPA)
- ❌ Ingress controllers (NGINX, Traefik, Istio)
- ❌ Service mesh implementations (Linkerd, Istio)
- ❌ GitOps tooling (ArgoCD, FluxCD)
- ❌ Monitoring stack (Prometheus, Grafana) - only basic kubectl diagnostics
- ❌ Centralized logging (ELK, Loki)
- ❌ CI/CD pipeline integration (GitHub Actions, Jenkins)
- ❌ Multi-cluster or multi-region deployments
- ❌ Certificate management (cert-manager, Let's Encrypt)
- ❌ Persistent storage provisioning beyond basic hostPath or emptyDir
- ❌ Cost optimization or resource quota management

#### BOUNDARY CLARIFICATIONS
- **Database:**
  - **Option A (Preferred):** Continue using external Neon PostgreSQL (no containerization required)
  - **Option B:** Deploy simple PostgreSQL StatefulSet in Minikube (if learning goal requires)
  - Decision should be made during `/sp.plan` phase
- **Configuration:**
  - Environment variables from Phase III MUST be preserved
  - Secrets MUST be stored in Kubernetes Secrets (not hardcoded)
  - ConfigMaps for non-sensitive configuration
- **Networking:**
  - Frontend-to-backend communication via Kubernetes Service DNS
  - Backend-to-database communication (either in-cluster or external)
  - External access via NodePort or `kubectl port-forward` (NOT LoadBalancer)

### 1.3 Success Criteria

**Functional Success:**
- [ ] Frontend container builds successfully from Dockerfile
- [ ] Backend container builds successfully from Dockerfile
- [ ] Helm chart installs without errors (`helm install todo-app ./charts/todo-app`)
- [ ] Frontend pod reaches Running state with 1/1 ready
- [ ] Backend pod reaches Running state with 1/1 ready
- [ ] Frontend can communicate with backend via Kubernetes Service
- [ ] Application is accessible from host machine (localhost:XXXXX)
- [ ] All existing Phase III functionality works identically (login, todos, AI chatbot)
- [ ] Environment variables correctly injected from ConfigMaps/Secrets

**Technical Success:**
- [ ] Docker images use multi-stage builds for size optimization
- [ ] Images pass vulnerability scanning (basic `docker scan` or equivalent)
- [ ] Helm charts are parameterized (values.yaml allows customization)
- [ ] Kubernetes health probes configured (liveness, readiness)
- [ ] Pods restart automatically on failure
- [ ] kubectl-ai can successfully execute common operations (scale, logs, describe)
- [ ] Kagent can analyze cluster health and provide recommendations

**Learning Success (Zero-Cost Validation):**
- [ ] All components run on local machine (no cloud costs)
- [ ] Minikube cluster resource usage < 4GB RAM
- [ ] Gordon provides helpful Dockerfile suggestions when invoked
- [ ] kubectl-ai reduces manual kubectl command lookup
- [ ] Kagent identifies at least one configuration improvement opportunity

---

## 2. Containerization Spec

### 2.1 Docker Image Requirements - Frontend (Next.js)

**Base Image:**
- Use official `node:18-alpine` or `node:20-alpine` for minimal footprint
- Alpine Linux for reduced image size (typically 50-100MB vs 200-300MB for full Debian)

**Multi-Stage Build Structure:**
```dockerfile
# Stage 1: Dependencies (builder)
FROM node:18-alpine AS deps
# Install production dependencies only

# Stage 2: Build (builder)
FROM node:18-alpine AS builder
# Copy dependencies from deps stage
# Run `next build` to generate optimized production build

# Stage 3: Runtime (production)
FROM node:18-alpine AS runner
# Copy only necessary artifacts from builder
# Run as non-root user
# Expose port 3000
# Start with `next start`
```

**Build Requirements:**
- MUST copy `package.json` and `package-lock.json` before other files (layer caching)
- MUST run `npm ci` (not `npm install`) for reproducible builds
- MUST build Next.js with `next build` in builder stage
- MUST copy only `.next`, `public`, `node_modules` (production only), `package.json` to final stage
- MUST NOT include `.env` files in image (use ConfigMaps/Secrets instead)
- MUST set `NODE_ENV=production`
- MUST run as non-root user (`USER node`)

**Environment Variable Handling:**
- Build-time variables (e.g., `NEXT_PUBLIC_API_URL`) injected via Dockerfile ARG
- Runtime variables (e.g., API keys) injected via Kubernetes Secrets/ConfigMaps
- NO hardcoded secrets in Dockerfile

**Port Exposure:**
- Expose port `3000` (Next.js default)
- Container listens on `0.0.0.0:3000`

**Health Check:**
- Optional `HEALTHCHECK` instruction (Kubernetes will handle via probes)

**Size Optimization Requirements:**
- Final image size MUST be < 200MB
- Use `.dockerignore` to exclude `node_modules`, `.git`, `.next` (before build), `*.md`

### 2.2 Docker Image Requirements - Backend (Node.js Auth Service)

**Base Image:**
- Use official `node:18-alpine` or `node:20-alpine`

**Multi-Stage Build Structure:**
```dockerfile
# Stage 1: Dependencies
FROM node:18-alpine AS deps
# Install production dependencies

# Stage 2: Build (if TypeScript)
FROM node:18-alpine AS builder
# Compile TypeScript to JavaScript (if applicable)

# Stage 3: Runtime
FROM node:18-alpine AS runner
# Copy compiled code and production dependencies
# Run as non-root user
# Expose port (check auth-service/package.json for actual port)
```

**Build Requirements:**
- MUST compile TypeScript if source is `.ts` files
- MUST copy `dist/` output (compiled JS) to final stage
- MUST NOT include `.ts` source files in production image
- MUST run as non-root user
- MUST set `NODE_ENV=production`

**Environment Variable Handling:**
- Database connection string from Kubernetes Secret
- Better Auth secrets from Kubernetes Secret
- NO hardcoded credentials

**Port Exposure:**
- Expose port based on auth-service configuration (verify in `backend/auth-service/package.json` scripts)

**Size Optimization:**
- Target < 150MB final image
- Exclude dev dependencies in final stage

### 2.3 Docker Image Requirements - Backend (Python FastAPI - if applicable)

**Note:** Verify if Phase III includes Python FastAPI backend (referenced in constitution but may not be implemented yet).

**Base Image (if applicable):**
- Use official `python:3.11-slim` or `python:3.11-alpine`

**Multi-Stage Build Structure:**
```dockerfile
# Stage 1: Dependencies
FROM python:3.11-slim AS builder
# Install dependencies via pip
# Use virtual environment

# Stage 2: Runtime
FROM python:3.11-slim AS runner
# Copy virtual environment from builder
# Run as non-root user
# Expose port 8000
# Start with `uvicorn` or `fastapi run`
```

**Build Requirements:**
- MUST use `requirements.txt` for dependencies
- MUST create virtual environment (`/opt/venv`)
- MUST NOT include build tools in final image
- MUST run as non-root user (create `appuser`)

**Environment Variable Handling:**
- Database URL from Kubernetes Secret
- OpenAI/Gemini API keys from Kubernetes Secret

**Port Exposure:**
- Expose port `8000` (FastAPI/Uvicorn default)

**Size Optimization:**
- Target < 300MB final image (Python images are larger than Node)
- Use `--no-cache-dir` with pip

### 2.4 Use of Docker AI Agent (Gordon)

**Gordon Overview:**
Gordon is Docker Desktop's built-in AI assistant for Docker operations.

**Allowed Use Cases:**
1. **Dockerfile Generation:** Ask Gordon to generate initial Dockerfile based on project structure
   - Example: "Generate a Dockerfile for a Next.js 16 production application"
2. **Dockerfile Optimization:** Request multi-stage build improvements
   - Example: "Optimize this Dockerfile for smaller image size"
3. **Build Error Diagnosis:** Paste build errors for troubleshooting suggestions
   - Example: "Why is my npm ci failing in Docker build?"
4. **Best Practices Validation:** Ask Gordon to review Dockerfile for security/performance issues
   - Example: "Review this Dockerfile for security vulnerabilities"

**Invocation Methods:**
- Docker Desktop GUI: Click "Ask Gordon" button
- Command-line: `docker help <command>` (if Gordon CLI integration available)
- Docker Desktop chat interface

**Safety Boundaries:**
- Gordon suggestions MUST be reviewed by human before applying
- Do NOT blindly trust generated Dockerfiles without validation
- Always test builds locally before committing to version control

### 2.5 Fallback Behavior if Gordon is Unavailable

**Gordon Unavailability Scenarios:**
- Docker Desktop not installed (using standalone Docker Engine)
- Gordon feature not enabled or unavailable in region
- Network connectivity issues

**Fallback Strategy:**
1. Use manually authored Dockerfiles based on official Docker best practices
2. Reference Dockerfile templates from official Next.js/Node.js documentation
3. Validate with `docker build` and `docker run` commands manually
4. Use `hadolint` (Dockerfile linter) for static analysis
5. Reference community-vetted Dockerfiles from GitHub repositories

**Required Manual Validations (Gordon or No Gordon):**
- [ ] Dockerfile builds without errors
- [ ] Container runs and serves application correctly
- [ ] Environment variables inject properly
- [ ] Image size is within acceptable limits
- [ ] No security vulnerabilities in base images (check with `docker scan`)

### 2.6 Docker Build & Push Workflow

**Local Build Commands:**
```bash
# Frontend
docker build -t todo-chatbot-frontend:latest ./frontend

# Backend (auth-service)
docker build -t todo-chatbot-backend:latest ./backend/auth-service

# Tag for Minikube (if using Minikube registry)
docker tag todo-chatbot-frontend:latest localhost:5000/todo-chatbot-frontend:latest
```

**Minikube Registry Usage:**
```bash
# Enable Minikube registry addon
minikube addons enable registry

# Build images inside Minikube's Docker daemon
eval $(minikube docker-env)
docker build -t todo-chatbot-frontend:latest ./frontend
docker build -t todo-chatbot-backend:latest ./backend/auth-service
```

**Image Tagging Convention:**
- Use semantic versioning: `todo-chatbot-frontend:v1.0.0`
- Use `latest` tag for current development version
- Include git commit SHA for traceability: `todo-chatbot-frontend:v1.0.0-abc123`

**Registry Options:**
- **Option A:** Minikube's built-in registry (recommended for local dev)
- **Option B:** Local Docker registry container (`docker run -d -p 5000:5000 registry:2`)
- **Option C:** Use Minikube's Docker daemon directly (no push required)

**Image Pull Policy:**
- Set `imagePullPolicy: IfNotPresent` in Kubernetes manifests for local images
- Set `imagePullPolicy: Always` only if using external registry

---

## 3. Local Kubernetes Environment Spec

### 3.1 Minikube Setup Assumptions

**Installation Prerequisites:**
- Minikube installed (version ≥ 1.30.0)
- Docker Desktop or Docker Engine installed as Minikube driver
- kubectl installed (version within 1 minor version of Minikube's Kubernetes)
- Helm installed (version ≥ 3.10.0)
- Minimum system resources: 4GB RAM, 2 CPUs, 20GB disk space

**Minikube Configuration:**
```bash
# Start Minikube with appropriate resources
minikube start --cpus=2 --memory=4096 --disk-size=20g --driver=docker

# Enable required addons
minikube addons enable metrics-server  # For resource monitoring
minikube addons enable registry        # For local image registry
```

**Kubernetes Version:**
- Target Kubernetes version: 1.28.x or 1.29.x (Minikube default)
- No specific version pinning required (use Minikube's default stable release)

**Driver Selection:**
- **Preferred:** Docker driver (cross-platform, consistent with Docker Desktop)
- **Alternatives:** VirtualBox, HyperKit, Hyper-V (platform-specific)
- Assumption: Docker driver is available and functional

### 3.2 Local Cluster Constraints

**Resource Limits:**
- Total cluster RAM: 4GB (shared across all pods and system components)
- Frontend pod limit: 512Mi RAM, 500m CPU
- Backend pod limit: 512Mi RAM, 500m CPU
- Database pod limit (if deployed): 1Gi RAM, 1000m CPU

**Performance Expectations:**
- Pod startup time: 10-30 seconds (slower than cloud due to local disk I/O)
- Image pull time: N/A (using local images)
- Application response time: Similar to Phase III local development

**Networking Constraints:**
- No external LoadBalancer support (Minikube limitation)
- Service exposure via NodePort (30000-32767 range) or `kubectl port-forward`
- DNS resolution works only within cluster (use Service names)

**Storage Constraints:**
- Persistent storage via `hostPath` (binds to Minikube VM filesystem)
- No dynamic provisioning by default (unless `storageclass` configured)
- Data persists only as long as Minikube cluster exists

### 3.3 Namespace and Resource Isolation Rules

**Namespace Strategy:**
- **Primary Namespace:** `todo-app` (all application components)
- **System Namespaces:** `kube-system`, `kube-public`, `default` (do not modify)

**Resource Naming Convention:**
```
{component}-{resource-type}
Examples:
- frontend-deployment
- backend-service
- postgres-statefulset
- app-config (ConfigMap)
- db-secret (Secret)
```

**Isolation Requirements:**
- All application resources MUST be created in `todo-app` namespace
- Use labels for component grouping:
  ```yaml
  labels:
    app: todo-chatbot
    component: frontend  # or backend, database
    managed-by: helm
  ```

**Resource Quotas (Optional for Learning):**
```yaml
# Optional: Limit total namespace resources
apiVersion: v1
kind: ResourceQuota
metadata:
  name: todo-app-quota
  namespace: todo-app
spec:
  hard:
    requests.cpu: "2"
    requests.memory: 2Gi
    limits.cpu: "4"
    limits.memory: 4Gi
```

**Cross-Namespace Access:**
- Not applicable (all components in single namespace)
- Future: If separating frontend/backend into different namespaces, use fully qualified Service DNS

---

## 4. Helm Chart Specification

### 4.1 Helm Chart Structure for Frontend

**Chart Directory Layout:**
```
charts/todo-chatbot-frontend/
├── Chart.yaml              # Chart metadata
├── values.yaml             # Default configuration values
├── templates/
│   ├── deployment.yaml     # Frontend Deployment
│   ├── service.yaml        # Frontend Service
│   ├── configmap.yaml      # Non-sensitive config
│   └── NOTES.txt           # Post-install instructions
└── .helmignore             # Files to exclude from chart
```

**Chart.yaml Metadata:**
```yaml
apiVersion: v2
name: todo-chatbot-frontend
description: Next.js frontend for Todo AI Chatbot
type: application
version: 1.0.0        # Chart version
appVersion: "1.0.0"   # Application version
keywords:
  - nextjs
  - frontend
  - todo
maintainers:
  - name: Your Name
    email: your.email@example.com
```

**values.yaml Structure:**
```yaml
replicaCount: 1

image:
  repository: todo-chatbot-frontend
  pullPolicy: IfNotPresent
  tag: "latest"

service:
  type: NodePort
  port: 3000
  nodePort: 30080  # Static NodePort for easy access

resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 250m
    memory: 256Mi

env:
  # Build-time variables (baked into image)
  NEXT_PUBLIC_API_URL: "http://localhost:30081"  # Backend NodePort

  # Runtime variables (from ConfigMap/Secret)
  # (Add as needed)

healthCheck:
  liveness:
    enabled: true
    path: /api/health  # Assumes Next.js health endpoint
    initialDelaySeconds: 10
    periodSeconds: 10
  readiness:
    enabled: true
    path: /api/health
    initialDelaySeconds: 5
    periodSeconds: 5
```

**deployment.yaml Template (Kubernetes Deployment):**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "todo-chatbot-frontend.fullname" . }}
  labels:
    {{- include "todo-chatbot-frontend.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      {{- include "todo-chatbot-frontend.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "todo-chatbot-frontend.selectorLabels" . | nindent 8 }}
    spec:
      containers:
      - name: frontend
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
        imagePullPolicy: {{ .Values.image.pullPolicy }}
        ports:
        - name: http
          containerPort: 3000
          protocol: TCP
        env:
        - name: NEXT_PUBLIC_API_URL
          value: {{ .Values.env.NEXT_PUBLIC_API_URL | quote }}
        {{- if .Values.healthCheck.liveness.enabled }}
        livenessProbe:
          httpGet:
            path: {{ .Values.healthCheck.liveness.path }}
            port: http
          initialDelaySeconds: {{ .Values.healthCheck.liveness.initialDelaySeconds }}
          periodSeconds: {{ .Values.healthCheck.liveness.periodSeconds }}
        {{- end }}
        {{- if .Values.healthCheck.readiness.enabled }}
        readinessProbe:
          httpGet:
            path: {{ .Values.healthCheck.readiness.path }}
            port: http
          initialDelaySeconds: {{ .Values.healthCheck.readiness.initialDelaySeconds }}
          periodSeconds: {{ .Values.healthCheck.readiness.periodSeconds }}
        {{- end }}
        resources:
          {{- toYaml .Values.resources | nindent 12 }}
```

**service.yaml Template (Kubernetes Service):**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ include "todo-chatbot-frontend.fullname" . }}
  labels:
    {{- include "todo-chatbot-frontend.labels" . | nindent 4 }}
spec:
  type: {{ .Values.service.type }}
  ports:
  - port: {{ .Values.service.port }}
    targetPort: http
    protocol: TCP
    name: http
    {{- if and (eq .Values.service.type "NodePort") .Values.service.nodePort }}
    nodePort: {{ .Values.service.nodePort }}
    {{- end }}
  selector:
    {{- include "todo-chatbot-frontend.selectorLabels" . | nindent 4 }}
```

### 4.2 Helm Chart Structure for Backend

**Chart Directory Layout:**
```
charts/todo-chatbot-backend/
├── Chart.yaml
├── values.yaml
├── templates/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── configmap.yaml      # Non-sensitive config
│   ├── secret.yaml         # Sensitive config (DB credentials, API keys)
│   └── NOTES.txt
└── .helmignore
```

**values.yaml Structure (Backend):**
```yaml
replicaCount: 1

image:
  repository: todo-chatbot-backend
  pullPolicy: IfNotPresent
  tag: "latest"

service:
  type: NodePort
  port: 3001  # Assuming auth-service port
  nodePort: 30081

resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 250m
    memory: 256Mi

env:
  # Non-sensitive config (from ConfigMap)
  NODE_ENV: production
  LOG_LEVEL: info

  # Sensitive config (from Secret - values injected at install time)
  # DATABASE_URL: "postgresql://user:pass@host/db"
  # AUTH_SECRET: "secret-key"
  # GEMINI_API_KEY: "api-key"

healthCheck:
  liveness:
    enabled: true
    path: /health  # Verify actual health endpoint
    initialDelaySeconds: 15
    periodSeconds: 10
  readiness:
    enabled: true
    path: /health
    initialDelaySeconds: 10
    periodSeconds: 5
```

**secret.yaml Template (Kubernetes Secret):**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: {{ include "todo-chatbot-backend.fullname" . }}-secret
  labels:
    {{- include "todo-chatbot-backend.labels" . | nindent 4 }}
type: Opaque
data:
  DATABASE_URL: {{ .Values.secrets.databaseUrl | b64enc | quote }}
  AUTH_SECRET: {{ .Values.secrets.authSecret | b64enc | quote }}
  GEMINI_API_KEY: {{ .Values.secrets.geminiApiKey | b64enc | quote }}
```

**deployment.yaml (Backend - Secret Injection):**
```yaml
spec:
  template:
    spec:
      containers:
      - name: backend
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: {{ include "todo-chatbot-backend.fullname" . }}-secret
              key: DATABASE_URL
        - name: AUTH_SECRET
          valueFrom:
            secretKeyRef:
              name: {{ include "todo-chatbot-backend.fullname" . }}-secret
              key: AUTH_SECRET
        - name: GEMINI_API_KEY
          valueFrom:
            secretKeyRef:
              name: {{ include "todo-chatbot-backend.fullname" . }}-secret
              key: GEMINI_API_KEY
```

### 4.3 Helm Values, Templates, and Configurable Parameters

**Parameterization Philosophy:**
- ALL environment-specific values MUST be in `values.yaml`
- NO hardcoded values in templates (use `{{ .Values.xxx }}` syntax)
- Support overriding values at install time: `helm install --set image.tag=v1.0.1`

**Common Configurable Parameters:**
- `replicaCount`: Number of pod replicas (default: 1 for local)
- `image.repository`: Container image name
- `image.tag`: Container image tag
- `image.pullPolicy`: Image pull policy (IfNotPresent, Always, Never)
- `service.type`: Service type (NodePort, ClusterIP)
- `service.port`: Service port
- `service.nodePort`: Static NodePort value (for NodePort type)
- `resources.requests/limits`: CPU and memory constraints
- `env.*`: Environment variables

**Helm Helper Templates (_helpers.tpl):**
```yaml
{{/*
Expand the name of the chart.
*/}}
{{- define "todo-chatbot-frontend.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "todo-chatbot-frontend.labels" -}}
helm.sh/chart: {{ include "todo-chatbot-frontend.chart" . }}
{{ include "todo-chatbot-frontend.selectorLabels" . }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "todo-chatbot-frontend.selectorLabels" -}}
app.kubernetes.io/name: {{ include "todo-chatbot-frontend.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
```

### 4.4 Replica Configuration and Service Exposure

**Replica Count:**
- **Default:** 1 replica per component (frontend, backend)
- **Rationale:** Local Minikube resource constraints; horizontal scaling not a learning goal
- **Future:** Can increase to 2-3 replicas to test load balancing behavior

**Service Exposure Strategies:**

**Strategy A: NodePort (Recommended for Learning)**
```yaml
# Frontend Service
type: NodePort
port: 3000
nodePort: 30080  # Access via http://$(minikube ip):30080

# Backend Service
type: NodePort
port: 3001
nodePort: 30081  # Access via http://$(minikube ip):30081
```

**Strategy B: Port-Forwarding (Alternative)**
```bash
# Forward frontend port
kubectl port-forward -n todo-app svc/frontend-service 3000:3000

# Forward backend port
kubectl port-forward -n todo-app svc/backend-service 3001:3001

# Access via http://localhost:3000 and http://localhost:3001
```

**Strategy C: ClusterIP + Minikube Tunnel (Advanced)**
```bash
# Use ClusterIP services
minikube tunnel  # Exposes services on localhost

# Access via http://localhost:3000 (no port-forward needed)
```

**Recommendation:**
Use NodePort for Phase IV to explicitly demonstrate Kubernetes service exposure concepts. Port-forwarding is easier but hides Kubernetes networking details.

---

## 5. AI-Assisted Kubernetes Operations Spec

### 5.1 Use Cases for kubectl-ai

**kubectl-ai Overview:**
kubectl-ai is a kubectl plugin that translates natural language queries into kubectl commands using AI.

**Allowed Use Cases:**

**1. Resource Inspection:**
- Query: "Show me all pods in the todo-app namespace"
- Expected: `kubectl get pods -n todo-app`

**2. Debugging Failed Pods:**
- Query: "Why is the frontend pod failing?"
- Expected: `kubectl describe pod <pod-name> -n todo-app` + analysis

**3. Log Retrieval:**
- Query: "Show logs for the backend pod"
- Expected: `kubectl logs <pod-name> -n todo-app`

**4. Scaling Operations:**
- Query: "Scale frontend to 2 replicas"
- Expected: `kubectl scale deployment frontend-deployment --replicas=2 -n todo-app`

**5. Configuration Inspection:**
- Query: "Show environment variables for backend pod"
- Expected: `kubectl get pod <pod-name> -n todo-app -o jsonpath='{.spec.containers[*].env}'`

**Installation:**
```bash
# Install kubectl-ai (example using krew)
kubectl krew install ai
```

**Usage Pattern:**
```bash
kubectl ai "natural language query here"
```

**Safety Guardrails:**
- kubectl-ai should show the generated command BEFORE executing (confirm with user)
- Do NOT use for destructive operations without confirmation (`delete`, `drain`, `cordon`)
- Always validate commands in non-production environment first

### 5.2 Use Cases for Kagent

**Kagent Overview:**
Kagent is an AI-powered Kubernetes agent that provides cluster analysis, optimization recommendations, and automated troubleshooting.

**Allowed Use Cases:**

**1. Cluster Health Analysis:**
- Query: "Analyze my Minikube cluster health"
- Expected Output: Report on node status, resource usage, pod health

**2. Resource Optimization:**
- Query: "Recommend resource limits for my pods"
- Expected Output: Suggested CPU/memory requests and limits based on actual usage

**3. Configuration Best Practices:**
- Query: "Review my deployment for security issues"
- Expected Output: Missing security contexts, non-root users, readonly filesystems

**4. Troubleshooting Assistance:**
- Query: "Why is my pod stuck in ImagePullBackOff?"
- Expected Output: Diagnosis (wrong image tag, missing registry credentials) + remediation steps

**5. Cost Optimization (N/A for Local):**
- Not applicable for Minikube, but useful pattern for future cloud deployments

**Installation:**
```bash
# Install Kagent (verify actual installation method from official docs)
# Example: helm install kagent kagent/kagent
```

**Usage Pattern:**
```bash
kagent analyze cluster
kagent recommend deployment frontend-deployment
kagent diagnose pod <pod-name>
```

### 5.3 Allowed AI-Assisted Operations

**Permitted Operations (Safe for Local Learning):**
- ✅ Deployment scaling (`kubectl scale`)
- ✅ Pod log retrieval (`kubectl logs`)
- ✅ Resource inspection (`kubectl get`, `kubectl describe`)
- ✅ Configuration viewing (`kubectl get configmap/secret -o yaml`)
- ✅ Port forwarding setup (`kubectl port-forward`)
- ✅ Health check validation (`kubectl get events`)
- ✅ Cluster health analysis (Kagent)
- ✅ Resource optimization recommendations (Kagent)

**Restricted Operations (Require Manual Confirmation):**
- ⚠️  Pod deletion (`kubectl delete pod`) - Only for testing restart behavior
- ⚠️  Deployment updates (`kubectl set image`) - Verify image exists first
- ⚠️  Secret modifications (`kubectl create secret`) - Avoid exposing secrets in shell history

**Prohibited Operations (Manual Only):**
- ❌ Namespace deletion (`kubectl delete namespace`) - Irreversible
- ❌ Cluster-wide operations (`kubectl delete all --all`) - Catastrophic
- ❌ RBAC changes (`kubectl create clusterrole`) - Security risk
- ❌ Node operations (`kubectl drain`, `kubectl cordon`) - Minikube has single node

### 5.4 Safety and Boundary Rules for AI Agents

**General Safety Rules:**
1. **Read-Only by Default:** Prefer `get`, `describe`, `logs` over `create`, `delete`, `update`
2. **Namespace Scoping:** Always specify `-n todo-app` to avoid affecting system namespaces
3. **Dry-Run First:** Use `--dry-run=client` for any create/update operations before applying
4. **Confirmation Required:** AI tools MUST show generated command and ask for confirmation before execution
5. **No Credential Exposure:** Never pass secrets directly in commands (use `kubectl create secret` with file input)

**kubectl-ai Specific Rules:**
- Set `KUBECTL_AI_CONFIRM=true` environment variable to require confirmation
- Review generated YAML manifests before applying (`kubectl ai "..." --dry-run=client -o yaml`)
- Do NOT use for multi-cluster operations (Minikube is single-cluster)

**Kagent Specific Rules:**
- Treat recommendations as suggestions, not requirements (validate against project constraints)
- Do NOT auto-apply Kagent recommendations without human review
- Use Kagent for learning, not as replacement for understanding Kubernetes concepts

**Fallback to Manual Commands:**
- If kubectl-ai generates incorrect command, run manual kubectl command
- If Kagent analysis is unclear, use standard `kubectl describe` and `kubectl logs`
- Always cross-reference AI suggestions with official Kubernetes documentation

---

## 6. Deployment Spec

### 6.1 Local Deployment Flow Using Helm + Minikube

**Step-by-Step Deployment Process:**

**Step 1: Prepare Minikube Environment**
```bash
# Start Minikube
minikube start --cpus=2 --memory=4096 --driver=docker

# Enable addons
minikube addons enable metrics-server
minikube addons enable registry

# Create namespace
kubectl create namespace todo-app
```

**Step 2: Build Docker Images**
```bash
# Use Minikube's Docker daemon (avoids push to registry)
eval $(minikube docker-env)

# Build frontend
docker build -t todo-chatbot-frontend:v1.0.0 ./frontend

# Build backend
docker build -t todo-chatbot-backend:v1.0.0 ./backend/auth-service

# Verify images
docker images | grep todo-chatbot
```

**Step 3: Prepare Secrets**
```bash
# Create Kubernetes secret for backend (one-time setup)
kubectl create secret generic backend-secrets \
  --from-literal=DATABASE_URL='postgresql://user:pass@neon.tech/db' \
  --from-literal=AUTH_SECRET='your-auth-secret' \
  --from-literal=GEMINI_API_KEY='your-gemini-key' \
  -n todo-app
```

**Step 4: Install Helm Charts**
```bash
# Install frontend
helm install frontend ./charts/todo-chatbot-frontend \
  --namespace todo-app \
  --set image.tag=v1.0.0

# Install backend
helm install backend ./charts/todo-chatbot-backend \
  --namespace todo-app \
  --set image.tag=v1.0.0
```

**Step 5: Verify Deployment**
```bash
# Check pod status
kubectl get pods -n todo-app

# Expected output:
# NAME                                READY   STATUS    RESTARTS   AGE
# frontend-deployment-xxx-yyy         1/1     Running   0          30s
# backend-deployment-zzz-www          1/1     Running   0          30s

# Check services
kubectl get svc -n todo-app

# Expected output:
# NAME                TYPE       CLUSTER-IP      EXTERNAL-IP   PORT(S)          AGE
# frontend-service    NodePort   10.96.10.10     <none>        3000:30080/TCP   30s
# backend-service     NodePort   10.96.10.11     <none>        3001:30081/TCP   30s
```

**Step 6: Access Application**
```bash
# Get Minikube IP
minikube ip  # Example: 192.168.49.2

# Access frontend
# Open browser: http://192.168.49.2:30080

# Verify backend health
curl http://192.168.49.2:30081/health
```

**Step 7: Validate Application Functionality**
- [ ] Frontend loads without errors
- [ ] User can log in via Better Auth
- [ ] User can create todos
- [ ] AI chatbot responds to messages
- [ ] Backend logs show successful database connections

### 6.2 Frontend ↔ Backend Connectivity Expectations

**Service Discovery via DNS:**
- Frontend communicates with backend using Kubernetes Service DNS
- Backend Service name: `backend-service.todo-app.svc.cluster.local`
- Shortened form: `backend-service` (within same namespace)

**Frontend Configuration:**
```javascript
// In Next.js environment variables or config
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://backend-service:3001'
```

**Problem:** `NEXT_PUBLIC_API_URL` is client-side (browser), cannot use cluster DNS.

**Solution:**
- **Option A (Server-Side Proxy):** Frontend proxies API requests to backend via Next.js API routes
  ```javascript
  // pages/api/proxy/[...path].js
  export default async function handler(req, res) {
    const response = await fetch(`http://backend-service:3001/${req.query.path.join('/')}`)
    const data = await response.json()
    res.json(data)
  }
  ```
- **Option B (NodePort from Browser):** Frontend uses `http://<minikube-ip>:30081` for direct backend access from browser
  ```javascript
  const API_URL = 'http://192.168.49.2:30081'  // Hardcoded or injected at build time
  ```

**Recommendation:** Use Option B for Phase IV simplicity (acknowledge this is not production-ready; Ingress would be used in production).

**Backend ↔ Database Connectivity:**
- If using external Neon PostgreSQL: Backend connects via `DATABASE_URL` secret (public internet)
- If using in-cluster PostgreSQL: Backend uses Service DNS `postgres-service.todo-app.svc.cluster.local`

### 6.3 Environment Configuration Handling

**Build-Time Configuration (Baked into Docker Image):**
- `NEXT_PUBLIC_API_URL`: Frontend's API endpoint (visible to browser)
- Injected via Dockerfile ARG during `docker build --build-arg NEXT_PUBLIC_API_URL=...`

**Runtime Configuration (Injected via Kubernetes):**

**Non-Sensitive (ConfigMap):**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: backend-config
  namespace: todo-app
data:
  NODE_ENV: "production"
  LOG_LEVEL: "info"
  PORT: "3001"
```

**Sensitive (Secret):**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: backend-secrets
  namespace: todo-app
type: Opaque
data:
  DATABASE_URL: <base64-encoded-value>
  AUTH_SECRET: <base64-encoded-value>
  GEMINI_API_KEY: <base64-encoded-value>
```

**Injection into Pods (Deployment):**
```yaml
spec:
  containers:
  - name: backend
    envFrom:
    - configMapRef:
        name: backend-config  # Inject all keys as env vars
    env:
    - name: DATABASE_URL
      valueFrom:
        secretKeyRef:
          name: backend-secrets
          key: DATABASE_URL
    - name: AUTH_SECRET
      valueFrom:
        secretKeyRef:
          name: backend-secrets
          key: AUTH_SECRET
```

**Configuration Update Process:**
1. Update ConfigMap or Secret: `kubectl edit configmap backend-config -n todo-app`
2. Restart pods to pick up changes: `kubectl rollout restart deployment backend-deployment -n todo-app`

---

## 7. Observability & Troubleshooting Spec

### 7.1 Pod Health Checks

**Liveness Probe:**
- **Purpose:** Detect when a pod is stuck and needs restart
- **Configuration (Frontend):**
  ```yaml
  livenessProbe:
    httpGet:
      path: /api/health  # Next.js health endpoint
      port: 3000
    initialDelaySeconds: 10
    periodSeconds: 10
    timeoutSeconds: 5
    failureThreshold: 3
  ```
- **Behavior:** Kubernetes restarts container if 3 consecutive probes fail

**Readiness Probe:**
- **Purpose:** Detect when a pod is ready to receive traffic
- **Configuration (Backend):**
  ```yaml
  readinessProbe:
    httpGet:
      path: /health  # Auth-service health endpoint
      port: 3001
    initialDelaySeconds: 5
    periodSeconds: 5
    timeoutSeconds: 3
    failureThreshold: 2
  ```
- **Behavior:** Kubernetes removes pod from Service endpoints if probe fails

**Startup Probe (Optional):**
- Use for slow-starting applications (database initialization)
- Delays liveness/readiness probes until first successful check

**Health Endpoint Requirements:**
- Frontend (`/api/health`): Return 200 OK with JSON `{"status": "healthy"}`
- Backend (`/health`): Return 200 OK with JSON `{"status": "healthy", "database": "connected"}`

**Verification:**
```bash
# Check probe status
kubectl describe pod <pod-name> -n todo-app | grep -A 5 "Liveness\|Readiness"

# Manually test health endpoint
kubectl port-forward pod/<pod-name> 3000:3000 -n todo-app
curl http://localhost:3000/api/health
```

### 7.2 Failure Diagnosis Using kubectl-ai

**Common Failure Scenarios:**

**Scenario 1: Pod Stuck in Pending**
```bash
kubectl ai "Why is frontend pod pending?"

# Expected diagnosis:
# - Insufficient resources (check node capacity)
# - Image pull failure (check events)
# - PVC not bound (if using persistent storage)
```

**Scenario 2: Pod Stuck in ImagePullBackOff**
```bash
kubectl ai "Diagnose ImagePullBackOff for backend pod"

# Expected diagnosis:
# - Image tag does not exist (check docker images)
# - ImagePullPolicy set to Always but no registry
# - Typo in image name
```

**Scenario 3: Pod CrashLoopBackOff**
```bash
kubectl ai "Why is backend pod crash looping?"

# Expected diagnosis:
# - Application error on startup (check logs)
# - Missing environment variable (check secrets/configmaps)
# - Database connection failure (check DATABASE_URL)
```

**Scenario 4: Service Not Accessible**
```bash
kubectl ai "Why can't I access frontend service on NodePort?"

# Expected diagnosis:
# - Pod not ready (check readiness probe)
# - Wrong nodePort value (check service YAML)
# - Firewall blocking port (check minikube ip)
```

**Manual Fallback Commands:**
```bash
# View pod events
kubectl describe pod <pod-name> -n todo-app

# Check logs
kubectl logs <pod-name> -n todo-app --tail=50

# Check service endpoints
kubectl get endpoints -n todo-app

# Check resource usage
kubectl top pod <pod-name> -n todo-app
```

### 7.3 Cluster Health Analysis Using Kagent

**Cluster-Wide Health Check:**
```bash
kagent analyze cluster

# Expected output:
# ✅ Node status: Ready (1/1 nodes)
# ✅ System pods: Running (kube-system namespace)
# ⚠️  Resource usage: 75% memory (consider scaling down)
# ✅ Persistent volumes: All bound
```

**Deployment-Specific Analysis:**
```bash
kagent recommend deployment frontend-deployment -n todo-app

# Expected recommendations:
# - Add resource limits (currently unbounded)
# - Enable readiness probe (missing)
# - Use non-root user (security)
# - Add pod disruption budget (high availability)
```

**Performance Diagnostics:**
```bash
kagent diagnose pod <pod-name> -n todo-app

# Expected output:
# - CPU throttling detected (increase limits)
# - OOMKilled events (increase memory)
# - Slow startup time (optimize Dockerfile)
```

**Actionable Insights:**
- Kagent SHOULD provide specific kubectl commands to fix issues
- Example: "Run `kubectl set resources deployment frontend --limits=cpu=500m,memory=512Mi`"

**Limitations (Minikube Context):**
- Cost optimization recommendations not applicable
- Multi-zone/region recommendations irrelevant
- Focus on resource efficiency and configuration best practices

---

## 8. Non-Goals & Constraints Spec

### 8.1 Explicitly Excluded from Phase IV

**Infrastructure & Platform:**
- ❌ Cloud provider deployments (AWS EKS, GCP GKE, Azure AKS, DigitalOcean Kubernetes)
- ❌ Managed Kubernetes services
- ❌ Multi-cluster setups (federation, cluster API)
- ❌ Production-grade HA configurations (multi-master, etcd clustering)

**Networking:**
- ❌ Ingress controllers (NGINX, Traefik, Kong, Istio Gateway)
- ❌ Service mesh (Istio, Linkerd, Consul Connect)
- ❌ Network policies (Calico, Cilium)
- ❌ DNS customization (CoreDNS configuration)
- ❌ TLS/SSL certificate management (cert-manager, Let's Encrypt)

**Security:**
- ❌ Advanced RBAC configurations (fine-grained permissions)
- ❌ Pod security policies (deprecated) or Pod Security Standards enforcement
- ❌ Secret encryption at rest (KMS integration)
- ❌ Image signing and verification (Notary, Cosign)
- ❌ Vulnerability scanning automation (Trivy, Snyk)
- ❌ Network segmentation beyond namespace isolation

**Observability & Monitoring:**
- ❌ Full monitoring stack (Prometheus, Grafana, Alertmanager)
- ❌ Centralized logging (ELK stack, Loki, Fluentd)
- ❌ Distributed tracing (Jaeger, Zipkin)
- ❌ APM tools (Datadog, New Relic)
- ❌ Custom metrics and dashboards

**Storage:**
- ❌ Dynamic persistent volume provisioning (StorageClasses)
- ❌ Persistent volume claims for application state
- ❌ StatefulSets for databases (optional: simple PostgreSQL StatefulSet allowed)
- ❌ Volume snapshots and backups

**Automation & GitOps:**
- ❌ CI/CD pipeline integration (GitHub Actions, GitLab CI, Jenkins)
- ❌ GitOps operators (ArgoCD, FluxCD)
- ❌ Automated rollback mechanisms
- ❌ Blue-green or canary deployments

**Scaling & Performance:**
- ❌ Horizontal Pod Autoscaler (HPA)
- ❌ Vertical Pod Autoscaler (VPA)
- ❌ Cluster Autoscaler
- ❌ Load testing and performance benchmarking
- ❌ Caching layers (Redis, Memcached)

**Application Changes:**
- ❌ New features or UI modifications
- ❌ Code refactoring or optimization
- ❌ Database schema changes
- ❌ API contract modifications

### 8.2 No Cloud Hosting

**Zero Cloud Costs Requirement:**
- ALL infrastructure MUST run on local machine (Minikube)
- NO cloud provider accounts required (AWS, GCP, Azure)
- NO external services requiring payment (except existing Neon PostgreSQL if already provisioned)

**Implications:**
- No external LoadBalancer (use NodePort or port-forward)
- No managed database (use external Neon or local PostgreSQL pod)
- No CDN for static assets (serve directly from Next.js)
- No cloud-native storage (use hostPath or emptyDir)

**Learning Trade-offs:**
- Gain: Cost-free learning of Kubernetes concepts
- Loss: No experience with cloud-specific integrations (EKS, GKE features)

### 8.3 No Advanced Security or Production Hardening

**Security Scope Limitations:**
- Basic authentication (Better Auth) carries over from Phase III
- Kubernetes Secrets for sensitive data (base64-encoded, NOT encrypted at rest)
- No mTLS between services
- No network policies (all pods can communicate freely)
- No image vulnerability scanning in pipeline
- No runtime security monitoring (Falco, Sysdig)

**Production Readiness Gaps:**
- No resource quotas or limit ranges enforced
- No pod disruption budgets
- No multi-zone replication
- No automated backups
- No disaster recovery plan

**Rationale:**
Phase IV focuses on deployment mechanics, not production hardening. Security and reliability patterns are future learning phases.

---

## 9. Spec-Driven Infrastructure Notes

### 9.1 How These Specs Support Future Spec-Driven Automation

**Current Phase IV Scope:**
- Manual execution of Helm installs and kubectl commands
- Human-driven troubleshooting with AI tool assistance

**Future Automation Opportunities:**

**1. Infrastructure as Code (IaC) Automation:**
```yaml
# Future: specs/phase-v-automation/plan.md
- Terraform modules for Minikube provisioning
- Automated Helm value generation from spec.md
- GitOps-driven deployments via ArgoCD
```

**2. Spec-to-Kubernetes Manifest Generation:**
```yaml
# Future: Claude Code skill to generate Helm charts from spec.md
/sp.k8s-chart --spec=specs/phase-iv-kubernetes-deployment/spec.md
# Output: charts/todo-chatbot/templates/*.yaml
```

**3. Automated Testing of Kubernetes Deployments:**
```yaml
# Future: specs/phase-iv-kubernetes-deployment/tasks.md
- Task: "Validate frontend pod reaches Running state"
  Test: "kubectl wait --for=condition=Ready pod -l app=frontend --timeout=60s"
```

**4. AI-Driven Infrastructure Optimization:**
```yaml
# Future: Kagent integration with spec.md constraints
- Kagent reads resource limits from spec.md
- Auto-generates recommendations aligned with spec constraints
```

### 9.2 Blueprint Readiness for Claude Code Agent Skills (Conceptual Only)

**Conceptual Future Skills (Not Implemented in Phase IV):**

**Skill 1: /sp.k8s-deploy**
```yaml
Description: Deploy application to Kubernetes based on spec.md
Inputs:
  - spec-file: specs/phase-iv-kubernetes-deployment/spec.md
  - environment: local|staging|production
Process:
  1. Parse spec.md for container requirements
  2. Generate Dockerfiles if missing
  3. Build Docker images
  4. Generate Helm charts from spec templates
  5. Install Helm charts to target cluster
  6. Validate deployment success
Output:
  - Deployment status report
  - Access URLs for services
```

**Skill 2: /sp.k8s-troubleshoot**
```yaml
Description: Diagnose and fix Kubernetes deployment issues
Inputs:
  - namespace: todo-app
  - component: frontend|backend|all
Process:
  1. Run kubectl-ai diagnostics
  2. Run Kagent cluster analysis
  3. Check pod logs and events
  4. Cross-reference spec.md health check requirements
  5. Generate remediation plan
Output:
  - Diagnosis report
  - Suggested kubectl fix commands
```

**Skill 3: /sp.k8s-optimize**
```yaml
Description: Optimize Kubernetes resources based on spec constraints
Inputs:
  - spec-file: specs/phase-iv-kubernetes-deployment/spec.md
Process:
  1. Read resource limits from spec.md
  2. Query actual resource usage (kubectl top)
  3. Compare actual vs spec-defined limits
  4. Generate rightsizing recommendations
  5. Propose updated values.yaml
Output:
  - Optimization report
  - Updated Helm values.yaml
```

**Implementation Timeline:**
- Phase IV: Manual execution (current scope)
- Phase V: Semi-automated skills (human approval required)
- Phase VI: Fully automated infrastructure management

**Spec-Driven Development Philosophy Applied to Infrastructure:**
- Spec.md defines WHAT to deploy (contracts, resources, constraints)
- Plan.md defines HOW to deploy (Helm, Dockerfiles, Minikube setup)
- Tasks.md defines step-by-step deployment checklist
- Claude Code Agent executes tasks autonomously (future state)

**Current Phase IV Limitations:**
- No automated skill execution (all manual)
- Specs serve as documentation and planning artifacts
- Human executes Helm and kubectl commands directly

---

## 10. Acceptance Criteria (Definition of Done)

### 10.1 Functional Acceptance

- [ ] Frontend Docker image builds successfully without errors
- [ ] Backend Docker image builds successfully without errors
- [ ] Frontend Helm chart installs without errors
- [ ] Backend Helm chart installs without errors
- [ ] Frontend pod reaches `Running` state within 60 seconds
- [ ] Backend pod reaches `Running` state within 60 seconds
- [ ] Frontend pod shows `1/1 READY` in `kubectl get pods`
- [ ] Backend pod shows `1/1 READY` in `kubectl get pods`
- [ ] Frontend accessible via browser at `http://<minikube-ip>:30080`
- [ ] Backend health endpoint returns 200 OK at `http://<minikube-ip>:30081/health`
- [ ] User can log in to application via Better Auth
- [ ] User can create todo items
- [ ] User can interact with AI chatbot
- [ ] All Phase III functionality works identically in Kubernetes deployment

### 10.2 Technical Acceptance

- [ ] Docker images use multi-stage builds
- [ ] Frontend image size < 200MB
- [ ] Backend image size < 150MB
- [ ] No hardcoded secrets in Dockerfiles or Helm charts
- [ ] All sensitive config stored in Kubernetes Secrets
- [ ] All non-sensitive config stored in Kubernetes ConfigMaps
- [ ] Health probes configured (liveness and readiness)
- [ ] Pods restart automatically on failure (verified by killing pod)
- [ ] Resource limits defined for all pods (CPU and memory)
- [ ] Images use non-root user (verified with `docker run --rm <image> whoami`)
- [ ] Helm charts are parameterized (can override values at install time)
- [ ] Namespace isolation works (all resources in `todo-app` namespace)

### 10.3 AI Tooling Acceptance

- [ ] Gordon provides valid Dockerfile suggestions when queried (or manual Dockerfiles pass validation)
- [ ] kubectl-ai successfully executes at least 3 different query types (logs, describe, scale)
- [ ] Kagent analyzes cluster and provides at least 1 actionable recommendation
- [ ] AI-generated kubectl commands are syntactically correct
- [ ] All AI tool suggestions are validated before execution (human-in-the-loop)

### 10.4 Documentation Acceptance

- [ ] README.md includes Minikube setup instructions
- [ ] README.md includes Docker build instructions
- [ ] README.md includes Helm install commands
- [ ] README.md includes troubleshooting section
- [ ] Helm chart NOTES.txt displays post-install access instructions
- [ ] Kubernetes manifests include comments explaining key configurations
- [ ] Environment variable documentation updated for Kubernetes deployment

### 10.5 Learning Objectives Achieved

- [ ] Successfully deployed multi-container application to Kubernetes
- [ ] Understood Docker multi-stage builds
- [ ] Created parameterized Helm charts
- [ ] Used NodePort for service exposure
- [ ] Configured health probes for automatic restarts
- [ ] Managed secrets securely with Kubernetes Secrets
- [ ] Used AI tools to assist with Kubernetes operations
- [ ] Diagnosed and fixed at least 1 pod failure scenario

---

## 11. Risks & Mitigations

### Risk 1: Docker Build Failures Due to Dependency Issues
- **Impact:** Cannot create container images, blocks entire deployment
- **Probability:** Medium (npm/pip dependency conflicts)
- **Mitigation:**
  - Lock dependency versions in package.json / requirements.txt
  - Use `npm ci` instead of `npm install` for reproducible builds
  - Test Docker builds locally before committing Dockerfiles
  - Use Gordon to validate Dockerfile syntax and best practices

### Risk 2: Minikube Resource Exhaustion
- **Impact:** Pods stuck in Pending, OOMKilled, or slow performance
- **Probability:** Medium (4GB RAM limit for all pods + system)
- **Mitigation:**
  - Set conservative resource limits (512Mi per pod)
  - Monitor resource usage with `kubectl top pods`
  - Reduce replica count to 1 per component
  - Use `minikube stop` when not actively developing

### Risk 3: Image Pull Policy Misconfiguration
- **Impact:** Pods stuck in ImagePullBackOff, unable to start
- **Probability:** Medium (common mistake for local images)
- **Mitigation:**
  - Set `imagePullPolicy: IfNotPresent` for local images
  - Use `eval $(minikube docker-env)` to build images in Minikube's Docker
  - Verify image exists with `minikube ssh -- docker images`

### Risk 4: Service DNS Resolution Issues
- **Impact:** Frontend cannot communicate with backend
- **Probability:** Low (Kubernetes DNS is reliable)
- **Mitigation:**
  - Use fully qualified Service names (e.g., `backend-service.todo-app.svc.cluster.local`)
  - Test DNS resolution: `kubectl run -it --rm debug --image=busybox -- nslookup backend-service`
  - Fallback to ClusterIP for inter-service communication

### Risk 5: kubectl-ai or Kagent Unavailable or Inaccurate
- **Impact:** Loss of AI-assisted operations, slower troubleshooting
- **Probability:** Medium (tools are experimental)
- **Mitigation:**
  - Maintain manual kubectl command knowledge (don't rely solely on AI)
  - Validate all AI-generated commands before execution
  - Fallback to `kubectl` documentation and community resources

### Kill Switch
- **Command:** `minikube delete` (destroys entire cluster)
- **Backup:** Export Helm values before deletion: `helm get values frontend -n todo-app > frontend-values-backup.yaml`

---

## 12. Open Questions (Requires Clarification Before `/sp.plan`)

1. **Database Deployment Strategy:**
   - Should we deploy PostgreSQL in Kubernetes (StatefulSet) or continue using external Neon?
   - If in-cluster: Do we need persistent storage or is ephemeral acceptable for learning?

2. **Frontend-Backend Communication:**
   - Should frontend use Kubernetes Service DNS (requires server-side proxy) or NodePort from browser?
   - Preference for production-like (Ingress would be needed) vs. simplicity (NodePort)?

3. **Health Endpoint Availability:**
   - Does Phase III implementation include `/api/health` (frontend) and `/health` (backend)?
   - If not, should we add minimal health endpoints or skip health probes?

4. **Gordon Availability:**
   - Is Docker Desktop with Gordon AI agent installed and accessible?
   - If not available, proceed with manual Dockerfiles?

5. **kubectl-ai and Kagent Installation:**
   - Are these tools already installed or should setup instructions be included?
   - Are there licensing or cost implications for these tools?

6. **Minikube Driver Preference:**
   - Docker driver confirmed as available on development machine?
   - Any platform-specific constraints (Windows, macOS, Linux)?

---

## Appendix A: Technology Stack Version Matrix

| Component | Technology | Version | Installation Method |
|-----------|-----------|---------|---------------------|
| Container Runtime | Docker Desktop | 24.x+ | https://docker.com/get-started |
| Container Orchestration | Minikube | 1.30.0+ | `brew install minikube` or official installer |
| CLI Tool | kubectl | 1.28.x+ | Bundled with Minikube |
| Package Manager | Helm | 3.10.0+ | `brew install helm` or official installer |
| AI Docker Assistant | Gordon | Latest | Bundled with Docker Desktop |
| AI kubectl Plugin | kubectl-ai | Latest | `kubectl krew install ai` |
| AI Cluster Agent | Kagent | Latest | Verify official installation method |
| Image Registry (Optional) | Docker Registry | 2.x | `minikube addons enable registry` |

---

## Appendix B: Example Commands Reference

### Minikube Commands
```bash
# Start cluster
minikube start --cpus=2 --memory=4096 --driver=docker

# Stop cluster (preserves state)
minikube stop

# Delete cluster (destroys all data)
minikube delete

# Get cluster IP
minikube ip

# SSH into Minikube VM
minikube ssh

# Enable addon
minikube addons enable metrics-server

# Use Minikube's Docker daemon
eval $(minikube docker-env)

# Tunnel for LoadBalancer services (if used)
minikube tunnel
```

### Docker Commands
```bash
# Build frontend image
docker build -t todo-chatbot-frontend:v1.0.0 ./frontend

# List images
docker images | grep todo-chatbot

# Run container locally for testing
docker run -p 3000:3000 todo-chatbot-frontend:v1.0.0

# Scan for vulnerabilities (if Docker Scout available)
docker scan todo-chatbot-frontend:v1.0.0

# Ask Gordon for help (Docker Desktop GUI)
# Click "Ask Gordon" button in Docker Desktop
```

### Helm Commands
```bash
# Install chart
helm install frontend ./charts/todo-chatbot-frontend -n todo-app

# Upgrade chart (after changes)
helm upgrade frontend ./charts/todo-chatbot-frontend -n todo-app

# Uninstall chart
helm uninstall frontend -n todo-app

# List installed charts
helm list -n todo-app

# Get values
helm get values frontend -n todo-app

# Override values at install
helm install frontend ./charts/todo-chatbot-frontend \
  --set image.tag=v2.0.0 \
  --set replicaCount=2 \
  -n todo-app
```

### kubectl Commands
```bash
# Get pods
kubectl get pods -n todo-app

# Describe pod
kubectl describe pod <pod-name> -n todo-app

# Get logs
kubectl logs <pod-name> -n todo-app --tail=100 -f

# Get services
kubectl get svc -n todo-app

# Port forward
kubectl port-forward svc/frontend-service 3000:3000 -n todo-app

# Scale deployment
kubectl scale deployment frontend-deployment --replicas=2 -n todo-app

# Delete pod (to test restart)
kubectl delete pod <pod-name> -n todo-app

# Get events
kubectl get events -n todo-app --sort-by='.lastTimestamp'

# Resource usage
kubectl top pod -n todo-app
kubectl top node

# Execute command in pod
kubectl exec -it <pod-name> -n todo-app -- /bin/sh
```

### kubectl-ai Commands
```bash
# Install (if using krew)
kubectl krew install ai

# Example queries
kubectl ai "show me all pods in todo-app namespace"
kubectl ai "why is my frontend pod failing"
kubectl ai "scale backend deployment to 2 replicas"
kubectl ai "show logs for the backend pod"
```

### Kagent Commands
```bash
# Analyze cluster
kagent analyze cluster

# Get deployment recommendations
kagent recommend deployment frontend-deployment -n todo-app

# Diagnose pod
kagent diagnose pod <pod-name> -n todo-app
```

---

## Appendix C: Expected File Structure After Phase IV

```
Todo-Full-Stack-Web-Application/
├── frontend/
│   ├── Dockerfile                    # NEW: Multi-stage build for Next.js
│   ├── .dockerignore                 # NEW: Exclude unnecessary files
│   ├── (existing Phase III files)
│
├── backend/
│   ├── auth-service/
│   │   ├── Dockerfile                # NEW: Multi-stage build for Node.js
│   │   ├── .dockerignore             # NEW
│   │   ├── (existing Phase III files)
│
├── charts/                           # NEW: Helm charts directory
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
│   └── todo-chatbot-backend/
│       ├── Chart.yaml
│       ├── values.yaml
│       ├── templates/
│       │   ├── deployment.yaml
│       │   ├── service.yaml
│       │   ├── configmap.yaml
│       │   ├── secret.yaml
│       │   ├── _helpers.tpl
│       │   └── NOTES.txt
│       └── .helmignore
│
├── k8s/                              # NEW: Optional raw Kubernetes manifests (if not using Helm)
│   ├── namespace.yaml
│   ├── frontend/
│   └── backend/
│
├── specs/
│   ├── phase-iv-kubernetes-deployment/
│   │   ├── spec.md                   # THIS FILE
│   │   ├── plan.md                   # Generated by /sp.plan
│   │   └── tasks.md                  # Generated by /sp.tasks
│
├── .env.example                      # Updated with Kubernetes-specific vars
├── README.md                         # Updated with Kubernetes deployment instructions
└── DEPLOYMENT.md                     # NEW: Detailed deployment guide for Minikube
```

---

**END OF PHASE IV SPECIFICATION**

This specification is COMPLETE, NON-OVERLAPPING, and IMPLEMENTATION-READY for `/sp.plan` and `/sp.tasks` execution via the Spec-Driven Development workflow.
