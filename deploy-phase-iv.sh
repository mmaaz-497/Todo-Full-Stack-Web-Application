#!/bin/bash
# Phase IV Kubernetes Deployment Script for WSL Ubuntu
# Run this after Docker Desktop is running

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================"
echo "  Phase IV Kubernetes Deployment"
echo "======================================${NC}"
echo ""

# Step 1: Verify prerequisites
echo -e "${YELLOW}Step 1: Verifying prerequisites...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found. Make sure Docker Desktop is running with WSL2 integration.${NC}"
    exit 1
fi

if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}❌ kubectl not found. Installing...${NC}"
    curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
    sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
    rm kubectl
fi

if ! command -v minikube &> /dev/null; then
    echo -e "${RED}❌ Minikube not found. Installing...${NC}"
    curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
    sudo install minikube-linux-amd64 /usr/local/bin/minikube
    rm minikube-linux-amd64
fi

if ! command -v helm &> /dev/null; then
    echo -e "${RED}❌ Helm not found. Installing...${NC}"
    curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
fi

echo -e "${GREEN}✅ All prerequisites installed${NC}"
echo ""

# Step 2: Start Minikube
echo -e "${YELLOW}Step 2: Starting Minikube cluster...${NC}"
minikube status &> /dev/null || minikube start --cpus=2 --memory=4096 --driver=docker
echo -e "${GREEN}✅ Minikube running${NC}"
echo ""

# Step 3: Build auth service
echo -e "${YELLOW}Step 3: Building auth service Docker image...${NC}"
cd backend/auth-service
docker build --target prod -t todo-chatbot-auth:v1.0.0 . || {
    echo -e "${RED}❌ Failed to build auth service${NC}"
    exit 1
}
cd ../..
echo -e "${GREEN}✅ Auth service built${NC}"
echo ""

# Step 4: Load images into Minikube
echo -e "${YELLOW}Step 4: Loading images into Minikube (this may take 3-4 minutes)...${NC}"
minikube image load todo-chatbot-frontend:v1.0.0 &
minikube image load todo-chatbot-api:v1.0.0 &
minikube image load todo-chatbot-reminder:v1.0.0 &
minikube image load todo-chatbot-auth:v1.0.0 &
wait
echo -e "${GREEN}✅ All images loaded${NC}"
echo ""

# Step 5: Deploy/upgrade backend
echo -e "${YELLOW}Step 5: Deploying backend services...${NC}"
helm upgrade backend charts/todo-chatbot-backend \
  --install \
  --namespace todo-app \
  --create-namespace \
  --set secrets.databaseUrl="${DATABASE_URL}" \
  --set secrets.authSecret="${AUTH_SECRET}" \
  --set secrets.geminiApiKey="${GOOGLE_API_KEY}" \
  --set secrets.openaiApiKey="${OPENAI_API_KEY}" \
  --set secrets.smtpUser="${SMTP_USERNAME}" \
  --set secrets.smtpPassword="${SMTP_PASSWORD}"

echo -e "${GREEN}✅ Backend deployed${NC}"
echo ""

# Step 6: Deploy/upgrade frontend (if not already deployed)
echo -e "${YELLOW}Step 6: Checking frontend deployment...${NC}"
if ! helm status frontend -n todo-app &> /dev/null; then
    echo "Frontend not deployed yet. Deploying..."
    helm install frontend charts/todo-chatbot-frontend --namespace todo-app
fi
echo -e "${GREEN}✅ Frontend ready${NC}"
echo ""

# Step 7: Wait for pods
echo -e "${YELLOW}Step 7: Waiting for pods to start...${NC}"
echo "This may take 1-2 minutes..."
sleep 20

# Check pod status
kubectl get pods -n todo-app

# Wait for all pods to be ready
echo ""
echo "Waiting for all pods to be ready..."
kubectl wait --for=condition=Ready pod --all -n todo-app --timeout=120s || {
    echo -e "${RED}⚠️  Some pods are not ready yet. Check logs below:${NC}"
    kubectl get pods -n todo-app
}

echo ""
echo -e "${GREEN}✅ Pods are running${NC}"
echo ""

# Step 8: Display access information
echo -e "${BLUE}======================================"
echo "  Deployment Complete!"
echo "======================================${NC}"
echo ""

MINIKUBE_IP=$(minikube ip)

echo -e "${GREEN}🌍 Access URLs:${NC}"
echo "   Frontend: http://$MINIKUBE_IP:30080"
echo "   API Health: http://$MINIKUBE_IP:30081/health"
echo ""

echo -e "${BLUE}📊 Current Status:${NC}"
kubectl get pods -n todo-app
echo ""

echo -e "${BLUE}🔍 Services:${NC}"
kubectl get svc -n todo-app
echo ""

echo -e "${YELLOW}Testing API health endpoint...${NC}"
if curl -s http://$MINIKUBE_IP:30081/health > /dev/null; then
    echo -e "${GREEN}✅ API is responding!${NC}"
else
    echo -e "${RED}⚠️  API not responding yet. Check logs:${NC}"
    echo "   kubectl logs deployment/api-service-deployment -n todo-app --tail=50"
fi

echo ""
echo -e "${GREEN}🎉 Phase IV deployment complete!${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "1. Open http://$MINIKUBE_IP:30080 in your browser"
echo "2. Test user registration and login"
echo "3. Create some todos"
echo "4. Test the AI chatbot"
echo ""
echo -e "${YELLOW}Useful commands:${NC}"
echo "  View logs: kubectl logs deployment/api-service-deployment -n todo-app"
echo "  Check status: kubectl get pods -n todo-app"
echo "  Restart pods: kubectl rollout restart deployment -n todo-app"
echo "  Stop cluster: minikube stop"
echo ""
