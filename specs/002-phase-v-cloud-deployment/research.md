# Architecture Research: Phase V - Advanced Cloud Deployment

**Feature**: Phase V - Advanced Cloud Deployment
**Date**: 2026-01-02
**Status**: Complete

This document captures all architectural research decisions for implementing the event-driven, cloud-native transformation of the Todo AI Chatbot.

---

## 1. Kafka Deployment Strategy

### Research Question
Evaluate Kafka deployment strategies for local (Minikube) and cloud (Redpanda Cloud/Confluent Cloud) environments.

### Decision
- **Local Development**: Redpanda (single binary)
- **Cloud Staging/Dev**: Redpanda Cloud Free Tier
- **Cloud Production**: Redpanda Cloud (primary) or Confluent Cloud (alternative)

### Rationale
**Redpanda Advantages**:
- Single Go binary with lower memory footprint than Strimzi (JVM-based)
- Kafka API compatible - no code changes required
- Free tier available: 10GB retention, 10MB/s throughput
- Simpler operation for local development (no ZooKeeper required)
- Faster startup time on Minikube (2-3 minutes vs 5-10 minutes for Strimzi)

**Resource Comparison**:
- Redpanda: ~512MB RAM per broker
- Strimzi Kafka: ~1.5GB RAM per broker (Java heap + overhead)
- Minikube constraint: 8GB total RAM

### Alternatives Considered
1. **Strimzi Operator**
   - Pros: Production-grade, Kubernetes-native, full Kafka feature set
   - Cons: Higher resource usage (3 brokers = 4.5GB minimum), slower startup
   - Use case: Enterprise production deployments with dedicated infrastructure

2. **Confluent Cloud**
   - Pros: Managed service, enterprise features (Schema Registry, ksqlDB), 99.95% SLA
   - Cons: No free tier (starts at $1/hour), vendor lock-in
   - Use case: Production deployments with budget for managed services

### Topic Configuration
- **Partitions**: 6 for `task-events` and `task-updates` (user sharding), 3 for `reminders` and `dlq-events`
- **Replication Factor**: 3 for production (high availability), 1 for local development
- **Retention**: 7 days for operational topics, 30 days for DLQ (investigation window)
- **Compression**: Snappy (balance between CPU and storage)

### Topic Creation Strategy
- **Local**: Manual creation via `kubectl apply -f` with KafkaTopic CRDs (Strimzi) or Redpanda Admin API
- **Cloud**: Terraform or Redpanda Cloud CLI for infrastructure-as-code
- **Application**: No auto-topic-creation - fail fast if topics missing (explicit dependency)

---

## 2. Dapr Component Configuration Patterns

### Research Question
Define Dapr component YAML structure for pub/sub, state, secrets, and jobs.

### Decision
- **Secrets**: Kubernetes-native Secrets for Phase V (with migration path to external secrets in Phase VI)
- **Component Scoping**: Service-specific scopes to enforce least privilege
- **Connection Pooling**: Managed by Dapr State component (not application-level)

### Dapr Pub/Sub Component (Kafka)

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
      value: "kafka-broker-0.kafka-headless.todo-app-dev.svc.cluster.local:9092"
    - name: consumerGroup
      value: "{podName}"  # Unique per consumer instance
    - name: authType
      value: "sasl"  # Cloud only
    - name: saslUsername
      secretKeyRef:
        name: kafka-credentials
        key: username
    - name: saslPassword
      secretKeyRef:
        name: kafka-credentials
        key: password
    - name: saslMechanism
      value: "SCRAM-SHA-256"
  scopes:
    - api-service
    - recurring-task-service
    - notification-service
    - audit-service
    - websocket-sync-service
```

**Key Decisions**:
- **Consumer Group Naming**: `{podName}` ensures unique groups for horizontal scaling
- **Auth**: SASL/SCRAM for cloud (encrypted passwords), none for local
- **Scopes**: Explicit allow-list prevents unauthorized Kafka access

### Dapr State Management Component (PostgreSQL)

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: postgres-statestore
spec:
  type: state.postgresql
  version: v1
  metadata:
    - name: connectionString
      secretKeyRef:
        name: database-credentials
        key: connectionString
    - name: tablePrefix
      value: "dapr_state_"
    - name: timeout
      value: "20s"
    - name: maxConns
      value: "20"  # Per pod
  scopes:
    - recurring-task-service
    - websocket-sync-service
```

