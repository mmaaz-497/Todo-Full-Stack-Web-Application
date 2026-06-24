# Phase V: Advanced Cloud Deployment - Specification

## Project Overview
Deploy the Todo Chatbot application to production-grade Kubernetes (AKS/GKE/OKE) with advanced event-driven architecture using Kafka and Dapr. The application must first be deployed locally on Minikube, then promoted to cloud infrastructure.

## Current Application State
- ✅ Todo app with chatbot interface (MCP-based)
- ✅ Task CRUD operations via natural language
- ✅ Email reminder system (scheduled reminders)
- ✅ Authentication (Better Auth)
- ✅ Database (Neon PostgreSQL)

## Phase V Objectives

### Part A: Advanced Features Implementation
1. Implement all Advanced Level features:
   - Recurring tasks (daily, weekly, monthly patterns)
   - Due dates with timezone support
   - Reminder scheduling system (already implemented - enhance with Kafka)

2. Implement Intermediate Level features:
   - Task priorities (High, Medium, Low)
   - Tags/labels system
   - Search functionality across tasks
   - Filter by status, priority, tags, due date
   - Sort by created date, due date, priority

3. Add Event-Driven Architecture:
   - Kafka integration for event streaming
   - Event publishers and consumers
   - Asynchronous event processing

4. Add Dapr Integration:
   - Pub/Sub for Kafka abstraction
   - State Management for conversation history
   - Service Invocation for inter-service communication
   - Jobs API for scheduled reminders
   - Secrets Management for credentials

### Part B: Local Deployment (Minikube)
1. Deploy complete application stack on Minikube
2. Deploy Dapr on Minikube with full capabilities
3. Test all features locally before cloud promotion

### Part C: Cloud Deployment
1. Deploy to Azure (AKS) or Google Cloud (GKE) or Oracle Cloud (OKE)
2. Deploy Dapr on cloud Kubernetes
3. Integrate managed Kafka (Redpanda Cloud or Strimzi self-hosted)
4. Set up CI/CD pipeline (GitHub Actions)
5. Configure monitoring and logging

---

## Detailed Technical Specifications

## 1. Architecture Overview

### 1.1 System Architecture

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                         KUBERNETES CLUSTER (AKS/GKE/OKE)                         │
│                                                                                  │
│  ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐               │
│  │  Frontend Pod   │   │  Backend Pod    │   │ Notification Pod│               │
│  │  ┌───────────┐  │   │  ┌───────────┐  │   │  ┌───────────┐  │               │
│  │  │ Next.js   │  │   │  │ FastAPI   │  │   │  │ Notif     │  │               │
│  │  │ + Chat UI │  │   │  │ + MCP     │  │   │  │ Service   │  │               │
│  │  └─────┬─────┘  │   │  └─────┬─────┘  │   │  └─────┬─────┘  │               │
│  │  ┌─────▼─────┐  │   │  ┌─────▼─────┐  │   │  ┌─────▼─────┐  │               │
│  │  │   Dapr    │  │   │  │   Dapr    │  │   │  │   Dapr    │  │               │
│  │  │  Sidecar  │  │   │  │  Sidecar  │  │   │  │  Sidecar  │  │               │
│  │  └───────────┘  │   │  └───────────┘  │   │  └───────────┘  │               │
│  └─────────────────┘   └─────────────────┘   └─────────────────┘               │
│                                                                                  │
│  ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐               │
│  │ Recurring Task  │   │  Audit Service  │   │  WebSocket      │               │
│  │    Service      │   │                 │   │  Service        │               │
│  │  ┌───────────┐  │   │  ┌───────────┐  │   │  ┌───────────┐  │               │
│  │  │ Consumer  │  │   │  │ Consumer  │  │   │  │ Consumer  │  │               │
│  │  └─────┬─────┘  │   │  └─────┬─────┘  │   │  └─────┬─────┘  │               │
│  │  ┌─────▼─────┐  │   │  ┌─────▼─────┐  │   │  ┌─────▼─────┐  │               │
│  │  │   Dapr    │  │   │  │   Dapr    │  │   │  │   Dapr    │  │               │
│  │  └───────────┘  │   │  └───────────┘  │   │  └───────────┘  │               │
│  └─────────────────┘   └─────────────────┘   └─────────────────┘               │
│                                                                                  │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │                        DAPR COMPONENTS                                   │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐         │   │
│  │  │ pubsub.kafka    │  │ state.postgres  │  │ secretstore.k8s │         │   │
│  │  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘         │   │
│  └───────────┼────────────────────┼────────────────────┼──────────────────┘   │
│              │                    │                    │                       │
└──────────────┼────────────────────┼────────────────────┼───────────────────────┘
               │                    │                    │
               ▼                    ▼                    ▼
      ┌────────────────┐   ┌────────────────┐   ┌────────────────┐
      │ KAFKA CLUSTER  │   │   NEON DB      │   │  K8S SECRETS   │
      │ (Redpanda/     │   │  (PostgreSQL)  │   │                │
      │  Strimzi)      │   │                │   │                │
      └────────────────┘   └────────────────┘   └────────────────┘
```

### 1.2 Event-Driven Flow

```
Task Operation (Create/Update/Delete) → Backend MCP Tool
                                            ↓
                                   Publish to Kafka
                                            ↓
                        ┌───────────────────┼───────────────────┐
                        ▼                   ▼                   ▼
              Recurring Task Service  Audit Service    WebSocket Service
                        ↓                   ↓                   ↓
                Auto-create next      Store history     Broadcast to clients
