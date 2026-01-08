# Kafka Usage Strategy Intelligence

## Skill Name
Apache Kafka Architecture and Operational Best Practices

## Scope
Apply Kafka-specific design patterns for topic design, consumer groups, partitioning, replication, delivery semantics, and operational excellence.

## Trigger Conditions

Apply this skill when:
- Designing Kafka topic architecture
- Implementing Kafka producers or consumers
- Planning partitioning and ordering strategies
- Configuring replication and durability
- Handling failures and dead-letter scenarios
- Choosing between Kafka and alternative message brokers
- Optimizing Kafka performance and costs

## Core Intelligence Rules

### 1. Topic Design Principles
**Rule**: Topics represent event streams, not commands. Design for read patterns, not just write patterns.

**Naming Convention**:
```
{domain}.{entity}.{event-type}

Examples:
✓ GOOD: task.events, reminders.due, user.registered
✗ BAD:  events, messages, queue1
```

**Topic Characteristics**:
```yaml
# Production-ready topic
name: task-events
partitions: 6               # Based on throughput (1 partition ≈ 10 MB/s)
replication_factor: 3       # Minimum 3 for durability (2 in dev/staging)
retention_ms: 604800000     # 7 days (business requirement)
compression_type: snappy    # CPU-efficient compression
min_insync_replicas: 2      # Quorum writes (replication - 1)
cleanup_policy: delete      # vs compact (for state/changelog topics)
```

**Topic Count Strategy**:
```
Few Large Topics (Preferred):
- task-events (all task CRUD)
- reminders (all reminders)
- task-updates (WebSocket sync)

NOT Many Small Topics:
- task-created, task-updated, task-deleted (too fine-grained)
```

**Rationale**: Fewer topics reduce operational overhead (monitoring, rebalancing).

### 2. Partitioning Strategy
**Rule**: Partition by entity ID for ordering within entity. Partitions = parallelism.

**Partitioning Decision Tree**:
```
IF ordering required within entity (user, task):
   partition_key = entity_id (user_id, task_id)

ELSE IF ordering not required:
   partition_key = null (round-robin)

ELSE IF ordering required globally:
   partitions = 1 (NOT RECOMMENDED, throughput bottleneck)
```

**Partition Count Sizing**:
```
partitions = max(
   (target_throughput_MB_per_sec / 10),  # Throughput-based
   (consumer_count)                       # Parallelism-based
)

Examples:
- 60 MB/s throughput → 6 partitions minimum
- 6 consumers for parallel processing → 6 partitions
- Result: 6 partitions
```

**Growth Headroom**: Add 50% partitions for growth (6 → 9).

**Warning**: Changing partition count later requires manual repartitioning.

### 3. Replication and Durability
**Rule**: Use replication factor 3 in production. Accept 2 for cost-sensitive staging.

**Replication Configuration**:
```yaml
# Production
replication_factor: 3
min_insync_replicas: 2  # Quorum (RF - 1)

# Staging
replication_factor: 2
min_insync_replicas: 1

# Local Dev
replication_factor: 1  # Single broker
min_insync_replicas: 1
```

**Producer Acknowledgment**:
```python
# Production (durability)
acks = "all"  # Wait for min.insync.replicas

# High throughput, acceptable data loss
acks = "1"    # Wait for leader only
```

**Tradeoff**: `acks=all` + `min.insync.replicas=2` = **durability** but higher latency.

### 4. Consumer Group Strategy
**Rule**: One consumer group per logical application. Multiple consumers in group for parallelism.

**Consumer Group Pattern**:
```
Topic: task-events (6 partitions)

Consumer Group: reminder-service
- Consumer 1: Partitions 0, 1
- Consumer 2: Partitions 2, 3
- Consumer 3: Partitions 4, 5

Consumer Group: audit-service
- Consumer 1: Partitions 0, 1, 2, 3, 4, 5
```

