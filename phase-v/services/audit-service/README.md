# Audit Service

Event-driven microservice that logs all system events for compliance and debugging.

## Purpose

Consumes events from ALL Kafka topics (`task-events`, `reminders`, `task-updates`) and stores them in PostgreSQL for audit trails, compliance, and debugging.

## Architecture

```
Kafka (all topics)
    ↓          ↓          ↓
task-events reminders task-updates
    ↓          ↓          ↓
      Dapr Pub/Sub
           ↓
    Audit Service
           ↓
      PostgreSQL
    (audit_logs table)
```

## Features

- **Multi-Topic Subscription**: Consumes all events from all topics
- **Complete Event Storage**: Stores full event payload as JSONB
- **Query API**: RESTful API for retrieving audit logs with filters
- **Compliance Ready**: 90-day retention policy, tamper-proof logging
- **High Performance**: Indexed queries, JSONB support for flexible querying
- **Idempotency**: Prevents duplicate log entries

## Database Schema

```sql
CREATE TABLE audit_logs (
    log_id SERIAL PRIMARY KEY,
    event_id VARCHAR(255) UNIQUE NOT NULL,
    user_id INTEGER,
    action_type VARCHAR(50) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id INTEGER,
    event_data JSONB NOT NULL,
    source_service VARCHAR(100),
    timestamp TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for fast querying
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action_type ON audit_logs(action_type);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp);
CREATE INDEX idx_audit_logs_event_data_gin ON audit_logs USING GIN(event_data);
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://...` | PostgreSQL connection string |
| `DAPR_HTTP_URL` | `http://localhost:3500` | Dapr sidecar HTTP endpoint |
| `DAPR_PUBSUB` | `kafka-pubsub` | Dapr Pub/Sub component name |

## API Endpoints

### Query Audit Logs

```http
GET /api/audit/logs?user_id=1&action_type=task.created&limit=50
```

**Query Parameters:**
- `user_id` (optional): Filter by user ID
- `action_type` (optional): Filter by action type (task.created, task.updated, etc.)
- `resource_type` (optional): Filter by resource type (task, reminder)
- `start_date` (optional): Start of date range (ISO 8601)
- `end_date` (optional): End of date range (ISO 8601)
- `limit` (default: 100, max: 1000): Number of results
- `offset` (default: 0): Pagination offset

**Response:**
```json
[
  {
    "log_id": 123,
    "event_id": "uuid-123",
    "user_id": 1,
    "action_type": "task.created",
    "resource_type": "task",
    "resource_id": 456,
    "event_data": {...},
    "source_service": "api-service",
    "timestamp": "2026-01-03T10:00:00Z",
    "created_at": "2026-01-03T10:00:01Z"
  }
]
```

### Get Statistics

```http
GET /api/audit/stats
```

**Response:**
```json
{
  "total_logs": 10000,
  "action_type_distribution": {
    "task.created": 3000,
    "task.updated": 4000,
    "task.deleted": 500,
    "task.completed": 2500
  },
  "resource_type_distribution": {
    "task": 9500,
    "reminder": 500
  }
}
```

## Local Development

### Run Database Migration

```bash
# Connect to PostgreSQL
psql -U user -d audit_db

# Run migration
\i app/migrations/001_create_audit_logs.sql
```

### Run with Dapr

```bash
# Install dependencies
pip install -r requirements.txt

# Run with Dapr sidecar
dapr run \
  --app-id audit-service \
  --app-port 8000 \
  --dapr-http-port 3500 \
  --components-path ../../dapr-components/local \
  -- uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Docker Build

```bash
docker build -t audit-service:latest .
```

## Kubernetes Deployment

```bash
# Run database migration
kubectl exec -it postgres-pod -- psql -U user -d audit_db -f /migrations/001_create_audit_logs.sql

# Deploy service
kubectl apply -f k8s/deployment.yaml
```

## Testing

### Publish Test Event

```bash
curl -X POST http://localhost:3500/v1.0/publish/kafka-pubsub/task-events \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "test-789",
    "schema_version": "1.0",
    "event_type": "task.created",
    "timestamp": "2026-01-03T10:00:00Z",
    "task_id": 1,
    "user_id": 1,
    "task_data": {"title": "Test task"}
  }'
```

### Query Audit Logs

```bash
# All logs
curl http://localhost:8000/api/audit/logs

# Filter by user
curl "http://localhost:8000/api/audit/logs?user_id=1"

# Filter by action type
curl "http://localhost:8000/api/audit/logs?action_type=task.created"

# Date range
curl "http://localhost:8000/api/audit/logs?start_date=2026-01-01T00:00:00Z&end_date=2026-01-31T23:59:59Z"
```

### Get Statistics

```bash
curl http://localhost:8000/api/audit/stats
```

## Compliance Features

### Data Retention

Implement automated cleanup of logs older than 90 days:

```sql
-- Run daily via cron or Kubernetes CronJob
DELETE FROM audit_logs
WHERE created_at < NOW() - INTERVAL '90 days';
```

### Tamper Detection

Audit logs are append-only. To detect tampering:

1. Verify `event_id` uniqueness
2. Check timestamp sequence
3. Validate event_data schema

### Export for Compliance

Export audit logs for compliance audits:

```bash
# Export to CSV
psql -U user -d audit_db -c "COPY (SELECT * FROM audit_logs WHERE created_at >= '2026-01-01') TO STDOUT CSV HEADER" > audit_export.csv

# Export to JSON
psql -U user -d audit_db -t -c "SELECT row_to_json(t) FROM audit_logs t WHERE created_at >= '2026-01-01'" > audit_export.json
```

## Monitoring

### Metrics

- `audit_logs_total`: Total number of audit logs
- `audit_logs_per_action_type`: Count by action type
- `audit_logs_insert_duration`: Time to insert log

### Alerts

- **High event volume**: Insert rate > 10,000/min for > 5 minutes
- **Database errors**: Insert failure rate > 1% for > 5 minutes
- **Disk space**: Database disk usage > 80%

## Troubleshooting

### No logs being created

1. Check Dapr subscriptions:
   ```bash
   curl http://localhost:3500/v1.0/dapr/subscribe
   ```

2. Check database connection:
   ```bash
   psql -U user -d audit_db -c "SELECT COUNT(*) FROM audit_logs"
   ```

3. Check event consumption:
   ```bash
   kubectl logs -l app=audit-service -f
   ```

### Duplicate log entries

1. Verify `event_id` uniqueness in source events
2. Check idempotency logic in consumer
3. Review database constraints

### Slow queries

1. Verify indexes are created:
   ```sql
   SELECT * FROM pg_indexes WHERE tablename = 'audit_logs';
   ```

2. Analyze query performance:
   ```sql
   EXPLAIN ANALYZE SELECT * FROM audit_logs WHERE user_id = 1;
   ```

3. Consider partitioning by date for large datasets

## Future Enhancements

- [ ] Elasticsearch integration for full-text search
- [ ] Real-time anomaly detection
- [ ] Automated compliance report generation
- [ ] Log archival to S3/Azure Blob
- [ ] GraphQL API for complex queries
- [ ] Event replay capability
