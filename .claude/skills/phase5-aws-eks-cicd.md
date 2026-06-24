# Phase V – AWS EKS CI/CD Pipeline (Hackathon II)

## 1. Overview

This phase establishes a continuous integration and continuous deployment (CI/CD) pipeline for your EKS-hosted full-stack application. The pipeline automates the process of building, testing, and deploying your Next.js frontend and FastAPI backend applications to AWS EKS.

### CI/CD Pipeline Architecture Description
```
Code Commit/Push -> GitHub Actions -> Build Docker Images -> Push to ECR -> Deploy to EKS -> Run Tests -> Notify
     |                  |                   |                    |                |           |         |
   PR/Master       Automated Build     Container Registry   Kubernetes      Quality Gate   Slack/Discord
   Branch          Security Scans      Vulnerability Scan   Deployment      Validation    Notifications
```

## 2. Prerequisites

Before implementing the CI/CD pipeline:

- GitHub repository with Next.js + FastAPI code
- AWS account with necessary permissions
- GitHub Actions enabled
- EKS cluster already created
- ECR repositories for frontend and backend
- AWS CLI configured for programmatic access
- Basic understanding of GitHub Actions workflow syntax

## 3. GitHub Actions Workflow Setup

### Create GitHub Actions Directory Structure
```bash
mkdir -p .github/workflows
```

### Main Deployment Workflow
Create `.github/workflows/deploy-to-eks.yml`:

```yaml
name: Deploy to EKS

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

env:
  AWS_REGION: us-east-1
  ECR_REPOSITORY_FRONTEND: todo-frontend
  ECR_REPOSITORY_BACKEND: todo-backend
  CLUSTER_NAME: my-cluster
  CONTAINER_PORT: 80

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'

    - name: Install frontend dependencies
      run: |
        cd frontend
        npm ci

    - name: Run frontend tests
      run: |
        cd frontend
        npm test

    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Install backend dependencies
      run: |
        cd backend
        pip install -r requirements.txt

    - name: Run backend tests
      run: |
        cd backend
        python -m pytest tests/

  build-and-push:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - name: Checkout
      uses: actions/checkout@v3

    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: ${{ env.AWS_REGION }}

    - name: Login to Amazon ECR
      id: login-ecr
      uses: aws-actions/amazon-ecr-login@v1

    - name: Build, tag, and push frontend image to ECR
      id: build-frontend
      env:
        ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
        IMAGE_TAG: ${{ github.sha }}
      run: |
        cd frontend
        docker build -t $ECR_REGISTRY/$ECR_REPOSITORY_FRONTEND:$IMAGE_TAG .
        docker push $ECR_REGISTRY/$ECR_REPOSITORY_FRONTEND:$IMAGE_TAG
        echo "image=$ECR_REGISTRY/$ECR_REPOSITORY_FRONTEND:$IMAGE_TAG" >> $GITHUB_OUTPUT

    - name: Build, tag, and push backend image to ECR
      id: build-backend
      env:
        ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
        IMAGE_TAG: ${{ github.sha }}
      run: |
        cd backend
        docker build -t $ECR_REGISTRY/$ECR_REPOSITORY_BACKEND:$IMAGE_TAG .
        docker push $ECR_REGISTRY/$ECR_REPOSITORY_BACKEND:$IMAGE_TAG
        echo "image=$ECR_REGISTRY/$ECR_REPOSITORY_BACKEND:$IMAGE_TAG" >> $GITHUB_OUTPUT

    - name: Update K8s deployment files
      run: |
        sed -i 's|YOUR_FRONTEND_IMAGE|${{ steps.build-frontend.outputs.image }}|g' k8s/frontend-deployment.yaml
        sed -i 's|YOUR_BACKEND_IMAGE|${{ steps.build-backend.outputs.image }}|g' k8s/backend-deployment.yaml

    - name: Upload updated manifests
      uses: actions/upload-artifact@v3
      with:
        name: k8s-manifests
        path: k8s/

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    steps:
    - name: Download manifests
      uses: actions/download-artifact@v3
      with:
        name: k8s-manifests
        path: k8s/

    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: ${{ env.AWS_REGION }}

    - name: Install kubectl
      run: |
        curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
        sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

    - name: Configure kubectl
      run: |
        aws eks update-kubeconfig --name ${{ env.CLUSTER_NAME }} --region ${{ env.AWS_REGION }}

    - name: Deploy to EKS
      run: |
        kubectl apply -f k8s/

    - name: Verify deployment
      run: |
        kubectl rollout status deployment/todo-frontend
        kubectl rollout status deployment/todo-backend
```

