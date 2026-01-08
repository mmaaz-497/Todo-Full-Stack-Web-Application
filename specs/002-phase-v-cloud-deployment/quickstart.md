# Quickstart: Phase V - Local Development Environment

**Feature**: Phase V - Advanced Cloud Deployment
**Purpose**: Get the complete event-driven Todo AI Chatbot running locally on Minikube with Dapr, Kafka, and all microservices
**Estimated Setup Time**: 30 minutes

---

## Prerequisites

### Required Software

| Tool | Version | Purpose | Installation |
|------|---------|---------|--------------|
| **Minikube** | 1.32+ | Local Kubernetes cluster | `brew install minikube` (macOS) or [minikube.sigs.k8.io](https://minikube.sigs.k8.io/) |
| **kubectl** | 1.24+ | Kubernetes CLI | `brew install kubectl` or [kubernetes.io/docs/tasks/tools](https://kubernetes.io/docs/tasks/tools/) |
| **Helm** | 3.10+ | Kubernetes package manager | `brew install helm` or [helm.sh/docs/intro/install](https://helm.sh/docs/intro/install/) |
| **Dapr CLI** | 1.12+ | Dapr command-line tool | `wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash` |
| **Docker** | 24+ | Container runtime | [docker.com/get-docker](https://www.docker.com/get-docker) |

### System Requirements

- **CPU**: 4 cores minimum
- **RAM**: 8GB minimum
- **Disk**: 20GB free space
- **OS**: Windows 10+, macOS 10.15+, or Linux (Ubuntu 20.04+)

---

## Step 1: Start Minikube

```bash
# Start Minikube with sufficient resources
minikube start --cpus=4 --memory=8192 --driver=docker

# Verify cluster is running
kubectl get nodes

# Expected output:
# NAME       STATUS   ROLES           AGE   VERSION
# minikube   Ready    control-plane   1m    v1.28.3

# Enable required addons
minikube addons enable ingress
minikube addons enable metrics-server
```

---

## Step 2: Install Dapr on Kubernetes

```bash
# Initialize Dapr in Kubernetes mode
dapr init -k

# Verify Dapr installation
kubectl get pods -n dapr-system

# Expected output (all pods Running):
# NAME                                     READY   STATUS    RESTARTS   AGE
# dapr-dashboard-xxx                       1/1     Running   0          1m
# dapr-operator-xxx                        1/1     Running   0          1m
# dapr-placement-server-xxx                1/1     Running   0          1m
# dapr-sentry-xxx                          1/1     Running   0          1m
# dapr-sidecar-injector-xxx                1/1     Running   0          1m

# Access Dapr dashboard (optional)
dapr dashboard -k
# Opens http://localhost:8080 in browser
```

---

## Step 3: Create Kubernetes Namespace

```bash
# Create development namespace
kubectl create namespace todo-app-dev

# Verify namespace
kubectl get namespaces | grep todo-app-dev
```

---

## Step 4: Deploy Kafka (Redpanda)

### Option A: Redpanda (Recommended for local - lower memory)

```bash
# Add Redpanda Helm repo
helm repo add redpanda https://charts.redpanda.com
helm repo update

# Install Redpanda
helm install redpanda redpanda/redpanda \
  --namespace todo-app-dev \
  --set replicas=1 \
  --set resources.memory.container.max=512Mi \
  --set resources.cpu.cores=1 \
  --set storage.persistentVolume.size=10Gi

# Wait for Redpanda to be ready
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=redpanda -n todo-app-dev --timeout=5m

# Verify Redpanda is running
kubectl get pods -n todo-app-dev | grep redpanda
```

### Option B: Strimzi (Alternative - full Kafka)

```bash
# Apply Strimzi Operator
kubectl apply -f kubernetes/kafka/local/strimzi-operator.yaml -n todo-app-dev

# Wait for operator
kubectl wait --for=condition=ready pod -l name=strimzi-cluster-operator -n todo-app-dev --timeout=2m

# Deploy Kafka cluster
kubectl apply -f kubernetes/kafka/local/kafka-cluster.yaml -n todo-app-dev

# Wait for Kafka brokers
kubectl wait kafka/kafka-cluster --for=condition=Ready --timeout=5m -n todo-app-dev
```

---

## Step 5: Create Kafka Topics

```bash
# Apply topic definitions
kubectl apply -f kubernetes/kafka/local/task-events-topic.yaml -n todo-app-dev
kubectl apply -f kubernetes/kafka/local/reminders-topic.yaml -n todo-app-dev
kubectl apply -f kubernetes/kafka/local/task-updates-topic.yaml -n todo-app-dev
kubectl apply -f kubernetes/kafka/local/dlq-events-topic.yaml -n todo-app-dev

# Verify topics created
kubectl get kafkatopics -n todo-app-dev

# Expected output:
# NAME            CLUSTER         PARTITIONS   REPLICATION FACTOR   READY
# task-events     kafka-cluster   6            1                    True
# reminders       kafka-cluster   3            1                    True
# task-updates    kafka-cluster   6            1                    True
# dlq-events      kafka-cluster   3            1                    True
```

---

## Step 6: Configure Database Secrets

```bash
# Create database connection secret
kubectl create secret generic database-credentials \
  --from-literal=connectionString="postgresql://user:password@neon.tech:5432/tododb?sslmode=require" \
  --namespace todo-app-dev

# Create SMTP credentials for notifications
kubectl create secret generic smtp-credentials \
  --from-literal=host="smtp.gmail.com" \
  --from-literal=port="587" \
  --from-literal=username="your-email@gmail.com" \
  --from-literal=password="your-app-password" \
  --namespace todo-app-dev

# Verify secrets
kubectl get secrets -n todo-app-dev
```

---

## Step 7: Deploy Dapr Components

```bash
# Deploy pub/sub component (Kafka)
kubectl apply -f dapr-components/local/kafka-pubsub.yaml -n todo-app-dev

# Deploy state store component (PostgreSQL)
kubectl apply -f dapr-components/local/postgres-statestore.yaml -n todo-app-dev

# Deploy secrets component (Kubernetes)
kubectl apply -f dapr-components/local/kubernetes-secrets.yaml -n todo-app-dev

# Verify components
kubectl get components -n todo-app-dev

# Expected output:
# NAME                  AGE
# kafka-pubsub          1m
# postgres-statestore   1m
# kubernetes-secrets    1m
```

---

## Step 8: Build and Push Docker Images

```bash
# Build all service images
docker build -t todo-api-service:latest ./backend/api-service
docker build -t recurring-task-service:latest ./backend/recurring-task-service
docker build -t notification-service:latest ./backend/notification-service
docker build -t audit-service:latest ./backend/audit-service
docker build -t websocket-sync-service:latest ./backend/websocket-sync-service
docker build -t frontend:latest ./frontend

# Load images into Minikube (so Minikube can access them)
minikube image load todo-api-service:latest
minikube image load recurring-task-service:latest
minikube image load notification-service:latest
minikube image load audit-service:latest
minikube image load websocket-sync-service:latest
minikube image load frontend:latest

# Verify images loaded
minikube image ls | grep todo
```

---

## Step 9: Deploy Backend Services via Helm

```bash
# Deploy backend microservices
helm install backend charts/todo-chatbot-backend \
  --namespace todo-app-dev \
  --values charts/todo-chatbot-backend/values-local.yaml \
  --wait \
  --timeout 5m

# Verify all pods are running
kubectl get pods -n todo-app-dev

# Expected output (all Running with Dapr sidecars):
# NAME                                      READY   STATUS    RESTARTS   AGE
# api-service-xxx                           2/2     Running   0          2m
# recurring-task-service-xxx                2/2     Running   0          2m
# notification-service-xxx                  2/2     Running   0          2m
# audit-service-xxx                         2/2     Running   0          2m
# websocket-sync-service-xxx                2/2     Running   0          2m

# Check Dapr sidecar injection
kubectl logs api-service-xxx -c daprd -n todo-app-dev | head -20
```

---

## Step 10: Deploy Frontend

```bash
# Deploy frontend
helm install frontend charts/todo-chatbot-frontend \
  --namespace todo-app-dev \
  --values charts/todo-chatbot-frontend/values-local.yaml \
  --wait \
  --timeout 3m

# Verify frontend pod
kubectl get pods -n todo-app-dev | grep frontend
```

---

## Step 11: Access the Application

### Option A: Port Forwarding (Quick)

```bash
# Forward frontend port
kubectl port-forward svc/frontend 3000:3000 -n todo-app-dev

# Open browser to http://localhost:3000
```

### Option B: Minikube Service (Automatic)

```bash
# Get service URL
minikube service frontend -n todo-app-dev --url

# Open the URL in browser
```

### Option C: Ingress (Production-like)

```bash
# Get Minikube IP
minikube ip

# Add to /etc/hosts (macOS/Linux) or C:\Windows\System32\drivers\etc\hosts (Windows)
# Example: 192.168.49.2 todo-app.local

# Access via http://todo-app.local
```

---

## Step 12: Test Event-Driven Features

### Test 1: Create Recurring Task

```bash
# Open frontend at http://localhost:3000
# Login with test credentials
# Create task with:
# - Title: "Weekly team meeting"
# - Recurrence: Every Monday
# - Due date: Next Monday 10:00 AM

# Verify task created
curl http://localhost:3000/api/tasks | jq '.[] | select(.title == "Weekly team meeting")'
```

### Test 2: Verify Kafka Event Published

```bash
# Check Kafka topic for task.created event
kubectl exec -it redpanda-0 -n todo-app-dev -- rpk topic consume task-events --num 1

# Expected output:
# {"event_id":"...","event_type":"task.created","task_id":1,...}
```

### Test 3: Verify Recurring Task Generation

```bash
# Complete the recurring task
curl -X PATCH http://localhost:3000/api/tasks/1 -d '{"status":"completed"}'

# Wait 5 seconds for Recurring Task Service to process

# Check for new occurrence
curl http://localhost:3000/api/tasks | jq '.[] | select(.parent_task_id == 1)'

# Should show new task with due_date = next Monday
```

### Test 4: Verify Reminder Scheduling

```bash
# Create task with reminder
curl -X POST http://localhost:3000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Important deadline",
    "due_date": "2026-01-03T14:00:00Z",
    "reminder_offset": "1 hour"
  }'

# Check Dapr Jobs API scheduled job
kubectl exec api-service-xxx -c daprd -n todo-app-dev -- curl http://localhost:3500/v1.0/jobs

# Should show scheduled job for 2026-01-03T13:00:00Z
```

### Test 5: Verify WebSocket Real-Time Sync

```bash
# Open two browser tabs at http://localhost:3000
# Login with same user in both tabs
# Create task in Tab 1
# Observe task appears immediately in Tab 2 (without refresh)
```

---

## Step 13: Monitor and Debug

### View Dapr Dashboard

```bash
# Start dashboard
dapr dashboard -k

# Open http://localhost:8080
# View pub/sub subscriptions, state stores, service invocations
```

### View Logs

```bash
# API Service logs
kubectl logs -f api-service-xxx -c api-service -n todo-app-dev

# Dapr sidecar logs
kubectl logs -f api-service-xxx -c daprd -n todo-app-dev

# Recurring Task Service logs
kubectl logs -f recurring-task-service-xxx -c recurring-task-service -n todo-app-dev

# All pods logs (follow)
kubectl logs -f --all-containers=true -l app=backend -n todo-app-dev
```

### Check Kafka Consumer Lag

```bash
# Exec into Redpanda pod
kubectl exec -it redpanda-0 -n todo-app-dev -- /bin/bash

# Check consumer groups
rpk group list

# Check lag for recurring-task-service
rpk group describe recurring-task-service
```

### View Prometheus Metrics

```bash
# Port-forward Prometheus (if deployed)
kubectl port-forward svc/prometheus 9090:9090 -n todo-app-dev

# Open http://localhost:9090
# Query: rate(http_requests_total[5m])
```

---

## Troubleshooting

### Problem: Pods stuck in Pending state

```bash
# Check pod description
kubectl describe pod <pod-name> -n todo-app-dev

# Common causes:
# - Insufficient resources: Increase Minikube memory/CPU
# - Image pull failure: Verify image loaded with `minikube image ls`
```

### Problem: Dapr sidecar not injected

```bash
# Verify annotation on deployment
kubectl get deployment api-service -n todo-app-dev -o yaml | grep dapr.io/enabled

# Should show: dapr.io/enabled: "true"

# If missing, update Helm chart and redeploy
```

### Problem: Kafka topics not created

```bash
# Check Strimzi operator logs
kubectl logs deployment/strimzi-cluster-operator -n todo-app-dev

# Manually create topic (alternative)
kubectl exec -it kafka-cluster-kafka-0 -n todo-app-dev -- \
  bin/kafka-topics.sh --create \
  --bootstrap-server localhost:9092 \
  --topic task-events \
  --partitions 6 \
  --replication-factor 1
```

### Problem: Database connection timeout

```bash
# Check secret exists
kubectl get secret database-credentials -n todo-app-dev -o yaml

# Verify connection string is correct
kubectl get secret database-credentials -n todo-app-dev -o jsonpath='{.data.connectionString}' | base64 --decode

# Test connection from pod
kubectl exec -it api-service-xxx -n todo-app-dev -- \
  python -c "import psycopg2; conn = psycopg2.connect('<connection-string>'); print('Connected!')"
```

---

## Clean Up

```bash
# Delete Helm releases
helm uninstall backend -n todo-app-dev
helm uninstall frontend -n todo-app-dev

# Delete Dapr components
kubectl delete components --all -n todo-app-dev

# Delete Kafka resources
kubectl delete -f kubernetes/kafka/local/ -n todo-app-dev

# Delete namespace
kubectl delete namespace todo-app-dev

# Stop Minikube
minikube stop

# (Optional) Delete Minikube cluster
minikube delete
```

---

## Next Steps

1. **Cloud Deployment**: Follow `docs/CLOUD_DEPLOYMENT.md` to deploy to AKS/GKE/OKE
2. **CI/CD Setup**: Configure GitHub Actions for automated deployments
3. **Observability**: Deploy Prometheus, Grafana, and Jaeger for monitoring
4. **Load Testing**: Run k6 scripts from `tests/load/` to validate performance

---

## Common Commands Reference

```bash
# Restart a deployment
kubectl rollout restart deployment/api-service -n todo-app-dev

# Scale a deployment
kubectl scale deployment/recurring-task-service --replicas=3 -n todo-app-dev

# Execute command in pod
kubectl exec -it api-service-xxx -n todo-app-dev -- /bin/bash

# View Dapr component logs
kubectl logs -f dapr-operator-xxx -n dapr-system

# Check Helm release status
helm status backend -n todo-app-dev

# Upgrade Helm release
helm upgrade backend charts/todo-chatbot-backend \
  --namespace todo-app-dev \
  --values charts/todo-chatbot-backend/values-local.yaml
```

---

**Estimated Total Setup Time**: 25-30 minutes (assuming no errors)
**Support**: See `docs/TROUBLESHOOTING.md` for additional help
