# Implementation Plan: Phase V - Advanced Cloud Deployment

**Branch**: `002-phase-v-cloud-deployment` | **Date**: 2026-01-02 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-phase-v-cloud-deployment/spec.md`

## Summary

Phase V transforms the Todo AI Chatbot into a cloud-native, event-driven microservices system deployed on Kubernetes with Dapr abstraction and Kafka event backbone. The plan orchestrates:

1. **Advanced Features**: Recurring tasks, due date reminders, priority/tags/search/filter/sort
2. **Event-Driven Architecture**: Kafka topics with schema-versioned events, idempotent consumers, dead letter queues
3. **Dapr Integration**: Pub/Sub (Kafka), State Management (PostgreSQL), Service Invocation, Jobs API (reminders), Secrets Management
4. **Multi-Environment Deployment**: Local (Minikube + Strimzi/Redpanda) → Cloud (AKS/GKE/OKE + Redpanda Cloud/Confluent)
5. **New Services**: Recurring Task Service, Notification Service, Audit Service, WebSocket Sync Service
6. **CI/CD Automation**: GitHub Actions pipeline with automated testing, image building, and deployment
7. **Observability**: Structured logging, Prometheus metrics, Dapr telemetry, centralized dashboards

**Technical Approach**: Phase IV Helm charts enhanced with Dapr sidecar injection, Kafka event topics provisioned with replication, new Python/Node.js microservices consuming events, and database schema extended with recurrence rules, priority, tags, and due dates.

## Technical Context

**Languages/Versions**:
- Python 3.11+ (Chat API, Recurring Task Service, Notification Service, Audit Service)
- Node.js 20+ (Frontend, Auth Service, WebSocket Sync Service)
- TypeScript 5+ (Frontend, Auth Service, WebSocket Sync Service)

**Primary Dependencies**:
- **Event Streaming**: Apache Kafka 2.8+ (via Redpanda Cloud, Confluent Cloud, or Strimzi Operator)
- **Dapr Runtime**: Dapr 1.12+ with Jobs API support
- **Kubernetes**: Kubernetes 1.24+ (Minikube 1.32+ for local, managed clusters for cloud)
- **Helm**: Helm 3.10+ for packaging and deployment
- **Container Runtime**: Docker 24+ or Podman 4+
- **FastAPI**: 0.100+ for Python services
- **Socket.IO**: 4.6+ for WebSocket Sync Service
- **Pytest**: 7.4+ for Python testing
- **Vitest**: 1.0+ for TypeScript testing

**Storage**:
- **Primary Database**: Neon Serverless PostgreSQL (external, managed)
- **Event Store**: Kafka topics (4 topics: task-events, reminders, task-updates, dlq-events)
- **State Management**: Dapr State component backed by PostgreSQL
- **Secrets Storage**: Kubernetes Secrets accessed via Dapr Secrets component

**Testing**:
- **Unit Tests**: pytest (Python services), vitest (TypeScript services)
- **Integration Tests**: pytest with testcontainers (Kafka, PostgreSQL)
- **E2E Tests**: playwright (frontend → backend → database → events)
- **Contract Tests**: Pact for event schema validation
- **Load Tests**: k6 for performance validation (10K concurrent users)

**Target Platforms**:
- **Local Development**: Minikube 1.32+ on Windows/macOS/Linux (4 CPUs, 8GB RAM minimum)
- **Cloud Production**: Azure AKS, Google GKE, Oracle OKE (Always Free tier supported)
- **Container Registry**: Docker Hub, Azure ACR, Google GCR, or GitHub Container Registry

**Project Type**: Web + Microservices (frontend + auth-service + api-service + 4 new event-driven services)

**Performance Goals**:
- **API Response Time**: p95 < 500ms for 10,000 concurrent users
- **Event Processing Latency**: Average < 100ms from publish to consumer processed
- **WebSocket Broadcast**: < 500ms to 10,000 concurrent connections
- **Search/Filter**: < 1 second for 10,000 tasks per user
- **Recurring Task Generation**: < 5 seconds after occurrence completion
- **Reminder Scheduling**: < 2 seconds via Dapr Jobs API

**Constraints**:
- **Cost**: Total cloud infrastructure < $50/month for 1,000 DAU
- **Uptime**: 99.9% availability (< 43 minutes downtime/month)
- **Free Tier Compatibility**: Must run on Oracle OKE Always Free tier (2 VMs, 1GB RAM each)
- **Event Retention**: Minimum 7 days for Kafka topics
- **Consumer Lag**: < 1 second under normal load
- **Database Connections**: Managed via Dapr State component connection pooling

**Scale/Scope**:
- **Users**: 100,000 users with average 50 tasks per user
- **Services**: 7 microservices (3 from Phase IV + 4 new)
- **Event Volume**: Peak 10,000 events/second across all topics
- **Kafka Topics**: 4 topics with 6 partitions each (task-events, task-updates)
- **Kubernetes Pods**: 15-30 pods (services + Dapr sidecars + Kafka brokers for local)
- **Helm Charts**: 2 charts (frontend, backend) with Dapr enhancements

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Stateless-First Architecture ✅ COMPLIANT

**Status**: COMPLIANT

**Evidence**:
- Dapr State Management component enforces stateless service design
- All conversation context stored in PostgreSQL via Dapr State API
- Event consumers load state from database per event (recurring task last_generated_at)
- No in-memory caches or session stores
- All services horizontally scalable without shared state

**Phase V Enhancements**:
- Recurring Task Service: Stores last occurrence timestamp in Dapr State (not memory)
- WebSocket Sync Service: Manages connection registry in Dapr State
- Notification Service: No state retained between email sends
- Audit Service: Streams events directly to database without buffering

### II. MCP-First Tool Integration ⚠️ EXTENDED

**Status**: EXTENDED (new services do NOT use MCP)

**Evidence**:
- Phase IV Chat API continues using MCP tools for task operations
- NEW services (Recurring Task Service, Notification Service, Audit Service, WebSocket Sync Service) interact directly with database and Kafka

**Justification**:
- MCP is AI-agent interface; new services are event-driven background workers
- Event consumers (Recurring Task Service, Notification Service) process Kafka events, not user requests
- Audit Service and WebSocket Sync Service are system-level infrastructure, not AI tools
- Chat API (AI agent interface) remains MCP-compliant

**Action**: Update constitution to clarify MCP applies only to AI-agent interfaces, not event-driven microservices

### III. Database Persistence Guarantee ✅ COMPLIANT

**Status**: COMPLIANT

**Evidence**:
- All task operations persist to Neon PostgreSQL before publishing events
- Event producers (Chat API) commit database transaction THEN publish Kafka event
- Recurring Task Service persists generated occurrences before publishing completion event
- Notification Service logs all sent emails to audit log table
- WebSocket Sync Service does not persist connection state (ephemeral by design)

**Phase V Enhancements**:
- New tables: recurring_task_state (last_generated_at), audit_logs (all events), notification_history
- Event sourcing: Events published AFTER database commit (no dual writes without saga/outbox)

### IV. Test-First Development (NON-NEGOTIABLE) ✅ PLANNED

**Status**: COMPLIANT (will be enforced in /sp.tasks)

**Evidence**:
- All 87 functional requirements have testable acceptance criteria in spec.md
- Integration tests required for: Kafka producer/consumer, Dapr component interactions, event schema validation
- Contract tests required for: Event schemas (Task Event, Reminder Event, Task Update Event)
- E2E tests required for: Recurring task generation flow, reminder scheduling via Dapr Jobs API

**Phase V Test Coverage**:
- Unit tests: Event serialization/deserialization, idempotency key validation
- Integration tests: Kafka topic creation, Dapr pub/sub publish/subscribe, Dapr Jobs API scheduling
- E2E tests: Create recurring task → complete occurrence → verify next occurrence generated

### V. Conversational Error Handling ✅ COMPLIANT (Chat API only)

**Status**: COMPLIANT for user-facing Chat API; N/A for background services

**Evidence**:
- Chat API maintains conversational error messages for user interactions
- Background services (Recurring Task Service, Notification Service, Audit Service) log errors to structured logs
- Dead letter queue captures failed events for manual inspection
- WebSocket Sync Service sends user-friendly error messages to connected clients

**Phase V Error Handling**:
- Kafka consumer failures → retry with exponential backoff (max 5 retries) → dead letter queue
- Dapr Jobs API failures → logged with correlation ID for debugging
- Database connection errors → service restart via Kubernetes liveness probe

### VI. Natural Language Intent Mapping ✅ COMPLIANT (Chat API only)

**Status**: COMPLIANT for Chat API; N/A for event-driven services

**Evidence**:
- Chat API (Phase IV) continues to handle natural language → MCP tool mapping
- New services consume structured Kafka events (no NLU required)
- Event schemas enforce strict JSON structure with versioning

**Phase V Intent Extensions**:
- "Set reminder for tomorrow" → Chat API invokes MCP tool → publishes event with due_date
- "Make this task recurring every week" → Chat API invokes MCP tool → publishes event with recurrence_rule

### VII. Security and User Isolation ✅ COMPLIANT

**Status**: COMPLIANT

**Evidence**:
- All Kafka events include user_id in event payload
- Recurring Task Service filters events by user_id before processing
- Notification Service validates user_id ownership before sending reminders
- Audit Service logs include user_id for all actions
- WebSocket Sync Service authenticates JWT token on connection establishment

**Phase V Security Enhancements**:
- Kafka messages include user_id for multi-tenancy enforcement
- Dapr Secrets component secures SMTP credentials, Kafka SASL passwords
- Kubernetes RBAC restricts service account permissions per service
- Network policies (out of scope for Phase V but documented for Phase VI)

## Project Structure

### Documentation (this feature)

```text
specs/002-phase-v-cloud-deployment/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   ├── task-event-schema.json
│   ├── reminder-event-schema.json
│   ├── task-update-event-schema.json
│   └── kafka-topics.yaml
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── api-service/                     # Existing Phase IV service
│   ├── app/
│   │   ├── main.py                  # Enhanced with Dapr pub/sub integration
│   │   ├── models.py                # Extended: priority, tags, due_date, recurrence_rule
│   │   ├── agent.py                 # Existing MCP tool integration
│   │   ├── database.py              # Existing Neon PostgreSQL connection
│   │   ├── dapr_client.py           # NEW: Dapr HTTP client wrapper
│   │   └── events/                  # NEW: Event publishing logic
│   │       ├── __init__.py
│   │       ├── schemas.py           # Task Event, Reminder Event schemas
│   │       └── publisher.py         # Dapr pub/sub publish wrapper
│   ├── migrations/                  # NEW: Alembic migrations for Phase V schema
│   │   └── 003_add_phase_v_fields.sql
│   ├── Dockerfile                   # Updated with Dapr sidecar expectations
│   └── requirements.txt             # Added: httpx (Dapr client)
│
├── recurring-task-service/          # NEW: Event-driven task occurrence generator
│   ├── app/
│   │   ├── main.py                  # FastAPI app with Dapr subscription endpoint
│   │   ├── consumer.py              # Kafka consumer via Dapr pub/sub
│   │   ├── generator.py             # Recurrence rule processing logic
│   │   ├── models.py                # RecurringTaskState model
│   │   └── dapr_client.py           # Dapr State Management client
│   ├── tests/
│   │   ├── test_generator.py        # Unit tests for recurrence logic
│   │   └── test_consumer.py         # Integration tests with Kafka
│   ├── Dockerfile
│   └── requirements.txt             # FastAPI, httpx, python-dateutil
│
├── notification-service/            # NEW: Reminder email sender
│   ├── app/
│   │   ├── main.py                  # FastAPI app with Dapr subscription endpoint
│   │   ├── consumer.py              # Kafka consumer for reminders topic
│   │   ├── email_sender.py          # SMTP email logic
│   │   ├── dapr_client.py           # Dapr Secrets client for SMTP credentials
│   │   └── templates/               # Email templates
│   │       └── reminder.html
│   ├── tests/
│   │   ├── test_email_sender.py     # Unit tests with mocked SMTP
│   │   └── test_consumer.py         # Integration tests
│   ├── Dockerfile
│   └── requirements.txt             # FastAPI, httpx, aiosmtplib
│
├── audit-service/                   # NEW: Event logger for compliance
│   ├── app/
│   │   ├── main.py                  # FastAPI app with Dapr subscription endpoint
│   │   ├── consumer.py              # Multi-topic Kafka consumer
│   │   ├── models.py                # AuditLogEntry model
│   │   └── database.py              # Direct PostgreSQL write (high volume)
│   ├── tests/
│   │   └── test_consumer.py         # Integration tests
│   ├── Dockerfile
│   └── requirements.txt             # FastAPI, httpx, sqlmodel
│
├── websocket-sync-service/          # NEW: Real-time task update broadcaster
│   ├── src/
│   │   ├── server.ts                # Socket.IO server with Dapr integration
│   │   ├── consumer.ts              # Kafka consumer via Dapr pub/sub
│   │   ├── auth.ts                  # JWT token validation
│   │   └── dapr-client.ts           # Dapr HTTP client (TypeScript)
│   ├── tests/
│   │   └── consumer.test.ts         # Integration tests
│   ├── Dockerfile
│   ├── package.json                 # socket.io, axios (Dapr client)
│   └── tsconfig.json
│
└── auth-service/                    # Existing Phase IV service (no changes)

