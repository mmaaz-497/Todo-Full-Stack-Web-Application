# Phase V: Cloud Deployment - Implementation Plan

## Project Overview
**Goal:** Deploy the Todo Chatbot application to production-grade Kubernetes with event-driven architecture using Kafka and Dapr.

**Timeline:** 12-18 days  
**Approach:** Agentic Dev Stack (Spec → Plan → Tasks → Implementation via Claude Code)

---

## Implementation Phases

```
Phase 1: Database & Advanced Features (Days 1-3)
    ↓
Phase 2: Kafka Integration (Days 4-5)
    ↓
Phase 3: Consumer Services (Days 6-8)
    ↓
Phase 4: Dapr Integration (Days 9-10)
    ↓
Phase 5: Local Deployment (Days 11-12)
    ↓
Phase 6: Cloud Deployment (Days 13-15)
    ↓
Phase 7: CI/CD & Monitoring (Days 16-17)
    ↓
Phase 8: Testing & Documentation (Days 18)
```

---

## Phase 1: Database Schema & Advanced Features (Days 1-3)

### 1.1 Database Schema Updates
**Priority:** High  
**Dependencies:** None  
**Estimated Time:** 4-6 hours

**Tasks:**
- [ ] Create migration file for recurring tasks columns
  ```sql
  ALTER TABLE tasks ADD COLUMN is_recurring BOOLEAN DEFAULT FALSE;
  ALTER TABLE tasks ADD COLUMN recurrence_pattern VARCHAR(20);
  ALTER TABLE tasks ADD COLUMN recurrence_end_date TIMESTAMP WITH TIME ZONE;
  ALTER TABLE tasks ADD COLUMN parent_task_id INTEGER REFERENCES tasks(id);
  ```

- [ ] Create migration for priority column
  ```sql
  ALTER TABLE tasks ADD COLUMN priority VARCHAR(10) DEFAULT 'medium';
  CREATE INDEX idx_tasks_priority ON tasks(priority);
  ```

- [ ] Create tags table and junction table
  ```sql
  CREATE TABLE tags (...);
  CREATE TABLE task_tags (...);
  ```

- [ ] Create audit_logs table for event storage
  ```sql
  CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    event_id UUID NOT NULL,
    event_type VARCHAR(50),
    task_id INTEGER,
    task_data JSONB,
    user_id VARCHAR(255),
    timestamp TIMESTAMP WITH TIME ZONE,
    metadata JSONB
  );
  ```

- [ ] Run migrations on Neon DB
- [ ] Verify schema changes with test queries

**Claude Code Prompt:**
```
Create database migration files for Phase V according to the specification in /specs/phase-v-cloud-deployment-spec.md section 4. Include:
1. Recurring tasks columns
2. Priority column with index
3. Tags and task_tags tables
4. Audit_logs table
5. All necessary indexes

Place migrations in backend/migrations/ folder.
```

### 1.2 Recurring Tasks Feature
**Priority:** High  
**Dependencies:** 1.1  
**Estimated Time:** 6-8 hours

**Tasks:**
- [ ] Update Task model to include recurring fields
- [ ] Create database queries for recurring task operations
- [ ] Implement `create_recurring_task` MCP tool
- [ ] Implement recurrence pattern calculation logic
- [ ] Add tests for recurring task creation
- [ ] Test various recurrence patterns (daily, weekly, monthly)

**Claude Code Prompt:**
```
Implement recurring tasks feature according to specification section 4.1:
1. Update backend/models/task.py with new fields
2. Add database queries in backend/db/queries.py
3. Create MCP tool in backend/mcp/tools/task_tools.py for create_recurring_task
4. Implement calculate_next_occurrence function
5. Add unit tests in backend/tests/test_recurring_tasks.py

Follow the exact schema and logic from the spec.
```

### 1.3 Priority System
**Priority:** Medium  
**Dependencies:** 1.1  
**Estimated Time:** 3-4 hours

**Tasks:**
- [ ] Update Task model with priority field
- [ ] Create `set_task_priority` MCP tool
- [ ] Add priority filtering to existing search queries
- [ ] Add validation for priority values
- [ ] Add tests for priority operations

**Claude Code Prompt:**
```
Implement task priority system per specification section 4.2:
1. Update Task model
2. Create set_task_priority MCP tool
3. Add priority to search/filter queries
4. Add validation and tests
```

### 1.4 Tags System
**Priority:** Medium  
**Dependencies:** 1.1  
**Estimated Time:** 4-6 hours

**Tasks:**
- [ ] Create Tag and TaskTag models
- [ ] Implement tag database queries (get_or_create, add_to_task, remove_from_task)
- [ ] Create `add_tags_to_task` MCP tool
- [ ] Create `remove_tag_from_task` MCP tool
- [ ] Create `search_by_tags` functionality
- [ ] Add tests for tag operations

**Claude Code Prompt:**
```
Implement tags system according to specification section 4.3:
1. Create models in backend/models/tag.py
2. Add tag queries in backend/db/queries.py
3. Create MCP tools for tag operations
4. Integrate tags into search functionality
5. Add comprehensive tests
```

### 1.5 Advanced Search, Filter, Sort
**Priority:** High  
**Dependencies:** 1.1, 1.3, 1.4  
**Estimated Time:** 6-8 hours

**Tasks:**
- [ ] Implement advanced `search_tasks` MCP tool with all parameters
- [ ] Create complex SQL query builder for filters
- [ ] Add support for:
  - Text search in title/description
  - Status filtering
  - Priority filtering
  - Tag filtering
  - Date range filtering (due_before, due_after)
  - Multi-field sorting
- [ ] Add pagination support
- [ ] Add tests for all filter combinations

**Claude Code Prompt:**
```
Implement advanced search functionality per specification section 4.4:
1. Create search_tasks MCP tool with all filter parameters
2. Implement dynamic SQL query builder in backend/db/queries.py
3. Support all filters: query, status, priority, tags, date ranges
4. Add sorting by multiple fields
5. Include pagination
6. Add comprehensive tests for edge cases
```