**Rules**:
- Consumers in same group = **load balancing** (each message to one consumer)
- Different groups = **pub/sub** (each group gets all messages)
- Max parallelism = partition count (adding more consumers than partitions = idle)

**Scaling Strategy**:
```
IF consumer lag increasing:
   Add consumers (up to partition count)

IF still lagging:
   Increase partitions (requires repartitioning)
```

### 5. Delivery Semantics
**Rule**: Kafka guarantees at-least-once delivery. Design consumers for idempotency.

**Delivery Guarantees**:
- **At-Most-Once**: `enable.auto.commit=true` (data loss possible)
- **At-Least-Once**: Manual commit after processing (duplicates possible)
- **Exactly-Once**: Transactional producer + consumer (complex, avoid unless critical)

**Recommended Pattern (At-Least-Once)**:
```python
while True:
    messages = consumer.poll()
    for message in messages:
        # 1. Check deduplication (idempotency)
        if already_processed(message.event_id):
            continue

        # 2. Process message
        process_event(message)

        # 3. Record as processed
        mark_processed(message.event_id)

        # 4. Commit offset
        consumer.commit()
```

**Never**:
```python
# Anti-pattern: commit before processing
consumer.commit()
process_event(message)  # If this fails, message is lost
```

### 6. Retention and Cleanup Policies
**Rule**: Set retention based on business requirements, not arbitrary defaults.

**Retention Strategy**:
```yaml
# Event streams (task-events, reminders)
retention_ms: 604800000     # 7 days
cleanup_policy: delete

# Dead-letter queue
retention_ms: 2592000000    # 30 days (compliance, debugging)
cleanup_policy: delete

# Changelog/state topics (if using Kafka Streams)
retention_ms: -1            # Infinite
cleanup_policy: compact
```

**Sizing Formula**:
```
storage_needed = (messages_per_day × avg_message_size × retention_days)

Example:
- 100K events/day
- 1 KB avg size
- 7 days retention
= 100K × 1KB × 7 = 700 MB
× 3 replicas = 2.1 GB
```

### 7. Dead-Letter Queue Pattern
**Rule**: Use single DLQ topic for all failures. Route by original topic in payload.

**DLQ Topic Design**:
```yaml
name: dlq-events
partitions: 3              # Lower than main topics (lower volume)
replication_factor: 3
retention_ms: 2592000000   # 30 days (long retention for investigation)
```

**DLQ Event Structure**:
```json
{
  "dlq_id": "uuid",
  "original_topic": "task-events",
  "original_partition": 3,
  "original_offset": 12345,
  "original_event": { ... },
  "error_context": {
    "error_message": "Database connection timeout",
    "retry_count": 3,
    "consumer_service": "reminder-service",
    "timestamp": "2026-01-03T10:00:00Z"
  }
}
```

**DLQ Processing**:
1. Alert on DLQ accumulation (threshold: 10 messages)
2. Manual investigation
3. Fix root cause
4. Replay from DLQ or re-publish to original topic

### 8. Compression Strategy
**Rule**: Use Snappy for balanced CPU and compression ratio. Use LZ4 for CPU-sensitive workloads.

**Compression Comparison**:
```
Algorithm   | Compression Ratio | CPU Usage | Recommendation
------------|-------------------|-----------|---------------
none        | 1x                | Low       | Only if CPU constrained
snappy      | 2-3x              | Low       | Default choice
lz4         | 2-3x              | Very Low  | CPU-sensitive
gzip        | 4-5x              | High      | Network-constrained
zstd        | 4-5x              | Medium    | Kafka 2.1+ only
```

**Configuration**:
```yaml
compression_type: snappy  # Broker-side (applies to all producers)
```

**Producer override**: Allowed but discouraged (consistency).

### 9. Performance Optimization
**Rule**: Tune batch size and linger time for throughput vs latency tradeoff.