**Key Decisions**:
- **Table Prefix**: Separates Dapr state from application tables
- **Connection Pool**: 20 connections per pod (5 pods × 20 = 100 total < Neon free tier 300 limit)
- **Timeout**: 20 seconds for state operations (prevent hung connections)

### Dapr Secrets Component (Kubernetes)

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kubernetes-secrets
spec:
  type: secretstores.kubernetes
  version: v1
  metadata:
    - name: defaultNamespace
      value: "todo-app-dev"
```

**Phase VI Migration Path**:
- Replace `type: secretstores.kubernetes` with `type: secretstores.azure.keyvault` or `secretstores.hashicorp.vault`
- No application code changes required (Dapr abstraction layer)

### Dapr Jobs API Configuration

```yaml
# Configured via Dapr sidecar annotations
annotations:
  dapr.io/enabled: "true"
  dapr.io/app-id: "api-service"
  dapr.io/enable-api-logging: "true"
  dapr.io/jobs-api: "true"  # Enable Jobs API
```

**Scheduling Syntax**:
```json
{
  "data": {"task_id": 123, "user_id": 456},
  "dueTime": "2026-01-03T14:00:00Z",
  "ttl": "1h"
}
```

**Callback Endpoint**: `POST /api/reminders/trigger`

**Failure Retry**: Dapr handles retries (exponential backoff up to 5 attempts)

---

## 3. Event Schema Versioning Strategy

### Research Question
Define approach for evolving event schemas without breaking consumers.

### Decision
- **Schema Version**: String field (e.g., "1.0") in every event
- **Change Policy**: Additive only (new fields must be nullable)
- **Validation**: JSON Schema files in `specs/002-phase-v-cloud-deployment/contracts/`
- **Registry**: No external registry (Phase V) - validation in tests only

### Schema Evolution Rules

**Allowed (Non-Breaking)**:
- Adding new optional fields
- Adding new event types to existing topic
- Extending enum values (if consumers ignore unknown)

**Disallowed (Breaking)**:
- Removing fields
- Changing field types
- Renaming fields
- Making optional fields required

### Consumer Compatibility

**Forward Compatibility** (new producer, old consumer):
- Old consumer ignores unknown fields
- Schema version check: `if event.schema_version not in ["1.0", "1.1"]: log_warning()`

**Backward Compatibility** (old producer, new consumer):
- New consumer provides defaults for missing fields
- Validate required fields exist before processing

### JSON Schema Validation (Test-Time)

```python
# tests/contract/test_task_event_schema.py
import jsonschema

def test_task_event_schema():
    with open("specs/002-phase-v-cloud-deployment/contracts/task-event-schema.json") as f:
        schema = json.load(f)

    event = {
        "event_id": "uuid-v4",
        "schema_version": "1.0",
        "event_type": "task.created",
        # ...
    }

    jsonschema.validate(instance=event, schema=schema)
```

### Alternatives Considered
- **Confluent Schema Registry**: Requires separate infrastructure, overkill for Phase V
- **Protobuf**: Requires code generation, adds build complexity
- **Avro**: Good for large-scale systems, unnecessary for 4 topics

---

## 4. Idempotency Key Generation

### Research Question
Define strategy for generating unique event IDs to prevent duplicate processing.

### Decision
- **ID Format**: UUID v4
- **Generation**: Client-side (event producer)
- **Duplicate Detection**: Consumer tracks processed IDs in Dapr State with 7-day TTL
- **Partition Key**: task_id for related events (ensures ordering)

### Implementation

**Producer**:
```python
import uuid

event_id = str(uuid.uuid4())
event = {
    "event_id": event_id,
    "schema_version": "1.0",
    "event_type": "task.created",
    # ...
}
```

**Consumer**:
```python
async def process_event(event: TaskEvent):
    # Check if already processed
    processed = await dapr_client.get_state(
        store_name="postgres-statestore",
        key=f"processed_event_{event.event_id}"
    )

    if processed:
        logger.info(f"Duplicate event {event.event_id}, skipping")
        return

    # Process event
    await generate_next_occurrence(event.task_data)

    # Mark as processed with 7-day TTL
    await dapr_client.save_state(
        store_name="postgres-statestore",
        key=f"processed_event_{event.event_id}",
        value="true",
        metadata={"ttlInSeconds": "604800"}  # 7 days
    )
