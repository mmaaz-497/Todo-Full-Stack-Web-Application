#!/bin/bash

##############################################################################
# Phase V: Cloud Kubernetes Deployment Script
#
# This script automates the deployment of the Todo AI Chatbot to a cloud
# Kubernetes cluster (AKS, GKE, or OKE)
#
# Prerequisites:
# - Kubernetes cluster already created and kubectl configured
# - Dapr CLI installed
# - Helm 3.10+ installed
# - Docker images built and pushed to registry
# - Secrets prepared (see docs/CLOUD_DEPLOYMENT.md)
#
# Usage:
#   ./deploy-cloud.sh [namespace] [registry] [version]
#
# Example:
#   ./deploy-cloud.sh todo-app-prod docker.io/yourusername 1.0.0
##############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE=${1:-todo-app-prod}
REGISTRY=${2:-docker.io/yourusername}
VERSION=${3:-1.0.0}
CHART_PATH="./charts/todo-chatbot-backend"
VALUES_FILE="values-cloud.yaml"

# Timeouts
DAPR_TIMEOUT=600
ROLLOUT_TIMEOUT=300

##############################################################################
# Helper Functions
##############################################################################

print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

check_command() {
    if ! command -v $1 &> /dev/null; then
        print_error "$1 is not installed. Please install it first."
        exit 1
    fi
}

wait_for_pods() {
    local namespace=$1
    local label=$2
    local timeout=${3:-120}

    print_info "Waiting for pods with label $label to be ready..."
    kubectl wait --for=condition=Ready pod \
        -l "$label" \
        -n "$namespace" \
        --timeout="${timeout}s" || true
}

##############################################################################
# Pre-flight Checks
##############################################################################

preflight_checks() {
    print_header "Pre-flight Checks"

    # Check required commands
    check_command kubectl
    check_command helm
    check_command dapr

    # Check kubectl connection
    if ! kubectl cluster-info &> /dev/null; then
        print_error "Cannot connect to Kubernetes cluster"
        print_info "Please configure kubectl to point to your cluster"
        exit 1
    fi
    print_success "kubectl connected to cluster"

    # Display cluster info
    CLUSTER_NAME=$(kubectl config current-context)
    print_info "Current cluster: $CLUSTER_NAME"

    # Check nodes
    NODE_COUNT=$(kubectl get nodes --no-headers | wc -l)
    print_info "Cluster nodes: $NODE_COUNT"

    if [ "$NODE_COUNT" -lt 3 ]; then
        print_warning "Less than 3 nodes detected. Production requires at least 3 nodes."
    fi

    # Check Helm chart exists
    if [ ! -d "$CHART_PATH" ]; then
        print_error "Helm chart not found at $CHART_PATH"
        exit 1
    fi
    print_success "Helm chart found"

    # Check values file exists
    if [ ! -f "$CHART_PATH/$VALUES_FILE" ]; then
        print_error "Values file not found: $CHART_PATH/$VALUES_FILE"
        exit 1
    fi
    print_success "Values file found"

    echo ""
}

# 1. Create namespace if it doesn't exist
echo -e "${YELLOW}📦 Creating namespace...${NC}"
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# 2. Install Dapr
echo -e "${YELLOW}🔧 Installing Dapr...${NC}"
dapr init -k --wait --timeout 300

echo -e "${GREEN}✓ Dapr installed${NC}"

# 3. Build and push Docker images
echo -e "${YELLOW}🐳 Building and pushing Docker images...${NC}"

# Function to build and push image
build_and_push() {
  local service=$1
  local context=$2
  local image_name="$REGISTRY/$service:$IMAGE_TAG"

  echo "Building $service..."
  docker build -t $image_name $context

  echo "Pushing $service..."
  docker push $image_name

  echo -e "${GREEN}✓ $service pushed to registry${NC}"
}

# Build and push all services
build_and_push "api-service" "./backend/api-service"
build_and_push "recurring-task-service" "./phase-v/services/recurring-task-service"
build_and_push "notification-service" "./phase-v/services/notification-service"
build_and_push "audit-service" "./phase-v/services/audit-service"
build_and_push "websocket-sync-service" "./phase-v/services/websocket-sync-service"

# 4. Update deployment YAMLs with registry path
echo -e "${YELLOW}📝 Updating deployment manifests with registry...${NC}"

# Temporary directory for modified manifests
TEMP_DIR="./phase-v/kubernetes/temp"
mkdir -p $TEMP_DIR

