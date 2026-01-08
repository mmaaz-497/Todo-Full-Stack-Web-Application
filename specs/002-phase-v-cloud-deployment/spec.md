# Feature Specification: Phase V - Advanced Cloud Deployment

**Feature Branch**: `002-phase-v-cloud-deployment`
**Created**: 2026-01-02
**Status**: Draft
**Input**: User description: "You are a Senior Cloud Architect, Kubernetes Expert, Event-Driven Systems Designer, and Spec-Kit Plus Specifications Author. Your task is to generate a COMPLETE, DETAILED, and IMPLEMENTABLE `/sp.specs` specification for **Phase V: Advanced Cloud Deployment** of the Todo AI Chatbot project."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Local Development with Event-Driven Architecture (Priority: P1)

As a developer, I need to run the complete event-driven Todo AI Chatbot application locally on Minikube with Dapr, Kafka, and all microservices to test advanced features like recurring tasks and real-time reminders before deploying to production.

**Why this priority**: Foundation for all other features. Developers must be able to develop and test locally before cloud deployment. Without this, no other Phase V features can be validated.

**Independent Test**: Can be fully tested by starting Minikube, installing Dapr, deploying Kafka (Strimzi/Redpanda), deploying all services via Helm, creating a recurring task, and verifying reminder notifications are sent. Delivers complete local development environment.

**Acceptance Scenarios**:

1. **Given** Minikube is running with Dapr installed, **When** developer deploys all Helm charts with Kafka enabled, **Then** all pods start successfully with Dapr sidecars attached
2. **Given** all services are running locally, **When** developer creates a recurring task via Chat API, **Then** Recurring Task Service consumes the event from Kafka and generates next occurrence
3. **Given** a task with a due date is created, **When** due time approaches, **Then** Notification Service receives reminder event via Kafka and sends email notification
4. **Given** local deployment is complete, **When** developer checks service logs, **Then** Dapr telemetry shows successful pub/sub, state management, and service invocation operations
5. **Given** local environment is running, **When** developer modifies code and rebuilds images, **Then** Helm upgrade applies changes without data loss

---

### User Story 2 - Production Multi-Cloud Deployment (Priority: P2)

As a DevOps engineer, I need to deploy the Todo AI Chatbot to production Kubernetes clusters (AKS/GKE/Oracle OKE) with external Kafka (Redpanda Cloud/Confluent) and observe all services running with high availability and fault tolerance.

**Why this priority**: Core business requirement for production deployment. Enables actual users to access the application with enterprise-grade reliability. Depends on P1 local validation.

**Independent Test**: Can be fully tested by provisioning a cloud Kubernetes cluster (any of AKS/GKE/OKE), creating Redpanda Cloud Kafka cluster, configuring Dapr components with cloud credentials, deploying via Helm, and performing end-to-end task operations. Delivers production-ready deployment.

**Acceptance Scenarios**:

1. **Given** cloud Kubernetes cluster is provisioned, **When** deploying Dapr with cloud-specific configurations, **Then** Dapr control plane installs successfully with proper RBAC
2. **Given** Redpanda Cloud Kafka is provisioned, **When** configuring Dapr pub/sub component with SASL credentials, **Then** all services connect securely to cloud Kafka brokers
3. **Given** production deployment is complete, **When** traffic increases to 10,000 concurrent users, **Then** services auto-scale via HPA and maintain performance SLOs
4. **Given** a service pod crashes, **When** Kubernetes restarts the pod, **Then** Dapr sidecar reconnects and event processing resumes without data loss
5. **Given** production cluster is running, **When** deploying a new version, **Then** rolling update completes with zero downtime

---

### User Story 3 - Recurring Task Management (Priority: P3)

As a user, I need to create tasks that repeat daily, weekly, or monthly so that I don't have to manually recreate routine tasks.

**Why this priority**: High-value user feature that leverages event-driven architecture. Differentiates the product from basic todo apps. Depends on P1 local infrastructure.

**Independent Test**: Can be fully tested by creating a task with recurrence rule "daily at 9 AM", waiting for next occurrence generation, and verifying new task instance appears in task list. Delivers tangible user value independently.

**Acceptance Scenarios**:

1. **Given** user is authenticated, **When** user creates a task with recurrence rule "every Monday at 10 AM", **Then** task is created and recurrence metadata is stored
2. **Given** recurring task exists, **When** current occurrence is completed, **Then** Recurring Task Service generates next occurrence based on recurrence rule
3. **Given** multiple recurring tasks with different rules, **When** Recurring Task Service processes events, **Then** each task generates next occurrence according to its specific rule
4. **Given** user completes a recurring task occurrence, **When** viewing task history, **Then** user sees all past occurrences marked as completed and next occurrence scheduled
5. **Given** user deletes a recurring task, **When** deletion event is published, **Then** Recurring Task Service stops generating future occurrences

---

### User Story 4 - Due Date Reminders with Dapr Jobs API (Priority: P4)

As a user, I need to receive email reminders before my tasks are due so that I never miss important deadlines.

**Why this priority**: Enhances user engagement and task completion rates. Demonstrates Dapr Jobs API integration. Can be built after core event infrastructure (P1).