## 4. Security Scanning Integration

### Add Container Security Scanning
Update the workflow to include security scanning:

```yaml
    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'image'
        image-ref: ${{ steps.build-frontend.outputs.image }}
        format: 'sarif'
        output: 'trivy-frontend-results.sarif'

    - name: Upload Trivy scan results to GitHub Security tab
      uses: github/codeql-action/upload-sarif@v2
      if: always()
      with:
        sarif_file: 'trivy-frontend-results.sarif'
```

### Add Infrastructure as Code Security Scanning
```yaml
    - name: Run Conftest on Kubernetes manifests
      run: |
        wget https://github.com/open-policy-agent/conftest/releases/download/v0.38.0/conftest_0.38.0_Linux_x86_64.tar.gz
        tar -xzf conftest_0.38.0_Linux_x86_64.tar.gz
        ./conftest test k8s/*.yaml
```

## 5. Environment-Specific Deployments

### Create Environment Configurations
Create separate workflow files for different environments:

#### Staging Environment: `.github/workflows/deploy-staging.yml`
```yaml
name: Deploy to Staging EKS

on:
  push:
    branches: [ develop ]

env:
  AWS_REGION: us-east-1
  ECR_REPOSITORY_FRONTEND: todo-frontend-staging
  ECR_REPOSITORY_BACKEND: todo-backend-staging
  CLUSTER_NAME: my-staging-cluster

# Similar job structure as main deployment but with staging-specific configurations
```

#### Production Environment: `.github/workflows/deploy-production.yml`
```yaml
name: Deploy to Production EKS

on:
  push:
    tags: ['v*']

env:
  AWS_REGION: us-east-1
  ECR_REPOSITORY_FRONTEND: todo-frontend
  ECR_REPOSITORY_BACKEND: todo-backend
  CLUSTER_NAME: my-prod-cluster

# Similar job structure but only triggered on version tags
```

## 6. Helm-Based Deployment Pipeline

### Update Workflow for Helm Deployments
```yaml
  deploy-with-helm:
    needs: build-and-push
    runs-on: ubuntu-latest
    steps:
    - name: Checkout
      uses: actions/checkout@v3

    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: ${{ env.AWS_REGION }}

    - name: Install kubectl
      run: |
        curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
        sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

    - name: Install Helm
      run: |
        curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
        chmod 700 get_helm.sh
        ./get_helm.sh

    - name: Configure kubectl
      run: |
        aws eks update-kubeconfig --name ${{ env.CLUSTER_NAME }} --region ${{ env.AWS_REGION }}

    - name: Update Helm values with image tags
      run: |
        sed -i 's|image.tag: "latest"|image.tag: "${{ github.sha }}"|g' helm/values.yaml

    - name: Deploy with Helm
      run: |
        helm upgrade --install todo-app ./helm --values helm/values.yaml --wait --atomic
```

## 7. Automated Testing in Pipeline

### Add End-to-End Tests
```yaml
  e2e-tests:
    needs: deploy
    runs-on: ubuntu-latest
    steps:
    - name: Checkout
      uses: actions/checkout@v3

    - name: Wait for deployment to be ready
      run: |
        kubectl wait --for=condition=ready pod -l app=todo-frontend --timeout=300s
        kubectl wait --for=condition=ready pod -l app=todo-backend --timeout=300s

    - name: Run E2E tests
      run: |
        cd tests
        npm install
        npm run test:e2e
```

