# Cloud Portability Intelligence

## Skill Name
Multi-Cloud Portability and Vendor Lock-In Prevention

## Scope
Design applications that run on any cloud provider (Azure, AWS, GCP, Oracle, on-premises) without code changes, preventing vendor lock-in through abstraction layers and portable patterns.

## Trigger Conditions

Apply this skill when:
- Designing new cloud-native applications
- Choosing cloud services and APIs
- Implementing infrastructure-as-code
- Managing secrets, storage, or messaging
- Making architectural decisions with cloud implications
- Planning disaster recovery or multi-cloud strategy
- Evaluating vendor-specific vs portable solutions

## Core Intelligence Rules

### 1. Abstraction Layer Mandate
**Rule**: Application code must never call cloud-specific APIs directly. Use abstraction layers.

**Abstraction Strategy**:
```
Application Code
      ↓
Abstraction Layer (Dapr, Terraform, Helm)
      ↓
Cloud-Specific Implementation
```

**Enforcement**:
```
✓ GOOD: Dapr Secrets API → Azure Key Vault / AWS Secrets Manager / GCP Secret Manager
✗ BAD:  boto3.secretsmanager.get_secret() hardcoded in application
```

### 2. Kubernetes as Portability Foundation
**Rule**: Use Kubernetes as the universal runtime. If it runs on Kubernetes, it runs anywhere.

**Portable Stack**:
- **Compute**: Kubernetes pods (not EC2, VMs, Cloud Functions)
- **Storage**: Persistent Volumes (not EBS, Azure Disks directly)
- **Networking**: Kubernetes Services (not cloud-specific load balancers in code)
- **Configuration**: ConfigMaps/Secrets (not Parameter Store, App Configuration)

**Cloud Differences Handled By**:
- Storage classes (map to cloud-specific volume types)
- Load balancer annotations (map to cloud LB implementations)
- Ingress controllers (map to cloud routing)

### 3. Infrastructure-as-Code Portability
**Rule**: Use multi-cloud IaC tools (Terraform, Pulumi). Avoid cloud-specific tools in shared components.

**IaC Tool Selection**:
```
IF provisioning Kubernetes + managed services:
   Use Terraform with cloud-specific providers
   Keep Kubernetes manifests/Helm charts cloud-agnostic
ELSE IF pure Kubernetes:
   Use Helm, Kustomize (100% portable)
ELSE IF single cloud with tight integration:
   Cloud-specific tools acceptable (ARM, CloudFormation)
   BUT isolate from application code
```

**Pattern**:
```
terraform/
  modules/
    kubernetes/        # Portable
    azure/            # Cloud-specific (AKS, Key Vault)
    aws/              # Cloud-specific (EKS, Secrets Manager)
    gcp/              # Cloud-specific (GKE, Secret Manager)
  environments/
    dev/
    prod/
```

### 4. Managed Service Abstraction
**Rule**: Use Dapr components to abstract managed services. Switch backends without code changes.

**Managed Service Mapping**:

| Concern | Abstraction | Azure | AWS | GCP | On-Prem |
|---------|-------------|-------|-----|-----|---------|
| Pub/Sub | Dapr Pub/Sub | Service Bus | SNS/SQS | Pub/Sub | Kafka |
| State | Dapr State | Cosmos DB | DynamoDB | Firestore | PostgreSQL |
| Secrets | Dapr Secrets | Key Vault | Secrets Mgr | Secret Mgr | Kubernetes |
| Blob Storage | Dapr Binding | Blob Storage | S3 | Cloud Storage | MinIO |
| Jobs | Dapr Jobs | N/A | N/A | N/A | Built-in |

**Application Impact**: Zero. Only Dapr component YAML changes.

### 5. Database Portability Strategy
**Rule**: Use portable databases (PostgreSQL, MongoDB) over cloud-native databases.

**Decision Matrix**:
```
IF cloud-agnostic requirement:
   Use PostgreSQL (Neon Serverless, Azure DB, RDS, Cloud SQL)
   OR MongoDB (Atlas multi-cloud)
ELSE IF cloud-specific acceptable AND unique value:
   Azure → Cosmos DB
   AWS → DynamoDB
   GCP → Firestore
   BUT accept migration cost if cloud changes
```

**Portable Database Pattern**:
- Use standard SQL (PostgreSQL dialect)
- Avoid cloud-specific extensions (unless behind feature flag)
- Use ORMs for further abstraction (SQLAlchemy, Prisma)

### 6. Configuration-Driven Cloud Differences
**Rule**: Cloud-specific differences live in configuration files, not application code.

**Pattern**:
```yaml
# Helm values-azure.yaml
cloudProvider: azure
storage:
  class: managed-premium
ingress:
  annotations:
    kubernetes.io/ingress.class: azure/application-gateway

# Helm values-aws.yaml
cloudProvider: aws
storage:
  class: gp3
ingress:
  annotations:
    kubernetes.io/ingress.class: alb
```