**Independent Test**: Can be fully tested by creating a task with due date "tomorrow at 2 PM", configuring reminder "1 hour before", and verifying email notification is received at 1 PM tomorrow. Delivers immediate user value.

**Acceptance Scenarios**:

1. **Given** user creates a task with due date and reminder time, **When** task is saved, **Then** Dapr Jobs API schedules reminder job with correct trigger time
2. **Given** reminder job is scheduled, **When** trigger time arrives, **Then** Dapr calls reminder webhook endpoint with task details
3. **Given** reminder webhook is triggered, **When** Notification Service receives callback, **Then** email notification is sent to user with task details
4. **Given** user updates task due date, **When** update event is processed, **Then** old reminder job is cancelled and new job is scheduled
5. **Given** user completes task before reminder time, **When** completion event is processed, **Then** reminder job is cancelled

---

### User Story 5 - Advanced Task Management Features (Priority: P5)

As a user, I need to prioritize tasks, add tags, search by keywords, filter by status/priority/tags, and sort by various criteria so that I can efficiently organize and find tasks in large task lists.

**Why this priority**: Quality-of-life improvements that enhance user experience. Can be incrementally added after core features are stable.

**Independent Test**: Can be fully tested by creating 50 tasks with different priorities/tags, performing search query "project meeting", filtering by "high priority" + "work" tag, and sorting by due date. Delivers improved usability.

**Acceptance Scenarios**:

1. **Given** user creates tasks, **When** assigning priority levels (low/medium/high/urgent), **Then** tasks display with priority indicators
2. **Given** tasks have tags, **When** user searches for "work", **Then** all tasks tagged with "work" are returned
3. **Given** task list contains 100+ tasks, **When** user filters by "completed" status and "personal" tag, **Then** only matching tasks are displayed within 1 second
4. **Given** filtered task list, **When** user sorts by "due date ascending", **Then** tasks are reordered with nearest due dates first
5. **Given** user performs complex query (priority=high AND tag=urgent AND status=pending), **When** applying filters, **Then** results match all criteria

---

### User Story 6 - Real-Time Task Synchronization via WebSocket (Priority: P6)

As a user with multiple browser tabs or devices, I need task updates to appear instantly across all sessions so that I always see the current state.

**Why this priority**: Advanced feature that improves multi-device experience. Requires WebSocket infrastructure. Lower priority than core features.

**Independent Test**: Can be fully tested by opening two browser tabs, creating a task in tab 1, and verifying task appears immediately in tab 2 without refresh. Delivers seamless multi-device experience.

**Acceptance Scenarios**:

1. **Given** user has two browser sessions open, **When** creating a task in session 1, **Then** session 2 receives WebSocket message and updates task list in real-time
2. **Given** WebSocket connection is established, **When** network is temporarily disconnected, **Then** WebSocket reconnects automatically and syncs missed updates
3. **Given** task update event is published to Kafka, **When** WebSocket Sync Service consumes event, **Then** all connected clients receive update within 500ms
4. **Given** 10,000 concurrent WebSocket connections, **When** broadcast event is triggered, **Then** all clients receive message without server overload

---

### User Story 7 - Audit Log and Activity Tracking (Priority: P7)

As a system administrator, I need to view audit logs of all task operations (create/update/delete) with timestamps, user IDs, and action details for compliance and debugging.

**Why this priority**: Supports compliance, debugging, and user behavior analytics. Not critical for initial launch but valuable for enterprise adoption.

**Independent Test**: Can be fully tested by performing various task operations, querying audit log API filtered by user ID, and verifying all actions are recorded with correct metadata. Delivers compliance capability.

**Acceptance Scenarios**:

1. **Given** user creates a task, **When** task creation event is published, **Then** Audit Service records event with timestamp, user ID, action type, and task payload
2. **Given** audit logs are stored, **When** admin queries logs filtered by date range and user, **Then** matching log entries are returned
3. **Given** compliance requirement for 90-day retention, **When** logs reach 91 days old, **Then** automated job archives or deletes old logs
4. **Given** suspicious activity is detected, **When** admin views audit log, **Then** all actions by suspect user are visible with full details

---

### User Story 8 - CI/CD Pipeline for Automated Deployment (Priority: P8)

As a DevOps engineer, I need GitHub Actions pipeline to automatically build, test, containerize, and deploy the application to Kubernetes whenever code is merged to main branch.

**Why this priority**: Operational excellence feature that improves development velocity. Can be added after manual deployment process is validated.

**Independent Test**: Can be fully tested by creating a pull request with code change, merging to main, and observing GitHub Actions automatically build images, run tests, and deploy to dev/staging clusters. Delivers automation.

**Acceptance Scenarios**:

1. **Given** PR is merged to main branch, **When** GitHub Actions workflow triggers, **Then** all service images are built and pushed to container registry
2. **Given** images are built, **When** test suite runs, **Then** all unit and integration tests must pass before deployment proceeds
3. **Given** tests pass, **When** deploying to dev environment, **Then** Helm charts are applied with dev-specific values
4. **Given** dev deployment succeeds, **When** manual approval is granted, **Then** production deployment proceeds with blue-green strategy
5. **Given** deployment fails, **When** rollback is triggered, **Then** previous working version is restored automatically

---

### Edge Cases

