# Kubernetes-Native Deployment Intelligence

## Skill Name
Kubernetes-Native Application Design and Deployment

## Scope
Apply Kubernetes-native patterns for container orchestration, resource management, configuration, scaling, and deployment strategies.

## Trigger Conditions

Apply this skill when:
- Designing microservices for Kubernetes deployment
- Creating deployment manifests or Helm charts
- Configuring environment-specific settings
- Implementing health checks and readiness probes
- Managing secrets and configuration
- Planning resource allocation and limits
- Implementing scaling strategies
- Designing for high availability

## Core Intelligence Rules

### 1. Helm-First Deployment Strategy
**Rule**: Use Helm charts as the primary deployment mechanism, not raw YAML manifests.

**Rationale**:
- Templating for multi-environment deployment
- Version control for releases
- Rollback capability
- Dependency management
- Values-driven configuration

**Chart Structure**:
```
charts/{service-name}/
  Chart.yaml              # Metadata
  values.yaml             # Default values
  values-dev.yaml         # Dev overrides
  values-prod.yaml        # Prod overrides
  templates/
    deployment.yaml
    service.yaml
    configmap.yaml
    secret.yaml
    hpa.yaml
```

**Deployment Pattern**:
```bash
# Dev
helm upgrade --install {release} ./charts/{service} -f values-dev.yaml -n {namespace}

# Prod
helm upgrade --install {release} ./charts/{service} -f values-prod.yaml -n {namespace}
```

### 2. Environment Parity Principle
**Rule**: Local (Minikube) → Staging → Production should use identical Helm charts with different values files.

**Parity Requirements**:
- Same container images (different tags)
- Same Kubernetes resources (different replicas/limits)
- Same Helm chart (different values)
- Same Dapr components (different backends)

**Differences via Values**:
```yaml
# values-dev.yaml
replicaCount: 1
resources:
  limits:
    memory: 512Mi
    cpu: 500m

# values-prod.yaml
replicaCount: 3
resources:
  limits:
    memory: 2Gi
    cpu: 2000m
```

### 3. Namespace Isolation Strategy
**Rule**: Use namespaces to isolate environments and enforce resource boundaries.

**Namespace Pattern**:
```
{app-name}-{environment}

Examples:
- todo-app-dev
- todo-app-staging
- todo-app-prod
```

**Benefits**:
- Resource quotas per environment
- RBAC isolation
- Network policies
- Cost tracking

**Resource Quota Example**:
```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: dev-quota
  namespace: todo-app-dev
spec:
  hard:
    requests.cpu: "4"
    requests.memory: 8Gi
    persistentvolumeclaims: "5"
```

### 4. Sidecar Injection Pattern
**Rule**: Use annotations for automatic sidecar injection (Dapr, Istio), not manual container definitions.

**Dapr Sidecar Injection**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  annotations:
    dapr.io/enabled: "true"
    dapr.io/app-id: "api-service"
    dapr.io/app-port: "8000"
    dapr.io/log-level: "info"
    dapr.io/enable-metrics: "true"
spec:
  template:
    spec:
      containers:
      - name: api-service
        # Dapr sidecar automatically injected
```

**Enforcement**:
- Never manually define sidecar containers
- Use operator/webhook for injection
- Configure via annotations

### 5. ConfigMap and Secret Management
**Rule**: Externalize all configuration. Never hardcode in container images.

**Configuration Hierarchy**:
```
1. Environment variables (from ConfigMap/Secret)
2. Volume mounts (for files)
3. Application defaults (fallback only)
```

**ConfigMap Pattern**:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: api-service-config
data:
  LOG_LEVEL: "info"
  DATABASE_POOL_SIZE: "10"
```

**Secret Pattern**:
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: api-service-secrets
type: Opaque
stringData:
  DATABASE_URL: "postgresql://..."
```

**Consumption**:
```yaml
env:
- name: LOG_LEVEL
  valueFrom:
    configMapKeyRef:
      name: api-service-config
      key: LOG_LEVEL