**Producer Tuning**:
```python
# High throughput (batch writes)
batch_size = 65536          # 64 KB (default: 16 KB)
linger_ms = 10              # Wait 10ms to batch (default: 0)

# Low latency (immediate send)
batch_size = 16384          # Default
linger_ms = 0               # Send immediately
```

**Consumer Tuning**:
```python
# High throughput
fetch_min_bytes = 100000    # Wait for 100 KB before returning
fetch_max_wait_ms = 500     # Or 500ms timeout

# Low latency
fetch_min_bytes = 1         # Return immediately
fetch_max_wait_ms = 100     # 100ms max wait
```

### 10. When NOT to Use Kafka
**Rule**: Kafka is not always the right choice. Consider alternatives for specific use cases.

**Use Kafka When**:
- High throughput event streaming (millions of events/day)
- Multiple consumers need same events
- Event replay required
- Ordering within partition critical
- Durable message storage needed

**Consider Alternatives When**:
```
Low volume (< 10K events/day):
   → Use Redis Pub/Sub (simpler)

Request-response pattern:
   → Use HTTP/gRPC (not events)

Task queue with workers:
   → Use RabbitMQ or Redis Queue (better for task queues)

Real-time updates to UI:
   → Use WebSockets + lightweight topic (task-updates)

Scheduled jobs:
   → Use Dapr Jobs API or Kubernetes CronJobs
```

**Kafka Overhead**:
- Operational complexity (ZooKeeper/KRaft, rebalancing)
- Higher resource usage (memory, storage)
- More expensive than simple queues

**Decision**: Use Kafka when benefits (durability, replay, multi-consumer) outweigh overhead.

## Anti-Patterns to Avoid

### ❌ Too Many Topics
**Anti-Pattern**: One topic per event type (100+ topics).
**Fix**: Consolidate related events (task.created, task.updated → task-events).

### ❌ Unbounded Retention
**Anti-Pattern**: `retention.ms = -1` (infinite) for event streams.
**Fix**: Set retention based on business need (7 days typical).

### ❌ Single Partition for Ordered Processing
**Anti-Pattern**: 1 partition to guarantee global order.
**Fix**: Partition by entity ID, accept eventual consistency across entities.

### ❌ Consumer Commits Before Processing
**Anti-Pattern**: Auto-commit or commit before handling message.
**Fix**: Manual commit after successful processing.

### ❌ Ignoring Consumer Lag
**Anti-Pattern**: No monitoring of consumer lag.
**Fix**: Alert on lag > threshold (e.g., 1000 messages or 5 minutes).

### ❌ No Message Schema
**Anti-Pattern**: Arbitrary JSON with no version or validation.
**Fix**: Use Pydantic models, include schema_version in every message.

### ❌ Using Kafka as Database
**Anti-Pattern**: Querying Kafka for current state.
**Fix**: Maintain read models/projections in database, use Kafka for changes.

### ❌ Synchronous Kafka Publishing in Critical Path
**Anti-Pattern**: Blocking API response on Kafka publish success.
**Fix**: Publish asynchronously, handle failures gracefully (best-effort).

## Decision Heuristics

### Kafka vs Redis Pub/Sub
```
IF (volume > 100K events/day OR replay needed OR multiple consumers):
   Use Kafka
ELSE IF (volume < 10K events/day AND simple pub/sub):
   Use Redis Pub/Sub
ELSE:
   Use Kafka via Dapr (portable, can swap later)
```

### Partition Count
```
partitions = ROUND_UP(
   MAX(
      target_throughput_MB_per_sec / 10,
      max_consumers
   ) × 1.5  # 50% growth headroom
)

Constraints:
- Minimum: 3
- Maximum: 50 (operational complexity increases)
```

### Replication Factor
```
IF production:
   replication_factor = 3
   min_insync_replicas = 2
ELSE IF staging:
   replication_factor = 2
   min_insync_replicas = 1
ELSE (local dev):
   replication_factor = 1
   min_insync_replicas = 1
```