- What happens when Kafka broker is temporarily unavailable? (Services must buffer events locally and retry with exponential backoff)
- How does system handle duplicate event processing? (Consumers must implement idempotency using event IDs)
- What happens when Dapr sidecar crashes? (Kubernetes restarts sidecar; application waits for sidecar readiness before processing)
- How does system handle clock skew across distributed services? (Use server-side timestamps; validate time differences within acceptable threshold)
- What happens when database connection pool is exhausted? (Dapr state management component handles connection pooling; requests queue with timeout)
- How does system handle malformed events in Kafka topics? (Dead letter queue captures failed events; monitoring alerts on DLQ accumulation)
- What happens when WebSocket connection limit is reached? (Reject new connections gracefully with HTTP 503; implement connection limit per user)
- How does system handle reminder scheduling for past dates? (Validate due date is in future; reject or fire reminder immediately based on policy)
- What happens when recurring task generation falls behind? (Catch-up mechanism generates missed occurrences up to configured limit; alert if backlog exceeds threshold)
- How does system handle concurrent task updates from multiple clients? (Optimistic locking with version numbers; last-write-wins with conflict notification)

## Requirements *(mandatory)*

### Functional Requirements

#### Core Event-Driven Architecture

- **FR-001**: System MUST use Kafka as the event backbone for all asynchronous inter-service communication
- **FR-002**: System MUST use Dapr as abstraction layer for pub/sub, state management, service invocation, secrets, and scheduled jobs
- **FR-003**: All events MUST follow defined schemas with versioning (schema version included in event metadata)
- **FR-004**: System MUST support event durability with minimum retention of 7 days on all Kafka topics
- **FR-005**: All event consumers MUST implement idempotent event processing using unique event IDs
- **FR-006**: System MUST implement retry logic with exponential backoff for failed event processing (max 5 retries)
- **FR-007**: System MUST route failed events after max retries to dead letter queue topic for manual inspection

#### Recurring Tasks

- **FR-008**: System MUST support recurring task rules: daily, weekly (specific days), monthly (specific date)
- **FR-009**: Recurring tasks MUST store recurrence metadata: frequency, interval, days of week (for weekly), day of month (for monthly)
- **FR-010**: System MUST publish task-created events to `task-events` Kafka topic when recurring tasks are created
- **FR-011**: Recurring Task Service MUST consume `task-events` topic and generate next task occurrence when current occurrence is completed
- **FR-012**: System MUST prevent duplicate occurrence generation by tracking last generated occurrence timestamp
- **FR-013**: System MUST support disabling recurring task without deleting historical occurrences
- **FR-014**: System MUST link all occurrences of recurring task via parent task ID for history tracking

#### Due Dates & Reminders

- **FR-015**: Tasks MUST support optional due date field with date-time precision (timezone-aware)
- **FR-016**: Tasks MUST support reminder configuration: time offset before due date (e.g., 1 hour, 1 day, 1 week)
- **FR-017**: System MUST use Dapr Jobs API to schedule reminder jobs when task with reminder is created
- **FR-018**: System MUST publish reminder events to `reminders` Kafka topic when scheduled job triggers
- **FR-019**: Notification Service MUST consume `reminders` topic and send email notifications to task owners
- **FR-020**: System MUST cancel scheduled reminder jobs when task is completed or deleted before due date
- **FR-021**: System MUST reschedule reminder jobs when task due date is updated
- **FR-022**: System MUST support multiple reminder times per task (e.g., 1 week before AND 1 day before)

#### Advanced Task Management

- **FR-023**: Tasks MUST support priority field with values: low, medium, high, urgent
- **FR-024**: Tasks MUST support tags field as array of strings (user-defined labels)
- **FR-025**: System MUST provide search capability across task title and description with keyword matching
- **FR-026**: System MUST support filtering tasks by: status, priority, tags, due date range, creation date range
- **FR-027**: System MUST support sorting tasks by: due date, priority, creation date, update date (ascending/descending)
- **FR-028**: Search and filter operations MUST return results within 1 second for task lists up to 10,000 items per user
- **FR-029**: System MUST support combining multiple filters (AND logic) and multiple tags (OR logic)

#### Service Specifications

- **FR-030**: Chat API Service MUST provide all CRUD operations for tasks via RESTful API
- **FR-031**: Chat API Service MUST publish task events (created, updated, deleted, completed) to `task-events` Kafka topic
- **FR-032**: Chat API Service MUST use Dapr State Management for conversation context storage
- **FR-033**: Chat API Service MUST use Dapr Service Invocation for auth token validation
- **FR-034**: Recurring Task Service MUST consume `task-events` topic and process recurring task generation
- **FR-035**: Recurring Task Service MUST use Dapr State Management to track last generated occurrence timestamp
- **FR-036**: Notification Service MUST consume `reminders` topic and send email notifications via SMTP
- **FR-037**: Notification Service MUST use Dapr Secrets Management to retrieve SMTP credentials
- **FR-038**: Audit Service MUST consume all topics (`task-events`, `reminders`, `task-updates`) and log events to persistent storage
- **FR-039**: Audit Service MUST provide query API for retrieving audit logs filtered by user, action type, and date range
- **FR-040**: WebSocket Sync Service MUST consume `task-updates` topic and broadcast to connected WebSocket clients
- **FR-041**: WebSocket Sync Service MUST maintain WebSocket connections with automatic reconnection on disconnect
- **FR-042**: WebSocket Sync Service MUST authenticate WebSocket connections using JWT tokens

