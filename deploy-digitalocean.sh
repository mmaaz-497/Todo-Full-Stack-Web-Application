#!/bin/bash
set -e

# ============================================
# DigitalOcean Deployment Script
# Todo AI Chatbot - Phase V
# ============================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}DigitalOcean Deployment Script${NC}"
echo -e "${GREEN}Todo AI Chatbot - Phase V${NC}"
echo -e "${GREEN}=========================================${NC}"

# ============================================
# Configuration Variables
# ============================================

# Required: Set these before running
CLUSTER_NAME="${CLUSTER_NAME:-todo-app-cluster}"
REGION="${REGION:-nyc1}"
NODE_SIZE="${NODE_SIZE:-s-2vcpu-4gb}"
NODE_COUNT="${NODE_COUNT:-3}"

# Optional: External Services (leave empty to use in-cluster)
DO_DB_ID="${DO_DB_ID:-}"  # DigitalOcean Managed PostgreSQL Database ID
KAFKA_BOOTSTRAP_SERVERS="${KAFKA_BOOTSTRAP_SERVERS:-}"  # External Kafka (Confluent/Redpanda Cloud)

# Domain Configuration
DOMAIN="${DOMAIN:-}"  # e.g., todo.example.com

# Container Registry
DO_REGISTRY="${DO_REGISTRY:-registry.digitalocean.com/todo-app}"

# ============================================
# Prerequisite Check
# ============================================

echo -e "\n${YELLOW}Checking prerequisites...${NC}"

# Check if doctl is installed
if ! command -v doctl &> /dev/null; then
    echo -e "${RED}Error: doctl CLI not found${NC}"
    echo "Install: https://docs.digitalocean.com/reference/doctl/how-to/install/"
    exit 1
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}Error: kubectl not found${NC}"
    echo "Install: https://kubernetes.io/docs/tasks/tools/"
    exit 1
fi

# Check if helm is installed
if ! command -v helm &> /dev/null; then
    echo -e "${RED}Error: helm not found${NC}"
    echo "Install: https://helm.sh/docs/intro/install/"
    exit 1
fi

# Check doctl authentication
if ! doctl account get &> /dev/null; then
    echo -e "${RED}Error: doctl not authenticated${NC}"
    echo "Run: doctl auth init"
    exit 1
fi

echo -e "${GREEN}✓ All prerequisites met${NC}"

# ============================================
# Step 1: Create DigitalOcean Kubernetes Cluster
# ============================================

echo -e "\n${YELLOW}Step 1: Creating DOKS cluster...${NC}"

# Check if cluster already exists
if doctl kubernetes cluster get "$CLUSTER_NAME" &> /dev/null; then
    echo -e "${GREEN}✓ Cluster '$CLUSTER_NAME' already exists${NC}"
else
    echo "Creating new cluster: $CLUSTER_NAME in region $REGION"
    doctl kubernetes cluster create "$CLUSTER_NAME" \
        --region "$REGION" \
        --node-pool "name=worker-pool;size=$NODE_SIZE;count=$NODE_COUNT;auto-scale=true;min-nodes=2;max-nodes=5" \
        --wait \
        --update-kubeconfig \
        --set-current-context

    echo -e "${GREEN}✓ Cluster created successfully${NC}"
fi

# Get kubeconfig
doctl kubernetes cluster kubeconfig save "$CLUSTER_NAME"
kubectl config use-context "do-$REGION-$CLUSTER_NAME"

echo -e "${GREEN}✓ Connected to cluster${NC}"

# ============================================
# Step 2: Create DigitalOcean Container Registry
# ============================================

echo -e "\n${YELLOW}Step 2: Setting up Container Registry...${NC}"

REGISTRY_NAME="todo-app"

# Check if registry exists
if doctl registry get &> /dev/null; then
    echo -e "${GREEN}✓ Container registry already exists${NC}"
else
    echo "Creating container registry: $REGISTRY_NAME"
    doctl registry create "$REGISTRY_NAME" --subscription-tier basic
    echo -e "${GREEN}✓ Registry created${NC}"
fi

# Authenticate Docker with registry
doctl registry login

# Integrate registry with Kubernetes cluster
doctl kubernetes cluster registry add "$CLUSTER_NAME"

echo -e "${GREEN}✓ Registry configured${NC}"