```

### Rationale
- **UUID v4**: Universally unique without coordination, no collision risk
- **Client-side**: No dependency on broker or database for ID generation
- **7-day TTL**: Matches Kafka retention (events older than 7 days can't be reprocessed)
- **Dapr State**: Distributed storage accessible across pod restarts

### Alternatives Considered
- **UUID v7**: Timestamp-based ordering, but newer (Python 3.11+ only)
- **ULID**: Sortable and efficient, but requires external library
- **Database-tracked IDs**: Query overhead on every event, doesn't scale

---

## 5. Dead Letter Queue Handling

### Research Question
Define DLQ handling for events that fail max retry attempts.

### Decision
- **DLQ Topic**: Single `dlq-events` topic for all failures
- **Retention**: 30 days (longer investigation window)
- **Payload**: Original event + error context
- **Consumption**: Manual inspection initially, automated retry service in Phase VI

### DLQ Event Schema

```json
{
  "dlq_id": "uuid-v4",
  "original_event_id": "uuid-v4",
  "original_topic": "task-events",
  "original_event": { /* full original event */ },
  "error_context": {
    "error_message": "Database connection timeout",
    "stack_trace": "...",
    "retry_count": 5,
    "first_attempt_at": "2026-01-02T10:00:00Z",
    "last_attempt_at": "2026-01-02T10:05:30Z",
    "consumer_service": "recurring-task-service",
    "consumer_pod": "recurring-task-service-7d8f9-xkj2p"
  },
  "timestamp": "2026-01-02T10:05:30Z"
}
```

### Producer Logic (in Consumer Error Handler)

```python
async def handle_event_failure(event: TaskEvent, error: Exception, retry_count: int):
    if retry_count >= 5:
        # Publish to DLQ
        dlq_event = {
            "dlq_id": str(uuid.uuid4()),
            "original_event_id": event.event_id,
            "original_topic": "task-events",
            "original_event": event.dict(),
            "error_context": {
                "error_message": str(error),
                "stack_trace": traceback.format_exc(),
                "retry_count": retry_count,
                # ...
            }
        }
        await dapr_client.publish_event(
            pubsub_name="kafka-pubsub",
            topic_name="dlq-events",
            data=json.dumps(dlq_event)
        )
        logger.error(f"Event {event.event_id} sent to DLQ after {retry_count} retries")
```

### Monitoring

- **Prometheus Metric**: `dlq_events_total{topic="task-events"}`
- **Alert**: Fire if DLQ growth rate > 10 events/minute
- **Dashboard**: Grafana panel showing DLQ accumulation over time

### Alternatives Considered
- **Per-Topic DLQ**: `task-events.dlq`, `reminders.dlq` - topic sprawl, harder to monitor
- **Per-Consumer DLQ**: Couples DLQ to consumer implementation, less flexible

---

## 6. Kubernetes Namespace Strategy

### Research Question
Define namespace isolation for dev, staging, prod environments.

### Decision
- **Environment-Based Namespaces**: `todo-app-dev`, `todo-app-staging`, `todo-app-prod`
- **No Feature-Based Namespaces**: Avoid ephemeral namespace complexity
- **Resource Quotas**: Enforced per namespace to prevent resource exhaustion

### Namespace Configuration

```yaml
# kubernetes/namespaces/dev.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: todo-app-dev
  labels:
    environment: dev
    app: todo-chatbot

---
apiVersion: v1
kind: ResourceQuota
metadata:
  name: dev-quota
  namespace: todo-app-dev
spec:
  hard:
    requests.cpu: "4"
    requests.memory: "8Gi"
    limits.cpu: "8"
    limits.memory: "16Gi"
    persistentvolumeclaims: "5"