---

## Phase 2: Kafka Integration (Days 4-5)

### 2.1 Kafka Setup Decision
**Priority:** Critical  
**Dependencies:** None  
**Estimated Time:** 1-2 hours

**Tasks:**
- [ ] Choose Kafka deployment strategy:
  - Option A: Redpanda Cloud (easier, managed)
  - Option B: Strimzi self-hosted (learning experience)
- [ ] If Redpanda: Sign up and create cluster
- [ ] If Strimzi: Prepare Kubernetes manifests
- [ ] Document the chosen approach in README

**Manual Decision Point:** Choose based on:
- Available cloud credits
- Learning goals (Strimzi = more learning)
- Complexity tolerance

### 2.2 Kafka Topics Setup
**Priority:** Critical  
**Dependencies:** 2.1  
**Estimated Time:** 2-3 hours

**Tasks:**
- [ ] Create Kafka topics:
  - `task-events` (3 partitions, 3 replicas)
  - `reminders` (2 partitions, 3 replicas)
  - `task-updates` (2 partitions, 3 replicas)
  - `audit-logs` (1 partition, 2 replicas)
- [ ] Configure topic retention policies
- [ ] Test topic creation and accessibility
- [ ] Document bootstrap servers and credentials

**For Strimzi:**
```
Apply Kafka cluster YAML from spec section 2.3
Then apply topics YAML from spec section 5.1.2
```

**For Redpanda:**
```
Use Redpanda Cloud console to create topics
Save credentials in secure location
```

### 2.3 Kafka Producer Implementation
**Priority:** Critical  
**Dependencies:** 2.2  
**Estimated Time:** 6-8 hours

**Tasks:**
- [ ] Create `backend/services/kafka_producer.py` with TaskEventProducer class
- [ ] Implement event schemas (TaskEvent, ReminderEvent, TaskUpdateEvent)
- [ ] Add Kafka producer initialization to FastAPI app startup
- [ ] Integrate producer into existing MCP tools:
  - `create_task` → publish "created" event
  - `update_task` → publish "updated" event
  - `complete_task` → publish "completed" event
  - `delete_task` → publish "deleted" event
- [ ] Add error handling and retry logic
- [ ] Add producer metrics
- [ ] Add tests for producer

**Claude Code Prompt:**
```
Implement Kafka producer according to specification section 2.4:
1. Create backend/services/kafka_producer.py with TaskEventProducer class
2. Implement all event publishing methods
3. Integrate into existing MCP tools in backend/mcp/tools/task_tools.py
4. Add proper error handling
5. Add unit tests for producer
6. Use aiokafka library for async support

Ensure all events match the schemas in spec section 2.2.
```

### 2.4 Producer Integration Testing
**Priority:** High  
**Dependencies:** 2.3  
**Estimated Time:** 2-3 hours

**Tasks:**
- [ ] Test event publishing for each operation
- [ ] Verify events appear in Kafka topics (use kafka-console-consumer)
- [ ] Test error scenarios (Kafka down, network issues)
- [ ] Validate event schemas
- [ ] Performance test (can handle 100 events/sec?)

**Testing Commands:**
```bash
# Consume events to verify
kubectl exec -it taskflow-kafka-0 -n kafka -- \
  bin/kafka-console-consumer.sh \
  --topic task-events \
  --from-beginning \
  --bootstrap-server localhost:9092
```

---

## Phase 3: Consumer Services (Days 6-8)

### 3.1 Recurring Task Service
**Priority:** High  
**Dependencies:** 2.3  
**Estimated Time:** 6-8 hours

**Tasks:**
- [ ] Create service structure: `services/recurring-task-service/`
- [ ] Implement Kafka consumer for `task-events` topic
- [ ] Filter for "completed" events with `is_recurring=true`
- [ ] Implement `calculate_next_occurrence` logic
- [ ] Call backend API to create next task occurrence
- [ ] Add error handling and dead letter queue
- [ ] Create Dockerfile
- [ ] Add tests for recurrence calculation logic
- [ ] Add integration tests

**Claude Code Prompt:**
```
Create recurring task service according to specification section 2.5.1:
1. Set up service in services/recurring-task-service/
2. Implement Kafka consumer using aiokafka
3. Add business logic for processing completed recurring tasks
4. Implement calculate_next_occurrence for daily/weekly/monthly patterns
5. Add HTTP client to call backend API
6. Include error handling and logging
7. Create Dockerfile
8. Add unit and integration tests

Use FastAPI for the service framework.
```

### 3.2 Notification Service
**Priority:** High  
**Dependencies:** 2.3  
**Estimated Time:** 4-6 hours

**Tasks:**
- [ ] Create service structure: `services/notification-service/`
- [ ] Implement Kafka consumer for `reminders` topic
- [ ] Integrate with existing email service
- [ ] Add email template for reminders
- [ ] Add support for multiple notification channels (extensible)
- [ ] Add retry logic for failed sends
- [ ] Create Dockerfile
- [ ] Add tests

**Claude Code Prompt:**
```
Create notification service per specification section 2.5.3:
1. Set up service in services/notification-service/
2. Implement Kafka consumer for reminders topic
3. Integrate with email service (reuse existing email code)
4. Create email template for reminders
5. Add retry logic and error handling
6. Create Dockerfile
7. Add tests

The service should consume reminder events and send emails using the existing email configuration.
```

### 3.3 Audit Service
**Priority:** Medium  
**Dependencies:** 2.3  
**Estimated Time:** 4-5 hours

**Tasks:**
- [ ] Create service structure: `services/audit-service/`
- [ ] Implement Kafka consumer for `task-events` topic
- [ ] Store all events in `audit_logs` table
- [ ] Add batch insert optimization
- [ ] Add database connection pooling
- [ ] Create Dockerfile
- [ ] Add tests