**Application Code**:
```python
# No cloud-specific logic
# All configuration via environment variables
```

### 7. Observability Portability
**Rule**: Use cloud-agnostic observability tools or standards.

**Portable Observability Stack**:
- **Metrics**: Prometheus (de facto standard)
- **Logs**: Fluent Bit → cloud-agnostic backend
- **Traces**: OpenTelemetry → Jaeger, Zipkin, or cloud backend
- **Dashboards**: Grafana

**Cloud Integration**:
```
Prometheus → Azure Monitor (via remote write)
           → CloudWatch (via remote write)
           → Cloud Monitoring (via remote write)
```

**Application**: Uses OpenTelemetry SDK (portable), backend configured in infra.

### 8. Authentication and Authorization Portability
**Rule**: Use standards (OAuth 2.0, OIDC) over cloud-specific identity systems.

**Portable Auth Pattern**:
```
Application → OAuth 2.0 / OIDC
              ↓
Identity Provider (configurable):
- Azure AD (B2C)
- AWS Cognito
- Google Identity
- Keycloak (self-hosted)
```

**Configuration**:
```yaml
auth:
  issuer: https://login.microsoftonline.com/{tenant}/v2.0  # Azure
  # OR
  issuer: https://cognito-idp.{region}.amazonaws.com/{pool}  # AWS
```

**Application Code**: Validates JWT, doesn't care about issuer.

### 9. Cost Optimization Through Portability
**Rule**: Design for minimal cloud resources. Start with free tiers, scale as needed.

**Free Tier Targets**:
- **Compute**: 3 nodes × 2 vCPU (within AKS/GKE/EKS free tiers)
- **Database**: Neon Serverless free tier (0.5 GB storage, 100 hours compute)
- **Kafka**: Redpanda Cloud free tier OR Upstash Kafka
- **Storage**: Minimal usage (logs, backups)

**Portability Benefit**: Switch to cheaper cloud if costs increase.

### 10. Disaster Recovery and Multi-Cloud
**Rule**: Design active-passive or active-active multi-cloud for critical systems.

**Multi-Cloud Patterns**:
- **Active-Passive**: Primary cloud, failover to secondary
- **Active-Active**: Traffic split across clouds (complex, expensive)
- **Development Multi-Cloud**: Dev on Azure, Prod on AWS (cost optimization)

**Requirements for Multi-Cloud**:
- Infrastructure-as-code for both clouds
- Data replication strategy (database, object storage)
- DNS-based failover (Route 53, Azure Traffic Manager, Cloud DNS)
- Tested failover process

## Anti-Patterns to Avoid

### ❌ Cloud SDK in Application Code
**Anti-Pattern**: Using `boto3`, `azure-sdk`, `google-cloud-*` in application business logic.
**Fix**: Use Dapr abstractions or isolate cloud SDK behind interface.

### ❌ Cloud-Specific Database Features
**Anti-Pattern**: Using DynamoDB streams, Cosmos DB change feed in application.
**Fix**: Use portable patterns (polling, event sourcing) or accept lock-in with migration plan.

### ❌ Hardcoded Cloud Endpoints
**Anti-Pattern**: `s3.amazonaws.com` hardcoded in application.
**Fix**: Configuration-driven endpoints, use Dapr bindings.

### ❌ Cloud-Specific Annotations Everywhere
**Anti-Pattern**: Azure-specific annotations in core Kubernetes manifests.
**Fix**: Helm templating with conditional annotations based on cloud provider.

### ❌ Vendor Lock-In for Convenience
**Anti-Pattern**: "Lambda is easy, let's use it" without considering portability.
**Fix**: Evaluate Kubernetes Jobs or Dapr Jobs for portable alternative.

### ❌ No Cloud Abstraction Strategy
**Anti-Pattern**: Building on one cloud without portability plan.
**Fix**: Use Dapr, Kubernetes, and portable services from day one.

### ❌ Ignoring Exit Costs
**Anti-Pattern**: Storing TBs in proprietary format, no export strategy.
**Fix**: Plan data export, use standard formats (Parquet, CSV, JSON).

## Decision Heuristics

### When to Accept Cloud Lock-In
```
IF (unique cloud feature provides 10x value)
   AND (migration cost acceptable OR low likelihood of cloud switch)
   AND (feature isolated behind interface)
THEN accept cloud-specific implementation
ELSE use portable alternative
```

**Examples Where Lock-In Acceptable**:
- Managed Kubernetes (AKS, EKS, GKE) → core platform
- Managed databases (Cloud SQL, RDS) → Postgres compatible
- Identity (Azure AD, Cognito) → OAuth/OIDC compatible

**Examples Where Lock-In NOT Acceptable**:
- Lambda → Use Kubernetes Jobs instead
- DynamoDB → Use Postgres or portable NoSQL
- S3-specific APIs → Use Dapr bindings