frontend/                            # Existing Phase IV service
├── src/
│   ├── components/
│   │   ├── TaskList.tsx             # Enhanced: priority badges, tag chips
│   │   ├── TaskForm.tsx             # Enhanced: priority dropdown, due date picker, recurrence selector
│   │   ├── TaskFilters.tsx          # NEW: Filter by priority, tags, status, due date
│   │   └── TaskSearch.tsx           # NEW: Search by keywords
│   ├── hooks/
│   │   └── useWebSocket.ts          # NEW: Socket.IO client for real-time updates
│   └── pages/
│       └── tasks.tsx                # Enhanced with filtering, sorting, search

charts/
├── todo-chatbot-frontend/           # Existing Phase IV chart
│   ├── Chart.yaml                   # Version bump to 2.0.0
│   ├── values.yaml                  # Dapr annotations added
│   └── templates/
│       └── deployment.yaml          # Enhanced with Dapr sidecar injection
│
└── todo-chatbot-backend/            # Enhanced Phase IV chart
    ├── Chart.yaml                   # Version bump to 2.0.0
    ├── values.yaml                  # NEW: 4 additional services + Dapr config
    ├── values-local.yaml            # NEW: Minikube-specific overrides
    ├── values-cloud.yaml            # NEW: AKS/GKE/OKE overrides
    └── templates/
        ├── api-deployment.yaml      # Enhanced with Dapr pub/sub annotations
        ├── api-service.yaml
        ├── recurring-task-deployment.yaml  # NEW
        ├── recurring-task-service.yaml     # NEW (ClusterIP)
        ├── notification-deployment.yaml    # NEW
        ├── notification-service.yaml       # NEW (ClusterIP)
        ├── audit-deployment.yaml           # NEW
        ├── audit-service.yaml              # NEW (ClusterIP)
        ├── websocket-deployment.yaml       # NEW
        ├── websocket-service.yaml          # NEW (LoadBalancer for cloud, NodePort for local)
        ├── dapr-components/                # NEW: Dapr component YAML
        │   ├── kafka-pubsub.yaml
        │   ├── postgres-statestore.yaml
        │   └── kubernetes-secrets.yaml
        └── configmap.yaml                  # Enhanced with Kafka broker URLs

dapr-components/                     # Dapr component configurations (deployed separately)
├── local/                           # Minikube environment
│   ├── kafka-pubsub.yaml            # Strimzi or Redpanda local brokers
│   ├── postgres-statestore.yaml     # Local Neon or PostgreSQL service
│   └── kubernetes-secrets.yaml
└── cloud/                           # AKS/GKE/OKE environment
    ├── kafka-pubsub.yaml            # Redpanda Cloud or Confluent Cloud
    ├── postgres-statestore.yaml     # Neon PostgreSQL (production tier)
    └── kubernetes-secrets.yaml

.github/
└── workflows/
    ├── ci-cd.yaml                   # NEW: GitHub Actions pipeline
    │   # - Build all 7 service images
    │   # - Run unit + integration tests
    │   # - Push images to registry
    │   # - Deploy to dev environment (auto)
    │   # - Deploy to prod (manual approval)
    └── rollback.yaml                # NEW: Automated rollback on failure

kubernetes/                          # Kubernetes-specific configs (not in Helm)
├── namespaces/
│   ├── dev.yaml
│   ├── staging.yaml
│   └── prod.yaml
├── secrets/                         # Sealed secrets or external secrets operator
│   └── backend-secrets.yaml
└── ingress/                         # Ingress controller configs (Phase VI)
    └── todo-app-ingress.yaml

tests/
├── contract/                        # Pact contract tests for event schemas
│   ├── test_task_event_contract.py
│   ├── test_reminder_event_contract.py
│   └── test_task_update_event_contract.py
├── integration/
│   ├── test_kafka_pubsub.py         # Dapr pub/sub integration tests
│   ├── test_dapr_state.py           # Dapr State Management tests
│   ├── test_dapr_jobs.py            # Dapr Jobs API tests
│   └── test_recurring_task_flow.py  # E2E: task created → occurrence generated
└── e2e/
    ├── test_user_journey.spec.ts    # Playwright: complete user workflow
    └── test_websocket_sync.spec.ts  # WebSocket real-time sync validation