```

### Network Isolation

- **Default**: No NetworkPolicy (allow all traffic within namespace)
- **Phase VI**: Implement NetworkPolicies to restrict pod-to-pod communication

### Resource Quotas by Environment

| Environment | CPU Request | Memory Request | CPU Limit | Memory Limit |
|-------------|-------------|----------------|-----------|--------------|
| dev         | 4 cores     | 8Gi            | 8 cores   | 16Gi         |
| staging     | 8 cores     | 16Gi           | 16 cores  | 32Gi         |
| prod        | 16 cores    | 32Gi           | 32 cores  | 64Gi         |

### Rationale
- **Environment Isolation**: Prevents dev/staging failures from impacting production
- **Resource Quotas**: Protects cluster from runaway pods
- **Namespace Reuse**: Same namespace for all microservices in environment (simpler RBAC)

### Alternatives Considered
- **Single Namespace with Labels**: Less isolation, accidental cross-environment impacts
- **Feature-Based Namespaces**: `002-phase-v-cloud-deployment` - ephemeral, complicates DNS

---

## 7. Helm Chart Upgrade Strategy

### Research Question
Define migration path from Phase IV charts to Phase V Dapr-enhanced charts.

### Decision
- **In-Place Upgrade**: `helm upgrade` existing releases with new values
- **Pre-Upgrade Migration**: Alembic migration job via Helm hook
- **Rollback**: `helm rollback <release> <revision>` with automated health checks

### Upgrade Process

**Step 1: Database Migration** (Helm Pre-Upgrade Hook)
```yaml
# charts/todo-chatbot-backend/templates/migration-job.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ .Release.Name }}-migration
  annotations:
    "helm.sh/hook": pre-upgrade
    "helm.sh/hook-weight": "-5"
    "helm.sh/hook-delete-policy": before-hook-creation
spec:
  template:
    spec:
      containers:
      - name: migration
        image: {{ .Values.api.image }}
        command: ["alembic", "upgrade", "head"]
        env:
          - name: DATABASE_URL
            valueFrom:
              secretKeyRef:
                name: database-credentials
                key: connectionString
```

**Step 2: Helm Upgrade**
```bash
helm upgrade backend charts/todo-chatbot-backend \
  --namespace todo-app-dev \
  --values charts/todo-chatbot-backend/values-local.yaml \
  --wait \
  --timeout 5m
```

**Step 3: Verification**
```bash
kubectl rollout status deployment/api-service -n todo-app-dev
kubectl get pods -n todo-app-dev | grep -E "api-service|recurring-task-service"
```

### Rollback Strategy

**Trigger Conditions**:
- Error rate > 5% for 2 minutes
- p95 latency > 2 seconds for 2 minutes
- Pod crash loop (>3 restarts in 5 minutes)
- Critical CVE discovered in deployed image

**Rollback Procedure**:
```bash
# Automatic rollback (via monitoring alert webhook)
helm rollback backend --namespace todo-app-prod --wait

# Database rollback (if schema change incompatible)
kubectl run alembic-downgrade \
  --image=api-service:previous \
  --restart=Never \
  --rm -it \
  --command -- alembic downgrade -1
```

### Alternatives Considered
- **Blue-Green Deployment**: Requires 2x resources, overkill for non-production
- **Separate Phase V Namespace**: Data duplication, migration complexity

---

## Summary

| Decision Area | Selected Approach | Key Benefit |
|---------------|-------------------|-------------|
| Kafka | Redpanda (local), Redpanda Cloud (cloud) | Low resource footprint, Kafka-compatible |
| Dapr Secrets | Kubernetes-native Secrets | Simple, no external dependencies |
| Event Versioning | JSON Schema with additive-only changes | Forward/backward compatibility |
| Idempotency | UUID v4 + Dapr State (7-day TTL) | No coordination needed, scalable |
| Dead Letter Queue | Single `dlq-events` topic | Centralized monitoring, simple alerting |
| Namespaces | Environment-based (`-dev`, `-staging`, `-prod`) | Strong isolation, resource quotas |
| Helm Upgrade | In-place with pre-upgrade migration hook | Zero data duplication, automated rollback |

---

**Next Steps**: Use these decisions to guide Phase 2 (database schema), Phase 3 (Kafka topics), and Phase 4 (Dapr components) implementation.
