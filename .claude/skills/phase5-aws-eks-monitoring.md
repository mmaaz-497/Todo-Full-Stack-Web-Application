# Phase V – AWS EKS Monitoring & Observability (Hackathon II)

## 1. Overview

This phase establishes comprehensive monitoring and observability for your EKS-hosted full-stack application. It covers logging, metrics, tracing, alerting, and visualization to ensure your Next.js frontend and FastAPI backend applications run reliably and performantly.

### Monitoring Architecture Description
```
Application Pods -> Prometheus/Grafana -> CloudWatch -> AlertManager -> Notifications
      |                |                   |              |              |
   Structured Logs   Metrics Exporters   AWS Services   Alert Rules   Slack/Email
      |                |                   |              |              |
   Jaeger Tracing   Grafana Dashboards   CloudTrail    SNS Topics   PagerDuty
```

## 2. Prerequisites

Before implementing monitoring and observability:

- EKS cluster with deployed applications
- AWS account with CloudWatch permissions
- Helm installed
- kubectl configured
- Understanding of Prometheus and Grafana
- Basic knowledge of distributed tracing concepts

## 3. Prometheus and Grafana Installation

### Install Prometheus Stack via Helm

Create a values file for Prometheus stack:

```yaml
# prometheus-values.yaml
prometheus:
  prometheusSpec:
    storageSpec:
      volumeClaimTemplate:
        spec:
          storageClassName: gp2
          accessModes: ["ReadWriteOnce"]
          resources:
            requests:
              storage: 10Gi
  service:
    type: LoadBalancer

grafana:
  adminPassword: prom-operator
  service:
    type: LoadBalancer
  persistence:
    enabled: true
    storageClassName: gp2
    size: 10Gi
  datasources:
    datasources.yaml:
      apiVersion: 1
      datasources:
      - name: Prometheus
        type: prometheus
        url: http://prometheus-operated:9090/
        access: proxy
        isDefault: true
  dashboardProviders:
    dashboardproviders.yaml:
      apiVersion: 1
      providers:
      - name: 'default'
        orgId: 1
        folder: ''
        type: file
        disableDeletion: false
        editable: true
        options:
          path: /var/lib/grafana/dashboards/default
  dashboards:
    default:
      k8s-cluster-summary:
        gnetId: 11001
        revision: 1
        datasource: Prometheus
      k8s-applications:
        gnetId: 11002
        revision: 1
        datasource: Prometheus
```

Install Prometheus Operator:

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install prometheus prometheus-community/kube-prometheus-stack -f prometheus-values.yaml
```

## 4. Application-Level Metrics Collection

### Configure Application Metrics Endpoints

For FastAPI backend, add metrics middleware:

```python
# backend/metrics.py
from prometheus_client import Counter, Histogram, generate_latest
from starlette.middleware.base import BaseHTTPMiddleware
import time

REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start_time = time.time()

        response = await call_next(request)

        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()

        REQUEST_LATENCY.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(time.time() - start_time)

        return response
```

For Next.js frontend, expose metrics endpoint:

```javascript
// pages/api/metrics.js
import { collectDefaultMetrics, register } from 'prom-client';

collectDefaultMetrics();

export default async function handler(req, res) {
  res.setHeader('Content-Type', register.contentType);
  res.send(await register.metrics());
}
```

### Create Service Monitors

Create ServiceMonitor resources for Prometheus to scrape application metrics:

```yaml
# application-metrics.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: todo-backend-metrics
  labels:
    app: todo-backend
spec:
  selector:
    matchLabels:
      app: todo-backend
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics
---
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: todo-frontend-metrics
  labels:
    app: todo-frontend
spec:
  selector:
    matchLabels:
      app: todo-frontend
  endpoints:
  - port: metrics
    interval: 30s
    path: /api/metrics
```

## 5. Distributed Tracing with Jaeger

### Install Jaeger Operator

```bash
kubectl create namespace observability
helm repo add jaegertracing https://jaegertracing.github.io/helm-charts
helm install jaeger jaegertracing/jaeger-operator --namespace observability --set rbac.clusterRole=true
```

### Configure Jaeger Instance

```yaml
# jaeger-config.yaml
apiVersion: jaegertracing.io/v1
kind: Jaeger
metadata:
  name: todo-tracing
