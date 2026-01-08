# Data Model: Phase V - Advanced Cloud Deployment

**Feature**: Phase V - Advanced Cloud Deployment
**Date**: 2026-01-02
**Status**: Complete

This document defines the database schema extensions and new entities for Phase V event-driven features.

---

## Entity Relationship Overview

```
User (Phase IV - existing)
  ↓ 1:N
Task (Phase IV - extended)
  ↓ 1:1
RecurringTaskState (Phase V - new)

Task
  ↓ 1:N (self-referential)
Task (parent_task_id → id)
```

---

## Task Entity (Extended)

**Table**: `tasks`
**Purpose**: Core todo item with Phase V enhancements for recurring tasks, reminders, priority, and tags

### Schema Changes (Phase V)

| Column Name | Type | Constraints | Description |
|-------------|------|-------------|-------------|
| `priority` | `VARCHAR(10)` | `CHECK (priority IN ('low', 'medium', 'high', 'urgent'))` | Task priority level (nullable) |
| `tags` | `TEXT[]` | PostgreSQL array | User-defined labels for categorization |
| `due_date` | `TIMESTAMPTZ` | Nullable | When task must be completed (timezone-aware) |
| `reminder_offset` | `INTERVAL` | Nullable | Time before due_date to send reminder (e.g., '1 hour', '1 day') |
| `recurrence_rule` | `JSONB` | Nullable | Recurrence pattern specification (see schema below) |
| `parent_task_id` | `INTEGER` | `REFERENCES tasks(id) ON DELETE CASCADE` | Links recurring task occurrences to original task |

### Existing Columns (Phase IV)

| Column Name | Type | Constraints | Description |
|-------------|------|-------------|-------------|
| `id` | `SERIAL` | `PRIMARY KEY` | Auto-incrementing task ID |
| `user_id` | `INTEGER` | `NOT NULL, REFERENCES users(id)` | Task owner |
| `title` | `VARCHAR(200)` | `NOT NULL` | Task title |
| `description` | `TEXT` | Nullable | Task description |
| `status` | `VARCHAR(20)` | `NOT NULL, DEFAULT 'pending'` | Task status (pending, in_progress, completed) |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL, DEFAULT NOW()` | Creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL, DEFAULT NOW()` | Last update timestamp |
| `completed_at` | `TIMESTAMPTZ` | Nullable | Completion timestamp |

### Recurrence Rule JSONB Schema

```json
{
  "frequency": "daily | weekly | monthly",
  "interval": 1,
  "days_of_week": [0, 1, 2, 3, 4, 5, 6],
  "day_of_month": 15,
  "end_date": "2026-12-31T23:59:59Z"
}
```

**Field Definitions**:
- `frequency` (required): Recurrence pattern type
- `interval` (required): Every N days/weeks/months (default: 1)
- `days_of_week` (optional): For weekly recurrence, 0=Sunday, 6=Saturday
- `day_of_month` (optional): For monthly recurrence, 1-31
- `end_date` (optional): Stop generating occurrences after this date

**Examples**:
- Daily: `{"frequency": "daily", "interval": 1}`
- Every Monday: `{"frequency": "weekly", "interval": 1, "days_of_week": [1]}`
- Every 2 weeks on Mon/Wed/Fri: `{"frequency": "weekly", "interval": 2, "days_of_week": [1, 3, 5]}`
- Monthly on 15th: `{"frequency": "monthly", "interval": 1, "day_of_month": 15}`

### Indexes

```sql
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_tags ON tasks USING GIN(tags);  -- GIN index for array containment
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
CREATE INDEX idx_tasks_parent_id ON tasks(parent_task_id);
```

**Performance Rationale**:
- `idx_tasks_priority`: Fast filtering by priority (common query pattern)
- `idx_tasks_tags`: GIN index for array `@>` operator (tag search)
- `idx_tasks_due_date`: Range queries for upcoming tasks
- `idx_tasks_parent_id`: Lookup child occurrences of recurring tasks

---

## RecurringTaskState Entity (New)

