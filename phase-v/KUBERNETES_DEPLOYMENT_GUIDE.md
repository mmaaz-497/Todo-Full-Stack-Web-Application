# Kubernetes Deployment Guide - Phase V

Complete guide for deploying the Todo AI Chatbot microservices architecture to Kubernetes.

## Table of Contents

1. [Deployment Architecture](#deployment-architecture)
2. [Prerequisites](#prerequisites)
3. [Infrastructure Setup](#infrastructure-setup)
4. [Deployment Sequence](#deployment-sequence)
5. [Local Deployment (Minikube)](#local-deployment-minikube)
6. [Cloud Deployment (AKS/GKE/OKE)](#cloud-deployment-aksgkeoke)
7. [Verification & Testing](#verification--testing)
8. [Troubleshooting](#troubleshooting)

## Deployment Architecture

### Service Topology

```
┌─────────────────────────────────────────────────────────────────┐
│                         Kubernetes Cluster                       │
│                                                                   │
│  ┌────────────────┐      ┌──────────────────────────────────┐  │
│  │   Ingress      │──────│  API Service (FastAPI)           │  │
│  │  (NGINX/Traefik)│      │  + Dapr Sidecar                  │  │
│  └────────────────┘      └──────────────────────────────────┘  │
│                                     │                            │
│                          ┌──────────┴──────────┐                │
│                          │                     │                │
│  ┌───────────────────────▼───┐    ┌───────────▼──────────────┐ │
│  │  Auth Service (Better-Auth)│    │ WebSocket Sync Service  │ │
│  │  + Dapr Sidecar            │    │ + Dapr Sidecar          │ │
│  └────────────────────────────┘    └─────────────────────────┘ │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Kafka Event Backbone (Strimzi)              │  │
│  │  Topics: task-events, reminders, task-updates            │  │
│  └──────────────┬───────────────────┬──────────────────┬────┘  │
│                 │                   │                  │        │
│  ┌──────────────▼────┐  ┌──────────▼────┐  ┌─────────▼──────┐ │
│  │ Recurring Task    │  │ Notification  │  │ Audit Service  │ │
│  │ Service           │  │ Service       │  │ + Dapr Sidecar │ │
│  │ + Dapr Sidecar    │  │ + Dapr Sidecar│  └────────────────┘ │
│  └───────────────────┘  └───────────────┘                      │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         Dapr Control Plane (dapr-system namespace)       │  │
│  │  - dapr-operator   - dapr-placement                      │  │
│  │  - dapr-sidecar-injector  - dapr-sentry                  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────┐      ┌──────────────────────────────┐   │
│  │  PostgreSQL      │      │  Redis (optional)            │   │
│  │  StatefulSet     │      │  For distributed state       │   │
│  └──────────────────┘      └──────────────────────────────┘   │
└───────────────────────────────────────────────────────────────┘
```

### Key Components

| Component | Type | Replicas | Dapr Enabled | Purpose |
|-----------|------|----------|--------------|---------|
| API Service | Deployment | 3 | ✅ | Main REST API, task CRUD, chat |
| Auth Service | Deployment | 2 | ✅ | Better-Auth authentication |
| Recurring Task Service | Deployment | 2 | ✅ | Generate recurring task instances |
| Notification Service | Deployment | 2 | ✅ | Send email notifications |
| Audit Service | Deployment | 2 | ✅ | Event logging and compliance |
| WebSocket Sync Service | Deployment | 2 | ✅ | Real-time task synchronization |
| PostgreSQL | StatefulSet | 1 | ❌ | Primary database |
| Kafka (Strimzi) | StatefulSet | 3 | ❌ | Event streaming backbone |
| Dapr Control Plane | Deployment | - | - | Dapr infrastructure |

## Prerequisites

### Tools Required

```bash
# Kubernetes CLI
kubectl version --client

# Dapr CLI
dapr version

# Helm (for Kafka and other charts)
helm version

# Docker (for building images)
docker version

# Optional: k9s for cluster management
k9s version
```

### Minimum Cluster Requirements

**Local (Minikube):**
- CPU: 4 cores
- Memory: 8GB RAM
- Disk: 20GB

**Production (AKS/GKE/OKE):**
- Nodes: 3+ worker nodes
- CPU per node: 4 cores
- Memory per node: 16GB RAM
- Disk: 50GB SSD per node

## Infrastructure Setup

### Step 1: Install Dapr on Kubernetes

```bash
# Initialize Dapr on Kubernetes cluster
dapr init -k

# Verify Dapr installation
dapr status -k

# Expected output:
#   NAME                   NAMESPACE    HEALTHY  STATUS   REPLICAS  VERSION  AGE  CREATED
#   dapr-sidecar-injector  dapr-system  True     Running  1         1.12.0   1m   2024-01-04 10:00:00
#   dapr-sentry            dapr-system  True     Running  1         1.12.0   1m   2024-01-04 10:00:00
#   dapr-operator          dapr-system  True     Running  1         1.12.0   1m   2024-01-04 10:00:00
#   dapr-placement-server  dapr-system  True     Running  1         1.12.0   1m   2024-01-04 10:00:00

# Verify namespace
kubectl get pods -n dapr-system
```

### Step 2: Install Kafka (Strimzi Operator)

```bash
# Add Strimzi Helm repository
helm repo add strimzi https://strimzi.io/charts/
helm repo update

# Create namespace
kubectl create namespace kafka

# Install Strimzi operator
helm install kafka-operator strimzi/strimzi-kafka-operator \
  --namespace kafka \
  --set watchNamespaces="{default,kafka}"

# Wait for operator to be ready
kubectl wait --for=condition=ready pod -l name=strimzi-cluster-operator -n kafka --timeout=300s
```

### Step 3: Deploy Kafka Cluster

Create `phase-v/kubernetes/infrastructure/kafka-cluster.yaml`:

```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: kafka-cluster
  namespace: default
spec:
  kafka:
    version: 3.6.0
    replicas: 3
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
      auto.create.topics.enable: true
    storage:
      type: persistent-claim
      size: 10Gi
      class: standard
  zookeeper:
    replicas: 3
    storage:
      type: persistent-claim
      size: 5Gi
      class: standard
  entityOperator:
    topicOperator: {}
    userOperator: {}
---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: task-events
  namespace: default
  labels:
    strimzi.io/cluster: kafka-cluster
spec:
  partitions: 6
  replicas: 3
  config:
    retention.ms: 604800000  # 7 days
    segment.bytes: 1073741824
---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: reminders
  namespace: default
  labels:
    strimzi.io/cluster: kafka-cluster
spec:
  partitions: 3
  replicas: 3
  config:
    retention.ms: 86400000  # 1 day
---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: task-updates
  namespace: default
  labels:
    strimzi.io/cluster: kafka-cluster
spec:
  partitions: 6
  replicas: 3
  config:
    retention.ms: 3600000  # 1 hour
```

Deploy Kafka:

```bash
kubectl apply -f phase-v/kubernetes/infrastructure/kafka-cluster.yaml

# Wait for Kafka to be ready (takes 5-10 minutes)
kubectl wait kafka/kafka-cluster --for=condition=Ready --timeout=600s -n default

# Verify Kafka pods
kubectl get pods -l strimzi.io/cluster=kafka-cluster
```

### Step 4: Deploy PostgreSQL

Create `phase-v/kubernetes/infrastructure/postgres.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: postgres-config
  namespace: default
data:
  POSTGRES_DB: todo_db
  POSTGRES_USER: postgres
---
apiVersion: v1
kind: Secret
metadata:
  name: postgres-secret
  namespace: default
type: Opaque
stringData:
  POSTGRES_PASSWORD: "your-secure-password-change-in-production"
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
  namespace: default
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
  storageClassName: standard
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: default
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15-alpine
        ports:
        - containerPort: 5432
          name: postgres
        envFrom:
        - configMapRef:
            name: postgres-config
        - secretRef:
            name: postgres-secret
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
          subPath: postgres
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          exec:
            command:
            - pg_isready
            - -U
            - postgres
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          exec:
            command:
            - pg_isready
            - -U
            - postgres
          initialDelaySeconds: 5
          periodSeconds: 5
  volumeClaimTemplates:
  - metadata:
      name: postgres-storage
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: standard
      resources:
        requests:
          storage: 10Gi
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: default
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
  clusterIP: None  # Headless service
```

Deploy PostgreSQL:

```bash
kubectl apply -f phase-v/kubernetes/infrastructure/postgres.yaml

# Wait for PostgreSQL to be ready
kubectl wait --for=condition=ready pod -l app=postgres --timeout=300s

# Verify
kubectl get statefulset postgres
kubectl get svc postgres
```

### Step 5: Create Application Secrets

Create `phase-v/kubernetes/secrets/backend-secrets.yaml`:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: backend-secrets
  namespace: default
type: Opaque
stringData:
  # Database
  DATABASE_URL: "postgresql://postgres:your-secure-password-change-in-production@postgres.default.svc.cluster.local:5432/todo_db"

  # JWT
  JWT_SECRET_KEY: "your-jwt-secret-key-change-in-production-min-32-chars"

  # Better Auth
  BETTER_AUTH_SECRET: "your-better-auth-secret-change-in-production"
  BETTER_AUTH_URL: "http://better-auth-service.default.svc.cluster.local:3001"

  # SMTP (for notifications)
  SMTP_HOST: "smtp.gmail.com"
  SMTP_PORT: "587"
  SMTP_USERNAME: "your-email@gmail.com"
  SMTP_PASSWORD: "your-app-specific-password"
  SMTP_FROM_EMAIL: "noreply@yourdomain.com"
  SMTP_FROM_NAME: "Todo App Notifications"
```

Apply secrets:

```bash
# Edit the file with your actual credentials first!
kubectl apply -f phase-v/kubernetes/secrets/backend-secrets.yaml

# Verify
kubectl get secret backend-secrets
```

### Step 6: Deploy Dapr Components

```bash
# Deploy local Dapr components (for Minikube)
kubectl apply -f phase-v/dapr-components/local/

# OR deploy cloud Dapr components (for AKS/GKE/OKE with Redpanda Cloud)
# kubectl apply -f phase-v/dapr-components/cloud/

# Verify Dapr components
kubectl get components

# Expected output:
#   NAME                  AGE
#   kafka-pubsub          10s
#   secrets-kubernetes    10s
#   statestore-postgres   10s
```

## Deployment Sequence

Deploy services in this order to respect dependencies:

1. **Database & Infrastructure** (PostgreSQL, Kafka) ✅ Done above
2. **Dapr Components** ✅ Done above
3. **Auth Service** (authentication foundation)
4. **API Service** (depends on Auth)
5. **Event-Driven Services** (Recurring Task, Notification, Audit, WebSocket)

## Service Deployments

### 1. Auth Service Deployment

Create `phase-v/kubernetes/deployments/auth-service.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: better-auth-service
  namespace: default
spec:
  replicas: 2
  selector:
    matchLabels:
      app: better-auth-service
  template:
    metadata:
      labels:
        app: better-auth-service
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "better-auth-service"
        dapr.io/app-port: "3001"
        dapr.io/log-level: "info"
        dapr.io/config: "dapr-config"
    spec:
      containers:
      - name: better-auth-service
        image: your-registry/better-auth-service:latest
        ports:
        - containerPort: 3001
          name: http
        env:
        - name: NODE_ENV
          value: "production"
        - name: PORT
          value: "3001"
        envFrom:
        - secretRef:
            name: backend-secrets
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /api/auth/health
            port: 3001
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/auth/health
            port: 3001
          initialDelaySeconds: 10
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: better-auth-service
  namespace: default
spec:
  selector:
    app: better-auth-service
  ports:
  - port: 3001
    targetPort: 3001
    name: http
  type: ClusterIP
```

### 2. API Service Deployment

Create `phase-v/kubernetes/deployments/api-service.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-service
  namespace: default
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api-service
  template:
    metadata:
      labels:
        app: api-service
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "api-service"
        dapr.io/app-port: "8000"
        dapr.io/log-level: "info"
        dapr.io/config: "dapr-config"
    spec:
      containers:
      - name: api-service
        image: your-registry/api-service:latest
        ports:
        - containerPort: 8000
          name: http
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: DAPR_HTTP_URL
          value: "http://localhost:3500"
        - name: DAPR_PUBSUB
          value: "kafka-pubsub"
        - name: USE_DAPR_INVOCATION
          value: "true"
        - name: DAPR_APP_ID_AUTH
          value: "better-auth-service"
        envFrom:
        - secretRef:
            name: backend-secrets
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
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
          initialDelaySeconds: 10
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: api-service
  namespace: default
spec:
  selector:
    app: api-service
  ports:
  - port: 8000
    targetPort: 8000
    name: http
  type: ClusterIP
```

### 3. Recurring Task Service Deployment

Create `phase-v/kubernetes/deployments/recurring-task-service.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: recurring-task-service
  namespace: default
spec:
  replicas: 2
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
        dapr.io/log-level: "info"
        dapr.io/config: "dapr-config"
    spec:
      containers:
      - name: recurring-task-service
        image: your-registry/recurring-task-service:latest
        ports:
        - containerPort: 8001
          name: http
        env:
        - name: DAPR_HTTP_URL
          value: "http://localhost:3500"
        - name: DAPR_PUBSUB
          value: "kafka-pubsub"
        - name: DAPR_TOPIC
          value: "task-events"
        - name: DAPR_STATE_STORE
          value: "statestore-postgres"
        envFrom:
        - secretRef:
            name: backend-secrets
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8001
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8001
          initialDelaySeconds: 10
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: recurring-task-service
  namespace: default
spec:
  selector:
    app: recurring-task-service
  ports:
  - port: 8001
    targetPort: 8001
    name: http
  type: ClusterIP
```

### 4. Notification Service Deployment

Create `phase-v/kubernetes/deployments/notification-service.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: notification-service
  namespace: default
spec:
  replicas: 2
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
        dapr.io/log-level: "info"
        dapr.io/config: "dapr-config"
    spec:
      containers:
      - name: notification-service
        image: your-registry/notification-service:latest
        ports:
        - containerPort: 8002
          name: http
        env:
        - name: DAPR_HTTP_URL
          value: "http://localhost:3500"
        - name: DAPR_PUBSUB
          value: "kafka-pubsub"
        - name: DAPR_TOPIC
          value: "reminders"
        - name: DAPR_SECRETS_STORE
          value: "secrets-kubernetes"
        - name: DAPR_STATE_STORE
          value: "statestore-postgres"
        envFrom:
        - secretRef:
            name: backend-secrets
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8002
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8002
          initialDelaySeconds: 10
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: notification-service
  namespace: default
spec:
  selector:
    app: notification-service
  ports:
  - port: 8002
    targetPort: 8002
    name: http
  type: ClusterIP
```

### 5. Audit Service Deployment

Create `phase-v/kubernetes/deployments/audit-service.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: audit-service
  namespace: default
spec:
  replicas: 2
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
        dapr.io/log-level: "info"
        dapr.io/config: "dapr-config"
    spec:
      containers:
      - name: audit-service
        image: your-registry/audit-service:latest
        ports:
        - containerPort: 8003
          name: http
        env:
        - name: DAPR_HTTP_URL
          value: "http://localhost:3500"
        - name: DAPR_PUBSUB
          value: "kafka-pubsub"
        envFrom:
        - secretRef:
            name: backend-secrets
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8003
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8003
          initialDelaySeconds: 10
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: audit-service
  namespace: default
spec:
  selector:
    app: audit-service
  ports:
  - port: 8003
    targetPort: 8003
    name: http
  type: ClusterIP
```

### 6. WebSocket Sync Service Deployment

Create `phase-v/kubernetes/deployments/websocket-sync-service.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: websocket-sync-service
  namespace: default
spec:
  replicas: 2
  selector:
    matchLabels:
      app: websocket-sync-service
  template:
    metadata:
      labels:
        app: websocket-sync-service
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "websocket-sync-service"
        dapr.io/app-port: "8004"
        dapr.io/log-level: "info"
        dapr.io/config: "dapr-config"
    spec:
      containers:
      - name: websocket-sync-service
        image: your-registry/websocket-sync-service:latest
        ports:
        - containerPort: 8004
          name: http
        env:
        - name: DAPR_HTTP_URL
          value: "http://localhost:3500"
        - name: DAPR_PUBSUB
          value: "kafka-pubsub"
        - name: DAPR_TOPIC
          value: "task-updates"
        envFrom:
        - secretRef:
            name: backend-secrets
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8004
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8004
          initialDelaySeconds: 10
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: websocket-sync-service
  namespace: default
spec:
  selector:
    app: websocket-sync-service
  ports:
  - port: 8004
    targetPort: 8004
    name: http
  type: ClusterIP
  sessionAffinity: ClientIP  # Sticky sessions for WebSocket
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 10800  # 3 hours
```

## Local Deployment (Minikube)

Complete deployment script for local development:

```bash
#!/bin/bash
# deploy-local.sh

set -e

echo "🚀 Deploying Todo App to Minikube..."

# 1. Start Minikube with sufficient resources
echo "📦 Starting Minikube..."
minikube start --cpus=4 --memory=8192 --disk-size=20g

# 2. Enable addons
echo "🔌 Enabling Minikube addons..."
minikube addons enable ingress
minikube addons enable metrics-server

# 3. Initialize Dapr
echo "🔧 Installing Dapr..."
dapr init -k

# Wait for Dapr to be ready
kubectl wait --for=condition=ready pod -l app=dapr-operator -n dapr-system --timeout=300s

# 4. Install Kafka
echo "☕ Installing Kafka (Strimzi)..."
helm repo add strimzi https://strimzi.io/charts/
helm repo update
kubectl create namespace kafka --dry-run=client -o yaml | kubectl apply -f -

helm upgrade --install kafka-operator strimzi/strimzi-kafka-operator \
  --namespace kafka \
  --set watchNamespaces="{default,kafka}"

kubectl wait --for=condition=ready pod -l name=strimzi-cluster-operator -n kafka --timeout=300s

# Deploy Kafka cluster
kubectl apply -f phase-v/kubernetes/infrastructure/kafka-cluster.yaml
kubectl wait kafka/kafka-cluster --for=condition=Ready --timeout=600s -n default

# 5. Deploy PostgreSQL
echo "🐘 Deploying PostgreSQL..."
kubectl apply -f phase-v/kubernetes/infrastructure/postgres.yaml
kubectl wait --for=condition=ready pod -l app=postgres --timeout=300s

# 6. Create secrets
echo "🔐 Creating secrets..."
kubectl apply -f phase-v/kubernetes/secrets/backend-secrets.yaml

# 7. Deploy Dapr components
echo "🎯 Deploying Dapr components..."
kubectl apply -f phase-v/dapr-components/local/

# 8. Build and load Docker images into Minikube
echo "🐳 Building and loading Docker images..."
eval $(minikube docker-env)

docker build -t api-service:latest ./backend/api-service
docker build -t recurring-task-service:latest ./phase-v/services/recurring-task-service
docker build -t notification-service:latest ./phase-v/services/notification-service
docker build -t audit-service:latest ./phase-v/services/audit-service
docker build -t websocket-sync-service:latest ./phase-v/services/websocket-sync-service

# 9. Deploy services
echo "🚢 Deploying microservices..."
kubectl apply -f phase-v/kubernetes/deployments/

# Wait for all deployments
echo "⏳ Waiting for deployments to be ready..."
kubectl wait --for=condition=available deployment/api-service --timeout=300s
kubectl wait --for=condition=available deployment/recurring-task-service --timeout=300s
kubectl wait --for=condition=available deployment/notification-service --timeout=300s
kubectl wait --for=condition=available deployment/audit-service --timeout=300s
kubectl wait --for=condition=available deployment/websocket-sync-service --timeout=300s

# 10. Expose API service
echo "🌐 Exposing API service..."
kubectl expose deployment api-service --type=NodePort --port=8000

# Get service URL
API_URL=$(minikube service api-service --url)

echo "✅ Deployment complete!"
echo ""
echo "📊 Service URLs:"
echo "  API Service: $API_URL"
echo "  Minikube Dashboard: minikube dashboard"
echo ""
echo "🔍 Useful commands:"
echo "  kubectl get pods"
echo "  kubectl get svc"
echo "  kubectl logs -f deployment/api-service -c api-service"
echo "  kubectl logs -f deployment/api-service -c daprd"
```

Run deployment:

```bash
chmod +x deploy-local.sh
./deploy-local.sh
```

## Cloud Deployment (AKS/GKE/OKE)

### Azure Kubernetes Service (AKS)

```bash
#!/bin/bash
# deploy-aks.sh

set -e

# Configuration
RESOURCE_GROUP="todo-app-rg"
CLUSTER_NAME="todo-app-aks"
LOCATION="eastus"
NODE_COUNT=3
NODE_SIZE="Standard_D4s_v3"
REGISTRY_NAME="todoappregistry"

echo "🚀 Deploying to Azure Kubernetes Service..."

# 1. Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# 2. Create AKS cluster
az aks create \
  --resource-group $RESOURCE_GROUP \
  --name $CLUSTER_NAME \
  --node-count $NODE_COUNT \
  --node-vm-size $NODE_SIZE \
  --enable-managed-identity \
  --generate-ssh-keys \
  --network-plugin azure \
  --enable-addons monitoring

# 3. Get credentials
az aks get-credentials --resource-group $RESOURCE_GROUP --name $CLUSTER_NAME

# 4. Create Azure Container Registry
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $REGISTRY_NAME \
  --sku Standard

# Attach ACR to AKS
az aks update \
  --name $CLUSTER_NAME \
  --resource-group $RESOURCE_GROUP \
  --attach-acr $REGISTRY_NAME

# 5. Build and push images
az acr build --registry $REGISTRY_NAME --image api-service:latest ./backend/api-service
az acr build --registry $REGISTRY_NAME --image recurring-task-service:latest ./phase-v/services/recurring-task-service
az acr build --registry $REGISTRY_NAME --image notification-service:latest ./phase-v/services/notification-service
az acr build --registry $REGISTRY_NAME --image audit-service:latest ./phase-v/services/audit-service
az acr build --registry $REGISTRY_NAME --image websocket-sync-service:latest ./phase-v/services/websocket-sync-service

# 6. Install Dapr
dapr init -k

# 7. Install infrastructure (Kafka with Redpanda Cloud, PostgreSQL)
# Use cloud Dapr components
kubectl apply -f phase-v/kubernetes/secrets/kafka-secrets.yaml
kubectl apply -f phase-v/kubernetes/secrets/backend-secrets.yaml
kubectl apply -f phase-v/dapr-components/cloud/

# Deploy PostgreSQL (or use Azure Database for PostgreSQL)
kubectl apply -f phase-v/kubernetes/infrastructure/postgres.yaml

# 8. Update deployment YAMLs with ACR image paths
# Example: todoappregistry.azurecr.io/api-service:latest

# 9. Deploy services
kubectl apply -f phase-v/kubernetes/deployments/

# 10. Create Ingress
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: todo-app-ingress
  annotations:
    kubernetes.io/ingress.class: azure/application-gateway
spec:
  rules:
  - host: api.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: api-service
            port:
              number: 8000
  - host: ws.yourdomain.com
    http:
      paths:
      - path: /ws
        pathType: Prefix
        backend:
          service:
            name: websocket-sync-service
            port:
              number: 8004
EOF

echo "✅ AKS deployment complete!"
```

## Verification & Testing

### 1. Check Pod Status

```bash
# View all pods
kubectl get pods

# Expected output (all Running with 2/2 containers - app + dapr sidecar):
#   NAME                                       READY   STATUS    RESTARTS   AGE
#   api-service-5d8f7c9b4d-abcde              2/2     Running   0          5m
#   recurring-task-service-6c8d9f7a5b-fghij   2/2     Running   0          5m
#   notification-service-7d9e8f6b4c-klmno     2/2     Running   0          5m
#   audit-service-8e7f9g5c3d-pqrst            2/2     Running   0          5m
#   websocket-sync-service-9f8g7h6d5e-uvwxy   2/2     Running   0          5m
#   postgres-0                                 1/1     Running   0          10m
#   kafka-cluster-kafka-0                      1/1     Running   0          10m
#   kafka-cluster-kafka-1                      1/1     Running   0          10m
#   kafka-cluster-kafka-2                      1/1     Running   0          10m

# Check Dapr sidecars
kubectl get pods -l dapr.io/enabled=true
```

### 2. Test API Endpoints

```bash
# Port-forward API service
kubectl port-forward svc/api-service 8000:8000

# Test health endpoint
curl http://localhost:8000/health

# Test task creation (with auth token)
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "title": "Test Task",
    "description": "Testing Kubernetes deployment",
    "status": "pending"
  }'
```

### 3. Verify Kafka Events

```bash
# Exec into Kafka pod
kubectl exec -it kafka-cluster-kafka-0 -- bash

# Consume task-events topic
/opt/kafka/bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic task-events \
  --from-beginning
```

### 4. Check Service Logs

```bash
# API Service logs (app container)
kubectl logs -f deployment/api-service -c api-service

# API Service logs (Dapr sidecar)
kubectl logs -f deployment/api-service -c daprd

# Recurring Task Service logs
kubectl logs -f deployment/recurring-task-service -c recurring-task-service

# Notification Service logs
kubectl logs -f deployment/notification-service -c notification-service

# All logs from a pod
kubectl logs -f pod-name --all-containers
```

### 5. Test WebSocket Connection

```bash
# Port-forward WebSocket service
kubectl port-forward svc/websocket-sync-service 8004:8004

# Connect with websocat
websocat "ws://localhost:8004/ws?token=YOUR_JWT_TOKEN"

# Send ping
{"type": "ping"}

# Expected response
{"type": "pong"}
```

## Troubleshooting

### Dapr Sidecar Not Injecting

```bash
# Check Dapr installation
dapr status -k

# Verify annotations on deployment
kubectl describe pod api-service-xxx | grep dapr

# Check Dapr operator logs
kubectl logs -n dapr-system -l app=dapr-operator
```

### Service Can't Connect to Kafka

```bash
# Verify Kafka is ready
kubectl get kafka kafka-cluster

# Check Dapr pubsub component
kubectl describe component kafka-pubsub

# Test Kafka connectivity from pod
kubectl exec -it api-service-xxx -c api-service -- sh
curl http://localhost:3500/v1.0/metadata
```

### Database Connection Issues

```bash
# Check PostgreSQL pod
kubectl logs postgres-0

# Test connection from app pod
kubectl exec -it api-service-xxx -c api-service -- sh
psql postgresql://postgres:password@postgres.default.svc.cluster.local:5432/todo_db
```

### High Memory/CPU Usage

```bash
# Check resource usage
kubectl top pods
kubectl top nodes

# Describe pod for resource limits
kubectl describe pod api-service-xxx

# Adjust resources in deployment YAML
resources:
  requests:
    memory: "512Mi"  # Increase
    cpu: "500m"
  limits:
    memory: "2Gi"
    cpu: "2000m"
```

## Summary

**Deployment Flow:**
1. Infrastructure (Kafka, PostgreSQL, Dapr) → 2. Secrets & Components → 3. Services (Auth → API → Event-driven services)

**Key Points:**
- **Dapr sidecars** are automatically injected via annotations
- **Service-to-service** calls use Dapr service invocation
- **Events** flow through Kafka via Dapr Pub/Sub
- **Secrets** managed via Kubernetes Secrets + Dapr Secrets component
- **State** persisted in PostgreSQL via Dapr State Management
- **WebSocket** uses sticky sessions for multi-device support

**Next Steps:**
- Set up Helm charts for easier deployment
- Implement CI/CD pipeline (GitHub Actions / Azure DevOps)
- Configure monitoring (Prometheus, Grafana)
- Set up distributed tracing (Jaeger, Zipkin)
- Implement autoscaling (HPA, KEDA)
