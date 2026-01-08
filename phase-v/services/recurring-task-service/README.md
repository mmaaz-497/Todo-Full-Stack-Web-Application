# Recurring Task Service

Event-driven microservice that generates next occurrences for recurring tasks.

## Purpose

Consumes `task.completed` events from Kafka and automatically creates the next occurrence for recurring tasks based on their recurrence rules (daily, weekly, monthly).

## Architecture

```
Kafka (task-events topic)
         ↓
    Dapr Pub/Sub
         ↓
Recurring Task Service
    ↓           ↓
Dapr State  Dapr Pub/Sub
    ↓           ↓
PostgreSQL  Kafka (task-events)
```

## Features

- **Event-Driven**: Dapr subscription to `task-events` Kafka topic
- **Recurrence Logic**: Daily, weekly (specific days), monthly (specific day of month) patterns
- **Idempotency**: Tracks processed events via Dapr State Management
- **Time Preservation**: Maintains original time-of-day for next occurrences
- **Error Handling**: Retry logic with dead letter queue support

## Recurrence Rules

### Daily
```json
{
  "frequency": "daily",
  "interval": 2
}
```
→ Every 2 days

### Weekly
```json
{
  "frequency": "weekly",
  "interval": 1,
  "days_of_week": [0, 2, 4]
}
```
→ Every Monday (0), Wednesday (2), Friday (4)

### Monthly
```json
{
  "frequency": "monthly",
  "interval": 1,
  "day_of_month": 15
}
```
→ 15th of every month

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DAPR_HTTP_URL` | `http://localhost:3500` | Dapr sidecar HTTP endpoint |
| `DAPR_PUBSUB` | `kafka-pubsub` | Dapr Pub/Sub component name |
| `DAPR_TOPIC` | `task-events` | Kafka topic to subscribe |
| `DAPR_STATE_STORE` | `postgres-statestore` | Dapr State Store component name |

## Local Development

### Prerequisites
- Python 3.11+
- Dapr CLI installed
- Kafka running (Strimzi on Minikube)
- PostgreSQL (Neon)

### Run with Dapr

```bash
# Install dependencies
pip install -r requirements.txt

# Run with Dapr sidecar
dapr run \
  --app-id recurring-task-service \
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
docker build -t recurring-task-service:latest .
```

## Kubernetes Deployment

```bash
# Apply Dapr components (Pub/Sub, State)
kubectl apply -f ../../dapr-components/local/

# Deploy service
kubectl apply -f k8s/deployment.yaml
```

## Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Service information |
| `/health` | GET | Health check for K8s probes |
| `/dapr/subscribe` | GET | Dapr subscription discovery |
| `/events/task` | POST | Task event handler (Dapr calls this) |

## Testing

### Manual Event Publishing

```bash
# Publish test task.completed event via Dapr
curl -X POST http://localhost:3500/v1.0/publish/kafka-pubsub/task-events \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "test-123",
    "schema_version": "1.0",
    "event_type": "task.completed",
    "timestamp": "2026-01-03T10:00:00Z",
    "task_id": 1,
    "user_id": 1,
    "task_data": {
      "title": "Weekly team meeting",
      "status": "completed",
      "due_date": "2026-01-03T14:00:00Z",
      "recurrence_rule": {
        "frequency": "weekly",
        "interval": 1,
        "days_of_week": [0, 2]
      }
    }
  }'
```

### Check State (Idempotency)

```bash
# Check if event was processed
curl http://localhost:3500/v1.0/state/postgres-statestore/recurring-task:processed:test-123
```

### View Logs

```bash
# Local
tail -f logs/recurring-task-service.log

# Kubernetes
kubectl logs -l app=recurring-task-service -f
```

## Monitoring

### Metrics

- Dapr automatically exposes metrics on `:9090/metrics`
- Track consumer lag: `kafka_consumer_lag{topic="task-events"}`
- Track events processed: `dapr_pubsub_messages_consumed_total`

### Alerts

- **High consumer lag**: Lag > 1000 messages for > 5 minutes
- **Event processing failures**: Retry rate > 10% for > 10 minutes
- **Service down**: No heartbeat for > 2 minutes

## Troubleshooting

### No events being received

1. Check Dapr subscription:
   ```bash
   curl http://localhost:3500/v1.0/dapr/subscribe
   ```

2. Check Kafka topic exists:
   ```bash
   kubectl exec kafka-cluster-kafka-0 -- \
     /opt/kafka/bin/kafka-topics.sh --list \
     --bootstrap-server localhost:9092
   ```

3. Check Dapr Pub/Sub component:
   ```bash
   kubectl get component kafka-pubsub
   ```

### Events processed but no new tasks created

1. Check event publisher logs for errors
2. Verify Dapr Pub/Sub publish permissions
3. Check task-events topic in Kafka for published events

### Duplicate occurrences generated

1. Verify idempotency state is being saved
2. Check event_id uniqueness
3. Review Dapr State component configuration

## Architecture Decisions

### Why Dapr Pub/Sub instead of direct Kafka?

- **Portability**: Can switch Kafka providers without code changes
- **Simplicity**: No Kafka SDK dependencies
- **Reliability**: Built-in retry and DLQ handling
- **Observability**: Automatic distributed tracing

### Why Dapr State instead of direct database?

- **Abstraction**: Can switch state backends (PostgreSQL → Redis → CosmosDB)
- **Optimized**: Dapr handles connection pooling and timeouts
- **Consistency**: Strong consistency guarantees for idempotency

## Future Enhancements

- [ ] Advanced recurrence rules (e.g., "2nd Tuesday of every month")
- [ ] End date support for recurring tasks
- [ ] Skip holidays (integration with holiday calendar API)
- [ ] Batch processing for high-volume recurring tasks
- [ ] Metrics dashboard for recurring task analytics