**Claude Code Prompt:**
```
Create audit service according to specification section 2.5.2:
1. Set up service in services/audit-service/
2. Implement Kafka consumer for task-events topic
3. Store all events in audit_logs table
4. Use batch inserts for performance
5. Add proper error handling
6. Create Dockerfile
7. Add tests

Connect to same Neon database as backend.
```

### 3.4 WebSocket Service (Optional - Stretch Goal)
**Priority:** Low  
**Dependencies:** 2.3  
**Estimated Time:** 6-8 hours

**Tasks:**
- [ ] Create service structure: `services/websocket-service/`
- [ ] Implement WebSocket server with FastAPI
- [ ] Implement Kafka consumer for `task-updates` topic
- [ ] Maintain active WebSocket connections per user
- [ ] Broadcast updates to connected clients
- [ ] Add connection management
- [ ] Create Dockerfile
- [ ] Add tests

**Note:** This can be deferred to post-hackathon if time is tight.

### 3.5 Consumer Services Testing
**Priority:** High  
**Dependencies:** 3.1, 3.2, 3.3  
**Estimated Time:** 3-4 hours

**Tasks:**
- [ ] Test each consumer service individually
- [ ] Test end-to-end flow:
  1. Create recurring task via chatbot
  2. Complete task
  3. Verify next occurrence created
  4. Check audit log entry
- [ ] Test error scenarios
- [ ] Load testing with multiple concurrent events

---

## Phase 4: Dapr Integration (Days 9-10)

### 4.1 Dapr Installation
**Priority:** Critical  
**Dependencies:** None  
**Estimated Time:** 1-2 hours

**Tasks:**
- [ ] Install Dapr CLI locally
- [ ] Initialize Dapr on local development machine
- [ ] Install Dapr on Minikube (will be done in Phase 5)
- [ ] Verify Dapr installation
- [ ] Read Dapr documentation for components

**Commands:**
```bash
# Install Dapr CLI
curl -fsSL https://raw.githubusercontent.com/dapr/cli/master/install/install.sh | bash

# Init locally
dapr init

# Verify
dapr --version
```

### 4.2 Dapr Components Configuration
**Priority:** Critical  
**Dependencies:** 4.1, 2.2  
**Estimated Time:** 4-6 hours

**Tasks:**
- [ ] Create `k8s/dapr-components/` directory
- [ ] Create Pub/Sub component (pubsub.yaml) for Kafka
- [ ] Create State Store component (statestore.yaml) for PostgreSQL
- [ ] Create Secrets component (secrets.yaml) for Kubernetes secrets
- [ ] Configure component metadata (connection strings, etc.)
- [ ] Test components locally with `dapr run`
- [ ] Validate component configurations

**Claude Code Prompt:**
```
Create Dapr component configurations according to specification section 3.1:
1. Create k8s/dapr-components/ directory
2. Create pubsub.yaml for Kafka integration
3. Create statestore.yaml for PostgreSQL state management
4. Create secrets.yaml for Kubernetes secrets
5. Use exact configurations from spec

Adjust connection strings to use Kubernetes service names.
```

### 4.3 Dapr Publisher Implementation
**Priority:** High  
**Dependencies:** 4.2  
**Estimated Time:** 4-6 hours

**Tasks:**
- [ ] Create `backend/services/dapr_publisher.py`
- [ ] Implement DaprPublisher class with methods:
  - `publish_event()`
  - `publish_task_event()`
  - `publish_reminder()`
- [ ] Replace direct Kafka calls with Dapr API calls
- [ ] Update MCP tools to use Dapr publisher
- [ ] Add fallback to direct Kafka if Dapr unavailable
- [ ] Add tests

**Claude Code Prompt:**
```
Implement Dapr publisher according to specification section 3.2.1:
1. Create backend/services/dapr_publisher.py with DaprPublisher class
2. Implement event publishing via Dapr HTTP API (localhost:3500)
3. Refactor MCP tools to use Dapr instead of direct Kafka
4. Keep existing Kafka producer as fallback
5. Add comprehensive tests
6. Add proper error handling

Use httpx for async HTTP calls to Dapr sidecar.
```

### 4.4 Dapr State Management
**Priority:** Medium  
**Dependencies:** 4.2  
**Estimated Time:** 3-4 hours

**Tasks:**
- [ ] Create `backend/services/dapr_state.py`
- [ ] Implement DaprStateManager class
- [ ] Use for conversation history storage (optional enhancement)
- [ ] Add tests

**Claude Code Prompt:**
```
Implement Dapr state management per specification section 3.2.2:
1. Create backend/services/dapr_state.py
2. Implement save_state and get_state methods
3. Add conversation state management functions
4. Add tests
```

### 4.5 Dapr Service Invocation
**Priority:** Low  
**Dependencies:** 4.2  
**Estimated Time:** 2-3 hours

**Tasks:**
- [ ] Create `backend/services/dapr_client.py`
- [ ] Implement service-to-service calls via Dapr
- [ ] Update recurring task service to use Dapr invocation
- [ ] Add tests

**Note:** Can be deferred if time is tight.

### 4.6 Dapr Jobs API for Reminders
**Priority:** High  
**Dependencies:** 4.2  
**Estimated Time:** 4-6 hours

**Tasks:**
- [ ] Create `backend/services/dapr_scheduler.py`
- [ ] Implement `schedule_reminder()` method
- [ ] Create endpoint `/api/dapr/jobs/trigger` to receive job callbacks
- [ ] Integrate with task creation (schedule reminder when task has due date)
- [ ] Test scheduling and callback execution
- [ ] Add tests

**Claude Code Prompt:**
```
Implement Dapr Jobs API for reminders per specification section 3.2.4:
1. Create backend/services/dapr_scheduler.py
2. Implement schedule_reminder using Dapr Jobs API
3. Create FastAPI endpoint for job callbacks
4. Integrate into create_task MCP tool
5. Add tests for scheduling and callbacks

Use Dapr v1.0-alpha1 Jobs API.
```

