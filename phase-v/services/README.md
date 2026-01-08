# Phase V Microservices

This directory contains the implementation of Phase V microservices for the Todo AI Chatbot.

## Services Overview

### 1. API Service (Enhanced in Phase V)
**Location**: `backend/api-service/`
**Status**: ✅ Phase 1-5 Complete
**Responsibilities**:
- Task CRUD operations with advanced features (priority, tags, search, filters)
- Event publishing to Kafka via Dapr Pub/Sub
- Reminder scheduling via Dapr Jobs API
- Service invocation to auth service via Dapr

**Phase V Enhancements**:
- Recurring task support (recurrence_rule field)
- Due date and reminder scheduling
- Priority and tags filtering
- Keyword search across title/description
- Dapr sidecar integration

---

### 2. Recurring Task Service (Phase 6)
**Location**: `phase-v/services/recurring-task-service/`
**Status**: 🔄 To be implemented
**Responsibilities**:
- Consume `task.completed` events from Kafka
- Calculate next occurrence based on recurrence rules (daily, weekly, monthly)
- Publish `task.created` events for new occurrences
- Track last generated occurrence via Dapr State Management
- Idempotency using event IDs

**Key Components**:
- Event consumer (Dapr subscription)
- Recurrence calculator (daily/weekly/monthly logic)
- State management (last_generated_at tracking)
- Event publisher (new task occurrences)

---

### 3. Notification Service (Phase 7)
**Location**: `phase-v/services/notification-service/`
**Status**: 🔄 To be implemented
**Responsibilities**:
- Consume `reminders` events from Kafka
- Send email notifications via SMTP
- Retrieve SMTP credentials via Dapr Secrets API
- Track notification delivery status
- Handle failures with retry and DLQ

**Key Components**:
- Event consumer (Dapr subscription to reminders topic)
- SMTP client (email sending)
- Secrets integration (Dapr Secrets API)
- Template rendering (email HTML/text)

---

### 4. Audit Service (Phase 8)
**Location**: `phase-v/services/audit-service/`
**Status**: 🔄 To be implemented
**Responsibilities**:
- Consume all events from all topics (task-events, reminders, task-updates)
- Store audit logs in PostgreSQL
- Provide query API for audit log retrieval
- Filter by user, action type, date range
- Compliance and debugging support

**Key Components**:
- Multi-topic event consumer
- Audit log storage (PostgreSQL)
- Query API (filter, search, pagination)
- Retention policy enforcement (90-day default)

---

### 5. WebSocket Sync Service (Phase 9)
**Location**: `phase-v/services/websocket-sync-service/`
**Status**: 🔄 To be implemented
**Responsibilities**:
- Consume `task-updates` events from Kafka
- Maintain WebSocket connections with clients
- Broadcast task updates to connected clients in real-time
- Authenticate WebSocket connections via JWT
- Handle connection lifecycle (connect, disconnect, reconnect)

**Key Components**:
- WebSocket server (FastAPI WebSocket)
- Event consumer (Dapr subscription to task-updates topic)
- Connection manager (track active connections by user_id)
- Broadcasting logic (send updates to relevant clients)

---

## Service Communication Patterns

### Event-Driven (Asynchronous)
```
API Service → Kafka (task-events) → Recurring Task Service
API Service → Kafka (reminders) → Notification Service
API Service → Kafka (task-updates) → WebSocket Sync Service
All Services → Kafka (all topics) → Audit Service
```

### Request-Response (Synchronous via Dapr)
```
API Service → Dapr Service Invocation → Auth Service (BetterAuth)
```

### State Management (via Dapr)
```
Recurring Task Service → Dapr State API → PostgreSQL (last_generated_at)
API Service → Dapr State API → PostgreSQL (idempotency keys)
```

### Secrets Management (via Dapr)
```
Notification Service → Dapr Secrets API → Kubernetes Secrets (SMTP credentials)
All Services → Dapr Secrets API → Kubernetes Secrets (database, Kafka credentials)
```

---

## Deployment Architecture

### Kubernetes Pod Structure (with Dapr Sidecars)
```
┌─────────────────────────────────────┐
│ Pod: api-service                    │
│  ┌──────────────┐  ┌─────────────┐ │
│  │ api-service  │  │ dapr-sidecar│ │
│  │ (port 8000)  │←→│ (port 3500) │ │
│  └──────────────┘  └─────────────┘ │
└─────────────────────────────────────┘
         ↓ Dapr Pub/Sub
┌─────────────────────────────────────┐
│        Kafka Cluster                │
│  ┌─────────┬──────────┬───────────┐│
│  │task-    │reminders │task-      ││
│  │events   │          │updates    ││
│  └─────────┴──────────┴───────────┘│
└─────────────────────────────────────┘
         ↓ Kafka Consumers
┌──────────────────────────────────────────────────┐
│ Recurring Task Service | Notification Service   │
│ Audit Service          | WebSocket Sync Service │
└──────────────────────────────────────────────────┘
```

---

## Service Dependencies

| Service | Depends On | Kafka Topics | Dapr Components |
|---------|------------|--------------|-----------------|
| API Service | Auth Service | task-events (producer), reminders (producer), task-updates (producer) | pub/sub, state, secrets, jobs |
| Recurring Task Service | API Service | task-events (consumer), task-events (producer) | pub/sub, state |
| Notification Service | SMTP Server | reminders (consumer) | pub/sub, secrets |
| Audit Service | None | task-events, reminders, task-updates (consumer) | pub/sub, state |
| WebSocket Sync Service | None | task-updates (consumer) | pub/sub |

---

## Implementation Order

1. ✅ **Phase 1-4**: Infrastructure setup (Kafka, Dapr components)
2. ✅ **Phase 5**: API Service enhancements
3. 🔄 **Phase 6**: Recurring Task Service
4. 🔄 **Phase 7**: Notification Service
5. 🔄 **Phase 8**: Audit Service
6. 🔄 **Phase 9**: WebSocket Sync Service

---

## Testing Strategy

### Unit Tests
- Each service has `/tests` directory
- Mock Dapr HTTP API for isolated testing
- Test recurrence logic, email templates, WebSocket messages

### Integration Tests
- Deploy all services to Minikube
- Send end-to-end requests (create task → receive notification)
- Verify Kafka events, state management, service invocation

### E2E Tests
- Deploy to staging environment (cloud Kubernetes)
- Test with real Kafka, database, email provider
- Load testing with 10,000 concurrent users

---

## Monitoring and Observability

### Dapr Telemetry
- Automatic tracing for all Dapr operations
- Metrics exposed on `/metrics` endpoint
- Zipkin/Jaeger integration for distributed tracing

### Application Logs
- Structured JSON logs with correlation IDs
- Log levels: DEBUG (dev), INFO (prod)
- Centralized logging via Kubernetes (kubectl logs)

### Kafka Consumer Lag
- Monitor lag for each consumer group
- Alert if lag > 1000 messages or > 5 minutes
- Auto-scaling based on lag metrics

---

## Next Steps

Implement Phase 6: Recurring Task Service
- Create service structure
- Implement event consumer
- Implement recurrence calculator
- Integrate Dapr State Management
- Write Dockerfile and Helm chart