### Health Check Integration
```yaml
  health-check:
    needs: deploy
    runs-on: ubuntu-latest
    steps:
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: ${{ env.AWS_REGION }}

    - name: Configure kubectl
      run: |
        aws eks update-kubeconfig --name ${{ env.CLUSTER_NAME }} --region ${{ env.AWS_REGION }}

    - name: Check service endpoints
      run: |
        FRONTEND_IP=$(kubectl get svc todo-frontend -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
        BACKEND_IP=$(kubectl get svc todo-backend -o jsonpath='{.spec.clusterIP}')

        # Test frontend health
        curl -f http://${FRONTEND_IP}/health || exit 1
        # Test backend health
        curl -f http://${BACKEND_IP}:8000/health || exit 1
```

## 8. Notification and Monitoring Setup

### Slack Notifications
Add to workflow:
```yaml
  notify:
    needs: [deploy, e2e-tests]
    runs-on: ubuntu-latest
    if: always()
    steps:
    - name: Notify Slack on Success
      if: ${{ needs.deploy.result == 'success' && needs.e2e-tests.result == 'success' }}
      uses: 8398a7/action-slack@v3
      with:
        status: success
        text: '✅ Deployment to EKS succeeded!'
        webhook_url: ${{ secrets.SLACK_WEBHOOK_URL }}

    - name: Notify Slack on Failure
      if: ${{ contains(needs.*.result, 'failure') }}
      uses: 8398a7/action-slack@v3
      with:
        status: failure
        text: '❌ Deployment to EKS failed! Check logs.'
        webhook_url: ${{ secrets.SLACK_WEBHOOK_URL }}
```

## 9. Manual Approval Gates

### Add Manual Approval for Production
```yaml
  manual-approval:
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    steps:
    - name: Manual approval
      uses: trstringer/manual-approval@v1
      with:
        secret: ${{ github.TOKEN }}
        approvers: user1,user2
        minimum-approvals: 1
        issue-title: 'Production deployment approval for ${{ github.sha }}'
        issue-body: 'Please approve the production deployment for commit ${{ github.sha }}'
```

## 10. Testing Checklist

Complete these CI/CD validation steps:

```bash
# Test the workflow locally with act
act -j test
act -j build-and-push

# Verify GitHub secrets are properly set
# AWS_ACCESS_KEY_ID
# AWS_SECRET_ACCESS_KEY
# SLACK_WEBHOOK_URL

# Check workflow syntax
yamllint .github/workflows/

# Test manual trigger
gh workflow run "Deploy to EKS" --ref main

# Verify deployment automation
kubectl get events --sort-by='.lastTimestamp'
```

## 11. Troubleshooting

### Common CI/CD Issues
- **Authentication failures**: Verify AWS credentials in GitHub secrets
- **Image pull errors**: Check ECR repository permissions and image tagging
- **Kubernetes deployment failures**: Review deployment manifest syntax
- **Timeout errors**: Increase timeout values for slow operations

### Pipeline Optimization Tips
- Use caching for dependencies to speed up builds
- Implement parallel jobs for independent tasks
- Use matrix builds for multi-environment testing
- Set up proper cleanup of old container images

### Security Considerations
- Rotate AWS credentials regularly
- Use minimal IAM permissions for CI/CD role
- Encrypt sensitive data in workflow files
- Monitor for credential leaks in logs

## 12. Research Notes

### GitOps Principles
The CI/CD pipeline implements GitOps principles where the desired state of the infrastructure is stored in Git. Changes to the application or infrastructure are made through pull requests, providing audit trails and enabling easy rollbacks.

### Immutable Infrastructure
Using container images ensures that each deployment creates immutable infrastructure components. This eliminates configuration drift and makes deployments predictable and repeatable.

### Progressive Delivery
Consider implementing progressive delivery strategies like blue-green deployments or canary releases to reduce deployment risk and improve application availability during updates.