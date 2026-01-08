# Tasks: Phase V - Advanced Cloud Deployment

**Input**: Design documents from `/specs/002-phase-v-cloud-deployment/`
**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Organization**: Tasks are grouped by implementation phase following strict dependency order. Each task is atomic, sequential, and implementation-ready for Claude Code.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Spec Validation & Environment Readiness

**Purpose**: Verify specifications are complete and prepare execution environment

**⚠️ CRITICAL**: All tasks in this phase MUST complete before proceeding to Phase 2

- [X] T001 Verify specs/002-phase-v-cloud-deployment/spec.md contains all 87 functional requirements
- [X] T002 Verify specs/002-phase-v-cloud-deployment/plan.md contains all 9 implementation phases
- [X] T003 Create specs/002-phase-v-cloud-deployment/research.md with architecture research template
- [X] T004 Document Kafka deployment decision (Strimzi vs Redpanda) in specs/002-phase-v-cloud-deployment/research.md
- [X] T005 Document Dapr component configuration patterns in specs/002-phase-v-cloud-deployment/research.md
- [X] T006 Document event schema versioning strategy in specs/002-phase-v-cloud-deployment/research.md
- [X] T007 Document idempotency key generation approach in specs/002-phase-v-cloud-deployment/research.md
- [X] T008 Document dead letter queue handling pattern in specs/002-phase-v-cloud-deployment/research.md
- [X] T009 Document Kubernetes namespace strategy in specs/002-phase-v-cloud-deployment/research.md
- [X] T010 Document Helm chart upgrade strategy in specs/002-phase-v-cloud-deployment/research.md
- [X] T011 Create specs/002-phase-v-cloud-deployment/data-model.md with database schema documentation
- [X] T012 Create specs/002-phase-v-cloud-deployment/quickstart.md with local deployment steps
- [X] T013 Create specs/002-phase-v-cloud-deployment/contracts/ directory for event schemas
- [X] T014 Create specs/002-phase-v-cloud-deployment/contracts/task-event-schema.json with Task Event schema
- [X] T015 Create specs/002-phase-v-cloud-deployment/contracts/reminder-event-schema.json with Reminder Event schema
- [X] T016 Create specs/002-phase-v-cloud-deployment/contracts/task-update-event-schema.json with Task Update Event schema
- [X] T017 Create specs/002-phase-v-cloud-deployment/contracts/kafka-topics.yaml with topic specifications

**Checkpoint**: Research and specification artifacts complete - implementation can begin

---

## Phase 2: Advanced Feature Enablement

**Purpose**: Extend database schema and API models for recurring tasks, due dates, priority, tags, and search

**Preconditions**: Phase 1 complete

**Deliverables**: Database migration, updated models, API contracts

### Database Schema

- [X] T018 Create backend/api-service/migrations/003_add_phase_v_fields.sql for Alembic migration
- [X] T019 Add priority VARCHAR(10) column to tasks table in backend/api-service/migrations/003_add_phase_v_fields.sql
- [X] T020 Add tags TEXT[] column to tasks table in backend/api-service/migrations/003_add_phase_v_fields.sql
- [X] T021 Add due_date TIMESTAMPTZ column to tasks table in backend/api-service/migrations/003_add_phase_v_fields.sql
- [X] T022 Add reminder_offset INTERVAL column to tasks table in backend/api-service/migrations/003_add_phase_v_fields.sql
- [X] T023 Add recurrence_rule JSONB column to tasks table in backend/api-service/migrations/003_add_phase_v_fields.sql
- [X] T024 Add parent_task_id INTEGER column to tasks table in backend/api-service/migrations/003_add_phase_v_fields.sql
- [X] T025 Create recurring_task_state table in backend/api-service/migrations/003_add_phase_v_fields.sql
- [X] T026 Create indexes (idx_tasks_priority, idx_tasks_tags, idx_tasks_due_date) in backend/api-service/migrations/003_add_phase_v_fields.sql

### API Models

- [X] T027 [P] Create backend/api-service/app/models/priority.py with Priority enum (low, medium, high, urgent)
- [X] T028 [P] Create backend/api-service/app/models/recurrence_rule.py with RecurrenceRule SQLModel
- [X] T029 Update backend/api-service/app/models.py to import Priority and RecurrenceRule
- [X] T030 Add priority field to Task model in backend/api-service/app/models.py
- [X] T031 Add tags field to Task model in backend/api-service/app/models.py
- [X] T032 Add due_date field to Task model in backend/api-service/app/models.py
- [X] T033 Add reminder_offset field to Task model in backend/api-service/app/models.py
- [X] T034 Add recurrence_rule field to Task model in backend/api-service/app/models.py
- [X] T035 Add parent_task_id field to Task model in backend/api-service/app/models.py
- [X] T036 Create backend/api-service/app/models/recurring_task_state.py with RecurringTaskState model

### API Enhancements

- [X] T037 Update backend/api-service/app/main.py to add search endpoint GET /api/tasks/search
- [X] T038 Update backend/api-service/app/main.py to add filter endpoint GET /api/tasks/filter
- [X] T039 Implement search_tasks function in backend/api-service/app/main.py with keyword matching
- [X] T040 Implement filter_tasks function in backend/api-service/app/main.py with priority, tags, status filters
- [X] T041 Add sort_tasks parameter support in backend/api-service/app/main.py (due_date, priority, created_at)

**Checkpoint**: Database schema extended, models updated, API contracts enhanced

---

## Phase 3: Kafka Event Backbone

**Purpose**: Provision Kafka topics and set up event infrastructure

**Preconditions**: Phase 2 complete

**Deliverables**: Kafka topic configurations, local Kafka deployment manifests

### Kafka Topic Provisioning

- [X] T042 Create kubernetes/kafka/local/strimzi-operator.yaml for Strimzi Operator deployment
- [X] T043 Create kubernetes/kafka/local/kafka-cluster.yaml with 3-broker Kafka cluster spec
- [X] T044 Create kubernetes/kafka/local/task-events-topic.yaml with 6 partitions and 3 replicas
- [X] T045 Create kubernetes/kafka/local/reminders-topic.yaml with 3 partitions and 3 replicas
- [X] T046 Create kubernetes/kafka/local/task-updates-topic.yaml with 6 partitions and 3 replicas
- [X] T047 Create kubernetes/kafka/local/dlq-events-topic.yaml with 3 partitions and 30-day retention
- [X] T048 Create kubernetes/kafka/cloud/redpanda-cloud-topics.yaml for cloud Kafka topic configurations

