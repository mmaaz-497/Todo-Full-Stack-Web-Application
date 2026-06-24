# Minikube Deployment Guide

This document provides instructions for deploying the TaskFlow application to a local Minikube cluster with Kafka and Dapr integration.

## Prerequisites

- Minikube installed
- kubectl installed
- Docker installed
- 8GB RAM minimum
- 20GB disk space
- Dapr CLI installed

## Quick Start

### 1. Start Minikube

```bash
minikube start --cpus=4 --memory=8192 --disk-size=20g --driver=docker
```

### 2. Install Dapr

```bash
# Initialize Dapr on Kubernetes
dapr init -k

# Verify Dapr installation
dapr status -k
```

### 3. Create Kafka Namespace and Install Strimzi

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
```

### 4. Deploy Kafka Cluster

```bash
# Apply Kafka cluster configuration
kubectl apply -f k8s/kafka/kafka-cluster.yaml -n kafka

# Wait for cluster to be ready (this takes 2-5 minutes)
kubectl wait kafka/taskflow-kafka --for=condition=Ready --timeout=600s -n kafka

# Verify all pods are running
kubectl get pods -n kafka
```

### 5. Create Kafka Topics

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
```

### 6. Deploy Dapr Components

```bash
# Apply all Dapr components
kubectl apply -f k8s/dapr-components/ -n default

# Verify components are created
kubectl get components -n default
```

### 7. Create Kubernetes Secrets

```bash
# Create database secret
kubectl create secret generic db-secrets \
  --from-literal=connection-string="postgresql://user:password@hostname/database?sslmode=require" \
  -n default

# Create API secrets
kubectl create secret generic api-secrets \
  --from-literal=openai-api-key="sk-..." \
  -n default

# Create email secrets
kubectl create secret generic email-secrets \
  --from-literal=smtp-host="smtp.gmail.com" \
  --from-literal=smtp-port="587" \
  --from-literal=smtp-user="your-email@gmail.com" \
  --from-literal=smtp-password="your-app-password" \
  --from-literal=smtp-from="noreply@taskflow.com" \
  -n default
```

### 8. Build Docker Images

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
```

### 9. Load Images into Minikube

```bash
# Load all images into Minikube
minikube image load taskflow-backend:latest
minikube image load taskflow-frontend:latest
minikube image load recurring-task-service:latest
minikube image load notification-service:latest
minikube image load audit-service:latest
```

### 10. Deploy Application

```bash
# Apply all deployments
kubectl apply -f k8s/deployments/ -n default

# Wait for all pods to be ready
kubectl wait --for=condition=ready pod \
  --all \
  -n default \
  --timeout=300s

# Check pod status
kubectl get pods -n default
```

### 11. Access the Application

```bash
# Get frontend service URL
minikube service frontend-service --url