**Table**: `recurring_task_state`
**Purpose**: Tracks last generated occurrence for recurring tasks to prevent duplicates

### Schema

| Column Name | Type | Constraints | Description |
|-------------|------|-------------|-------------|
| `task_id` | `INTEGER` | `PRIMARY KEY, REFERENCES tasks(id) ON DELETE CASCADE` | Links to parent recurring task |
| `last_generated_at` | `TIMESTAMPTZ` | `NOT NULL` | When last occurrence was generated |
| `next_occurrence_due` | `TIMESTAMPTZ` | Nullable | Calculated next occurrence due date (cached) |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL, DEFAULT NOW()` | Record creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL, DEFAULT NOW()` | Record last update timestamp |

### Usage Pattern

**On Task Completion** (Recurring Task Service):
```python
# Check if task is recurring
if task.recurrence_rule and task.status == "completed":
    # Get or create state
    state = await db.get_recurring_task_state(task.id)

    # Calculate next occurrence
    next_due = calculate_next_occurrence(
        recurrence_rule=task.recurrence_rule,
        last_completed_at=task.completed_at
    )

    # Update state
    state.last_generated_at = datetime.utcnow()
    state.next_occurrence_due = next_due
    await db.save(state)

    # Create next occurrence
    new_task = Task(
        user_id=task.user_id,
        title=task.title,
        description=task.description,
        priority=task.priority,
        tags=task.tags,
        due_date=next_due,
        parent_task_id=task.id,  # Link to parent
        recurrence_rule=task.recurrence_rule  # Inherit rule
    )
    await db.save(new_task)
```

---

## Task Event Entity (Not Persisted)

**Purpose**: Event payload published to Kafka `task-events` topic

### Schema

```json
{
  "event_id": "uuid-v4",
  "schema_version": "1.0",
  "event_type": "task.created | task.updated | task.deleted | task.completed",
  "timestamp": "2026-01-02T10:00:00Z",
  "task_id": 123,
  "user_id": 456,
  "task_data": {
    "title": "Complete project proposal",
    "description": "Finalize Q1 2026 project proposal",
    "status": "pending",
    "priority": "high",
    "tags": ["work", "urgent"],
    "due_date": "2026-01-10T17:00:00Z",
    "reminder_offset": "1 day",
    "recurrence_rule": {
      "frequency": "weekly",
      "interval": 1,
      "days_of_week": [1]
    },
    "parent_task_id": null,
    "created_at": "2026-01-02T10:00:00Z",
    "updated_at": "2026-01-02T10:00:00Z",
    "completed_at": null
  }
}
```

**Kafka Topic**: `task-events`
**Producers**: api-service (Chat API)
**Consumers**: recurring-task-service, audit-service

---

## Reminder Event Entity (Not Persisted)

**Purpose**: Event payload published to Kafka `reminders` topic

### Schema

```json
{
  "event_id": "uuid-v4",
  "schema_version": "1.0",
  "event_type": "reminder.due",
  "timestamp": "2026-01-09T17:00:00Z",
  "task_id": 123,
  "user_id": 456,
  "due_date": "2026-01-10T17:00:00Z",
  "task_title": "Complete project proposal",
  "task_description": "Finalize Q1 2026 project proposal",
  "notification_channels": ["email"],
  "reminder_time": "2026-01-09T17:00:00Z"
}
```

**Kafka Topic**: `reminders`
**Producers**: api-service (via Dapr Jobs API callback)
**Consumers**: notification-service, audit-service

---

## Task Update Event Entity (Not Persisted)

**Purpose**: Lightweight event for WebSocket real-time synchronization

### Schema

```json
{
  "event_id": "uuid-v4",
  "schema_version": "1.0",
  "event_type": "task.sync",
  "timestamp": "2026-01-02T10:05:00Z",
  "user_id": 456,
  "operation": "create | update | delete",
  "task_id": 123,
  "task_snapshot": {
    "title": "Complete project proposal",
    "status": "in_progress",
    "updated_at": "2026-01-02T10:05:00Z"
  }
}
```

