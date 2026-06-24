# Phase V: Cloud Deployment - Focused Task Breakdown
## Deployment Tasks Only (Features Already Implemented)

**Context:** All application features, Kafka integration, Dapr integration, and consumer services are already implemented. This task list focuses ONLY on deploying the existing application to Minikube locally and then to cloud Kubernetes.

---

## PHASE 5: Local Deployment - Minikube (Days 1-2)

### 5.1 Minikube Environment Setup

#### Task 5.1.1: Install and Configure Minikube
**Task ID:** P5-T1  
**Priority:** Critical  
**Estimated Time:** 30 minutes  
**Dependencies:** None

**Description:**
Install Minikube and start cluster with adequate resources.

**Manual Steps:**
```bash
# Install Minikube (if not already installed)
# macOS
brew install minikube

# Linux
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Start Minikube with adequate resources
minikube start --cpus=4 --memory=8192 --disk-size=20g --driver=docker

# Verify
kubectl get nodes
minikube status
```

**Acceptance Criteria:**
- Minikube running successfully
- kubectl can connect to cluster
- Node shows as Ready
- Sufficient resources allocated

**Verification:**
```bash
kubectl cluster-info
kubectl get nodes
# Should show: minikube   Ready    control-plane   <time>   v1.xx.x
```

---

#### Task 5.1.2: Install Required Tools
**Task ID:** P5-T2  
**Priority:** Critical  
**Estimated Time:** 30 minutes  
**Dependencies:** P5-T1

**Description:**
Install Helm, Dapr CLI, and other required Kubernetes tools.

**Manual Steps:**
```bash
# Install Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
helm version

# Install Dapr CLI
curl -fsSL https://raw.githubusercontent.com/dapr/cli/master/install/install.sh | bash
dapr --version

# Verify kubectl
kubectl version --client
```

**Acceptance Criteria:**
- Helm 3.x installed
- Dapr CLI installed
- kubectl working
- All tools accessible in PATH

---

### 5.2 Deploy Kafka on Minikube

#### Task 5.2.1: Create Kafka Namespace and Install Strimzi Operator
**Task ID:** P5-T3  
**Priority:** Critical  
**Estimated Time:** 1 hour  
**Dependencies:** P5-T1

**Description:**
Set up Kafka namespace and install Strimzi operator for managing Kafka on Kubernetes.

**Manual Steps:**
```bash
# Create namespace
kubectl create namespace kafka

# Install Strimzi operator
kubectl create -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka

# Wait for operator to be ready
kubectl wait deployment/strimzi-cluster-operator \
  --for=condition=Available \
  --timeout=300s \
  -n kafka

# Verify operator is running
kubectl get pods -n kafka
```

**Acceptance Criteria:**
- kafka namespace created
- Strimzi operator pod running
- Operator logs show no errors
- CRDs installed (check with `kubectl get crd | grep kafka`)

**Verification:**
```bash
kubectl get pods -n kafka
# Should show: strimzi-cluster-operator-xxx   Running
```

---

#### Task 5.2.2: Create Kafka Cluster Configuration
**Task ID:** P5-T4  
**Priority:** Critical  
**Estimated Time:** 45 minutes  
**Dependencies:** None (can be done in parallel with T3)

**Description:**
Create Kafka cluster YAML configuration for Minikube deployment.

**Claude Code Prompt:**
```
Create Kafka cluster configuration for Minikube.

Location: k8s/kafka/kafka-cluster.yaml

apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: taskflow-kafka
  namespace: kafka
spec:
  kafka:
    version: 3.6.0
    replicas: 1  # Single replica for Minikube
    listeners:
      - name: plain
        port: 9092
        type: internal
        tls: false
    config:
      offsets.topic.replication.factor: 1
      transaction.state.log.replication.factor: 1
      transaction.state.log.min.isr: 1
      default.replication.factor: 1
      min.insync.replicas: 1
      inter.broker.protocol.version: "3.6"
    storage:
      type: ephemeral  # For Minikube, persistent-claim for production
  zookeeper:
    replicas: 1
    storage:
      type: ephemeral
  entityOperator:
    topicOperator: {}
    userOperator: {}

This is optimized for Minikube with minimal resources.
```

**Acceptance Criteria:**
- YAML file created in k8s/kafka/ directory
- Valid Kafka CRD format
- Configuration suitable for Minikube resources
- Can be applied without errors

---

#### Task 5.2.3: Deploy Kafka Cluster
**Task ID:** P5-T5  
**Priority:** Critical  
**Estimated Time:** 1 hour  
**Dependencies:** P5-T3, P5-T4

**Description:**
Deploy Kafka cluster to Minikube and wait for it to be ready.

**Manual Steps:**
```bash
# Apply Kafka cluster configuration
kubectl apply -f k8s/kafka/kafka-cluster.yaml -n kafka

# Watch the deployment (this takes 2-5 minutes)
kubectl get kafka -n kafka -w

# Wait for Ready status
kubectl wait kafka/taskflow-kafka --for=condition=Ready --timeout=600s -n kafka

# Verify all pods are running
kubectl get pods -n kafka

# Check Kafka broker logs
kubectl logs -n kafka taskflow-kafka-kafka-0 -c kafka
```

**Acceptance Criteria:**
- Kafka cluster shows Ready status
- Kafka broker pods running (taskflow-kafka-kafka-0)
- Zookeeper pods running (taskflow-kafka-zookeeper-0)
- Entity operator pods running
- No errors in logs

**Verification:**
```bash
kubectl get kafka -n kafka
# Should show: taskflow-kafka   True

kubectl get pods -n kafka
# Should show multiple running pods:
# - taskflow-kafka-kafka-0
# - taskflow-kafka-zookeeper-0
# - taskflow-kafka-entity-operator-xxx
```

---

#### Task 5.2.4: Create Kafka Topics
**Task ID:** P5-T6  
**Priority:** Critical  
**Estimated Time:** 45 minutes  
**Dependencies:** P5-T5

**Description:**
Create all required Kafka topics for the application.

**Claude Code Prompt:**
```
Create Kafka topics configuration.

Location: k8s/kafka/topics.yaml

Create 4 KafkaTopic resources:

---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: task-events
  namespace: kafka
  labels:
    strimzi.io/cluster: taskflow-kafka
spec:
  partitions: 3
  replicas: 1
  config:
    retention.ms: 604800000  # 7 days
    segment.bytes: 1073741824

---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: reminders
  namespace: kafka
  labels:
    strimzi.io/cluster: taskflow-kafka
spec:
  partitions: 2
  replicas: 1
  config:
    retention.ms: 604800000  # 7 days

---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: task-updates
  namespace: kafka
  labels:
    strimzi.io/cluster: taskflow-kafka
spec:
  partitions: 2
  replicas: 1
  config:
    retention.ms: 86400000  # 1 day

---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: audit-logs
  namespace: kafka
  labels:
    strimzi.io/cluster: taskflow-kafka
spec:
  partitions: 1
  replicas: 1
  config:
    retention.ms: 2592000000  # 30 days
```

**Manual Steps:**
```bash
# Apply topics
kubectl apply -f k8s/kafka/topics.yaml -n kafka

# Wait for topics to be ready
kubectl wait kafkatopic/task-events --for=condition=Ready --timeout=60s -n kafka
kubectl wait kafkatopic/reminders --for=condition=Ready --timeout=60s -n kafka
kubectl wait kafkatopic/task-updates --for=condition=Ready --timeout=60s -n kafka
kubectl wait kafkatopic/audit-logs --for=condition=Ready --timeout=60s -n kafka

# Verify topics created
kubectl get kafkatopic -n kafka

# Alternative: Check directly in Kafka
kubectl exec -it taskflow-kafka-kafka-0 -n kafka -- \
  bin/kafka-topics.sh --list --bootstrap-server localhost:9092
```

**Acceptance Criteria:**
- All 4 topics created successfully
- Topics show Ready status
- Correct partition counts
- Retention policies applied

---

### 5.3 Deploy Dapr on Minikube

#### Task 5.3.1: Initialize Dapr on Kubernetes
**Task ID:** P5-T7  
**Priority:** Critical  
**Estimated Time:** 30 minutes  
**Dependencies:** P5-T1

**Description:**
Install Dapr runtime on Minikube cluster.

**Manual Steps:**
```bash
# Initialize Dapr on Kubernetes
dapr init -k

# Wait for Dapr system pods to be ready
kubectl wait --for=condition=ready pod \
  --all \
  -n dapr-system \
  --timeout=300s

# Verify Dapr installation
dapr status -k

# Check Dapr pods
kubectl get pods -n dapr-system
```

**Acceptance Criteria:**
- Dapr control plane pods running in dapr-system namespace
- dapr-operator, dapr-sidecar-injector, dapr-placement-server pods healthy
- `dapr status -k` shows all components running
- No errors in Dapr logs