### Event Schemas

- [X] T049 [P] Create backend/api-service/app/events/__init__.py for events module
- [X] T050 [P] Create backend/api-service/app/events/schemas.py with TaskEvent Pydantic model
- [X] T051 [P] Create backend/api-service/app/events/schemas.py with ReminderEvent Pydantic model
- [X] T052 [P] Create backend/api-service/app/events/schemas.py with TaskUpdateEvent Pydantic model
- [X] T053 Add schema_version field to all event schemas in backend/api-service/app/events/schemas.py
- [X] T054 Add event_id UUID v4 generation to all event schemas in backend/api-service/app/events/schemas.py

### Event Publisher

- [X] T055 Create backend/api-service/app/dapr_client.py with DaprClient class for HTTP requests
- [X] T056 Create backend/api-service/app/events/publisher.py with DaprPublisher class
- [X] T057 Implement publish_task_event method in backend/api-service/app/events/publisher.py
- [X] T058 Implement publish_reminder_event method in backend/api-service/app/events/publisher.py
- [X] T059 Implement publish_task_update_event method in backend/api-service/app/events/publisher.py
- [X] T060 Add error handling with exponential backoff in backend/api-service/app/events/publisher.py
- [X] T061 Add dead letter queue publishing on max retry in backend/api-service/app/events/publisher.py

### API Integration

- [X] T062 Update backend/api-service/app/main.py to import DaprPublisher
- [X] T063 Add publish_task_event call after task creation in backend/api-service/app/main.py
- [X] T064 Add publish_task_event call after task update in backend/api-service/app/main.py
- [X] T065 Add publish_task_event call after task deletion in backend/api-service/app/main.py
- [X] T066 Add publish_task_event call after task completion in backend/api-service/app/main.py

**Checkpoint**: Kafka topics defined, event schemas implemented, API publishes events

---

## Phase 4: Dapr Integration Tasks

**Purpose**: Configure Dapr components for pub/sub, state, secrets, and jobs

**Preconditions**: Phase 3 complete

**Deliverables**: Dapr component YAML files, Dapr sidecar injection annotations

### Dapr Pub/Sub Component

- [X] T067 Create dapr-components/local/kafka-pubsub.yaml with Kafka pub/sub component for Minikube
- [X] T068 Configure brokers metadata in dapr-components/local/kafka-pubsub.yaml with localhost:9092
- [X] T069 Configure consumerGroup metadata in dapr-components/local/kafka-pubsub.yaml with unique group IDs
- [X] T070 Create dapr-components/cloud/kafka-pubsub.yaml with SASL/SSL configuration for Redpanda Cloud
- [X] T071 Add scopes field to dapr-components/cloud/kafka-pubsub.yaml to restrict service access

### Dapr State Store Component

- [X] T072 Create dapr-components/local/postgres-statestore.yaml with PostgreSQL state store component
- [X] T073 Configure connectionString metadata in dapr-components/local/postgres-statestore.yaml with Neon connection
- [X] T074 Configure tablePrefix metadata in dapr-components/local/postgres-statestore.yaml with "dapr_state_"
- [X] T075 Create dapr-components/cloud/postgres-statestore.yaml with production connection pool settings

### Dapr Secrets Component

- [X] T076 Create dapr-components/local/kubernetes-secrets.yaml with Kubernetes secret store component
- [X] T077 Create kubernetes/secrets/backend-secrets.yaml with SMTP credentials for Notification Service
- [X] T078 Create kubernetes/secrets/kafka-secrets.yaml with SASL credentials for cloud Kafka

### Dapr Jobs API Configuration

- [X] T079 Add Dapr Jobs API annotation to backend/api-service deployment for reminder scheduling
- [X] T080 Create backend/api-service/app/jobs/reminder_scheduler.py with schedule_reminder function
- [X] T081 Implement schedule_reminder using Dapr Jobs API HTTP endpoint in backend/api-service/app/jobs/reminder_scheduler.py
- [X] T082 Add reminder scheduling call after task creation with due_date in backend/api-service/app/main.py
- [X] T083 Add reminder cancellation call after task completion in backend/api-service/app/main.py
- [X] T084 Add reminder rescheduling call after due_date update in backend/api-service/app/main.py

### Dapr Service Invocation

- [X] T085 Update backend/api-service/app/main.py to use Dapr service invocation for auth token validation
- [X] T086 Replace direct HTTP call to auth-service with Dapr invocation in backend/api-service/app/main.py

**Checkpoint**: Dapr components configured, Jobs API enabled, service invocation wired

---

## Phase 5: Service-Level Execution - Chat API (US1, US3, US4, US5)

**Purpose**: Enhance Chat API service with event publishing and advanced features

**Preconditions**: Phase 4 complete

**Story Coverage**: US1 (Local Development), US3 (Recurring Tasks), US4 (Reminders), US5 (Advanced Management)

### Dockerfile Updates

- [X] T087 [P] [US1] Update backend/api-service/Dockerfile to expose port 3500 for Dapr sidecar
- [X] T088 [P] [US1] Add httpx dependency to backend/api-service/requirements.txt for Dapr client

### Recurring Task Support

- [X] T089 [US3] Add recurrence validation in backend/api-service/app/main.py POST /api/tasks endpoint
- [X] T090 [US3] Validate recurrence_rule frequency values (daily, weekly, monthly) in backend/api-service/app/main.py
- [X] T091 [US3] Validate days_of_week for weekly recurrence in backend/api-service/app/main.py
- [X] T092 [US3] Validate day_of_month for monthly recurrence in backend/api-service/app/main.py

### Reminder Support

- [X] T093 [US4] Add due_date validation in backend/api-service/app/main.py (must be future timestamp)
- [X] T094 [US4] Add reminder_offset validation in backend/api-service/app/main.py (valid ISO duration)
- [X] T095 [US4] Calculate reminder trigger time from due_date - reminder_offset in backend/api-service/app/jobs/reminder_scheduler.py
- [X] T096 [US4] Create reminder callback endpoint POST /api/reminders/trigger in backend/api-service/app/main.py
- [X] T097 [US4] Implement reminder callback to publish reminder event in backend/api-service/app/main.py

### Advanced Management