### 4.7 Dapr Subscriptions for Consumers
**Priority:** High  
**Dependencies:** 4.2, 3.1, 3.2, 3.3  
**Estimated Time:** 4-6 hours

**Tasks:**
- [ ] Update consumer services to use Dapr Pub/Sub subscriptions
- [ ] Add `/dapr/subscribe` endpoint to each consumer
- [ ] Convert Kafka consumers to Dapr CloudEvent handlers
- [ ] Create Dapr Subscription YAML files
- [ ] Test subscriptions locally
- [ ] Add tests

**Claude Code Prompt:**
```
Update consumer services to use Dapr subscriptions per specification section 3.3:
1. Add /dapr/subscribe endpoint to recurring-task-service
2. Convert Kafka consumer to CloudEvent handler
3. Create Dapr Subscription YAML in k8s/dapr-subscriptions/
4. Repeat for notification-service and audit-service
5. Test with dapr run locally
6. Add integration tests

Follow the exact pattern from spec section 3.3.1 and 3.3.2.
```

---

## Phase 5: Local Deployment - Minikube (Days 11-12)

### 5.1 Minikube Setup
**Priority:** Critical  
**Dependencies:** None  
**Estimated Time:** 1-2 hours

**Tasks:**
- [ ] Install Minikube
- [ ] Start Minikube with adequate resources
- [ ] Verify kubectl access
- [ ] Install Helm if not already installed

**Commands:**
```bash
# Start Minikube
minikube start --cpus=4 --memory=8192 --disk-size=20g --driver=docker

# Verify
kubectl get nodes
```

### 5.2 Kafka Deployment on Minikube
**Priority:** Critical  
**Dependencies:** 5.1  
**Estimated Time:** 2-3 hours

**Tasks:**
- [ ] Create kafka namespace
- [ ] Install Strimzi operator
- [ ] Deploy Kafka cluster using spec from section 5.1.2
- [ ] Wait for Kafka to be ready
- [ ] Create Kafka topics
- [ ] Test Kafka accessibility from within cluster

**Commands:**
```bash
kubectl create namespace kafka
kubectl apply -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka
kubectl apply -f k8s/kafka/kafka-cluster.yaml -n kafka
kubectl wait kafka/taskflow-kafka --for=condition=Ready --timeout=300s -n kafka
kubectl apply -f k8s/kafka/topics.yaml -n kafka
```

### 5.3 Dapr Deployment on Minikube
**Priority:** Critical  
**Dependencies:** 5.1  
**Estimated Time:** 1 hour

**Tasks:**
- [ ] Initialize Dapr on Kubernetes
- [ ] Verify Dapr system pods running
- [ ] Deploy Dapr components
- [ ] Test Dapr components

**Commands:**
```bash
dapr init -k
dapr status -k
kubectl apply -f k8s/dapr-components/ -n default
```

### 5.4 Kubernetes Secrets Creation
**Priority:** Critical  
**Dependencies:** 5.1  
**Estimated Time:** 30 minutes

**Tasks:**
- [ ] Create secret for database connection string
- [ ] Create secret for OpenAI API key
- [ ] Create secret for email credentials
- [ ] Create secret for Kafka credentials (if using Redpanda)
- [ ] Verify secrets created

**Commands:**
```bash
kubectl create secret generic db-secrets \
  --from-literal=connection-string="$DATABASE_URL"

kubectl create secret generic api-secrets \
  --from-literal=openai-api-key="$OPENAI_API_KEY"

kubectl create secret generic email-secrets \
  --from-literal=smtp-password="$EMAIL_PASSWORD"
```

### 5.5 Docker Images Build
**Priority:** Critical  
**Dependencies:** All previous phases  
**Estimated Time:** 2-3 hours

**Tasks:**
- [ ] Create Dockerfile for backend
- [ ] Create Dockerfile for frontend
- [ ] Create Dockerfile for recurring-task-service
- [ ] Create Dockerfile for notification-service
- [ ] Create Dockerfile for audit-service
- [ ] Build all images
- [ ] Tag images appropriately
- [ ] Load images into Minikube (or push to registry)

**Commands:**
```bash
# Build images
docker build -t taskflow-backend:latest ./backend
docker build -t taskflow-frontend:latest ./frontend
docker build -t recurring-task-service:latest ./services/recurring-task-service
docker build -t notification-service:latest ./services/notification-service
docker build -t audit-service:latest ./services/audit-service

# Load into Minikube
minikube image load taskflow-backend:latest
minikube image load taskflow-frontend:latest
minikube image load recurring-task-service:latest
minikube image load notification-service:latest
minikube image load audit-service:latest
```

**Claude Code Prompt:**
```
Create Dockerfiles for all services:
1. backend/Dockerfile - FastAPI app
2. frontend/Dockerfile - Next.js app
3. services/recurring-task-service/Dockerfile
4. services/notification-service/Dockerfile
5. services/audit-service/Dockerfile

Use multi-stage builds for optimization.
Include health check endpoints.
```

### 5.6 Kubernetes Deployment Manifests
**Priority:** Critical  
**Dependencies:** 5.5  
**Estimated Time:** 4-6 hours

**Tasks:**
- [ ] Create deployment YAML for backend (with Dapr annotations)
- [ ] Create deployment YAML for frontend (with Dapr annotations)
- [ ] Create deployment YAML for recurring-task-service
- [ ] Create deployment YAML for notification-service
- [ ] Create deployment YAML for audit-service
- [ ] Create Service YAML for backend
- [ ] Create Service YAML for frontend
- [ ] Create Ingress YAML (optional for Minikube)
- [ ] Apply all manifests
- [ ] Verify all pods running

