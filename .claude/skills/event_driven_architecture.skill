# Event-Driven Architecture Intelligence

## Skill Name
Event-Driven Architecture Pattern Recognition and Application

## Scope
Apply event-driven architecture principles to distributed systems design, microservices communication, and asynchronous workflows.

## Trigger Conditions

Apply this skill when:
- Designing inter-service communication patterns
- Implementing state changes that need to propagate to multiple consumers
- Building audit trails or activity logs
- Handling asynchronous workflows or background processing
- Designing systems requiring temporal decoupling
- Creating notification or alerting systems
- Implementing CQRS or event sourcing patterns

## Core Intelligence Rules

### 1. Async-First Mindset
**Rule**: Prefer asynchronous events over synchronous calls for state changes and notifications.

**Decision Matrix**:
- **Use Events When**:
  - Multiple consumers need the same information
  - Producer doesn't need immediate response
  - Action has side effects across domains
  - Audit trail is required
  - Temporal decoupling is beneficial
  - Failure in one consumer shouldn't block others

- **Use Synchronous Calls When**:
  - Immediate response required (query operations)
  - Transaction must be atomic across services
  - Failure must block the operation
  - Single consumer, simple request-response

### 2. Producer-Consumer Separation
**Rule**: Producers publish facts, not commands. Consumers decide what to do with facts.

**Pattern**:
```
✓ GOOD: Publish "TaskCreated" event → Multiple consumers react independently
✗ BAD:  Publish "SendEmailForNewTask" command → Tight coupling
```

**Enforcement**:
- Event names should be past-tense (TaskCreated, UserRegistered, OrderPlaced)
- Events contain complete state snapshot at time of occurrence
- Producers never know who consumes events
- Consumers own their processing logic

### 3. Event Schema Discipline
**Rule**: Treat event schemas as contracts. Version them. Never break backwards compatibility.

**Standards**:
- Every event MUST have: `event_id`, `event_type`, `timestamp`, `schema_version`
- Use semantic versioning for schemas (1.0, 1.1, 2.0)
- Additive changes only within major version
- Include complete context in event payload (avoid joins)
- Use ISO 8601 for timestamps
- Use UUID v4 for event IDs

**Migration Strategy**:
- New fields: add with defaults, increment minor version
- Breaking changes: new event type or major version increment
- Deprecate old schemas with sunset timeline
- Support multiple versions during transition

### 4. Idempotency by Design
**Rule**: Every event consumer must be idempotent. Processing the same event multiple times produces the same result.

**Implementation Patterns**:
- **Deduplication**: Store processed event IDs (with TTL matching retention)
- **Natural Idempotency**: Design operations to be naturally idempotent (SET vs INCREMENT)
- **State Versioning**: Use optimistic locking or version fields

**Check Before Processing**:
```
1. Has this event_id been processed? → Skip
2. Apply business logic
3. Record event_id as processed
4. Commit atomically
```

### 5. At-Least-Once Delivery Assumption
**Rule**: Assume events may be delivered multiple times. Design for it.

**Implications**:
- Never assume exactly-once delivery
- Implement idempotency (see Rule 4)
- Use transactions where possible
- Accept potential duplicate processing

### 6. Auditability Through Events
**Rule**: Events are the source of truth for "what happened". Design them for audit and debugging.

**Requirements**:
- Include `user_id` or `actor_id` for accountability
- Include `source_service` for traceability
- Include sufficient context to answer "why did this happen?"
- Retain events long enough for compliance/debugging (30+ days for DLQ)
- Never delete events; archive if needed

### 7. Dead Letter Queue Strategy
**Rule**: Failed events go to DLQ after max retries. DLQ is monitored and manually resolved.

**DLQ Event Structure**:
```
{
  "dlq_id": "uuid",
  "original_event": { ... },
  "error_context": {
    "error_message": "...",
    "retry_count": 3,
    "consumer_service": "reminder-service",
    "timestamp": "..."
  }
}
```

**Process**:
- Retry with exponential backoff (3 attempts typical)
- Publish to DLQ after max retries
- Alert on DLQ accumulation
- Manual investigation and replay