- [X] T098 [US5] Implement keyword search using PostgreSQL LIKE query in backend/api-service/app/main.py
- [X] T099 [US5] Implement priority filter using WHERE priority = clause in backend/api-service/app/main.py
- [X] T100 [US5] Implement tags filter using PostgreSQL array containment @> operator in backend/api-service/app/main.py
- [X] T101 [US5] Implement status filter in backend/api-service/app/main.py
- [X] T102 [US5] Implement due_date range filter in backend/api-service/app/main.py
- [X] T103 [US5] Implement sort by due_date, priority, created_at in backend/api-service/app/main.py
- [X] T104 [US5] Add pagination support (offset, limit) in backend/api-service/app/main.py

**Checkpoint**: Chat API enhanced with all Phase V features

---

## Phase 6: Service-Level Execution - Recurring Task Service (US3)

**Purpose**: Build event-driven service to generate recurring task occurrences

**Preconditions**: Phase 5 complete

**Story Coverage**: US3 (Recurring Task Management)

### Project Setup

- [X] T105 [P] [US3] Create backend/recurring-task-service/ directory
- [X] T106 [P] [US3] Create backend/recurring-task-service/app/ directory
- [X] T107 [P] [US3] Create backend/recurring-task-service/tests/ directory
- [X] T108 [P] [US3] Create backend/recurring-task-service/Dockerfile
- [X] T109 [P] [US3] Create backend/recurring-task-service/requirements.txt with FastAPI, httpx, python-dateutil

### Service Implementation

- [X] T110 [US3] Create backend/recurring-task-service/app/main.py with FastAPI app initialization
- [X] T111 [US3] Add Dapr subscription endpoint POST /dapr/subscribe in backend/recurring-task-service/app/main.py
- [X] T112 [US3] Configure subscription to task-events topic in backend/recurring-task-service/app/main.py
- [X] T113 [US3] Create backend/recurring-task-service/app/consumer.py with event handler
- [X] T114 [US3] Implement filter for task.completed event type in backend/recurring-task-service/app/consumer.py
- [X] T115 [US3] Create backend/recurring-task-service/app/generator.py with recurrence logic
- [X] T116 [US3] Implement calculate_next_occurrence for daily recurrence in backend/recurring-task-service/app/generator.py
- [X] T117 [US3] Implement calculate_next_occurrence for weekly recurrence in backend/recurring-task-service/app/generator.py
- [X] T118 [US3] Implement calculate_next_occurrence for monthly recurrence in backend/recurring-task-service/app/generator.py
- [X] T119 [US3] Create backend/recurring-task-service/app/dapr_client.py with Dapr State Management client
- [X] T120 [US3] Implement save_state for last_generated_at tracking in backend/recurring-task-service/app/dapr_client.py
- [X] T121 [US3] Implement get_state for idempotency check in backend/recurring-task-service/app/dapr_client.py
- [X] T122 [US3] Add idempotency check using event_id in backend/recurring-task-service/app/consumer.py
- [X] T123 [US3] Publish task.created event for new occurrence in backend/recurring-task-service/app/consumer.py
- [X] T124 [US3] Add error handling with DLQ publishing in backend/recurring-task-service/app/consumer.py

### Dockerfile

- [X] T125 [US3] Add Python 3.11 base image to backend/recurring-task-service/Dockerfile
- [X] T126 [US3] Copy requirements.txt and install dependencies in backend/recurring-task-service/Dockerfile
- [X] T127 [US3] Expose port 8000 in backend/recurring-task-service/Dockerfile
- [X] T128 [US3] Add CMD to run uvicorn in backend/recurring-task-service/Dockerfile

**Checkpoint**: Recurring Task Service complete and ready for deployment

---

## Phase 7: Service-Level Execution - Notification Service (US4)

**Purpose**: Build email notification service for task reminders

**Preconditions**: Phase 6 complete

**Story Coverage**: US4 (Due Date Reminders)

### Project Setup

- [X] T129 [P] [US4] Create backend/notification-service/ directory
- [X] T130 [P] [US4] Create backend/notification-service/app/ directory
- [X] T131 [P] [US4] Create backend/notification-service/app/templates/ directory
- [X] T132 [P] [US4] Create backend/notification-service/tests/ directory
- [X] T133 [P] [US4] Create backend/notification-service/Dockerfile
- [X] T134 [P] [US4] Create backend/notification-service/requirements.txt with FastAPI, httpx, aiosmtplib

### Service Implementation

- [X] T135 [US4] Create backend/notification-service/app/main.py with FastAPI app initialization
- [X] T136 [US4] Add Dapr subscription endpoint POST /dapr/subscribe in backend/notification-service/app/main.py
- [X] T137 [US4] Configure subscription to reminders topic in backend/notification-service/app/main.py
- [X] T138 [US4] Create backend/notification-service/app/consumer.py with reminder event handler
- [X] T139 [US4] Create backend/notification-service/app/email_sender.py with send_email function
- [X] T140 [US4] Implement SMTP connection using aiosmtplib in backend/notification-service/app/email_sender.py
- [X] T141 [US4] Create backend/notification-service/app/dapr_client.py with Dapr Secrets client
- [X] T142 [US4] Implement get_smtp_credentials from Kubernetes secrets in backend/notification-service/app/dapr_client.py
- [X] T143 [US4] Create backend/notification-service/app/templates/reminder.html with email template
- [X] T144 [US4] Add task title, due date, description to email template in backend/notification-service/app/templates/reminder.html
- [X] T145 [US4] Implement render_email_template in backend/notification-service/app/email_sender.py
- [X] T146 [US4] Add idempotency check using event_id in backend/notification-service/app/consumer.py
- [X] T147 [US4] Log sent notifications to audit log in backend/notification-service/app/consumer.py
- [X] T148 [US4] Add error handling with DLQ publishing in backend/notification-service/app/consumer.py

### Dockerfile

- [X] T149 [US4] Add Python 3.11 base image to backend/notification-service/Dockerfile
- [X] T150 [US4] Copy requirements.txt and install dependencies in backend/notification-service/Dockerfile
- [X] T151 [US4] Expose port 8000 in backend/notification-service/Dockerfile
- [X] T152 [US4] Add CMD to run uvicorn in backend/notification-service/Dockerfile

**Checkpoint**: Notification Service complete and ready for deployment

---

## Phase 8: Service-Level Execution - Audit Service (US7)

**Purpose**: Build audit logging service for compliance

**Preconditions**: Phase 7 complete

**Story Coverage**: US7 (Audit Log and Activity Tracking)

### Project Setup