**Verification:**
```bash
dapr status -k
# Should show:
# NAME                   NAMESPACE    HEALTHY  STATUS   REPLICAS  VERSION  AGE  CREATED
# dapr-operator          dapr-system  True     Running  1         1.xx.x   ...
# dapr-sidecar-injector  dapr-system  True     Running  1         1.xx.x   ...
# dapr-placement-server  dapr-system  True     Running  1         1.xx.x   ...
```

---

#### Task 5.3.2: Create Dapr Components Configuration
**Task ID:** P5-T8  
**Priority:** Critical  
**Estimated Time:** 1 hour  
**Dependencies:** P5-T6 (Kafka topics ready)

**Description:**
Create Dapr component YAML files for Pub/Sub, State Store, and Secrets.

**Claude Code Prompt:**
```
Create Dapr components for Minikube deployment.

Location: k8s/dapr-components/

Create 3 files:

1. k8s/dapr-components/pubsub.yaml
---
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
  namespace: default
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "taskflow-kafka-kafka-bootstrap.kafka.svc.cluster.local:9092"
    - name: consumerGroup
      value: "taskflow-consumer-group"
    - name: authType
      value: "none"

2. k8s/dapr-components/statestore.yaml
---
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
  namespace: default
spec:
  type: state.postgresql
  version: v1
  metadata:
    - name: connectionString
      secretKeyRef:
        name: db-secrets
        key: connection-string
    - name: tableName
      value: "dapr_state"

3. k8s/dapr-components/secrets.yaml
---
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kubernetes-secrets
  namespace: default
spec:
  type: secretstores.kubernetes
  version: v1
  metadata: []

Adjust the Kafka bootstrap server URL to match your Kafka service name.
```

**Acceptance Criteria:**
- 3 Dapr component files created
- Valid Dapr component format
- Kafka bootstrap server URL correct
- Can be applied without errors

---

#### Task 5.3.3: Deploy Dapr Components
**Task ID:** P5-T9  
**Priority:** Critical  
**Estimated Time:** 30 minutes  
**Dependencies:** P5-T7, P5-T8

**Description:**
Apply Dapr components to default namespace.

**Manual Steps:**
```bash
# Apply all Dapr components
kubectl apply -f k8s/dapr-components/ -n default

# Verify components are created
kubectl get components -n default

# Check component details
kubectl describe component kafka-pubsub -n default
kubectl describe component statestore -n default
kubectl describe component kubernetes-secrets -n default
```

**Acceptance Criteria:**
- All 3 components created in default namespace
- No errors in component status
- Components reference correct resources

**Verification:**
```bash
kubectl get components -n default
# Should show:
# NAME                  AGE
# kafka-pubsub          ...
# kubernetes-secrets    ...
# statestore           ...
```

---

### 5.4 Create Kubernetes Secrets

#### Task 5.4.1: Create Database Secrets
**Task ID:** P5-T10  
**Priority:** Critical  
**Estimated Time:** 15 minutes  
**Dependencies:** None

**Description:**
Create Kubernetes secret with Neon database connection string.

**Manual Steps:**
```bash
# Create database secret
kubectl create secret generic db-secrets \
  --from-literal=connection-string="postgresql://user:password@hostname/database?sslmode=require" \
  -n default

# Verify secret created
kubectl get secret db-secrets -n default

# Check secret (base64 encoded)
kubectl get secret db-secrets -n default -o yaml
```

**Important:** Replace with your actual Neon connection string!

**Acceptance Criteria:**
- Secret created in default namespace
- Contains connection-string key
- Connection string is valid

---

#### Task 5.4.2: Create API Secrets
**Task ID:** P5-T11  
**Priority:** Critical  
**Estimated Time:** 15 minutes  
**Dependencies:** None

**Description:**
Create Kubernetes secrets for API keys (OpenAI, etc.).

**Manual Steps:**
```bash
# Create API secrets
kubectl create secret generic api-secrets \
  --from-literal=openai-api-key="sk-..." \
  -n default

# If using other APIs, add them
kubectl create secret generic email-secrets \
  --from-literal=smtp-host="smtp.gmail.com" \
  --from-literal=smtp-port="587" \
  --from-literal=smtp-user="your-email@gmail.com" \
  --from-literal=smtp-password="your-app-password" \
  -n default

# Verify
kubectl get secrets -n default
```

**Acceptance Criteria:**
- api-secrets created with OpenAI key
- email-secrets created (if using email)
- All sensitive data stored as secrets

---

### 5.5 Build and Load Docker Images

#### Task 5.5.1: Create Dockerfiles for All Services
**Task ID:** P5-T12  
**Priority:** Critical  
**Estimated Time:** 2 hours  
**Dependencies:** None

**Description:**
Create optimized Dockerfiles for all services (if not already created).

**Claude Code Prompt:**
```
Create Dockerfiles for all services.

1. backend/Dockerfile
---
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

2. frontend/Dockerfile
---
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci

# Copy source code
COPY . .

# Build application
RUN npm run build

# Production image
FROM node:18-alpine

WORKDIR /app

COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/public ./public

EXPOSE 3000

CMD ["npm", "start"]

3. services/recurring-task-service/Dockerfile
---
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

CMD ["python", "main.py"]

4. services/notification-service/Dockerfile
(Similar to recurring-task-service)

5. services/audit-service/Dockerfile
(Similar to recurring-task-service)

Create all Dockerfiles with multi-stage builds where appropriate.
Include health checks.
Run as non-root user for security.
```

**Acceptance Criteria:**
- Dockerfile for each service
- Optimized with multi-stage builds (where applicable)
- Health checks included
- Non-root user configured
- Can build without errors

---

#### Task 5.5.2: Build Docker Images
**Task ID:** P5-T13  
**Priority:** Critical  
**Estimated Time:** 1 hour  
**Dependencies:** P5-T12

**Description:**
Build all Docker images for the application.

**Manual Steps:**
```bash
# Build backend
cd backend
docker build -t taskflow-backend:latest .

# Build frontend
cd ../frontend
docker build -t taskflow-frontend:latest .

# Build consumer services
cd ../services/recurring-task-service
docker build -t recurring-task-service:latest .

cd ../notification-service
docker build -t notification-service:latest .

cd ../audit-service
docker build -t audit-service:latest .

# Verify images
docker images | grep taskflow
```

**Acceptance Criteria:**
- All 5 images built successfully
- Images tagged with :latest
- No build errors
- Images present in docker images list

---

#### Task 5.5.3: Load Images into Minikube
**Task ID:** P5-T14  
**Priority:** Critical  
**Estimated Time:** 30 minutes  
**Dependencies:** P5-T13

**Description:**
Load Docker images into Minikube's Docker daemon.

**Manual Steps:**
```bash
# Load all images into Minikube
minikube image load taskflow-backend:latest
minikube image load taskflow-frontend:latest
minikube image load recurring-task-service:latest
minikube image load notification-service:latest
minikube image load audit-service:latest

# Verify images in Minikube
minikube ssh
docker images | grep taskflow
exit
```