#### Kubernetes Deployment

- **FR-043**: All services MUST run in Kubernetes with Dapr sidecar injection enabled
- **FR-044**: All services MUST define Kubernetes deployments with health checks (liveness and readiness probes)
- **FR-045**: All services MUST define resource requests and limits (CPU and memory)
- **FR-046**: All services MUST be packaged as Helm charts with configurable values for different environments
- **FR-047**: System MUST support deployment to local Minikube and cloud Kubernetes (AKS, GKE, Oracle OKE)
- **FR-048**: Helm charts MUST reuse Phase IV charts with Dapr-specific enhancements
- **FR-049**: System MUST use Kubernetes namespaces for environment isolation (dev, staging, prod)
- **FR-050**: All sensitive configuration MUST be stored in Kubernetes Secrets and accessed via Dapr Secrets component

#### Local Deployment (Minikube)

- **FR-051**: Local deployment MUST run on Minikube with minimum 4 CPUs and 8GB RAM
- **FR-052**: Dapr MUST be installed on Minikube using `dapr init -k` command
- **FR-053**: Kafka MUST be deployed using Strimzi Operator OR Redpanda for local testing
- **FR-054**: Local Kafka cluster MUST have minimum 3 brokers for fault tolerance testing
- **FR-055**: All Dapr components (pub/sub, state, secrets) MUST be configured for local Kafka and PostgreSQL
- **FR-056**: Local deployment MUST support NodePort services for external access
- **FR-057**: Local deployment MUST include monitoring dashboard for Dapr telemetry

#### Cloud Deployment

- **FR-058**: Cloud deployment MUST support Azure AKS, Google GKE, and Oracle OKE clusters
- **FR-059**: Cloud Kubernetes clusters MUST be provisioned with minimum 3 nodes for high availability
- **FR-060**: Dapr MUST be installed on cloud clusters with production configuration (mTLS enabled)
- **FR-061**: Cloud deployment MUST use external managed Kafka (Redpanda Cloud as primary, Confluent Cloud as alternative)
- **FR-062**: Cloud deployment MUST use external managed PostgreSQL (Neon, Azure Database, Cloud SQL)
- **FR-063**: Dapr pub/sub component MUST be configured with SASL/SSL for secure cloud Kafka connection
- **FR-064**: Cloud deployment MUST use LoadBalancer services for external access
- **FR-065**: Cloud deployment MUST support custom domain names with TLS certificates

#### Kafka Cloud Integration

- **FR-066**: System MUST support Redpanda Cloud as primary cloud Kafka provider
- **FR-067**: System MUST support Confluent Cloud as alternative cloud Kafka provider
- **FR-068**: System MUST support self-hosted Strimzi Kafka as fallback for cloud deployments
- **FR-069**: Kafka authentication MUST use SASL/SCRAM or SASL/PLAIN with credentials stored in Dapr Secrets
- **FR-070**: Kafka connection MUST use SSL/TLS encryption for data in transit
- **FR-071**: Kafka topics MUST be created with replication factor 3 for production environments
- **FR-072**: Kafka topics MUST be configured with appropriate retention policies (7 days minimum)

#### CI/CD Pipeline

- **FR-073**: GitHub Actions workflow MUST build Docker images for all services on code push
- **FR-074**: GitHub Actions workflow MUST run unit tests and integration tests before deployment
- **FR-075**: GitHub Actions workflow MUST push Docker images to container registry with semantic version tags
- **FR-076**: GitHub Actions workflow MUST deploy to dev environment automatically on main branch merge
- **FR-077**: GitHub Actions workflow MUST require manual approval for production deployment
- **FR-078**: GitHub Actions workflow MUST support environment-specific Helm values (dev, staging, prod)
- **FR-079**: GitHub Actions workflow MUST implement rollback mechanism on deployment failure
- **FR-080**: GitHub Actions workflow MUST send deployment notifications to Slack/Teams channel

#### Observability

- **FR-081**: All services MUST emit structured logs in JSON format with correlation IDs
- **FR-082**: All services MUST expose Prometheus metrics endpoint for monitoring
- **FR-083**: Dapr telemetry MUST be enabled for tracing pub/sub, state, and service invocation operations
- **FR-084**: System MUST aggregate logs from all services using Kubernetes logging infrastructure
- **FR-085**: System MUST provide centralized dashboard for monitoring service health and performance
- **FR-086**: System MUST generate alerts for critical failures (pod crashes, event processing delays, dead letter queue growth)
- **FR-087**: All Kafka consumer lag MUST be monitored with alerts when lag exceeds threshold

### Event Schemas

#### Task Event Schema

```json
{
  "event_id": "uuid-v4",
  "schema_version": "1.0",
  "event_type": "task.created | task.updated | task.deleted | task.completed",
  "timestamp": "ISO 8601 datetime",
  "task_id": "integer",
  "user_id": "integer",
  "task_data": {
    "title": "string",
    "description": "string | null",
    "status": "pending | in_progress | completed",
    "priority": "low | medium | high | urgent | null",
    "tags": ["string"],
    "due_date": "ISO 8601 datetime | null",
    "reminder_offset": "ISO 8601 duration | null",
    "recurrence_rule": {
      "frequency": "daily | weekly | monthly",
      "interval": "integer",
      "days_of_week": "[0-6] | null",
      "day_of_month": "1-31 | null",
      "end_date": "ISO 8601 datetime | null"
    } | null,
    "parent_task_id": "integer | null"
  }
}
```

