# Production Readiness Gate Intelligence

## Skill Name
Production Deployment Readiness Assessment and Quality Gate

## Scope
Validate system readiness for production deployment through comprehensive checks across observability, reliability, security, performance, cost, and operational excellence.

## Trigger Conditions

Apply this skill when:
- Preparing to deploy to production for the first time
- Deploying major version or breaking change
- Moving from staging to production
- Conducting pre-release audit
- Implementing new infrastructure or cloud resources
- After completing development but before user-facing release

## Core Intelligence Rules

### 1. Observability Baseline
**Rule**: Production systems must be observable. If you can't measure it, you can't improve it.

**Required Observability Components**:
```
✓ Metrics:    Prometheus + Grafana (or cloud equivalent)
✓ Logs:       Structured logging with correlation IDs
✓ Traces:     OpenTelemetry instrumentation
✓ Dashboards: Service-level dashboards with key metrics
✓ Alerts:     Critical path alerts configured
```

**Service-Level Metrics** (Minimum):
```yaml
# RED Metrics (Request-driven services)
- Request Rate (requests/second)
- Error Rate (% of requests failing)
- Duration (p50, p95, p99 latency)

# USE Metrics (Resource-driven services)
- Utilization (CPU, memory, disk)
- Saturation (queue depth, thread pool)
- Errors (error rate, timeout rate)

# Business Metrics
- Tasks created/completed per hour
- Active users
- Event processing lag (Kafka consumer lag)
```

**Logging Requirements**:
```python
# Structured logging format
{
  "timestamp": "2026-01-03T10:00:00Z",
  "level": "INFO",
  "service": "api-service",
  "correlation_id": "uuid",
  "user_id": "123",
  "message": "Task created",
  "task_id": 456,
  "duration_ms": 45
}
```

**Validation**:
- [ ] All services emit metrics to Prometheus
- [ ] All services use structured logging (JSON)
- [ ] Correlation IDs present in logs and traces
- [ ] At least 3 dashboards created (service overview, Kafka, database)
- [ ] OpenTelemetry configured with trace collection

### 2. Alerting Strategy
**Rule**: Alert on symptoms (user-facing impact), not causes. Alerts must be actionable.

**Critical Alerts** (Tier 1 - Page on-call):
```yaml
# Service Availability
- name: ServiceDown
  condition: up{service="api-service"} == 0
  duration: 1m
  severity: critical
  action: "Check pod status: kubectl get pods -n todo-app-prod"

# Error Rate
- name: HighErrorRate
  condition: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
  duration: 5m
  severity: critical
  action: "Check logs: kubectl logs -l app=api-service --tail=100"

# Kafka Consumer Lag
- name: ConsumerLagHigh
  condition: kafka_consumer_lag > 1000
  duration: 10m
  severity: critical
  action: "Scale consumers: kubectl scale deployment reminder-service --replicas=3"
```

**Warning Alerts** (Tier 2 - Slack/email):
```yaml
# Resource Usage
- name: HighMemoryUsage
  condition: container_memory_usage_bytes / container_spec_memory_limit_bytes > 0.80
  duration: 15m
  severity: warning

# Slow Queries
- name: SlowDatabaseQueries
  condition: histogram_quantile(0.95, rate(db_query_duration_seconds_bucket[5m])) > 1
  duration: 10m
  severity: warning
```

**Validation**:
- [ ] Critical alerts cover: service down, high error rate, database down, Kafka lag
- [ ] Alerts have clear remediation steps
- [ ] Alert fatigue avoided (< 5 alerts/day on average)
- [ ] On-call runbook exists for each critical alert

### 3. Failure Scenario Validation
**Rule**: Test failure scenarios before production. Hope is not a strategy.

**Failure Scenarios to Test**:
```
1. Pod Restart
   - Kill random pod: kubectl delete pod <name>
   - Validate: Traffic routes to healthy pods, no errors

2. Database Connection Loss
   - Block database traffic temporarily
   - Validate: Graceful degradation, retry logic, alerts fire

3. Kafka Broker Down
   - Stop Kafka broker
   - Validate: Producers retry, consumers reconnect, no data loss

4. High Load
   - Load test at 2x expected traffic
   - Validate: Autoscaling works, latency acceptable, no OOM

5. Deployment Rollout
   - Deploy with intentional error
   - Validate: Readiness probes fail, rollout halts, rollback successful

6. Disk Full
   - Fill persistent volume
   - Validate: Alerts fire, graceful handling, no data corruption
```

**Chaos Testing** (Advanced):
- Use chaos engineering tools (Chaos Mesh, Litmus)
- Test network latency, packet loss
- Test node failures, availability zone outages

**Validation**:
- [ ] At least 3 failure scenarios tested
- [ ] Pod restart causes no user-facing errors
- [ ] Database connection failure handled gracefully
- [ ] Load testing completed at 2x expected traffic