**Kafka Topic**: `task-updates`
**Producers**: api-service, recurring-task-service
**Consumers**: websocket-sync-service, audit-service

---

## Audit Log Entry Entity (New)

**Table**: `audit_logs`
**Purpose**: Compliance and debugging record of all system events

### Schema

| Column Name | Type | Constraints | Description |
|-------------|------|-------------|-------------|
| `log_id` | `BIGSERIAL` | `PRIMARY KEY` | Auto-incrementing log ID |
| `event_id` | `UUID` | `NOT NULL` | Original event ID from Kafka |
| `user_id` | `INTEGER` | Nullable | User who triggered action |
| `action_type` | `VARCHAR(50)` | `NOT NULL` | Event type (task.created, reminder.due, etc.) |
| `resource_type` | `VARCHAR(50)` | `NOT NULL` | Resource affected (task, user, etc.) |
| `resource_id` | `INTEGER` | Nullable | ID of affected resource |
| `payload` | `JSONB` | `NOT NULL` | Full event payload |
| `timestamp` | `TIMESTAMPTZ` | `NOT NULL` | Event timestamp |
| `source_service` | `VARCHAR(100)` | `NOT NULL` | Service that published event |

### Indexes

```sql
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action_type ON audit_logs(action_type);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp DESC);
CREATE INDEX idx_audit_logs_resource ON audit_logs(resource_type, resource_id);
```

**Retention Policy**: 90 days (automated cleanup job)

---

## WebSocket Connection Entity (Not Persisted)

**Purpose**: Active WebSocket connections tracked in Dapr State

### Dapr State Key Format
```
websocket_connection_{user_id}_{connection_id}
```

### Value Schema

```json
{
  "connection_id": "uuid-v4",
  "user_id": 456,
  "session_token": "jwt-token-string",
  "connected_at": "2026-01-02T10:00:00Z",
  "last_ping_at": "2026-01-02T10:05:00Z"
}
```

**TTL**: 1 hour (auto-expire stale connections)

---

## DLQ Event Entity (Not Persisted)

**Purpose**: Failed events captured for manual inspection

### Schema

```json
{
  "dlq_id": "uuid-v4",
  "original_event_id": "uuid-v4",
  "original_topic": "task-events",
  "original_event": { /* full original event */ },
  "error_context": {
    "error_message": "Database connection timeout",
    "stack_trace": "...",
    "retry_count": 5,
    "first_attempt_at": "2026-01-02T10:00:00Z",
    "last_attempt_at": "2026-01-02T10:05:30Z",
    "consumer_service": "recurring-task-service",
    "consumer_pod": "recurring-task-service-7d8f9-xkj2p"
  },
  "timestamp": "2026-01-02T10:05:30Z"
}
```

**Kafka Topic**: `dlq-events`
**Retention**: 30 days

---

## Query Patterns

### Find Upcoming Tasks with Reminders

```sql
SELECT t.id, t.title, t.due_date, t.reminder_offset
FROM tasks t
WHERE t.due_date IS NOT NULL
  AND t.reminder_offset IS NOT NULL
  AND t.status != 'completed'
  AND (t.due_date - t.reminder_offset) <= NOW() + INTERVAL '1 hour'
  AND (t.due_date - t.reminder_offset) > NOW()
ORDER BY t.due_date;
```

### Search Tasks by Tags

```sql
SELECT *
FROM tasks
WHERE tags @> ARRAY['work', 'urgent']::TEXT[]  -- Contains both tags (AND)
  AND user_id = 456
ORDER BY priority DESC, due_date ASC;
```

### Find All Occurrences of Recurring Task

```sql
SELECT *
FROM tasks
WHERE parent_task_id = 123  -- Original recurring task ID
ORDER BY created_at DESC;
```

### Get Audit Trail for User

```sql
SELECT log_id, action_type, resource_type, resource_id, timestamp
FROM audit_logs
WHERE user_id = 456
  AND timestamp >= NOW() - INTERVAL '30 days'
ORDER BY timestamp DESC
LIMIT 100;
```

