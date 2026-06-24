# Phase V – AWS EKS Deployment Scripts & Best Practices (Hackathon II)

## 1. Overview

This phase provides comprehensive deployment scripts and best practices for operating your full-stack application on AWS EKS. These scripts automate common deployment tasks and implement industry-standard practices for managing EKS clusters.

### Script Architecture Description
```
Deployment Scripts -> Parameter Validation -> Pre-flight Checks -> Resource Creation -> Post-deployment Validation -> Status Reporting
      |                     |                      |                     |                    |                        |
   cluster-up.sh        validate-inputs.sh    health-check.sh      deploy-app.sh      verify-deployment.sh    status-report.sh
   cluster-down.sh      check-permissions.sh  readiness-check.sh   rollback.sh        smoke-test.sh           cleanup.sh
```

## 2. Prerequisites

Before using these deployment scripts:

- AWS CLI installed and configured
- eksctl installed
- kubectl installed and configured
- jq for JSON parsing
- Helm installed
- Docker installed
- Basic shell scripting knowledge
- Administrative access to AWS account

## 3. Cluster Management Scripts

### Cluster Creation Script: `cluster-up.sh`

```bash
#!/bin/bash

# cluster-up.sh - Create EKS cluster with best practices

set -euo pipefail

# Configuration
CLUSTER_NAME="${CLUSTER_NAME:-my-todo-cluster}"
REGION="${AWS_DEFAULT_REGION:-us-east-1}"
NODE_TYPE="${NODE_TYPE:-t3.medium}"
NODE_COUNT="${NODE_COUNT:-2}"
MIN_NODES="${MIN_NODES:-1}"
MAX_NODES="${MAX_NODES:-4}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Error handling
error_exit() {
    log "${RED}ERROR: $1${NC}" >&2
    exit 1
}

# Validate prerequisites
validate_prerequisites() {
    log "${YELLOW}Validating prerequisites...${NC}"

    command -v aws >/dev/null 2>&1 || error_exit "AWS CLI is not installed"
    command -v eksctl >/dev/null 2>&1 || error_exit "eksctl is not installed"
    command -v kubectl >/dev/null 2>&1 || error_exit "kubectl is not installed"
    command -v jq >/dev/null 2>&1 || error_exit "jq is not installed"

    # Check AWS credentials
    aws sts get-caller-identity >/dev/null 2>&1 || error_exit "AWS credentials not configured"

    log "${GREEN}Prerequisites validated${NC}"
}

# Validate input parameters
validate_inputs() {
    log "${YELLOW}Validating input parameters...${NC}"

    if [[ -z "$CLUSTER_NAME" ]]; then
        error_exit "CLUSTER_NAME cannot be empty"
    fi

    if ! aws ec2 describe-regions --region-names "$REGION" >/dev/null 2>&1; then
        error_exit "Invalid AWS region: $REGION"
    fi

    log "${GREEN}Input parameters validated${NC}"
}

# Check if cluster already exists
check_cluster_exists() {
    log "${YELLOW}Checking if cluster exists...${NC}"

    if aws eks describe-cluster --name "$CLUSTER_NAME" --region "$REGION" >/dev/null 2>&1; then
        log "${YELLOW}Cluster $CLUSTER_NAME already exists${NC}"
        read -p "Do you want to continue? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log "Aborting cluster creation"
            exit 0
        fi
    else
        log "${GREEN}Cluster does not exist, proceeding with creation${NC}"
    fi
}

# Create EKS cluster
create_cluster() {
    log "${YELLOW}Creating EKS cluster: $CLUSTER_NAME...${NC}"

    eksctl create cluster \
        --name "$CLUSTER_NAME" \
        --region "$REGION" \
        --nodegroup-name standard-workers \
        --node-type "$NODE_TYPE" \
        --nodes "$NODE_COUNT" \
        --nodes-minimum "$MIN_NODES" \
        --nodes-maximum "$MAX_NODES" \
        --managed \
        --with-oidc \
        --alb-ingress-access \
        --ssh-access \
        --ssh-public-key "$HOME/.ssh/id_rsa.pub" \
        --zones "$(aws ec2 describe-availability-zones --region "$REGION" --query 'AvailabilityZones[0:2][].ZoneName' --output text | tr '\t' ',')" \
        || error_exit "Failed to create EKS cluster"

    log "${GREEN}EKS cluster created successfully${NC}"
}

# Configure kubectl
configure_kubectl() {
    log "${YELLOW}Configuring kubectl...${NC}"

    aws eks update-kubeconfig --name "$CLUSTER_NAME" --region "$REGION" || error_exit "Failed to update kubeconfig"

    # Wait for cluster to be ready
    log "${YELLOW}Waiting for cluster to be ready...${NC}"
    kubectl wait --for=condition=Ready node --all --timeout=300s || error_exit "Cluster nodes are not ready"

    log "${GREEN}kubectl configured and cluster is ready${NC}"
}

# Install essential addons
install_addons() {
    log "${YELLOW}Installing essential addons...${NC}"

    # Install AWS Load Balancer Controller
    eksctl create addon --name vpc-cni --cluster "$CLUSTER_NAME" --region "$REGION" || log "${RED}Warning: Failed to install VPC CNI addon${NC}"
    eksctl create addon --name coredns --cluster "$CLUSTER_NAME" --region "$REGION" || log "${RED}Warning: Failed to install CoreDNS addon${NC}"
    eksctl create addon --name kube-proxy --cluster "$CLUSTER_NAME" --region "$REGION" || log "${RED}Warning: Failed to install Kube Proxy addon${NC}"

    log "${GREEN}Essential addons installed${NC}"
}

# Main execution
main() {
    log "${GREEN}Starting EKS cluster creation...${NC}"

    validate_prerequisites
    validate_inputs
    check_cluster_exists
    create_cluster
    configure_kubectl
    install_addons

    log "${GREEN}EKS cluster creation completed successfully!${NC}"
    log "Cluster: $CLUSTER_NAME"
    log "Region: $REGION"
    log "Node Type: $NODE_TYPE"
    log "Node Count: $NODE_COUNT"
    log "Access the cluster with: kubectl get nodes"
}

main "$@"
```