#### Reminder Event Schema

```json
{
  "event_id": "uuid-v4",
  "schema_version": "1.0",
  "event_type": "reminder.due",
  "timestamp": "ISO 8601 datetime",
  "task_id": "integer",
  "user_id": "integer",
  "due_date": "ISO 8601 datetime",
  "task_title": "string",
  "task_description": "string | null",
  "notification_channels": ["email", "sms", "push"],
  "reminder_time": "ISO 8601 datetime"
}
```

#### Task Update Event Schema (for WebSocket)

```json
{
  "event_id": "uuid-v4",
  "schema_version": "1.0",
  "event_type": "task.sync",
  "timestamp": "ISO 8601 datetime",
  "user_id": "integer",
  "operation": "create | update | delete",
  "task_id": "integer",
  "task_snapshot": {
    "title": "string",
    "status": "pending | in_progress | completed",
    "updated_at": "ISO 8601 datetime"
  }
}
```

### Kafka Topic Specifications

| Topic Name      | Partitions | Replication | Retention | Producers                 | Consumers                                   |
|-----------------|------------|-------------|-----------|---------------------------|---------------------------------------------|
| `task-events`   | 6          | 3           | 7 days    | Chat API                  | Recurring Task Service, Audit Service       |
| `reminders`     | 3          | 3           | 7 days    | Chat API (via Dapr Jobs)  | Notification Service, Audit Service         |
| `task-updates`  | 6          | 3           | 1 day     | All task services         | WebSocket Sync Service, Audit Service       |
| `dlq-events`    | 3          | 3           | 30 days   | All consumers (on failure)| Manual inspection / retry service (future)  |

### Key Entities

- **Task**: Represents a todo item with attributes: id, user_id, title, description, status, priority, tags, due_date, reminder_offset, recurrence_rule, parent_task_id, created_at, updated_at, completed_at
- **Recurrence Rule**: Defines task repetition pattern with attributes: frequency (daily/weekly/monthly), interval (every N days/weeks/months), days_of_week (for weekly), day_of_month (for monthly), end_date (optional)
- **Reminder Configuration**: Defines when to send reminder with attributes: task_id, offset_before_due (duration), notification_channels (email/sms/push), sent_at, status
- **Task Event**: Event published when task changes with attributes: event_id, event_type (created/updated/deleted/completed), task_id, user_id, task_payload, timestamp, schema_version
- **Reminder Event**: Event published when reminder triggers with attributes: event_id, task_id, user_id, due_date, message, timestamp, schema_version
- **Audit Log Entry**: Record of system activity with attributes: log_id, event_id, user_id, action_type, resource_type, resource_id, payload, timestamp, source_service
- **Dapr Component**: Configuration defining Dapr building block with attributes: component_name, component_type (pubsub/state/secretstore/binding), version, metadata (key-value pairs), scopes (services allowed to use component)
- **WebSocket Connection**: Active real-time connection with attributes: connection_id, user_id, session_token, connected_at, last_ping_at

## Success Criteria *(mandatory)*

### Measurable Outcomes

#### Local Development

- **SC-001**: Developers can set up complete local environment (Minikube + Dapr + Kafka + all services) in under 30 minutes following documentation
- **SC-002**: Local environment supports hot-reload workflow with code changes reflected in under 2 minutes
- **SC-003**: Local Kafka cluster handles 1,000 events per second across all topics without message loss
- **SC-004**: All Dapr sidecar operations (pub/sub, state, service invocation) complete with p95 latency under 50ms in local environment

#### Cloud Production Deployment

- **SC-005**: Cloud deployment to any supported Kubernetes provider (AKS/GKE/OKE) completes in under 20 minutes using Helm charts
- **SC-006**: Production system handles 10,000 concurrent users with p95 API response time under 500ms
- **SC-007**: System maintains 99.9% uptime (less than 43 minutes downtime per month)
- **SC-008**: Production Kafka cluster processes 10,000 events per second with consumer lag under 1 second
- **SC-009**: Dapr service invocation succeeds with 99.95% success rate in production
- **SC-010**: System auto-scales from 3 to 20 replicas based on load within 2 minutes

#### Recurring Tasks

- **SC-011**: Users can create recurring tasks with any supported rule (daily/weekly/monthly) in under 30 seconds
- **SC-012**: Recurring Task Service generates next occurrence within 5 seconds of current occurrence completion
- **SC-013**: System handles 1,000 recurring tasks per user without performance degradation
- **SC-014**: Recurring task occurrence generation has 99.99% accuracy (no missed or duplicate occurrences)

#### Reminders

- **SC-015**: Reminder notifications are sent within 1 minute of scheduled time with 99.9% reliability
- **SC-016**: System schedules reminder jobs using Dapr Jobs API within 2 seconds of task creation
- **SC-017**: Users receive reminder emails with 99% deliverability rate
- **SC-018**: System handles cancellation and rescheduling of 10,000 reminder jobs per minute

