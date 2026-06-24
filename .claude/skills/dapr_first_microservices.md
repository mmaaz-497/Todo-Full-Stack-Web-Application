# Dapr-First Microservices Intelligence

## Skill Name
Dapr-First Microservices Architecture and Abstraction

## Scope
Apply Dapr as the default abstraction layer for distributed application concerns: pub/sub, state management, service invocation, secrets, observability, and scheduling.

## Trigger Conditions

Apply this skill when:
- Building microservices that need to communicate
- Implementing pub/sub messaging
- Managing distributed state
- Storing or retrieving secrets
- Scheduling background jobs or cron tasks
- Invoking services across network boundaries
- Adding observability to distributed systems
- Designing for cloud portability

## Core Intelligence Rules

### 1. Abstraction Over Implementation
**Rule**: Use Dapr building blocks, not vendor-specific SDKs. The application should not know if it's using Kafka, RabbitMQ, Redis, or PostgreSQL.

**Decision Matrix**:
```
Need to...                  → Use Dapr Building Block       → NOT vendor SDK
Publish event               → Dapr Pub/Sub                  → NOT Kafka client
Store state                 → Dapr State API                → NOT Redis client
Call another service        → Dapr Service Invocation       → NOT HTTP client with hardcoded URL
Access secret               → Dapr Secrets API              → NOT cloud-specific KMS
Schedule job                → Dapr Jobs API                 → NOT cron or cloud scheduler
Observe traces              → Dapr middleware (auto)        → NOT manual instrumentation
```

**Benefit**: Swap infrastructure without changing application code.

### 2. Sidecar Architecture Pattern
**Rule**: Every application container has a Dapr sidecar container. Application calls localhost:3500 (HTTP) or localhost:50001 (gRPC).

**Kubernetes Deployment Pattern**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  annotations:
    dapr.io/enabled: "true"
    dapr.io/app-id: "api-service"
    dapr.io/app-port: "8000"
    dapr.io/log-level: "info"
spec:
  template:
    spec:
      containers:
      - name: api-service
        # Dapr sidecar injected automatically
```

**Enforcement**:
- Application NEVER talks directly to Kafka, Redis, etc.
- Application ONLY talks to localhost Dapr sidecar
- Dapr sidecar talks to infrastructure
- Configuration lives in Dapr components, not application code

### 3. Component-Driven Configuration
**Rule**: Infrastructure choices are Dapr component YAML files, not application code.

**Component Structure**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "kafka-cluster:9092"
```

**Swap Example**:
```
Local:      type: pubsub.redis
Cloud:      type: pubsub.kafka
Azure:      type: pubsub.azure.servicebus
```

**Application code stays identical.**

### 4. Dapr Pub/Sub Pattern
**Rule**: Publish events via Dapr HTTP API, not native Kafka/RabbitMQ clients.

**Publishing Pattern**:
```
POST http://localhost:3500/v1.0/publish/{pubsub-name}/{topic}
Body: { event payload }
```

**Subscribing Pattern**:
```yaml
# subscription.yaml
apiVersion: dapr.io/v2alpha1
kind: Subscription
metadata:
  name: task-events-sub
spec:
  pubsubname: kafka-pubsub
  topic: task-events
  routes:
    default: /events/task-events
```

**Benefits**:
- Automatic retries
- Dead-letter queue support
- Message tracing
- Cloud-agnostic

### 5. Dapr State Management Pattern
**Rule**: Store transient application state (sessions, cache, deduplication) in Dapr state store, not direct database.

**State API Pattern**:
```
# Save
POST http://localhost:3500/v1.0/state/{store-name}
[{ "key": "processed-events:{event_id}", "value": true }]

# Get
GET http://localhost:3500/v1.0/state/{store-name}/{key}

# Delete
DELETE http://localhost:3500/v1.0/state/{store-name}/{key}
```

**Use Cases**:
- Idempotency deduplication (7-day TTL)
- Session storage
- Distributed locks
- Rate limiting counters
- Feature flags

**NOT For**:
- Primary business data (use database directly)
- Long-term persistence (use database)