### Cluster Deletion Script: `cluster-down.sh`

```bash
#!/bin/bash

# cluster-down.sh - Safely delete EKS cluster

set -euo pipefail

CLUSTER_NAME="${CLUSTER_NAME:-my-todo-cluster}"
REGION="${AWS_DEFAULT_REGION:-us-east-1}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Error handling
error_exit() {
    log "${RED}ERROR: $1${NC}" >&2
    exit 1
}

# Confirmation prompt
confirm_deletion() {
    log "${RED}WARNING: This will permanently delete the EKS cluster and all associated resources${NC}"
    read -p "Are you sure you want to delete cluster $CLUSTER_NAME? (yes/no): " -r
    echo
    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        log "Deletion cancelled"
        exit 0
    fi
}

# Check cluster status
check_cluster_status() {
    log "${YELLOW}Checking cluster status...${NC}"

    if ! aws eks describe-cluster --name "$CLUSTER_NAME" --region "$REGION" >/dev/null 2>&1; then
        log "${YELLOW}Cluster $CLUSTER_NAME does not exist${NC}"
        exit 0
    fi

    STATUS=$(aws eks describe-cluster --name "$CLUSTER_NAME" --region "$REGION" --query 'cluster.status' --output text)
    if [[ "$STATUS" != "ACTIVE" ]]; then
        log "${RED}Cluster is not ACTIVE, current status: $STATUS${NC}"
        exit 1
    fi

    log "${GREEN}Cluster status: $STATUS${NC}"
}

# Delete load balancers first
delete_load_balancers() {
    log "${YELLOW}Deleting load balancers...${NC}"

    LB_NAMES=$(aws elb describe-load-balancers --query 'LoadBalancerDescriptions[].LoadBalancerName' --output text 2>/dev/null || true)
    if [[ -n "$LB_NAMES" ]]; then
        for lb in $LB_NAMES; do
            if [[ "$lb" == *"-$CLUSTER_NAME-"* ]]; then
                log "Deleting load balancer: $lb"
                aws elb delete-load-balancer --load-balancer-name "$lb" 2>/dev/null || true
            fi
        done
    fi

    # Also check for ALBs
    ALB_ARNS=$(aws elbv2 describe-load-balancers --query 'LoadBalancers[].LoadBalancerArn' --output text 2>/dev/null || true)
    if [[ -n "$ALB_ARNS" ]]; then
        for arn in $ALB_ARNS; do
            if [[ "$arn" == *"$CLUSTER_NAME"* ]]; then
                log "Deleting ALB: $arn"
                aws elbv2 delete-load-balancer --load-balancer-arn "$arn" 2>/dev/null || true
            fi
        done
    fi
}

# Delete cluster
delete_cluster() {
    log "${YELLOW}Deleting EKS cluster: $CLUSTER_NAME...${NC}"

    eksctl delete cluster --name "$CLUSTER_NAME" --region "$REGION" || error_exit "Failed to delete EKS cluster"

    log "${GREEN}EKS cluster deleted successfully${NC}"
}

# Main execution
main() {
    log "${RED}Starting EKS cluster deletion...${NC}"

    check_cluster_status
    confirm_deletion
    delete_load_balancers
    delete_cluster

    log "${GREEN}EKS cluster deletion completed${NC}"
}

main "$@"
```

