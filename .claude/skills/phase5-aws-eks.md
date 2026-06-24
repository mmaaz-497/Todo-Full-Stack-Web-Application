# Phase V – Deploy Existing Project to AWS EKS (Hackathon II)

## 1. Overview

Phase V focuses on deploying an existing full-stack application to AWS Elastic Kubernetes Service (EKS). This phase takes your containerized Next.js frontend and FastAPI backend applications and deploys them to a managed Kubernetes environment on AWS.

Amazon EKS is used because it provides a managed Kubernetes control plane, automatic scaling, high availability, and seamless integration with other AWS services. EKS handles the operational overhead of managing Kubernetes clusters while allowing you to focus on deploying and managing your applications.

### Architecture Diagram Description
```
Internet -> ALB -> EKS Nodes -> Pods (Frontend + Backend)
                    |
              ECR (Container Images)
                    |
              Neon DB (External Database)
                    |
              CloudWatch (Monitoring)
```

## 2. Prerequisites

Before starting the deployment, ensure you have:

- AWS account with billing enabled
- IAM permissions for EKS, EC2, ECR, CloudWatch, and VPC
- AWS CLI installed and configured (`aws configure`)
- eksctl installed
- kubectl installed
- Docker installed
- Helm installed
- Access to your existing Next.js + FastAPI codebase

## 3. Step-by-Step EKS Cluster Creation

Create an EKS cluster with 2-3 t3.medium nodes:

```bash
eksctl create cluster \
  --name my-cluster \
  --region us-east-1 \
  --nodegroup-name standard-workers \
  --node-type t3.medium \
  --nodes 2 \
  --nodes-minimum 1 \
  --nodes-maximum 4 \
  --managed
```

Configure kubectl to connect to your new cluster:

```bash
aws eks update-kubeconfig --name my-cluster --region us-east-1
```

Validate the cluster setup:

```bash
kubectl get nodes
kubectl cluster-info
```

## 4. Dockerization

### Frontend Dockerfile (Next.js)
```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY frontend/package*.json ./
RUN npm install
COPY frontend/. .
RUN npm run build

FROM node:18-alpine AS runner
WORKDIR /app
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001
COPY --from=builder --chown=nextjs:nodejs /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/public ./public
USER nextjs
EXPOSE 3000
ENV PORT 3000
CMD ["npm", "start"]
```

### Backend Dockerfile (FastAPI)
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY backend/ .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build your Docker images:

```bash
docker build -t todo-frontend:latest -f Dockerfile.frontend .
docker build -t todo-backend:latest -f Dockerfile.backend .
```

## 5. AWS ECR Setup

Create ECR repositories for your images:

```bash
aws ecr create-repository --repository-name todo-frontend --region us-east-1
aws ecr create-repository --repository-name todo-backend --region us-east-1
```

Login to ECR:

```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin [your-account-id].dkr.ecr.us-east-1.amazonaws.com
```

Tag and push your images:

```bash
docker tag todo-frontend:latest [your-account-id].dkr.ecr.us-east-1.amazonaws.com/todo-frontend:latest
docker tag todo-backend:latest [your-account-id].dkr.ecr.us-east-1.amazonaws.com/todo-backend:latest

docker push [your-account-id].dkr.ecr.us-east-1.amazonaws.com/todo-frontend:latest
docker push [your-account-id].dkr.ecr.us-east-1.amazonaws.com/todo-backend:latest
```

## 6. Helm Deployment

### Helm Chart Structure
```
todo-chart/
├── Chart.yaml
├── values.yaml
└── templates/
    ├── frontend-deployment.yaml
    ├── frontend-service.yaml
    ├── backend-deployment.yaml
    ├── backend-service.yaml
    └── secret.yaml
```

### values.yaml Example
```yaml
frontend:
  replicaCount: 2
  image:
    repository: [your-account-id].dkr.ecr.us-east-1.amazonaws.com/todo-frontend
    tag: latest
    pullPolicy: Always
  service:
    type: LoadBalancer
    port: 80

backend:
  replicaCount: 2
  image:
    repository: [your-account-id].dkr.ecr.us-east-1.amazonaws.com/todo-backend
    tag: latest
    pullPolicy: Always
  service:
    type: ClusterIP
    port: 8000

secrets:
  databaseUrl: "your-neon-db-url"
```

### Secret Template
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: todo-app-secrets
type: Opaque
data:
  database-url: {{ .Values.secrets.databaseUrl | b64enc }}
```

Deploy using Helm:

```bash
helm install todo ./todo-chart
```

## 7. AI-Assisted Ops

Use kubectl-ai for common operations:

```bash
# Check pod status
kubectl ai "show me the status of all pods in the default namespace"

# Get service details
kubectl ai "get load balancer service details"

# Scale deployments
kubectl ai "scale frontend deployment to 3 replicas"
```

Use kagent for complex troubleshooting:

```bash
kagent "analyze why pods are stuck in ContainerCreating state"
```

## 8. Monitoring

Enable CloudWatch logging for your EKS cluster:

```bash
# Create IAM policy for CloudWatch
eksctl utils associate-iam-oidc-provider --cluster my-cluster --region=us-east-1 --approve

# Install CloudWatch agent
kubectl apply -f https://raw.githubusercontent.com/aws-samples/amazon-cloudwatch-container-insights/latest/k8s-deployment-manifest-templates/deployment-mode/daemonset/container-insights-monitoring/quickstart/cwagent-fluentd-quickstart.yaml
```

For advanced monitoring, consider installing Prometheus and Grafana:

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install prometheus prometheus-community/kube-prometheus-stack
```

## 9. Testing Checklist

Complete these steps to verify your deployment:

```bash
# Update kubeconfig
aws eks update-kubeconfig --name my-cluster --region us-east-1

# Build frontend image
docker build -t todo-frontend:latest ./frontend

# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin [account].dkr.ecr.us-east-1.amazonaws.com

# Tag and push frontend
docker tag todo-frontend:latest [account].dkr.ecr.us-east-1.amazonaws.com/todo-frontend:latest
docker push [account].dkr.ecr.us-east-1.amazonaws.com/todo-frontend:latest

# Install Helm release
helm install todo ./helm-charts/todo-chart

# Verify services
kubectl get svc
```

## 10. Troubleshooting

### Common EKS Errors
- **Cluster creation timeouts**: Check VPC security groups and IAM permissions
- **Node group creation failures**: Verify subnet availability and IAM roles

### ImagePullBackOff
- Check ECR repository permissions
- Verify image tags and repository names
- Ensure correct AWS region in image URLs

### IAM Issues
- Attach `AmazonEKSClusterPolicy` to cluster role
- Attach `AmazonEKSWorkerNodePolicy`, `AmazonEC2ContainerRegistryReadOnly`, and `AmazonS3ReadOnlyAccess` to node role

### LoadBalancer Not Getting URL
- Verify VPC subnets have public IP assignment enabled
- Check that subnets have internet gateway attached
- Ensure ALB controller is properly installed

## 11. Research Notes

### Spec-Driven Infrastructure
Infrastructure as Code (IaC) ensures reproducible environments and eliminates configuration drift. Using Helm charts with version-controlled specifications creates a single source of truth for your deployments.

### Cloud Blueprints
EKS provides a standardized platform that abstracts away infrastructure complexity while maintaining flexibility. The combination of managed control plane and customizable worker nodes offers optimal balance between operational simplicity and control.

### Why Infra-as-Code Matters
Declarative infrastructure definitions enable consistent deployments across environments, facilitate disaster recovery, and support team collaboration. Version-controlling your infrastructure specifications creates an audit trail and enables rollbacks when needed.