- [X] T153 [P] [US7] Create backend/audit-service/ directory
- [X] T154 [P] [US7] Create backend/audit-service/app/ directory
- [X] T155 [P] [US7] Create backend/audit-service/tests/ directory
- [X] T156 [P] [US7] Create backend/audit-service/Dockerfile
- [X] T157 [P] [US7] Create backend/audit-service/requirements.txt with FastAPI, httpx, sqlmodel

### Database Schema

- [X] T158 [US7] Create backend/audit-service/migrations/001_create_audit_logs.sql
- [X] T159 [US7] Define audit_logs table with log_id, event_id, user_id, action_type, resource_type, timestamp in migrations
- [X] T160 [US7] Add indexes on user_id, action_type, timestamp in backend/audit-service/migrations/001_create_audit_logs.sql

### Service Implementation

- [X] T161 [US7] Create backend/audit-service/app/main.py with FastAPI app initialization
- [X] T162 [US7] Add Dapr subscription endpoint POST /dapr/subscribe in backend/audit-service/app/main.py
- [X] T163 [US7] Configure subscription to task-events, reminders, task-updates topics in backend/audit-service/app/main.py
- [X] T164 [US7] Create backend/audit-service/app/consumer.py with multi-topic event handler
- [X] T165 [US7] Create backend/audit-service/app/models.py with AuditLogEntry SQLModel
- [X] T166 [US7] Create backend/audit-service/app/database.py with PostgreSQL connection
- [X] T167 [US7] Implement insert_audit_log in backend/audit-service/app/consumer.py
- [X] T168 [US7] Add query endpoint GET /api/audit/logs in backend/audit-service/app/main.py
- [X] T169 [US7] Implement filter by user_id in backend/audit-service/app/main.py
- [X] T170 [US7] Implement filter by action_type in backend/audit-service/app/main.py
- [X] T171 [US7] Implement filter by date_range in backend/audit-service/app/main.py
- [X] T172 [US7] Add pagination support in backend/audit-service/app/main.py

### Dockerfile

- [X] T173 [US7] Add Python 3.11 base image to backend/audit-service/Dockerfile
- [X] T174 [US7] Copy requirements.txt and install dependencies in backend/audit-service/Dockerfile
- [X] T175 [US7] Expose port 8000 in backend/audit-service/Dockerfile
- [X] T176 [US7] Add CMD to run uvicorn in backend/audit-service/Dockerfile

**Checkpoint**: Audit Service complete and ready for deployment

---

## Phase 9: Service-Level Execution - WebSocket Sync Service (US6)

**Purpose**: Build real-time task synchronization service with WebSocket

**Preconditions**: Phase 8 complete

**Story Coverage**: US6 (Real-Time Task Synchronization)

### Project Setup

- [X] T177 [P] [US6] Create backend/websocket-sync-service/ directory
- [X] T178 [P] [US6] Create backend/websocket-sync-service/src/ directory
- [X] T179 [P] [US6] Create backend/websocket-sync-service/tests/ directory
- [X] T180 [P] [US6] Create backend/websocket-sync-service/Dockerfile
- [X] T181 [P] [US6] Create backend/websocket-sync-service/package.json with socket.io, axios, typescript

### Service Implementation

- [X] T182 [US6] Create backend/websocket-sync-service/src/server.ts with Socket.IO server initialization
- [X] T183 [US6] Add connection event handler in backend/websocket-sync-service/src/server.ts
- [X] T184 [US6] Create backend/websocket-sync-service/src/auth.ts with JWT token validation
- [X] T185 [US6] Implement authenticate_socket middleware in backend/websocket-sync-service/src/auth.ts
- [X] T186 [US6] Add user_id extraction from JWT in backend/websocket-sync-service/src/auth.ts
- [X] T187 [US6] Create backend/websocket-sync-service/src/consumer.ts with Dapr subscription handler
- [X] T188 [US6] Add POST /dapr/subscribe endpoint in backend/websocket-sync-service/src/server.ts
- [X] T189 [US6] Configure subscription to task-updates topic in backend/websocket-sync-service/src/server.ts
- [X] T190 [US6] Implement broadcast_to_user in backend/websocket-sync-service/src/consumer.ts
- [X] T191 [US6] Filter WebSocket connections by user_id in backend/websocket-sync-service/src/consumer.ts
- [X] T192 [US6] Emit task.sync event to connected clients in backend/websocket-sync-service/src/consumer.ts
- [X] T193 [US6] Create backend/websocket-sync-service/src/dapr-client.ts with Dapr State client
- [X] T194 [US6] Store active connections in Dapr State in backend/websocket-sync-service/src/dapr-client.ts
- [X] T195 [US6] Add disconnect event handler in backend/websocket-sync-service/src/server.ts
- [X] T196 [US6] Remove connection from Dapr State on disconnect in backend/websocket-sync-service/src/server.ts
- [X] T197 [US6] Add reconnection logic in backend/websocket-sync-service/src/server.ts

### Dockerfile

- [X] T198 [US6] Add Node.js 20 base image to backend/websocket-sync-service/Dockerfile
- [X] T199 [US6] Copy package.json and install dependencies in backend/websocket-sync-service/Dockerfile
- [X] T200 [US6] Build TypeScript in backend/websocket-sync-service/Dockerfile
- [X] T201 [US6] Expose port 8080 in backend/websocket-sync-service/Dockerfile
- [X] T202 [US6] Add CMD to run node server in backend/websocket-sync-service/Dockerfile

### Frontend Integration

- [X] T203 [US6] Create frontend/src/hooks/useWebSocket.ts with Socket.IO client hook
- [X] T204 [US6] Add connection to WebSocket Sync Service in frontend/src/hooks/useWebSocket.ts
- [X] T205 [US6] Add JWT token to connection auth in frontend/src/hooks/useWebSocket.ts
- [X] T206 [US6] Add task.sync event listener in frontend/src/hooks/useWebSocket.ts
- [X] T207 [US6] Update task list state on sync event in frontend/src/hooks/useWebSocket.ts
- [X] T208 [US6] Add auto-reconnect on disconnect in frontend/src/hooks/useWebSocket.ts

**Checkpoint**: WebSocket Sync Service complete, real-time updates working

---

## Phase 10: Local Kubernetes Deployment - Minikube (US1)

**Purpose**: Deploy all services to local Minikube with Dapr and Kafka

**Preconditions**: Phase 9 complete

**Story Coverage**: US1 (Local Development with Event-Driven Architecture)

### Minikube Setup

