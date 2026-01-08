#!/bin/bash
# deploy-local.sh - Deploy Todo App to Minikube

set -e

echo "🚀 Deploying Todo App to Minikube..."

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Start Minikube with sufficient resources
echo -e "${YELLOW}📦 Checking Minikube...${NC}"
# Use existing Minikube instance if running, otherwise start with available memory
if minikube status | grep -q "Running"; then
  echo "Minikube already running, skipping start..."
else
  minikube start --cpus=4 --memory=6000 --disk-size=20g --driver=docker
fi

# 2. Enable addons
echo -e "${YELLOW}🔌 Enabling Minikube addons...${NC}"
minikube addons enable ingress
minikube addons enable metrics-server

# 3. Initialize Dapr
echo -e "${YELLOW}🔧 Installing Dapr...${NC}"
dapr init -k

# Wait for Dapr to be ready
echo "Waiting for Dapr operator to be ready..."
kubectl wait --for=condition=ready pod -l app=dapr-operator -n dapr-system --timeout=300s

echo -e "${GREEN}✓ Dapr installed successfully${NC}"

# 4. Install Kafka
echo -e "${YELLOW}☕ Installing Kafka (Strimzi)...${NC}"
helm repo add strimzi https://strimzi.io/charts/
helm repo update

kubectl create namespace kafka --dry-run=client -o yaml | kubectl apply -f -

helm upgrade --install kafka-operator strimzi/strimzi-kafka-operator \
  --namespace kafka \
  --set watchNamespaces="{default,kafka}" \
  --wait \
  --timeout=5m

echo "Waiting for Strimzi operator to be ready..."
kubectl wait --for=condition=ready pod -l name=strimzi-cluster-operator -n kafka --timeout=300s

# Deploy Kafka cluster
echo "Deploying Kafka cluster..."
kubectl apply -f phase-v/kubernetes/infrastructure/kafka-cluster.yaml

echo "Waiting for Kafka cluster to be ready (this may take 5-10 minutes)..."
kubectl wait kafka/kafka-cluster --for=condition=Ready --timeout=600s -n default

echo -e "${GREEN}✓ Kafka cluster deployed successfully${NC}"

# 5. Deploy PostgreSQL
echo -e "${YELLOW}🐘 Deploying PostgreSQL...${NC}"
kubectl apply -f phase-v/kubernetes/infrastructure/postgres.yaml

echo "Waiting for PostgreSQL to be ready..."
kubectl wait --for=condition=ready pod -l app=postgres --timeout=300s

echo -e "${GREEN}✓ PostgreSQL deployed successfully${NC}"

# 6. Create secrets
echo -e "${YELLOW}🔐 Creating secrets...${NC}"
kubectl apply -f phase-v/kubernetes/secrets/backend-secrets.yaml

echo -e "${GREEN}✓ Secrets created${NC}"

# 7. Deploy Dapr components
echo -e "${YELLOW}🎯 Deploying Dapr components...${NC}"
kubectl apply -f phase-v/dapr-components/local/

echo -e "${GREEN}✓ Dapr components deployed${NC}"

# 8. Build and load Docker images into Minikube
echo -e "${YELLOW}🐳 Building and loading Docker images...${NC}"
eval $(minikube docker-env)

echo "Building API Service..."
docker build -t api-service:latest ./backend/api-service

echo "Building Recurring Task Service..."
docker build -t recurring-task-service:latest ./phase-v/services/recurring-task-service

echo "Building Notification Service..."
docker build -t notification-service:latest ./phase-v/services/notification-service

echo "Building Audit Service..."
docker build -t audit-service:latest ./phase-v/services/audit-service

echo "Building WebSocket Sync Service..."
docker build -t websocket-sync-service:latest ./phase-v/services/websocket-sync-service

echo -e "${GREEN}✓ All images built and loaded into Minikube${NC}"

# 9. Deploy services
echo -e "${YELLOW}🚢 Deploying microservices...${NC}"
kubectl apply -f phase-v/kubernetes/deployments/

# Wait for all deployments
echo "Waiting for deployments to be ready..."

echo "  - API Service..."
kubectl wait --for=condition=available deployment/api-service --timeout=300s

echo "  - Recurring Task Service..."
kubectl wait --for=condition=available deployment/recurring-task-service --timeout=300s

echo "  - Notification Service..."
kubectl wait --for=condition=available deployment/notification-service --timeout=300s

echo "  - Audit Service..."
kubectl wait --for=condition=available deployment/audit-service --timeout=300s

echo "  - WebSocket Sync Service..."
kubectl wait --for=condition=available deployment/websocket-sync-service --timeout=300s

echo -e "${GREEN}✓ All services deployed successfully${NC}"

# 10. Deploy Ingress
echo -e "${YELLOW}🌐 Deploying Ingress...${NC}"
kubectl apply -f phase-v/kubernetes/ingress.yaml

echo -e "${GREEN}✓ Ingress deployed${NC}"

# 11. Get service URLs
echo ""
echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""
echo "📊 Service Information:"
echo "================================"

INGRESS_IP=$(minikube ip)
echo "Ingress IP: $INGRESS_IP"
echo ""
echo "Add these to your /etc/hosts (or C:\Windows\System32\drivers\etc\hosts on Windows):"
echo "$INGRESS_IP api.yourdomain.com"
echo "$INGRESS_IP ws.yourdomain.com"
echo "$INGRESS_IP audit.yourdomain.com"
echo ""
echo "Service URLs:"
echo "  - API Service: http://api.yourdomain.com"
echo "  - WebSocket Service: ws://ws.yourdomain.com/ws"
echo "  - Audit Service: http://audit.yourdomain.com"
echo ""
echo "Or use NodePort access:"
API_PORT=$(kubectl get svc api-service -o jsonpath='{.spec.ports[0].nodePort}' 2>/dev/null || echo "N/A")
if [ "$API_PORT" != "N/A" ]; then
  echo "  - API Service: http://$INGRESS_IP:$API_PORT"
fi
echo ""
echo "🔍 Useful commands:"
echo "  kubectl get pods                              # View all pods"
echo "  kubectl get svc                               # View all services"
echo "  kubectl logs -f deployment/api-service -c api-service    # View API logs"
echo "  kubectl logs -f deployment/api-service -c daprd          # View Dapr sidecar logs"
echo "  minikube dashboard                            # Open Kubernetes dashboard"
echo "  kubectl port-forward svc/api-service 8000:8000           # Port-forward API"
echo ""
echo "🧪 Test the deployment:"
echo "  kubectl port-forward svc/api-service 8000:8000"
echo "  curl http://localhost:8000/health"
echo ""
echo -e "${GREEN}Happy coding! 🎉${NC}"