**Alternative (use Minikube's Docker daemon directly):**
```bash
# Point Docker to Minikube's Docker
eval $(minikube docker-env)

# Now build images directly in Minikube
cd backend && docker build -t taskflow-backend:latest .
cd ../frontend && docker build -t taskflow-frontend:latest .
# etc...

# Verify
docker images | grep taskflow
```

**Acceptance Criteria:**
- All images loaded into Minikube
- Images accessible from within Minikube
- Can list images with `minikube ssh` + `docker images`

---

### 5.6 Create Kubernetes Deployment Manifests

#### Task 5.6.1: Create Backend Deployment
**Task ID:** P5-T15  
**Priority:** Critical  
**Estimated Time:** 1 hour  
**Dependencies:** P5-T14

**Description:**
Create Kubernetes Deployment and Service for backend with Dapr sidecar.

**Claude Code Prompt:**
```
Create backend deployment with Dapr sidecar.

Location: k8s/deployments/backend.yaml

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: default
  labels:
    app: backend
spec:
  replicas: 1  # Start with 1 for Minikube
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "backend-service"
        dapr.io/app-port: "8000"
        dapr.io/log-level: "info"
        dapr.io/enable-metrics: "true"
        dapr.io/metrics-port: "9090"
    spec:
      containers:
      - name: backend
        image: taskflow-backend:latest
        imagePullPolicy: Never  # Use local image in Minikube
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secrets
              key: connection-string
        - name: KAFKA_BOOTSTRAP_SERVERS
          value: "taskflow-kafka-kafka-bootstrap.kafka.svc.cluster.local:9092"
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: openai-api-key
        - name: DAPR_HTTP_PORT
          value: "3500"
        - name: DAPR_GRPC_PORT
          value: "50001"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: backend-service
  namespace: default
spec:
  selector:
    app: backend
  ports:
  - port: 8000
    targetPort: 8000
    name: http
  type: ClusterIP

Important Dapr annotations:
- dapr.io/enabled: "true" - Enables Dapr sidecar injection
- dapr.io/app-id: Unique app identifier for service invocation
- dapr.io/app-port: Port your app listens on

Use imagePullPolicy: Never for Minikube.
Change to IfNotPresent or Always for cloud deployment.
```

**Acceptance Criteria:**
- Deployment YAML created
- Dapr annotations present
- Service definition included
- Environment variables from secrets
- Resource limits defined
- Health checks configured

---

#### Task 5.6.2: Create Frontend Deployment
**Task ID:** P5-T16  
**Priority:** Critical  
**Estimated Time:** 45 minutes  
**Dependencies:** P5-T14

**Description:**
Create Kubernetes Deployment and Service for frontend.

**Claude Code Prompt:**
```
Create frontend deployment.

Location: k8s/deployments/frontend.yaml

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: default
spec:
  replicas: 1
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "frontend-service"
        dapr.io/app-port: "3000"
    spec:
      containers:
      - name: frontend
        image: taskflow-frontend:latest
        imagePullPolicy: Never
        ports:
        - containerPort: 3000
        env:
        - name: NEXT_PUBLIC_API_URL
          value: "http://backend-service:8000"
        - name: NEXT_PUBLIC_WS_URL
          value: "ws://websocket-service:8080"  # If using WebSocket
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
---
apiVersion: v1
kind: Service
metadata:
  name: frontend-service
  namespace: default
spec:
  selector:
    app: frontend
  ports:
  - port: 80
    targetPort: 3000
    name: http
  type: LoadBalancer  # For Minikube, exposes service externally
```

**Acceptance Criteria:**
- Frontend deployment created
- LoadBalancer service type for external access
- Environment variables configured
- Resource limits set

---

#### Task 5.6.3: Create Consumer Services Deployments
**Task ID:** P5-T17  
**Priority:** Critical  
**Estimated Time:** 1.5 hours  
**Dependencies:** P5-T14

**Description:**
Create Kubernetes Deployments for all consumer services (recurring-task, notification, audit).

**Claude Code Prompt:**
```
Create deployments for consumer services.

Location: k8s/deployments/consumers.yaml

---
# Recurring Task Service
apiVersion: apps/v1
kind: Deployment
metadata:
  name: recurring-task-service
  namespace: default
spec:
  replicas: 1
  selector:
    matchLabels:
      app: recurring-task-service
  template:
    metadata:
      labels:
        app: recurring-task-service
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "recurring-task-service"
        dapr.io/app-port: "8001"
    spec:
      containers:
      - name: recurring-task-service
        image: recurring-task-service:latest
        imagePullPolicy: Never
        env:
        - name: KAFKA_BOOTSTRAP_SERVERS
          value: "taskflow-kafka-kafka-bootstrap.kafka.svc.cluster.local:9092"
        - name: BACKEND_SERVICE_URL
          value: "http://backend-service:8000"
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"

---
# Notification Service
apiVersion: apps/v1
kind: Deployment
metadata:
  name: notification-service
  namespace: default
spec:
  replicas: 1
  selector:
    matchLabels:
      app: notification-service
  template:
    metadata:
      labels:
        app: notification-service
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "notification-service"
        dapr.io/app-port: "8002"
    spec:
      containers:
      - name: notification-service
        image: notification-service:latest
        imagePullPolicy: Never
        env:
        - name: KAFKA_BOOTSTRAP_SERVERS
          value: "taskflow-kafka-kafka-bootstrap.kafka.svc.cluster.local:9092"
        - name: EMAIL_SMTP_HOST
          valueFrom:
            secretKeyRef:
              name: email-secrets
              key: smtp-host
        - name: EMAIL_SMTP_PORT
          valueFrom:
            secretKeyRef:
              name: email-secrets
              key: smtp-port
        - name: EMAIL_SMTP_USER
          valueFrom:
            secretKeyRef:
              name: email-secrets
              key: smtp-user
        - name: EMAIL_SMTP_PASSWORD
          valueFrom:
            secretKeyRef:
              name: email-secrets
              key: smtp-password
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"

---
# Audit Service
apiVersion: apps/v1
kind: Deployment
metadata:
  name: audit-service
  namespace: default
spec:
  replicas: 1
  selector:
    matchLabels:
      app: audit-service
  template:
    metadata:
      labels:
        app: audit-service
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "audit-service"
        dapr.io/app-port: "8003"
    spec:
      containers:
      - name: audit-service
        image: audit-service:latest
        imagePullPolicy: Never
        env:
        - name: KAFKA_BOOTSTRAP_SERVERS
          value: "taskflow-kafka-kafka-bootstrap.kafka.svc.cluster.local:9092"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secrets
              key: connection-string
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"

All consumer services should have Dapr enabled.
Each should have unique app-id.
```

**Acceptance Criteria:**
- All 3 consumer services deployed
- Dapr sidecars enabled
- Proper environment variables
- Resource limits set

---

### 5.7 Deploy Application to Minikube

#### Task 5.7.1: Apply All Deployments
**Task ID:** P5-T18  
**Priority:** Critical  
**Estimated Time:** 30 minutes  
**Dependencies:** P5-T15, P5-T16, P5-T17

**Description:**
Deploy all application services to Minikube.

**Manual Steps:**
```bash
# Apply all deployments
kubectl apply -f k8s/deployments/ -n default

# Watch pods starting
kubectl get pods -n default -w

# Wait for all pods to be ready
kubectl wait --for=condition=ready pod \
  --all \
  -n default \
  --timeout=300s

# Check pod status
kubectl get pods -n default

# Check if Dapr sidecars are injected
kubectl get pods -n default -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[*].name}{"\n"}{end}'
```

**Expected Pods:**
- backend-xxx (2 containers: backend + daprd)
- frontend-xxx (2 containers: frontend + daprd)
- recurring-task-service-xxx (2 containers)
- notification-service-xxx (2 containers)
- audit-service-xxx (2 containers)

**Acceptance Criteria:**
- All pods running
- Each pod has 2 containers (app + daprd sidecar)
- No CrashLoopBackOff
- No ImagePullBackOff

---

#### Task 5.7.2: Verify Services and Connectivity
**Task ID:** P5-T19  
**Priority:** Critical  
**Estimated Time:** 30 minutes  
**Dependencies:** P5-T18

**Description:**
Verify all services are accessible and can communicate.

**Manual Steps:**
```bash
# Check all services
kubectl get svc -n default

# Check backend service
kubectl port-forward svc/backend-service 8000:8000 -n default
# Open browser: http://localhost:8000/health
# Should return: {"status": "healthy"}

# Check frontend service
minikube service frontend-service --url
# Open returned URL in browser
# Should load frontend application

# Check pod logs
kubectl logs -f deployment/backend -c backend -n default
kubectl logs -f deployment/backend -c daprd -n default

# Check if Kafka connectivity works
kubectl exec -it deployment/backend -c backend -n default -- \
  curl http://localhost:3500/v1.0/healthz
```

**Acceptance Criteria:**
- Backend health endpoint responds
- Frontend loads in browser
- Dapr sidecars healthy
- No error logs
- Services can reach Kafka

---

### 5.8 End-to-End Testing on Minikube

#### Task 5.8.1: Test Task Creation Flow
**Task ID:** P5-T20  
**Priority:** Critical  
**Estimated Time:** 1 hour  
**Dependencies:** P5-T19

**Description:**
Test complete task creation flow through chatbot with Kafka events.

**Manual Test Steps:**
1. Access frontend via Minikube URL
2. Log in with Better Auth
3. Open chatbot
4. Create task: "Team meeting tomorrow at 2pm"
5. Verify task appears in UI
6. Check Kafka for event:
```bash
kubectl exec -it taskflow-kafka-kafka-0 -n kafka -- \
  bin/kafka-console-consumer.sh \
  --topic task-events \
  --from-beginning \
  --bootstrap-server localhost:9092 \
  --max-messages 1
```
7. Check backend logs for event publishing
8. Verify task in database

**Acceptance Criteria:**
- Task created successfully via chatbot
- Task appears in UI
- Event published to Kafka (visible in console consumer)
- Backend logs show successful event publishing
- Task stored in Neon database

**Expected Event:**
```json
{
  "event_id": "...",
  "event_type": "created",
  "task_id": 123,
  "task_data": { "id": 123, "title": "Team meeting...", ... },
  "user_id": "...",
  "timestamp": "2024-..."
}
```

---

#### Task 5.8.2: Test Recurring Task Flow
**Task ID:** P5-T21  
**Priority:** High  
**Estimated Time:** 1 hour  
**Dependencies:** P5-T20

**Description:**
Test recurring task creation and auto-generation of next occurrence.

**Manual Test Steps:**
1. Create recurring task via chatbot: "Daily standup at 9am"
2. Verify task created with is_recurring=true
3. Complete the task
4. Check recurring-task-service logs:
```bash
kubectl logs -f deployment/recurring-task-service -c recurring-task-service -n default
```
5. Wait for next occurrence to be created (should happen within seconds)
6. Verify new task appears in UI
7. Check it has correct due date (next day, same time)
8. Verify parent_task_id is set

**Acceptance Criteria:**
- Recurring task created with correct pattern
- Completion event triggers consumer service
- New occurrence created automatically
- New task has correct due date
- parent_task_id links to original task
- Service logs show processing

---

#### Task 5.8.3: Test Reminder Flow
**Task ID:** P5-T22  
**Priority:** High  
**Estimated Time:** 1 hour  
**Dependencies:** P5-T20

**Description:**
Test email reminder functionality.

**Manual Test Steps:**
1. Create task with due date (set to 5 minutes from now for testing)
2. Verify reminder event published to Kafka:
```bash
kubectl exec -it taskflow-kafka-kafka-0 -n kafka -- \
  bin/kafka-console-consumer.sh \
  --topic reminders \
  --from-beginning \
  --bootstrap-server localhost:9092
```
3. Check notification-service logs:
```bash
kubectl logs -f deployment/notification-service -c notification-service -n default
```
4. Wait for reminder time
5. Check email inbox
6. Verify reminder email received

**Acceptance Criteria:**
- Reminder event published to reminders topic
- Notification service consumes event
- Email sent successfully
- Email content correct (task title, due date)
- Logs show successful email delivery

**Note:** For testing, you might want to modify the reminder time to be 1 minute before due date instead of 1 hour.

---

#### Task 5.8.4: Test Advanced Features
**Task ID:** P5-T23  
**Priority:** Medium  
**Estimated Time:** 1 hour  
**Dependencies:** P5-T20

**Description:**
Test priorities, tags, and search functionality.

**Manual Test Steps:**
1. **Test Priorities:**
   - Create task with high priority
   - Verify priority badge shows in UI
   - Filter tasks by priority
   - Verify only high priority tasks shown

2. **Test Tags:**
   - Add tags "work" and "urgent" to task
   - Verify tags appear in UI
   - Search for tasks with "work" tag
   - Verify correct tasks returned

3. **Test Search:**
   - Create tasks with different titles
   - Search for specific keyword
   - Verify search results accurate
   - Test combined filters (status + priority + tags)

4. **Test Audit Logs:**
   - Check audit_logs table in database
   - Verify all operations logged
   - Query logs by event_type

**Acceptance Criteria:**
- All advanced features working
- Priority filtering works
- Tags system functional
- Search returns accurate results
- Audit logs captured all events

---

#### Task 5.8.5: Document Minikube Setup
**Task ID:** P5-T24  
**Priority:** Medium  
**Estimated Time:** 1 hour  
**Dependencies:** P5-T23

**Description:**
Document complete Minikube setup process for team and submission.

**Claude Code Prompt:**
```
Create comprehensive Minikube deployment documentation.

Location: docs/MINIKUBE_DEPLOYMENT.md

Include:

# Minikube Deployment Guide

## Prerequisites
- Minikube installed
- kubectl installed
- Docker installed
- 8GB RAM minimum
- 20GB disk space

## Quick Start
Step-by-step commands to deploy:
1. Start Minikube
2. Install Kafka
3. Install Dapr
4. Create secrets
5. Build and load images
6. Deploy application
7. Access frontend

## Architecture
(Include diagram of components)

## Troubleshooting
Common issues and solutions:
- Pods stuck in Pending
- ImagePullBackOff
- CrashLoopBackOff
- Kafka connection errors
- Dapr sidecar not injecting

## Testing
How to test each feature

## Cleanup
How to tear down everything

Include all commands used, expected outputs, and verification steps.
```

**Acceptance Criteria:**
- Complete documentation created
- All commands documented
- Troubleshooting section included
- Screenshots (optional but helpful)
- Tested by following the doc from scratch

---

## PHASE 6: Cloud Deployment (Days 3-5)

### 6.1 Cloud Provider Setup

#### Task 6.1.1: Choose Cloud Provider
**Task ID:** P6-T1  
**Priority:** Critical  
**Estimated Time:** 30 minutes  
**Dependencies:** None

**Description:**
Select cloud provider based on credits, requirements, and long-term viability.

**Decision Matrix:**

| Provider | Free Credits | Duration | Best For | Recommendation |
|----------|-------------|----------|----------|----------------|
| Oracle Cloud (OKE) | Always Free | Forever | Learning, no time pressure | ⭐⭐⭐⭐⭐ |
| Google Cloud (GKE) | $300 | 90 days | Generous credits, longer eval | ⭐⭐⭐⭐ |
| Azure (AKS) | $200 | 30 days | Quick hackathon demo | ⭐⭐⭐ |

**Recommended:** Oracle Cloud Infrastructure (OKE) - Always Free tier with 2 nodes.

**Manual Steps:**
1. Review each provider's free tier
2. Consider project timeline
3. Make decision
4. Document choice in README.md
5. Sign up for chosen provider

**Acceptance Criteria:**
- Cloud provider selected
- Account created
- Credits verified
- Billing alerts set (if applicable)

---

#### Task 6.1.2: Sign Up and Configure Cloud Account (Oracle Cloud)
**Task ID:** P6-T2A  
**Priority:** Critical  
**Estimated Time:** 1 hour  
**Dependencies:** P6-T1 (if Oracle chosen)

**Description:**
Create Oracle Cloud account and configure for OKE deployment.

**Manual Steps:**
1. Go to https://www.oracle.com/cloud/free/
2. Click "Start for free"
3. Fill in account information
4. Verify email
5. Complete identity verification (may require credit card, but won't be charged)
6. Access OCI Console
7. Note your tenancy OCID and region

**Acceptance Criteria:**
- OCI account active
- Can access OCI Console
- Always Free tier enabled
- Tenancy information documented

---

#### Task 6.1.2: Sign Up and Configure Cloud Account (GKE)
**Task ID:** P6-T2B  
**Priority:** Critical  
**Estimated Time:** 1 hour  
**Dependencies:** P6-T1 (if GCP chosen)

**Description:**
Create Google Cloud account and enable GKE.

**Manual Steps:**
1. Go to https://cloud.google.com/free
2. Click "Get started for free"
3. Sign in with Google account
4. Add billing information ($300 credits, not charged)
5. Create new project: "taskflow-production"
6. Enable Kubernetes Engine API
7. Install gcloud CLI

**Acceptance Criteria:**
- GCP account with $300 credits
- Project created
- GKE API enabled
- gcloud CLI installed and configured

---

#### Task 6.1.2: Sign Up and Configure Cloud Account (Azure)
**Task ID:** P6-T2C  
**Priority:** Critical  
**Estimated Time:** 1 hour  
**Dependencies:** P6-T1 (if Azure chosen)

**Description:**
Create Azure account and configure for AKS.

**Manual Steps:**
1. Go to https://azure.microsoft.com/en-us/free/
2. Sign up (requires credit card, $200 credits)
3. Verify account
4. Create resource group: "taskflow-rg"
5. Install Azure CLI
6. Login: `az login`

**Acceptance Criteria:**
- Azure account with $200 credits
- Resource group created
- Azure CLI installed

---

### 6.2 Kubernetes Cluster Creation

#### Task 6.2.1: Create OKE Cluster (Oracle Cloud)
**Task ID:** P6-T3A  
**Priority:** Critical  
**Estimated Time:** 2 hours  
**Dependencies:** P6-T2A

**Description:**
Create Oracle Kubernetes Engine cluster using Always Free tier.

**Manual Steps via OCI Console:**
1. Navigate to: Developer Services → Kubernetes Clusters (OKE)
2. Click "Create Cluster"
3. Choose "Quick Create"
4. Configuration:
   - Name: taskflow-oke-cluster
   - Kubernetes Version: Latest
   - Node Pool: 
     - Shape: VM.Standard.E2.1.Micro (Always Free)
     - Number of nodes: 2
     - Boot Volume: 50GB
   - Visibility Type: Public
   - Kubernetes API Endpoint: Public
5. Click "Create Cluster"
6. Wait 10-15 minutes for cluster creation

**Configure kubectl:**
```bash
# Install OCI CLI
bash -c "$(curl -L https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh)"

# Generate kubeconfig
oci ce cluster create-kubeconfig \
  --cluster-id <cluster-ocid> \
  --file $HOME/.kube/config \
  --region us-ashburn-1 \
  --token-version 2.0.0

# Verify
kubectl get nodes
```

**Acceptance Criteria:**
- Cluster created successfully
- 2 nodes running
- kubectl can connect
- Nodes show Ready status

---

#### Task 6.2.1: Create GKE Cluster (Google Cloud)
**Task ID:** P6-T3B  
**Priority:** Critical  
**Estimated Time:** 1.5 hours  
**Dependencies:** P6-T2B

**Description:**
Create Google Kubernetes Engine cluster.

**Manual Steps:**
```bash
# Set project
gcloud config set project taskflow-production

# Create cluster
gcloud container clusters create taskflow-gke \
  --zone us-central1-a \
  --num-nodes 3 \
  --machine-type e2-medium \
  --disk-size 20GB \
  --enable-autoscaling \
  --min-nodes 1 \
  --max-nodes 5 \
  --enable-autorepair \
  --enable-autoupgrade

# Get credentials
gcloud container clusters get-credentials taskflow-gke \
  --zone us-central1-a

# Verify
kubectl get nodes
```

**Acceptance Criteria:**
- GKE cluster running
- 3 nodes (or as configured)
- kubectl connected
- Autoscaling enabled

---

#### Task 6.2.1: Create AKS Cluster (Azure)
**Task ID:** P6-T3C  
**Priority:** Critical  
**Estimated Time:** 1.5 hours  
**Dependencies:** P6-T2C

**Description:**
Create Azure Kubernetes Service cluster.

**Manual Steps:**
```bash
# Create AKS cluster
az aks create \
  --resource-group taskflow-rg \
  --name taskflow-aks \
  --node-count 3 \
  --node-vm-size Standard_B2s \
  --enable-addons monitoring \
  --generate-ssh-keys

# Get credentials
az aks get-credentials \
  --resource-group taskflow-rg \
  --name taskflow-aks

# Verify
kubectl get nodes
```

**Acceptance Criteria:**
- AKS cluster created
- 3 nodes running
- Monitoring enabled
- kubectl connected

---

### 6.3 Install Dapr on Cloud Cluster

#### Task 6.3.1: Initialize Dapr on Cloud Kubernetes
**Task ID:** P6-T4  
**Priority:** Critical  
**Estimated Time:** 30 minutes  
**Dependencies:** P6-T3A or P6-T3B or P6-T3C

**Description:**
Install Dapr runtime on cloud Kubernetes cluster.

**Manual Steps:**
```bash
# Initialize Dapr on cloud cluster
dapr init -k

# Wait for Dapr to be ready
kubectl wait --for=condition=ready pod \
  --all \
  -n dapr-system \
  --timeout=300s

# Verify Dapr installation
dapr status -k

# Check Dapr version
dapr version
```

**Acceptance Criteria:**
- Dapr control plane deployed
- All Dapr pods running in dapr-system namespace
- No errors in Dapr logs
- dapr status shows healthy

---

### 6.4 Setup Kafka in Cloud

#### Task 6.4.1: Choose Kafka Deployment Strategy for Cloud
**Task ID:** P6-T5  
**Priority:** Critical  
**Estimated Time:** 30 minutes  
**Dependencies:** None

**Description:**
Decide between Redpanda Cloud (managed) or Strimzi (self-hosted) for production.

**Decision Factors:**
- **Redpanda Cloud:** Easy, managed, free tier available, less ops overhead
- **Strimzi on Cloud:** Full control, learning experience, uses cloud compute

**Recommendation:** Redpanda Cloud for production simplicity.

**Manual Decision:**
1. Review Redpanda Cloud pricing
2. Review Strimzi resource requirements
3. Make choice
4. Document in README

---

#### Task 6.4.2: Setup Redpanda Cloud (Option A - Recommended)
**Task ID:** P6-T6A  
**Priority:** Critical  
**Estimated Time:** 1 hour  
**Dependencies:** P6-T5

**Description:**
Create Redpanda Cloud serverless cluster for production.

**Manual Steps:**
1. Sign up at https://redpanda.com/cloud
2. Create serverless cluster:
   - Name: taskflow-production
   - Cloud: Same as K8s cluster (AWS/GCP/Azure)
   - Region: Same as K8s cluster
3. Create topics (same as Minikube):
   - task-events (3 partitions)
   - reminders (2 partitions)
   - task-updates (2 partitions)
   - audit-logs (1 partition)
4. Create SASL user:
   - Username: taskflow-app
   - Password: (generate secure password)
5. Note bootstrap server URL
6. Download client.properties or save credentials

**Acceptance Criteria:**
- Redpanda cluster running
- All topics created
- SASL credentials generated
- Bootstrap URL documented
- Can connect from local machine (test with kafka-console-producer)

**Save Credentials Securely:**
```bash
# Example bootstrap server
bootstrap-xxxxxx.cloud.redpanda.com:9092

# Save to secure location (NOT in git!)
echo "KAFKA_BOOTSTRAP_SERVERS=bootstrap-xxx.cloud.redpanda.com:9092" >> .env.production
echo "KAFKA_SASL_USERNAME=taskflow-app" >> .env.production
echo "KAFKA_SASL_PASSWORD=<password>" >> .env.production
```

---

#### Task 6.4.2: Deploy Strimzi Kafka on Cloud (Option B)
**Task ID:** P6-T6B  
**Priority:** Critical  
**Estimated Time:** 2-3 hours  
**Dependencies:** P6-T5

**Description:**
Deploy self-hosted Kafka using Strimzi on cloud Kubernetes.

**Manual Steps:**
```bash
# Create namespace
kubectl create namespace kafka

# Install Strimzi operator
kubectl create -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka

# Wait for operator
kubectl wait deployment/strimzi-cluster-operator \
  --for=condition=Available \
  --timeout=300s \
  -n kafka
```

**Create Production Kafka Cluster:**

**Claude Code Prompt:**
```
Create production Kafka cluster configuration for cloud.

Location: k8s/kafka/kafka-cluster-production.yaml

apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: taskflow-kafka
  namespace: kafka
spec:
  kafka:
    version: 3.6.0
    replicas: 3  # 3 replicas for production
    listeners:
      - name: plain
        port: 9092
        type: internal
        tls: false
      - name: tls
        port: 9093
        type: internal
        tls: true
    config:
      offsets.topic.replication.factor: 3
      transaction.state.log.replication.factor: 3
      transaction.state.log.min.isr: 2
      default.replication.factor: 3
      min.insync.replicas: 2
      inter.broker.protocol.version: "3.6"
    storage:
      type: persistent-claim
      size: 20Gi  # Persistent storage for production
      deleteClaim: false
  zookeeper:
    replicas: 3
    storage:
      type: persistent-claim
      size: 10Gi
      deleteClaim: false
  entityOperator:
    topicOperator: {}
    userOperator: {}

This uses persistent storage and 3 replicas for high availability.
```

**Apply and Verify:**
```bash
# Apply cluster
kubectl apply -f k8s/kafka/kafka-cluster-production.yaml -n kafka

# This takes 5-10 minutes
kubectl wait kafka/taskflow-kafka --for=condition=Ready --timeout=900s -n kafka

# Create topics (reuse topics.yaml from Minikube, update replicas to 3)
kubectl apply -f k8s/kafka/topics-production.yaml -n kafka
```

**Acceptance Criteria:**
- Kafka cluster with 3 brokers running
- All topics created with replication factor 3
- Persistent volumes attached
- Can produce/consume messages

---

### 6.5 Update Dapr Components for Cloud

#### Task 6.5.1: Update Dapr Pub/Sub Component for Cloud Kafka
**Task ID:** P6-T7  
**Priority:** Critical  
**Estimated Time:** 45 minutes  
**Dependencies:** P6-T6A or P6-T6B

**Description:**
Update Dapr Pub/Sub component to use cloud Kafka (Redpanda or Strimzi).

**For Redpanda Cloud:**

**Claude Code Prompt:**
```
Update Dapr Pub/Sub component for Redpanda Cloud.

Location: k8s/dapr-components/pubsub-production.yaml

apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
  namespace: default
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "bootstrap-xxxxx.cloud.redpanda.com:9092"
    - name: consumerGroup
      value: "taskflow-consumer-group"
    - name: authType
      value: "sasl"
    - name: saslMechanism
      value: "SCRAM-SHA-256"
    - name: saslUsername
      secretKeyRef:
        name: kafka-secrets
        key: username
    - name: saslPassword
      secretKeyRef:
        name: kafka-secrets
        key: password

Replace bootstrap server with your actual Redpanda URL.
Uses SASL authentication with secrets.
```

**For Strimzi (self-hosted):**
```yaml
# Same as Minikube, just update broker URL
metadata:
  - name: brokers
    value: "taskflow-kafka-kafka-bootstrap.kafka.svc.cluster.local:9092"
```

**Acceptance Criteria:**
- Component references correct Kafka bootstrap servers
- Authentication configured (if using Redpanda)
- Can be applied without errors

---

#### Task 6.5.2: Apply Updated Dapr Components to Cloud
**Task ID:** P6-T8  
**Priority:** Critical  
**Estimated Time:** 30 minutes  
**Dependencies:** P6-T7

**Description:**
Deploy Dapr components to cloud Kubernetes cluster.

**Manual Steps:**
```bash
# Apply all Dapr components
kubectl apply -f k8s/dapr-components/pubsub-production.yaml -n default
kubectl apply -f k8s/dapr-components/statestore.yaml -n default
kubectl apply -f k8s/dapr-components/secrets.yaml -n default

# Verify components
kubectl get components -n default

# Check component status
kubectl describe component kafka-pubsub -n default
```

**Acceptance Criteria:**
- All Dapr components created
- No errors in component status
- Components reference correct cloud resources

---

### 6.6 Container Registry Setup

#### Task 6.6.1: Choose and Setup Container Registry
**Task ID:** P6-T9  
**Priority:** Critical  
**Estimated Time:** 1 hour  
**Dependencies:** P6-T1

**Description:**
Set up container registry for storing Docker images.

**Options:**
1. **GitHub Container Registry (ghcr.io)** - Free, integrated with GitHub ⭐ Recommended
2. **Docker Hub** - Free for public repos
3. **Cloud Provider Registry** (GCR, ACR, OCIR) - Integrated with cloud

**For GitHub Container Registry:**

**Manual Steps:**
```bash
# Create GitHub Personal Access Token
# Go to: Settings → Developer Settings → Personal Access Tokens → Tokens (classic)
# Generate new token with `write:packages` and `read:packages` scopes

# Login to GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin

# Verify login
docker info | grep Username
```

**Acceptance Criteria:**
- Container registry selected
- Authentication configured
- Can push images
- Registry URL documented

---

#### Task 6.6.2: Tag and Push Docker Images
**Task ID:** P6-T10  
**Priority:** Critical  
**Estimated Time:** 1 hour  
**Dependencies:** P6-T9, P5-T13 (images built)

**Description:**
Tag images with registry prefix and push to container registry.

**Manual Steps:**
```bash
# Set variables
REGISTRY="ghcr.io"
USERNAME="your-github-username"
VERSION="v1.0.0"

# Tag all images
docker tag taskflow-backend:latest $REGISTRY/$USERNAME/taskflow-backend:$VERSION
docker tag taskflow-backend:latest $REGISTRY/$USERNAME/taskflow-backend:latest

docker tag taskflow-frontend:latest $REGISTRY/$USERNAME/taskflow-frontend:$VERSION
docker tag taskflow-frontend:latest $REGISTRY/$USERNAME/taskflow-frontend:latest

docker tag recurring-task-service:latest $REGISTRY/$USERNAME/recurring-task-service:$VERSION
docker tag recurring-task-service:latest $REGISTRY/$USERNAME/recurring-task-service:latest

docker tag notification-service:latest $REGISTRY/$USERNAME/notification-service:$VERSION
docker tag notification-service:latest $REGISTRY/$USERNAME/notification-service:latest

docker tag audit-service:latest $REGISTRY/$USERNAME/audit-service:$VERSION
docker tag audit-service:latest $REGISTRY/$USERNAME/audit-service:latest

# Push all images
docker push $REGISTRY/$USERNAME/taskflow-backend:$VERSION
docker push $REGISTRY/$USERNAME/taskflow-backend:latest

docker push $REGISTRY/$USERNAME/taskflow-frontend:$VERSION
docker push $REGISTRY/$USERNAME/taskflow-frontend:latest

docker push $REGISTRY/$USERNAME/recurring-task-service:$VERSION
docker push $REGISTRY/$USERNAME/recurring-task-service:latest

docker push $REGISTRY/$USERNAME/notification-service:$VERSION
docker push $REGISTRY/$USERNAME/notification-service:latest

docker push $REGISTRY/$USERNAME/audit-service:$VERSION
docker push $REGISTRY/$USERNAME/audit-service:latest

# Verify images in registry
# Go to: github.com/USERNAME?tab=packages
```

**Acceptance Criteria:**
- All 5 images pushed to registry
- Both :latest and :v1.0.0 tags pushed
- Images visible in registry UI
- Images are public (or have proper access configured)

---

### 6.7 Create Cloud Secrets

#### Task 6.7.1: Create Kubernetes Secrets for Cloud
**Task ID:** P6-T11  
**Priority:** Critical  
**Estimated Time:** 30 minutes  
**Dependencies:** P6-T3A/B/C

**Description:**
Create all required Kubernetes secrets in cloud cluster.

**Manual Steps:**
```bash
# Create database secret
kubectl create secret generic db-secrets \
  --from-literal=connection-string="$DATABASE_URL" \
  -n default

# Create API secrets
kubectl create secret generic api-secrets \
  --from-literal=openai-api-key="$OPENAI_API_KEY" \
  -n default

# Create email secrets
kubectl create secret generic email-secrets \
  --from-literal=smtp-host="$SMTP_HOST" \
  --from-literal=smtp-port="$SMTP_PORT" \
  --from-literal=smtp-user="$SMTP_USER" \
  --from-literal=smtp-password="$SMTP_PASSWORD" \
  -n default

# Create Kafka secrets (if using Redpanda with SASL)
kubectl create secret generic kafka-secrets \
  --from-literal=username="$KAFKA_USERNAME" \
  --from-literal=password="$KAFKA_PASSWORD" \
  -n default

# Verify all secrets created
kubectl get secrets -n default
```

**Important:** Never commit secrets to git!

**Acceptance Criteria:**
- All required secrets created
- Secrets contain correct values
- No secrets in git repository
- Secrets documented in .env.example (without values)

---

### 6.8 Update Deployment Manifests for Cloud

#### Task 6.8.1: Create Production Deployment Manifests
**Task ID:** P6-T12  
**Priority:** Critical  
**Estimated Time:** 1.5 hours  
**Dependencies:** P6-T10

**Description:**
Update Kubernetes manifests for cloud deployment with correct image references and settings.

**Claude Code Prompt:**
```
Create production deployment manifests.

Location: k8s/production/

Copy all deployment manifests from k8s/deployments/ to k8s/production/
and update them for cloud:

Changes needed:
1. Update image references:
   - FROM: taskflow-backend:latest
   - TO: ghcr.io/USERNAME/taskflow-backend:v1.0.0

2. Update imagePullPolicy:
   - FROM: Never (Minikube)
   - TO: IfNotPresent (Cloud)

3. Update replicas:
   - Backend: 2 replicas
   - Frontend: 2 replicas
   - Consumer services: 1 replica each

4. Update resource limits (increase for cloud):
   - Backend: 512Mi memory, 500m CPU
   - Frontend: 256Mi memory, 250m CPU

5. Update Kafka bootstrap servers:
   - If using Redpanda: Update to cloud URL
   - If using Strimzi: Keep same (service name)

6. Add imagePullSecrets if using private registry:
   spec:
     imagePullSecrets:
     - name: ghcr-secret

Example for backend:

apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: default
spec:
  replicas: 2  # Changed from 1
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "backend-service"
        dapr.io/app-port: "8000"
    spec:
      containers:
      - name: backend
        image: ghcr.io/USERNAME/taskflow-backend:v1.0.0  # Updated
        imagePullPolicy: IfNotPresent  # Updated
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secrets
              key: connection-string
        - name: KAFKA_BOOTSTRAP_SERVERS
          value: "bootstrap-xxx.cloud.redpanda.com:9092"  # Updated for Redpanda
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: openai-api-key
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"  # Increased
            cpu: "500m"  # Increased
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5

Repeat for all services (frontend, consumers).
```

**Acceptance Criteria:**
- Production manifests created in k8s/production/
- Image references updated to registry
- imagePullPolicy set to IfNotPresent
- Replicas increased for HA
- Resource limits appropriate for cloud
- Kafka URLs updated

---

### 6.9 Deploy to Cloud

#### Task 6.9.1: Deploy Application to Cloud Kubernetes
**Task ID:** P6-T13  
**Priority:** Critical  
**Estimated Time:** 1 hour  
**Dependencies:** P6-T12

**Description:**
Deploy complete application stack to cloud Kubernetes cluster.

**Manual Steps:**
```bash
# Verify kubectl is pointing to cloud cluster
kubectl cluster-info
kubectl config current-context

# Apply all production deployments
kubectl apply -f k8s/production/ -n default

# Watch deployment progress
kubectl get pods -n default -w

# Wait for all pods to be ready
kubectl wait --for=condition=ready pod \
  --all \
  -n default \
  --timeout=600s

# Check deployment status
kubectl get deployments -n default
kubectl get pods -n default
kubectl get svc -n default

# Check logs for any errors
kubectl logs -f deployment/backend -c backend -n default
```

**Expected Pods:**
- backend-xxx-xxx (2 pods)
- frontend-xxx-xxx (2 pods)
- recurring-task-service-xxx-xxx (1 pod)
- notification-service-xxx-xxx (1 pod)
- audit-service-xxx-xxx (1 pod)

**Acceptance Criteria:**
- All pods running
- All pods have 2/2 containers ready (app + daprd)
- No CrashLoopBackOff or Error status
- Services created
- No errors in logs

---

#### Task 6.9.2: Troubleshoot Deployment Issues
**Task ID:** P6-T14  
**Priority:** High  
**Estimated Time:** 2-4 hours (buffer)  
**Dependencies:** P6-T13

**Description:**
Debug and fix any deployment issues that arise.

**Common Issues and Solutions:**

**1. ImagePullBackOff:**
```bash
# Check if images are accessible
kubectl describe pod <pod-name> -n default

# Solution: Verify image exists in registry
# If private registry, create imagePullSecret:
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=$GITHUB_USERNAME \
  --docker-password=$GITHUB_TOKEN \
  -n default

# Add to deployment:
spec:
  imagePullSecrets:
  - name: ghcr-secret
```

**2. CrashLoopBackOff:**
```bash
# Check logs
kubectl logs <pod-name> -c <container-name> -n default --previous

# Common causes:
# - Database connection failed (check connection string)
# - Kafka connection failed (check bootstrap servers)
# - Missing environment variables
# - Application errors
```

**3. Pods Pending:**
```bash
# Check node resources
kubectl describe pod <pod-name> -n default

# Check if nodes have enough resources
kubectl top nodes

# Solution: Scale cluster or reduce resource requests
```

**4. Dapr Sidecar Not Injecting:**
```bash
# Check Dapr annotations
kubectl get pod <pod-name> -n default -o yaml | grep dapr

# Verify Dapr is running
dapr status -k

# Solution: Add proper annotations
```

**5. Kafka Connection Errors:**
```bash
# Test Kafka connectivity from pod
kubectl exec -it <pod-name> -c <container-name> -n default -- bash
# Try to connect to Kafka from inside pod

# Check Dapr component
kubectl describe component kafka-pubsub -n default

# Verify Kafka secrets (if using SASL)
kubectl get secret kafka-secrets -n default -o yaml
```

**Debugging Commands:**
```bash
# Get pod details
kubectl describe pod <pod-name> -n default

# Check events
kubectl get events -n default --sort-by='.lastTimestamp'

# Check logs
kubectl logs -f <pod-name> -c <container-name> -n default

# Exec into pod
kubectl exec -it <pod-name> -c <container-name> -n default -- /bin/bash

# Check Dapr sidecar logs
kubectl logs <pod-name> -c daprd -n default
```

**Acceptance Criteria:**
- All deployment issues resolved
- All pods running stably
- Application functional
- No recurring errors in logs

---

### 6.10 Setup Ingress and DNS

#### Task 6.10.1: Install Ingress Controller
**Task ID:** P6-T15  
**Priority:** High  
**Estimated Time:** 45 minutes  
**Dependencies:** P6-T13

**Description:**
Install NGINX Ingress Controller to expose application externally.

**Manual Steps:**
```bash
# Install NGINX Ingress Controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml

# Wait for controller to be ready
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=300s

# Check ingress controller
kubectl get pods -n ingress-nginx
kubectl get svc -n ingress-nginx

# Get external IP (may take a few minutes)
kubectl get svc ingress-nginx-controller -n ingress-nginx -w
```

**For Oracle Cloud (OCI LoadBalancer):**
- External IP will be provisioned automatically
- Note down the EXTERNAL-IP

**Acceptance Criteria:**
- Ingress controller running
- External IP assigned to LoadBalancer service
- Controller healthy (check logs)

---

#### Task 6.10.2: Create Ingress Resource
**Task ID:** P6-T16  
**Priority:** High  
**Estimated Time:** 45 minutes  
**Dependencies:** P6-T15

**Description:**
Create Ingress resource to route traffic to frontend and backend.

**Claude Code Prompt:**
```
Create Ingress resource for application.

Location: k8s/production/ingress.yaml

apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: taskflow-ingress
  namespace: default
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "false"  # Set to "true" when SSL is configured
spec:
  ingressClassName: nginx
  rules:
  - http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: backend-service
            port:
              number: 8000
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 80

This routes:
- /api/* → backend-service:8000
- /* → frontend-service:80
```

**Apply Ingress:**
```bash
# Apply ingress
kubectl apply -f k8s/production/ingress.yaml -n default

# Check ingress status
kubectl get ingress -n default

# Get ingress IP
kubectl get ingress taskflow-ingress -n default -o jsonpath='{.status.loadBalancer.ingress[0].ip}'

# Test access
curl http://<EXTERNAL-IP>
```

**Acceptance Criteria:**
- Ingress resource created
- IP address assigned
- Can access frontend via IP
- Can access backend via IP/api

---

#### Task 6.10.3: Configure Domain and DNS (Optional)
**Task ID:** P6-T17  
**Priority:** Low  
**Estimated Time:** 30 minutes  
**Dependencies:** P6-T16

**Description:**
Point domain name to application (if you have one).

**Manual Steps:**
1. Get ingress external IP:
```bash
kubectl get ingress taskflow-ingress -n default
```

2. Add DNS A record:
   - Go to your domain registrar (Namecheap, GoDaddy, etc.)
   - Add A record:
     - Name: taskflow (or @for root domain)
     - Type: A
     - Value: <EXTERNAL-IP>
     - TTL: 300 (5 minutes)

3. Wait for DNS propagation (5-30 minutes)

4. Test:
```bash
dig taskflow.yourdomain.com
curl http://taskflow.yourdomain.com
```

5. Update Ingress with host:
```yaml
spec:
  rules:
  - host: taskflow.yourdomain.com
    http:
      paths:
      # ... paths
```

**Acceptance Criteria:**
- Domain points to application
- DNS resolves correctly
- Application accessible via domain

---

#### Task 6.10.4: Setup TLS/HTTPS (Optional - Recommended)
**Task ID:** P6-T18  
**Priority:** Low  
**Estimated Time:** 1 hour  
**Dependencies:** P6-T17

**Description:**
Configure HTTPS with Let's Encrypt certificate.

**Manual Steps:**
```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Wait for cert-manager
kubectl wait --for=condition=ready pod \
  --all \
  -n cert-manager \
  --timeout=300s
```

**Create ClusterIssuer:**
```yaml
# k8s/production/cert-issuer.yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
```

**Update Ingress:**
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: taskflow-ingress
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  tls:
  - hosts:
    - taskflow.yourdomain.com
    secretName: taskflow-tls
  rules:
  - host: taskflow.yourdomain.com
    # ...
```

**Apply:**
```bash
kubectl apply -f k8s/production/cert-issuer.yaml
kubectl apply -f k8s/production/ingress.yaml -n default

# Check certificate
kubectl get certificate -n default
kubectl describe certificate taskflow-tls -n default
```

**Acceptance Criteria:**
- Certificate issued by Let's Encrypt
- HTTPS working
- HTTP redirects to HTTPS
- Browser shows secure connection

---

### 6.11 End-to-End Testing on Cloud

#### Task 6.11.1: Comprehensive Cloud Testing
**Task ID:** P6-T19  
**Priority:** Critical  
**Estimated Time:** 2 hours  
**Dependencies:** P6-T16

**Description:**
Test all application features end-to-end on cloud deployment.

**Test Checklist:**

**1. Basic Connectivity:**
- [ ] Can access frontend via external IP/domain
- [ ] Frontend loads without errors
- [ ] Backend API responds (check /health)

**2. Authentication:**
- [ ] Can sign up new user
- [ ] Can log in
- [ ] Session persists across page reloads

**3. Task Operations:**
- [ ] Can create task via chatbot
- [ ] Task appears in UI immediately
- [ ] Can update task (title, description, status)
- [ ] Can mark task complete
- [ ] Can delete task

**4. Kafka Events:**
```bash
# Check events are flowing
kubectl exec -it taskflow-kafka-kafka-0 -n kafka -- \
  bin/kafka-console-consumer.sh \
  --topic task-events \
  --from-beginning \
  --bootstrap-server localhost:9092 \
  --max-messages 5
```
- [ ] Events published to Kafka
- [ ] Event schema correct

**5. Consumer Services:**
- [ ] Create recurring task → complete it → next occurrence created
- [ ] Create task with due date → reminder email received
- [ ] Check audit_logs table → all events logged

**6. Advanced Features:**
- [ ] Set task priority (high/medium/low)
- [ ] Add tags to task
- [ ] Search for tasks by keyword
- [ ] Filter by status, priority, tags
- [ ] Sort tasks by date, priority

**7. Performance:**
- [ ] Create 10 tasks rapidly → all successful
- [ ] Search with 100+ tasks → responds in <2 seconds
- [ ] Multiple users simultaneously → no conflicts

**8. Stability:**
- [ ] Application runs for 30 minutes → no crashes
- [ ] Check pod restarts: `kubectl get pods -n default`
- [ ] Check for memory leaks: `kubectl top pods -n default`

**Acceptance Criteria:**
- All tests pass
- No critical bugs
- Application stable
- Performance acceptable

---

### 6.12 Monitoring and Logging (Optional but Recommended)

#### Task 6.12.1: Setup Basic Monitoring
**Task ID:** P6-T20  
**Priority:** Medium  
**Estimated Time:** 2 hours  
**Dependencies:** P6-T13

**Description:**
Set up basic monitoring with Prometheus and Grafana.

**Manual Steps:**
```bash
# Add Prometheus Helm repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install kube-prometheus-stack
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false

# Wait for pods
kubectl wait --for=condition=ready pod \
  --all \
  -n monitoring \
  --timeout=300s

# Access Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80

# Default credentials:
# Username: admin
# Password: prom-operator

# Open browser: http://localhost:3000
```

**Import Dapr Dashboards:**
- Dashboard ID: 11085 (Dapr System)
- Dashboard ID: 11086 (Dapr Services)

**Acceptance Criteria:**
- Prometheus collecting metrics
- Grafana accessible
- Dapr metrics visible
- Resource usage dashboards working

---

### 6.13 Documentation and Cleanup

#### Task 6.13.1: Document Cloud Deployment
**Task ID:** P6-T21  
**Priority:** High  
**Estimated Time:** 2 hours  
**Dependencies:** P6-T19

**Description:**
Create comprehensive documentation for cloud deployment.

**Claude Code Prompt:**
```
Create cloud deployment documentation.

Location: docs/CLOUD_DEPLOYMENT.md

# Cloud Deployment Guide

## Infrastructure
- Cloud Provider: [Oracle Cloud / GCP / Azure]
- Kubernetes Version: [version]
- Node Count: [X]
- Kafka: [Redpanda Cloud / Strimzi]
- Container Registry: [ghcr.io / other]

## Prerequisites
- Cloud account with credits
- kubectl installed
- Docker installed
- Helm installed
- Dapr CLI installed

## Deployment Steps

### 1. Cluster Setup
[Step-by-step commands used]

### 2. Kafka Setup
[Commands for Kafka deployment]

### 3. Dapr Installation
[Dapr initialization steps]

### 4. Secrets Creation
[How to create secrets - without actual values]

### 5. Application Deployment
[Deployment commands]

### 6. Ingress Configuration
[Ingress setup steps]

## Accessing the Application
URL: http://[EXTERNAL-IP] or https://taskflow.yourdomain.com
Backend API: http://[EXTERNAL-IP]/api/health

## Monitoring
- Grafana: [how to access]
- Prometheus: [how to access]
- Logs: [how to view logs]

## Scaling
How to scale the application:
```bash
kubectl scale deployment backend --replicas=3 -n default
```

## Cost Estimation
[Estimated monthly cost or free tier limits]

## Troubleshooting
Common issues and solutions

## Cleanup
How to delete everything:
```bash
# Delete cluster
[cloud-specific delete commands]
```

Include all actual commands used, URLs, and configurations.
```

**Acceptance Criteria:**
- Complete deployment guide
- All commands documented
- Troubleshooting section
- Cleanup instructions included

---

#### Task 6.13.2: Update Main README
**Task ID:** P6-T22  
**Priority:** High  
**Estimated Time:** 1 hour  
**Dependencies:** P6-T21

**Description:**
Update main README with deployment information and links.

**Updates to README.md:**
```markdown
## Deployments

### Local Development (Minikube)
See [Minikube Deployment Guide](docs/MINIKUBE_DEPLOYMENT.md)

### Production (Cloud)
See [Cloud Deployment Guide](docs/CLOUD_DEPLOYMENT.md)

**Live Demo:** http://taskflow.example.com
**API Health:** http://taskflow.example.com/api/health

## Architecture
[Include updated architecture diagram with cloud components]

## Features
- ✅ All features from Phase I-IV
- ✅ Event-driven architecture with Kafka
- ✅ Dapr for distributed runtime
- ✅ Deployed on Kubernetes
- ✅ High availability (multiple replicas)
- ✅ Monitoring with Prometheus/Grafana
```

**Acceptance Criteria:**
- README updated with deployment info
- Live URL added
- Architecture diagram updated
- All documentation linked

---

## Phase 7: CI/CD Pipeline (Optional - Day 6)

#### Task 7.1: Setup GitHub Actions Workflow
**Task ID:** P7-T1  
**Priority:** Medium  
**Estimated Time:** 3 hours  
**Dependencies:** P6-T13

**Description:**
Create CI/CD pipeline for automatic deployment on push to main.

**Claude Code Prompt:**
```
Create GitHub Actions workflow for CI/CD.

Location: .github/workflows/deploy.yml

name: Build and Deploy to Kubernetes

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    
    strategy:
      matrix:
        service:
          - name: backend
            path: ./backend
          - name: frontend
            path: ./frontend
          - name: recurring-task-service
            path: ./services/recurring-task-service
          - name: notification-service
            path: ./services/notification-service
          - name: audit-service
            path: ./services/audit-service
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Log in to Container Registry
      uses: docker/login-action@v2
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v4
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-${{ matrix.service.name }}
        tags: |
          type=ref,event=branch
          type=sha,prefix={{branch}}-
          type=raw,value=latest,enable={{is_default_branch}}
    
    - name: Build and push Docker image
      uses: docker/build-push-action@v4
      with:
        context: ${{ matrix.service.path }}
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
  
  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Set up kubectl
      uses: azure/setup-kubectl@v3
    
    - name: Configure kubectl
      run: |
        echo "${{ secrets.KUBECONFIG }}" > kubeconfig.yaml
        export KUBECONFIG=kubeconfig.yaml
    
    - name: Deploy to Kubernetes
      run: |
        export KUBECONFIG=kubeconfig.yaml
        kubectl apply -f k8s/production/ -n default
        kubectl rollout status deployment/backend -n default
        kubectl rollout status deployment/frontend -n default
    
    - name: Verify deployment
      run: |
        export KUBECONFIG=kubeconfig.yaml
        kubectl get pods -n default
        kubectl get services -n default

Add secrets to GitHub:
- KUBECONFIG: base64 encoded kubeconfig file
```

**Setup GitHub Secrets:**
```bash
# Encode kubeconfig
cat ~/.kube/config | base64 > kubeconfig.b64

# Add to GitHub:
# Settings → Secrets and variables → Actions → New repository secret
# Name: KUBECONFIG
# Value: [paste content of kubeconfig.b64]
```

**Acceptance Criteria:**
- GitHub Actions workflow created
- Workflow triggers on push to main
- Images built and pushed automatically
- Deployment triggered automatically
- Workflow succeeds

---

## Final Checklist

### Pre-Submission Checklist
**Task ID:** FINAL-T1  
**Priority:** Critical

- [ ] **Minikube Deployment:**
  - [ ] Application runs on Minikube
  - [ ] All features tested locally
  - [ ] Documentation complete

- [ ] **Cloud Deployment:**
  - [ ] Application deployed to cloud
  - [ ] Accessible via public URL
  - [ ] All features working
  - [ ] Stable for 1+ hour

- [ ] **Code Quality:**
  - [ ] All code in GitHub repository
  - [ ] No secrets in repository
  - [ ] README.md comprehensive
  - [ ] CLAUDE.md with instructions
  - [ ] Architecture diagrams included

- [ ] **Documentation:**
  - [ ] Minikube deployment guide
  - [ ] Cloud deployment guide
  - [ ] Troubleshooting section
  - [ ] API documentation
  - [ ] Environment variables documented

- [ ] **Demo Video:**
  - [ ] Video recorded (under 90 seconds)
  - [ ] Shows architecture
  - [ ] Demonstrates features
  - [ ] Shows deployment
  - [ ] Uploaded to YouTube

- [ ] **Submission:**
  - [ ] GitHub repository public
  - [ ] Live URL accessible
  - [ ] Demo video linked
  - [ ] All required files present
  - [ ] Submission form filled

---

## Time Estimates Summary

| Phase | Tasks | Estimated Time |
|-------|-------|----------------|
| Phase 5: Minikube | 24 tasks | 12-16 hours (1.5-2 days) |
| Phase 6: Cloud | 22 tasks | 16-24 hours (2-3 days) |
| Phase 7: CI/CD (Optional) | 1 task | 3 hours |
| **Total** | **47 tasks** | **31-43 hours (4-5 days)** |

---

## Quick Reference Commands

### Minikube
```bash
# Start
minikube start --cpus=4 --memory=8192

# Get frontend URL
minikube service frontend-service --url

# SSH into Minikube
minikube ssh

# Stop
minikube stop

# Delete
minikube delete
```

### Kubectl
```bash
# Get all resources
kubectl get all -n default

# Check pod logs
kubectl logs -f <pod-name> -c <container-name> -n default

# Exec into pod
kubectl exec -it <pod-name> -c <container-name> -n default -- /bin/bash

# Port forward
kubectl port-forward svc/<service-name> 8000:8000 -n default

# Describe resource
kubectl describe pod <pod-name> -n default

# Delete all resources
kubectl delete all --all -n default
```

### Dapr
```bash
# Check Dapr status
dapr status -k

# View Dapr logs
dapr logs --app-id backend-service -k

# Dapr dashboard
dapr dashboard -k
```

### Kafka (Strimzi)
```bash
# List topics
kubectl exec -it taskflow-kafka-kafka-0 -n kafka -- \
  bin/kafka-topics.sh --list --bootstrap-server localhost:9092

# Consume messages
kubectl exec -it taskflow-kafka-kafka-0 -n kafka -- \
  bin/kafka-console-consumer.sh \
  --topic task-events \
  --from-beginning \
  --bootstrap-server localhost:9092
```

---

**Good luck with your cloud deployment! Follow these tasks systematically and you'll have a production-ready application running on Kubernetes. 🚀**