- [X] T209 [US1] Create docs/DEPLOYMENT.md with Minikube setup instructions
- [X] T210 [US1] Document minikube start command with 4 CPUs and 8GB RAM in docs/DEPLOYMENT.md
- [X] T211 [US1] Document dapr init -k command for Dapr installation in docs/DEPLOYMENT.md
- [X] T212 [US1] Document kubectl create namespace todo-app-dev in docs/DEPLOYMENT.md

### Kafka Deployment

- [X] T213 [US1] Document Strimzi Operator installation in docs/DEPLOYMENT.md
- [X] T214 [US1] Apply kubernetes/kafka/local/strimzi-operator.yaml to Minikube
- [X] T215 [US1] Apply kubernetes/kafka/local/kafka-cluster.yaml to Minikube
- [X] T216 [US1] Apply kubernetes/kafka/local/task-events-topic.yaml to Minikube
- [X] T217 [US1] Apply kubernetes/kafka/local/reminders-topic.yaml to Minikube
- [X] T218 [US1] Apply kubernetes/kafka/local/task-updates-topic.yaml to Minikube
- [X] T219 [US1] Apply kubernetes/kafka/local/dlq-events-topic.yaml to Minikube
- [X] T220 [US1] Wait for Kafka brokers to be ready using kubectl wait command

### Dapr Components Deployment

- [X] T221 [US1] Apply dapr-components/local/kafka-pubsub.yaml to todo-app-dev namespace
- [X] T222 [US1] Apply dapr-components/local/postgres-statestore.yaml to todo-app-dev namespace
- [X] T223 [US1] Apply dapr-components/local/kubernetes-secrets.yaml to todo-app-dev namespace
- [X] T224 [US1] Apply kubernetes/secrets/backend-secrets.yaml to todo-app-dev namespace

### Helm Chart Updates

- [X] T225 [P] [US1] Update charts/todo-chatbot-backend/Chart.yaml version to 2.0.0
- [X] T226 [P] [US1] Create charts/todo-chatbot-backend/values-local.yaml with Minikube overrides
- [X] T227 [US1] Add dapr.io/enabled annotation to charts/todo-chatbot-backend/templates/api-deployment.yaml
- [X] T228 [US1] Add dapr.io/app-id annotation to charts/todo-chatbot-backend/templates/api-deployment.yaml
- [X] T229 [US1] Add dapr.io/app-port annotation to charts/todo-chatbot-backend/templates/api-deployment.yaml

### Service Helm Templates

- [X] T230 [P] [US1] Create charts/todo-chatbot-backend/templates/recurring-task-deployment.yaml
- [X] T231 [P] [US1] Create charts/todo-chatbot-backend/templates/recurring-task-service.yaml with ClusterIP
- [X] T232 [P] [US1] Create charts/todo-chatbot-backend/templates/notification-deployment.yaml
- [X] T233 [P] [US1] Create charts/todo-chatbot-backend/templates/notification-service.yaml with ClusterIP
- [X] T234 [P] [US1] Create charts/todo-chatbot-backend/templates/audit-deployment.yaml
- [X] T235 [P] [US1] Create charts/todo-chatbot-backend/templates/audit-service.yaml with ClusterIP
- [X] T236 [P] [US1] Create charts/todo-chatbot-backend/templates/websocket-deployment.yaml
- [X] T237 [P] [US1] Create charts/todo-chatbot-backend/templates/websocket-service.yaml with NodePort

### Helm Deployment

- [X] T238 [US1] Build Docker images for all 5 services (api, recurring, notification, audit, websocket)
- [X] T239 [US1] Tag Docker images with latest and version tags
- [X] T240 [US1] Push Docker images to Docker Hub or local registry
- [X] T241 [US1] Run helm install backend charts/todo-chatbot-backend with values-local.yaml
- [X] T242 [US1] Wait for all pods to be ready using kubectl wait command
- [X] T243 [US1] Verify Dapr sidecars attached using kubectl get pods
- [X] T244 [US1] Check Dapr logs using kubectl logs with -c daprd flag

### Local Testing

- [X] T245 [US1] Create test script to create recurring task via Chat API
- [X] T246 [US1] Verify task-events topic receives event using kafka-console-consumer
- [X] T247 [US1] Verify Recurring Task Service processes event
- [X] T248 [US1] Create test script to create task with reminder
- [X] T249 [US1] Verify Dapr Jobs API schedules reminder job
- [X] T250 [US1] Verify Notification Service sends email

**Checkpoint**: Local Minikube deployment complete, all services running with Dapr

---

## Phase 11: Cloud Kubernetes Deployment (US2)

**Purpose**: Deploy to production Kubernetes cluster (AKS/GKE/OKE)

**Preconditions**: Phase 10 complete, US1 validated

**Story Coverage**: US2 (Production Multi-Cloud Deployment)

### Cloud Preparation

- [ ] T251 [US2] Create docs/CLOUD_DEPLOYMENT.md with cloud provider setup instructions
- [ ] T252 [US2] Document Azure AKS cluster creation in docs/CLOUD_DEPLOYMENT.md
- [ ] T253 [US2] Document Google GKE cluster creation in docs/CLOUD_DEPLOYMENT.md
- [ ] T254 [US2] Document Oracle OKE cluster creation in docs/CLOUD_DEPLOYMENT.md
- [ ] T255 [US2] Document kubectl context switching in docs/CLOUD_DEPLOYMENT.md

### Cloud Kafka Setup

- [ ] T256 [US2] Document Redpanda Cloud cluster creation in docs/CLOUD_DEPLOYMENT.md
- [ ] T257 [US2] Create Redpanda Cloud topics using redpanda-cloud CLI or web console
- [ ] T258 [US2] Generate SASL credentials for Kafka access
- [ ] T259 [US2] Update kubernetes/secrets/kafka-secrets.yaml with SASL credentials
- [ ] T260 [US2] Update dapr-components/cloud/kafka-pubsub.yaml with Redpanda Cloud brokers

### Dapr Cloud Installation

- [ ] T261 [US2] Install Dapr on cloud cluster using dapr init -k with production mode
- [ ] T262 [US2] Enable mTLS in Dapr configuration
- [ ] T263 [US2] Apply dapr-components/cloud/kafka-pubsub.yaml to todo-app-prod namespace
- [ ] T264 [US2] Apply dapr-components/cloud/postgres-statestore.yaml to todo-app-prod namespace
- [ ] T265 [US2] Apply dapr-components/cloud/kubernetes-secrets.yaml to todo-app-prod namespace

### Helm Cloud Deployment