# Or access via tunnel
minikube tunnel
# Then access the LoadBalancer IP
```

## Architecture

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                         KUBERNETES CLUSTER (Minikube)                           │
│                                                                                  │
│  ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐               │
│  │  Frontend Pod   │   │  Backend Pod    │   │ Notification Pod│               │
│  │  ┌───────────┐  │   │  ┌───────────┐  │   │  ┌───────────┐  │               │
│  │  │ Next.js   │  │   │  │ FastAPI   │  │   │  │ Notif     │  │               │
│  │  │ + Chat UI │  │   │  │ + MCP     │  │   │  │ Service   │  │               │
│  │  └─────┬─────┘  │   │  └─────┬─────┘  │   │  └─────┬─────┘  │               │
│  │  ┌─────▼─────┐  │   │  ┌─────▼─────┐  │   │  ┌─────▼─────┐  │               │
│  │  │   Dapr    │  │   │  │   Dapr    │  │   │  │   Dapr    │  │               │
│  │  │  Sidecar  │  │   │  │  Sidecar  │  │   │  │  Sidecar  │  │               │
│  │  └───────────┘  │   │  └───────────┘  │   │  └───────────┘  │               │
│  └─────────────────┘   └─────────────────┘   └─────────────────┘               │
│                                                                                  │
│  ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐               │
│  │ Recurring Task  │   │  Audit Service  │   │  WebSocket      │               │
│  │    Service      │   │                 │   │  Service        │               │
│  │  ┌───────────┐  │   │  ┌───────────┐  │   │  ┌───────────┐  │               │
│  │  │ Consumer  │  │   │  │ Consumer  │  │   │  │ Consumer  │  │               │
│  │  └─────┬─────┘  │   │  └─────┬─────┘  │   │  └─────┬─────┘  │               │
│  │  ┌─────▼─────┐  │   │  ┌─────▼─────┐  │   │  ┌─────▼─────┐  │               │
│  │  │   Dapr    │  │   │  │   Dapr    │  │   │  │   Dapr    │  │               │
│  │  └───────────┘  │   │  └───────────┘  │   │  └───────────┘  │               │
│  └─────────────────┘   └─────────────────┘   └─────────────────┘               │
│                                                                                  │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │                        DAPR COMPONENTS                                   │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐         │   │
│  │  │ pubsub.kafka    │  │ state.postgres  │  │ secretstore.k8s │         │   │
│  │  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘         │   │
│  └───────────┼────────────────────┼────────────────────┼──────────────────┘   │
│              │                    │                    │                       │
└──────────────┼────────────────────┼────────────────────┼───────────────────────┘
               │                    │                    │
               ▼                    ▼                    ▼
      ┌────────────────┐   ┌────────────────┐   ┌────────────────┐
      │ KAFKA CLUSTER  │   │   POSTGRES DB  │   │  K8S SECRETS   │
      │   (Strimzi)    │   │  (Neon/Local)  │   │                │
      └────────────────┘   └────────────────┘   └────────────────┘
```

## Troubleshooting

### Common Issues:

1. **Pods stuck in Pending:**
   - Check node resources: `kubectl describe nodes`
   - Increase Minikube resources: `minikube stop && minikube start --memory=8192`

2. **ImagePullBackOff:**
   - Verify images are loaded: `minikube ssh` and `docker images`
   - Check imagePullPolicy is set to Never for local images

3. **CrashLoopBackOff:**
   - Check pod logs: `kubectl logs <pod-name> -c <container-name>`
   - Verify secrets are created properly

4. **Kafka connection errors:**
   - Verify Kafka cluster is ready: `kubectl get kafka -n kafka`
   - Check Kafka pod logs: `kubectl logs taskflow-kafka-kafka-0 -n kafka`

5. **Dapr sidecar not injecting:**
   - Check Dapr status: `dapr status -k`
   - Verify annotations in deployment YAML

### Useful Commands:

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

# Check Dapr logs
dapr logs --app-id backend-service -k

# Check Kafka topics
kubectl exec -it taskflow-kafka-kafka-0 -n kafka -- \
  bin/kafka-topics.sh --list --bootstrap-server localhost:9092
```

## Testing

### 1. Basic Connectivity
- Access frontend via Minikube URL
- Verify backend health: `curl <backend-url>/health`

### 2. Task Operations
- Create a task via chatbot
- Verify task appears in UI
- Update task status

### 3. Kafka Events
- Check events are flowing to Kafka:
```bash
kubectl exec -it taskflow-kafka-kafka-0 -n kafka -- \
  bin/kafka-console-consumer.sh \
  --topic task-events \
  --from-beginning \
  --bootstrap-server localhost:9092 \
  --max-messages 5
```

### 4. Consumer Services
- Complete a task
- Verify recurring task service processes completion
- Check notification service receives events

## Cleanup

To remove all resources:

```bash
# Delete all deployments
kubectl delete all --all -n default

# Delete Dapr components
kubectl delete components --all -n default

# Delete Kafka topics and cluster
kubectl delete -f k8s/kafka/topics.yaml -n kafka
kubectl delete -f k8s/kafka/kafka-cluster.yaml -n kafka

# Uninstall Strimzi operator
kubectl delete -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka

# Delete namespaces
kubectl delete namespace kafka default

# Stop Minikube
minikube stop
```

## Next Steps

Once the local deployment is working, you can proceed to deploy to cloud infrastructure (see [CLOUD_DEPLOYMENT.md](CLOUD_DEPLOYMENT.md)).