docs/
├── DEPLOYMENT.md                    # NEW: Minikube + cloud deployment guide
├── ARCHITECTURE.md                  # NEW: Event-driven architecture overview
├── DAPR_GUIDE.md                    # NEW: Dapr component configuration reference
└── TROUBLESHOOTING.md               # NEW: Common deployment issues and fixes
```

**Structure Decision**: Web + Microservices architecture with 7 services (3 existing Phase IV services enhanced, 4 new event-driven services). Backend services are Python (FastAPI) for data-intensive workloads and Node.js (TypeScript) for WebSocket real-time sync. Helm charts reuse Phase IV structure with Dapr-specific enhancements (sidecar annotations, component configurations).

## Complexity Tracking

> **Justification for Constitution Extensions**:

**Extension 1: MCP-First Tool Integration (Extended)**

- **Violation**: New services (Recurring Task Service, Notification Service, Audit Service, WebSocket Sync Service) do NOT use MCP tools
- **Justification**: MCP is designed for AI-agent tool calling, not event-driven microservices. Event consumers process Kafka messages asynchronously and do not interact with AI agents.
- **Mitigation**: Chat API (AI agent interface) remains MCP-compliant. Constitution will be updated to clarify MCP applies only to AI-agent interfaces.

**Extension 2: Database Persistence Guarantee (Extended)**

- **Violation**: WebSocket Sync Service does not persist connection state
- **Justification**: WebSocket connections are ephemeral by design and do not require persistence. Connection registry stored in Dapr State for service-to-service lookup, not durability.
- **Mitigation**: All user-facing data (tasks, messages, events) remains persisted per constitution.

---

## Phase 0: Architecture & Validation

**Purpose**: Establish foundational understanding of Kubernetes, Dapr, Kafka, and event-driven patterns. Resolve all unknowns before design phase.

**Preconditions**: Spec.md complete, constitution reviewed

**Deliverables**:
1. `research.md` with decisions on:
   - Kafka deployment strategy (Strimzi vs Redpanda for local)
   - Dapr component configuration patterns (pub/sub, state, secrets, jobs)
   - Event schema versioning strategy
   - Idempotency key generation approach
   - Dead letter queue handling patterns
   - Kubernetes namespace strategy (single vs multi-namespace)
   - Helm chart upgrade strategy (Phase IV → Phase V migration)

**Steps**:

### 0.1: Research Kafka Deployment Options

**Task**: Evaluate Kafka deployment strategies for local (Minikube) and cloud (Redpanda Cloud/Confluent Cloud) environments

**Research Questions**:
- Strimzi Operator vs Redpanda single binary: resource footprint, ease of setup, operational complexity
- Redpanda Cloud Free Tier limits: 10GB retention, 10MB/s throughput sufficient for dev/staging?
- Confluent Cloud vs Redpanda Cloud: pricing, features, Dapr compatibility
- Kafka topic creation: manual via CLI, automated via Helm hooks, or application-driven?
- Topic configuration: partition count (6 recommended), replication factor (3 for prod), retention (7 days)

**Output**: `research.md` section documenting:
- **Decision**: Redpanda for local (single binary, low resource), Redpanda Cloud for staging/dev, Confluent Cloud as prod alternative
- **Rationale**: Redpanda has lower memory footprint than Strimzi (single Go binary vs JVM), compatible with Kafka protocol, free tier available
- **Alternatives**: Strimzi (heavier but more Kafka-native), Confluent Cloud (more expensive but enterprise features)

### 0.2: Research Dapr Component Configuration Patterns

**Task**: Define Dapr component YAML structure for pub/sub, state, secrets, and jobs

**Research Questions**:
- Pub/Sub component metadata: broker list, SASL auth, consumer group ID, topic creation behavior
- State Management component: PostgreSQL connection string handling, table prefix, timeout configuration
- Secrets component: Kubernetes native vs external (Vault, AWS Secrets Manager)
- Jobs API: scheduling syntax, callback endpoint, failure retry behavior
- Component scoping: global vs service-specific (scopes field)

**Output**: `research.md` section documenting:
- **Decision**: Kubernetes-native secrets for Phase V (simplicity), external secrets for Phase VI (production hardening)
- **Rationale**: Kubernetes Secrets sufficient for free-tier deployments, easy Dapr integration, no external dependencies
- **Alternatives**: HashiCorp Vault (requires separate deployment), cloud provider secret managers (vendor lock-in)

### 0.3: Research Event Schema Versioning Strategy

**Task**: Define approach for evolving event schemas without breaking consumers

**Research Questions**:
- Schema version field: semver string, integer, timestamp?
- Breaking vs non-breaking changes: adding fields (safe), removing fields (breaking), changing types (breaking)
- Consumer compatibility: ignore unknown fields, validate schema version, reject unknown versions?
- Schema registry: Confluent Schema Registry (not in scope), JSON Schema files in repo, Pact contract tests?

**Output**: `research.md` section documenting:
- **Decision**: Schema version as string field (e.g., "1.0"), additive changes only (new fields nullable), JSON Schema validation in tests
- **Rationale**: Simple versioning without registry infrastructure, consumers ignore unknown fields for forward compatibility
- **Alternatives**: Confluent Schema Registry (adds infrastructure), Protobuf (requires code generation)

### 0.4: Research Idempotency Key Generation

**Task**: Define strategy for generating unique event IDs to prevent duplicate processing

**Research Questions**:
- ID format: UUID v4, UUID v7 (timestamp-based), ULID (sortable)?
- ID generation: client-side (producer), server-side (Kafka broker), hybrid?
- Duplicate detection: consumer tracks processed IDs in database, Dapr State, in-memory cache?
- ID TTL: how long to retain processed IDs (1 day, 7 days, retention period)?

**Output**: `research.md` section documenting:
- **Decision**: UUID v4 client-side generation, consumer tracks in Dapr State with 7-day TTL
- **Rationale**: UUID v4 universally unique, client-side avoids broker dependency, Dapr State provides distributed storage
- **Alternatives**: UUID v7 (sortable but newer library support), ULID (custom library), database-tracked IDs (query overhead)

### 0.5: Research Dead Letter Queue Patterns

**Task**: Define DLQ handling for events that fail max retry attempts

**Research Questions**:
- DLQ topic naming: `{source-topic}.dlq`, `dlq-events` (single topic), per-consumer DLQ?
- DLQ payload: original event + error metadata (stack trace, retry count, failure timestamp)?
- DLQ consumption: manual inspection, automated retry service, alerting integration?
- DLQ retention: 30 days (longer than source topics) for investigation?

**Output**: `research.md` section documenting:
- **Decision**: Single `dlq-events` topic with 30-day retention, payload includes original event + error context
- **Rationale**: Centralized DLQ simplifies monitoring, longer retention for root cause analysis
- **Alternatives**: Per-topic DLQ (topic sprawl), per-consumer DLQ (consumer coupling)

### 0.6: Research Kubernetes Namespace Strategy

**Task**: Define namespace isolation for dev, staging, prod environments

**Research Questions**:
- Namespace per environment: `todo-app-dev`, `todo-app-staging`, `todo-app-prod`?
- Namespace per feature: `002-phase-v-cloud-deployment`?
- Resource quotas: CPU/memory limits per namespace?
- Network policies: isolate namespaces or allow cross-namespace communication?

**Output**: `research.md` section documenting:
- **Decision**: Environment-based namespaces (`todo-app-dev`, `todo-app-staging`, `todo-app-prod`), no feature-based namespaces
- **Rationale**: Environment isolation prevents dev/staging from affecting prod, resource quotas enforced per env
- **Alternatives**: Single namespace with labels (less isolation), feature namespaces (ephemeral complexity)

### 0.7: Research Helm Chart Upgrade Strategy

**Task**: Define migration path from Phase IV charts to Phase V Dapr-enhanced charts

**Research Questions**:
- In-place upgrade: `helm upgrade` existing releases with new values?
- Blue-green deployment: deploy Phase V alongside Phase IV, switch traffic?
- Data migration: Alembic migrations for new schema fields before or after deployment?
- Rollback strategy: `helm rollback` restores Phase IV state?

**Output**: `research.md` section documenting:
- **Decision**: In-place upgrade with pre-upgrade Alembic migration job (Helm hook), rollback via `helm rollback`
- **Rationale**: In-place upgrade simplest for non-production, migration job ensures schema before app starts
- **Alternatives**: Blue-green (requires 2x resources), separate Phase V namespace (data duplication)

**Phase 0 Exit Criteria**:
- All NEEDS CLARIFICATION items in Technical Context resolved
- `research.md` complete with decisions, rationale, alternatives for all 7 research questions
- No conflicting decisions or technical debt introduced

---

## Phase 1: Advanced Feature Enablement

**Purpose**: Extend database schema and API contracts to support recurring tasks, due dates, priority, tags, search/filter/sort

**Preconditions**: Phase 0 research complete

**Deliverables**:
1. `data-model.md` documenting new entities and schema changes
2. Alembic migration script `003_add_phase_v_fields.sql`
3. Updated SQLModel models in `api-service/app/models.py`
4. API contract enhancements in `contracts/task-api-openapi.yaml`

**Steps**:

### 1.1: Design Database Schema Extensions

**Task**: Extend `tasks` table with Phase V fields

**Schema Changes**:
```sql
ALTER TABLE tasks ADD COLUMN priority VARCHAR(10) CHECK (priority IN ('low', 'medium', 'high', 'urgent'));
ALTER TABLE tasks ADD COLUMN tags TEXT[]; -- PostgreSQL array type
ALTER TABLE tasks ADD COLUMN due_date TIMESTAMPTZ;
ALTER TABLE tasks ADD COLUMN reminder_offset INTERVAL; -- e.g., '1 day', '1 hour'
ALTER TABLE tasks ADD COLUMN recurrence_rule JSONB; -- {frequency, interval, days_of_week, day_of_month, end_date}
ALTER TABLE tasks ADD COLUMN parent_task_id INTEGER REFERENCES tasks(id) ON DELETE CASCADE; -- Link recurring occurrences
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_tags ON tasks USING GIN(tags); -- GIN index for array containment
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
CREATE INDEX idx_tasks_parent_id ON tasks(parent_task_id);
```

**New Table**:
```sql
CREATE TABLE recurring_task_state (
  task_id INTEGER PRIMARY KEY REFERENCES tasks(id) ON DELETE CASCADE,
  last_generated_at TIMESTAMPTZ NOT NULL,
  next_occurrence_due TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Output**: `data-model.md` documenting:
- Task entity with new fields (priority, tags, due_date, reminder_offset, recurrence_rule, parent_task_id)
- RecurringTaskState entity (task_id, last_generated_at, next_occurrence_due)
- Indexes for query performance (priority, tags GIN, due_date, parent_task_id)

### 1.2: Update SQLModel Models

**Task**: Add new fields to `Task` model in `api-service/app/models.py`

**Changes**:
```python
from sqlmodel import SQLModel, Field
from typing import Optional, List
from datetime import datetime, timedelta
from enum import Enum

class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"

class RecurrenceRule(SQLModel):
    frequency: str  # "daily", "weekly", "monthly"
    interval: int = 1  # Every N days/weeks/months
    days_of_week: Optional[List[int]] = None  # 0-6 for weekly
    day_of_month: Optional[int] = None  # 1-31 for monthly
    end_date: Optional[datetime] = None

class Task(SQLModel, table=True):
    # ... existing fields (id, user_id, title, description, status, created_at, updated_at, completed_at)
    priority: Optional[Priority] = None
    tags: Optional[List[str]] = Field(default=None, sa_column=Column(ARRAY(String)))
    due_date: Optional[datetime] = None
    reminder_offset: Optional[timedelta] = None  # Stored as INTERVAL in PostgreSQL
    recurrence_rule: Optional[RecurrenceRule] = Field(default=None, sa_column=Column(JSON))
    parent_task_id: Optional[int] = Field(default=None, foreign_key="task.id")

class RecurringTaskState(SQLModel, table=True):
    task_id: int = Field(primary_key=True, foreign_key="task.id")
    last_generated_at: datetime
    next_occurrence_due: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Output**: Updated `api-service/app/models.py` with new fields and validation

### 1.3: Create Alembic Migration Script

**Task**: Generate migration for Phase V schema changes

**Steps**:
1. Auto-generate migration: `alembic revision --autogenerate -m "Add Phase V fields: priority, tags, due_date, recurrence_rule"`
2. Review and edit migration file: `backend/api-service/migrations/versions/003_add_phase_v_fields.py`
3. Add rollback logic: `downgrade()` function drops columns and indexes

**Output**: `migrations/versions/003_add_phase_v_fields.py` with upgrade/downgrade functions

### 1.4: Extend API Contracts

**Task**: Update OpenAPI schema for task creation/update endpoints

**Changes**:
```yaml
# contracts/task-api-openapi.yaml
TaskCreate:
  type: object
  properties:
    title: {type: string, minLength: 1, maxLength: 200}
    description: {type: string, maxLength: 2000}
    priority: {type: string, enum: [low, medium, high, urgent]}
    tags: {type: array, items: {type: string}, maxItems: 10}
    due_date: {type: string, format: date-time}
    reminder_offset: {type: string, pattern: '^P(\d+D)?(T(\d+H)?(\d+M)?)?$'}  # ISO 8601 duration
    recurrence_rule:
      type: object
      properties:
        frequency: {type: string, enum: [daily, weekly, monthly]}
        interval: {type: integer, minimum: 1, maximum: 365}
        days_of_week: {type: array, items: {type: integer, minimum: 0, maximum: 6}}
        day_of_month: {type: integer, minimum: 1, maximum: 31}
        end_date: {type: string, format: date-time}
  required: [title]

TaskResponse:
  allOf:
    - $ref: '#/components/schemas/TaskCreate'
    - type: object
      properties:
        id: {type: integer}
        user_id: {type: integer}
        status: {type: string, enum: [pending, in_progress, completed]}
        parent_task_id: {type: integer, nullable: true}
        created_at: {type: string, format: date-time}
        updated_at: {type: string, format: date-time}
        completed_at: {type: string, format: date-time, nullable: true}
```

**Output**: Updated `contracts/task-api-openapi.yaml` with new fields

### 1.5: Implement Search/Filter/Sort Endpoints

**Task**: Add query parameters to `GET /api/tasks` endpoint

**Query Parameters**:
```python
@router.get("/api/tasks", response_model=List[TaskResponse])
async def list_tasks(
    user_id: int = Depends(get_current_user_id),
    status: Optional[str] = None,  # pending, in_progress, completed
    priority: Optional[Priority] = None,
    tags: Optional[List[str]] = Query(None),  # Multiple tags (OR logic)
    due_date_start: Optional[datetime] = None,
    due_date_end: Optional[datetime] = None,
    search: Optional[str] = None,  # Keyword search in title/description
    sort_by: str = "created_at",  # created_at, due_date, priority, updated_at
    sort_order: str = "desc",  # asc, desc
    limit: int = 100,
    offset: int = 0
):
    query = select(Task).where(Task.user_id == user_id)

    if status:
        query = query.where(Task.status == status)
    if priority:
        query = query.where(Task.priority == priority)
    if tags:
        query = query.where(Task.tags.overlap(tags))  # PostgreSQL array overlap
    if due_date_start:
        query = query.where(Task.due_date >= due_date_start)
    if due_date_end:
        query = query.where(Task.due_date <= due_date_end)
    if search:
        query = query.where(
            or_(
                Task.title.ilike(f"%{search}%"),
                Task.description.ilike(f"%{search}%")
            )
        )

    # Sorting
    sort_column = getattr(Task, sort_by)
    query = query.order_by(desc(sort_column) if sort_order == "desc" else asc(sort_column))

    query = query.limit(limit).offset(offset)

    tasks = await session.execute(query)
    return tasks.scalars().all()
```

**Output**: Enhanced `GET /api/tasks` endpoint with filtering, search, sorting, pagination

### 1.6: Update Frontend Components

**Task**: Enhance frontend UI with priority badges, tag chips, due date picker, recurrence selector

**Components to Update**:
- `TaskForm.tsx`: Add priority dropdown, tags input, due date picker, recurrence selector
- `TaskList.tsx`: Display priority badges, tag chips, due date with countdown
- `TaskFilters.tsx` (NEW): Filter UI for priority, tags, status, due date range
- `TaskSearch.tsx` (NEW): Search input with debouncing

**Output**: Updated frontend components in `frontend/src/components/`

**Phase 1 Exit Criteria**:
- `data-model.md` complete with schema changes documented
- Alembic migration tested locally (upgrade + downgrade)
- SQLModel models updated with new fields and validation
- OpenAPI contract updated and validated against spec
- Search/filter/sort endpoint implemented with query performance validated (< 1 second for 10K tasks)

---

## Phase 2: Event-Driven Backbone (Kafka)

**Purpose**: Provision Kafka topics, define event schemas, implement event publishing from Chat API

**Preconditions**: Phase 1 complete, research.md Kafka deployment decision finalized

**Deliverables**:
1. Kafka topic creation scripts (`contracts/kafka-topics.yaml`)
2. Event schema JSON files (`contracts/task-event-schema.json`, `contracts/reminder-event-schema.json`, `contracts/task-update-event-schema.json`)
3. Event publisher module in Chat API (`api-service/app/events/publisher.py`)
4. Dapr Pub/Sub component YAML (`dapr-components/local/kafka-pubsub.yaml`, `dapr-components/cloud/kafka-pubsub.yaml`)

**Steps**:

### 2.1: Provision Kafka Topics

**Task**: Create Kafka topics via Kubernetes manifest (Strimzi KafkaTopic CRD or manual `kafka-topics.sh`)

**Topic Specifications**:
```yaml
# contracts/kafka-topics.yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: task-events
  labels:
    strimzi.io/cluster: todo-kafka-cluster
spec:
  partitions: 6
  replicas: 3  # 3 for prod, 1 for local
  config:
    retention.ms: 604800000  # 7 days
    compression.type: snappy
    min.insync.replicas: 2  # Durability guarantee (prod only)
---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: reminders
spec:
  partitions: 3
  replicas: 3
  config:
    retention.ms: 604800000  # 7 days
---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: task-updates
spec:
  partitions: 6
  replicas: 3
  config:
    retention.ms: 86400000  # 1 day (shorter retention for UI updates)
---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: dlq-events
spec:
  partitions: 3
  replicas: 3
  config:
    retention.ms: 2592000000  # 30 days (longer for investigation)
```

**Output**: `contracts/kafka-topics.yaml` with 4 topic definitions

### 2.2: Define Event Schemas

**Task**: Create JSON Schema files for Task Event, Reminder Event, Task Update Event

**Task Event Schema**:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://todo-chatbot.com/schemas/task-event.json",
  "title": "Task Event",
  "type": "object",
  "required": ["event_id", "schema_version", "event_type", "timestamp", "task_id", "user_id", "task_data"],
  "properties": {
    "event_id": {"type": "string", "format": "uuid"},
    "schema_version": {"type": "string", "pattern": "^\\d+\\.\\d+$"},
    "event_type": {"type": "string", "enum": ["task.created", "task.updated", "task.deleted", "task.completed"]},
    "timestamp": {"type": "string", "format": "date-time"},
    "task_id": {"type": "integer"},
    "user_id": {"type": "integer"},
    "task_data": {
      "type": "object",
      "required": ["title", "status"],
      "properties": {
        "title": {"type": "string", "minLength": 1, "maxLength": 200},
        "description": {"type": "string", "maxLength": 2000},
        "status": {"type": "string", "enum": ["pending", "in_progress", "completed"]},
        "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"]},
        "tags": {"type": "array", "items": {"type": "string"}},
        "due_date": {"type": "string", "format": "date-time"},
        "reminder_offset": {"type": "string"},
        "recurrence_rule": {
          "type": "object",
          "properties": {
            "frequency": {"type": "string", "enum": ["daily", "weekly", "monthly"]},
            "interval": {"type": "integer"},
            "days_of_week": {"type": "array", "items": {"type": "integer", "minimum": 0, "maximum": 6}},
            "day_of_month": {"type": "integer", "minimum": 1, "maximum": 31},
            "end_date": {"type": "string", "format": "date-time"}
          }
        },
        "parent_task_id": {"type": "integer"}
      }
    }
  }
}
```

**Output**: `contracts/task-event-schema.json`, `contracts/reminder-event-schema.json`, `contracts/task-update-event-schema.json`

### 2.3: Implement Event Publisher in Chat API

**Task**: Create Dapr HTTP client wrapper for publishing events

**Module Structure**:
```python
# api-service/app/events/schemas.py
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import uuid4

class TaskEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    schema_version: str = "1.0"
    event_type: str  # task.created, task.updated, task.deleted, task.completed
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    task_id: int
    user_id: int
    task_data: dict

# api-service/app/events/publisher.py
import httpx
from typing import Optional

class DaprPublisher:
    def __init__(self, dapr_url: str = "http://localhost:3500"):
        self.dapr_url = dapr_url
        self.pubsub_name = "kafka-pubsub"

    async def publish_task_event(self, event: TaskEvent) -> bool:
        """Publish task event to task-events topic via Dapr Pub/Sub"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.dapr_url}/v1.0/publish/{self.pubsub_name}/task-events",
                    json=event.dict(),
                    timeout=5.0
                )
                response.raise_for_status()
                return True
        except httpx.HTTPError as e:
            # Log error with correlation ID
            logger.error(f"Failed to publish event {event.event_id}: {e}")
            return False

    async def publish_reminder_event(self, event: ReminderEvent) -> bool:
        """Publish reminder event to reminders topic via Dapr Pub/Sub"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.dapr_url}/v1.0/publish/{self.pubsub_name}/reminders",
                json=event.dict()
            )
            response.raise_for_status()
            return True

    async def publish_task_update_event(self, event: TaskUpdateEvent) -> bool:
        """Publish task update event to task-updates topic for WebSocket sync"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.dapr_url}/v1.0/publish/{self.pubsub_name}/task-updates",
                json=event.dict()
            )
            response.raise_for_status()
            return True
```

**Output**: Event publisher module with Dapr HTTP client

### 2.4: Integrate Event Publishing into Chat API Endpoints

**Task**: Publish events after database commits in task CRUD endpoints

**Example Integration**:
```python
# api-service/app/main.py
from app.events.publisher import DaprPublisher
from app.events.schemas import TaskEvent

publisher = DaprPublisher()

@router.post("/api/tasks", response_model=TaskResponse)
async def create_task(task_data: TaskCreate, user_id: int = Depends(get_current_user_id)):
    # 1. Persist to database (existing logic)
    task = Task(**task_data.dict(), user_id=user_id, status="pending")
    session.add(task)
    await session.commit()
    await session.refresh(task)

    # 2. Publish event to Kafka via Dapr
    event = TaskEvent(
        event_type="task.created",
        task_id=task.id,
        user_id=user_id,
        task_data=task.dict()
    )
    await publisher.publish_task_event(event)

    # 3. If due_date and reminder_offset exist, publish reminder event
    if task.due_date and task.reminder_offset:
        await publisher.publish_task_update_event(TaskUpdateEvent(...))

    return task
```

**Output**: Enhanced CRUD endpoints with event publishing

### 2.5: Create Dapr Pub/Sub Component Configuration

**Task**: Define Dapr Pub/Sub component YAML for local and cloud Kafka

**Local Configuration (Strimzi/Redpanda)**:
```yaml
# dapr-components/local/kafka-pubsub.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
  namespace: todo-app-dev
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "redpanda-0.redpanda.todo-app-dev.svc.cluster.local:9092"
    - name: consumerGroup
      value: "todo-app-consumers"
    - name: authType
      value: "none"  # No auth for local
    - name: maxMessageBytes
      value: "1048576"  # 1MB max message size
```

**Cloud Configuration (Redpanda Cloud/Confluent Cloud)**:
```yaml
# dapr-components/cloud/kafka-pubsub.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
  namespace: todo-app-prod
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "kafka.redpanda.cloud:9092"
    - name: consumerGroup
      value: "todo-app-consumers"
    - name: authType
      value: "password"
    - name: saslUsername
      secretKeyRef:
        name: kafka-secrets
        key: username
    - name: saslPassword
      secretKeyRef:
        name: kafka-secrets
        key: password
    - name: saslMechanism
      value: "SCRAM-SHA-256"
    - name: enableTLS
      value: "true"
```

**Output**: Dapr Pub/Sub component YAML for local and cloud environments

### 2.6: Deploy Kafka to Minikube (Local)

**Task**: Install Strimzi Operator or Redpanda Helm chart on Minikube

**Option A: Redpanda (Recommended for Resource Constraints)**:
```bash
helm repo add redpanda https://charts.redpanda.com/
helm install redpanda redpanda/redpanda \
  --namespace todo-app-dev \
  --create-namespace \
  --set replicas=1 \
  --set resources.cpu.cores=1 \
  --set resources.memory.container.max=1Gi \
  --set storage.persistentVolume.size=5Gi
```

**Option B: Strimzi Operator**:
```bash
kubectl create namespace todo-app-dev
kubectl apply -f https://strimzi.io/install/latest?namespace=todo-app-dev
kubectl apply -f contracts/kafka-topics.yaml -n todo-app-dev
```

**Output**: Kafka cluster running in Minikube with 4 topics created

**Phase 2 Exit Criteria**:
- Kafka topics created and accessible (verify with `kafka-topics.sh --list`)
- Event schemas validated with JSON Schema validator
- Event publisher module unit tested (mocked Dapr HTTP calls)
- Integration test: Publish event from Chat API → verify message in Kafka topic
- Dapr Pub/Sub component deployed and tested (`dapr dashboard` shows component)

---

## Phase 3: Dapr Integration

**Purpose**: Install Dapr on Kubernetes, configure Dapr components (pub/sub, state, secrets, jobs), enable sidecar injection

**Preconditions**: Phase 2 complete, Kafka cluster running

**Deliverables**:
1. Dapr installed on Minikube and cloud clusters (`dapr init -k`)
2. Dapr State Management component YAML (`dapr-components/local/postgres-statestore.yaml`)
3. Dapr Secrets component YAML (`dapr-components/local/kubernetes-secrets.yaml`)
4. Helm chart templates updated with Dapr annotations (`dapr.io/enabled: "true"`)
5. Dapr Jobs API integration in Chat API (reminder scheduling)

**Steps**:

### 3.1: Install Dapr on Minikube

**Task**: Install Dapr control plane on local Kubernetes cluster

**Commands**:
```bash
# Initialize Dapr on Kubernetes
dapr init -k --wait --timeout 600

# Verify Dapr installation
dapr status -k

# Expected output:
#   NAME                   NAMESPACE    HEALTHY  STATUS   REPLICAS  VERSION  AGE  CREATED
#   dapr-operator          dapr-system  True     Running  1         1.12.0   30s  2026-01-02 10:00:00
#   dapr-sidecar-injector  dapr-system  True     Running  1         1.12.0   30s  2026-01-02 10:00:00
#   dapr-sentry            dapr-system  True     Running  1         1.12.0   30s  2026-01-02 10:00:00
#   dapr-placement-server  dapr-system  True     Running  1         1.12.0   30s  2026-01-02 10:00:00
```

**Output**: Dapr control plane pods running in `dapr-system` namespace

### 3.2: Create Dapr State Management Component

**Task**: Configure Dapr State component to use Neon PostgreSQL

**Component YAML**:
```yaml
# dapr-components/local/postgres-statestore.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: postgres-statestore
  namespace: todo-app-dev
spec:
  type: state.postgresql
  version: v1
  metadata:
    - name: connectionString
      secretKeyRef:
        name: backend-secrets
        key: DATABASE_URL
    - name: tableName
      value: "dapr_state"
    - name: metadataTableName
      value: "dapr_state_metadata"
    - name: timeoutInSeconds
      value: "30"
```

**Database Schema**:
```sql
-- Dapr State Management tables (auto-created by Dapr)
CREATE TABLE IF NOT EXISTS dapr_state (
  key TEXT NOT NULL PRIMARY KEY,
  value JSONB NOT NULL,
  etag TEXT,
  creationTime TIMESTAMPTZ NOT NULL,
  updateTime TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS dapr_state_metadata (
  key TEXT NOT NULL PRIMARY KEY,
  value TEXT NOT NULL
);
```

**Output**: Dapr State component configured for PostgreSQL

### 3.3: Create Dapr Secrets Component

**Task**: Configure Dapr Secrets component to use Kubernetes Secrets

**Component YAML**:
```yaml
# dapr-components/local/kubernetes-secrets.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kubernetes-secrets
  namespace: todo-app-dev
spec:
  type: secretstores.kubernetes
  version: v1
  metadata: []
```

**Output**: Dapr Secrets component configured for Kubernetes native secrets

### 3.4: Enable Dapr Sidecar Injection in Helm Charts

**Task**: Add Dapr annotations to Kubernetes Deployment templates

**Deployment Template Enhancement**:
```yaml
# charts/todo-chatbot-backend/templates/api-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-service
spec:
  replicas: 3
  template:
    metadata:
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "api-service"
        dapr.io/app-port: "8000"
        dapr.io/enable-api-logging: "true"
        dapr.io/log-level: "info"
        dapr.io/config: "dapr-config"
    spec:
      containers:
        - name: api-service
          image: todo-chatbot-api:v2.0.0
          ports:
            - containerPort: 8000
          env:
            - name: DAPR_HTTP_PORT
              value: "3500"
            - name: DAPR_GRPC_PORT
              value: "50001"
```

**Output**: Helm chart templates updated with Dapr sidecar injection annotations

### 3.5: Implement Dapr State Management in Recurring Task Service

**Task**: Use Dapr State API to track last generated occurrence timestamp

**State Management Client**:
```python
# recurring-task-service/app/dapr_client.py
import httpx
from typing import Optional

class DaprStateClient:
    def __init__(self, dapr_url: str = "http://localhost:3500"):
        self.dapr_url = dapr_url
        self.store_name = "postgres-statestore"

    async def save_state(self, key: str, value: dict) -> bool:
        """Save state to Dapr State Management"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.dapr_url}/v1.0/state/{self.store_name}",
                json=[{"key": key, "value": value}]
            )
            response.raise_for_status()
            return True

    async def get_state(self, key: str) -> Optional[dict]:
        """Retrieve state from Dapr State Management"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.dapr_url}/v1.0/state/{self.store_name}/{key}"
            )
            if response.status_code == 204:  # No content
                return None
            response.raise_for_status()
            return response.json()

    async def delete_state(self, key: str) -> bool:
        """Delete state from Dapr State Management"""
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{self.dapr_url}/v1.0/state/{self.store_name}/{key}"
            )
            response.raise_for_status()
            return True
```

**Usage in Recurring Task Service**:
```python
# recurring-task-service/app/generator.py
async def generate_next_occurrence(task_id: int, recurrence_rule: dict):
    state_client = DaprStateClient()

    # Load last generated timestamp from Dapr State
    state = await state_client.get_state(f"recurring-task-{task_id}")
    last_generated = state.get("last_generated_at") if state else None

    # Calculate next occurrence based on recurrence rule
    next_due = calculate_next_occurrence(last_generated, recurrence_rule)

    # Save new occurrence to database
    new_task = create_task_occurrence(task_id, next_due)

    # Update state with new timestamp
    await state_client.save_state(
        f"recurring-task-{task_id}",
        {"last_generated_at": datetime.utcnow().isoformat(), "next_due": next_due.isoformat()}
    )

    return new_task
```

**Output**: Dapr State Management integrated into Recurring Task Service

### 3.6: Implement Dapr Jobs API for Reminder Scheduling

**Task**: Schedule reminder jobs using Dapr Jobs API (v1.12+)

**Jobs API Integration in Chat API**:
```python
# api-service/app/dapr_client.py
class DaprJobsClient:
    def __init__(self, dapr_url: str = "http://localhost:3500"):
        self.dapr_url = dapr_url

    async def schedule_job(self, job_name: str, due_time: datetime, data: dict) -> bool:
        """Schedule a job using Dapr Jobs API"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.dapr_url}/v1.0-alpha1/jobs/{job_name}",
                json={
                    "dueTime": due_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "data": data,
                    "ttl": "168h"  # 7 days TTL
                }
            )
            response.raise_for_status()
            return True

    async def delete_job(self, job_name: str) -> bool:
        """Cancel a scheduled job"""
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{self.dapr_url}/v1.0-alpha1/jobs/{job_name}"
            )
            response.raise_for_status()
            return True

# Usage in task creation
async def create_task_with_reminder(task_data: TaskCreate):
    task = Task(**task_data.dict())
    session.add(task)
    await session.commit()

    # Schedule reminder if due_date and reminder_offset provided
    if task.due_date and task.reminder_offset:
        reminder_time = task.due_date - task.reminder_offset
        jobs_client = DaprJobsClient()
        await jobs_client.schedule_job(
            job_name=f"reminder-task-{task.id}",
            due_time=reminder_time,
            data={"task_id": task.id, "user_id": task.user_id}
        )
```

**Jobs Callback Endpoint**:
```python
# api-service/app/main.py
@router.post("/api/jobs/trigger")
async def handle_job_trigger(request: Request):
    """Dapr calls this endpoint when scheduled job fires"""
    job_data = await request.json()

    # Publish reminder event to Kafka
    event = ReminderEvent(
        event_type="reminder.due",
        task_id=job_data["data"]["task_id"],
        user_id=job_data["data"]["user_id"],
        due_date=datetime.utcnow()
    )
    await publisher.publish_reminder_event(event)

    return {"status": "SUCCESS"}
```

**Output**: Dapr Jobs API integrated for reminder scheduling

### 3.7: Deploy Dapr Components to Kubernetes

**Task**: Apply Dapr component YAML files to Kubernetes cluster

**Commands**:
```bash
# Deploy Dapr components to dev namespace
kubectl apply -f dapr-components/local/kafka-pubsub.yaml
kubectl apply -f dapr-components/local/postgres-statestore.yaml
kubectl apply -f dapr-components/local/kubernetes-secrets.yaml

# Verify components
kubectl get components -n todo-app-dev

# Expected output:
#   NAME                   AGE
#   kafka-pubsub           10s
#   postgres-statestore    10s
#   kubernetes-secrets     10s
```

**Output**: Dapr components deployed and accessible to services

**Phase 3 Exit Criteria**:
- Dapr control plane running in `dapr-system` namespace
- All 3 Dapr components deployed (pub/sub, state, secrets)
- Dapr sidecar injected into all service pods (verify with `kubectl get pods -n todo-app-dev -o jsonpath='{.items[*].spec.containers[*].name}'`)
- Dapr State API tested: save/get/delete state via HTTP endpoint
- Dapr Jobs API tested: schedule job → verify callback endpoint invoked
- Integration test: Publish event via Dapr → consume in subscriber

---

## Phase 4: Local Kubernetes Deployment (Minikube)

**Purpose**: Deploy all services to Minikube with Dapr sidecars, Kafka topics, and validate end-to-end flows

**Preconditions**: Phase 3 complete, Dapr components configured

**Deliverables**:
1. Helm values file for local deployment (`charts/todo-chatbot-backend/values-local.yaml`)
2. Docker images built and loaded into Minikube (`minikube image load`)
3. All services deployed and running (verify with `kubectl get pods`)
4. End-to-end test: Create recurring task → verify occurrence generated → verify reminder scheduled

**Steps**:

### 4.1: Build Docker Images for New Services

**Task**: Build Docker images for Recurring Task Service, Notification Service, Audit Service, WebSocket Sync Service

**Build Commands**:
```bash
# Recurring Task Service
cd backend/recurring-task-service
docker build -t todo-recurring-task:v1.0.0 .

# Notification Service
cd backend/notification-service
docker build -t todo-notification:v1.0.0 .

# Audit Service
cd backend/audit-service
docker build -t todo-audit:v1.0.0 .

# WebSocket Sync Service
cd backend/websocket-sync-service
docker build -t todo-websocket-sync:v1.0.0 .

# Rebuild Chat API with Phase V enhancements
cd backend/api-service
docker build -t todo-chatbot-api:v2.0.0 .
```

**Output**: 5 Docker images built

### 4.2: Load Images into Minikube

**Task**: Load Docker images into Minikube's Docker daemon

**Commands**:
```bash
minikube image load todo-recurring-task:v1.0.0
minikube image load todo-notification:v1.0.0
minikube image load todo-audit:v1.0.0
minikube image load todo-websocket-sync:v1.0.0
minikube image load todo-chatbot-api:v2.0.0

# Verify images
minikube image ls | grep todo
```

**Output**: Images available in Minikube registry

### 4.3: Create Helm Values for Local Deployment

**Task**: Create `values-local.yaml` with Minikube-specific configuration

**values-local.yaml**:
```yaml
# charts/todo-chatbot-backend/values-local.yaml
global:
  environment: local
  daprEnabled: true

apiService:
  image:
    repository: todo-chatbot-api
    tag: v2.0.0
    pullPolicy: IfNotPresent
  replicas: 1
  resources:
    requests:
      cpu: 100m
      memory: 256Mi
    limits:
      cpu: 500m
      memory: 512Mi
  dapr:
    appId: api-service
    appPort: 8000
    enabled: true

recurringTaskService:
  image:
    repository: todo-recurring-task
    tag: v1.0.0
    pullPolicy: IfNotPresent
  replicas: 1
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 250m
      memory: 256Mi
  dapr:
    appId: recurring-task-service
    appPort: 8001
    enabled: true

notificationService:
  image:
    repository: todo-notification
    tag: v1.0.0
    pullPolicy: IfNotPresent
  replicas: 1
  dapr:
    appId: notification-service
    appPort: 8002
    enabled: true

auditService:
  image:
    repository: todo-audit
    tag: v1.0.0
    pullPolicy: IfNotPresent
  replicas: 1
  dapr:
    appId: audit-service
    appPort: 8003
    enabled: true

websocketSyncService:
  image:
    repository: todo-websocket-sync
    tag: v1.0.0
    pullPolicy: IfNotPresent
  replicas: 1
  service:
    type: NodePort
    nodePort: 30082
  dapr:
    appId: websocket-sync-service
    appPort: 3001
    enabled: true

secrets:
  databaseUrl: "postgresql://user:pass@neon-host/db"
  kafkaBrokers: "redpanda-0.redpanda.todo-app-dev.svc.cluster.local:9092"
  smtpUser: "email@gmail.com"
  smtpPassword: "app-password"
  geminiApiKey: "AIzaSy..."
  openaiApiKey: "sk-proj-..."
```

**Output**: `values-local.yaml` with local-specific configuration

### 4.4: Create Helm Chart Templates for New Services

**Task**: Create Kubernetes Deployment and Service templates for new services

**Recurring Task Service Deployment**:
```yaml
# charts/todo-chatbot-backend/templates/recurring-task-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: recurring-task-service
spec:
  replicas: {{ .Values.recurringTaskService.replicas }}
  selector:
    matchLabels:
      app: recurring-task-service
  template:
    metadata:
      labels:
        app: recurring-task-service
      annotations:
        dapr.io/enabled: "{{ .Values.recurringTaskService.dapr.enabled }}"
        dapr.io/app-id: "{{ .Values.recurringTaskService.dapr.appId }}"
        dapr.io/app-port: "{{ .Values.recurringTaskService.dapr.appPort }}"
    spec:
      containers:
        - name: recurring-task-service
          image: "{{ .Values.recurringTaskService.image.repository }}:{{ .Values.recurringTaskService.image.tag }}"
          ports:
            - containerPort: 8001
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: backend-secrets
                  key: DATABASE_URL
            - name: DAPR_HTTP_PORT
              value: "3500"
          resources:
            {{- toYaml .Values.recurringTaskService.resources | nindent 12 }}
```

**Output**: Helm templates for all 4 new services (recurring-task, notification, audit, websocket-sync)

### 4.5: Deploy Helm Charts to Minikube

**Task**: Install Helm charts with local values

**Commands**:
```bash
# Create namespace
kubectl create namespace todo-app-dev

# Deploy backend services
helm install backend charts/todo-chatbot-backend \
  --namespace todo-app-dev \
  --values charts/todo-chatbot-backend/values-local.yaml

# Deploy frontend (Phase IV chart)
helm install frontend charts/todo-chatbot-frontend \
  --namespace todo-app-dev \
  --values charts/todo-chatbot-frontend/values-local.yaml

# Verify deployments
kubectl get pods -n todo-app-dev

# Expected output:
#   NAME                                      READY   STATUS    RESTARTS   AGE
#   api-service-xxx                           2/2     Running   0          30s
#   recurring-task-service-xxx                2/2     Running   0          30s
#   notification-service-xxx                  2/2     Running   0          30s
#   audit-service-xxx                         2/2     Running   0          30s
#   websocket-sync-service-xxx                2/2     Running   0          30s
#   frontend-todo-chatbot-frontend-xxx        2/2     Running   0          30s
#   redpanda-0                                1/1     Running   0          5m
```

**Output**: All services deployed with Dapr sidecars (2/2 READY indicates main container + Dapr sidecar)

### 4.6: Run Database Migrations

**Task**: Apply Alembic migrations for Phase V schema changes

**Commands**:
```bash
# Run migration from api-service pod
kubectl exec -it deployment/api-service -n todo-app-dev -c api-service -- alembic upgrade head

# Verify schema changes
kubectl exec -it deployment/api-service -n todo-app-dev -c api-service -- \
  psql $DATABASE_URL -c "\d tasks"

# Expected columns: id, user_id, title, description, status, priority, tags, due_date, reminder_offset, recurrence_rule, parent_task_id
```

**Output**: Database schema updated with Phase V fields

### 4.7: End-to-End Testing on Minikube

**Task**: Validate complete user journey with recurring task and reminders

**Test Steps**:
1. Access frontend: `minikube service frontend-todo-chatbot-frontend -n todo-app-dev --url`
2. Create recurring task via UI: "Team standup every Monday at 10 AM"
3. Complete first occurrence
4. Verify next occurrence generated:
   ```bash
   kubectl logs deployment/recurring-task-service -n todo-app-dev -c recurring-task-service --tail=50
   ```
5. Create task with due date and reminder: "Deadline tomorrow at 5 PM, remind 1 hour before"
6. Verify reminder scheduled:
   ```bash
   kubectl logs deployment/api-service -n todo-app-dev -c api-service | grep "Dapr Jobs API"
   ```
7. Verify WebSocket real-time sync:
   - Open two browser tabs
   - Create task in tab 1
   - Verify task appears in tab 2 without refresh

**Output**: End-to-end flow validated on Minikube

**Phase 4 Exit Criteria**:
- All 7 services running with 2/2 READY status (main + Dapr sidecar)
- Database migrations applied successfully
- Kafka topics accessible from all services
- End-to-end test passes: recurring task generation, reminder scheduling, WebSocket sync
- Dapr telemetry shows successful pub/sub, state, and jobs operations (`dapr dashboard`)

---

## Phase 5: Cloud Kubernetes Deployment (AKS / GKE / OKE)

**Purpose**: Deploy to production cloud Kubernetes with Redpanda Cloud/Confluent Cloud Kafka and Neon PostgreSQL

**Preconditions**: Phase 4 complete, local deployment validated

**Deliverables**:
1. Cloud Kubernetes cluster provisioned (AKS, GKE, or Oracle OKE)
2. Helm values file for cloud deployment (`charts/todo-chatbot-backend/values-cloud.yaml`)
3. Redpanda Cloud or Confluent Cloud Kafka cluster provisioned
4. Dapr components configured for cloud Kafka and Neon PostgreSQL
5. All services deployed to cloud with LoadBalancer access

**Steps**:

### 5.1: Provision Cloud Kubernetes Cluster

**Task**: Create managed Kubernetes cluster on Azure AKS, Google GKE, or Oracle OKE

**Option A: Oracle OKE (Always Free Tier)**:
```bash
# Create OKE cluster via OCI Console
# Configuration:
#   - Cluster Name: todo-app-oke-cluster
#   - Kubernetes Version: 1.28+
#   - Node Pool: 2 x VM.Standard.E2.1.Micro (Always Free)
#   - VCN: Create new VCN with internet gateway

# Configure kubectl
oci ce cluster create-kubeconfig \
  --cluster-id ocid1.cluster.oc1... \
  --file ~/.kube/oke-config \
  --region us-ashburn-1

export KUBECONFIG=~/.kube/oke-config

# Verify cluster access
kubectl cluster-info
```

**Option B: Azure AKS**:
```bash
az aks create \
  --resource-group todo-app-rg \
  --name todo-app-aks-cluster \
  --node-count 3 \
  --node-vm-size Standard_B2s \
  --kubernetes-version 1.28 \
  --enable-addons monitoring

az aks get-credentials \
  --resource-group todo-app-rg \
  --name todo-app-aks-cluster
```

**Option C: Google GKE**:
```bash
gcloud container clusters create todo-app-gke-cluster \
  --zone us-central1-a \
  --num-nodes 3 \
  --machine-type e2-small \
  --cluster-version 1.28

gcloud container clusters get-credentials todo-app-gke-cluster \
  --zone us-central1-a
```

**Output**: Kubernetes cluster running and accessible via kubectl

### 5.2: Install Dapr on Cloud Cluster

**Task**: Install Dapr with production configuration (mTLS enabled)

**Commands**:
```bash
# Install Dapr with Helm (recommended for production)
helm repo add dapr https://dapr.github.io/helm-charts/
helm repo update

helm install dapr dapr/dapr \
  --namespace dapr-system \
  --create-namespace \
  --set global.ha.enabled=true \
  --set global.mtls.enabled=true

# Verify Dapr installation
dapr status -k
```

**Output**: Dapr control plane running with mTLS enabled

### 5.3: Provision Redpanda Cloud Kafka Cluster

**Task**: Create Kafka cluster on Redpanda Cloud (free tier or paid)

**Steps**:
1. Sign up at https://redpanda.com/cloud
2. Create cluster:
   - Name: `todo-app-kafka`
   - Region: `us-east-1` (or closest to Kubernetes cluster)
   - Tier: Free tier (10GB retention) for dev, Tier 2 for prod
3. Create SASL/SCRAM user:
   - Username: `todo-app-producer`
   - Password: Generate secure password
4. Create topics via Redpanda Console:
   - `task-events` (6 partitions, 7 days retention)
   - `reminders` (3 partitions, 7 days retention)
   - `task-updates` (6 partitions, 1 day retention)
   - `dlq-events` (3 partitions, 30 days retention)
5. Get broker URL: `kafka.redpanda.cloud:9092`

**Output**: Redpanda Cloud Kafka cluster with topics created

### 5.4: Create Kubernetes Secrets for Cloud Credentials

**Task**: Store Kafka credentials, SMTP passwords, API keys in Kubernetes Secrets

**Commands**:
```bash
kubectl create namespace todo-app-prod

kubectl create secret generic backend-secrets \
  --namespace todo-app-prod \
  --from-literal=DATABASE_URL="postgresql://user:pass@ep-xxx.neon.tech/db" \
  --from-literal=KAFKA_USERNAME="todo-app-producer" \
  --from-literal=KAFKA_PASSWORD="secure-password" \
  --from-literal=SMTP_USER="email@gmail.com" \
  --from-literal=SMTP_PASSWORD="app-password" \
  --from-literal=GEMINI_API_KEY="AIzaSy..." \
  --from-literal=OPENAI_API_KEY="sk-proj-..."
```

**Output**: Kubernetes Secrets created in production namespace

### 5.5: Create Dapr Components for Cloud Environment

**Task**: Configure Dapr components with cloud Kafka and Neon PostgreSQL

**Cloud Kafka Pub/Sub Component**:
```yaml
# dapr-components/cloud/kafka-pubsub.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
  namespace: todo-app-prod
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "kafka.redpanda.cloud:9092"
    - name: consumerGroup
      value: "todo-app-prod-consumers"
    - name: authType
      value: "password"
    - name: saslUsername
      secretKeyRef:
        name: backend-secrets
        key: KAFKA_USERNAME
    - name: saslPassword
      secretKeyRef:
        name: backend-secrets
        key: KAFKA_PASSWORD
    - name: saslMechanism
      value: "SCRAM-SHA-256"
    - name: enableTLS
      value: "true"
```

**Cloud State Management Component**:
```yaml
# dapr-components/cloud/postgres-statestore.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: postgres-statestore
  namespace: todo-app-prod
spec:
  type: state.postgresql
  version: v1
  metadata:
    - name: connectionString
      secretKeyRef:
        name: backend-secrets
        key: DATABASE_URL
    - name: tableName
      value: "dapr_state"
```

**Output**: Dapr components configured for cloud providers

### 5.6: Create Helm Values for Cloud Deployment

**Task**: Create `values-cloud.yaml` with cloud-specific configuration

**values-cloud.yaml**:
```yaml
# charts/todo-chatbot-backend/values-cloud.yaml
global:
  environment: production
  daprEnabled: true

apiService:
  image:
    repository: docker.io/yourorg/todo-chatbot-api
    tag: v2.0.0
    pullPolicy: Always
  replicas: 3
  resources:
    requests:
      cpu: 250m
      memory: 512Mi
    limits:
      cpu: 1000m
      memory: 1Gi
  autoscaling:
    enabled: true
    minReplicas: 3
    maxReplicas: 10
    targetCPUUtilizationPercentage: 70

recurringTaskService:
  image:
    repository: docker.io/yourorg/todo-recurring-task
    tag: v1.0.0
  replicas: 2
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 5

websocketSyncService:
  service:
    type: LoadBalancer
    annotations:
      service.beta.kubernetes.io/azure-load-balancer-internal: "false"  # Public load balancer

secrets:
  # Secrets managed via Kubernetes Secrets, not values file
  useExistingSecret: backend-secrets
```

**Output**: `values-cloud.yaml` with production configuration

### 5.7: Push Docker Images to Container Registry

**Task**: Build and push images to Docker Hub or cloud provider registry

**Commands**:
```bash
# Tag images for registry
docker tag todo-chatbot-api:v2.0.0 docker.io/yourorg/todo-chatbot-api:v2.0.0
docker tag todo-recurring-task:v1.0.0 docker.io/yourorg/todo-recurring-task:v1.0.0
docker tag todo-notification:v1.0.0 docker.io/yourorg/todo-notification:v1.0.0
docker tag todo-audit:v1.0.0 docker.io/yourorg/todo-audit:v1.0.0
docker tag todo-websocket-sync:v1.0.0 docker.io/yourorg/todo-websocket-sync:v1.0.0

# Push to registry
docker push docker.io/yourorg/todo-chatbot-api:v2.0.0
docker push docker.io/yourorg/todo-recurring-task:v1.0.0
docker push docker.io/yourorg/todo-notification:v1.0.0
docker push docker.io/yourorg/todo-audit:v1.0.0
docker push docker.io/yourorg/todo-websocket-sync:v1.0.0
```

**Output**: Images available in container registry

### 5.8: Deploy to Cloud Kubernetes Cluster

**Task**: Deploy Helm charts to production namespace

**Commands**:
```bash
# Deploy Dapr components
kubectl apply -f dapr-components/cloud/kafka-pubsub.yaml
kubectl apply -f dapr-components/cloud/postgres-statestore.yaml
kubectl apply -f dapr-components/cloud/kubernetes-secrets.yaml

# Deploy backend services
helm install backend charts/todo-chatbot-backend \
  --namespace todo-app-prod \
  --values charts/todo-chatbot-backend/values-cloud.yaml

# Deploy frontend
helm install frontend charts/todo-chatbot-frontend \
  --namespace todo-app-prod \
  --values charts/todo-chatbot-frontend/values-cloud.yaml

# Verify deployments
kubectl get pods -n todo-app-prod
kubectl get svc -n todo-app-prod
```

**Output**: All services running in cloud Kubernetes with LoadBalancer IPs assigned

### 5.9: Run Database Migrations in Cloud

**Task**: Apply Alembic migrations to production Neon database

**Commands**:
```bash
# Run migrations from api-service pod
kubectl exec -it deployment/api-service -n todo-app-prod -c api-service -- alembic upgrade head

# Verify schema
kubectl exec -it deployment/api-service -n todo-app-prod -c api-service -- \
  psql $DATABASE_URL -c "\d tasks"
```

**Output**: Production database schema updated

### 5.10: Configure DNS and TLS

**Task**: Set up custom domain and TLS certificates

**Steps**:
1. Get LoadBalancer IP: `kubectl get svc frontend-service -n todo-app-prod -o jsonpath='{.status.loadBalancer.ingress[0].ip}'`
2. Create DNS A record: `app.todo-chatbot.com` → LoadBalancer IP
3. Install cert-manager for TLS:
   ```bash
   kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
   ```
4. Create ClusterIssuer for Let's Encrypt
5. Create Ingress resource with TLS annotations

**Output**: Application accessible at https://app.todo-chatbot.com

**Phase 5 Exit Criteria**:
- Cloud Kubernetes cluster running with Dapr installed
- Redpanda Cloud Kafka cluster accessible from all services
- All services deployed with HPA enabled (3-10 replicas)
- Database migrations applied to production Neon database
- LoadBalancer IPs assigned and DNS configured
- End-to-end test passes on cloud deployment
- Cost tracking confirms under $50/month for 1,000 DAU

---

## Phase 6: Observability & Reliability

**Purpose**: Implement logging, metrics, health checks, and monitoring dashboards

**Preconditions**: Phase 5 complete, cloud deployment running

**Deliverables**:
1. Structured JSON logging in all services
2. Prometheus metrics endpoints exposed
3. Liveness and readiness probes configured
4. Dapr telemetry enabled for distributed tracing
5. Grafana dashboards for service health and event metrics

**Steps**:

### 6.1: Implement Structured JSON Logging

**Task**: Configure all services to emit JSON logs with correlation IDs

**Python Services (FastAPI)**:
```python
# api-service/app/logging_config.py
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "service": "api-service",
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        if hasattr(record, "correlation_id"):
            log_obj["correlation_id"] = record.correlation_id
        if hasattr(record, "user_id"):
            log_obj["user_id"] = record.user_id
        return json.dumps(log_obj)

# Configure logging
logging.basicConfig(level=logging.INFO)
for handler in logging.root.handlers:
    handler.setFormatter(JSONFormatter())
```

**Node.js Services (TypeScript)**:
```typescript
// websocket-sync-service/src/logger.ts
import winston from 'winston';

const logger = winston.createLogger({
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  defaultMeta: { service: 'websocket-sync-service' },
  transports: [new winston.transports.Console()]
});

export default logger;
```

**Output**: All services emit JSON-formatted logs

### 6.2: Add Prometheus Metrics Endpoints

**Task**: Expose `/metrics` endpoint in Prometheus format for all services

**FastAPI Metrics**:
```python
# api-service/app/main.py
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response

# Define metrics
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

event_publish_duration = Histogram(
    "event_publish_duration_seconds",
    "Time spent publishing events",
    ["topic"]
)

@app.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

# Instrument endpoints
@app.post("/api/tasks")
async def create_task(...):
    with event_publish_duration.labels(topic="task-events").time():
        await publisher.publish_task_event(event)
    http_requests_total.labels(method="POST", endpoint="/api/tasks", status=200).inc()
```

**Output**: `/metrics` endpoint exposed for Prometheus scraping

### 6.3: Configure Liveness and Readiness Probes

**Task**: Add health check endpoints and Kubernetes probe configuration

**Health Endpoint**:
```python
# api-service/app/main.py
@app.get("/health")
async def health_check():
    try:
        # Check database connection
        await session.execute(select(1))

        # Check Dapr sidecar
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:3500/v1.0/healthz")
            response.raise_for_status()

        return {"status": "healthy", "database": "connected", "dapr": "ready"}
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )
```

**Kubernetes Probe Configuration**:
```yaml
# charts/todo-chatbot-backend/templates/api-deployment.yaml
spec:
  containers:
    - name: api-service
      livenessProbe:
        httpGet:
          path: /health
          port: 8000
        initialDelaySeconds: 30
        periodSeconds: 10
        timeoutSeconds: 5
        failureThreshold: 3
      readinessProbe:
        httpGet:
          path: /health
          port: 8000
        initialDelaySeconds: 10
        periodSeconds: 5
        timeoutSeconds: 3
        failureThreshold: 2
```

**Output**: Health probes configured for all services

### 6.4: Enable Dapr Telemetry

**Task**: Configure Dapr to export telemetry to Prometheus and Zipkin

**Dapr Configuration**:
```yaml
# dapr-components/dapr-config.yaml
apiVersion: dapr.io/v1alpha1
kind: Configuration
metadata:
  name: dapr-config
  namespace: todo-app-prod
spec:
  tracing:
    samplingRate: "1"
    zipkin:
      endpointAddress: "http://zipkin.observability.svc.cluster.local:9411/api/v2/spans"
  metric:
    enabled: true
  mtls:
    enabled: true
```

**Output**: Dapr telemetry enabled for distributed tracing

### 6.5: Deploy Prometheus and Grafana

**Task**: Install Prometheus Operator and Grafana for monitoring

**Commands**:
```bash
# Install kube-prometheus-stack
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace observability \
  --create-namespace

# Configure ServiceMonitor for Todo App services
kubectl apply -f kubernetes/observability/service-monitor.yaml
```

**ServiceMonitor Configuration**:
```yaml
# kubernetes/observability/service-monitor.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: todo-app-metrics
  namespace: observability
spec:
  selector:
    matchLabels:
      app.kubernetes.io/part-of: todo-app
  endpoints:
    - port: metrics
      path: /metrics
      interval: 30s
```

**Output**: Prometheus scraping metrics from all services

### 6.6: Create Grafana Dashboards

**Task**: Import pre-built dashboards for Kubernetes, Dapr, and custom metrics

**Dashboards**:
1. **Kubernetes Cluster Dashboard**: CPU, memory, pod status
2. **Dapr Dashboard**: Sidecar health, pub/sub operations, state management ops
3. **Todo App Dashboard**: Task operations, event publish rate, consumer lag, API response time

**Custom Dashboard JSON**:
```json
{
  "dashboard": {
    "title": "Todo App Metrics",
    "panels": [
      {
        "title": "Event Publish Rate",
        "targets": [
          {"expr": "rate(dapr_component_pubsub_outbound_total[5m])", "legendFormat": "{{topic}}"}
        ]
      },
      {
        "title": "Consumer Lag",
        "targets": [
          {"expr": "kafka_consumer_lag{job='todo-app'}", "legendFormat": "{{topic}}-{{partition}}"}
        ]
      },
      {
        "title": "API Response Time (p95)",
        "targets": [
          {"expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))", "legendFormat": "{{endpoint}}"}
        ]
      }
    ]
  }
}
```

**Output**: Grafana dashboards available at http://grafana.observability.svc.cluster.local

### 6.7: Configure Alerting Rules

**Task**: Define Prometheus alerting rules for critical failures

**Alert Rules**:
```yaml
# kubernetes/observability/alert-rules.yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: todo-app-alerts
  namespace: observability
spec:
  groups:
    - name: todo-app
      interval: 30s
      rules:
        - alert: HighConsumerLag
          expr: kafka_consumer_lag > 1000
          for: 5m
          labels:
            severity: warning
          annotations:
            summary: "Kafka consumer lag exceeds 1000 messages"

        - alert: PodCrashLooping
          expr: rate(kube_pod_container_status_restarts_total[5m]) > 0
          for: 5m
          labels:
            severity: critical
          annotations:
            summary: "Pod {{ $labels.pod }} is crash-looping"

        - alert: HighErrorRate
          expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
          for: 5m
          labels:
            severity: warning
          annotations:
            summary: "High error rate detected on {{ $labels.endpoint }}"
```

**Output**: Alerting rules configured in Prometheus

**Phase 6 Exit Criteria**:
- All services emit structured JSON logs
- Prometheus metrics endpoints accessible and scraped
- Health probes passing for all services
- Dapr telemetry visible in distributed tracing UI
- Grafana dashboards showing real-time metrics
- Alerting rules tested (simulate pod crash, consumer lag)

---

## Phase 7: Security & Secrets Management

**Purpose**: Harden security with RBAC, network policies, secrets encryption, and Dapr mTLS

**Preconditions**: Phase 6 complete

**Deliverables**:
1. Kubernetes RBAC policies for service accounts
2. Kubernetes Secrets sealed with SealedSecrets or External Secrets Operator
3. Dapr mTLS enabled for service-to-service communication
4. Network policies for pod-to-pod isolation

**Steps**:

### 7.1: Create Service Accounts with RBAC

**Task**: Define least-privilege service accounts for each service

**Service Account**:
```yaml
# kubernetes/rbac/api-service-sa.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: api-service-sa
  namespace: todo-app-prod
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: api-service-role
  namespace: todo-app-prod
rules:
  - apiGroups: [""]
    resources: ["secrets"]
    verbs: ["get"]
  - apiGroups: [""]
    resources: ["configmaps"]
    verbs: ["get", "list"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: api-service-rolebinding
  namespace: todo-app-prod
subjects:
  - kind: ServiceAccount
    name: api-service-sa
    namespace: todo-app-prod
roleRef:
  kind: Role
  name: api-service-role
  apiGroup: rbac.authorization.k8s.io
```

**Output**: Service accounts with minimal permissions created

### 7.2: Seal Kubernetes Secrets

**Task**: Use SealedSecrets to encrypt secrets in Git

**Commands**:
```bash
# Install SealedSecrets controller
kubectl apply -f https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.24.0/controller.yaml

# Create sealed secret
kubectl create secret generic backend-secrets \
  --namespace todo-app-prod \
  --from-literal=DATABASE_URL="..." \
  --dry-run=client -o yaml | \
  kubeseal -o yaml > kubernetes/secrets/backend-secrets-sealed.yaml

# Apply sealed secret
kubectl apply -f kubernetes/secrets/backend-secrets-sealed.yaml
```

**Output**: Secrets encrypted and safe to commit to Git

### 7.3: Enable Dapr mTLS

**Task**: Configure Dapr to enforce mutual TLS between services

**Dapr Configuration**:
```yaml
# dapr-components/dapr-config.yaml
apiVersion: dapr.io/v1alpha1
kind: Configuration
metadata:
  name: dapr-config
  namespace: todo-app-prod
spec:
  mtls:
    enabled: true
    workloadCertTTL: "24h"
    allowedClockSkew: "15m"
```

**Output**: mTLS enabled for all Dapr service-to-service calls

### 7.4: Define Network Policies

**Task**: Restrict pod-to-pod communication

**Network Policy**:
```yaml
# kubernetes/network-policies/api-service-netpol.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-service-netpol
  namespace: todo-app-prod
spec:
  podSelector:
    matchLabels:
      app: api-service
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: frontend
      ports:
        - protocol: TCP
          port: 8000
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: postgres
      ports:
        - protocol: TCP
          port: 5432
    - to:
        - podSelector:
            matchLabels:
              app: redpanda
      ports:
        - protocol: TCP
          port: 9092
```

**Output**: Network policies restricting inter-pod traffic

**Phase 7 Exit Criteria**:
- Service accounts created with least-privilege RBAC
- Secrets encrypted with SealedSecrets
- Dapr mTLS enabled and verified (check `dapr dashboard`)
- Network policies applied and tested (verify pod isolation)

---

## Phase 8: CI/CD Automation

**Purpose**: Automate build, test, and deployment with GitHub Actions

**Preconditions**: Phase 7 complete

**Deliverables**:
1. GitHub Actions workflow for CI/CD (`.github/workflows/ci-cd.yaml`)
2. Docker image builds on every commit
3. Automated tests run before deployment
4. Automated deployment to dev/staging/prod environments

**Steps**:

### 8.1: Create GitHub Actions Workflow

**Task**: Define CI/CD pipeline in `.github/workflows/ci-cd.yaml`

**Workflow**:
```yaml
# .github/workflows/ci-cd.yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  REGISTRY: docker.io
  IMAGE_PREFIX: yourorg

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Run unit tests
        run: |
          cd backend/api-service
          pip install -r requirements.txt
          pytest tests/unit/

      - name: Run integration tests
        run: |
          docker-compose -f docker-compose.test.yaml up -d
          pytest tests/integration/
          docker-compose -f docker-compose.test.yaml down

  build:
    needs: test
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: [api-service, recurring-task-service, notification-service, audit-service, websocket-sync-service]
    steps:
      - uses: actions/checkout@v4

      - name: Build Docker image
        run: |
          docker build -t ${{ env.REGISTRY }}/${{ env.IMAGE_PREFIX }}/todo-${{ matrix.service }}:${{ github.sha }} \
            backend/${{ matrix.service }}

      - name: Push to registry
        if: github.ref == 'refs/heads/main'
        run: |
          echo "${{ secrets.DOCKER_PASSWORD }}" | docker login -u "${{ secrets.DOCKER_USERNAME }}" --password-stdin
          docker push ${{ env.REGISTRY }}/${{ env.IMAGE_PREFIX }}/todo-${{ matrix.service }}:${{ github.sha }}

  deploy-dev:
    needs: build
    if: github.ref == 'refs/heads/develop'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up kubectl
        uses: azure/setup-kubectl@v3

      - name: Configure kubectl
        run: |
          echo "${{ secrets.KUBECONFIG_DEV }}" > kubeconfig
          export KUBECONFIG=kubeconfig

      - name: Deploy to dev
        run: |
          helm upgrade --install backend charts/todo-chatbot-backend \
            --namespace todo-app-dev \
            --values charts/todo-chatbot-backend/values-dev.yaml \
            --set global.imageTag=${{ github.sha }}

  deploy-prod:
    needs: build
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4

      - name: Deploy to production
        run: |
          helm upgrade --install backend charts/todo-chatbot-backend \
            --namespace todo-app-prod \
            --values charts/todo-chatbot-backend/values-cloud.yaml \
            --set global.imageTag=${{ github.sha }}
```

**Output**: CI/CD pipeline configured in GitHub Actions

### 8.2: Configure GitHub Secrets

**Task**: Store sensitive credentials as GitHub Secrets

**Secrets**:
- `DOCKER_USERNAME`: Docker Hub username
- `DOCKER_PASSWORD`: Docker Hub token
- `KUBECONFIG_DEV`: Dev cluster kubeconfig (base64 encoded)
- `KUBECONFIG_PROD`: Prod cluster kubeconfig (base64 encoded)

**Output**: Secrets configured in GitHub repository settings

### 8.3: Implement Automated Rollback

**Task**: Add rollback step on deployment failure

**Rollback Job**:
```yaml
# .github/workflows/rollback.yaml
name: Rollback on Failure

on:
  workflow_run:
    workflows: ["CI/CD Pipeline"]
    types: [completed]
    branches: [main]

jobs:
  rollback:
    if: ${{ github.event.workflow_run.conclusion == 'failure' }}
    runs-on: ubuntu-latest
    steps:
      - name: Rollback Helm release
        run: |
          helm rollback backend --namespace todo-app-prod
```

**Output**: Automated rollback on deployment failure

**Phase 8 Exit Criteria**:
- GitHub Actions workflow runs on every commit
- All tests pass before deployment
- Images pushed to registry with commit SHA tags
- Automated deployment to dev environment on `develop` branch
- Manual approval required for production deployment
- Rollback mechanism tested (simulate deployment failure)

---

## Phase 9: Production Readiness & Final Validation

**Purpose**: Perform load testing, chaos engineering, and final acceptance testing before production launch

**Preconditions**: Phase 8 complete

**Deliverables**:
1. Load test results (k6) for 10,000 concurrent users
2. Chaos engineering tests (pod failures, network partitions)
3. Acceptance test report covering all 87 functional requirements
4. Production readiness checklist signed off

**Steps**:

### 9.1: Run Load Tests with k6

**Task**: Simulate 10,000 concurrent users and validate performance SLOs

**k6 Test Script**:
```javascript
// tests/load/load-test.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '5m', target: 1000 },   // Ramp up to 1K users
    { duration: '10m', target: 5000 },  // Ramp up to 5K users
    { duration: '10m', target: 10000 }, // Ramp up to 10K users
    { duration: '15m', target: 10000 }, // Sustain 10K users
    { duration: '5m', target: 0 },      // Ramp down
  ],
  thresholds: {
    'http_req_duration{p(95)}': ['<500'], // p95 response time < 500ms
    'http_req_failed': ['<0.01'],          // Error rate < 1%
  },
};

export default function () {
  let res = http.post('https://api.todo-chatbot.com/api/tasks', JSON.stringify({
    title: 'Load test task',
    priority: 'medium',
    tags: ['test']
  }), {
    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${__ENV.AUTH_TOKEN}` }
  });

  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });

  sleep(1);
}
```

**Commands**:
```bash
k6 run --out cloud tests/load/load-test.js
```

**Output**: Load test report confirming p95 < 500ms for 10K users

### 9.2: Chaos Engineering Tests

**Task**: Validate resilience to pod failures, network partitions, and Kafka broker failures

**Chaos Mesh Experiments**:
```yaml
# tests/chaos/pod-failure.yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: PodChaos
metadata:
  name: api-service-pod-failure
  namespace: todo-app-prod