- [ ] T266 [US2] Create charts/todo-chatbot-backend/values-cloud.yaml with production overrides
- [ ] T267 [US2] Configure resource limits (CPU, memory) in values-cloud.yaml
- [ ] T268 [US2] Configure HPA (Horizontal Pod Autoscaler) in values-cloud.yaml
- [ ] T269 [US2] Configure LoadBalancer service type for WebSocket in values-cloud.yaml
- [ ] T270 [US2] Run helm install backend charts/todo-chatbot-backend with values-cloud.yaml in todo-app-prod namespace
- [ ] T271 [US2] Wait for LoadBalancer external IP assignment
- [ ] T272 [US2] Configure DNS A record to point to LoadBalancer IP
- [ ] T273 [US2] Verify all pods running with kubectl get pods -n todo-app-prod

### Production Testing

- [ ] T274 [US2] Run end-to-end test suite against cloud deployment
- [ ] T275 [US2] Verify auto-scaling triggers with load test
- [ ] T276 [US2] Verify pod restart resilience
- [ ] T277 [US2] Verify zero-downtime rolling update

**Checkpoint**: Cloud deployment complete, production cluster operational

---

## Phase 12: CI/CD Pipeline Tasks (US8)

**Purpose**: Automate build, test, and deployment with GitHub Actions

**Preconditions**: Phase 11 complete

**Story Coverage**: US8 (CI/CD Pipeline for Automated Deployment)

### GitHub Actions Workflow

- [ ] T278 [P] [US8] Create .github/workflows/ci-cd.yaml
- [ ] T279 [P] [US8] Add workflow triggers for push to main and pull_request in .github/workflows/ci-cd.yaml
- [ ] T280 [US8] Create test job in .github/workflows/ci-cd.yaml
- [ ] T281 [US8] Add unit test step for api-service in .github/workflows/ci-cd.yaml
- [ ] T282 [US8] Add unit test step for recurring-task-service in .github/workflows/ci-cd.yaml
- [ ] T283 [US8] Add unit test step for notification-service in .github/workflows/ci-cd.yaml
- [ ] T284 [US8] Add unit test step for audit-service in .github/workflows/ci-cd.yaml
- [ ] T285 [US8] Add unit test step for websocket-sync-service in .github/workflows/ci-cd.yaml

### Build and Push

- [ ] T286 [US8] Create build job dependent on test job in .github/workflows/ci-cd.yaml
- [ ] T287 [US8] Add Docker buildx setup in .github/workflows/ci-cd.yaml
- [ ] T288 [US8] Add Docker login step with registry credentials in .github/workflows/ci-cd.yaml
- [ ] T289 [US8] Add build and push step for api-service image in .github/workflows/ci-cd.yaml
- [ ] T290 [US8] Add build and push step for recurring-task-service image in .github/workflows/ci-cd.yaml
- [ ] T291 [US8] Add build and push step for notification-service image in .github/workflows/ci-cd.yaml
- [ ] T292 [US8] Add build and push step for audit-service image in .github/workflows/ci-cd.yaml
- [ ] T293 [US8] Add build and push step for websocket-sync-service image in .github/workflows/ci-cd.yaml
- [ ] T294 [US8] Tag images with git commit SHA and latest in .github/workflows/ci-cd.yaml

### Deploy to Dev

- [ ] T295 [US8] Create deploy-dev job dependent on build job in .github/workflows/ci-cd.yaml
- [ ] T296 [US8] Add kubectl setup step in .github/workflows/ci-cd.yaml
- [ ] T297 [US8] Add kubeconfig secret to GitHub repository
- [ ] T298 [US8] Add helm upgrade step with values-cloud.yaml in .github/workflows/ci-cd.yaml
- [ ] T299 [US8] Add wait for rollout complete step in .github/workflows/ci-cd.yaml
- [ ] T300 [US8] Add health check verification step in .github/workflows/ci-cd.yaml

### Deploy to Production

- [ ] T301 [US8] Create deploy-prod job with manual approval in .github/workflows/ci-cd.yaml
- [ ] T302 [US8] Add environment protection rule in GitHub repository settings
- [ ] T303 [US8] Add helm upgrade step for production namespace in .github/workflows/ci-cd.yaml
- [ ] T304 [US8] Add blue-green deployment strategy in .github/workflows/ci-cd.yaml

### Rollback

- [ ] T305 [P] [US8] Create .github/workflows/rollback.yaml
- [ ] T306 [US8] Add manual workflow_dispatch trigger in .github/workflows/rollback.yaml
- [ ] T307 [US8] Add helm rollback step with revision input in .github/workflows/rollback.yaml
- [ ] T308 [US8] Add health check after rollback in .github/workflows/rollback.yaml

**Checkpoint**: CI/CD pipeline operational, automated deployments working

---

## Phase 13: Observability & Reliability

**Purpose**: Enable logging, metrics, monitoring, and alerting

**Preconditions**: Phase 12 complete

### Structured Logging

- [ ] T309 [P] Add JSON logging formatter to backend/api-service/app/main.py
- [ ] T310 [P] Add JSON logging formatter to backend/recurring-task-service/app/main.py
- [ ] T311 [P] Add JSON logging formatter to backend/notification-service/app/main.py
- [ ] T312 [P] Add JSON logging formatter to backend/audit-service/app/main.py
- [ ] T313 [P] Add JSON logging formatter to backend/websocket-sync-service/src/server.ts
- [ ] T314 Add correlation_id to all log entries across services
- [ ] T315 Add user_id to all log entries across services

### Prometheus Metrics

- [ ] T316 [P] Add prometheus_client to backend/api-service/requirements.txt
- [ ] T317 [P] Create backend/api-service/app/metrics.py with Prometheus metrics
- [ ] T318 [P] Add http_requests_total counter in backend/api-service/app/metrics.py
- [ ] T319 [P] Add http_request_duration_seconds histogram in backend/api-service/app/metrics.py
- [ ] T320 [P] Add task_operations_total counter in backend/api-service/app/metrics.py
- [ ] T321 Add metrics endpoint GET /metrics in backend/api-service/app/main.py
- [ ] T322 Replicate metrics setup for recurring-task-service, notification-service, audit-service

### Dapr Telemetry

- [ ] T323 Create kubernetes/dapr-config/dapr-config.yaml with telemetry enabled
- [ ] T324 Configure Prometheus exporter in kubernetes/dapr-config/dapr-config.yaml
- [ ] T325 Configure tracing with Zipkin in kubernetes/dapr-config/dapr-config.yaml
- [ ] T326 Apply dapr-config.yaml to all namespaces

