# Todo AI Chatbot - Helm Chart

This Helm chart deploys the Todo AI Chatbot application with all its microservices to Kubernetes.

## Prerequisites

- Kubernetes 1.20+
- Helm 3.0+
- kubectl configured to communicate with your cluster
- cert-manager (for SSL certificates)
- NGINX Ingress Controller

## Installation

### Quick Install (Development)

```bash
helm install todo-app ./charts/todo-app
```

### Production Install

```bash
# Create namespace
kubectl create namespace production

# Install with production values
helm install todo-app ./charts/todo-app \
  --namespace production \
  --values ./charts/todo-app/values.production.yaml \
  --set domain=todo.yourdomain.com \
  --set secrets.jwtSecretKey="your-jwt-secret" \
  --set secrets.openaiApiKey="sk-your-key" \
  --set secrets.smtpUsername="your-email@gmail.com" \
  --set secrets.smtpPassword="your-app-password"
```

### Staging Install

```bash
# Create namespace
kubectl create namespace staging

# Install with staging values
helm install todo-app ./charts/todo-app \
  --namespace staging \
  --values ./charts/todo-app/values.staging.yaml \
  --set domain=staging-todo.yourdomain.com
```

## Configuration

### Key Configuration Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `environment` | Deployment environment | `production` |
| `domain` | Application domain | `todo.yourdomain.com` |
| `apiService.replicaCount` | Number of API service replicas | `3` |
| `postgresql.enabled` | Use in-cluster PostgreSQL | `true` |
| `externalDatabase.enabled` | Use external managed database | `false` |
| `kafka.enabled` | Use in-cluster Kafka | `true` |
| `externalKafka.enabled` | Use external Kafka | `false` |
| `ingress.enabled` | Enable Ingress | `true` |
| `monitoring.enabled` | Enable Prometheus/Grafana | `true` |

### Secrets Configuration

Create a `secrets.yaml` file:

```yaml
secrets:
  databaseUrl: "postgresql://user:pass@host:5432/db"
  jwtSecretKey: "your-super-secret-jwt-key-32-chars"
  betterAuthSecret: "your-better-auth-secret"
  authSecret: "your-auth-secret"
  openaiApiKey: "sk-your-openai-api-key"
  smtpUsername: "your-email@gmail.com"
  smtpPassword: "your-app-password"
  smtpFromEmail: "noreply@yourdomain.com"
```

Install with secrets:

```bash
helm install todo-app ./charts/todo-app \
  --values ./charts/todo-app/values.production.yaml \
  --values secrets.yaml
```

**Important**: Never commit `secrets.yaml` to version control!

## Architecture

This chart deploys the following components:

### Microservices
- **API Service**: Main REST API (port 8000)
- **Recurring Task Service**: Handles recurring tasks (port 8001)
- **Notification Service**: Sends notifications (port 8002)
- **Audit Service**: Logs all events (port 8003)
- **WebSocket Sync Service**: Real-time updates (port 8004)

### Infrastructure
- **PostgreSQL**: Database (in-cluster or external)
- **Kafka**: Event streaming (Strimzi operator)
- **NGINX Ingress**: HTTP/HTTPS routing
- **cert-manager**: SSL certificate management

### Optional Components
- **Prometheus**: Metrics collection
- **Grafana**: Metrics visualization

## Upgrades

### Update Application Version

```bash
# Update image tags
helm upgrade todo-app ./charts/todo-app \
  --set apiService.image.tag=v2.0.0 \
  --set recurringTaskService.image.tag=v2.0.0
```

### Update Configuration

```bash
helm upgrade todo-app ./charts/todo-app \
  --reuse-values \
  --set apiService.replicaCount=5
```

### Rollback

```bash
# List releases
helm history todo-app

# Rollback to previous version
helm rollback todo-app

# Rollback to specific revision
helm rollback todo-app 3
```

## Scaling

### Manual Scaling

```bash
kubectl scale deployment api-service --replicas=10
```

### Auto-Scaling

Auto-scaling is enabled by default for all services:

```yaml
autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
```

Disable auto-scaling:

```bash
helm upgrade todo-app ./charts/todo-app \
  --set apiService.autoscaling.enabled=false
```

## Monitoring

### Access Grafana

```bash
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80
# Open http://localhost:3000
# Username: admin
# Password: (from values.yaml)
```

### Access Prometheus

```bash
kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090
# Open http://localhost:9090
```

## Troubleshooting

### Check Pod Status

```bash
kubectl get pods
kubectl describe pod <pod-name>
kubectl logs <pod-name>
```

### Check Ingress

```bash
kubectl get ingress
kubectl describe ingress todo-app-ingress
```

### Check Certificate

```bash
kubectl get certificate
kubectl describe certificate todo-app-tls
```

### Debug Database Connection

```bash
kubectl exec -it deployment/api-service -- env | grep DATABASE
```

### Test Service Connectivity

```bash
# Port forward to API service
kubectl port-forward svc/api-service 8000:8000

# Test in another terminal
curl http://localhost:8000/health
```

## External Database Setup

### Using DigitalOcean Managed Database

1. Create managed PostgreSQL database in DigitalOcean
2. Get connection details
3. Update values:

```yaml
postgresql:
  enabled: false

externalDatabase:
  enabled: true
  host: "your-db.db.ondigitalocean.com"
  port: 25060
  username: "doadmin"
  password: "your-db-password"
  database: "defaultdb"
  sslMode: "require"
```

## External Kafka Setup

### Using Confluent Cloud

```yaml
kafka:
  enabled: false

externalKafka:
  enabled: true
  bootstrapServers: "pkc-xxxxx.us-east-1.aws.confluent.cloud:9092"
  sasl:
    enabled: true
    mechanism: "SCRAM-SHA-256"
    username: "your-api-key"
    password: "your-api-secret"
```

## Security Best Practices

1. **Use External Secrets**: Use [External Secrets Operator](https://external-secrets.io/) instead of storing secrets in values files
2. **Enable Network Policies**: Restrict pod-to-pod communication
3. **Enable Pod Security Policies**: Enforce security standards
4. **Use Managed Databases**: Use DigitalOcean Managed Database for production
5. **Regular Updates**: Keep images and dependencies updated
6. **Image Scanning**: Scan images for vulnerabilities
7. **RBAC**: Configure proper role-based access control

## Uninstallation

```bash
# Delete application
helm uninstall todo-app

# Delete namespace (optional)
kubectl delete namespace production
```

## Support

- Documentation: [DIGITALOCEAN_DEPLOYMENT.md](../../DIGITALOCEAN_DEPLOYMENT.md)
- Issues: [GitHub Issues](https://github.com/yourusername/todo-app/issues)
- Email: admin@yourdomain.com

## License

MIT License
