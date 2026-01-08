# WebSocket Sync Service

Real-time task synchronization service that broadcasts task updates to connected WebSocket clients.

## Purpose

Consumes `task-updates` events from Kafka and broadcasts them to WebSocket clients for real-time synchronization across multiple browser tabs or devices.

## Architecture

```
Kafka (task-updates topic)
         ↓
    Dapr Pub/Sub
         ↓
WebSocket Sync Service
         ↓
    WebSocket Server
         ↓
  Connected Clients
 (browsers, mobile apps)
```

## Features

- **Real-Time Sync**: Instant task updates across all user's devices
- **JWT Authentication**: Secure WebSocket connections
- **Multi-Device Support**: User can have multiple connections (tabs/devices)
- **Automatic Reconnection**: Client-side reconnection handling
- **Keep-Alive**: Ping/pong mechanism for connection health
- **Broadcasting**: Efficient message delivery to multiple connections

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DAPR_HTTP_URL` | `http://localhost:3500` | Dapr sidecar HTTP endpoint |
| `DAPR_PUBSUB` | `kafka-pubsub` | Dapr Pub/Sub component name |
| `DAPR_TOPIC` | `task-updates` | Kafka topic to subscribe |
| `JWT_SECRET_KEY` | - | Secret key for JWT validation (must match auth service) |

## WebSocket Protocol

### Connection

```javascript
// Client-side JavaScript example
const token = localStorage.getItem('jwt_token');
const ws = new WebSocket(`ws://localhost:8000/ws?token=${token}`);

ws.onopen = () => {
    console.log('WebSocket connected');
};

ws.onmessage = (event) => {
    const message = JSON.parse(event.data);
    handleTaskUpdate(message);
};

ws.onerror = (error) => {
    console.error('WebSocket error:', error);
};

ws.onclose = () => {
    console.log('WebSocket disconnected');
    // Implement reconnection logic
    setTimeout(reconnect, 3000);
};
```

### Message Types

#### Server → Client: Welcome Message

```json
{
  "type": "connected",
  "user_id": 1,
  "message": "WebSocket connection established"
}
```

#### Server → Client: Task Update

```json
{
  "type": "task_update",
  "operation": "create",
  "task_id": 123,
  "task": {
    "title": "Buy milk",
    "status": "pending",
    "updated_at": "2026-01-03T10:00:00Z"
  },
  "timestamp": "2026-01-03T10:00:00Z"
}
```

#### Client → Server: Ping (Keep-Alive)

```json
{
  "type": "ping"
}
```

#### Server → Client: Pong

```json
{
  "type": "pong"
}
```

## Local Development

### Run with Dapr

```bash
# Install dependencies
pip install -r requirements.txt

# Run with Dapr sidecar
dapr run \
  --app-id websocket-sync-service \
  --app-port 8000 \
  --dapr-http-port 3500 \
  --components-path ../../dapr-components/local \
  -- uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Run standalone (for testing)

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Docker Build

```bash
docker build -t websocket-sync-service:latest .
```

## Kubernetes Deployment

```bash
# Apply Dapr components
kubectl apply -f ../../dapr-components/local/

# Deploy service
kubectl apply -f k8s/deployment.yaml
```

## Testing

### Test WebSocket Connection

```bash
# Install websocat (WebSocket CLI client)
# macOS: brew install websocat
# Linux: cargo install websocat

# Connect to WebSocket
websocat "ws://localhost:8000/ws?token=YOUR_JWT_TOKEN"
```

### Publish Test Event

```bash
# Publish task-updates event via Dapr
curl -X POST http://localhost:3500/v1.0/publish/kafka-pubsub/task-updates \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "test-999",
    "schema_version": "1.0",
    "event_type": "task.sync",
    "timestamp": "2026-01-03T10:00:00Z",
    "user_id": 1,
    "operation": "create",
    "task_id": 123,
    "task_snapshot": {
      "title": "Buy milk",
      "status": "pending",
      "updated_at": "2026-01-03T10:00:00Z"
    }
  }'
```

### Check Connection Stats

```bash
# Get connection statistics
curl http://localhost:8000/stats
```

## Frontend Integration

### React Example