**Claude Code Prompt:**
```
Create Kubernetes deployment manifests according to specification section 5.1.4:
1. Create k8s/deployments/ directory
2. Create backend.yaml with Dapr sidecar annotations
3. Create frontend.yaml
4. Create recurring-task-service.yaml
5. Create notification-service.yaml
6. Create audit-service.yaml
7. Include proper resource limits, health checks, and environment variables
8. Create corresponding Service manifests

Follow exact structure from spec section 5.1.4.
```

### 5.7 Minikube Deployment Testing
**Priority:** Critical  
**Dependencies:** 5.6  
**Estimated Time:** 3-4 hours

**Tasks:**
- [ ] Verify all pods are running and healthy
- [ ] Check Dapr sidecars are injected
- [ ] Test frontend accessibility via `minikube service frontend-service --url`
- [ ] Test backend API health endpoint
- [ ] Create a task via chatbot
- [ ] Verify event appears in Kafka
- [ ] Verify consumers process events
- [ ] Test recurring task flow end-to-end
- [ ] Test reminder scheduling
- [ ] Check audit logs in database
- [ ] Test all advanced features (priorities, tags, search)

**Testing Checklist:**
```
□ Frontend loads successfully
□ Can authenticate with Better Auth
□ Can create task via chatbot
□ Task appears in UI
□ Event published to Kafka (check with console consumer)
□ Recurring task service processes completion
□ Notification service receives reminders
□ Audit service logs events to database
□ Can search and filter tasks
□ Can add tags and priorities
□ Real-time updates work (if WebSocket implemented)
```

### 5.8 Troubleshooting and Fixes
**Priority:** High  
**Dependencies:** 5.7  
**Estimated Time:** 4-8 hours (buffer)

**Common Issues:**
- [ ] Pods in CrashLoopBackOff → Check logs
- [ ] Dapr sidecar not injecting → Check annotations
- [ ] Kafka connection refused → Verify bootstrap servers
- [ ] Database connection errors → Check secrets
- [ ] Out of resources → Increase Minikube memory

**Debugging Commands:**
```bash
kubectl get pods -n default
kubectl logs <pod-name> -c <container-name>
kubectl describe pod <pod-name>
kubectl exec -it <pod-name> -- /bin/bash
dapr logs --app-id backend-service -k
```

---

## Phase 6: Cloud Deployment (Days 13-15)

### 6.1 Cloud Provider Selection
**Priority:** Critical  
**Dependencies:** None  
**Estimated Time:** 30 minutes

**Decision Matrix:**

| Provider | Free Tier | Pros | Cons | Recommendation |
|----------|-----------|------|------|----------------|
| Azure (AKS) | $200 for 30 days | Good integration, popular | Time limited | Good for quick demo |
| GCP (GKE) | $300 for 90 days | Generous credits, longer | Requires credit card | Best for extended dev |
| Oracle (OKE) | Always free 4 OCPU | No expiration, truly free | Less popular | **Best for hackathon** |

**Recommendation:** Oracle Cloud Infrastructure (OKE) for always-free tier.

**Tasks:**
- [ ] Sign up for chosen cloud provider
- [ ] Verify account and credits
- [ ] Set up billing alerts (if applicable)

### 6.2 Cloud Kubernetes Cluster Setup
**Priority:** Critical  
**Dependencies:** 6.1  
**Estimated Time:** 2-3 hours

**For Oracle Cloud (OKE):**
- [ ] Create OKE cluster via OCI Console
- [ ] Configure: 2 nodes, VM.Standard.E2.1.Micro
- [ ] Download kubeconfig
- [ ] Configure kubectl
- [ ] Verify cluster access

**For Azure (AKS):**
```bash
az login
az group create --name taskflow-rg --location eastus
az aks create --resource-group taskflow-rg --name taskflow-aks --node-count 3
az aks get-credentials --resource-group taskflow-rg --name taskflow-aks
```

**For GCP (GKE):**
```bash
gcloud container clusters create taskflow-gke \
  --zone us-central1-a --num-nodes 3
gcloud container clusters get-credentials taskflow-gke --zone us-central1-a
```

**Tasks:**
- [ ] Create cluster
- [ ] Get credentials
- [ ] Verify: `kubectl get nodes`
- [ ] Note down cluster info for documentation

### 6.3 Dapr Installation on Cloud
**Priority:** Critical  
**Dependencies:** 6.2  
**Estimated Time:** 30 minutes

**Tasks:**
- [ ] Initialize Dapr on cloud Kubernetes cluster
- [ ] Verify Dapr system pods
- [ ] Deploy Dapr components (same as Minikube)

**Commands:**
```bash
dapr init -k
dapr status -k
kubectl apply -f k8s/dapr-components/
```

### 6.4 Kafka Setup - Cloud Decision
**Priority:** Critical  
**Dependencies:** 6.2  
**Estimated Time:** 2-4 hours

**Option A: Redpanda Cloud (Recommended)**
- [ ] Sign up for Redpanda Cloud
- [ ] Create serverless cluster (free tier)
- [ ] Create topics (task-events, reminders, task-updates, audit-logs)
- [ ] Copy bootstrap servers and credentials
- [ ] Update Dapr Pub/Sub component with Redpanda credentials
- [ ] Create Kubernetes secret for Kafka credentials

**Option B: Strimzi Self-Hosted**
- [ ] Deploy Strimzi operator to cloud cluster
- [ ] Deploy Kafka cluster (adjust for cloud resources)
- [ ] Create topics
- [ ] Configure persistent storage

**Recommendation:** Use Redpanda Cloud for simplicity.

**Tasks:**
- [ ] Set up Kafka service
- [ ] Test connectivity from within cluster
- [ ] Update Dapr component configuration
- [ ] Document bootstrap servers

### 6.5 Container Registry Setup
**Priority:** Critical  
**Dependencies:** 6.1  
**Estimated Time:** 1-2 hours

**Options:**
- Docker Hub (free public repos)
- GitHub Container Registry (recommended)
- Cloud provider registry (GCR, ACR, OCIR)