### 8. Event Granularity
**Rule**: One event per business-meaningful state change. Not too coarse, not too fine.

**Heuristics**:
- **Too Fine**: "TaskTitleChanged", "TaskDescriptionChanged" → Use "TaskUpdated"
- **Too Coarse**: "SystemStateChanged" → Too vague
- **Just Right**: "TaskCreated", "TaskCompleted", "TaskDeleted"

**Exception**: Use fine-grained events when different consumers care about different changes.

### 9. Ordering Guarantees
**Rule**: Only guarantee order within a partition/key. Design consumers to handle out-of-order events.

**Partitioning Strategy**:
- Partition by entity ID (user_id, task_id) for ordering within entity
- Use consistent hashing for even distribution
- Accept that global ordering is impractical at scale

**Consumer Strategy**:
- Use version fields or timestamps to detect out-of-order
- Apply only if newer than current state
- Queue out-of-order events briefly, then accept best-effort

### 10. Event Payload Size
**Rule**: Keep events compact. Reference large objects, don't embed them.

**Guidelines**:
- Target < 1 KB per event
- Embed: IDs, primitives, small arrays (tags)
- Reference: Large text, files, binary data
- Include enough context to avoid N+1 queries in consumers

## Anti-Patterns to Avoid

### ❌ Request-Response via Events
**Anti-Pattern**: Publishing event and polling for response event.
**Fix**: Use synchronous API call or RPC pattern.

### ❌ Event Chains Without Sagas
**Anti-Pattern**: Event A triggers B triggers C with no coordination or rollback.
**Fix**: Implement saga pattern or use orchestration for complex workflows.

### ❌ Embedding Logic in Event Names
**Anti-Pattern**: "SendEmailIfUserIsNewAndTaskIsUrgent"
**Fix**: Publish "TaskCreated", let consumer decide based on business rules.

### ❌ Synchronous Calls in Event Handlers
**Anti-Pattern**: Event handler makes blocking API call to external service.
**Fix**: Publish new event or use async processing.

### ❌ Missing Correlation IDs
**Anti-Pattern**: No way to trace related events across services.
**Fix**: Include `correlation_id` or `trace_id` in all events.

### ❌ Unbounded Retries
**Anti-Pattern**: Retrying forever on failure, blocking queue.
**Fix**: Max retries (3-5), exponential backoff, then DLQ.

### ❌ State Stored Only in Events
**Anti-Pattern**: No queryable state store, must replay all events.
**Fix**: Maintain read models/projections for queries; events for writes.

### ❌ Events as Database Triggers
**Anti-Pattern**: Publishing event for every row change automatically.
**Fix**: Publish events only for business-meaningful actions.

## Decision Heuristics

### When to Split Events
```
IF (different consumers care about different aspects)
   OR (change frequency differs significantly)
   OR (security/privacy boundaries differ)
THEN split into multiple event types
ELSE keep as single event with all context
```

### When to Use Event Sourcing
```
IF (audit trail is critical AND full history replay needed)
   AND (willing to accept complexity of projections)
THEN use event sourcing
ELSE use events for integration only, maintain state in DB
```

### When to Batch Events
```
IF (high volume AND low latency not critical)
   AND (consumers can handle batches)
THEN batch events (e.g., 100 events or 5 seconds)
ELSE publish individually
```

### Retry Strategy Selection
```
IF error is transient (network, timeout):
   Retry with exponential backoff
ELSE IF error is permanent (validation, not found):
   Log and skip OR send to DLQ immediately
ELSE IF error is unknown:
   Retry 3 times, then DLQ
```

## Validation Checklist

Before shipping event-driven system, verify:
- [ ] All events have schema version and event_id
- [ ] Consumers are idempotent (can replay events safely)
- [ ] DLQ is configured and monitored
- [ ] Event retention matches business requirements
- [ ] Events contain enough context (no N+1 queries)
- [ ] Partitioning strategy ensures ordering where needed
- [ ] At-least-once delivery is handled correctly
- [ ] No blocking calls in event handlers
- [ ] Correlation IDs present for distributed tracing
- [ ] Event schemas are documented and versioned