```jsx
import { useEffect, useState } from 'react';

function useWebSocket(token) {
  const [socket, setSocket] = useState(null);
  const [tasks, setTasks] = useState([]);

  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8000/ws?token=${token}`);

    ws.onopen = () => {
      console.log('WebSocket connected');
    };

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);

      if (message.type === 'task_update') {
        setTasks(prevTasks => {
          // Update task list based on operation
          if (message.operation === 'create') {
            return [...prevTasks, message.task];
          } else if (message.operation === 'update') {
            return prevTasks.map(task =>
              task.id === message.task_id ? message.task : task
            );
          } else if (message.operation === 'delete') {
            return prevTasks.filter(task => task.id !== message.task_id);
          }
          return prevTasks;
        });
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      // Reconnect after 3 seconds
      setTimeout(() => window.location.reload(), 3000);
    };

    setSocket(ws);

    // Cleanup on unmount
    return () => {
      ws.close();
    };
  }, [token]);

  return { socket, tasks };
}

// Usage in component
function TaskList() {
  const token = localStorage.getItem('jwt_token');
  const { tasks } = useWebSocket(token);

  return (
    <div>
      <h1>My Tasks (Real-Time)</h1>
      {tasks.map(task => (
        <div key={task.id}>{task.title}</div>
      ))}
    </div>
  );
}
```

### Vue.js Example

```vue
<template>
  <div>
    <h1>My Tasks (Real-Time)</h1>
    <div v-for="task in tasks" :key="task.id">
      {{ task.title }}
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      socket: null,
      tasks: []
    };
  },
  mounted() {
    const token = localStorage.getItem('jwt_token');
    this.socket = new WebSocket(`ws://localhost:8000/ws?token=${token}`);

    this.socket.onmessage = (event) => {
      const message = JSON.parse(event.data);

      if (message.type === 'task_update') {
        if (message.operation === 'create') {
          this.tasks.push(message.task);
        } else if (message.operation === 'update') {
          const index = this.tasks.findIndex(t => t.id === message.task_id);
          if (index !== -1) {
            this.tasks.splice(index, 1, message.task);
          }
        } else if (message.operation === 'delete') {
          this.tasks = this.tasks.filter(t => t.id !== message.task_id);
        }
      }
    };
  },
  beforeUnmount() {
    if (this.socket) {
      this.socket.close();
    }
  }
};
</script>
```

## Monitoring

### Metrics

- `websocket_connections_total`: Total active connections
- `websocket_connections_by_user`: Connections per user
- `websocket_messages_sent_total`: Total messages sent
- `websocket_disconnections_total`: Total disconnections

### Alerts

- **High connection count**: > 10,000 connections per service instance
- **Frequent reconnections**: Disconnect rate > 10% for > 5 minutes
- **Message delivery failures**: Send failure rate > 1%

## Troubleshooting

### WebSocket connection fails

1. Check JWT token validity:
   ```bash
   # Decode JWT token
   echo "YOUR_TOKEN" | base64 -d
   ```

2. Verify CORS configuration:
   ```python
   # In main.py, add CORS middleware if needed
   from fastapi.middleware.cors import CORSMiddleware
   ```

3. Check Dapr sidecar:
   ```bash
   curl http://localhost:3500/v1.0/healthz
   ```

### No updates received

1. Verify Kafka events are being published:
   ```bash
   kubectl exec kafka-cluster-kafka-0 -- \
     /opt/kafka/bin/kafka-console-consumer.sh \
     --bootstrap-server localhost:9092 \
     --topic task-updates \
     --from-beginning
   ```

2. Check service logs:
   ```bash
   kubectl logs -l app=websocket-sync-service -f
   ```

3. Verify user_id matches:
   - Token user_id must match event user_id

### Connection drops frequently

1. Implement exponential backoff for reconnection
2. Add ping/pong keep-alive mechanism
3. Check network stability
4. Increase Kubernetes resource limits

## Scaling

### Horizontal Scaling

WebSocket service can scale horizontally with sticky sessions:

```yaml
# Kubernetes Service with session affinity
apiVersion: v1
kind: Service
metadata:
  name: websocket-sync-service
spec:
  sessionAffinity: ClientIP
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 10800  # 3 hours
```

### Load Balancing

Use sticky sessions (session affinity) to ensure user's connections go to same pod.

Alternatively, use Redis Pub/Sub for inter-pod communication:
1. User connects to Pod A
2. Pod B receives Kafka event
3. Pod B publishes to Redis
4. Pod A receives from Redis and sends to user

## Future Enhancements

- [ ] Redis Pub/Sub for multi-pod synchronization
- [ ] Presence detection (online/offline users)
- [ ] Typing indicators
- [ ] Read receipts
- [ ] Message history replay on reconnection
- [ ] WebSocket compression
- [ ] Binary protocol (Protocol Buffers)