```

---

## 2. Kafka Integration Specifications

### 2.1 Kafka Topics

| Topic Name | Partitions | Replication | Purpose | Producers | Consumers |
|------------|------------|-------------|---------|-----------|-----------|
| `task-events` | 3 | 3 | All task CRUD operations | Backend API | Recurring Service, Audit Service, WebSocket Service |
| `reminders` | 2 | 3 | Scheduled reminder triggers | Backend API | Notification Service |
| `task-updates` | 2 | 3 | Real-time client synchronization | Backend API | WebSocket Service |
| `audit-logs` | 1 | 2 | Immutable audit trail | Audit Service | Analytics (future) |

### 2.2 Event Schemas

#### Task Event Schema
```json
{
  "event_id": "uuid",
  "event_type": "created | updated | completed | deleted",
  "task_id": "integer",
  "task_data": {
    "id": "integer",
    "title": "string",
    "description": "string",
    "status": "pending | in_progress | completed",
    "priority": "high | medium | low",
    "tags": ["string"],
    "due_at": "ISO8601 datetime",
    "is_recurring": "boolean",
    "recurrence_pattern": "daily | weekly | monthly | null",
    "created_at": "ISO8601 datetime",
    "updated_at": "ISO8601 datetime"
  },
  "user_id": "string",
  "timestamp": "ISO8601 datetime",
  "metadata": {
    "source": "chatbot | api | ui",
    "ip_address": "string (optional)"
  }
}
```

#### Reminder Event Schema
```json
{
  "reminder_id": "uuid",
  "task_id": "integer",
  "title": "string",
  "description": "string",
  "due_at": "ISO8601 datetime",
  "remind_at": "ISO8601 datetime",
  "user_id": "string",
  "user_email": "string",
  "notification_channels": ["email", "push"],
  "timestamp": "ISO8601 datetime"
}
```

#### Task Update Event Schema (Real-time sync)
```json
{
  "update_id": "uuid",
  "task_id": "integer",
  "change_type": "created | updated | deleted | status_changed",
  "updated_fields": ["field_name"],
  "task_snapshot": { /* full task object */ },
  "user_id": "string",
  "timestamp": "ISO8601 datetime"
}
```

### 2.3 Kafka Setup Options

#### Option A: Redpanda Cloud (Recommended for Hackathon)
**Pros:**
- Free serverless tier
- Kafka-compatible API
- No Zookeeper required
- Fast setup (<5 minutes)
- Managed service (no maintenance)

**Setup Steps:**
1. Sign up at redpanda.com/cloud
2. Create serverless cluster
3. Create topics: `task-events`, `reminders`, `task-updates`, `audit-logs`
4. Copy bootstrap server URL and SASL credentials
5. Store credentials in Kubernetes secrets

**Configuration:**
```yaml
# config/kafka-config.yaml
bootstrap_servers: "your-cluster.redpanda.cloud:9092"
security_protocol: "SASL_SSL"
sasl_mechanism: "SCRAM-SHA-256"
sasl_username: "{{ from secret }}"
sasl_password: "{{ from secret }}"
```

#### Option B: Self-Hosted Kafka with Strimzi
**Pros:**
- Zero cost (except compute)
- Full control
- Great learning experience
- Production-grade operator

**Setup Steps:**
```bash
# Install Strimzi operator
kubectl create namespace kafka
kubectl apply -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka

# Deploy Kafka cluster
kubectl apply -f k8s/kafka-cluster.yaml -n kafka

# Wait for cluster ready
kubectl wait kafka/taskflow-kafka --for=condition=Ready --timeout=300s -n kafka
```

**Kafka Cluster Configuration:**
```yaml
# k8s/kafka-cluster.yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: taskflow-kafka
  namespace: kafka
spec:
  kafka:
    version: 3.6.0
    replicas: 3
    listeners:
      - name: plain
        port: 9092
        type: internal
        tls: false
      - name: tls
        port: 9093
        type: internal
        tls: true
    config:
      offsets.topic.replication.factor: 3
      transaction.state.log.replication.factor: 3
      transaction.state.log.min.isr: 2
      default.replication.factor: 3
      min.insync.replicas: 2
      inter.broker.protocol.version: "3.6"
    storage:
      type: persistent-claim
      size: 10Gi
      deleteClaim: false
  zookeeper:
    replicas: 3
    storage:
      type: persistent-claim
      size: 5Gi
      deleteClaim: false
  entityOperator:
    topicOperator: {}
    userOperator: {}
```

### 2.4 Kafka Producer Implementation

**Backend API Producer (FastAPI)**
```python
# backend/services/kafka_producer.py
from aiokafka import AIOKafkaProducer
import json
from datetime import datetime
from typing import Dict, Any