# ============================================
# Step 3: Build and Push Docker Images
# ============================================

echo -e "\n${YELLOW}Step 3: Building and pushing Docker images...${NC}"

SERVICES=("api-service" "recurring-task-service" "notification-service" "audit-service" "websocket-sync-service")

for SERVICE in "${SERVICES[@]}"; do
    echo "Building $SERVICE..."
    cd "backend/$SERVICE"

    # Build image
    docker build -t "$DO_REGISTRY/$SERVICE:latest" .
    docker build -t "$DO_REGISTRY/$SERVICE:$(git rev-parse --short HEAD 2>/dev/null || echo 'v1.0.0')" .

    # Push to registry
    docker push "$DO_REGISTRY/$SERVICE:latest"
    docker push "$DO_REGISTRY/$SERVICE:$(git rev-parse --short HEAD 2>/dev/null || echo 'v1.0.0')"

    cd ../..
    echo -e "${GREEN}✓ $SERVICE pushed to registry${NC}"
done

# ============================================
# Step 4: Setup External Services (Optional)
# ============================================

echo -e "\n${YELLOW}Step 4: Configuring external services...${NC}"

# PostgreSQL Database
if [ -n "$DO_DB_ID" ]; then
    echo "Using DigitalOcean Managed Database: $DO_DB_ID"

    # Get database connection details
    DB_HOST=$(doctl databases get "$DO_DB_ID" --format Host --no-header)
    DB_PORT=$(doctl databases get "$DO_DB_ID" --format Port --no-header)
    DB_USER=$(doctl databases get "$DO_DB_ID" --format User --no-header)
    DB_NAME=$(doctl databases get "$DO_DB_ID" --format Database --no-header)

    echo "Please manually retrieve DB_PASSWORD from DigitalOcean console"
    read -sp "Enter database password: " DB_PASSWORD
    echo

    DATABASE_URL="postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME?sslmode=require"
else
    echo "Using in-cluster PostgreSQL (not recommended for production)"
    DATABASE_URL="postgresql://postgres:your-secure-password-change-in-production@postgres.default.svc.cluster.local:5432/todo_db"
fi

# Kafka Configuration
if [ -n "$KAFKA_BOOTSTRAP_SERVERS" ]; then
    echo "Using external Kafka: $KAFKA_BOOTSTRAP_SERVERS"
    echo "Please provide Kafka credentials if using SASL"
    read -p "Enter Kafka SASL username (or press Enter to skip): " KAFKA_USERNAME
    if [ -n "$KAFKA_USERNAME" ]; then
        read -sp "Enter Kafka SASL password: " KAFKA_PASSWORD
        echo
    fi
else
    echo "Using in-cluster Kafka (Strimzi)"
    KAFKA_BOOTSTRAP_SERVERS="kafka-cluster-kafka-bootstrap.kafka.svc.cluster.local:9092"
fi

echo -e "${GREEN}✓ External services configured${NC}"

# ============================================
# Step 5: Create Kubernetes Secrets
# ============================================

echo -e "\n${YELLOW}Step 5: Creating Kubernetes secrets...${NC}"

# Get other required secrets
read -p "Enter JWT_SECRET_KEY (min 32 chars): " JWT_SECRET
read -p "Enter BETTER_AUTH_SECRET: " BETTER_AUTH_SECRET
read -p "Enter OPENAI_API_KEY: " OPENAI_API_KEY
read -p "Enter SMTP_HOST (default: smtp.gmail.com): " SMTP_HOST
SMTP_HOST=${SMTP_HOST:-smtp.gmail.com}
read -p "Enter SMTP_USERNAME: " SMTP_USERNAME
read -sp "Enter SMTP_PASSWORD: " SMTP_PASSWORD
echo
read -p "Enter SMTP_FROM_EMAIL: " SMTP_FROM_EMAIL