spec:
  action: pod-kill
  mode: one
  selector:
    namespaces:
      - todo-app-prod
    labelSelectors:
      app: api-service
  scheduler:
    cron: '@every 10m'
```

**Test Scenarios**:
1. Kill random API service pod → verify requests routed to healthy pods
2. Introduce network delay between services → verify timeout handling
3. Partition Kafka broker → verify consumer reconnection
4. Delete Dapr sidecar → verify main container waits for sidecar restart

**Output**: Chaos engineering report confirming 99.9% uptime maintained

### 9.3: End-to-End Acceptance Testing

**Task**: Run Playwright E2E tests covering all 87 functional requirements

**E2E Test Suite**:
```typescript
// tests/e2e/user-journey.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Phase V User Journey', () => {
  test('Create recurring task with due date and reminder', async ({ page }) => {
    await page.goto('https://app.todo-chatbot.com');

    // Login
    await page.fill('input[name=email]', 'test@example.com');
    await page.fill('input[name=password]', 'password123');
    await page.click('button[type=submit]');

    // Create task with advanced features
    await page.click('button:has-text("New Task")');
    await page.fill('input[name=title]', 'Team standup every Monday at 10 AM');
    await page.selectOption('select[name=priority]', 'high');
    await page.fill('input[name=tags]', 'work, meeting');
    await page.fill('input[name=due_date]', '2026-01-06T10:00');
    await page.fill('input[name=reminder_offset]', '1 hour');
    await page.check('input[name=recurring]');
    await page.selectOption('select[name=frequency]', 'weekly');
    await page.check('input[value=1]'); // Monday
    await page.click('button:has-text("Create")');

    // Verify task created
    await expect(page.locator('text=Team standup')).toBeVisible();

    // Complete task
    await page.click('button:has-text("Complete")');

    // Verify next occurrence generated (wait for Recurring Task Service)
    await page.waitForTimeout(5000);
    await page.reload();
    await expect(page.locator('text=Team standup')).toBeVisible();
  });

  test('WebSocket real-time sync', async ({ browser }) => {
    const context1 = await browser.newContext();
    const page1 = await context1.newPage();
    await page1.goto('https://app.todo-chatbot.com');

    const context2 = await browser.newContext();
    const page2 = await context2.newPage();
    await page2.goto('https://app.todo-chatbot.com');

    // Create task in page1
    await page1.fill('input[name=title]', 'WebSocket sync test');
    await page1.click('button:has-text("Create")');

    // Verify task appears in page2 without refresh
    await expect(page2.locator('text=WebSocket sync test')).toBeVisible({ timeout: 2000 });
  });
});
```

**Commands**:
```bash
npx playwright test --project=chromium
```

**Output**: E2E test report with 100% pass rate

### 9.4: Production Readiness Checklist

**Task**: Complete final checklist before production launch

**Checklist**:
```markdown
# Production Readiness Checklist