- name: DATABASE_URL
  valueFrom:
    secretKeyRef:
      name: api-service-secrets
      key: DATABASE_URL
```

### 6. Health Probes Design
**Rule**: Implement liveness, readiness, and startup probes for all services.

**Probe Types**:
- **Startup**: One-time check during initialization (slow starts)
- **Liveness**: Service is alive (restart if fails)
- **Readiness**: Service can handle traffic (remove from load balancer if fails)

**Implementation Pattern**:
```yaml
livenessProbe:
  httpGet:
    path: /health/live
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /health/ready
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 3

startupProbe:
  httpGet:
    path: /health/startup
    port: 8000
  initialDelaySeconds: 0
  periodSeconds: 5
  failureThreshold: 30  # 150 seconds max startup
```

**Endpoint Logic**:
```
/health/live   → Always returns 200 unless app is deadlocked
/health/ready  → Returns 200 only if DB connected, dependencies ready
/health/startup → Returns 200 after initialization complete
```

### 7. Resource Requests and Limits
**Rule**: Always set resource requests and limits. Prevent noisy neighbor problems.

**Pattern**:
```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

**Guidelines**:
- **Requests**: Minimum guaranteed resources (scheduling)
- **Limits**: Maximum allowed resources (throttling/OOMKill)
- **Ratio**: limits = 1.5x to 2x requests
- **QoS Class**: Guaranteed (requests == limits) > Burstable > BestEffort

**Sizing Strategy**:
```
1. Start conservative (256Mi/250m)
2. Monitor actual usage
3. Adjust based on p95 usage
4. Set limits 50-100% above p95
```

### 8. Horizontal Pod Autoscaling
**Rule**: Use HPA for traffic-based scaling, VPA for resource optimization.

**HPA Pattern**:
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-service-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-service
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
```

**Scaling Triggers**:
- CPU > 70%: Scale up
- Memory > 80%: Scale up (if memory-bound)
- Custom metrics: Queue depth, request latency

### 9. Rolling Update Strategy
**Rule**: Use rolling updates with proper surge and unavailability settings.

**Deployment Strategy**:
```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1        # 1 extra pod during update
    maxUnavailable: 0  # No downtime
```

**Guidelines**:
- **maxUnavailable: 0** for zero-downtime deployments
- **maxSurge: 1** for resource-constrained environments
- **maxSurge: 25%** for faster rollouts with resources
- Include readiness probes to prevent routing to unready pods

### 10. Persistent Volume Strategy
**Rule**: Use StatefulSets for stateful workloads, Deployments for stateless.

**When to Use StatefulSets**:
- Databases (PostgreSQL, Redis)
- Message brokers (Kafka)
- Ordered deployment/scaling required
- Stable network identity needed

**When to Use Deployments**:
- Stateless APIs
- Workers
- Frontends
- Any service where pods are interchangeable

**PVC Pattern** (for StatefulSets):
```yaml
volumeClaimTemplates:
- metadata:
    name: data
  spec:
    accessModes: [ "ReadWriteOnce" ]
    storageClassName: "standard"
    resources:
      requests:
        storage: 10Gi
```

## Anti-Patterns to Avoid

### ❌ Raw YAML Deployments
**Anti-Pattern**: Manually applying individual YAML files for each environment.
**Fix**: Use Helm charts with values files.

### ❌ No Resource Limits
**Anti-Pattern**: Deploying without CPU/memory limits.
**Fix**: Always set requests and limits.

### ❌ Missing Health Probes
**Anti-Pattern**: No liveness or readiness probes.
**Fix**: Implement all three probe types.

### ❌ Hardcoded Configuration
**Anti-Pattern**: Environment variables hardcoded in Deployment YAML.
**Fix**: Use ConfigMaps and Secrets.

### ❌ Single Replica in Production
**Anti-Pattern**: `replicas: 1` in production.
**Fix**: Minimum 2 replicas for availability.

### ❌ No Graceful Shutdown
**Anti-Pattern**: Pods killed immediately, requests dropped.
**Fix**: Handle SIGTERM, drain connections, respect terminationGracePeriodSeconds.

### ❌ Latest Tag in Production
**Anti-Pattern**: `image: api-service:latest`
**Fix**: Use semantic versioning `image: api-service:1.2.3`

### ❌ Privileged Containers
**Anti-Pattern**: `securityContext.privileged: true` unnecessarily.
**Fix**: Use least privilege, run as non-root.

### ❌ Ignoring Pod Disruption Budgets
**Anti-Pattern**: No PDB, cluster maintenance causes downtime.
**Fix**: Define PDB for critical services.

## Decision Heuristics

### Namespace Strategy
```
IF single application with multiple environments:
   Use {app-name}-{environment} namespaces