### 6. Dapr Service Invocation Pattern
**Rule**: Call other services by app-id, not hardcoded URLs or DNS names.

**Invocation Pattern**:
```
GET http://localhost:3500/v1.0/invoke/{app-id}/method/{method-name}
```

**Example**:
```
# Instead of: http://auth-service.default.svc.cluster.local:8080/validate
# Use:        http://localhost:3500/v1.0/invoke/auth-service/method/validate
```

**Benefits**:
- Service discovery (no DNS hardcoding)
- Automatic mTLS encryption
- Distributed tracing
- Retries and timeouts
- Circuit breaking

### 7. Dapr Secrets API Pattern
**Rule**: Retrieve secrets via Dapr Secrets API, not cloud-specific SDKs.

**Secrets API Pattern**:
```
GET http://localhost:3500/v1.0/secrets/{secret-store}/{secret-name}
```

**Component Example**:
```yaml
# Local: Kubernetes secrets
type: secretstores.kubernetes

# Azure: Azure Key Vault
type: secretstores.azure.keyvault

# AWS: AWS Secrets Manager
type: secretstores.aws.secretmanager
```

**Application code identical across clouds.**

### 8. Dapr Jobs API Pattern
**Rule**: Schedule recurring tasks via Dapr Jobs API, not cron or cloud-specific schedulers.

**Jobs API Pattern**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Job
metadata:
  name: recurring-task-generator
spec:
  schedule: "@every 1h"
  repeats: -1  # infinite
  data: { "action": "generate-recurring-tasks" }
  dueTime: "5m"
```

**Benefits**:
- Cloud-agnostic scheduling
- At-least-once delivery
- No infrastructure to manage
- Automatic retries

### 9. Component Scoping Strategy
**Rule**: Use namespaces or component scopes to isolate environments.

**Scoping Options**:
```yaml
# Option 1: Namespace isolation
metadata:
  namespace: todo-app-dev    # vs todo-app-prod

# Option 2: Component scoping
scopes:
- api-service
- reminder-service
```

**Enforcement**:
- Dev and prod use separate Dapr components
- Services only access components in their scope
- Secrets scoped to services that need them

### 10. Observability by Default
**Rule**: Enable Dapr observability middleware. Get traces, metrics, and logs without manual instrumentation.

**Tracing Configuration**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Configuration
metadata:
  name: tracing
spec:
  tracing:
    samplingRate: "1"
    zipkin:
      endpointAddress: "http://zipkin:9411/api/v2/spans"
```

**Automatic Instrumentation**:
- HTTP requests traced
- Pub/sub traced
- Service invocation traced
- State operations traced

**Application effort: Zero.**

## Anti-Patterns to Avoid

### ❌ Direct Infrastructure Access
**Anti-Pattern**: Using Kafka Python client directly in application.
**Fix**: Use Dapr Pub/Sub HTTP API.

### ❌ Hardcoded Service URLs
**Anti-Pattern**: `http://auth-service:8080/validate`
**Fix**: `http://localhost:3500/v1.0/invoke/auth-service/method/validate`

### ❌ Cloud-Specific SDKs in Application
**Anti-Pattern**: Using `boto3` for AWS Secrets Manager in application code.
**Fix**: Dapr Secrets API with swappable component.

### ❌ Manual Retry Logic
**Anti-Pattern**: Implementing exponential backoff in application for pub/sub.
**Fix**: Configure Dapr resiliency policies.

### ❌ Service-to-Service mTLS Implementation
**Anti-Pattern**: Managing TLS certificates manually in application.
**Fix**: Enable Dapr mTLS (automatic).

### ❌ Multiple Sidecars Per Pod
**Anti-Pattern**: Adding Envoy + Dapr + custom sidecar.
**Fix**: Use Dapr for most concerns; add others only if absolutely necessary.

### ❌ Bypassing Dapr for Performance
**Anti-Pattern**: "Dapr is slow, let's use direct Redis."
**Fix**: Profile first. Dapr overhead is typically < 1ms. Optimize Dapr config if needed.