### Monitoring Stack

- [ ] T327 Create kubernetes/monitoring/prometheus-deployment.yaml
- [ ] T328 Create kubernetes/monitoring/prometheus-service.yaml
- [ ] T329 Create kubernetes/monitoring/grafana-deployment.yaml
- [ ] T330 Create kubernetes/monitoring/grafana-service.yaml
- [ ] T331 Create kubernetes/monitoring/prometheus-configmap.yaml with scrape configs
- [ ] T332 Apply monitoring stack to todo-app-dev and todo-app-prod namespaces

### Dashboards

- [ ] T333 Create kubernetes/monitoring/grafana-dashboards/services-overview.json
- [ ] T334 Add API latency panel to services-overview.json
- [ ] T335 Add event processing rate panel to services-overview.json
- [ ] T336 Add consumer lag panel to services-overview.json
- [ ] T337 Add error rate panel to services-overview.json

### Alerting

- [ ] T338 Create kubernetes/monitoring/alertmanager-config.yaml
- [ ] T339 Add alert rule for pod crash loop in alertmanager-config.yaml
- [ ] T340 Add alert rule for high error rate (>5%) in alertmanager-config.yaml
- [ ] T341 Add alert rule for consumer lag >10 seconds in alertmanager-config.yaml
- [ ] T342 Add alert rule for DLQ growth in alertmanager-config.yaml
- [ ] T343 Configure notification channel (Slack, email) in alertmanager-config.yaml

**Checkpoint**: Observability stack deployed, metrics visible, alerts configured

---

## Phase 14: Security & Secrets

**Purpose**: Harden security with RBAC, network policies, and secret management

**Preconditions**: Phase 13 complete

### Kubernetes RBAC

- [ ] T344 [P] Create kubernetes/rbac/api-service-sa.yaml with ServiceAccount
- [ ] T345 [P] Create kubernetes/rbac/api-service-role.yaml with Role for secret access
- [ ] T346 [P] Create kubernetes/rbac/api-service-rolebinding.yaml
- [ ] T347 Replicate RBAC for recurring-task-service, notification-service, audit-service, websocket-sync-service
- [ ] T348 Update Helm templates to reference ServiceAccounts

### Network Policies

- [ ] T349 Create kubernetes/network-policies/default-deny.yaml to block all ingress by default
- [ ] T350 Create kubernetes/network-policies/api-service-policy.yaml to allow ingress from frontend
- [ ] T351 Create kubernetes/network-policies/kafka-access-policy.yaml to allow access to Kafka brokers
- [ ] T352 Create kubernetes/network-policies/postgres-access-policy.yaml to allow access to PostgreSQL
- [ ] T353 Apply network policies to todo-app-prod namespace

### Sealed Secrets

- [ ] T354 Install sealed-secrets controller on cloud cluster
- [ ] T355 Create sealed secret for SMTP credentials using kubeseal
- [ ] T356 Create sealed secret for Kafka SASL credentials using kubeseal
- [ ] T357 Create sealed secret for database connection string using kubeseal
- [ ] T358 Update Helm templates to reference SealedSecrets

### TLS/mTLS

- [ ] T359 Enable Dapr mTLS in dapr-config.yaml for production
- [ ] T360 Verify Dapr sidecar communication uses mTLS
- [ ] T361 Create kubernetes/ingress/tls-cert.yaml with Let's Encrypt certificate
- [ ] T362 Update WebSocket service to use TLS termination

**Checkpoint**: Security hardening complete, secrets encrypted, network isolated

---

## Phase 15: Production Readiness & Final Validation

**Purpose**: Load testing, chaos engineering, runbooks, final acceptance

**Preconditions**: Phase 14 complete

### Load Testing

- [ ] T363 [P] Create tests/load/k6-task-creation.js with k6 load test script
- [ ] T364 [P] Create tests/load/k6-recurring-tasks.js with recurring task load test
- [ ] T365 [P] Create tests/load/k6-websocket.js with WebSocket connection load test
- [ ] T366 Configure 10,000 concurrent users in k6 scripts
- [ ] T367 Set p95 latency threshold <500ms in k6 scripts
- [ ] T368 Run k6 load tests against cloud deployment
- [ ] T369 Analyze results and verify performance SLOs met
- [ ] T370 Optimize slow endpoints identified in load tests

### Chaos Engineering

- [ ] T371 Install Chaos Mesh on cloud cluster
- [ ] T372 Create tests/chaos/pod-kill-experiment.yaml to kill random pods
- [ ] T373 Create tests/chaos/network-delay-experiment.yaml to add network latency
- [ ] T374 Create tests/chaos/kafka-partition-experiment.yaml to simulate Kafka unavailability
- [ ] T375 Run chaos experiments and verify system resilience
- [ ] T376 Document recovery time for each failure scenario

### Runbooks

- [ ] T377 Create docs/RUNBOOKS.md with operational procedures
- [ ] T378 Document procedure for scaling services in docs/RUNBOOKS.md
- [ ] T379 Document procedure for rolling back deployment in docs/RUNBOOKS.md
- [ ] T380 Document procedure for investigating high consumer lag in docs/RUNBOOKS.md
- [ ] T381 Document procedure for handling DLQ events in docs/RUNBOOKS.md
- [ ] T382 Document procedure for database migration rollback in docs/RUNBOOKS.md

### Quickstart Validation

- [ ] T383 Update specs/002-phase-v-cloud-deployment/quickstart.md with complete local setup
- [ ] T384 Test quickstart.md on fresh workstation to verify accuracy
- [ ] T385 Document common errors and solutions in quickstart.md

### Final Acceptance

- [ ] T386 Verify all 8 user stories acceptance scenarios pass
- [ ] T387 Verify all 46 success criteria met
- [ ] T388 Run complete test suite (unit, integration, e2e, contract)
- [ ] T389 Verify cost <$50/month for 1,000 DAU on cloud deployment
- [ ] T390 Verify 99.9% uptime over 7-day monitoring period
- [ ] T391 Document known issues and future improvements