# Create backend secrets
kubectl create secret generic backend-secrets \
    --from-literal=DATABASE_URL="$DATABASE_URL" \
    --from-literal=JWT_SECRET_KEY="$JWT_SECRET" \
    --from-literal=BETTER_AUTH_SECRET="$BETTER_AUTH_SECRET" \
    --from-literal=BETTER_AUTH_URL="http://better-auth-service.default.svc.cluster.local:3001" \
    --from-literal=OPENAI_API_KEY="$OPENAI_API_KEY" \
    --from-literal=AUTH_SECRET="$JWT_SECRET" \
    --from-literal=AUTH_ISSUER="https://${DOMAIN:-localhost:8000}" \
    --from-literal=SMTP_HOST="$SMTP_HOST" \
    --from-literal=SMTP_PORT="587" \
    --from-literal=SMTP_USERNAME="$SMTP_USERNAME" \
    --from-literal=SMTP_PASSWORD="$SMTP_PASSWORD" \
    --from-literal=SMTP_FROM_EMAIL="$SMTP_FROM_EMAIL" \
    --from-literal=SMTP_FROM_NAME="Todo App Notifications" \
    --from-literal=KAFKA_BOOTSTRAP_SERVERS="$KAFKA_BOOTSTRAP_SERVERS" \
    --dry-run=client -o yaml | kubectl apply -f -

echo -e "${GREEN}✓ Secrets created${NC}"

# ============================================
# Step 6: Install Infrastructure Components
# ============================================

echo -e "\n${YELLOW}Step 6: Installing infrastructure components...${NC}"

# Install Cert-Manager for SSL
echo "Installing cert-manager..."
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
kubectl wait --for=condition=ready pod -l app.kubernetes.io/instance=cert-manager -n cert-manager --timeout=300s
echo -e "${GREEN}✓ cert-manager installed${NC}"

# Install NGINX Ingress Controller
echo "Installing NGINX Ingress..."
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.9.4/deploy/static/provider/do/deploy.yaml
kubectl wait --for=condition=ready pod -l app.kubernetes.io/component=controller -n ingress-nginx --timeout=300s
echo -e "${GREEN}✓ NGINX Ingress installed${NC}"

# Install Dapr (without mTLS)
if ! kubectl get namespace dapr-system &> /dev/null; then
    echo "Installing Dapr..."
    helm repo add dapr https://dapr.github.io/helm-charts/
    helm repo update
    helm install dapr dapr/dapr \
        --namespace dapr-system \
        --create-namespace \
        --set global.mtls.enabled=false \
        --wait
    echo -e "${GREEN}✓ Dapr installed${NC}"
else
    echo -e "${GREEN}✓ Dapr already installed${NC}"
fi

# Install PostgreSQL (if not using managed DB)
if [ -z "$DO_DB_ID" ]; then
    echo "Installing PostgreSQL..."
    kubectl apply -f phase-v/kubernetes/infrastructure/postgres.yaml
    kubectl wait --for=condition=ready pod -l app=postgres --timeout=300s
    echo -e "${GREEN}✓ PostgreSQL installed${NC}"
fi

# Install Kafka (if not using external Kafka)
if [ -z "$KAFKA_BOOTSTRAP_SERVERS" ] || [[ "$KAFKA_BOOTSTRAP_SERVERS" == *".svc.cluster.local"* ]]; then
    echo "Installing Kafka (Strimzi)..."

    # Create kafka namespace
    kubectl create namespace kafka --dry-run=client -o yaml | kubectl apply -f -

    # Install Strimzi operator
    kubectl create -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka
    sleep 10

    # Deploy Kafka cluster
    kubectl apply -f phase-v/kubernetes/infrastructure/kafka-cluster-kraft.yaml -n kafka

    echo "Waiting for Kafka to be ready (this may take 5-10 minutes)..."
    kubectl wait kafka/kafka-cluster --for=condition=Ready --timeout=600s -n kafka
    echo -e "${GREEN}✓ Kafka installed${NC}"
fi

echo -e "${GREEN}✓ Infrastructure components installed${NC}"

# ============================================
# Step 7: Deploy Application Services
# ============================================

echo -e "\n${YELLOW}Step 7: Deploying application services...${NC}"

# Update deployment images to use DO registry
for SERVICE in "${SERVICES[@]}"; do
    kubectl set image deployment/$SERVICE \
        $SERVICE=$DO_REGISTRY/$SERVICE:latest \
        --record || true
done

# Apply all deployments
kubectl apply -f phase-v/kubernetes/deployments/

echo "Waiting for deployments to be ready..."
sleep 30

# Check deployment status
kubectl get deployments

echo -e "${GREEN}✓ Application services deployed${NC}"