ELSE IF multi-tenant platform:
   Use {tenant-id} or {team-name} namespaces
ELSE IF microservices platform:
   Group by domain: {domain}-{environment}
```

### Replica Count
```
IF production:
   minReplicas: 2 (for availability)
   maxReplicas: 10+ (based on load testing)
ELSE IF staging:
   minReplicas: 1
   maxReplicas: 3
ELSE IF dev:
   replicas: 1 (no HPA)
```

### Resource Allocation
```
IF CPU-bound (video processing, ML):
   cpu requests == limits (Guaranteed QoS)
ELSE IF memory-bound (caching, in-memory):
   memory requests == limits
ELSE (typical web service):
   Burstable QoS (requests < limits)
```

### Storage Class Selection
```
IF database (high IOPS needed):
   storageClassName: "premium-ssd"
ELSE IF cache (ephemeral acceptable):
   Use emptyDir volume
ELSE (logs, temp files):
   storageClassName: "standard"
```

### Service Type Selection
```
IF internal service (backend, database):
   type: ClusterIP
ELSE IF needs load balancer:
   type: LoadBalancer (cloud) or Ingress
ELSE IF node-level access needed:
   type: NodePort
```

## Helm Chart Best Practices

### Values File Structure
```yaml
# Global settings
global:
  environment: production
  registry: docker.io/myorg

# Service-specific
replicaCount: 3
image:
  repository: api-service
  tag: 1.2.3
  pullPolicy: IfNotPresent

resources:
  requests:
    cpu: 250m
    memory: 256Mi
  limits:
    cpu: 500m
    memory: 512Mi

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70

config:
  LOG_LEVEL: info
  DATABASE_POOL_SIZE: 10

secrets:
  DATABASE_URL: ""  # Set via --set or separate secrets file
```

### Template Patterns
```yaml
# Use conditionals
{{- if .Values.autoscaling.enabled }}
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
{{- end }}

# Use helpers
{{- include "api-service.fullname" . }}

# Use values with defaults
{{ .Values.replicaCount | default 1 }}
```

### Pre-Install/Pre-Upgrade Hooks
```yaml
# Run database migrations before deployment
apiVersion: batch/v1
kind: Job
metadata:
  annotations:
    "helm.sh/hook": pre-upgrade,pre-install
    "helm.sh/hook-weight": "1"
    "helm.sh/hook-delete-policy": before-hook-creation
spec:
  template:
    spec:
      containers:
      - name: migrate
        image: {{ .Values.image.repository }}:{{ .Values.image.tag }}
        command: ["alembic", "upgrade", "head"]
```

## Validation Checklist

Before deploying to Kubernetes:
- [ ] Helm chart created with templates
- [ ] Values files for each environment
- [ ] Resource requests and limits set
- [ ] Liveness and readiness probes configured
- [ ] Configuration externalized to ConfigMaps
- [ ] Secrets managed via Kubernetes Secrets or external vault
- [ ] Minimum 2 replicas in production
- [ ] HPA configured for scalable services
- [ ] Rolling update strategy with maxUnavailable: 0
- [ ] Container runs as non-root user
- [ ] Image uses semantic version tag (not latest)
- [ ] Pod Disruption Budget defined for critical services
- [ ] Namespace and RBAC configured
- [ ] Network policies defined (if security required)
- [ ] Monitoring and logging configured