**Tasks:**
- [ ] Choose registry
- [ ] Create repository for each image
- [ ] Configure authentication
- [ ] Test push/pull

**For GitHub Container Registry:**
```bash
# Login
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Tag images
docker tag taskflow-backend:latest ghcr.io/username/taskflow-backend:v1.0.0

# Push
docker push ghcr.io/username/taskflow-backend:v1.0.0
```

### 6.6 Push Docker Images
**Priority:** Critical  
**Dependencies:** 6.5, 5.5  
**Estimated Time:** 1-2 hours

**Tasks:**
- [ ] Tag all images with registry prefix and version
- [ ] Push backend image
- [ ] Push frontend image
- [ ] Push recurring-task-service image
- [ ] Push notification-service image
- [ ] Push audit-service image
- [ ] Verify images in registry

### 6.7 Update Kubernetes Manifests for Cloud
**Priority:** High  
**Dependencies:** 6.6  
**Estimated Time:** 2-3 hours

**Tasks:**
- [ ] Update image references to registry URLs
- [ ] Update resource limits for cloud (increase if possible)
- [ ] Update Kafka bootstrap servers (if using Redpanda Cloud)
- [ ] Add imagePullSecrets if using private registry
- [ ] Update database connection string
- [ ] Review and adjust for cloud environment

**Claude Code Prompt:**
```
Update Kubernetes manifests for cloud deployment:
1. Change image references to ghcr.io/username/...
2. Update Kafka connection in Dapr components for Redpanda Cloud
3. Adjust resource limits
4. Add imagePullSecrets if needed
5. Create separate manifests in k8s/cloud/ directory
```

### 6.8 Create Cloud Secrets
**Priority:** Critical  
**Dependencies:** 6.2  
**Estimated Time:** 30 minutes

**Tasks:**
- [ ] Create db-secrets with Neon connection string
- [ ] Create api-secrets with OpenAI API key
- [ ] Create email-secrets
- [ ] Create kafka-secrets (if using Redpanda Cloud with auth)
- [ ] Create imagePullSecret for container registry (if private)

### 6.9 Deploy to Cloud
**Priority:** Critical  
**Dependencies:** 6.7, 6.8  
**Estimated Time:** 2-3 hours

**Tasks:**
- [ ] Create namespace: `kubectl create namespace taskflow`
- [ ] Apply secrets
- [ ] Deploy Kafka (if self-hosted) or configure Redpanda connection
- [ ] Deploy Dapr components
- [ ] Deploy application services
- [ ] Wait for all pods to be ready
- [ ] Check pod status
- [ ] Check logs for errors

**Commands:**
```bash
kubectl apply -f k8s/secrets/ -n taskflow
kubectl apply -f k8s/dapr-components/ -n taskflow
kubectl apply -f k8s/deployments/ -n taskflow

# Monitor deployment
kubectl get pods -n taskflow -w
```

### 6.10 Ingress and DNS Setup
**Priority:** High  
**Dependencies:** 6.9  
**Estimated Time:** 2-3 hours

**Tasks:**
- [ ] Install ingress controller (nginx)
- [ ] Create Ingress resource
- [ ] Get external IP
- [ ] Configure DNS (or use nip.io for testing)
- [ ] (Optional) Set up cert-manager for HTTPS
- [ ] (Optional) Configure Let's Encrypt certificate

**Commands:**
```bash
# Install nginx ingress
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml

# Apply ingress
kubectl apply -f k8s/ingress.yaml -n taskflow

# Get external IP
kubectl get ingress -n taskflow
```

### 6.11 Cloud Deployment Testing
**Priority:** Critical  
**Dependencies:** 6.10  
**Estimated Time:** 4-6 hours

**Full End-to-End Testing:**
- [ ] Access application via public URL
- [ ] Test authentication flow
- [ ] Create tasks via chatbot
- [ ] Verify events in Kafka (Redpanda console or CLI)
- [ ] Test recurring tasks
- [ ] Test reminders (check email delivery)
- [ ] Test priorities and tags
- [ ] Test search and filters
- [ ] Check audit logs in database
- [ ] Load test with multiple concurrent users
- [ ] Test all edge cases

**Performance Testing:**
- [ ] Test with 100 tasks
- [ ] Test with 10 concurrent users
- [ ] Monitor resource usage
- [ ] Check for memory leaks
- [ ] Verify auto-scaling (if configured)

### 6.12 Cloud Troubleshooting
**Priority:** High  
**Dependencies:** 6.11  
**Estimated Time:** 4-8 hours (buffer)

**Common Cloud Issues:**
- [ ] LoadBalancer external IP pending → Check cloud provider quotas
- [ ] Pods stuck in Pending → Check node resources
- [ ] Ingress not working → Check ingress controller logs
- [ ] DNS not resolving → Check DNS configuration
- [ ] High latency → Check network policies, add caching
- [ ] Kafka connection issues → Verify security groups/firewall rules

---

## Phase 7: CI/CD & Monitoring (Days 16-17)

### 7.1 GitHub Actions CI/CD Pipeline
**Priority:** High  
**Dependencies:** Phase 6  
**Estimated Time:** 4-6 hours

**Tasks:**
- [ ] Create `.github/workflows/deploy.yml`
- [ ] Configure build job:
  - Checkout code
  - Build Docker images
  - Push to registry
- [ ] Configure deploy job:
  - Update Kubernetes manifests
  - Deploy to cluster
  - Verify deployment
- [ ] Add secrets to GitHub (KUBECONFIG, REGISTRY_TOKEN)
- [ ] Test pipeline with a commit
- [ ] Add status badges to README

**Claude Code Prompt:**
```
Create GitHub Actions workflow according to specification section 6.1:
1. Create .github/workflows/deploy.yml
2. Implement matrix build for all services
3. Add deploy job with kubectl
4. Include verification steps
5. Add branch protection (main only)

Use the exact workflow structure from spec section 6.1.
```

