# Cloud Kubernetes Deployment Guide

**Version**: 1.0
**Last Updated**: 2026-01-05
**Supported Platforms**: Azure AKS, Google GKE, Oracle OKE

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Azure AKS Deployment](#azure-aks-deployment)
3. [Google GKE Deployment](#google-gke-deployment)
4. [Oracle OKE Deployment](#oracle-oke-deployment)
5. [Redpanda Cloud Setup](#redpanda-cloud-setup)
6. [Dapr Cloud Installation](#dapr-cloud-installation)
7. [Application Deployment](#application-deployment)
8. [DNS and Ingress Configuration](#dns-and-ingress-configuration)
9. [Monitoring and Observability](#monitoring-and-observability)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Tools

```bash
# Kubernetes CLI
kubectl version --client

# Helm 3.10+
helm version

# Dapr CLI
dapr --version

# Cloud Provider CLIs
az --version        # Azure CLI
gcloud --version    # Google Cloud SDK
oci --version       # Oracle Cloud CLI

# Docker (for image building)
docker --version
```

### Required Accounts

- Cloud provider account (Azure/Google/Oracle)
- Container registry (Docker Hub, ACR, GCR, or OCIR)
- Redpanda Cloud account (or Confluent Cloud/AWS MSK)
- PostgreSQL database (Neon, Supabase, or cloud-managed)

### Environment Variables

Create a `.env.production` file:

```bash
# Database
DATABASE_URL=postgresql://user:password@host:5432/dbname?sslmode=require

# Kafka (Redpanda Cloud)
KAFKA_BROKERS=seed-xxx.cloud.redpanda.com:9092
KAFKA_SASL_USERNAME=your-username
KAFKA_SASL_PASSWORD=your-password

# SMTP (for notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@yourdomain.com

# JWT
JWT_SECRET=your-jwt-secret-key-change-in-production

# Application
ENVIRONMENT=production
LOG_LEVEL=INFO
```

---

## Azure AKS Deployment

### 1. Create Resource Group

```bash
# Set variables
RESOURCE_GROUP=todo-app-rg
LOCATION=eastus
CLUSTER_NAME=todo-app-aks

# Create resource group
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION
```

### 2. Create AKS Cluster

```bash
# Create AKS cluster with 3 nodes
az aks create \
  --resource-group $RESOURCE_GROUP \
  --name $CLUSTER_NAME \
  --node-count 3 \
  --node-vm-size Standard_D2s_v3 \
  --enable-addons monitoring,http_application_routing \
  --enable-managed-identity \
  --generate-ssh-keys \
  --kubernetes-version 1.28.5 \
  --network-plugin azure

# Get credentials
az aks get-credentials \
  --resource-group $RESOURCE_GROUP \
  --name $CLUSTER_NAME

# Verify connection
kubectl cluster-info
kubectl get nodes
```

### 3. Create Azure Container Registry (Optional)

```bash
ACR_NAME=todoappackr

# Create ACR
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $ACR_NAME \
  --sku Standard

# Attach ACR to AKS
az aks update \
  --resource-group $RESOURCE_GROUP \
  --name $CLUSTER_NAME \
  --attach-acr $ACR_NAME

# Login to ACR
az acr login --name $ACR_NAME
```

### 4. Switch Kubernetes Context

```bash
# List contexts
kubectl config get-contexts

# Switch to AKS context
kubectl config use-context $CLUSTER_NAME
```

---

## Google GKE Deployment

### 1. Set GCP Project

```bash
# Set variables
PROJECT_ID=todo-app-project
REGION=us-central1
CLUSTER_NAME=todo-app-gke

# Set project
gcloud config set project $PROJECT_ID
gcloud config set compute/region $REGION
```

### 2. Create GKE Cluster

```bash
# Enable required APIs
gcloud services enable container.googleapis.com

# Create GKE cluster
gcloud container clusters create $CLUSTER_NAME \
  --region $REGION \
  --num-nodes 1 \
  --machine-type n1-standard-2 \
  --enable-autoscaling \
  --min-nodes 1 \
  --max-nodes 5 \
  --enable-stackdriver-kubernetes \
  --addons HorizontalPodAutoscaling,HttpLoadBalancing,GcePersistentDiskCsiDriver

# Get credentials
gcloud container clusters get-credentials $CLUSTER_NAME --region $REGION

# Verify connection
kubectl cluster-info
kubectl get nodes
```

### 3. Create Google Container Registry (Optional)

```bash
# Enable GCR API
gcloud services enable containerregistry.googleapis.com

# Configure Docker to use GCR
gcloud auth configure-docker

# Tag and push images
docker tag api-service:latest gcr.io/$PROJECT_ID/api-service:latest
docker push gcr.io/$PROJECT_ID/api-service:latest
```

### 4. Switch Kubernetes Context

```bash
# List contexts
kubectl config get-contexts

# Switch to GKE context
kubectl config use-context gke_${PROJECT_ID}_${REGION}_${CLUSTER_NAME}
```

---

## Oracle OKE Deployment

### 1. Set OCI Compartment

```bash
# Set variables
COMPARTMENT_ID=ocid1.compartment.oc1..xxx
CLUSTER_NAME=todo-app-oke
REGION=us-ashburn-1

# Set OCI config
oci setup config
```

### 2. Create OKE Cluster

```bash
# Create VCN (Virtual Cloud Network)
oci network vcn create \
  --compartment-id $COMPARTMENT_ID \
  --display-name todo-app-vcn \
  --cidr-block 10.0.0.0/16

# Create OKE cluster (via OCI Console is recommended)
# Alternatively, use OCI CLI:
oci ce cluster create \
  --compartment-id $COMPARTMENT_ID \
  --name $CLUSTER_NAME \
  --kubernetes-version v1.28.5 \
  --vcn-id <vcn-ocid>

# Get kubeconfig
oci ce cluster create-kubeconfig \
  --cluster-id <cluster-ocid> \
  --file ~/.kube/config \
  --region $REGION

# Verify connection
kubectl cluster-info
kubectl get nodes
```

### 3. Oracle Container Registry (OCIR)

```bash
# Login to OCIR
docker login <region-key>.ocir.io \
  --username <tenancy-namespace>/<username> \
  --password <auth-token>

# Tag and push images
docker tag api-service:latest <region-key>.ocir.io/<tenancy-namespace>/api-service:latest
docker push <region-key>.ocir.io/<tenancy-namespace>/api-service:latest
```

### 4. Switch Kubernetes Context

```bash
# List contexts
kubectl config get-contexts

# Switch to OKE context
kubectl config use-context $CLUSTER_NAME
```

---

## Redpanda Cloud Setup

### 1. Create Redpanda Cloud Cluster

1. Sign up at [https://cloud.redpanda.com](https://cloud.redpanda.com)
2. Create a new cluster:
   - **Provider**: AWS, GCP, or Azure
   - **Region**: Choose closest to your Kubernetes cluster
   - **Tier**: Serverless (free tier) or Dedicated
   - **Name**: `todo-app-kafka`

### 2. Create Kafka Topics

```bash
# Install Redpanda CLI
curl -LO https://github.com/redpanda-data/redpanda/releases/latest/download/rpk-linux-amd64.zip
unzip rpk-linux-amd64.zip
sudo mv rpk /usr/local/bin/

# Configure rpk
rpk cloud auth login

# Create topics
rpk topic create task-events \
  --partitions 6 \
  --replicas 3 \
  --config retention.ms=604800000

rpk topic create reminders \
  --partitions 3 \
  --replicas 3 \
  --config retention.ms=604800000

rpk topic create task-updates \
  --partitions 6 \
  --replicas 3 \
  --config retention.ms=86400000

rpk topic create dlq-events \
  --partitions 3 \
  --replicas 3 \
  --config retention.ms=2592000000

# Verify topics
rpk topic list
```

### 3. Generate SASL Credentials

In Redpanda Cloud Console:
1. Go to **Security** → **Service Accounts**
2. Create a new service account: `todo-app-service-account`
3. Copy the **Username** and **Password**
4. Grant permissions:
   - `task-events`: Read, Write
   - `reminders`: Read, Write
   - `task-updates`: Read, Write
   - `dlq-events`: Write

### 4. Get Bootstrap Servers

```bash
# Get cluster details
rpk cluster info

# Example output:
# CLUSTER
# =======
# redpanda.xxx.cloud.redpanda.com:9092
```

### 5. Test Connection

```bash
# Test with rpk
rpk topic produce task-events \
  --brokers redpanda.xxx.cloud.redpanda.com:9092 \
  --user <username> \
  --password <password> \
  --tls-enabled

# Type a test message and press Ctrl+D
{"event_id": "test", "event_type": "test"}

# Consume to verify
rpk topic consume task-events \
  --brokers redpanda.xxx.cloud.redpanda.com:9092 \
  --user <username> \
  --password <password> \
  --tls-enabled
```

---

## Dapr Cloud Installation

### 1. Install Dapr on Kubernetes

```bash
# Install Dapr with production settings
dapr init -k \
  --enable-mtls=true \
  --enable-ha=true \
  --wait \
  --timeout 600

# Verify Dapr installation
dapr status -k

# Expected output:
#   NAME                   NAMESPACE    HEALTHY  STATUS   REPLICAS  VERSION  AGE  CREATED
#   dapr-sidecar-injector  dapr-system  True     Running  3         1.12.0   1m   2024-01-05 10:00:00
#   dapr-sentry            dapr-system  True     Running  3         1.12.0   1m   2024-01-05 10:00:00
#   dapr-operator          dapr-system  True     Running  3         1.12.0   1m   2024-01-05 10:00:00
#   dapr-placement         dapr-system  True     Running  3         1.12.0   1m   2024-01-05 10:00:00
```

### 2. Create Production Namespace

```bash
# Create namespace
kubectl create namespace todo-app-prod

# Label namespace for Dapr sidecar injection
kubectl label namespace todo-app-prod dapr.io/enabled=true
```

### 3. Apply Dapr Configuration

```bash
# Apply Dapr configuration with mTLS and tracing
kubectl apply -f - <<EOF
apiVersion: dapr.io/v1alpha1
kind: Configuration
metadata:
  name: dapr-config
  namespace: todo-app-prod
spec:
  tracing:
    samplingRate: "1"
    zipkin:
      endpointAddress: "http://zipkin.default.svc.cluster.local:9411/api/v2/spans"
  mtls:
    enabled: true
    workloadCertTTL: "24h"
    allowedClockSkew: "15m"
  metric:
    enabled: true
EOF
```

### 4. Create Kubernetes Secrets

```bash
# Create database secret
kubectl create secret generic backend-secrets \
  --from-literal=DATABASE_URL='postgresql://user:pass@host:5432/db?sslmode=require' \
  --from-literal=SMTP_HOST='smtp.gmail.com' \
  --from-literal=SMTP_PORT='587' \
  --from-literal=SMTP_USERNAME='your-email@gmail.com' \
  --from-literal=SMTP_PASSWORD='your-app-password' \
  --from-literal=SMTP_FROM_EMAIL='noreply@yourdomain.com' \
  --from-literal=JWT_SECRET='your-jwt-secret-change-in-production' \
  --namespace=todo-app-prod

# Create Kafka secrets
kubectl create secret generic kafka-secrets \
  --from-literal=KAFKA_BROKERS='redpanda.xxx.cloud.redpanda.com:9092' \
  --from-literal=KAFKA_SASL_USERNAME='your-username' \
  --from-literal=KAFKA_SASL_PASSWORD='your-password' \
  --namespace=todo-app-prod

# Verify secrets
kubectl get secrets -n todo-app-prod
```

### 5. Apply Dapr Components (Cloud)

```bash
# Apply cloud Dapr components
kubectl apply -f phase-v/dapr-components/cloud/ -n todo-app-prod

# Verify components
kubectl get components -n todo-app-prod

# Expected output:
# NAME                   AGE
# kafka-pubsub           10s
# postgres-statestore    10s
# kubernetes-secrets     10s
```

---

## Application Deployment

### 1. Create Helm Values for Production

Create `charts/todo-chatbot-backend/values-cloud.yaml`:

```yaml
# Production Helm values
global:
  environment: production
  imageRegistry: docker.io/yourusername  # or ACR/GCR/OCIR
  imagePullPolicy: Always

# API Service
apiService:
  enabled: true
  replicaCount: 3
  image:
    repository: docker.io/yourusername/api-service
    tag: "1.0.0"
  resources:
    requests:
      cpu: 250m
      memory: 512Mi
    limits:
      cpu: 500m
      memory: 1Gi
  autoscaling:
    enabled: true
    minReplicas: 3
    maxReplicas: 10
    targetCPUUtilizationPercentage: 70
  service:
    type: ClusterIP
    port: 8000
  env:
    - name: DATABASE_URL
      valueFrom:
        secretKeyRef:
          name: backend-secrets
          key: DATABASE_URL
    - name: JWT_SECRET
      valueFrom:
        secretKeyRef:
          name: backend-secrets
          key: JWT_SECRET

# Recurring Task Service
recurringTaskService:
  enabled: true
  replicaCount: 2
  image:
    repository: docker.io/yourusername/recurring-task-service
    tag: "1.0.0"
  resources:
    requests:
      cpu: 100m
      memory: 256Mi
    limits:
      cpu: 200m
      memory: 512Mi
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 5
    targetCPUUtilizationPercentage: 70

# Notification Service
notificationService:
  enabled: true
  replicaCount: 2
  image:
    repository: docker.io/yourusername/notification-service
    tag: "1.0.0"
  resources:
    requests:
      cpu: 100m
      memory: 256Mi
    limits:
      cpu: 200m
      memory: 512Mi
  env:
    - name: SMTP_HOST
      valueFrom:
        secretKeyRef:
          name: backend-secrets
          key: SMTP_HOST

# Audit Service
auditService:
  enabled: true
  replicaCount: 2
  image:
    repository: docker.io/yourusername/audit-service
    tag: "1.0.0"
  resources:
    requests:
      cpu: 100m
      memory: 256Mi
    limits:
      cpu: 200m
      memory: 512Mi

# WebSocket Sync Service
websocketSyncService:
  enabled: true
  replicaCount: 2
  image:
    repository: docker.io/yourusername/websocket-sync-service
    tag: "1.0.0"
  resources:
    requests:
      cpu: 100m
      memory: 256Mi
    limits:
      cpu: 200m
      memory: 512Mi
  service:
    type: LoadBalancer
    port: 8080

# Ingress
ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
  hosts:
    - host: api.yourdomain.com
      paths:
        - path: /
          pathType: Prefix
          service: api-service
  tls:
    - secretName: api-tls-secret
      hosts:
        - api.yourdomain.com
```

### 2. Build and Push Docker Images

```bash
# Set your container registry
REGISTRY=docker.io/yourusername
VERSION=1.0.0

# Build all images
cd backend/api-service
docker build -t $REGISTRY/api-service:$VERSION .
docker push $REGISTRY/api-service:$VERSION

cd ../recurring-task-service
docker build -t $REGISTRY/recurring-task-service:$VERSION .
docker push $REGISTRY/recurring-task-service:$VERSION

cd ../notification-service
docker build -t $REGISTRY/notification-service:$VERSION .
docker push $REGISTRY/notification-service:$VERSION

cd ../audit-service
docker build -t $REGISTRY/audit-service:$VERSION .
docker push $REGISTRY/audit-service:$VERSION

cd ../websocket-sync-service
docker build -t $REGISTRY/websocket-sync-service:$VERSION .
docker push $REGISTRY/websocket-sync-service:$VERSION
```

### 3. Deploy with Helm

```bash
# Deploy to production namespace
helm upgrade --install todo-app-backend \
  ./charts/todo-chatbot-backend \
  --namespace todo-app-prod \
  --values ./charts/todo-chatbot-backend/values-cloud.yaml \
  --create-namespace \
  --wait \
  --timeout 10m

# Verify deployment
kubectl get pods -n todo-app-prod
kubectl get svc -n todo-app-prod
kubectl get ingress -n todo-app-prod
```

### 4. Wait for Rollout to Complete

```bash
# Wait for all deployments to be ready
kubectl rollout status deployment/api-service -n todo-app-prod
kubectl rollout status deployment/recurring-task-service -n todo-app-prod
kubectl rollout status deployment/notification-service -n todo-app-prod
kubectl rollout status deployment/audit-service -n todo-app-prod
kubectl rollout status deployment/websocket-sync-service -n todo-app-prod
```

### 5. Verify Dapr Sidecars

```bash
# Check that each pod has 2 containers (app + daprd)
kubectl get pods -n todo-app-prod -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[*].name}{"\n"}{end}'

# Check Dapr logs
kubectl logs -n todo-app-prod -l app=api-service -c daprd --tail=50
```

---

## DNS and Ingress Configuration

### 1. Install NGINX Ingress Controller

```bash
# Install NGINX Ingress
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.replicaCount=2 \
  --set controller.nodeSelector."kubernetes\.io/os"=linux \
  --set defaultBackend.nodeSelector."kubernetes\.io/os"=linux

# Get LoadBalancer IP
kubectl get svc -n ingress-nginx ingress-nginx-controller

# Wait for EXTERNAL-IP to be assigned
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=120s
```

### 2. Install cert-manager for TLS

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.3/cert-manager.yaml

# Create Let's Encrypt ClusterIssuer
kubectl apply -f - <<EOF
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
EOF
```

### 3. Configure DNS

Get the LoadBalancer external IP:

```bash
EXTERNAL_IP=$(kubectl get svc -n ingress-nginx ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "External IP: $EXTERNAL_IP"
```

Create DNS A records pointing to this IP:
- `api.yourdomain.com` → `$EXTERNAL_IP`
- `ws.yourdomain.com` → `$EXTERNAL_IP`

### 4. Verify TLS Certificate

```bash
# Check certificate status
kubectl get certificate -n todo-app-prod

# Describe certificate
kubectl describe certificate api-tls-secret -n todo-app-prod

# Test HTTPS
curl https://api.yourdomain.com/health
```

---

## Monitoring and Observability

### Install Prometheus and Grafana

```bash
# Add Helm repos
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Prometheus + Grafana stack
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set grafana.adminPassword=admin \
  --wait

# Port-forward Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80

# Access Grafana at http://localhost:3000
# Username: admin, Password: admin
```

---

## Troubleshooting

### Check Pod Logs

```bash
# API Service logs
kubectl logs -n todo-app-prod -l app=api-service -c api-service --tail=100

# Dapr sidecar logs
kubectl logs -n todo-app-prod -l app=api-service -c daprd --tail=100

# All services
kubectl logs -n todo-app-prod -l dapr.io/enabled=true --all-containers=true --tail=50
```

### Check Dapr Components

```bash
# List components
kubectl get components -n todo-app-prod

# Describe component
kubectl describe component kafka-pubsub -n todo-app-prod
```

### Test Kafka Connectivity

```bash
# Create test pod
kubectl run kafka-test -n todo-app-prod --rm -it --restart=Never \
  --image=confluentinc/cp-kafka:latest -- \
  kafka-console-consumer \
  --bootstrap-server $KAFKA_BROKERS \
  --topic task-events \
  --consumer-property security.protocol=SASL_SSL \
  --consumer-property sasl.mechanism=SCRAM-SHA-256 \
  --consumer-property sasl.jaas.config="org.apache.kafka.common.security.scram.ScramLoginModule required username=\"$KAFKA_USERNAME\" password=\"$KAFKA_PASSWORD\";"
```

### Common Issues

**Issue**: Pods stuck in `Pending` state
```bash
# Check events
kubectl describe pod <pod-name> -n todo-app-prod

# Common causes:
# - Insufficient cluster resources
# - Image pull errors
# - PVC mount issues
```

**Issue**: Dapr sidecar not injected
```bash
# Verify namespace label
kubectl get namespace todo-app-prod --show-labels

# Re-label if needed
kubectl label namespace todo-app-prod dapr.io/enabled=true --overwrite
```

**Issue**: Cannot connect to Kafka
```bash
# Verify secrets
kubectl get secret kafka-secrets -n todo-app-prod -o yaml

# Test from pod
kubectl exec -it <pod-name> -n todo-app-prod -c api-service -- \
  curl -X POST http://localhost:3500/v1.0/publish/kafka-pubsub/task-events \
  -H "Content-Type: application/json" \
  -d '{"event_id":"test","event_type":"test"}'
```

---

## Production Checklist

- [ ] Kubernetes cluster created and accessible
- [ ] Dapr installed with mTLS enabled
- [ ] Redpanda Cloud cluster created and topics configured
- [ ] Secrets created for database, Kafka, SMTP
- [ ] Dapr components applied (kafka-pubsub, postgres-statestore, kubernetes-secrets)
- [ ] Docker images built and pushed to registry
- [ ] Helm chart deployed with production values
- [ ] All pods running with Dapr sidecars
- [ ] LoadBalancer IP assigned
- [ ] DNS records configured
- [ ] TLS certificates issued
- [ ] Ingress routing working
- [ ] Health checks passing
- [ ] Monitoring stack installed
- [ ] End-to-end tests passing

---

**Next Steps**: [CI/CD Pipeline Setup](./CI_CD_SETUP.md)