#### Advanced Features

- **SC-019**: Task search returns results within 500ms for keyword queries across 10,000 tasks per user
- **SC-020**: Complex filters (priority + tags + status + date range) execute within 1 second
- **SC-021**: WebSocket clients receive task updates within 500ms of event publication
- **SC-022**: System supports 10,000 concurrent WebSocket connections per service instance
- **SC-023**: Audit log queries return results within 2 seconds for 1 million log entries

#### Event-Driven Architecture

- **SC-024**: All events follow defined schema with 100% schema validation compliance
- **SC-025**: Event processing idempotency prevents duplicate side effects in 100% of retry scenarios
- **SC-026**: Dead letter queue captures 100% of failed events after max retry attempts
- **SC-027**: Event-to-action latency (event published to consumer processed) averages under 100ms

#### Multi-Cloud Portability

- **SC-028**: Same Helm charts deploy successfully to AKS, GKE, and Oracle OKE with only provider-specific values changed
- **SC-029**: Switching between Redpanda Cloud, Confluent Cloud, and Strimzi requires only Dapr component configuration change (no code changes)
- **SC-030**: Migrating from one Kubernetes provider to another completes in under 4 hours including data migration

#### CI/CD Pipeline

- **SC-031**: Full CI/CD pipeline (build + test + deploy to dev) completes in under 15 minutes
- **SC-032**: Automated tests achieve minimum 80% code coverage across all services
- **SC-033**: Production deployment with blue-green strategy completes with zero downtime
- **SC-034**: Automated rollback restores previous version within 5 minutes of failure detection

#### Observability

- **SC-035**: All service logs are queryable within 30 seconds of emission
- **SC-036**: Monitoring dashboards update with real-time metrics every 10 seconds
- **SC-037**: Critical alerts (pod crashes, high error rates) trigger notifications within 1 minute
- **SC-038**: Dapr distributed tracing provides end-to-end request visibility across all services

#### Cost Efficiency

- **SC-039**: Local development environment runs on workstations with 8GB RAM (no cloud costs)
- **SC-040**: Production deployment on Oracle OKE Always Free tier supports 100 concurrent users
- **SC-041**: Redpanda Cloud free tier supports development and staging environments with 10GB/month
- **SC-042**: Total cloud infrastructure cost remains under $50/month for production with 1,000 daily active users

#### Developer Experience

- **SC-043**: 90% of developers can deploy local environment successfully on first attempt
- **SC-044**: All services start successfully with `helm install` command (no manual post-install steps)
- **SC-045**: Troubleshooting documentation resolves 80% of common deployment issues
- **SC-046**: Service-to-service communication works without hardcoded URLs (Dapr service discovery)

## Assumptions *(mandatory)*

### Technical Assumptions

1. **Container Registry**: Docker Hub or cloud provider registry (Azure ACR, Google GCR) is available for storing Docker images
2. **DNS Management**: Cloud provider DNS service or external DNS provider available for domain management
3. **SSL Certificates**: Let's Encrypt or cloud provider certificate manager available for TLS termination
4. **Email Provider**: SMTP server credentials available for sending email notifications (Gmail, SendGrid, AWS SES)
5. **Database**: External PostgreSQL database (Neon, Azure Database, Cloud SQL) provisioned separately from Kubernetes cluster
6. **Kubernetes Version**: Minimum Kubernetes version 1.24+ for all deployments
7. **Dapr Version**: Minimum Dapr version 1.12+ with Jobs API support
8. **Kafka Compatibility**: All Kafka services (Redpanda, Confluent, Strimzi) support Kafka protocol 2.8+
9. **Helm Version**: Helm 3.10+ installed on developer machines and CI/CD runners
10. **Network Connectivity**: Outbound HTTPS access from Kubernetes cluster to external services (Kafka, database, email)

### Operational Assumptions

11. **Minikube Resources**: Developer workstations have minimum 8GB RAM and 4 CPU cores available for Minikube
12. **Cloud Quotas**: Cloud provider accounts have sufficient quotas for requested resources (VMs, load balancers, IP addresses)
13. **Free Tier Limits**: Oracle OKE Always Free tier provides 2 VMs with 1GB RAM each (sufficient for basic deployment)
14. **Redpanda Cloud Free Tier**: Provides 10GB data retention and 10MB/s throughput (sufficient for development)
15. **GitHub Actions**: GitHub repository has Actions enabled with sufficient runner minutes (2,000 minutes/month on free tier)
16. **kubectl Access**: Developers have kubectl configured with cluster admin permissions for deployments
17. **Container Build**: Developers have Docker or Podman installed for building container images locally

### Security Assumptions

18. **Secrets Management**: Kubernetes cluster supports native Secrets and developers have secure process for managing secret values
19. **RBAC**: Kubernetes RBAC is enabled and cluster administrators can create service accounts with appropriate permissions
20. **Network Policies**: Kubernetes cluster supports NetworkPolicy resource for pod-to-pod communication restrictions
21. **TLS**: Cloud load balancers support TLS termination and automatic certificate renewal
22. **Authentication**: Auth service from Phase IV provides JWT tokens that remain valid across Phase V services

### Data Assumptions