### 4. Security Baseline
**Rule**: Security is not optional. Implement defense in depth.

**Security Checklist**:

**Authentication & Authorization**:
- [ ] All APIs require authentication (JWT validation)
- [ ] User ID isolation enforced (user A cannot access user B's data)
- [ ] Authorization checks on all write operations
- [ ] No default/test credentials in production

**Secrets Management**:
- [ ] No secrets in code or config files
- [ ] Secrets stored in Kubernetes Secrets or cloud vault (Azure Key Vault, AWS Secrets Manager)
- [ ] Secrets accessed via Dapr Secrets API (not hardcoded)
- [ ] Secrets rotated regularly (90-day policy)

**Network Security**:
- [ ] TLS/HTTPS enforced for all external traffic
- [ ] mTLS enabled for service-to-service (Dapr mTLS)
- [ ] Network policies limit pod-to-pod communication
- [ ] No privileged containers

**Data Protection**:
- [ ] Sensitive data encrypted at rest (database encryption)
- [ ] Sensitive data encrypted in transit (TLS)
- [ ] PII not logged (user emails, passwords)
- [ ] Database backups encrypted

**Vulnerability Management**:
- [ ] Container images scanned (Trivy, Snyk)
- [ ] No critical vulnerabilities in production images
- [ ] Base images updated regularly
- [ ] Dependency scanning enabled (Dependabot, Renovate)

**Validation**:
- [ ] Security scan passed (no critical vulnerabilities)
- [ ] All secrets retrieved via Dapr Secrets API
- [ ] mTLS enabled between services
- [ ] TLS certificate valid and not expiring soon (> 30 days)

### 5. Performance Baseline
**Rule**: Define performance targets. Measure against them. Do not deploy if degraded.

**Performance SLOs** (Service-Level Objectives):
```yaml
# API Latency
- metric: http_request_duration_p95
  target: < 200ms
  measurement_window: 5m

# Throughput
- metric: http_requests_per_second
  target: > 100 req/s (sustained)

# Error Rate
- metric: http_error_rate
  target: < 1% (excluding 4xx client errors)

# Database Query Time
- metric: db_query_duration_p95
  target: < 100ms

# Kafka Consumer Lag
- metric: kafka_consumer_lag
  target: < 100 messages OR < 1 minute
```

**Load Testing**:
```bash
# Use k6, Locust, or JMeter
# Test scenario: 1000 concurrent users, 10 req/s each
k6 run --vus 1000 --duration 10m load-test.js

# Validate:
# - p95 latency < 200ms
# - Error rate < 1%
# - No OOM kills
# - Autoscaling triggers correctly
```

**Validation**:
- [ ] Load test completed at expected traffic
- [ ] Load test completed at 2x expected traffic
- [ ] p95 latency meets SLO (< 200ms)
- [ ] Error rate meets SLO (< 1%)
- [ ] Database queries optimized (indexes added)

### 6. Reliability and High Availability
**Rule**: Design for failure. Single points of failure are not acceptable in production.

**High Availability Requirements**:
```yaml
# Replica Counts
api-service:
  replicas: 3              # Minimum 2 for HA
  maxUnavailable: 0        # Zero-downtime deployments

reminder-service:
  replicas: 2
  maxUnavailable: 0

# Database
postgres:
  replicas: 1              # Managed DB handles HA
  backup_frequency: daily
  point_in_time_recovery: enabled

# Kafka
kafka:
  brokers: 3
  replication_factor: 3
  min_insync_replicas: 2
```

**Pod Disruption Budgets**:
```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: api-service-pdb
spec:
  minAvailable: 2          # At least 2 pods during disruption
  selector:
    matchLabels:
      app: api-service
```

**Backup and Recovery**:
- [ ] Database backups automated (daily)
- [ ] Backup restore tested (< 1 hour RTO)
- [ ] Point-in-time recovery enabled
- [ ] Disaster recovery plan documented

**Graceful Shutdown**:
```python
# Handle SIGTERM
import signal
import sys

def signal_handler(sig, frame):
    print("Shutting down gracefully...")
    # 1. Stop accepting new requests
    # 2. Finish in-flight requests (up to 30s)
    # 3. Close database connections
    # 4. Exit
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
```

**Validation**:
- [ ] Minimum 2 replicas for all stateless services
- [ ] PodDisruptionBudgets defined for critical services
- [ ] Database backup tested and verified
- [ ] Graceful shutdown handles SIGTERM (30s grace period)
- [ ] Readiness probes prevent traffic to unready pods

### 7. Cost Awareness and Optimization
**Rule**: Understand production costs. Start minimal, scale as needed.

**Cost Targets** (Free Tier Strategy):
```yaml
# Compute (Kubernetes)
- 3 nodes × 2 vCPU × 8GB RAM
- Target: Within AKS/GKE/EKS free tier

# Database (Neon Serverless)
- 0.5 GB storage
- 100 hours compute/month
- Target: Free tier

# Kafka (Redpanda Cloud)
- 5 GB storage
- 10 GB ingress/month
- Target: Free tier

# Storage (Cloud Object Storage)
- < 5 GB for backups
- Target: < $1/month

# Total Monthly Cost: < $50
```

**Resource Optimization**:
```yaml
# Right-size resource requests/limits
api-service:
  requests:
    cpu: 250m          # Not 1000m
    memory: 256Mi      # Not 1Gi
  limits:
    cpu: 500m
    memory: 512Mi

# Use HPA to scale down when idle
autoscaling:
  minReplicas: 1       # Scale to 1 during low traffic
  maxReplicas: 10
```

**Validation**:
- [ ] Resource requests based on actual usage (not overprovisioned)
- [ ] HPA configured to scale down during low traffic
- [ ] Database within free tier or < $20/month
- [ ] Kafka within free tier or < $10/month
- [ ] Total monthly cost < $50 for MVP

### 8. Operational Readiness
**Rule**: Operations team (or developer on-call) must be able to operate the system.

**Operational Requirements**:
```
✓ Runbooks: Step-by-step guides for common tasks
✓ Deployment: Automated via CI/CD
✓ Rollback: One-command rollback (Helm)
✓ Monitoring: Dashboards accessible to ops team
✓ Logs: Centralized and searchable
✓ Alerts: Routed to on-call (PagerDuty, Opsgenie)
```

**Runbook Example**:
```markdown
# Runbook: Scale Reminder Service

## When to Use
Consumer lag > 1000 messages for > 10 minutes

## Steps
1. Check current replica count:
   kubectl get deployment reminder-service -n todo-app-prod

2. Scale up:
   kubectl scale deployment reminder-service --replicas=5 -n todo-app-prod

3. Monitor lag:
   kubectl logs -l app=reminder-service --tail=100 -n todo-app-prod

4. Validate lag decreasing:
   Check Grafana dashboard: Kafka Consumer Lag

5. Scale down after lag < 100:
   kubectl scale deployment reminder-service --replicas=2 -n todo-app-prod
```

**Deployment Automation**:
```yaml
# CI/CD Pipeline (GitHub Actions, GitLab CI)
1. Run tests
2. Build container image
3. Push to registry (ACR, ECR, GCR)
4. Helm upgrade (staging)
5. Run smoke tests
6. Manual approval gate
7. Helm upgrade (production)
8. Run smoke tests
9. Notify team (Slack)
```

**Validation**:
- [ ] Runbooks exist for top 5 operational tasks
- [ ] Deployment automated via CI/CD pipeline
- [ ] Rollback tested and documented
- [ ] On-call rotation defined
- [ ] Escalation path documented

### 9. Data Integrity and Consistency
**Rule**: Validate data consistency before and after deployment.

**Pre-Deployment Data Checks**:
```sql
-- Check for orphaned records
SELECT COUNT(*) FROM tasks WHERE user_id NOT IN (SELECT id FROM users);
-- Expected: 0

-- Check for null required fields
SELECT COUNT(*) FROM tasks WHERE title IS NULL;
-- Expected: 0

-- Check for data anomalies
SELECT COUNT(*) FROM tasks WHERE created_at > updated_at;
-- Expected: 0
```

**Post-Deployment Validation**:
```sql
-- Verify migration success
SELECT COUNT(*) FROM tasks WHERE priority IS NOT NULL;
-- Expected: > 0 (if default applied)

-- Verify indexes created
SELECT indexname FROM pg_indexes WHERE tablename = 'tasks';
-- Expected: idx_tasks_priority, idx_tasks_tags, ...
```

**Data Backup Before Major Changes**:
```bash
# Before schema migration
pg_dump -h <host> -U <user> -d <database> > backup-$(date +%Y%m%d).sql

# Verify backup
ls -lh backup-*.sql
```

**Validation**:
- [ ] Pre-deployment data integrity checks pass
- [ ] Database backup created before migration
- [ ] Post-deployment data validation queries pass
- [ ] No orphaned records or data corruption

### 10. Compliance and Documentation
**Rule**: Documentation is not optional. Future you (or your successor) will need it.

**Required Documentation**:
```
✓ README.md: Quick start, architecture overview
✓ DEPLOYMENT.md: Step-by-step deployment guide
✓ RUNBOOKS.md: Operational procedures
✓ ADRs: Architectural decisions documented
✓ API Documentation: OpenAPI/Swagger spec
✓ Database Schema: ERD and migration history
```

**README.md Checklist**:
- [ ] What the system does (1-paragraph description)
- [ ] Architecture diagram
- [ ] Tech stack
- [ ] Quick start (< 5 steps)
- [ ] Links to detailed docs

**DEPLOYMENT.md Checklist**:
- [ ] Prerequisites (tools, access)
- [ ] Environment setup (dev, staging, prod)
- [ ] Deployment steps (automated and manual fallback)
- [ ] Rollback procedure
- [ ] Smoke tests

**Compliance** (if applicable):
- [ ] GDPR: User data export/delete functionality
- [ ] SOC2: Audit logs for sensitive operations
- [ ] HIPAA: Encryption at rest and in transit (if health data)

**Validation**:
- [ ] README.md up to date
- [ ] DEPLOYMENT.md tested by someone other than author
- [ ] API documentation auto-generated (Swagger)
- [ ] All ADRs reviewed

## Production Readiness Score

**Scoring System** (0-100):
```
Observability:         /15 points
Alerting:             /10 points
Failure Testing:      /10 points
Security:             /20 points
Performance:          /10 points
High Availability:    /10 points
Cost Optimization:    /5 points
Operational Readiness:/10 points
Data Integrity:       /5 points
Documentation:        /5 points
----------------------------
Total:                /100 points

Minimum to deploy: 80/100
```

**Evaluation**:
```
IF score >= 90:
   Production ready, deploy with confidence
ELSE IF score >= 80:
   Production ready, but address gaps post-launch
ELSE IF score >= 70:
   Deploy to staging, fix critical gaps before production
ELSE:
   NOT ready, fix gaps before staging
```

## Anti-Patterns to Avoid

### ❌ "We'll Add Monitoring Later"
**Anti-Pattern**: Deploying without metrics/logging.
**Fix**: Observability is Day 1 requirement.

### ❌ No Load Testing
**Anti-Pattern**: "It works on my machine" → Deploy to production.
**Fix**: Load test at 2x expected traffic before production.

### ❌ Single Replica in Production
**Anti-Pattern**: `replicas: 1` because "it's cheaper."
**Fix**: Minimum 2 replicas for HA.

### ❌ No Rollback Plan
**Anti-Pattern**: Deploy and hope it works.
**Fix**: Test rollback before deployment.

### ❌ Secrets in Code
**Anti-Pattern**: Database password in environment variable in Deployment YAML.
**Fix**: Use Kubernetes Secrets or cloud vault.

### ❌ No Alerts
**Anti-Pattern**: System is down, nobody knows.
**Fix**: Critical alerts configured before production.

### ❌ No Documentation
**Anti-Pattern**: Only the author knows how to deploy.
**Fix**: DEPLOYMENT.md with step-by-step guide.

### ❌ Ignoring Costs
**Anti-Pattern**: Deploy expensive resources, get surprise bill.
**Fix**: Estimate costs, optimize for free tiers.

## Decision Heuristics

### Go/No-Go Decision
```
IF (critical gaps exist):
   NO-GO (fix before production)

Critical gaps:
- No authentication
- Secrets in code
- No database backups
- No alerts for service down
- Single replica for critical service

IF (security score < 15/20):
   NO-GO

IF (observability score < 10/15):
   NO-GO

ELSE IF (total score >= 80):
   GO
```

### Phased Rollout Strategy
```
IF (first production deployment):
   Phase 1: Deploy to 10% of traffic (canary)
   Wait 24 hours, monitor metrics
   Phase 2: Deploy to 50% of traffic
   Wait 12 hours
   Phase 3: Deploy to 100% of traffic

ELSE IF (minor update):
   Rolling update, 0 downtime
```

## Pre-Deployment Checklist

**1 Week Before Production**:
- [ ] Load testing completed
- [ ] Security scan passed
- [ ] Backup/restore tested
- [ ] Documentation reviewed

**1 Day Before Production**:
- [ ] Database backup created
- [ ] Rollback plan tested
- [ ] On-call notified
- [ ] Smoke tests prepared

**Deployment Day**:
- [ ] Deploy during low-traffic window
- [ ] Monitor metrics for 1 hour post-deployment
- [ ] Run smoke tests
- [ ] Verify alerts working
- [ ] Announce in team channel

**Post-Deployment** (within 24 hours):
- [ ] Review error logs
- [ ] Check performance metrics vs baseline
- [ ] Validate cost is within budget
- [ ] Create post-deployment report

## Validation Command Summary

```bash
# Security
trivy image api-service:1.0.0

# Performance
k6 run load-test.js

# High Availability
kubectl get pdb -n todo-app-prod

# Observability
kubectl port-forward svc/prometheus 9090:9090
kubectl port-forward svc/grafana 3000:3000

# Backups
pg_dump ... && pg_restore --validate

# Deployment
helm upgrade --dry-run --debug api-service ./charts/api-service

# Rollback
helm rollback api-service

# Logs
kubectl logs -l app=api-service --tail=100
```