# ============================================
# Step 8: Configure Ingress and SSL
# ============================================

if [ -n "$DOMAIN" ]; then
    echo -e "\n${YELLOW}Step 8: Configuring Ingress and SSL...${NC}"

    # Get LoadBalancer IP
    echo "Waiting for LoadBalancer IP..."
    LB_IP=""
    for i in {1..60}; do
        LB_IP=$(kubectl get svc ingress-nginx-controller -n ingress-nginx -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "")
        if [ -n "$LB_IP" ]; then
            break
        fi
        sleep 5
    done

    if [ -z "$LB_IP" ]; then
        echo -e "${RED}Warning: Could not get LoadBalancer IP${NC}"
    else
        echo -e "${GREEN}LoadBalancer IP: $LB_IP${NC}"
        echo -e "${YELLOW}Please configure DNS: $DOMAIN -> $LB_IP${NC}"
    fi

    # Create ClusterIssuer for Let's Encrypt
    cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@${DOMAIN}
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF

    # Create Ingress
    cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: todo-app-ingress
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/websocket-services: "websocket-sync-service"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - $DOMAIN
    secretName: todo-app-tls
  rules:
  - host: $DOMAIN
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: api-service
            port:
              number: 8000
      - path: /ws
        pathType: Prefix
        backend:
          service:
            name: websocket-sync-service
            port:
              number: 8004
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 80
EOF

    echo -e "${GREEN}✓ Ingress configured${NC}"
    echo -e "${YELLOW}SSL certificate will be issued automatically by Let's Encrypt${NC}"
else
    echo -e "\n${YELLOW}Step 8: Skipping Ingress configuration (no domain provided)${NC}"
fi

# ============================================
# Step 9: Configure Monitoring (Optional)
# ============================================

echo -e "\n${YELLOW}Step 9: Setting up monitoring...${NC}"

read -p "Install monitoring stack (Prometheus + Grafana)? [y/N]: " INSTALL_MONITORING

if [[ "$INSTALL_MONITORING" =~ ^[Yy]$ ]]; then
    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    helm repo update

    helm install prometheus prometheus-community/kube-prometheus-stack \
        --namespace monitoring \
        --create-namespace \
        --wait

    echo -e "${GREEN}✓ Monitoring stack installed${NC}"
    echo "Access Grafana: kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80"
    echo "Default credentials: admin / prom-operator"
else
    echo "Skipping monitoring installation"
fi

# ============================================
# Deployment Complete
# ============================================

echo -e "\n${GREEN}=========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}=========================================${NC}"

echo -e "\n${YELLOW}Cluster Information:${NC}"
echo "Cluster Name: $CLUSTER_NAME"
echo "Region: $REGION"
kubectl get nodes

echo -e "\n${YELLOW}Application URLs:${NC}"
if [ -n "$DOMAIN" ]; then
    echo "Production URL: https://$DOMAIN"
    echo "API Endpoint: https://$DOMAIN/api"
    echo "WebSocket: wss://$DOMAIN/ws"
else
    echo "LoadBalancer IP: $(kubectl get svc ingress-nginx-controller -n ingress-nginx -o jsonpath='{.status.loadBalancer.ingress[0].ip}')"
    echo "Access via: http://<LOADBALANCER_IP>"
fi

echo -e "\n${YELLOW}Service Status:${NC}"
kubectl get deployments
kubectl get pods

echo -e "\n${YELLOW}Useful Commands:${NC}"
echo "View logs: kubectl logs -f deployment/api-service"
echo "Scale service: kubectl scale deployment/api-service --replicas=5"
echo "Update image: kubectl set image deployment/api-service api-service=$DO_REGISTRY/api-service:v2"
echo "Delete cluster: doctl kubernetes cluster delete $CLUSTER_NAME"

echo -e "\n${YELLOW}Next Steps:${NC}"
echo "1. Configure DNS to point $DOMAIN to LoadBalancer IP"
echo "2. Wait for SSL certificate to be issued (check: kubectl get certificate)"
echo "3. Test application: curl https://$DOMAIN/api/health"
echo "4. Set up CI/CD pipeline for automatic deployments"
echo "5. Configure backups for PostgreSQL database"

echo -e "\n${GREEN}Deployment script completed successfully!${NC}"