23. **User Scale**: System designed for up to 100,000 users with average 50 tasks per user
24. **Event Volume**: Peak event load estimated at 10,000 events/second across all topics
25. **Data Retention**: Task data retained indefinitely; audit logs retained for 90 days; Kafka events retained for 7 days
26. **Timezone Handling**: All timestamps stored in UTC; user timezone conversion handled by frontend
27. **Event Ordering**: Events within single Kafka partition maintain order; cross-partition ordering not guaranteed

### Development Assumptions

28. **Phase IV Completion**: All Phase IV Helm charts, Docker images, and services are functional and tested
29. **Testing Strategy**: Integration tests run against local Minikube environment; E2E tests run against staging environment
30. **Documentation**: Existing README files from Phase IV updated with Phase V deployment instructions
31. **Monitoring**: Kubernetes cluster has Prometheus and Grafana available (via kube-prometheus-stack or cloud provider)
32. **Version Control**: All Phase V code committed to feature branch and merged via pull request with code review

## Dependencies *(mandatory)*

### External Service Dependencies

1. **Neon PostgreSQL** (or equivalent): External managed PostgreSQL database required for all service state persistence
   - Status: Must be provisioned before deployment
   - Owner: DevOps team
   - Impact: Blocks all service deployments

2. **Redpanda Cloud** (or Confluent Cloud): Managed Kafka cluster required for production event streaming
   - Status: Must be provisioned before cloud deployment
   - Owner: DevOps team
   - Impact: Blocks production deployment (local uses Strimzi)

3. **SMTP Email Provider**: Email service credentials required for sending reminder notifications
   - Status: Must be configured before Notification Service deployment
   - Owner: Operations team
   - Impact: Blocks reminder functionality

4. **Container Registry**: Docker registry required for storing and distributing container images
   - Status: Must be accessible before CI/CD pipeline execution
   - Owner: DevOps team
   - Impact: Blocks image distribution

### Platform Dependencies

5. **Kubernetes Cluster**: Running Kubernetes cluster (Minikube or cloud provider) required for all deployments
   - Status: Must be provisioned and accessible via kubectl
   - Owner: Infrastructure team
   - Impact: Blocks all Phase V work

6. **Dapr Runtime**: Dapr control plane installed on Kubernetes cluster
   - Status: Must be installed after Kubernetes cluster is ready
   - Owner: DevOps team
   - Impact: Blocks all service deployments with Dapr sidecars

7. **Helm**: Helm 3.10+ required for deploying charts
   - Status: Must be installed on developer machines and CI/CD runners
   - Owner: Development team
   - Impact: Blocks chart-based deployments

8. **GitHub Actions**: GitHub repository with Actions enabled for CI/CD
   - Status: Available (assumed)
   - Owner: Development team
   - Impact: Blocks automated deployments

### Internal Service Dependencies

9. **Auth Service** (Phase IV): JWT token generation and validation required for all authenticated endpoints
   - Status: Deployed and operational from Phase IV
   - Owner: Backend team
   - Impact: Blocks all user-specific operations

10. **Frontend** (Phase IV): User interface required for testing end-to-end workflows
    - Status: Deployed and operational from Phase IV
    - Owner: Frontend team
    - Impact: Blocks user acceptance testing

11. **Phase IV Helm Charts**: Existing charts required as base for Phase V enhancements
    - Status: Completed in Phase IV
    - Owner: DevOps team
    - Impact: Blocks Helm chart development

### Data Dependencies

12. **Database Migrations**: Schema migrations for new fields (priority, tags, due_date, recurrence_rule, parent_task_id)
    - Status: Must be created and tested
    - Owner: Backend team
    - Impact: Blocks database-dependent services

13. **Event Schema Definitions**: JSON schemas for task-events, reminders, task-updates topics
    - Status: Must be defined and versioned
    - Owner: Architecture team
    - Impact: Blocks event producer/consumer implementation

### Configuration Dependencies

14. **Dapr Component Configurations**: YAML files defining pub/sub, state, secrets, and jobs components
    - Status: Must be created for each environment (local, dev, prod)
    - Owner: DevOps team
    - Impact: Blocks Dapr-enabled service deployments

15. **Kubernetes Secrets**: Secret resources containing sensitive credentials (database URLs, Kafka credentials, SMTP passwords)
    - Status: Must be created before service deployment
    - Owner: Operations team
    - Impact: Blocks services requiring sensitive configuration

16. **Environment-Specific Helm Values**: values-dev.yaml, values-staging.yaml, values-prod.yaml files
    - Status: Must be created with environment-specific overrides
    - Owner: DevOps team
    - Impact: Blocks multi-environment deployments

## Out of Scope *(mandatory)*

The following items are explicitly excluded from Phase V to maintain focus on core objectives:

### Advanced Kubernetes Features

1. **Service Mesh (Istio/Linkerd)**: Traffic management, circuit breaking, and advanced routing via service mesh
   - Rationale: Dapr provides sufficient service-to-service communication features; service mesh adds complexity
   - Future: Consider in Phase VI for advanced traffic management

2. **Custom Operators**: Kubernetes operators for managing custom resources
   - Rationale: Standard Kubernetes primitives sufficient for Phase V requirements
   - Future: Consider for automated database schema migrations or Kafka topic management