# Copy and update manifests
for yaml in phase-v/kubernetes/deployments/*.yaml; do
  filename=$(basename $yaml)
  sed "s|your-registry/|$REGISTRY/|g" $yaml | \
  sed "s|:latest|:$IMAGE_TAG|g" > "$TEMP_DIR/$filename"
done

echo -e "${GREEN}✓ Manifests updated${NC}"

# 5. Deploy infrastructure
echo -e "${YELLOW}🏗️  Deploying infrastructure...${NC}"

# For cloud, we use managed services or cloud-specific configurations
case $CLOUD_PROVIDER in
  aks)
    echo "Using Azure-managed PostgreSQL and Redpanda Cloud for Kafka..."
    # Note: You should provision these separately and update connection strings
    ;;
  gke)
    echo "Using Google Cloud SQL for PostgreSQL and Redpanda Cloud for Kafka..."
    ;;
  oke)
    echo "Using Oracle Autonomous Database for PostgreSQL and Redpanda Cloud for Kafka..."
    ;;
esac

# If deploying PostgreSQL in-cluster (not recommended for production)
if [ "${DEPLOY_POSTGRES_IN_CLUSTER:-false}" = "true" ]; then
  echo "Deploying PostgreSQL in cluster..."
  kubectl apply -f phase-v/kubernetes/infrastructure/postgres.yaml -n $NAMESPACE
  kubectl wait --for=condition=ready pod -l app=postgres -n $NAMESPACE --timeout=300s
fi

echo -e "${GREEN}✓ Infrastructure ready${NC}"

# 6. Create secrets
echo -e "${YELLOW}🔐 Creating secrets...${NC}"

# Check if secrets file exists and has been customized
if grep -q "your-secure-password-change-in-production" phase-v/kubernetes/secrets/backend-secrets.yaml; then
  echo -e "${RED}⚠️  WARNING: Please update phase-v/kubernetes/secrets/backend-secrets.yaml with production values!${NC}"
  echo "Press Enter to continue or Ctrl+C to abort..."
  read
fi

kubectl apply -f phase-v/kubernetes/secrets/backend-secrets.yaml -n $NAMESPACE

# Apply Kafka secrets for cloud (if using Redpanda Cloud)
if [ -f "phase-v/kubernetes/secrets/kafka-secrets.yaml" ]; then
  kubectl apply -f phase-v/kubernetes/secrets/kafka-secrets.yaml -n $NAMESPACE
fi

echo -e "${GREEN}✓ Secrets created${NC}"

# 7. Deploy Dapr components
echo -e "${YELLOW}🎯 Deploying Dapr components...${NC}"

# Use cloud components (with Redpanda Cloud)
kubectl apply -f phase-v/dapr-components/cloud/ -n $NAMESPACE

echo -e "${GREEN}✓ Dapr components deployed${NC}"

# 8. Deploy services
echo -e "${YELLOW}🚢 Deploying microservices...${NC}"

kubectl apply -f $TEMP_DIR/ -n $NAMESPACE

# Wait for deployments
echo "Waiting for deployments to be ready..."

deployments=("api-service" "recurring-task-service" "notification-service" "audit-service" "websocket-sync-service")

for deployment in "${deployments[@]}"; do
  echo "  - Waiting for $deployment..."
  kubectl wait --for=condition=available deployment/$deployment -n $NAMESPACE --timeout=300s || {
    echo -e "${RED}Failed to deploy $deployment${NC}"
    kubectl logs -n $NAMESPACE deployment/$deployment -c $deployment --tail=50 || true
    exit 1
  }
done

echo -e "${GREEN}✓ All services deployed${NC}"

# 9. Deploy Ingress
echo -e "${YELLOW}🌐 Deploying Ingress...${NC}"

# Update ingress with your domain
INGRESS_TEMP="$TEMP_DIR/ingress.yaml"
cp phase-v/kubernetes/ingress.yaml $INGRESS_TEMP

# Prompt for domain (or use environment variable)
if [ -z "$DOMAIN" ]; then
  echo "Enter your domain (e.g., example.com):"
  read DOMAIN
fi

sed -i.bak "s/yourdomain.com/$DOMAIN/g" $INGRESS_TEMP

kubectl apply -f $INGRESS_TEMP -n $NAMESPACE

echo -e "${GREEN}✓ Ingress deployed${NC}"

# 10. Get external IP
echo ""
echo -e "${YELLOW}⏳ Waiting for external IP...${NC}"

# Wait for ingress to get an IP
for i in {1..30}; do
  EXTERNAL_IP=$(kubectl get ingress todo-app-ingress -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "")
  if [ -n "$EXTERNAL_IP" ]; then
    break
  fi
  echo "Waiting... ($i/30)"
  sleep 10
done

# Cleanup temp directory
rm -rf $TEMP_DIR

echo ""
echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""
echo "📊 Deployment Summary:"
echo "================================"
echo "Cluster: $(kubectl config current-context)"
echo "Namespace: $NAMESPACE"
echo "External IP: ${EXTERNAL_IP:-Pending}"
echo ""
echo "🌐 Configure DNS:"
if [ -n "$EXTERNAL_IP" ]; then
  echo "Add these A records to your DNS:"
  echo "  api.$DOMAIN  -> $EXTERNAL_IP"
  echo "  ws.$DOMAIN   -> $EXTERNAL_IP"
  echo "  audit.$DOMAIN -> $EXTERNAL_IP"
else
  echo "  Run: kubectl get ingress todo-app-ingress -n $NAMESPACE"
  echo "  to get the external IP once assigned"
fi
echo ""
echo "🔗 Service URLs:"
echo "  API: https://api.$DOMAIN"
echo "  WebSocket: wss://ws.$DOMAIN/ws"
echo "  Audit: https://audit.$DOMAIN"
echo ""
echo "🔍 Useful commands:"
echo "  kubectl get pods -n $NAMESPACE"
echo "  kubectl get svc -n $NAMESPACE"
echo "  kubectl logs -f deployment/api-service -c api-service -n $NAMESPACE"
echo "  kubectl describe ingress todo-app-ingress -n $NAMESPACE"
echo ""
echo -e "${GREEN}🎉 Happy deploying!${NC}"
