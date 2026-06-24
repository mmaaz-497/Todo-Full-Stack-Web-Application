# Phase V – AWS EKS Security & Network Configuration (Hackathon II)

## 1. Overview

This phase focuses on securing your EKS cluster and configuring proper network settings for your full-stack application. Security and network configuration are critical for protecting your application and ensuring proper connectivity between services.

### Security Architecture Description
```
Internet -> WAF -> ALB -> EKS Node Group -> Pods (Frontend + Backend)
                    |         |
                 Private    Network Policies
                 Subnets    RBAC
                    |         |
              RDS/NeonDB <- Secrets Manager
                    |
              VPC Flow Logs -> CloudTrail
```

## 2. Prerequisites

Before configuring security and networking:

- Completed Phase V EKS cluster creation
- AWS CLI with Administrator privileges
- eksctl installed
- kubectl installed
- Helm installed
- Understanding of AWS networking concepts
- Access to your existing Next.js + FastAPI application

## 3. EKS Cluster Security Hardening

### Create Cluster with Security Best Practices
```bash
eksctl create cluster \
  --name secure-todo-cluster \
  --region us-east-1 \
  --version 1.28 \
  --nodegroup-name secure-workers \
  --node-type t3.medium \
  --nodes 2 \
  --nodes-minimum 1 \
  --nodes-maximum 4 \
  --managed \
  --enable-ssm \
  --with-oidc \
  --alb-ingress-access
```

### Configure Cluster Addons
```bash
eksctl create addon --name vpc-cni --cluster secure-todo-cluster --region us-east-1
eksctl create addon --name coredns --cluster secure-todo-cluster --region us-east-1
eksctl create addon --name kube-proxy --cluster secure-todo-cluster --region us-east-1
```

## 4. Network Configuration

### VPC and Subnet Setup
```bash
# Create VPC with private and public subnets
aws ec2 create-vpc --cidr-block 10.0.0.0/16 --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=todo-eks-vpc}]'

# Create public subnets (for Load Balancers)
aws ec2 create-subnet --vpc-id vpc-xxxxxxxxx --cidr-block 10.0.1.0/24 --availability-zone us-east-1a
aws ec2 create-subnet --vpc-id vpc-xxxxxxxxx --cidr-block 10.0.2.0/24 --availability-zone us-east-1b

# Create private subnets (for nodes)
aws ec2 create-subnet --vpc-id vpc-xxxxxxxxx --cidr-block 10.0.101.0/24 --availability-zone us-east-1a
aws ec2 create-subnet --vpc-id vpc-xxxxxxxxx --cidr-block 10.0.102.0/24 --availability-zone us-east-1b
```

### Configure NAT Gateway for Private Subnets
```bash
# Allocate EIP for NAT Gateway
aws ec2 allocate-address --domain vpc

# Create NAT Gateway
aws ec2 create-nat-gateway --subnet-id subnet-xxxxxxx --allocation-id eipalloc-xxxxxxx

# Update route table for private subnets
aws ec2 create-route --route-table-id rtb-xxxxxxx --destination-cidr-block 0.0.0.0/0 --nat-gateway-id nat-xxxxxxx
```

## 5. Kubernetes Network Policies

### Create Network Policy for Frontend
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: frontend-network-policy
spec:
  podSelector:
    matchLabels:
      app: todo-frontend
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 3000
  egress:
  - to: []
    ports:
    - protocol: TCP
      port: 53
    - protocol: UDP
      port: 53
```

### Create Network Policy for Backend
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-network-policy
spec:
  podSelector:
    matchLabels:
      app: todo-backend
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: todo-frontend
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: kube-system
      podSelector:
        matchLabels:
          k8s-app: kube-dns
    ports:
    - protocol: TCP
      port: 53
    - protocol: UDP
      port: 53
```

## 6. AWS Load Balancer Controller

Install the AWS Load Balancer Controller for advanced load balancing:

```bash
# Create IAM OIDC provider
eksctl utils associate-iam-oidc-provider --cluster secure-todo-cluster --region us-east-1 --approve

# Create IAM policy
curl -o iam_policy.json https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/main/docs/install/iam_policy.json
aws iam create-policy --policy-name AWSLoadBalancerControllerIAMPolicy --policy-document file://iam_policy.json

# Create service account
eksctl create iamserviceaccount --cluster=secure-todo-cluster --namespace=kube-system --name=aws-load-balancer-controller --role-name AmazonEKSLoadBalancerControllerRole --attach-policy-arn=arn:aws:iam::ACCOUNT-ID:policy/AWSLoadBalancerControllerIAMPolicy --approve

# Install the controller
kubectl apply -k "github.com/aws/eks-charts/stable/aws-load-balancer-controller/crds?ref=master"
helm repo add eks https://aws.github.io/eks-charts
helm install aws-load-balancer-controller eks/aws-load-balancer-controller --set clusterName=secure-todo-cluster --set serviceAccount.create=false --set serviceAccount.name=aws-load-balancer-controller -n kube-system
```

## 7. Secrets Management