spec:
  strategy: production
  storage:
    type: elasticsearch
    options:
      es:
        server-urls: http://elasticsearch:9200
  collector:
    maxReplicas: 3
    resources:
      limits:
        cpu: 1
        memory: 1Gi
      requests:
        cpu: 500m
        memory: 512Mi
  query:
    service:
      type: LoadBalancer
  agent:
    strategy: DaemonSet
```

### Integrate Tracing in Applications

For FastAPI backend:

```python
# backend/tracing.py
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

def setup_tracing():
    trace.set_tracer_provider(TracerProvider())

    jaeger_exporter = JaegerExporter(
        agent_host_name='jaeger-collector.observability.svc.cluster.local',
        agent_port=14268,
    )

    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(jaeger_exporter)
    )

    return trace.get_tracer(__name__)
```

For Next.js frontend:

```javascript
// lib/tracing.js
import { WebTracerProvider } from '@opentelemetry/web';
import { ZipkinExporter } from '@opentelemetry/exporter-zipkin';
import { SimpleSpanProcessor } from '@opentelemetry/sdk-trace-base';

const provider = new WebTracerProvider();
const exporter = new ZipkinExporter({
  url: 'http://jaeger-collector.observability.svc.cluster.local:9411/api/v2/spans',
});
provider.addSpanProcessor(new SimpleSpanProcessor(exporter));
provider.register();
```

## 6. AWS CloudWatch Integration

### Install CloudWatch Agent

```bash
# Create IAM policy for CloudWatch
curl -O https://s3.amazonaws.com/amazoncloudwatch-agent/amazon_linux/amd64/latest/amazon-cloudwatch-agent.rpm
aws ssm put-parameter --name "/amazon-cloudwatch-agent" --value file://cwagentconfig.json --type String
```

### CloudWatch Agent Configuration

```json
{
  "agent": {
    "metrics_collection_interval": 60,
    "run_as_user": "root"
  },
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/var/log/containers/todo-*.log",
            "log_group_name": "/eks/todo-app/logs",
            "log_stream_name": "{container_name}-{pod_name}"
          }
        ]
      }
    }
  },
  "metrics": {
    "namespace": "EKS/Containers",
    "metrics_collected": {
      "kubernetes": {
        "cluster_name": "my-cluster",
        "enhanced_metrics_collection": true
      }
    }
  }
}
```

### Deploy CloudWatch Agent to EKS

```bash
kubectl apply -f https://raw.githubusercontent.com/aws-samples/amazon-cloudwatch-container-insights/latest/k8s-deployment-manifest-templates/deployment-mode/daemonset/container-insights-monitoring/quickstart/cwagent-fluentd-quickstart.yaml
```

## 7. Alerting Configuration

### Create AlertManager Configuration

```yaml
# alertmanager-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: alertmanager-config
  namespace: monitoring
data:
  alertmanager.yml: |
    global:
      smtp_smarthost: 'smtp.gmail.com:587'
      smtp_from: 'alerts@example.com'
      smtp_auth_username: 'your-email@gmail.com'
      smtp_auth_password: 'your-app-password'

    route:
      group_by: ['alertname', 'severity']
      group_wait: 10s
      group_interval: 10s
      repeat_interval: 1h
      receiver: 'slack-notifications'

    receivers:
    - name: 'slack-notifications'
      slack_configs:
      - api_url: 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'
        channel: '#alerts'
        text: |
          {{ range .Alerts }}
            *Alert:* {{ .Annotations.summary }}
            *Description:* {{ .Annotations.description }}
            *Severity:* {{ .Labels.severity }}
            *Instance:* {{ .Labels.instance }}
          {{ end }}

    inhibit_rules:
    - source_match:
        severity: 'critical'
      target_match:
        severity: 'warning'
      equal: ['alertname', 'dev', 'instance']
```

### Define Prometheus Alerts

```yaml
# prometheus-alerts.yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: todo-app-rules
  labels:
    app: prometheus
spec:
  groups:
  - name: todo-app.rules
    rules:
    - alert: HighErrorRate
      expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
      for: 2m
      labels:
        severity: critical
      annotations:
        summary: "High error rate detected"
        description: "More than 5% of requests are failing for more than 2 minutes"

    - alert: HighLatency
      expr: histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le)) > 2
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "High request latency"
        description: "95th percentile of request latency is higher than 2 seconds"

    - alert: PodDown
      expr: up == 0
      for: 1m
      labels:
        severity: critical
      annotations:
        summary: "Pod is down"
        description: "Pod {{ $labels.pod }} in namespace {{ $labels.namespace }} is down"

    - alert: HighCPUUsage
      expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "High CPU usage"
        description: "CPU usage is higher than 80%"