## Infrastructure
- [x] Cloud Kubernetes cluster provisioned (AKS/GKE/OKE)
- [x] Dapr installed with mTLS enabled
- [x] Kafka cluster provisioned (Redpanda Cloud/Confluent Cloud)
- [x] Neon PostgreSQL provisioned with backups enabled
- [x] Container images pushed to registry
- [x] Helm charts deployed to production namespace

## Security
- [x] RBAC policies configured for all service accounts
- [x] Kubernetes Secrets sealed with SealedSecrets
- [x] Network policies applied
- [x] mTLS enabled for service-to-service communication
- [x] TLS certificates configured for public endpoints

## Observability
- [x] Structured logging enabled
- [x] Prometheus metrics scraped
- [x] Grafana dashboards created
- [x] Alerting rules configured
- [x] Dapr telemetry enabled

## Testing
- [x] Unit tests pass (pytest, vitest)
- [x] Integration tests pass (Kafka, Dapr, database)
- [x] E2E tests pass (Playwright)
- [x] Load tests pass (10K concurrent users, p95 < 500ms)
- [x] Chaos engineering tests pass (pod failures, network partitions)

## Documentation
- [x] Deployment guide (DEPLOYMENT.md)
- [x] Architecture diagram (ARCHITECTURE.md)
- [x] Troubleshooting guide (TROUBLESHOOTING.md)
- [x] Runbooks for common operations