## 4. Application Deployment Scripts

### Deploy Application Script: `deploy-app.sh`

```bash
#!/bin/bash

# deploy-app.sh - Deploy Todo application to EKS

set -euo pipefail

CLUSTER_NAME="${CLUSTER_NAME:-my-todo-cluster}"
REGION="${AWS_DEFAULT_REGION:-us-east-1}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
HELM_RELEASE="${HELM_RELEASE:-todo-app}"
NAMESPACE="${NAMESPACE:-default}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Error handling
error_exit() {
    log "${RED}ERROR: $1${NC}" >&2
    exit 1
}

# Validate prerequisites
validate_prerequisites() {
    log "${YELLOW}Validating prerequisites...${NC}"

    command -v aws >/dev/null 2>&1 || error_exit "AWS CLI is not installed"
    command -v kubectl >/dev/null 2>&1 || error_exit "kubectl is not installed"
    command -v helm >/dev/null 2>&1 || error_exit "Helm is not installed"

    # Check if cluster is accessible
    aws eks describe-cluster --name "$CLUSTER_NAME" --region "$REGION" >/dev/null 2>&1 || error_exit "Cannot access EKS cluster $CLUSTER_NAME"

    log "${GREEN}Prerequisites validated${NC}"
}

# Validate inputs
validate_inputs() {
    log "${YELLOW}Validating input parameters...${NC}"

    if [[ -z "$CLUSTER_NAME" ]]; then
        error_exit "CLUSTER_NAME cannot be empty"
    fi

    if [[ -z "$HELM_RELEASE" ]]; then
        error_exit "HELM_RELEASE cannot be empty"
    fi

    log "${GREEN}Input parameters validated${NC}"
}

# Check cluster readiness
check_cluster_readiness() {
    log "${YELLOW}Checking cluster readiness...${NC}"

    # Wait for nodes to be ready
    kubectl wait --for=condition=Ready node --all --timeout=300s || error_exit "Cluster nodes are not ready"

    # Check if namespace exists, create if not
    if ! kubectl get namespace "$NAMESPACE" >/dev/null 2>&1; then
        log "Creating namespace: $NAMESPACE"
        kubectl create namespace "$NAMESPACE"
    fi

    log "${GREEN}Cluster is ready${NC}"
}

# Deploy using Helm
deploy_with_helm() {
    log "${YELLOW}Deploying application with Helm...${NC}"

    # Check if Helm release exists
    if helm status "$HELM_RELEASE" -n "$NAMESPACE" >/dev/null 2>&1; then
        log "Upgrading existing release: $HELM_RELEASE"
        helm upgrade "$HELM_RELEASE" ./charts/todo-chart -n "$NAMESPACE" --set image.tag="$IMAGE_TAG" --wait --timeout=300s
    else
        log "Installing new release: $HELM_RELEASE"
        helm install "$HELM_RELEASE" ./charts/todo-chart -n "$NAMESPACE" --set image.tag="$IMAGE_TAG" --wait --timeout=300s
    fi

    log "${GREEN}Application deployed successfully${NC}"
}

# Verify deployment
verify_deployment() {
    log "${YELLOW}Verifying deployment...${NC}"

    # Check if deployments are ready
    kubectl wait --for=condition=Ready deployment/todo-frontend -n "$NAMESPACE" --timeout=300s || error_exit "Frontend deployment is not ready"
    kubectl wait --for=condition=Ready deployment/todo-backend -n "$NAMESPACE" --timeout=300s || error_exit "Backend deployment is not ready"

    # Check if services are available
    FRONTEND_SVC=$(kubectl get svc todo-frontend -n "$NAMESPACE" -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || echo "")
    if [[ -n "$FRONTEND_SVC" ]]; then
        log "${GREEN}Frontend service available at: $FRONTEND_SVC${NC}"
    else
        log "${YELLOW}Frontend service is not yet available (may take a few more minutes)${NC}"
    fi

    log "${GREEN}Deployment verification completed${NC}"
}

# Display deployment status
display_status() {
    log "${BLUE}=== Deployment Status ===${NC}"
    kubectl get pods -n "$NAMESPACE"
    kubectl get services -n "$NAMESPACE"
    kubectl get deployments -n "$NAMESPACE"
    log "${BLUE}=========================${NC}"
}

# Main execution
main() {
    log "${GREEN}Starting application deployment...${NC}"

    validate_prerequisites
    validate_inputs
    check_cluster_readiness
    deploy_with_helm
    verify_deployment
    display_status

    log "${GREEN}Application deployment completed successfully!${NC}"
    log "Release: $HELM_RELEASE"
    log "Namespace: $NAMESPACE"
    log "Image Tag: $IMAGE_TAG"
}

main "$@"
```

