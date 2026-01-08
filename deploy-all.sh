#!/bin/bash
set -e

echo "=== Phase V Full Deployment ==="

# Step 1: Build all Docker images
echo "Building Docker images..."
eval $(minikube docker-env)

cd backend/api-service && docker build -t api-service:latest . && cd ../..
cd backend/recurring-task-service && docker build -t recurring-task-service:latest . && cd ../..
cd backend/notification-service && docker build -t notification-service:latest . && cd ../..
cd backend/audit-service && docker build -t audit-service:latest . && cd ../..
cd backend/websocket-sync-service && docker build -t websocket-sync-service:latest . && cd ../..

echo "All images built successfully"

# Step 2: Deploy infrastructure
echo "Deploying PostgreSQL..."
kubectl apply -f phase-v/kubernetes/infrastructure/postgres.yaml
kubectl wait --for=condition=ready pod -l app=postgres --timeout=120s

echo "Deploying Kafka..."
kubectl apply -f phase-v/kubernetes/infrastructure/kafka-cluster-kraft.yaml -n kafka
kubectl wait kafka/kafka-cluster --for=condition=Ready --timeout=600s -n kafka

# Step 3: Create secrets
echo "Creating secrets..."
kubectl apply -f phase-v/kubernetes/secrets/backend-secrets.yaml

# Step 4: Apply Dapr components
echo "Applying Dapr components..."
kubectl apply -f phase-v/dapr-components/local/

# Step 5: Disable Dapr mTLS
echo "Disabling Dapr mTLS..."
kubectl patch configuration daprsystem -n dapr-system --type merge -p '{"spec":{"mtls":{"enabled":false,"sentryAddress":""}}}'
kubectl scale deployment dapr-sentry -n dapr-system --replicas=0

# Step 6: Deploy all microservices
echo "Deploying microservices..."
kubectl apply -f phase-v/kubernetes/deployments/

echo "Waiting for pods to start..."
sleep 60

# Step 7: Check status
echo "=== Deployment Status ==="
kubectl get pods
kubectl get deployments

echo "=== Done ==="