---

## Migration Strategy

### Phase IV → Phase V Schema Migration

**Alembic Migration**: `003_add_phase_v_fields.sql`

```sql
-- Add new columns to existing tasks table
ALTER TABLE tasks ADD COLUMN priority VARCHAR(10) CHECK (priority IN ('low', 'medium', 'high', 'urgent'));
ALTER TABLE tasks ADD COLUMN tags TEXT[] DEFAULT '{}';
ALTER TABLE tasks ADD COLUMN due_date TIMESTAMPTZ;
ALTER TABLE tasks ADD COLUMN reminder_offset INTERVAL;
ALTER TABLE tasks ADD COLUMN recurrence_rule JSONB;
ALTER TABLE tasks ADD COLUMN parent_task_id INTEGER REFERENCES tasks(id) ON DELETE CASCADE;

-- Create indexes for performance
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_tags ON tasks USING GIN(tags);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
CREATE INDEX idx_tasks_parent_id ON tasks(parent_task_id);

-- Create new recurring_task_state table
CREATE TABLE recurring_task_state (
  task_id INTEGER PRIMARY KEY REFERENCES tasks(id) ON DELETE CASCADE,
  last_generated_at TIMESTAMPTZ NOT NULL,
  next_occurrence_due TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create new audit_logs table
CREATE TABLE audit_logs (
  log_id BIGSERIAL PRIMARY KEY,
  event_id UUID NOT NULL,
  user_id INTEGER,
  action_type VARCHAR(50) NOT NULL,
  resource_type VARCHAR(50) NOT NULL,
  resource_id INTEGER,
  payload JSONB NOT NULL,
  timestamp TIMESTAMPTZ NOT NULL,
  source_service VARCHAR(100) NOT NULL
);

-- Create indexes for audit_logs
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action_type ON audit_logs(action_type);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp DESC);
CREATE INDEX idx_audit_logs_resource ON audit_logs(resource_type, resource_id);
```

**Rollback**:
```sql
DROP INDEX IF EXISTS idx_audit_logs_resource;
DROP INDEX IF EXISTS idx_audit_logs_timestamp;
DROP INDEX IF EXISTS idx_audit_logs_action_type;
DROP INDEX IF EXISTS idx_audit_logs_user_id;
DROP TABLE IF EXISTS audit_logs;
DROP TABLE IF EXISTS recurring_task_state;
DROP INDEX IF EXISTS idx_tasks_parent_id;
DROP INDEX IF EXISTS idx_tasks_due_date;
DROP INDEX IF EXISTS idx_tasks_tags;
DROP INDEX IF EXISTS idx_tasks_priority;
ALTER TABLE tasks DROP COLUMN IF EXISTS parent_task_id;
ALTER TABLE tasks DROP COLUMN IF EXISTS recurrence_rule;
ALTER TABLE tasks DROP COLUMN IF EXISTS reminder_offset;
ALTER TABLE tasks DROP COLUMN IF EXISTS due_date;
ALTER TABLE tasks DROP COLUMN IF EXISTS tags;
ALTER TABLE tasks DROP COLUMN IF EXISTS priority;
```

---

## Summary

| Entity | Type | Purpose | Persistence |
|--------|------|---------|-------------|
| Task | Extended Table | Core todo item with Phase V fields | PostgreSQL |
| RecurringTaskState | New Table | Tracks recurring task generation | PostgreSQL |
| TaskEvent | Event | Kafka event for task changes | Kafka (7 days) |
| ReminderEvent | Event | Kafka event for reminders | Kafka (7 days) |
| TaskUpdateEvent | Event | Kafka event for WebSocket sync | Kafka (1 day) |
| AuditLogEntry | New Table | Compliance and debugging logs | PostgreSQL (90 days) |
| WebSocketConnection | State | Active WebSocket connections | Dapr State (1 hour TTL) |
| DLQEvent | Event | Failed event capture | Kafka (30 days) |

---

**Next Steps**: Use this data model to guide database migration (Phase 2) and event schema implementation (Phase 3).