class TaskEventProducer:
    def __init__(self, bootstrap_servers: str):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            compression_type='gzip',
            acks='all'
        )
    
    async def start(self):
        await self.producer.start()
    
    async def stop(self):
        await self.producer.stop()
    
    async def publish_task_event(
        self, 
        event_type: str, 
        task_data: Dict[str, Any],
        user_id: str,
        source: str = "chatbot"
    ):
        """Publish task event to Kafka"""
        event = {
            "event_id": str(uuid.uuid4()),
            "event_type": event_type,
            "task_id": task_data["id"],
            "task_data": task_data,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": {
                "source": source
            }
        }
        
        await self.producer.send_and_wait(
            topic="task-events",
            value=event,
            key=str(task_data["id"]).encode('utf-8')
        )
    
    async def publish_reminder(
        self,
        task_id: int,
        title: str,
        due_at: datetime,
        remind_at: datetime,
        user_id: str,
        user_email: str
    ):
        """Publish reminder event"""
        event = {
            "reminder_id": str(uuid.uuid4()),
            "task_id": task_id,
            "title": title,
            "due_at": due_at.isoformat(),
            "remind_at": remind_at.isoformat(),
            "user_id": user_id,
            "user_email": user_email,
            "notification_channels": ["email"],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.producer.send_and_wait(
            topic="reminders",
            value=event,
            key=str(task_id).encode('utf-8')
        )
```

**Integration with MCP Tools**
```python
# backend/mcp/tools/task_tools.py
from backend.services.kafka_producer import TaskEventProducer

producer = TaskEventProducer(bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS"))

@mcp_tool()
async def create_task(title: str, description: str = "", due_at: str = None):
    """Create a new task"""
    # Create task in database
    task = await db.create_task(title=title, description=description, due_at=due_at)
    
    # Publish event to Kafka
    await producer.publish_task_event(
        event_type="created",
        task_data=task.dict(),
        user_id=current_user.id,
        source="chatbot"
    )
    
    # If task has due date, schedule reminder
    if task.due_at:
        remind_at = task.due_at - timedelta(hours=1)  # 1 hour before
        await producer.publish_reminder(
            task_id=task.id,
            title=task.title,
            due_at=task.due_at,
            remind_at=remind_at,
            user_id=current_user.id,
            user_email=current_user.email
        )
    
    return task
```

### 2.5 Kafka Consumer Services

#### 2.5.1 Recurring Task Service
**Purpose:** Auto-create next occurrence when recurring task is completed

```python
# services/recurring-task-service/main.py
from aiokafka import AIOKafkaConsumer
import json
from datetime import datetime, timedelta

class RecurringTaskService:
    def __init__(self):
        self.consumer = AIOKafkaConsumer(
            'task-events',
            bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
            group_id='recurring-task-service',
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
    
    async def start(self):
        await self.consumer.start()
        async for message in self.consumer:
            await self.handle_event(message.value)
    
    async def handle_event(self, event: dict):
        """Process task events for recurring tasks"""
        if event['event_type'] != 'completed':
            return
        
        task_data = event['task_data']
        
        if not task_data.get('is_recurring'):
            return
        
        # Calculate next occurrence
        next_due = self.calculate_next_occurrence(
            current_due=datetime.fromisoformat(task_data['due_at']),
            pattern=task_data['recurrence_pattern']
        )
        
        # Create next task via API
        await self.create_next_task(task_data, next_due)
    
    def calculate_next_occurrence(self, current_due: datetime, pattern: str):
        """Calculate next due date based on recurrence pattern"""
        if pattern == 'daily':
            return current_due + timedelta(days=1)
        elif pattern == 'weekly':
            return current_due + timedelta(weeks=1)
        elif pattern == 'monthly':
            # Add one month (handle edge cases)
            return current_due + timedelta(days=30)
        return None
```

#### 2.5.2 Audit Service
**Purpose:** Maintain immutable audit trail of all task operations

```python
# services/audit-service/main.py
from aiokafka import AIOKafkaConsumer
import json

class AuditService:
    def __init__(self):
        self.consumer = AIOKafkaConsumer(
            'task-events',
            bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
            group_id='audit-service',
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
    
    async def start(self):
        await self.consumer.start()
        async for message in self.consumer:
            await self.store_audit_log(message.value)
    
    async def store_audit_log(self, event: dict):
        """Store event in audit_logs table"""
        await db.execute(
            """
            INSERT INTO audit_logs (
                event_id, event_type, task_id, task_data, 
                user_id, timestamp, metadata
            ) VALUES ($1, $2, $3, $4, $5, $6, $7)
            """,
            event['event_id'],
            event['event_type'],
            event['task_id'],
            json.dumps(event['task_data']),
            event['user_id'],
            event['timestamp'],
            json.dumps(event['metadata'])
        )
```

#### 2.5.3 Notification Service
**Purpose:** Send email reminders at scheduled times

```python
# services/notification-service/main.py
from aiokafka import AIOKafkaConsumer
import json
from email_service import send_email

class NotificationService:
    def __init__(self):
        self.consumer = AIOKafkaConsumer(
            'reminders',
            bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
            group_id='notification-service',
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
    
    async def start(self):
        await self.consumer.start()
        async for message in self.consumer:
            await self.send_reminder(message.value)
    
    async def send_reminder(self, reminder: dict):
        """Send reminder email"""
        await send_email(
            to=reminder['user_email'],
            subject=f"Reminder: {reminder['title']}",
            body=f"""
            Your task "{reminder['title']}" is due at {reminder['due_at']}.
            
            Task ID: {reminder['task_id']}
            Due: {reminder['due_at']}
            """
        )
```

#### 2.5.4 WebSocket Service (Real-time Sync)
**Purpose:** Broadcast task updates to all connected clients

```python
# services/websocket-service/main.py
from aiokafka import AIOKafkaConsumer
import json
from fastapi import WebSocket

class WebSocketService:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.consumer = AIOKafkaConsumer(
            'task-updates',
            bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
            group_id='websocket-service',
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
    
    async def start(self):
        await self.consumer.start()
        async for message in self.consumer:
            await self.broadcast_update(message.value)
    
    async def broadcast_update(self, update: dict):
        """Broadcast to all connected clients of the user"""
        user_id = update['user_id']
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                await connection.send_json(update)
```

---

## 3. Dapr Integration Specifications

### 3.1 Dapr Components Configuration

#### 3.1.1 Pub/Sub Component (Kafka)
```yaml
# k8s/dapr-components/pubsub.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
  namespace: default
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "taskflow-kafka-kafka-bootstrap.kafka.svc.cluster.local:9092"
    - name: consumerGroup
      value: "todo-service"
    - name: authType
      value: "none"  # Use "sasl" for Redpanda Cloud
    # For Redpanda Cloud, add:
    # - name: saslUsername
    #   secretKeyRef:
    #     name: kafka-secrets
    #     key: username
    # - name: saslPassword
    #   secretKeyRef:
    #     name: kafka-secrets
    #     key: password
```

#### 3.1.2 State Store Component (PostgreSQL)
```yaml
# k8s/dapr-components/statestore.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
  namespace: default
spec:
  type: state.postgresql
  version: v1
  metadata:
    - name: connectionString
      secretKeyRef:
        name: db-secrets
        key: connection-string
    - name: tableName
      value: "dapr_state"
    - name: metadataTableName
      value: "dapr_metadata"
    - name: keyLength
      value: "200"
```

#### 3.1.3 Secrets Store Component
```yaml
# k8s/dapr-components/secrets.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kubernetes-secrets
  namespace: default
spec:
  type: secretstores.kubernetes
  version: v1
  metadata: []
```

### 3.2 Using Dapr in Backend API

#### 3.2.1 Publish Events via Dapr (Instead of Direct Kafka)
```python
# backend/services/dapr_publisher.py
import httpx
from typing import Dict, Any

class DaprPublisher:
    def __init__(self, dapr_port: int = 3500):
        self.dapr_url = f"http://localhost:{dapr_port}"
    
    async def publish_event(
        self, 
        pubsub_name: str,
        topic: str,
        data: Dict[str, Any]
    ):
        """Publish event via Dapr sidecar"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.dapr_url}/v1.0/publish/{pubsub_name}/{topic}",
                json=data
            )
            response.raise_for_status()
    
    async def publish_task_event(
        self, 
        event_type: str,
        task_data: Dict[str, Any],
        user_id: str
    ):
        """Publish task event"""
        event = {
            "event_id": str(uuid.uuid4()),
            "event_type": event_type,
            "task_id": task_data["id"],
            "task_data": task_data,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.publish_event(
            pubsub_name="kafka-pubsub",
            topic="task-events",
            data=event
        )
```

#### 3.2.2 State Management via Dapr
```python
# backend/services/dapr_state.py
import httpx
from typing import Dict, Any, Optional

class DaprStateManager:
    def __init__(self, dapr_port: int = 3500):
        self.dapr_url = f"http://localhost:{dapr_port}"
    
    async def save_state(
        self, 
        store_name: str,
        key: str,
        value: Any
    ):
        """Save state via Dapr"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.dapr_url}/v1.0/state/{store_name}",
                json=[{
                    "key": key,
                    "value": value
                }]
            )
            response.raise_for_status()
    
    async def get_state(
        self, 
        store_name: str,
        key: str
    ) -> Optional[Any]:
        """Get state via Dapr"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.dapr_url}/v1.0/state/{store_name}/{key}"
            )
            if response.status_code == 200:
                return response.json()
            return None
    
    async def save_conversation_state(
        self,
        conversation_id: str,
        messages: list
    ):
        """Save conversation history"""
        await self.save_state(
            store_name="statestore",
            key=f"conversation-{conversation_id}",
            value={"messages": messages}
        )
```

#### 3.2.3 Service Invocation via Dapr
```python
# backend/services/dapr_client.py
import httpx

class DaprServiceClient:
    def __init__(self, dapr_port: int = 3500):
        self.dapr_url = f"http://localhost:{dapr_port}"
    
    async def invoke_service(
        self,
        app_id: str,
        method: str,
        data: dict = None
    ):
        """Invoke another service via Dapr"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.dapr_url}/v1.0/invoke/{app_id}/method/{method}",
                json=data
            )
            return response.json()

# Usage example
async def notify_user(user_id: str, message: str):
    dapr_client = DaprServiceClient()
    await dapr_client.invoke_service(
        app_id="notification-service",
        method="api/notify",
        data={"user_id": user_id, "message": message}
    )
```

#### 3.2.4 Dapr Jobs API for Scheduled Reminders
```python
# backend/services/dapr_scheduler.py
import httpx
from datetime import datetime

class DaprScheduler:
    def __init__(self, dapr_port: int = 3500):
        self.dapr_url = f"http://localhost:{dapr_port}"
    
    async def schedule_reminder(
        self,
        task_id: int,
        remind_at: datetime,
        user_id: str,
        task_title: str
    ):
        """Schedule reminder using Dapr Jobs API"""
        job_name = f"reminder-task-{task_id}"
        
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{self.dapr_url}/v1.0-alpha1/jobs/{job_name}",
                json={
                    "schedule": remind_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "repeats": 0,  # One-time job
                    "data": {
                        "task_id": task_id,
                        "user_id": user_id,
                        "task_title": task_title,
                        "type": "reminder"
                    }
                }
            )
            response.raise_for_status()

# Backend endpoint to receive job triggers
@app.post("/api/dapr/jobs/trigger")
async def handle_dapr_job_trigger(request: Request):
    """Dapr calls this at scheduled time"""
    job_data = await request.json()
    
    if job_data["data"]["type"] == "reminder":
        # Publish reminder event
        await dapr_publisher.publish_event(
            pubsub_name="kafka-pubsub",
            topic="reminders",
            data=job_data["data"]
        )
    
    return {"status": "SUCCESS"}
```

### 3.3 Dapr Subscriptions (Event Consumers)

#### 3.3.1 Recurring Task Service Subscription
```python
# services/recurring-task-service/main.py
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class CloudEvent(BaseModel):
    data: dict
    datacontenttype: str
    id: str
    pubsubname: str
    source: str
    specversion: str
    topic: str
    traceid: str
    traceparent: str
    tracestate: str
    type: str

@app.post("/dapr/subscribe")
async def subscribe():
    """Tell Dapr what topics to subscribe to"""
    return [
        {
            "pubsubname": "kafka-pubsub",
            "topic": "task-events",
            "route": "/events/task"
        }
    ]

@app.post("/events/task")
async def handle_task_event(event: CloudEvent):
    """Handle task events from Dapr"""
    task_event = event.data
    
    if task_event['event_type'] == 'completed':
        await process_recurring_task(task_event)
    
    return {"status": "SUCCESS"}
```

#### 3.3.2 Dapr Subscription Configuration
```yaml
# k8s/dapr-subscriptions/recurring-task-subscription.yaml
apiVersion: dapr.io/v1alpha1
kind: Subscription
metadata:
  name: recurring-task-subscription
  namespace: default
spec:
  topic: task-events
  route: /events/task
  pubsubname: kafka-pubsub
scopes:
  - recurring-task-service
```

---

## 4. Advanced Features Implementation

### 4.1 Recurring Tasks

#### 4.1.1 Database Schema
```sql
-- Add columns to tasks table
ALTER TABLE tasks ADD COLUMN is_recurring BOOLEAN DEFAULT FALSE;
ALTER TABLE tasks ADD COLUMN recurrence_pattern VARCHAR(20); -- 'daily', 'weekly', 'monthly'
ALTER TABLE tasks ADD COLUMN recurrence_end_date TIMESTAMP WITH TIME ZONE;
ALTER TABLE tasks ADD COLUMN parent_task_id INTEGER REFERENCES tasks(id);
```

#### 4.1.2 MCP Tool for Creating Recurring Tasks
```python
@mcp_tool()
async def create_recurring_task(
    title: str,
    description: str = "",
    recurrence_pattern: str = "daily",  # daily, weekly, monthly
    start_date: str = None,
    end_date: str = None
):
    """
    Create a recurring task
    
    Args:
        title: Task title
        description: Task description
        recurrence_pattern: How often task repeats (daily/weekly/monthly)
        start_date: When to start (ISO format)
        end_date: When to stop recurring (optional)
    """
    start = datetime.fromisoformat(start_date) if start_date else datetime.now()
    
    task = await db.create_task(
        title=title,
        description=description,
        is_recurring=True,
        recurrence_pattern=recurrence_pattern,
        due_at=start,
        recurrence_end_date=datetime.fromisoformat(end_date) if end_date else None
    )
    
    # Publish event
    await dapr_publisher.publish_task_event(
        event_type="created",
        task_data=task.dict(),
        user_id=current_user.id
    )
    
    return {
        "message": f"Created recurring task: {title} ({recurrence_pattern})",
        "task": task
    }
```

### 4.2 Task Priorities

#### 4.2.1 Database Schema
```sql
-- Add priority column
ALTER TABLE tasks ADD COLUMN priority VARCHAR(10) DEFAULT 'medium';
-- Values: 'high', 'medium', 'low'

-- Index for filtering
CREATE INDEX idx_tasks_priority ON tasks(priority);
```

#### 4.2.2 MCP Tool for Setting Priority
```python
@mcp_tool()
async def set_task_priority(task_id: int, priority: str):
    """
    Set task priority
    
    Args:
        task_id: Task ID
        priority: Priority level (high/medium/low)
    """
    if priority not in ['high', 'medium', 'low']:
        return {"error": "Priority must be high, medium, or low"}
    
    task = await db.update_task(task_id, priority=priority)
    
    await dapr_publisher.publish_task_event(
        event_type="updated",
        task_data=task.dict(),
        user_id=current_user.id
    )
    
    return {"message": f"Set priority to {priority}", "task": task}
```

### 4.3 Tags System

#### 4.3.1 Database Schema
```sql
-- Create tags table
CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create task_tags junction table
CREATE TABLE task_tags (
    task_id INTEGER REFERENCES tasks(id) ON DELETE CASCADE,
    tag_id INTEGER REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (task_id, tag_id)
);

-- Indexes
CREATE INDEX idx_tags_user ON tags(user_id);
CREATE INDEX idx_task_tags_task ON task_tags(task_id);
CREATE INDEX idx_task_tags_tag ON task_tags(tag_id);
```

#### 4.3.2 MCP Tools for Tags
```python
@mcp_tool()
async def add_tags_to_task(task_id: int, tags: list[str]):
    """
    Add tags to a task
    
    Args:
        task_id: Task ID
        tags: List of tag names (e.g., ["work", "urgent"])
    """
    for tag_name in tags:
        # Get or create tag
        tag = await db.get_or_create_tag(tag_name, current_user.id)
        await db.add_tag_to_task(task_id, tag.id)
    
    task = await db.get_task(task_id)
    
    await dapr_publisher.publish_task_event(
        event_type="updated",
        task_data=task.dict(),
        user_id=current_user.id
    )
    
    return {"message": f"Added tags: {', '.join(tags)}", "task": task}

@mcp_tool()
async def remove_tag_from_task(task_id: int, tag_name: str):
    """Remove a tag from a task"""
    await db.remove_tag_from_task(task_id, tag_name, current_user.id)
    return {"message": f"Removed tag: {tag_name}"}
```

### 4.4 Search, Filter, and Sort

#### 4.4.1 Advanced Search MCP Tool
```python
@mcp_tool()
async def search_tasks(
    query: str = None,
    status: str = None,
    priority: str = None,
    tags: list[str] = None,
    due_before: str = None,
    due_after: str = None,
    sort_by: str = "created_at",  # created_at, due_at, priority, title
    sort_order: str = "desc"  # asc, desc
):
    """
    Search and filter tasks with advanced options
    
    Args:
        query: Text search in title/description
        status: Filter by status (pending/in_progress/completed)
        priority: Filter by priority (high/medium/low)
        tags: Filter by tags (matches any)
        due_before: Tasks due before this date
        due_after: Tasks due after this date
        sort_by: Field to sort by
        sort_order: Sort direction
    """
    filters = {
        "user_id": current_user.id,
        "query": query,
        "status": status,
        "priority": priority,
        "tags": tags,
        "due_before": datetime.fromisoformat(due_before) if due_before else None,
        "due_after": datetime.fromisoformat(due_after) if due_after else None,
        "sort_by": sort_by,
        "sort_order": sort_order
    }
    
    tasks = await db.search_tasks(**filters)
    
    return {
        "count": len(tasks),
        "tasks": tasks
    }
```

#### 4.4.2 Database Query Implementation
```python
# backend/db/queries.py
async def search_tasks(
    user_id: str,
    query: str = None,
    status: str = None,
    priority: str = None,
    tags: list[str] = None,
    due_before: datetime = None,
    due_after: datetime = None,
    sort_by: str = "created_at",
    sort_order: str = "desc"
):
    """Execute advanced task search"""
    sql_query = """
        SELECT DISTINCT t.* 
        FROM tasks t
        LEFT JOIN task_tags tt ON t.id = tt.task_id
        LEFT JOIN tags tg ON tt.tag_id = tg.id
        WHERE t.user_id = $1
    """
    
    params = [user_id]
    param_count = 1
    
    if query:
        param_count += 1
        sql_query += f" AND (t.title ILIKE ${param_count} OR t.description ILIKE ${param_count})"
        params.append(f"%{query}%")
    
    if status:
        param_count += 1
        sql_query += f" AND t.status = ${param_count}"
        params.append(status)
    
    if priority:
        param_count += 1
        sql_query += f" AND t.priority = ${param_count}"
        params.append(priority)
    
    if tags:
        param_count += 1
        sql_query += f" AND tg.name = ANY(${param_count})"
        params.append(tags)
    
    if due_before:
        param_count += 1
        sql_query += f" AND t.due_at < ${param_count}"
        params.append(due_before)
    
    if due_after:
        param_count += 1
        sql_query += f" AND t.due_at > ${param_count}"
        params.append(due_after)
    
    # Add sorting
    sort_fields = {
        "created_at": "t.created_at",
        "due_at": "t.due_at",
        "priority": "t.priority",
        "title": "t.title"
    }
    
    order = "DESC" if sort_order.lower() == "desc" else "ASC"
    sql_query += f" ORDER BY {sort_fields.get(sort_by, 't.created_at')} {order}"
    
    return await db.fetch_all(sql_query, *params)
```

---

## 5. Kubernetes Deployment Specifications

### 5.1 Minikube Local Deployment

#### 5.1.1 Prerequisites
```bash
# Install required tools
brew install minikube kubectl helm

# Install Dapr CLI
curl -fsSL https://raw.githubusercontent.com/dapr/cli/master/install/install.sh | bash

# Start Minikube with sufficient resources
minikube start --cpus=4 --memory=8192 --disk-size=20g --driver=docker

# Initialize Dapr on Kubernetes
dapr init -k

# Verify Dapr installation
dapr status -k
```

#### 5.1.2 Deploy Kafka (Strimzi)
```bash
# Create kafka namespace
kubectl create namespace kafka

# Install Strimzi operator
kubectl apply -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka

# Deploy Kafka cluster
kubectl apply -f k8s/kafka/kafka-cluster.yaml -n kafka

# Wait for Kafka to be ready
kubectl wait kafka/taskflow-kafka --for=condition=Ready --timeout=300s -n kafka

# Create Kafka topics
kubectl apply -f k8s/kafka/topics.yaml -n kafka
```

**Kafka Topics Configuration:**
```yaml
# k8s/kafka/topics.yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: task-events
  namespace: kafka
  labels:
    strimzi.io/cluster: taskflow-kafka
spec:
  partitions: 3
  replicas: 1
  config:
    retention.ms: 604800000  # 7 days
    segment.bytes: 1073741824
---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: reminders
  namespace: kafka
  labels:
    strimzi.io/cluster: taskflow-kafka
spec:
  partitions: 2
  replicas: 1
  config:
    retention.ms: 604800000
---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: task-updates
  namespace: kafka
  labels:
    strimzi.io/cluster: taskflow-kafka
spec:
  partitions: 2
  replicas: 1
  config:
    retention.ms: 86400000  # 1 day
```

#### 5.1.3 Deploy Dapr Components
```bash
# Apply all Dapr components
kubectl apply -f k8s/dapr-components/
```

#### 5.1.4 Deploy Application Services
```yaml
# k8s/deployments/backend.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: default
  labels:
    app: backend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "backend-service"
        dapr.io/app-port: "8000"
        dapr.io/log-level: "info"
        dapr.io/enable-metrics: "true"
        dapr.io/metrics-port: "9090"
    spec:
      containers:
      - name: backend
        image: your-registry/taskflow-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secrets
              key: connection-string
        - name: KAFKA_BOOTSTRAP_SERVERS
          value: "taskflow-kafka-kafka-bootstrap.kafka.svc.cluster.local:9092"
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: openai-api-key
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: backend-service
  namespace: default
spec:
  selector:
    app: backend
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
```

**Frontend Deployment:**
```yaml
# k8s/deployments/frontend.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: default
spec:
  replicas: 2
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "frontend-service"
        dapr.io/app-port: "3000"
    spec:
      containers:
      - name: frontend
        image: your-registry/taskflow-frontend:latest
        ports:
        - containerPort: 3000
        env:
        - name: NEXT_PUBLIC_API_URL
          value: "http://backend-service:8000"
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
---
apiVersion: v1
kind: Service
metadata:
  name: frontend-service
spec:
  selector:
    app: frontend
  ports:
  - port: 80
    targetPort: 3000
  type: LoadBalancer
```

**Consumer Services Deployments:**
```yaml
# k8s/deployments/recurring-task-service.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: recurring-task-service
  namespace: default
spec:
  replicas: 1
  selector:
    matchLabels:
      app: recurring-task-service
  template:
    metadata:
      labels:
        app: recurring-task-service
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "recurring-task-service"
        dapr.io/app-port: "8001"
    spec:
      containers:
      - name: recurring-task-service
        image: your-registry/recurring-task-service:latest
        ports:
        - containerPort: 8001
        env:
        - name: KAFKA_BOOTSTRAP_SERVERS
          value: "taskflow-kafka-kafka-bootstrap.kafka.svc.cluster.local:9092"
        - name: BACKEND_SERVICE_URL
          value: "http://backend-service:8000"
```

#### 5.1.5 Deploy All Services
```bash
# Create secrets
kubectl create secret generic db-secrets \
  --from-literal=connection-string="postgresql://user:pass@neon.tech/db"

kubectl create secret generic api-secrets \
  --from-literal=openai-api-key="sk-..."

# Apply all deployments
kubectl apply -f k8s/deployments/

# Check status
kubectl get pods
kubectl get services

# Access frontend
minikube service frontend-service --url
```

### 5.2 Cloud Deployment (AKS/GKE/OKE)

#### 5.2.1 Azure Kubernetes Service (AKS) Setup

**Create AKS Cluster:**
```bash
# Login to Azure
az login

# Create resource group
az group create --name taskflow-rg --location eastus

# Create AKS cluster
az aks create \
  --resource-group taskflow-rg \
  --name taskflow-aks \
  --node-count 3 \
  --node-vm-size Standard_B2s \
  --enable-addons monitoring \
  --generate-ssh-keys

# Get credentials
az aks get-credentials --resource-group taskflow-rg --name taskflow-aks

# Verify connection
kubectl get nodes
```

**Install Dapr on AKS:**
```bash
dapr init -k
```

#### 5.2.2 Google Kubernetes Engine (GKE) Setup

**Create GKE Cluster:**
```bash
# Set project
gcloud config set project YOUR_PROJECT_ID

# Create cluster
gcloud container clusters create taskflow-gke \
  --zone us-central1-a \
  --num-nodes 3 \
  --machine-type e2-medium \
  --enable-autoscaling \
  --min-nodes 1 \
  --max-nodes 5

# Get credentials
gcloud container clusters get-credentials taskflow-gke --zone us-central1-a

# Install Dapr
dapr init -k
```

#### 5.2.3 Oracle Cloud (OKE) Setup - Recommended for Always Free Tier

**Create OKE Cluster:**
```bash
# Using OCI Console:
# 1. Navigate to Developer Services > Kubernetes Clusters (OKE)
# 2. Click "Create Cluster"
# 3. Choose "Quick Create"
# 4. Select:
#    - Kubernetes Version: Latest
#    - Node Shape: VM.Standard.E2.1.Micro (Always Free)
#    - Number of Nodes: 2
# 5. Click "Create Cluster"

# Configure kubectl
oci ce cluster create-kubeconfig \
  --cluster-id <cluster-ocid> \
  --file $HOME/.kube/config \
  --region us-ashburn-1

# Verify
kubectl get nodes

# Install Dapr
dapr init -k
```

#### 5.2.4 Deploy to Cloud Kubernetes

**Push Docker Images:**
```bash
# Build images
docker build -t your-registry/taskflow-backend:latest ./backend
docker build -t your-registry/taskflow-frontend:latest ./frontend
docker build -t your-registry/recurring-task-service:latest ./services/recurring-task-service
docker build -t your-registry/notification-service:latest ./services/notification-service
docker build -t your-registry/audit-service:latest ./services/audit-service

# Push to registry
docker push your-registry/taskflow-backend:latest
docker push your-registry/taskflow-frontend:latest
docker push your-registry/recurring-task-service:latest
docker push your-registry/notification-service:latest
docker push your-registry/audit-service:latest
```

**Deploy Application:**
```bash
# Create namespace
kubectl create namespace taskflow

# Create secrets
kubectl create secret generic db-secrets \
  --from-literal=connection-string="$DATABASE_URL" \
  -n taskflow

kubectl create secret generic api-secrets \
  --from-literal=openai-api-key="$OPENAI_API_KEY" \
  -n taskflow

# Deploy Kafka (or use Redpanda Cloud)
kubectl apply -f k8s/kafka/ -n taskflow

# Deploy Dapr components
kubectl apply -f k8s/dapr-components/ -n taskflow

# Deploy application
kubectl apply -f k8s/deployments/ -n taskflow

# Check status
kubectl get pods -n taskflow
kubectl get services -n taskflow
```

#### 5.2.5 Ingress Configuration
```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: taskflow-ingress
  namespace: taskflow
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - taskflow.yourdomain.com
    secretName: taskflow-tls
  rules:
  - host: taskflow.yourdomain.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: backend-service
            port:
              number: 8000
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 80
```

---

## 6. CI/CD Pipeline Specifications

### 6.1 GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml
name: Build and Deploy to Kubernetes

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    
    strategy:
      matrix:
        service:
          - name: backend
            path: ./backend
          - name: frontend
            path: ./frontend
          - name: recurring-task-service
            path: ./services/recurring-task-service
          - name: notification-service
            path: ./services/notification-service
          - name: audit-service
            path: ./services/audit-service
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v3
    
    - name: Log in to Container Registry
      uses: docker/login-action@v2
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v4
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-${{ matrix.service.name }}
        tags: |
          type=ref,event=branch
          type=sha,prefix={{branch}}-
          type=raw,value=latest,enable={{is_default_branch}}
    
    - name: Build and push Docker image
      uses: docker/build-push-action@v4
      with:
        context: ${{ matrix.service.path }}
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
  
  deploy-to-k8s:
    needs: build-and-push
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v3
    
    - name: Set up kubectl
      uses: azure/setup-kubectl@v3
    
    - name: Configure kubectl
      run: |
        echo "${{ secrets.KUBECONFIG }}" > kubeconfig.yaml
        export KUBECONFIG=kubeconfig.yaml
    
    - name: Update image tags
      run: |
        cd k8s/deployments
        kustomize edit set image \
          backend=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-backend:${{ github.sha }} \
          frontend=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-frontend:${{ github.sha }}
    
    - name: Deploy to Kubernetes
      run: |
        export KUBECONFIG=kubeconfig.yaml
        kubectl apply -f k8s/deployments/ -n taskflow
        kubectl rollout status deployment/backend -n taskflow
        kubectl rollout status deployment/frontend -n taskflow
    
    - name: Verify deployment
      run: |
        export KUBECONFIG=kubeconfig.yaml
        kubectl get pods -n taskflow
        kubectl get services -n taskflow
```

### 6.2 Helm Charts (Alternative to Raw YAML)

```yaml
# helm/taskflow/Chart.yaml
apiVersion: v2
name: taskflow
description: A Todo application with chatbot and event-driven architecture
type: application
version: 1.0.0
appVersion: "1.0.0"
```

```yaml
# helm/taskflow/values.yaml
replicaCount: 2

backend:
  image:
    repository: ghcr.io/yourorg/taskflow-backend
    tag: latest
  service:
    port: 8000

frontend:
  image:
    repository: ghcr.io/yourorg/taskflow-frontend
    tag: latest
  service:
    port: 3000

kafka:
  enabled: true
  bootstrapServers: "taskflow-kafka-kafka-bootstrap.kafka.svc.cluster.local:9092"

dapr:
  enabled: true
  
secrets:
  databaseUrl: ""  # Set via --set or values override
  openaiApiKey: ""

ingress:
  enabled: true
  className: nginx
  host: taskflow.yourdomain.com
```

**Deploy with Helm:**
```bash
# Install
helm install taskflow ./helm/taskflow \
  --namespace taskflow \
  --create-namespace \
  --set secrets.databaseUrl="$DATABASE_URL" \
  --set secrets.openaiApiKey="$OPENAI_API_KEY"

# Upgrade
helm upgrade taskflow ./helm/taskflow \
  --namespace taskflow \
  --set backend.image.tag=v1.1.0
```

---

## 7. Monitoring and Logging Specifications

### 7.1 Prometheus and Grafana Setup

```bash
# Add Prometheus Helm repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Prometheus
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace

# Access Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80

# Default credentials: admin/prom-operator
```

### 7.2 Application Metrics (Dapr)

Dapr automatically exposes metrics on port 9090. Configure Prometheus to scrape:

```yaml
# k8s/monitoring/servicemonitor.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: dapr-metrics
  namespace: taskflow
spec:
  selector:
    matchLabels:
      dapr.io/enabled: "true"
  endpoints:
  - port: metrics
    interval: 30s
```

### 7.3 Logging with EFK Stack

```bash
# Install Elasticsearch
helm repo add elastic https://helm.elastic.co
helm install elasticsearch elastic/elasticsearch \
  --namespace logging \
  --create-namespace

# Install Fluentd
helm install fluentd stable/fluentd-elasticsearch \
  --namespace logging

# Install Kibana
helm install kibana elastic/kibana \
  --namespace logging

# Access Kibana
kubectl port-forward -n logging svc/kibana-kibana 5601:5601
```

### 7.4 Custom Metrics in Application

```python
# backend/monitoring.py
from prometheus_client import Counter, Histogram, generate_latest

# Metrics
task_created_counter = Counter('tasks_created_total', 'Total tasks created')
task_completed_counter = Counter('tasks_completed_total', 'Total tasks completed')
event_processing_time = Histogram('event_processing_seconds', 'Event processing time')

# In your code
@event_processing_time.time()
async def process_event(event):
    # Process event
    pass

# Expose metrics endpoint
@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

---

## 8. Testing Strategy

### 8.1 Unit Tests
```bash
# Backend
cd backend
pytest tests/unit/

# Services
cd services/recurring-task-service
pytest tests/
```

### 8.2 Integration Tests
```python
# tests/integration/test_kafka_flow.py
import pytest
from kafka import KafkaProducer, KafkaConsumer

@pytest.mark.asyncio
async def test_task_event_flow():
    """Test event flows through Kafka"""
    # Publish event
    producer.send('task-events', value={'event_type': 'created'})
    
    # Consume event
    consumer = KafkaConsumer('task-events')
    message = next(consumer)
    
    assert message.value['event_type'] == 'created'
```

### 8.3 End-to-End Tests
```python
# tests/e2e/test_user_flow.py
from playwright.async_api import async_playwright

@pytest.mark.asyncio
async def test_create_task_via_chatbot():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        await page.goto('http://localhost:3000')
        await page.fill('[data-testid="chat-input"]', 'Create a task: Buy groceries')
        await page.click('[data-testid="send-button"]')
        
        # Wait for response
        await page.wait_for_selector('[data-testid="task-created"]')
        
        await browser.close()
```

---

## 9. Deployment Checklist

### 9.1 Pre-Deployment
- [ ] All unit tests passing
- [ ] Integration tests passing
- [ ] Environment variables configured
- [ ] Secrets created in Kubernetes
- [ ] Database migrations applied
- [ ] Docker images built and pushed

### 9.2 Minikube Deployment
- [ ] Minikube started with sufficient resources
- [ ] Dapr initialized on Kubernetes
- [ ] Kafka deployed (Strimzi)
- [ ] Kafka topics created
- [ ] Dapr components configured
- [ ] All services deployed
- [ ] Health checks passing
- [ ] Test via Minikube tunnel

### 9.3 Cloud Deployment
- [ ] Kubernetes cluster created (AKS/GKE/OKE)
- [ ] kubectl configured
- [ ] Dapr installed on cloud cluster
- [ ] Kafka service configured (Redpanda/Strimzi)
- [ ] Secrets migrated to cloud
- [ ] CI/CD pipeline configured
- [ ] Ingress controller installed
- [ ] TLS certificates configured
- [ ] Domain DNS updated
- [ ] Monitoring dashboards set up
- [ ] Logging pipeline configured
- [ ] Load testing performed

### 9.4 Post-Deployment Verification
- [ ] All pods running
- [ ] Services accessible
- [ ] Kafka consumers processing events
- [ ] Dapr sidecars healthy
- [ ] Create task via chatbot works
- [ ] Reminders being sent
- [ ] Recurring tasks spawning
- [ ] Real-time updates working
- [ ] Monitoring showing metrics
- [ ] Logs being collected

---

## 10. Documentation Requirements

### 10.1 README.md Structure
```markdown
# TaskFlow - Event-Driven Todo Application

## Overview
Brief description of the application

## Architecture
- System architecture diagram
- Event-driven flow explanation
- Technology stack

## Features
- ✅ Natural language task management
- ✅ Email reminders
- ✅ Recurring tasks
- ✅ Priority and tags
- ✅ Advanced search and filtering
- ✅ Real-time synchronization
- ✅ Event-driven architecture with Kafka
- ✅ Dapr integration

## Local Development
### Prerequisites
### Setup Instructions
### Running Locally

## Deployment
### Minikube Deployment
### Cloud Deployment (AKS/GKE/OKE)

## API Documentation

## Contributing

## License
```

### 10.2 CLAUDE.md Instructions
```markdown
# Claude Code Instructions for TaskFlow Phase V

## Project Context
This is Phase V of TaskFlow - implementing cloud deployment with Kafka and Dapr.

## Development Workflow
1. Read this specification: `/specs/phase-v-spec.md`
2. Follow Agentic Dev Stack: Spec → Plan → Tasks → Implementation
3. Use Claude Code for all implementations

## Key Technologies
- FastAPI (Backend)
- Next.js (Frontend)
- Kafka (Event Streaming)
- Dapr (Distributed Runtime)
- Kubernetes (Orchestration)
- Neon (PostgreSQL)

## Code Style
- Python: Follow PEP 8, use async/await
- TypeScript: Use strict mode
- Comments: Explain "why", not "what"

## Testing
- Write tests alongside implementation
- All new features must have tests
- Run `pytest` before committing

## Deployment
- Test on Minikube first
- Deploy to cloud only after local verification
- Use Helm for repeatable deployments
```

---

## 11. Submission Package

### 11.1 GitHub Repository Structure
```
taskflow/
├── backend/
│   ├── mcp/
│   │   └── tools/
│   ├── services/
│   │   ├── kafka_producer.py
│   │   ├── dapr_publisher.py
│   │   └── dapr_state.py
│   ├── db/
│   ├── tests/
│   └── Dockerfile
├── frontend/
│   ├── src/
│   ├── public/
│   └── Dockerfile
├── services/
│   ├── recurring-task-service/
│   ├── notification-service/
│   ├── audit-service/
│   └── websocket-service/
├── k8s/
│   ├── kafka/
│   ├── dapr-components/
│   ├── deployments/
│   ├── services/
│   └── ingress.yaml
├── helm/
│   └── taskflow/
├── .github/
│   └── workflows/
│       └── deploy.yml
├── specs/
│   └── phase-v-spec.md
├── README.md
├── CLAUDE.md
└── docker-compose.yml
```

### 11.2 Demo Video Script (90 seconds)
```
[0-15s] Introduction
- "Hi, I'm [Name], presenting TaskFlow Phase V"
- "Event-driven todo app with Kafka and Dapr on Kubernetes"

[15-30s] Architecture Overview
- Show architecture diagram
- "Backend publishes events to Kafka"
- "Specialized services consume and process events"
- "All wrapped with Dapr for portability"

[30-50s] Feature Demo
- Create recurring task via chatbot
- Show task in UI
- Complete task
- Show next occurrence auto-created
- Demonstrate real-time sync across clients

[50-70s] Deployment Demo
- Show Kubernetes pods running
- kubectl get pods
- Show Kafka topics
- Show Dapr components
- Access live application URL

[70-90s] Code Quality
- Show spec file
- Show Claude Code usage
- GitHub repository structure
- "All code generated from specs using Claude Code"
```

---

## 12. Success Criteria

### 12.1 Functional Requirements
- [ ] All CRUD operations via chatbot working
- [ ] Recurring tasks auto-creating next occurrence
- [ ] Email reminders being sent
- [ ] Priority and tags functioning
- [ ] Search and filters working
- [ ] Real-time updates across clients

### 12.2 Technical Requirements
- [ ] Kafka topics created and accessible
- [ ] Events published to Kafka for all task operations
- [ ] Consumer services processing events
- [ ] Dapr sidecars running for all pods
- [ ] Application deployed on Minikube
- [ ] Application deployed on cloud (AKS/GKE/OKE)
- [ ] CI/CD pipeline functional

### 12.3 Documentation Requirements
- [ ] README.md with complete setup instructions
- [ ] CLAUDE.md with Claude Code instructions
- [ ] Architecture diagrams included
- [ ] API documentation available
- [ ] Demo video under 90 seconds

---

## 13. Timeline Estimate

| Task | Estimated Time |
|------|----------------|
| Advanced features implementation | 2-3 days |
| Kafka integration | 1-2 days |
| Consumer services development | 2-3 days |
| Dapr integration | 1-2 days |
| Minikube deployment setup | 1 day |
| Cloud deployment setup | 1-2 days |
| CI/CD pipeline | 1 day |
| Testing and bug fixes | 2-3 days |
| Documentation | 1 day |
| Demo video | 0.5 day |
| **Total** | **12-18 days** |

---

## 14. Support Resources

### 14.1 Documentation Links
- Dapr: https://docs.dapr.io/
- Strimzi: https://strimzi.io/docs/
- Kafka: https://kafka.apache.org/documentation/
- Kubernetes: https://kubernetes.io/docs/
- MCP: https://modelcontextprotocol.io/

### 14.2 Troubleshooting

**Common Issues:**

1. **Kafka connection refused**
   - Check if Kafka pods are running
   - Verify bootstrap servers URL
   - Check network policies

2. **Dapr sidecar not injecting**
   - Verify Dapr annotations in deployment
   - Check Dapr installation: `dapr status -k`
   - Ensure namespace has Dapr enabled

3. **Consumer not receiving messages**
   - Check consumer group ID
   - Verify topic exists
   - Check Kafka logs

4. **Minikube out of resources**
   - Increase memory: `minikube start --memory=8192`
   - Delete unused pods
   - Clean up Docker images

---

## 15. Next Steps After Phase V

### 15.1 Potential Enhancements
- Add GraphQL API
- Implement caching with Redis
- Add analytics dashboard
- Mobile app development
- Multi-tenancy support
- Advanced ML features (task suggestions)

### 15.2 Scaling Considerations
- Horizontal pod autoscaling
- Database read replicas
- CDN for static assets
- Rate limiting
- Advanced monitoring with APM tools

---

## Appendix A: Environment Variables

```bash
# Backend
DATABASE_URL=postgresql://user:pass@neon.tech/taskflow
OPENAI_API_KEY=sk-...
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
DAPR_HTTP_PORT=3500
DAPR_GRPC_PORT=50001

# Frontend
NEXT_PUBLIC_API_URL=http://backend-service:8000
NEXT_PUBLIC_WS_URL=ws://websocket-service:8080

# Services
BACKEND_SERVICE_URL=http://backend-service:8000
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_FROM=noreply@taskflow.com
```

---

## Appendix B: Useful Commands

```bash
# Kubectl
kubectl get pods -n taskflow
kubectl logs -f pod-name -c container-name -n taskflow
kubectl describe pod pod-name -n taskflow
kubectl exec -it pod-name -c container-name -n taskflow -- /bin/bash

# Dapr
dapr status -k
dapr logs --app-id backend-service -k
dapr dashboard -k

# Kafka (Strimzi)
kubectl exec -it taskflow-kafka-0 -n kafka -- bin/kafka-topics.sh --list --bootstrap-server localhost:9092
kubectl exec -it taskflow-kafka-0 -n kafka -- bin/kafka-console-consumer.sh --topic task-events --from-beginning --bootstrap-server localhost:9092

# Minikube
minikube service list
minikube tunnel
minikube logs

# Helm
helm list -n taskflow
helm status taskflow -n taskflow
helm rollback taskflow -n taskflow
```

---

**End of Specification**

This specification document provides a comprehensive guide for implementing Phase V of the TaskFlow project. Follow this document systematically with Claude Code to ensure successful deployment of the event-driven architecture on Kubernetes.