### 7.2 Helm Charts (Optional Enhancement)
**Priority:** Low  
**Dependencies:** Phase 6  
**Estimated Time:** 3-4 hours

**Tasks:**
- [ ] Create Helm chart structure
- [ ] Convert YAML to Helm templates
- [ ] Create values.yaml
- [ ] Test Helm install locally
- [ ] Document Helm usage

**Note:** Can be skipped if time is tight. Raw YAML is acceptable.

### 7.3 Monitoring Setup
**Priority:** Medium  
**Dependencies:** 6.9  
**Estimated Time:** 3-4 hours

**Tasks:**
- [ ] Install Prometheus stack
- [ ] Configure ServiceMonitor for Dapr metrics
- [ ] Access Grafana dashboard
- [ ] Import Dapr dashboards
- [ ] Create custom dashboard for task metrics
- [ ] Set up alerts (optional)

**Commands:**
```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace
```

### 7.4 Logging Setup
**Priority:** Medium  
**Dependencies:** 6.9  
**Estimated Time:** 2-3 hours

**Options:**
- Use cloud provider logging (easiest)
- Deploy EFK stack (Elasticsearch, Fluentd, Kibana)
- Use Loki + Grafana

**Tasks:**
- [ ] Choose logging solution
- [ ] Deploy logging stack (if not using cloud provider)
- [ ] Configure log aggregation
- [ ] Create log queries for debugging
- [ ] Test log search

**Recommendation:** Use cloud provider logging (CloudWatch, Cloud Logging) for simplicity.

### 7.5 Application Metrics
**Priority:** Low  
**Dependencies:** 7.3  
**Estimated Time:** 2-3 hours

**Tasks:**
- [ ] Add Prometheus client to backend
- [ ] Expose custom metrics:
  - `tasks_created_total`
  - `tasks_completed_total`
  - `events_published_total`
  - `event_processing_duration_seconds`
- [ ] Add metrics endpoint `/metrics`
- [ ] Configure Prometheus to scrape app metrics
- [ ] Create Grafana dashboard

**Note:** Dapr already provides many metrics, so this is optional.

---

## Phase 8: Testing, Documentation & Demo (Day 18)

### 8.1 Comprehensive Testing
**Priority:** Critical  
**Dependencies:** All phases  
**Estimated Time:** 3-4 hours

**Test Checklist:**

**Functional Tests:**
- [ ] User can sign up and log in
- [ ] User can create task via chatbot
- [ ] User can create recurring task
- [ ] Recurring task spawns next occurrence
- [ ] User receives email reminders
- [ ] User can set priorities
- [ ] User can add tags
- [ ] User can search and filter
- [ ] All CRUD operations work
- [ ] Events flow through Kafka correctly
- [ ] Audit logs are created

**Non-Functional Tests:**
- [ ] Application handles 10 concurrent users
- [ ] Response time < 2 seconds for task creation
- [ ] No memory leaks after 1 hour of use
- [ ] Application recovers from Kafka downtime
- [ ] Database connections are properly pooled

**Edge Cases:**
- [ ] Empty search query
- [ ] Invalid date formats
- [ ] Very long task titles (1000+ characters)
- [ ] Special characters in task content
- [ ] Rapid task creation (100 tasks in 1 minute)

### 8.2 Documentation Writing
**Priority:** Critical  
**Dependencies:** All phases  
**Estimated Time:** 3-4 hours

**Tasks:**
- [ ] Update README.md with:
  - Project overview
  - Architecture diagram
  - Features list
  - Setup instructions (local and cloud)
  - Environment variables
  - Deployment guide
  - Troubleshooting section
- [ ] Create CLAUDE.md with:
  - Development workflow
  - Key technologies
  - Code style guidelines
  - Testing requirements
  - Claude Code prompts used
- [ ] Add architecture diagrams (use Excalidraw or draw.io)
- [ ] Document API endpoints
- [ ] Add inline code comments
- [ ] Create CHANGELOG.md

**Claude Code Prompt:**
```
Create comprehensive documentation:
1. Generate README.md following the structure in spec section 10.1
2. Create CLAUDE.md with development guidelines per spec section 10.2
3. Include architecture diagrams (as ASCII art or Mermaid)
4. Document all environment variables
5. Add troubleshooting guide with common issues

Base content on actual implementation and spec document.
```

### 8.3 Demo Video Creation
**Priority:** Critical  
**Dependencies:** 8.1, 8.2  
**Estimated Time:** 2-3 hours

**Video Script (90 seconds max):**

```
[0-15s] Introduction
- "Hi, I'm [Name], presenting TaskFlow Phase V"
- "An event-driven todo app built with Kafka, Dapr, and Kubernetes"
- Show title slide with project name

[15-30s] Architecture Overview
- Show architecture diagram
- "The backend publishes events to Kafka"
- "Consumer services process events asynchronously"
- "Dapr provides abstraction and portability"

[30-50s] Feature Demo
- Screen recording of chatbot
- "Create a recurring task: 'Team standup every Monday'"
- Show task in UI
- Complete the task
- "Watch as the next occurrence is automatically created"
- Show email reminder received

[50-70s] Deployment Demo
- Terminal: `kubectl get pods -n taskflow`
- Show all pods running
- Terminal: `kubectl get services`
- Show live URL
- Browser: Access application at public URL

[70-90s] Code Quality
- Show GitHub repository
- Show specs/ folder
- Show CLAUDE.md
- "All code generated from specifications using Claude Code"
- "Thank you for watching!"
```

**Tasks:**
- [ ] Write detailed script
- [ ] Record screen (use OBS Studio or QuickTime)
- [ ] Edit video (cut to 90 seconds max)
- [ ] Add subtitles (optional but helpful)
- [ ] Upload to YouTube (unlisted)
- [ ] Add video link to README

### 8.4 Final Repository Cleanup
**Priority:** High  
**Dependencies:** 8.2  
**Estimated Time:** 1-2 hours