### Configure AWS Secrets Manager Integration
```bash
# Create secret in Secrets Manager
aws secretsmanager create-secret --name todo-app/db-credentials --description "Database credentials for Todo app" --secret-string '{"username":"dbuser","password":"dbpass"}'

# Install Secrets Store CSI Driver
kubectl apply -f https://raw.githubusercontent.com/kubernetes-sigs/secrets-store-csi-driver/main/deploy/rbac-secretproviderclass.yaml
kubectl apply -f https://raw.githubusercontent.com/kubernetes-sigs/secrets-store-csi-driver/main/deploy/csidriver.yaml
kubectl apply -f https://raw.githubusercontent.com/kubernetes-sigs/secrets-store-csi-driver/main/deploy/secrets-store.csi.x-k8s.io_secretproviderclasses.yaml
kubectl apply -f https://raw.githubusercontent.com/kubernetes-sigs/secrets-store-csi-driver/main/deploy/secrets-store.csi.x-k8s.io_secretproviderclasspodstatuses.yaml
kubectl apply -f https://raw.githubusercontent.com/kubernetes-sigs/secrets-store-csi-driver/main/deploy/secrets-store-csi-driver.yaml

# Install AWS Provider
kubectl apply -f https://raw.githubusercontent.com/aws/secrets-store-csi-driver-provider-aws/main/deployment/aws-provider-installer.yaml
```

### SecretProviderClass for Database Credentials
```yaml
apiVersion: secrets-store.csi.x-k8s.io/v1
kind: SecretProviderClass
metadata:
  name: todo-db-secrets
spec:
  provider: aws
  parameters:
    objects: |
        - objectName: "todo-app/db-credentials"
          objectType: "secretsmanager"
          jmesPath:
            - path: "username"
              objectAlias: "username"
            - path: "password"
              objectAlias: "password"
  secretObjects:
  - data:
    - key: username
      objectName: username
    - key: password
      objectName: password
    secretName: todo-db-credentials
    type: Opaque
```

## 8. RBAC Configuration

### Create Custom RBAC Roles
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: todo-app-role
rules:
- apiGroups: [""]
  resources: ["pods", "services", "configmaps"]
  verbs: ["get", "list", "create", "update", "patch", "delete"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: todo-app-rolebinding
  namespace: default
subjects:
- kind: ServiceAccount
  name: default
  namespace: default
roleRef:
  kind: Role
  name: todo-app-role
  apiGroup: rbac.authorization.k8s.io
```

## 9. Pod Security Standards

### Configure Pod Security Admission
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: todo-app
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

### Secure Pod Templates
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-frontend
spec:
  template:
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 2000
      containers:
      - name: frontend
        image: [your-ecr-repo]/todo-frontend:latest
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities:
            drop:
            - ALL
        # ... rest of container spec
```

## 10. Monitoring and Logging Configuration

### Enable VPC Flow Logs
```bash
aws ec2 create-flow-logs --resource-type VPC --resource-ids vpc-xxxxxxxxx --traffic-type ALL --log-destination-type cloud-watch-logs --log-group-name todo-vpc-flowlogs
```

### Configure EKS Control Plane Logging
```bash
aws eks update-cluster-config --name secure-todo-cluster --logging '{"clusterLogging":[{"types":["api","audit","authenticator","controllerManager","scheduler"],"enabled":true}]}'
```

## 11. Testing Checklist

Complete these security and network validation steps:

```bash
# Verify cluster creation
aws eks describe-cluster --name secure-todo-cluster --query 'cluster.status'

# Check network policies
kubectl get networkpolicies

# Validate Load Balancer Controller
kubectl get pods -n kube-system | grep aws-load-balancer-controller

# Test network connectivity
kubectl run test-pod --image=nicolaka/netshoot -it --rm --generator=run-pod/v1

# Check security context enforcement
kubectl get ns todo-app -o yaml

# Verify secrets access
kubectl exec -it [pod-name] -- env | grep SECRET
```

## 12. Troubleshooting

### Network Policy Issues
- Verify pod labels match selectors in network policies
- Check that required ports are exposed in pod specifications
- Use `kubectl exec` to test connectivity between pods

### Load Balancer Problems
- Verify Load Balancer Controller installation
- Check that service accounts have proper IAM roles
- Ensure VPC subnets are tagged correctly for ALB

### Secrets Access Failures
- Confirm IAM roles are properly attached to service accounts
- Verify Secrets Manager permissions
- Check that SecretProviderClass references are correct

### RBAC Denials
- Review role bindings and permissions
- Use `kubectl auth can-i` to test permissions
- Verify service account usage in deployments

## 13. Research Notes

### Zero Trust Network Architecture
Implementing network policies and microsegmentation follows zero trust principles where no implicit trust is granted. Traffic between services is explicitly allowed only when necessary.

### Defense in Depth
Layered security controls including network policies, pod security standards, RBAC, and secrets management provide multiple barriers against potential threats.

### Infrastructure Security Posture
Regular security assessments of the EKS cluster configuration, including CIS benchmark compliance, help maintain a strong security posture over time.