## 5. Health Check and Monitoring Scripts

### Health Check Script: `health-check.sh`

```bash
#!/bin/bash

# health-check.sh - Comprehensive health check for EKS cluster and applications

set -euo pipefail

CLUSTER_NAME="${CLUSTER_NAME:-my-todo-cluster}"
REGION="${AWS_DEFAULT_REGION:-us-east-1}"
NAMESPACE="${NAMESPACE:-default}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Status function
status_ok() {
    echo -e "${GREEN}✓ OK${NC}"
}

status_warn() {
    echo -e "${YELLOW}⚠ WARN${NC}"
}

status_error() {
    echo -e "${RED}✗ ERROR${NC}"
}

# Check cluster status
check_cluster_status() {
    log "${CYAN}Checking cluster status...${NC}"

    if aws eks describe-cluster --name "$CLUSTER_NAME" --region "$REGION" >/dev/null 2>&1; then
        STATUS=$(aws eks describe-cluster --name "$CLUSTER_NAME" --region "$REGION" --query 'cluster.status' --output text)
        if [[ "$STATUS" == "ACTIVE" ]]; then
            status_ok
        else
            echo -n " ($STATUS) "
            status_error
        fi
    else
        status_error
    fi
}

# Check node status
check_node_status() {
    log "${CYAN}Checking node status...${NC}"

    NODE_COUNT=$(kubectl get nodes --no-headers 2>/dev/null | wc -l || echo "0")
    READY_NODES=$(kubectl get nodes --no-headers 2>/dev/null | grep " Ready " | wc -l || echo "0")

    if [[ "$NODE_COUNT" -gt 0 && "$READY_NODES" -eq "$NODE_COUNT" ]]; then
        echo -n " ($READY_NODES/$NODE_COUNT ready) "
        status_ok
    elif [[ "$NODE_COUNT" -gt 0 ]]; then
        echo -n " ($READY_NODES/$NODE_COUNT ready) "
        status_warn
    else
        status_error
    fi
}

# Check pod status
check_pod_status() {
    log "${CYAN}Checking pod status in $NAMESPACE...${NC}"

    TOTAL_PODS=$(kubectl get pods -n "$NAMESPACE" --no-headers 2>/dev/null | wc -l || echo "0")
    RUNNING_PODS=$(kubectl get pods -n "$NAMESPACE" --no-headers 2>/dev/null | grep -c "Running" || echo "0")
    FAILED_PODS=$(kubectl get pods -n "$NAMESPACE" --no-headers 2>/dev/null | grep -c -E "(CrashLoopBackOff|Error|Failed)" || echo "0")

    if [[ "$TOTAL_PODS" -gt 0 && "$RUNNING_PODS" -eq "$TOTAL_PODS" && "$FAILED_PODS" -eq 0 ]]; then
        echo -n " ($RUNNING_PODS/$TOTAL_PODS running) "
        status_ok
    elif [[ "$TOTAL_PODS" -gt 0 ]]; then
        echo -n " ($RUNNING_PODS/$TOTAL_PODS running, $FAILED_PODS failed) "
        status_warn
    else
        status_error
    fi
}

# Check service status
check_service_status() {
    log "${CYAN}Checking service status in $NAMESPACE...${NC}"

    SERVICES=$(kubectl get services -n "$NAMESPACE" --no-headers 2>/dev/null | wc -l || echo "0")
    if [[ "$SERVICES" -gt 0 ]]; then
        status_ok
        # Show service details
        kubectl get services -n "$NAMESPACE" --no-headers | while read -r line; do
            NAME=$(echo "$line" | awk '{print $1}')
            TYPE=$(echo "$line" | awk '{print $2}')
            EXTERNAL_IP=$(echo "$line" | awk '{print $4}')
            PORTS=$(echo "$line" | awk '{print $5}')

            if [[ "$TYPE" == "LoadBalancer" && "$EXTERNAL_IP" != "<pending>" ]]; then
                echo "    ${GREEN}✓$NC $NAME - $EXTERNAL_IP:$PORTS"
            elif [[ "$TYPE" == "LoadBalancer" && "$EXTERNAL_IP" == "<pending>" ]]; then
                echo "    ${YELLOW}⚠$NC $NAME - LoadBalancer pending"
            else
                echo "    ✓ $NAME - $TYPE ($PORTS)"
            fi
        done
    else
        status_error
    fi
}

# Check deployment status
check_deployment_status() {
    log "${CYAN}Checking deployment status in $NAMESPACE...${NC}"

    kubectl get deployments -n "$NAMESPACE" --no-headers 2>/dev/null | while read -r line; do
        NAME=$(echo "$line" | awk '{print $1}')
        READY=$(echo "$line" | awk '{print $2}')
        UP_TO_DATE=$(echo "$line" | awk '{print $3}')
        AVAILABLE=$(echo "$line" | awk '{print $4}')

        if [[ "$READY" == "$UP_TO_DATE" && "$AVAILABLE" == "${READY%/*}" ]]; then
            echo "    ${GREEN}✓$NC $NAME - $READY/$READY ready"
        else
            echo "    ${YELLOW}⚠$NC $NAME - $READY ready, $UP_TO_DATE up-to-date, $AVAILABLE available"
        fi
    done
}

# Check resource utilization
check_resource_utilization() {
    log "${CYAN}Checking resource utilization...${NC}"

    if command -v kubectl >/dev/null 2>&1 && kubectl top nodes >/dev/null 2>&1; then
        kubectl top nodes | while read -r line; do
            echo "    $line"
        done
        echo ""

        kubectl top pods -n "$NAMESPACE" 2>/dev/null | while read -r line; do
            echo "    $line"
        done
    else
        echo "    Metrics server not available or insufficient permissions"
        status_warn
    fi
}

# Run all health checks
run_health_checks() {
    log "${PURPLE}=== EKS Health Check Report ===${NC}"
    log "Cluster: $CLUSTER_NAME"
    log "Region: $REGION"
    log "Namespace: $NAMESPACE"
    log "${PURPLE}================================${NC}"

    check_cluster_status
    check_node_status
    check_pod_status
    check_service_status
    check_deployment_status
    check_resource_utilization

    log "${PURPLE}=== Health Check Complete ===${NC}"
}

# Main execution
main() {
    run_health_checks
}

main "$@"
```