**Tasks:**
- [ ] Remove any sensitive data from code
- [ ] Remove unused files and code
- [ ] Format all code consistently
- [ ] Run linters (black, eslint)
- [ ] Fix all linting warnings
- [ ] Update .gitignore
- [ ] Remove commented-out code
- [ ] Ensure all files have proper headers
- [ ] Tag release: `git tag v1.0.0`
- [ ] Push to GitHub

### 8.5 Submission Preparation
**Priority:** Critical  
**Dependencies:** 8.4  
**Estimated Time:** 1 hour

**Submission Checklist:**
- [ ] Public GitHub repository URL
- [ ] README.md with all required sections
- [ ] CLAUDE.md with development instructions
- [ ] specs/ folder with phase-v-spec.md
- [ ] Live application URL (cloud deployment)
- [ ] Demo video URL (YouTube)
- [ ] WhatsApp number for judging
- [ ] All required features implemented
- [ ] No exposed secrets in repository

**Submission Package:**
```
Submission Form:
- GitHub URL: https://github.com/username/taskflow
- Live URL: https://taskflow.yourdomain.com
- Video URL: https://youtube.com/watch?v=...
- WhatsApp: +92-XXX-XXXXXXX

Verification:
✓ Repository is public
✓ Application is accessible
✓ Video is under 90 seconds
✓ All documentation is complete
```

---

## Risk Management & Contingencies

### High-Risk Items
1. **Kafka Setup Complexity**
   - **Risk:** Strimzi might be too complex
   - **Mitigation:** Use Redpanda Cloud instead
   - **Fallback:** Simple message queue with Redis

2. **Cloud Resource Limits**
   - **Risk:** Free tier might be insufficient
   - **Mitigation:** Use Oracle Always Free tier
   - **Fallback:** Deploy only on Minikube, document cloud setup

3. **Dapr Learning Curve**
   - **Risk:** Team unfamiliar with Dapr
   - **Mitigation:** Follow spec exactly, use provided examples
   - **Fallback:** Direct Kafka integration (skip Dapr)

4. **Time Constraints**
   - **Risk:** 18 days might not be enough
   - **Mitigation:** Prioritize core features, defer optional ones

### Features to Defer if Time is Tight
1. WebSocket Service (real-time sync) - Low priority
2. Helm charts - Can use raw YAML
3. Advanced monitoring setup - Use basic metrics
4. Dapr Service Invocation - Not critical for core functionality
5. Complete EFK logging stack - Use cloud provider logs

---

## Daily Progress Tracking

### Daily Standup Template
```
Date: ___________

Completed Yesterday:
- Task 1
- Task 2

Planning Today:
- Task 1 (estimate: X hours)
- Task 2 (estimate: X hours)

Blockers:
- Issue 1 (action: ...)

Risks:
- Risk 1 (mitigation: ...)
```

### Phase Completion Criteria

**Phase 1 Complete When:**
- [ ] All database migrations applied
- [ ] All advanced features (recurring, priority, tags, search) working
- [ ] Tests passing

**Phase 2 Complete When:**
- [ ] Kafka topics created and accessible
- [ ] Producer publishes events successfully
- [ ] Events visible in Kafka

**Phase 3 Complete When:**
- [ ] All consumer services deployed
- [ ] End-to-end event flow working
- [ ] Tests passing

**Phase 4 Complete When:**
- [ ] Dapr components configured
- [ ] Services use Dapr APIs
- [ ] Subscriptions working

**Phase 5 Complete When:**
- [ ] Application fully deployed on Minikube
- [ ] All features working locally
- [ ] No critical bugs

**Phase 6 Complete When:**
- [ ] Application deployed to cloud
- [ ] Accessible via public URL
- [ ] All features working in production

**Phase 7 Complete When:**
- [ ] CI/CD pipeline functional
- [ ] Monitoring dashboards showing data
- [ ] Logs aggregated

**Phase 8 Complete When:**
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Demo video uploaded
- [ ] Repository cleaned and tagged

---

## Resource Links

### Documentation
- [Phase V Specification](/specs/phase-v-cloud-deployment-spec.md)
- [Dapr Docs](https://docs.dapr.io/)
- [Kafka Docs](https://kafka.apache.org/documentation/)
- [Strimzi Docs](https://strimzi.io/docs/)
- [Kubernetes Docs](https://kubernetes.io/docs/)

### Tools
- Claude Code: claude.com/product/claude-code
- Redpanda Cloud: redpanda.com/cloud
- Neon DB: neon.tech
- Minikube: minikube.sigs.k8s.io

### Community
- Dapr Discord
- Kubernetes Slack
- Stack Overflow

---

## Success Metrics

### Technical Success
- ✅ 100% feature completion (all advanced features working)
- ✅ Zero critical bugs in production
- ✅ < 2 second response time for API calls
- ✅ 99%+ uptime during demo period
- ✅ All tests passing (unit + integration + e2e)

### Process Success
- ✅ Used Claude Code for 100% of implementation
- ✅ Followed Agentic Dev Stack workflow
- ✅ All code generated from specifications
- ✅ Iterative development with reviews

### Presentation Success
- ✅ Demo video under 90 seconds
- ✅ Clear architecture explanation
- ✅ Working live demo
- ✅ Professional documentation

---

## Final Checklist Before Submission

- [ ] All phases completed
- [ ] Application running in production (cloud)
- [ ] Public GitHub repository with all code
- [ ] README.md comprehensive and clear
- [ ] CLAUDE.md with development workflow
- [ ] specs/ folder with complete specification
- [ ] Demo video uploaded and linked
- [ ] No secrets exposed in repository
- [ ] All environment variables documented
- [ ] Troubleshooting guide included
- [ ] License file added (if required)
- [ ] Contributors acknowledged
- [ ] Contact information provided
- [ ] Submission form filled out

---

**Good luck with Phase V implementation! Follow this plan systematically, use Claude Code for all development, and refer back to the specification frequently. You've got this! 🚀**