3. **Multi-Region Deployment**: Active-active or active-passive deployments across multiple cloud regions
   - Rationale: Single-region deployment sufficient for initial production launch
   - Future: Phase VI or VII for global availability

4. **Advanced Auto-Scaling**: Custom metrics-based HPA, vertical pod autoscaling (VPA), cluster autoscaling
   - Rationale: Basic CPU/memory-based HPA sufficient for Phase V workloads
   - Future: Add custom metrics (queue depth, event lag) in Phase VI

### Advanced Observability

5. **Distributed Tracing Backend**: Jaeger, Zipkin, or Tempo for storing and visualizing traces
   - Rationale: Dapr telemetry provides basic tracing; full backend adds operational overhead
   - Future: Add in Phase VI when trace volume justifies dedicated infrastructure

6. **Advanced Monitoring Stack**: Full Prometheus federation, long-term storage (Thanos, Cortex)
   - Rationale: Basic Prometheus sufficient for initial monitoring needs
   - Future: Add when retention and query performance requirements increase

7. **Log Aggregation Platform**: ELK Stack, Loki, or cloud provider log analytics
   - Rationale: Kubernetes native logging (`kubectl logs`) sufficient for Phase V troubleshooting
   - Future: Add when log volume and search requirements exceed native capabilities

8. **APM Tools**: Application Performance Monitoring tools like New Relic, Datadog, Dynatrace
   - Rationale: Adds significant cost; Prometheus + Dapr telemetry provide basic APM capabilities
   - Future: Evaluate when budget allows or specific APM features required

### Advanced Security

9. **mTLS Between Services**: Mutual TLS authentication for service-to-service communication
   - Rationale: Dapr supports mTLS but adds configuration complexity for initial deployment
   - Future: Enable in production hardening phase

10. **Network Policies**: Fine-grained pod-to-pod network traffic restrictions
    - Rationale: Kubernetes namespace isolation sufficient for Phase V security posture
    - Future: Add when compliance requirements mandate network segmentation

11. **Pod Security Policies/Standards**: Advanced pod security controls beyond basic non-root user
    - Rationale: Basic security contexts sufficient; PSP/PSS adds admission control complexity
    - Future: Implement for production hardening

12. **Secrets Encryption at Rest**: Encryption of Kubernetes Secrets in etcd
    - Rationale: Requires cluster-level configuration; not feasible for free-tier cloud clusters
    - Future: Enable when deploying to enterprise clusters

### Advanced Kafka Features

13. **Schema Registry**: Confluent Schema Registry or equivalent for enforcing event schemas
    - Rationale: Adds infrastructure dependency; JSON schema validation in code sufficient
    - Future: Add when multiple teams produce events and schema governance required

14. **Kafka Streams/ksqlDB**: Stream processing for complex event transformations
    - Rationale: Simple consume-process-publish pattern sufficient for Phase V event processing
    - Future: Consider when complex aggregations or windowing required

15. **Exactly-Once Semantics**: Kafka transactions for exactly-once event processing
    - Rationale: At-least-once with idempotency sufficient; exactly-once adds complexity
    - Future: Evaluate if duplicate processing becomes business problem

### Advanced Application Features

16. **Task Attachments**: File upload and storage for task-related documents
    - Rationale: Requires object storage integration (S3, Azure Blob); significant scope expansion
    - Future: Phase VI feature

17. **Task Comments/Collaboration**: Multi-user commenting and task discussions
    - Rationale: Adds significant complexity to data model and real-time sync requirements
    - Future: Phase VI or VII for collaboration features

18. **Advanced Recurrence Rules**: Custom recurrence (e.g., "2nd Tuesday of every month", "weekdays only")
    - Rationale: Simple daily/weekly/monthly rules cover 90% of use cases
    - Future: Add advanced rules based on user feedback

19. **Mobile Push Notifications**: iOS and Android push notification support
    - Rationale: Requires Firebase/APNs integration and mobile app development
    - Future: Phase VI when mobile apps are developed

20. **Calendar Integration**: Sync tasks with Google Calendar, Outlook, iCal
    - Rationale: Requires OAuth flows for each provider; significant integration effort
    - Future: Phase VII for ecosystem integration

### Infrastructure Automation

21. **Terraform/Infrastructure as Code**: Automated cloud infrastructure provisioning
    - Rationale: Manual cluster provisioning sufficient for Phase V; Terraform adds learning curve
    - Future: Add when managing multiple clusters or frequent infrastructure changes

22. **GitOps with ArgoCD/Flux**: Declarative continuous deployment from Git repositories
    - Rationale: GitHub Actions push-based deployment sufficient for initial CI/CD
    - Future: Phase VI for production-grade continuous deployment

23. **Automated Database Backups**: Scheduled database backup and restore automation
    - Rationale: Rely on managed database provider's backup features
    - Future: Add custom backup automation if provider features insufficient

### Development Tooling

24. **Local Development with Tilt/Skaffold**: Advanced local development workflows
    - Rationale: Standard `docker build` + `minikube load` + `helm install` workflow sufficient
    - Future: Add when developer onboarding time becomes bottleneck

25. **Service Code Generation**: Auto-generating service stubs from OpenAPI/Protobuf schemas
    - Rationale: Manual API implementation provides flexibility; code generation adds build complexity
    - Future: Consider when API contracts stabilize and multiple services need client generation