## CI/CD
- [x] GitHub Actions workflow configured
- [x] Automated tests run on every commit
- [x] Automated deployment to dev environment
- [x] Manual approval for production deployment
- [x] Automated rollback on failure

## Performance
- [x] API response time p95 < 500ms for 10K concurrent users
- [x] Event processing latency < 100ms
- [x] Kafka consumer lag < 1 second
- [x] WebSocket broadcast < 500ms to 10K connections

## Cost
- [x] Cloud infrastructure cost < $50/month for 1,000 DAU
- [x] Free tier usage optimized (Oracle OKE, Redpanda Cloud, Neon)

## Final Approval
- [x] Tech lead approval
- [x] Product owner approval
- [x] Security review completed
```

**Output**: Production readiness checklist 100% complete

**Phase 9 Exit Criteria**:
- Load tests pass with p95 < 500ms for 10K users
- Chaos engineering tests confirm 99.9% uptime
- E2E tests cover all 87 functional requirements with 100% pass rate
- Production readiness checklist signed off by all stakeholders

---

## Rollback Plan

### Rollback Triggers

Initiate rollback if any of the following conditions occur within 1 hour of deployment:

1. **Error Rate > 5%**: HTTP 500 errors exceed 5% of total requests
2. **Consumer Lag > 10,000**: Kafka consumer lag exceeds 10,000 messages for more than 5 minutes
3. **Pod Crash Loop**: Any service enters CrashLoopBackOff state
4. **Database Connection Failures**: > 10% of database connections fail
5. **User-Reported Outage**: Critical functionality unavailable to users

### Rollback Procedure

**Automatic Rollback (GitHub Actions)**:
```yaml
# .github/workflows/rollback.yaml (already defined in Phase 8)
- name: Rollback on failure
  run: |
    helm rollback backend --namespace todo-app-prod
    helm rollback frontend --namespace todo-app-prod