## 6. Cleanup and Maintenance Scripts

### Cleanup Script: `cleanup.sh`

```bash
#!/bin/bash

# cleanup.sh - Cleanup resources and prepare for next deployment

set -euo pipefail

CLUSTER_NAME="${CLUSTER_NAME:-my-todo-cluster}"
NAMESPACE="${NAMESPACE:-default}"
CLEANUP_OLD_IMAGES="${CLEANUP_OLD_IMAGES:-false}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Error handling
error_exit() {
    log "${RED}ERROR: $1${NC}" >&2
    exit 1
}

# Cleanup pods
cleanup_pods() {
    log "${YELLOW}Cleaning up pods in $NAMESPACE...${NC}"

    # Delete all pods in the namespace
    kubectl delete pods --all -n "$NAMESPACE" --grace-period=0 --force 2>/dev/null || true
    log "${GREEN}Pods cleaned up${NC}"
}

# Cleanup services
cleanup_services() {
    log "${YELLOW}Cleaning up services in $NAMESPACE...${NC}"

    # Delete all services in the namespace
    kubectl delete services --all -n "$NAMESPACE" 2>/dev/null || true
    log "${GREEN}Services cleaned up${NC}"
}

# Cleanup deployments
cleanup_deployments() {
    log "${YELLOW}Cleaning up deployments in $NAMESPACE...${NC}"

    # Delete all deployments in the namespace
    kubectl delete deployments --all -n "$NAMESPACE" 2>/dev/null || true
    log "${GREEN}Deployments cleaned up${NC}"
}

# Cleanup Helm releases
cleanup_helm_releases() {
    log "${YELLOW}Cleaning up Helm releases...${NC}"

    # List and delete all Helm releases in the namespace
    helm list -n "$NAMESPACE" --short | while read -r release; do
        if [[ -n "$release" ]]; then
            log "Deleting Helm release: $release"
            helm uninstall "$release" -n "$NAMESPACE" 2>/dev/null || true
        fi
    done

    log "${GREEN}Helm releases cleaned up${NC}"
}

# Cleanup old images from ECR
cleanup_ecr_images() {
    if [[ "$CLEANUP_OLD_IMAGES" == "true" ]]; then
        log "${YELLOW}Cleaning up old images from ECR...${NC}"

        # Get ECR repositories for the application
        REPOS=("todo-frontend" "todo-backend")

        for repo in "${REPOS[@]}"; do
            if aws ecr describe-repositories --repository-names "$repo" >/dev/null 2>&1; then
                # List all image digests except the latest
                IMAGES_TO_DELETE=$(aws ecr list-images --repository-name "$repo" --query 'imageIds[1:].imageDigest' --output text)

                if [[ -n "$IMAGES_TO_DELETE" ]]; then
                    # Delete old images
                    for digest in $IMAGES_TO_DELETE; do
                        aws ecr batch-delete-image --repository-name "$repo" --image-ids imageDigest="$digest" 2>/dev/null || true
                    done
                    log "Deleted old images from $repo"
                fi
            fi
        done

        log "${GREEN}ECR images cleaned up${NC}"
    else
        log "${YELLOW}Skipping ECR image cleanup (set CLEANUP_OLD_IMAGES=true to enable)${NC}"
    fi
}

# Cleanup system namespaces
cleanup_system_resources() {
    log "${YELLOW}Cleaning up system resources...${NC}"

    # Clean up any leftover load balancers
    LB_NAMES=$(aws elb describe-load-balancers --query 'LoadBalancerDescriptions[?contains(LoadBalancerName, `-$CLUSTER_NAME-`) ].LoadBalancerName' --output text 2>/dev/null || true)
    if [[ -n "$LB_NAMES" ]]; then
        for lb in $LB_NAMES; do
            log "Deleting load balancer: $lb"
            aws elb delete-load-balancer --load-balancer-name "$lb" 2>/dev/null || true
        done
    fi

    # Clean up ALBs
    ALB_ARNS=$(aws elbv2 describe-load-balancers --query 'LoadBalancers[?contains(LoadBalancerArn, `$CLUSTER_NAME`) ].LoadBalancerArn' --output text 2>/dev/null || true)
    if [[ -n "$ALB_ARNS" ]]; then
        for arn in $ALB_ARNS; do
            log "Deleting ALB: $arn"
            aws elbv2 delete-load-balancer --load-balancer-arn "$arn" 2>/dev/null || true
        done
    fi

    log "${GREEN}System resources cleaned up${NC}"
}

# Main execution
main() {
    log "${GREEN}Starting cleanup process...${NC}"

    cleanup_helm_releases
    cleanup_deployments
    cleanup_services
    cleanup_pods
    cleanup_ecr_images
    cleanup_system_resources

    log "${GREEN}Cleanup completed successfully!${NC}"
}

main "$@"
```

