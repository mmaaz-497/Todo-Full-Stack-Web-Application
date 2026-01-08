# ADR-001: Task Scheduling Architecture

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-25
- **Feature:** ai-reminder-agent
- **Context:** The AI Task Reminder Agent requires a reliable scheduling mechanism to periodically check for tasks needing reminders and process them. The system must balance simplicity for MVP deployment with scalability for future growth (potentially 50k+ users). The scheduler needs to run background jobs every 5 minutes, handle database queries, AI API calls, and email delivery, all while maintaining agent health monitoring.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - Determines deployment complexity and scalability path
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - APScheduler vs Celery + Redis
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - Affects deployment, monitoring, scaling, and operations
-->

## Decision

**Start with APScheduler for MVP, with planned migration to Celery + Redis when scaling requirements exceed 50,000 users.**

Implementation details:
- **Scheduler**: APScheduler (AsyncIOScheduler) running in-process
- **Job Frequency**: Every 5 minutes (configurable via environment variable)
- **Concurrency Model**: Single-process, async/await pattern
- **State Management**: PostgreSQL `agent_state` table for health monitoring
- **Migration Trigger**: When any of the following occur:
  - User base exceeds 50,000
  - Processing time per cycle exceeds 3 minutes
  - Need for horizontal scaling emerges
  - Fault tolerance becomes critical

## Consequences

### Positive

- **Simplicity**: Single Python process, no external message queue required
- **Fast Development**: Minimal setup, immediate productivity for MVP
- **Low Operational Overhead**: No Redis cluster to manage, fewer moving parts
- **Sufficient for MVP**: Handles up to 50,000 users with 5-minute polling
- **Easy Testing**: Unit tests don't require message queue infrastructure
- **Clear Migration Path**: Well-defined criteria for when to upgrade to Celery
- **Cost Effective**: Reduced infrastructure costs during validation phase

### Negative

- **Single Point of Failure**: If agent process crashes, reminders stop until restart
- **No Horizontal Scaling**: Cannot distribute work across multiple workers
- **Limited Fault Tolerance**: Process death = lost in-flight jobs
- **Memory Constraints**: All state held in single process memory
- **Restart Overhead**: Longer startup time as all schedules must be reloaded
- **Future Migration Required**: Will need significant refactoring when scaling beyond MVP

## Alternatives Considered

### Alternative 1: Celery + Redis from Day 1
**Components**: Celery Beat scheduler + Celery workers + Redis message broker

**Why Rejected**:
- **Premature Optimization**: Adds complexity before proving product-market fit
- **Increased Infrastructure**: Requires Redis cluster for production reliability
- **Higher Operational Burden**: Multiple services to monitor (beat, workers, Redis)
- **Slower Development**: More complex local development setup
- **YAGNI Principle**: Don't add complexity until proven necessary
- **Cost**: Additional infrastructure costs without proven user demand

**When to Reconsider**: When user base exceeds 50k or fault tolerance becomes critical

### Alternative 2: Cron + Stateless Script
**Components**: System cron + Python script executed every 5 minutes

**Why Rejected**:
- **No Job State Management**: Cannot track running jobs or prevent overlaps
- **Poor Error Handling**: Cron doesn't provide built-in retry or failure recovery
- **Limited Monitoring**: No visibility into job execution without custom logging
- **Concurrency Issues**: Risk of overlapping executions if job runs longer than interval
- **Not Cloud-Native**: Harder to deploy on containerized platforms (Docker, Kubernetes)

### Alternative 3: Temporal or AWS Step Functions
**Components**: Workflow orchestration platform

**Why Rejected**:
- **Over-Engineering**: Workflow orchestration is overkill for simple 5-minute polling
- **Vendor Lock-In**: AWS Step Functions ties us to AWS ecosystem
- **Complexity**: Steep learning curve for team unfamiliar with workflow engines
- **Cost**: Additional service charges not justified for simple scheduling

## References

- Feature Spec: `specs/ai-reminder-agent/spec.md` (Section 2.3 "Task Scheduler")
- Implementation Plan: `specs/ai-reminder-agent/plan.md` (Section "Critical Design Decisions > Decision 1")
- Related ADRs: None
- Evaluator Evidence: Task breakdown shows MVP timeline of 5 weeks; Celery migration complexity estimated at 1+ week when needed

## Migration Strategy

When triggering conditions are met, migration path:

1. **Phase 1**: Install Redis and Celery alongside APScheduler (dual-run for validation)
2. **Phase 2**: Migrate jobs to Celery tasks, test with staging traffic
3. **Phase 3**: Deploy Celery workers, cut over production traffic
4. **Phase 4**: Remove APScheduler code, monitor for 1 week
5. **Phase 5**: Update documentation and runbooks

Estimated migration effort: 40-60 developer hours