```

**Manual Rollback**:
```bash
# 1. Identify current revision
helm history backend -n todo-app-prod

# 2. Rollback to previous revision
helm rollback backend -n todo-app-prod

# 3. Verify rollback
kubectl get pods -n todo-app-prod
kubectl logs deployment/api-service -n todo-app-prod --tail=50

# 4. Rollback database migration if schema changes were deployed
kubectl exec -it deployment/api-service -n todo-app-prod -c api-service -- \
  alembic downgrade -1
```

**Rollback Validation**:
1. Verify all pods Running (2/2 READY)
2. Verify no error spike in logs
3. Verify consumer lag returns to < 1 second
4. Run smoke test: Create task → verify in database → verify event published

**Rollback Communication**:
1. Post in #incidents Slack channel: "Rollback initiated due to [trigger]"
2. Update status page: "Investigating deployment issue, rollback in progress"
3. After rollback: "Services restored to previous version, investigating root cause"

---

## Success Metrics

### Technical Metrics

| Metric | Target | Validation Method |
|--------|--------|-------------------|
| API Response Time (p95) | < 500ms | k6 load test report |
| Event Processing Latency | < 100ms | Prometheus `event_publish_duration` metric |
| Uptime | 99.9% | Uptime monitoring (< 43 min downtime/month) |
| Consumer Lag | < 1 second | Kafka consumer lag monitoring |
| WebSocket Broadcast | < 500ms | E2E test measurements |
| Search/Filter Query Time | < 1 second | Integration test assertions |
| Recurring Task Generation | < 5 seconds | E2E test timing |
| Reminder Scheduling | < 2 seconds | Integration test timing |
| Test Coverage | > 80% | pytest --cov report |
| Error Rate | < 1% | Prometheus `http_requests_total{status=~"5.."}` |

### Business Metrics

| Metric | Target | Validation Method |
|--------|--------|-------------------|
| Cloud Infrastructure Cost | < $50/month | Cloud billing dashboard |
| Deployment Time | < 20 minutes | GitHub Actions workflow duration |
| Rollback Time | < 5 minutes | Manual rollback test |
| Developer Setup Time | < 30 minutes | New developer onboarding |
| Multi-Cloud Portability | 3 providers (AKS, GKE, OKE) | Deploy to each provider, verify success |

### User Metrics

| Metric | Target | Validation Method |
|--------|--------|-------------------|
| Task Creation Success Rate | > 99% | E2E test assertions |
| Recurring Task Accuracy | 99.99% (no missed/duplicate occurrences) | Integration test validation |
| Reminder Delivery Rate | > 99% | Email delivery logs |
| Real-Time Sync Latency | < 500ms | WebSocket E2E test |

---

## Dependencies & Prerequisites

### External Dependencies

1. **Neon PostgreSQL** (REQUIRED)
   - Status: Must be provisioned before Phase 1
   - Owner: DevOps team
   - Validation: `psql $DATABASE_URL -c "SELECT version()"`

2. **Redpanda Cloud / Confluent Cloud** (REQUIRED for cloud deployment)
   - Status: Must be provisioned before Phase 5
   - Owner: DevOps team
   - Validation: `kafka-topics.sh --bootstrap-server $KAFKA_BROKER --list`

3. **SMTP Email Provider** (REQUIRED for reminders)
   - Status: Must be configured before Phase 4 (Notification Service)
   - Owner: Operations team
   - Validation: Send test email via SMTP

4. **Container Registry** (REQUIRED)
   - Status: Must be accessible before Phase 4
   - Owner: DevOps team
   - Validation: `docker push yourorg/test-image:latest`

### Platform Dependencies

5. **Minikube** (REQUIRED for local development)
   - Version: 1.32+
   - Resources: 4 CPUs, 8GB RAM minimum
   - Validation: `minikube status`

6. **Dapr CLI** (REQUIRED)
   - Version: 1.12+
   - Validation: `dapr version`

7. **Helm** (REQUIRED)
   - Version: 3.10+
   - Validation: `helm version`

8. **kubectl** (REQUIRED)
   - Version: 1.28+
   - Validation: `kubectl version --client`

### Internal Dependencies

9. **Phase IV Completion** (REQUIRED)
   - All Phase IV services deployed and tested
   - Helm charts functional
   - Database schema from Phase IV migrated

---

## Risk Mitigation

### High-Risk Items

1. **Kafka Event Ordering Issues**
   - **Risk**: Out-of-order events cause incorrect recurring task generation
   - **Mitigation**: Use consistent partition keys (task_id), event sequence numbers, idempotency keys
   - **Fallback**: Add event ordering validation in Recurring Task Service

2. **Dapr Sidecar Failures**
   - **Risk**: Dapr sidecar crashes prevent service communication
   - **Mitigation**: Kubernetes restarts sidecar, liveness probe waits for sidecar readiness
   - **Fallback**: Direct Kafka client libraries (removes Dapr abstraction)

3. **Cloud Cost Overruns**
   - **Risk**: Free tier limits exceeded, unexpected charges
   - **Mitigation**: Set up billing alerts at 50%, 75%, 90% thresholds, monitor daily costs
   - **Fallback**: Migrate to Oracle OKE Always Free tier, use Strimzi instead of Redpanda Cloud

### Medium-Risk Items

4. **Database Migration Failures**
   - **Risk**: Alembic migration fails, leaves database in inconsistent state
   - **Mitigation**: Test migrations on staging, take database backup before migration, implement rollback script
   - **Fallback**: Manual schema fix via SQL, restore from backup

5. **WebSocket Connection Limits**
   - **Risk**: Load balancer or Kubernetes ingress limits WebSocket connections
   - **Mitigation**: Test WebSocket connection limits in staging, configure load balancer timeout and max connections
   - **Fallback**: HTTP polling for real-time updates

---

## Phase Summary

| Phase | Purpose | Key Deliverables | Duration Estimate |
|-------|---------|------------------|-------------------|
| 0 | Architecture & Validation | research.md | 2-3 days |
| 1 | Advanced Feature Enablement | data-model.md, migrations, API contracts | 3-4 days |
| 2 | Event-Driven Backbone (Kafka) | Kafka topics, event schemas, publisher module | 3-4 days |
| 3 | Dapr Integration | Dapr components, sidecar injection, Jobs API | 4-5 days |
| 4 | Local Kubernetes Deployment | Minikube deployment, E2E validation | 3-4 days |
| 5 | Cloud Kubernetes Deployment | Cloud cluster, Redpanda Cloud, production deployment | 4-5 days |
| 6 | Observability & Reliability | Logging, metrics, monitoring dashboards | 2-3 days |
| 7 | Security & Secrets | RBAC, mTLS, network policies, sealed secrets | 2-3 days |
| 8 | CI/CD Automation | GitHub Actions pipeline, automated deployment | 2-3 days |
| 9 | Production Readiness | Load testing, chaos engineering, acceptance testing | 3-4 days |

**Total Duration**: 28-38 days (4-6 weeks)

---

## Next Steps

After Phase 2 planning complete, run:

```bash
/sp.tasks
```

This will generate `tasks.md` with detailed, testable tasks ordered by dependency for Claude Code execution.
