#!/bin/bash

##############################################################################
# Phase V: Cloud Kubernetes Deployment Script (Comprehensive)
#
# This script automates the deployment of the Todo AI Chatbot to a cloud
# Kubernetes cluster using Helm
#
# Prerequisites:
# - Kubernetes cluster created and kubectl configured
# - Dapr CLI installed
# - Helm 3.10+ installed
# - Docker images built and pushed to registry
#
# Usage: ./deploy-cloud-comprehensive.sh [namespace] [registry] [version]
#
# Example:
#   ./deploy-cloud-comprehensive.sh todo-app-prod docker.io/myusername 1.0.0
##############################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
NAMESPACE=${1:-todo-app-prod}
REGISTRY=${2:-docker.io/yourusername}
VERSION=${3:-1.0.0}
CHART_PATH="./charts/todo-chatbot-backend"
VALUES_FILE="values-cloud.yaml"

# Functions
print_header() { echo -e "${BLUE}========================================\n$1\n========================================${NC}"; }
print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_error() { echo -e "${RED}✗ $1${NC}"; exit 1; }
print_warning() { echo -e "${YELLOW}⚠ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ $1${NC}"; }

check_command() {
    if ! command -v $1 &> /dev/null; then
        print_error "$1 is not installed"
    fi
}

# Pre-flight checks
print_header "Pre-flight Checks"
check_command kubectl
check_command helm
check_command dapr

if ! kubectl cluster-info &> /dev/null; then
    print_error "Cannot connect to Kubernetes cluster"
fi
print_success "Connected to cluster: $(kubectl config current-context)"

# Install Dapr
print_header "Installing Dapr"
if kubectl get namespace dapr-system &> /dev/null; then
    print_warning "Dapr already installed"
else
    dapr init -k --enable-mtls=true --enable-ha=true --wait --timeout 600
    print_success "Dapr installed"
fi

# Create namespace
print_header "Creating Namespace"
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -
kubectl label namespace $NAMESPACE dapr.io/enabled=true --overwrite
print_success "Namespace $NAMESPACE ready"

# Deploy with Helm
print_header "Deploying with Helm"
print_info "Registry: $REGISTRY"
print_info "Version: $VERSION"

# Update values file with registry
TEMP_VALUES="/tmp/values-cloud-updated.yaml"
sed "s|docker.io/yourusername|$REGISTRY|g" "$CHART_PATH/$VALUES_FILE" > "$TEMP_VALUES"
sed -i "s|tag: \"1.0.0\"|tag: \"$VERSION\"|g" "$TEMP_VALUES"

helm upgrade --install todo-app-backend \
    "$CHART_PATH" \
    --namespace "$NAMESPACE" \
    --values "$TEMP_VALUES" \
    --wait \
    --timeout 10m \
    --create-namespace

rm -f "$TEMP_VALUES"
print_success "Helm deployment complete"

# Verify
print_header "Verifying Deployment"
kubectl get pods -n $NAMESPACE
kubectl get svc -n $NAMESPACE
print_success "Deployment complete!"

print_info "Access via:"
print_info "  kubectl port-forward -n $NAMESPACE svc/api-service 8000:8000"