```

## 8. Custom Grafana Dashboards

### Create Application-Specific Dashboard

```json
{
  "dashboard": {
    "id": null,
    "title": "Todo App Dashboard",
    "tags": ["todo", "application"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "sum(rate(http_requests_total[1m])) by (app)",
            "legendFormat": "{{app}}"
          }
        ],
        "yAxes": [
          {
            "label": "Requests/sec",
            "format": "short"
          }
        ]
      },
      {
        "id": 2,
        "title": "Request Latency",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le, app))",
            "legendFormat": "{{app}}"
          }
        ],
        "yAxes": [
          {
            "label": "Seconds",
            "format": "s"
          }
        ]
      },
      {
        "id": 3,
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "sum(rate(http_requests_total{status=~\"5..\"}[1m])) by (app)",
            "legendFormat": "{{app}}"
          }
        ],
        "yAxes": [
          {
            "label": "Errors/sec",
            "format": "short"
          }
        ]
      }
    ],
    "time": {
      "from": "now-6h",
      "to": "now"
    },
    "refresh": "5s"
  }
}
```

## 9. Log Aggregation and Analysis

### Configure Fluent Bit for Log Processing

```yaml
# fluent-bit-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluent-bit-config
  namespace: logging
data:
  fluent-bit.conf: |
    [SERVICE]
        Flush         1
        Log_Level     info
        Daemon        off
        Parsers_File  parsers.conf
        HTTP_Server   On
        HTTP_Listen   0.0.0.0
        HTTP_Port     2020

    [INPUT]
        Name              tail
        Path              /var/log/containers/todo-*.log
        Parser            docker
        Tag               kube.*
        Refresh_Interval  5
        Mem_Buf_Limit     50MB
        Skip_Long_Lines   On
        DB                /var/log/flb_kube.db

    [FILTER]
        Name                kubernetes
        Match               kube.*
        Kube_URL            https://kubernetes.default.svc:443
        Kube_CA_File        /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
        Kube_Token_File     /var/run/secrets/kubernetes.io/serviceaccount/token
        Kube_Tag_Prefix     kube.var.log.containers.
        Merge_Log           On
        Merge_Log_Key       log_processed
        K8S-Logging.Parser  On
        K8S-Logging.Exclude Off

    [OUTPUT]
        Name            cloudwatch
        Match           *
        region          us-east-1
        log_group_name  todo-app-logs
        log_stream_prefix todo-app-
        auto_create_group true
```

## 10. Testing Checklist

Complete these monitoring validation steps:

```bash
# Verify Prometheus is running
kubectl get pods -n monitoring | grep prometheus

# Check Grafana dashboard access
kubectl get svc -n monitoring | grep grafana

# Verify ServiceMonitors are created
kubectl get servicemonitor -n default

# Check Jaeger deployment
kubectl get pods -n observability | grep jaeger

# Test alert rules
kubectl get prometheusrules -n monitoring

# Verify metrics endpoints are accessible
kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090

# Check CloudWatch logs
aws logs describe-log-groups --log-group-name-prefix /eks/todo-app
```

## 11. Troubleshooting

### Common Monitoring Issues
- **Metrics not appearing**: Verify ServiceMonitor configurations and Prometheus discovery
- **Alerts not firing**: Check AlertManager configuration and Prometheus rule syntax
- **High resource usage**: Optimize metric collection intervals and retention periods
- **Log aggregation delays**: Verify Fluent Bit configuration and buffer sizes

### Performance Optimization
- Adjust scraping intervals based on metric importance
- Implement metric relabeling to reduce cardinality
- Use Prometheus federation for large deployments
- Configure proper storage classes for persistent metrics

### Alert Tuning
- Start with conservative thresholds and adjust based on baseline
- Use recording rules to pre-aggregate frequently queried metrics
- Implement proper alert grouping to avoid notification spam

## 12. Research Notes

### Observability Maturity Model
Start with basic metrics and logs, then progressively add distributed tracing and advanced alerting as the system grows in complexity and criticality.

### Cost Optimization
Monitor and optimize monitoring costs by adjusting retention periods, sampling rates for tracing, and selecting appropriate storage tiers for metrics and logs.

### Self-Healing Systems
Combine monitoring with automated remediation using Kubernetes operators and custom controllers that can respond to metric thresholds and trigger corrective actions.