## 7. Best Practices Documentation

### Deployment Best Practices

1. **Environment Variables**: Use environment variables for configuration instead of hardcoded values
2. **Secrets Management**: Never store secrets in plain text; use AWS Secrets Manager or Kubernetes secrets
3. **Rolling Updates**: Use rolling update strategies to ensure zero-downtime deployments
4. **Health Checks**: Implement both liveness and readiness probes for applications
5. **Resource Limits**: Set appropriate CPU and memory limits for containers
6. **Backup Strategy**: Regularly backup critical data and configurations
7. **Security Scanning**: Scan container images for vulnerabilities before deployment

### Security Best Practices

1. **Least Privilege**: Grant minimal required permissions to services and users
2. **Network Policies**: Implement network policies to restrict traffic between pods
3. **Pod Security Standards**: Use restrictive pod security standards
4. **IAM Roles**: Use IAM roles for service accounts instead of access keys
5. **Encryption**: Enable encryption for data at rest and in transit
6. **Audit Logging**: Enable and monitor audit logs for security events

## 8. Testing Checklist

Complete these deployment script validation steps:

```bash
# Make scripts executable
chmod +x cluster-up.sh cluster-down.sh deploy-app.sh health-check.sh cleanup.sh

# Test cluster creation (dry run with different name)
CLUSTER_NAME=test-cluster ./cluster-up.sh

# Test health check
./health-check.sh

# Test deployment
IMAGE_TAG=latest ./deploy-app.sh

# Test cleanup
./cleanup.sh

# Test cluster deletion
./cluster-down.sh
```

## 9. Troubleshooting

### Common Deployment Issues
- **Insufficient permissions**: Verify IAM roles and policies
- **Resource limits exceeded**: Check AWS service quotas
- **Network connectivity**: Verify VPC and security group configurations
- **Image pull failures**: Check ECR repository permissions
- **Service startup timeouts**: Adjust health check parameters

### Performance Optimization
- Use spot instances for non-critical workloads
- Implement horizontal pod autoscaling
- Optimize container images for size
- Use CDN for static assets
- Implement caching strategies

## 10. Research Notes

### Infrastructure as Code Benefits
Using scripts for infrastructure management provides consistency, repeatability, and version control for your deployment processes.

### Automated Operations
Scripted deployments enable reliable, repeatable operations that can be integrated into CI/CD pipelines for continuous delivery.

### Cost Optimization
Automated cleanup and resource management help optimize costs by removing unused resources and rightsizing infrastructure.