**Checkpoint**: Phase V complete, production-ready, all success criteria met

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1**: No dependencies - start immediately
- **Phase 2**: Depends on Phase 1 (research complete)
- **Phase 3**: Depends on Phase 2 (models ready)
- **Phase 4**: Depends on Phase 3 (Kafka topics exist)
- **Phase 5**: Depends on Phase 4 (Dapr components ready)
- **Phase 6-9**: Depends on Phase 5 (Chat API publishes events) - Services can be built in parallel
- **Phase 10**: Depends on Phases 6-9 (all services ready)
- **Phase 11**: Depends on Phase 10 (local deployment validated)
- **Phase 12**: Depends on Phase 11 (cloud deployment working)
- **Phase 13**: Depends on Phase 12 (services deployed)
- **Phase 14**: Depends on Phase 13 (observability in place)
- **Phase 15**: Depends on Phase 14 (security hardened)

### User Story Dependencies

- **US1 (Local Development)**: Foundational - enables all other stories
- **US2 (Cloud Deployment)**: Depends on US1 validation
- **US3 (Recurring Tasks)**: Can start after US1 (local infrastructure ready)
- **US4 (Reminders)**: Can start after US1 (local infrastructure ready)
- **US5 (Advanced Management)**: Can start after US1 (local infrastructure ready)
- **US6 (WebSocket Sync)**: Can start after US1 (local infrastructure ready)
- **US7 (Audit Logs)**: Can start after US1 (local infrastructure ready)
- **US8 (CI/CD)**: Depends on US2 (cloud deployment working)

### Parallel Opportunities

**Phase 1 (Research)**:
- T004-T010 can run in parallel (different research questions)
- T014-T017 can run in parallel (different event schemas)

**Phase 2 (Schema)**:
- T027-T028 can run in parallel (different model files)
- T037-T038 can run in parallel (different endpoints)

**Phase 3 (Events)**:
- T049-T052 can run in parallel (different schema files)
- T042-T047 can run in parallel (different Kafka topic manifests)

**Phase 4 (Dapr)**:
- T067-T071 can run in parallel (different Dapr components)
- T072-T075 can run in parallel (different state store configs)

**Phases 6-9 (Services)**:
- All four services (Recurring, Notification, Audit, WebSocket) can be built in parallel
- Within each service: Dockerfile, tests, documentation can be created in parallel

**Phase 13 (Observability)**:
- T309-T313 can run in parallel (logging for different services)
- T316-T320 can run in parallel (metrics for different services)

**Phase 14 (Security)**:
- T344-T346 can run in parallel (RBAC for different services)

---

## Parallel Example: Service Development (Phases 6-9)

```bash
# After Phase 5 completes, launch all service implementations in parallel:

# Team Member A:
Task: "Create backend/recurring-task-service/ directory"
Task: "Create backend/recurring-task-service/app/main.py with FastAPI app"
...

# Team Member B:
Task: "Create backend/notification-service/ directory"
Task: "Create backend/notification-service/app/main.py with FastAPI app"
...

# Team Member C:
Task: "Create backend/audit-service/ directory"
Task: "Create backend/audit-service/app/main.py with FastAPI app"
...

# Team Member D:
Task: "Create backend/websocket-sync-service/ directory"
Task: "Create backend/websocket-sync-service/src/server.ts with Socket.IO"
...
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Spec Validation & Environment Readiness
2. Complete Phase 2: Advanced Feature Enablement
3. Complete Phase 3: Kafka Event Backbone
4. Complete Phase 4: Dapr Integration
5. Complete Phase 5: Chat API Enhancements
6. Complete Phase 10: Local Kubernetes Deployment (Minikube)
7. **STOP and VALIDATE**: Test complete local workflow with Dapr and Kafka
8. Demo/Review before cloud deployment

### Incremental Delivery

1. Complete Phases 1-10 → Local deployment working (US1 delivered)
2. Add Phase 6 → Recurring tasks working (US3 delivered)
3. Add Phase 7 → Reminders working (US4 delivered)
4. Add Phase 8 → Audit logs working (US7 delivered)
5. Add Phase 9 → WebSocket sync working (US6 delivered)
6. Add Phase 11 → Cloud deployment working (US2 delivered)
7. Add Phase 12 → CI/CD working (US8 delivered)
8. Each phase adds value without breaking previous features

### Parallel Team Strategy

With 4 developers after Phase 5 completes:

1. Team completes Phases 1-5 together (foundational work)
2. Once Phase 5 done:
   - Developer A: Phase 6 (Recurring Task Service)
   - Developer B: Phase 7 (Notification Service)
   - Developer C: Phase 8 (Audit Service)
   - Developer D: Phase 9 (WebSocket Sync Service)
3. Reconvene for Phase 10 (Local Deployment)
4. Phases 11-15 can be parallelized by responsibility (infra vs testing vs docs)

---

## Notes

- **Total Tasks**: 391 atomic tasks
- **Estimated Duration**: 28-38 days (per plan.md Phase Summary)
- **Parallelization**: ~150 tasks marked [P] for parallel execution
- **User Story Coverage**: All 8 user stories covered across phases
- **Tests**: Optional - not included in this task list (can be added if TDD requested)
- **Commit Frequency**: Commit after each phase completion or logical group
- **Validation Checkpoints**: 15 checkpoints for independent story validation
- **Critical Path**: Phases 1-5 are sequential and block all service development
- **Risk Mitigation**: Early validation in Phase 10 before cloud spend in Phase 11

---

## Execution Commands

### Start Development

```bash
# 1. Create research document
Task T003: Create specs/002-phase-v-cloud-deployment/research.md

# 2. Begin database schema work
Task T018: Create backend/api-service/migrations/003_add_phase_v_fields.sql

# 3. After foundational work, parallelize service development
Task T105-T128: Recurring Task Service (Developer A)
Task T129-T152: Notification Service (Developer B)
Task T153-T176: Audit Service (Developer C)
Task T177-T208: WebSocket Sync Service (Developer D)
```

### Deploy Locally

```bash
# After Phase 10 tasks complete
minikube start --cpus 4 --memory 8192
dapr init -k
kubectl create namespace todo-app-dev
kubectl apply -f kubernetes/kafka/local/
kubectl apply -f dapr-components/local/
helm install backend charts/todo-chatbot-backend --namespace todo-app-dev --values charts/todo-chatbot-backend/values-local.yaml
```

### Deploy to Cloud

```bash
# After Phase 11 tasks complete
kubectl config use-context <cloud-cluster>
kubectl create namespace todo-app-prod
dapr init -k --enable-mtls
kubectl apply -f dapr-components/cloud/
helm install backend charts/todo-chatbot-backend --namespace todo-app-prod --values charts/todo-chatbot-backend/values-cloud.yaml
```

---

**End of Tasks**