### Cloud Provider Selection
```
IF team expertise AND existing infrastructure:
   Use familiar cloud
ELSE IF cost-sensitive:
   Compare total cost (compute + data transfer + managed services)
   Choose lowest for workload
ELSE IF compliance requirements:
   Filter clouds by region/compliance
ELSE:
   Default to AKS (good Dapr integration) or GKE (mature Kubernetes)
```

### Managed vs Self-Hosted Services
```
IF (free tier available AND sufficient):
   Use managed service
ELSE IF (cost > self-hosted + maintenance):
   Self-host on Kubernetes
ELSE IF (managed service is cloud-agnostic):
   Use managed (e.g., MongoDB Atlas, Neon, Upstash)
ELSE:
   Managed service with portability plan
```

### Database Selection for Portability
```
IF relational data:
   Use PostgreSQL (Neon, Supabase, Cloud SQL, RDS, Azure DB)
ELSE IF document store:
   Use MongoDB (Atlas multi-cloud)
ELSE IF key-value with cloud flexibility:
   Use Redis (Upstash, managed Redis on any cloud)
ELSE IF time-series:
   Use TimescaleDB (Postgres extension, portable)
```

## Portability Validation Checklist

Before committing to cloud architecture:
- [ ] No cloud-specific SDKs in application code (except behind abstraction)
- [ ] Dapr components used for pub/sub, state, secrets
- [ ] Database is portable (PostgreSQL, MongoDB) or export plan exists
- [ ] Infrastructure-as-code supports multiple clouds (Terraform modules)
- [ ] Kubernetes manifests/Helm charts are cloud-agnostic
- [ ] Configuration differences handled via values files, not code
- [ ] Observability uses standards (Prometheus, OpenTelemetry)
- [ ] Authentication uses OAuth/OIDC standards
- [ ] No hardcoded cloud endpoints in application
- [ ] Cost model includes egress and data transfer
- [ ] Exit strategy documented (data export, migration playbook)
- [ ] Multi-cloud tested (at least dev on one cloud, local on another)

## Cloud Provider Comparison Matrix

### Kubernetes Offerings
| Feature | Azure (AKS) | AWS (EKS) | GCP (GKE) | Oracle (OKE) |
|---------|-------------|-----------|-----------|--------------|
| Free Control Plane | ✓ | ✗ ($0.10/hr) | ✓ (Autopilot) | ✓ |
| Dapr Integration | Excellent | Good | Good | Good |
| Node Pricing | Competitive | Higher | Competitive | Lower |
| Ease of Use | High | Medium | High | Medium |

### Managed Database (PostgreSQL)
| Feature | Azure DB | RDS | Cloud SQL | Oracle DB |
|---------|----------|-----|-----------|-----------|
| Pricing | Medium | Medium | Medium | Higher |
| Free Tier | ✗ | ✗ | ✗ | ✗ |
| Postgres Compatibility | High | High | High | Medium |

**Recommendation**: Neon Serverless (cloud-agnostic, generous free tier)

### Kafka/Messaging
| Service | Azure | AWS | GCP | Portable |
|---------|-------|-----|-----|----------|
| Managed | Event Hubs | MSK | Pub/Sub | Redpanda Cloud |
| Dapr Support | ✓ | ✓ | ✓ | ✓ |
| Free Tier | ✗ | ✗ | ✗ | ✓ (5GB) |

**Recommendation**: Redpanda Cloud (portable, free tier)

## Migration Patterns

### Migrating Between Clouds

**Phase 1: Dual Deployment**
1. Deploy to second cloud in parallel
2. Replicate data (database, object storage)
3. Test functionality

**Phase 2: Traffic Shift**
1. Route 10% traffic to new cloud (DNS weighted routing)
2. Monitor metrics, errors
3. Gradually increase to 50%, then 100%

**Phase 3: Decommission**
1. Stop data replication
2. Archive data from old cloud
3. Delete resources

**Estimated Effort**: 2-4 weeks for well-architected portable application

### Lock-In Recovery

If locked into cloud-specific service:

**Assess**:
- What percentage of codebase uses cloud-specific APIs?
- What is migration effort estimate?

**Refactor**:
1. Create abstraction interface
2. Implement cloud-specific adapter
3. Implement portable adapter (Dapr, standard DB)
4. Switch via configuration

**Example**: DynamoDB → PostgreSQL
- Create repository interface
- Implement DynamoDB adapter (existing code)
- Implement PostgreSQL adapter
- Deploy PostgreSQL, migrate data
- Switch adapter via config
- Remove DynamoDB adapter

## Cost Optimization via Portability

**Leverage Competitive Pricing**:
- Run cost analysis every 6 months
- Compare: Compute hours, data transfer, storage
- Switch if savings > migration cost

**Use Free Tiers Strategically**:
- Development: Cloud with best free tier (GCP, Oracle)
- Production: Cloud with best production pricing
- No code changes needed (portable architecture)

**Spot/Preemptible Instances**:
- All clouds offer 70-90% discounts for interruptible workloads
- Kubernetes handles pod eviction gracefully
- Use for stateless services (APIs, workers)