### Compression Type
```
IF CPU is bottleneck:
   compression_type = lz4
ELSE IF network is bottleneck:
   compression_type = gzip
ELSE (default):
   compression_type = snappy
```

### Consumer Group Scaling
```
IF consumer lag increasing:
   current_consumers < partitions:
      Add consumers
   ELSE:
      Increase partitions (breaking change, requires migration)
ELSE IF consumer lag near zero AND multiple idle consumers:
   Reduce consumers
```

## Kafka Deployment Strategies

### Local Development
**Option 1: Strimzi Operator** (Production-like)
```yaml
# Heavy (1.5 GB RAM), but production-identical
kafka:
  replicas: 3
  storage: 10Gi per broker
zookeeper:
  replicas: 3
```

**Option 2: Redpanda** (Lightweight)
```yaml
# Light (512 MB RAM), faster startup
kafka:
  replicas: 1  # Single broker sufficient
  storage: 5Gi
# No ZooKeeper needed
```

**Recommendation**: Redpanda for local, Strimzi for staging/prod.

### Cloud Deployment
**Option 1: Self-Managed (Strimzi on K8s)**
- Full control
- No vendor lock-in
- Higher operational overhead

**Option 2: Managed Kafka**
- Azure: Event Hubs (Kafka-compatible)
- AWS: MSK (Managed Streaming for Kafka)
- GCP: Managed Kafka (preview)
- Higher cost, less control

**Option 3: Redpanda Cloud** (Recommended)
- Kafka-compatible
- Free tier (5 GB storage)
- Multi-cloud (AWS, GCP)
- Simpler than Kafka (no ZooKeeper)

**Decision**:
```
IF free tier sufficient:
   Use Redpanda Cloud
ELSE IF Kafka expertise available:
   Use Strimzi on Kubernetes (portable)
ELSE:
   Use managed Kafka (cloud-specific)
```

## Monitoring and Observability

### Critical Metrics
```
# Broker-level
- Under-replicated partitions (alert if > 0)
- Offline partitions (alert if > 0)
- Active controller count (alert if != 1)

# Topic-level
- Partition lag (alert if > 1000 messages)
- Bytes in/out rate
- Message rate

# Consumer-level
- Consumer lag (alert if > 5 minutes)
- Commit rate
- Rebalance frequency (alert if > 1/hour)
```

### Lag Alerting Strategy
```yaml
# Low-priority topics (analytics)
lag_threshold: 10000 messages or 1 hour

# High-priority topics (reminders)
lag_threshold: 100 messages or 5 minutes

# Critical topics (payments)
lag_threshold: 10 messages or 1 minute
```

## Schema Evolution

### Versioning Strategy
```json
{
  "event_id": "uuid",
  "schema_version": "1.0",  // Semantic versioning
  "event_type": "task.created",
  "timestamp": "2026-01-03T10:00:00Z",
  "data": { ... }
}
```

### Schema Changes
```
Additive (minor version bump):
- New optional field
- New event type

Breaking (major version bump):
- Remove field
- Change field type
- Rename field
```

### Consumer Compatibility
```python
# Handle multiple schema versions
if message.schema_version == "1.0":
    process_v1(message)
elif message.schema_version == "2.0":
    process_v2(message)
else:
    log_unknown_version(message)
```

## Validation Checklist

Before deploying Kafka-based system:
- [ ] Topic partition count based on throughput calculation
- [ ] Replication factor = 3 in production
- [ ] min.insync.replicas = 2 in production
- [ ] Retention period matches business requirements
- [ ] Compression enabled (snappy default)
- [ ] Consumer groups defined per application
- [ ] Idempotency implemented (deduplication)
- [ ] DLQ topic configured with alerts
- [ ] Consumer lag monitoring and alerting
- [ ] Schema versioning in place
- [ ] Manual offset commit (not auto-commit)
- [ ] Partition key strategy documented
- [ ] No single-partition topics (unless justified)
- [ ] Producer acks=all for critical data
- [ ] Backup/disaster recovery plan
