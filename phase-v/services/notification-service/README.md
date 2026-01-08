# Notification Service

Event-driven microservice that sends email notifications for task reminders.

## Purpose

Consumes `reminders` events from Kafka and sends email notifications to users via SMTP.

## Architecture

```
Kafka (reminders topic)
         ↓
    Dapr Pub/Sub
         ↓
Notification Service
    ↓           ↓
Dapr Secrets  Email (SMTP)
    ↓           ↓
K8s Secrets   User Inbox
```

## Features

- **Event-Driven**: Dapr subscription to `reminders` Kafka topic
- **SMTP Integration**: Async email sending via aiosmtplib
- **Template Rendering**: Jinja2 HTML email templates
- **Secrets Management**: SMTP credentials via Dapr Secrets API
- **Idempotency**: Tracks sent notifications via Dapr State Management
- **Delivery Tracking**: Logs notification delivery status

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DAPR_HTTP_URL` | `http://localhost:3500` | Dapr sidecar HTTP endpoint |
| `DAPR_PUBSUB` | `kafka-pubsub` | Dapr Pub/Sub component name |
| `DAPR_TOPIC` | `reminders` | Kafka topic to subscribe |
| `DAPR_SECRET_STORE` | `kubernetes-secrets` | Dapr Secrets component name |
| `DAPR_STATE_STORE` | `postgres-statestore` | Dapr State Store component name |

## SMTP Configuration

SMTP credentials are stored in Kubernetes Secret `backend-secrets` and accessed via Dapr Secrets API:

```yaml
SMTP_HOST: smtp.gmail.com
SMTP_PORT: 587
SMTP_USERNAME: your-email@gmail.com
SMTP_PASSWORD: your-app-password
SMTP_FROM_EMAIL: noreply@example.com
```

### Gmail Setup

1. Enable 2-factor authentication on your Google account
2. Generate an App Password: https://myaccount.google.com/apppasswords
3. Use the app password in `SMTP_PASSWORD`

## Local Development

### Prerequisites
- Python 3.11+
- Dapr CLI installed
- Kafka running (Strimzi on Minikube)
- SMTP credentials configured

### Run with Dapr

```bash
# Install dependencies
pip install -r requirements.txt

# Run with Dapr sidecar
dapr run \
  --app-id notification-service \
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
docker build -t notification-service:latest .
```

## Kubernetes Deployment

```bash
# Create SMTP secrets
kubectl create secret generic backend-secrets \
  --from-literal=SMTP_HOST='smtp.gmail.com' \
  --from-literal=SMTP_PORT='587' \
  --from-literal=SMTP_USERNAME='your-email@gmail.com' \
  --from-literal=SMTP_PASSWORD='your-app-password' \
  --from-literal=SMTP_FROM_EMAIL='noreply@example.com' \
  --namespace=todo-app-dev

# Apply Dapr components
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
| `/events/reminder` | POST | Reminder event handler (Dapr calls this) |

## Email Template

The service uses a responsive HTML email template (`app/templates/reminder.html`) with:
- Task title and description
- Due date prominently displayed
- Branded header and footer
- Mobile-friendly design
- Plain text fallback

## Testing

### Manual Event Publishing

```bash
# Publish test reminder event via Dapr
curl -X POST http://localhost:3500/v1.0/publish/kafka-pubsub/reminders \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "test-456",
    "schema_version": "1.0",
    "event_type": "reminder.due",
    "timestamp": "2026-01-03T13:00:00Z",
    "task_id": 1,
    "user_id": 1,
    "due_date": "2026-01-03T14:00:00Z",
    "task_title": "Team meeting",
    "task_description": "Weekly sync with the team",
    "notification_channels": ["email"],
    "reminder_time": "2026-01-03T13:00:00Z"
  }'
```

### Check Delivery Status (Idempotency)

```bash
# Check if notification was sent
curl http://localhost:3500/v1.0/state/postgres-statestore/notification:sent:test-456
```

### View Logs

```bash
# Local
tail -f logs/notification-service.log

# Kubernetes
kubectl logs -l app=notification-service -f
```

## Monitoring

### Metrics

- Track emails sent: `notification_emails_sent_total`
- Track failures: `notification_emails_failed_total`
- Track SMTP errors: `notification_smtp_errors_total`

### Alerts

- **SMTP connection failures**: Retry rate > 50% for > 5 minutes
- **Email delivery failures**: Failure rate > 10% for > 10 minutes
- **Service down**: No heartbeat for > 2 minutes

## Troubleshooting

### No emails being sent

1. Check SMTP credentials:
   ```bash
   kubectl get secret backend-secrets -o yaml
   ```

2. Test SMTP connection:
   ```python
   import aiosmtplib
   # Test connection manually
   ```

3. Check Dapr Secrets component:
   ```bash
   kubectl get component kubernetes-secrets
   ```

### Emails going to spam

1. Configure SPF record for sending domain
2. Configure DKIM signing
3. Use a verified sending domain
4. Reduce sending frequency

### Duplicate notifications

1. Verify idempotency state is being saved
2. Check event_id uniqueness
3. Review Dapr State component configuration

## Future Enhancements

- [ ] SMS notifications via Twilio
- [ ] Push notifications for mobile apps
- [ ] Custom email templates per user
- [ ] Notification preferences (user can disable)
- [ ] Digest emails (daily summary)
- [ ] Rich email formatting with markdown support