### ❌ Storing Large State in Dapr State Store
**Anti-Pattern**: Storing 10 MB files in Dapr state.
**Fix**: Use object storage (S3, Blob) via Dapr Bindings or direct SDK.

## Decision Heuristics

### When to Use Dapr vs Direct SDK
```
IF (need cloud portability OR infrastructure might change)
   AND (Dapr building block exists for use case)
THEN use Dapr
ELSE IF (no Dapr building block AND performance critical)
THEN use direct SDK but isolate behind interface
ELSE default to Dapr
```

### Pub/Sub Choice
```
IF local development:
   Use pubsub.redis (lightweight)
ELSE IF production AND Kafka expertise available:
   Use pubsub.kafka
ELSE IF cloud-managed preferred:
   Azure → pubsub.azure.servicebus
   AWS → pubsub.aws.sns-sqs
   GCP → pubsub.gcp.pubsub
```

### State Store Choice
```
IF need transactions:
   Use statestore.postgresql
ELSE IF need TTL and high performance:
   Use statestore.redis
ELSE IF cloud-managed:
   Azure → statestore.azure.cosmosdb
   AWS → statestore.aws.dynamodb
```

### Secrets Store Choice
```
IF local/Minikube:
   Use secretstores.kubernetes
ELSE IF cloud production:
   Azure → secretstores.azure.keyvault
   AWS → secretstores.aws.secretmanager
   GCP → secretstores.gcp.secretmanager
```

### Jobs API vs Cron
```
IF recurring task AND Dapr 1.14+:
   Use Dapr Jobs API
ELSE IF complex cron expressions needed:
   Use Kubernetes CronJob (temporary, migrate to Jobs API)
ELSE:
   Use Dapr Jobs API
```

## Component Configuration Patterns

### Multi-Environment Strategy
```
environments/
  local/
    components/
      kafka-pubsub.yaml      # type: pubsub.redis
      state-store.yaml        # type: statestore.redis
  cloud/
    components/
      kafka-pubsub.yaml      # type: pubsub.kafka
      state-store.yaml        # type: statestore.postgresql
```

### Naming Convention
```
{purpose}-{type}.yaml

Examples:
- kafka-pubsub.yaml
- redis-state.yaml
- postgres-state.yaml
- keyvault-secrets.yaml
```

### Version Pinning
```yaml
spec:
  type: pubsub.kafka
  version: v1  # Pin version for stability
```

## Resiliency Policies

### Default Resiliency Policy
```yaml
apiVersion: dapr.io/v1alpha1
kind: Resiliency
metadata:
  name: default
spec:
  policies:
    retries:
      pubsubRetry:
        policy: exponential
        maxRetries: 3
        maxInterval: 30s
    timeouts:
      general:
        timeout: 10s
  targets:
    apps:
      api-service:
        retry: pubsubRetry
        timeout: general
```

**Apply by default for**:
- Pub/Sub publishing
- Service invocation
- State operations

## Migration Path from Native SDKs

### Phase 1: Wrap Existing SDK
```python
# Before
kafka_client.publish(topic, data)

# Transition
class DaprPublisher:
    def publish(self, topic, data):
        # Call Dapr HTTP API
        requests.post(f"{dapr_url}/v1.0/publish/kafka-pubsub/{topic}", json=data)

# Use DaprPublisher
```

### Phase 2: Remove Native SDK
```python
# Remove kafka-python from requirements.txt
# Remove Kafka configuration from application
# Keep only Dapr HTTP client
```

### Phase 3: Componentize
```yaml
# Create Dapr component YAML
# Deploy to Kubernetes
# Application code unchanged
```

## Validation Checklist

Before shipping Dapr-based system:
- [ ] All services have dapr.io/enabled annotation
- [ ] No direct Kafka/Redis/RabbitMQ clients in application code
- [ ] Dapr components deployed for all environments
- [ ] Component names match across environments
- [ ] Secrets retrieved via Dapr Secrets API
- [ ] Service invocation uses app-id, not URLs
- [ ] Observability middleware configured
- [ ] Resiliency policies defined
- [ ] Component scoping configured
- [ ] mTLS enabled in production
