# Dapr Integration Skill

## Purpose
Integrate Dapr (Distributed Application Runtime) for event-driven architecture in Phase V.

## Dapr Building Blocks Used
1. **Pub/Sub** - Kafka event streaming
2. **State Management** - Conversation storage
3. **Service Invocation** - Frontend ↔ Backend communication
4. **Bindings** - Scheduled triggers (reminders)
5. **Secrets** - Secure credential management

## Quick Setup

### Install Dapr CLI
```bash
# Install Dapr
curl -fsSL https://raw.githubusercontent.com/dapr/cli/master/install/install.sh | bash

# Initialize on Kubernetes
dapr init -k

# Verify installation
dapr status -k
```

## Pattern 1: Pub/Sub (Kafka Events)

### Component Definition
```yaml
# dapr-components/kafka-pubsub.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "kafka:9092"  # Or Redpanda Cloud URL
    - name: consumerGroup
      value: "todo-service"
    - name: authType
      value: "password"  # For cloud Kafka
    - name: saslUsername
      secretKeyRef:
        name: kafka-secrets
        key: username
    - name: saslPassword
      secretKeyRef:
        name: kafka-secrets
        key: password
```

### Publish Events (FastAPI)
```python
# Instead of direct Kafka client
import httpx

async def publish_task_event(event_type: str, task_data: dict):
    """Publish event via Dapr sidecar"""
    async with httpx.AsyncClient() as client:
        await client.post(
            "http://localhost:3500/v1.0/publish/kafka-pubsub/task-events",
            json={
                "event_type": event_type,
                "task_id": task_data["id"],
                "task_data": task_data,
                "user_id": task_data["user_id"],
                "timestamp": datetime.utcnow().isoformat()
            }
        )

# Usage in endpoint
@router.post("/api/{user_id}/tasks")
async def create_task(task_data: TaskCreate, current_user: User = Depends(get_current_user)):
    task = Task(**task_data.dict(), user_id=current_user.id)
    session.add(task)
    session.commit()

    # Publish event
    await publish_task_event("created", task.dict())

    return task
```

### Subscribe to Events
```python
# notification_service.py
from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/dapr/subscribe")
def subscribe():
    """Tell Dapr which topics to subscribe to"""
    return [
        {
            "pubsubname": "kafka-pubsub",
            "topic": "task-events",
            "route": "/task-events"
        },
        {
            "pubsubname": "kafka-pubsub",
            "topic": "reminders",
            "route": "/reminders"
        }
    ]

@app.post("/task-events")
async def handle_task_event(request: Request):
    """Handle task events"""
    event = await request.json()

    if event["data"]["event_type"] == "created":
        # Send notification
        print(f"Task created: {event['data']['task_data']['title']}")

    return {"status": "SUCCESS"}
```

## Pattern 2: State Management

### Component Definition
```yaml
# dapr-components/statestore.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
spec:
  type: state.postgresql
  version: v1
  metadata:
    - name: connectionString
      secretKeyRef:
        name: db-secrets
        key: connection-string
```

### Save/Retrieve State
```python
import httpx

async def save_conversation_state(conversation_id: int, messages: list):
    """Save conversation via Dapr State API"""
    async with httpx.AsyncClient() as client:
        await client.post(
            "http://localhost:3500/v1.0/state/statestore",
            json=[{
                "key": f"conversation-{conversation_id}",
                "value": {"messages": messages}
            }]
        )

async def get_conversation_state(conversation_id: int):
    """Retrieve conversation via Dapr State API"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://localhost:3500/v1.0/state/statestore/conversation-{conversation_id}"
        )
        return response.json()
```

## Pattern 3: Dapr Jobs API (Reminders)

### Schedule Reminder
```python
import httpx
from datetime import datetime

async def schedule_reminder(task_id: int, remind_at: datetime, user_id: str):
    """Schedule reminder using Dapr Jobs API"""
    async with httpx.AsyncClient() as client:
        await client.post(
            f"http://localhost:3500/v1.0-alpha1/jobs/reminder-task-{task_id}",
            json={
                "dueTime": remind_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "data": {
                    "task_id": task_id,
                    "user_id": user_id,
                    "type": "reminder"
                }
            }
        )

# Handle callback when job fires
@app.post("/api/jobs/trigger")
async def handle_job_trigger(request: Request):
    """Dapr calls this at scheduled time"""
    job_data = await request.json()

    if job_data["data"]["type"] == "reminder":
        # Publish to notification service
        await publish_task_event("reminder.due", job_data["data"])

    return {"status": "SUCCESS"}
```

## Pattern 4: Service Invocation

### Frontend → Backend (via Dapr)
```typescript
// Instead of direct fetch
async function callBackend(endpoint: string, data: any) {
  // Dapr provides service discovery and retries
  const response = await fetch(
    `http://localhost:3500/v1.0/invoke/backend-service/method${endpoint}`,
    {
      method: 'POST',
      body: JSON.stringify(data),
      headers: {
        'Content-Type': 'application/json'
      }
    }
  );
  return response.json();
}
```

## Pattern 5: Secrets Management

### Component Definition
```yaml
# dapr-components/kubernetes-secrets.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kubernetes-secrets
spec:
  type: secretstores.kubernetes
  version: v1
```

### Access Secrets
```python
import httpx

async def get_secret(secret_name: str, key: str):
    """Retrieve secret via Dapr"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://localhost:3500/v1.0/secrets/kubernetes-secrets/{secret_name}"
        )
        secrets = response.json()
        return secrets.get(key)

# Usage
openai_key = await get_secret("app-secrets", "openai-api-key")
```

## Deployment with Dapr Annotations

### Add to Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  template:
    metadata:
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "backend-service"
        dapr.io/app-port: "8000"
        dapr.io/enable-api-logging: "true"
    spec:
      containers:
      - name: backend
        image: todo-backend:latest
        ports:
        - containerPort: 8000
```

## Benefits
- **No Kafka Libraries**: Use HTTP instead of kafka-python
- **Portability**: Swap Kafka for RabbitMQ by changing YAML
- **Service Discovery**: No hardcoded URLs
- **Retries & Circuit Breakers**: Built-in resilience
- **Secrets Management**: Unified API across providers

## Checklist
- [ ] Dapr installed on Kubernetes
- [ ] PubSub component for Kafka
- [ ] State component for PostgreSQL
- [ ] Secrets component configured
- [ ] Dapr annotations on deployments
- [ ] Application uses Dapr HTTP APIs
- [ ] Components tested locally

## Usage in Phase V
Core integration for event-driven architecture with Kafka and cloud deployment.
