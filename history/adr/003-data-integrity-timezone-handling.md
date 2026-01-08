# ADR-003: Data Integrity and Timezone Handling

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-25
- **Feature:** ai-reminder-agent
- **Context:** The reminder system must handle two critical data integrity challenges: (1) preventing duplicate reminders to users, which damages trust and appears unprofessional, and (2) correctly handling user timezones to ensure reminders arrive at the expected local time. Both decisions are deeply interconnected—duplicate prevention requires exact datetime matching, while timezone handling requires UTC normalization. These decisions impact database schema, application logic, and user experience.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - Core data model and correctness guarantees
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - Database vs cache, UTC vs local storage
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - Affects database, scheduling, email, and user interface
-->

## Decision

**Use database UNIQUE constraint for duplicate prevention combined with UTC storage and user timezone conversion.**

Implementation details:

### Duplicate Prevention
- **Primary Defense**: PostgreSQL UNIQUE constraint on `(task_id, reminder_datetime)`
- **Secondary Defense**: Application-level check with ±60 second tolerance window
- **Rationale for Dual Defense**:
  - Database constraint prevents race conditions across multiple agent instances (future scalability)
  - Tolerance window handles minor timing variations in scheduler execution

### Timezone Handling
- **Storage**: All `datetime` fields stored in UTC with `TIMESTAMP WITH TIME ZONE`
- **Conversion**: Convert to user's local timezone only for display in emails
- **User Timezone**: Add `timezone` column to `users` table (e.g., "America/New_York")
- **Default Behavior**: Fall back to UTC if user timezone not set
- **Libraries**: Use `pytz` for timezone conversions with IANA timezone database

### Integration Pattern
```python
# Example: Calculate reminder datetime
reminder_datetime_utc = calculate_reminder(task)  # Always in UTC

# Check for duplicates (±60s tolerance)
if duplicate_exists(task.id, reminder_datetime_utc, tolerance=60):
    skip_reminder()

# Convert for email display
user_tz = get_user_timezone(user_id) or "UTC"
reminder_local = reminder_datetime_utc.astimezone(user_tz)
email_body = f"Reminder for {task.title} at {reminder_local:%I:%M %p %Z}"
```

## Consequences

### Positive

**Duplicate Prevention**:
- **Race Condition Safety**: Database constraint prevents duplicates even with multiple agent instances
- **Idempotent Operations**: Duplicate INSERT attempts fail gracefully without crashes
- **Audit Trail**: `reminder_log` table provides complete history of all reminders sent
- **No External Dependencies**: No Redis or cache required for MVP

**Timezone Handling**:
- **Industry Standard**: UTC storage is universal best practice, easy for team to understand
- **DST Compatibility**: pytz handles daylight saving time transitions automatically
- **Migration Friendly**: Adding timezones later doesn't require datetime column changes
- **Testing Simplified**: All test fixtures use UTC, no timezone mocking needed

**Combined Benefits**:
- **Data Consistency**: Single source of truth (database) for both duplicate checks and time storage
- **Debugging Ease**: All logs and database records in consistent timezone (UTC)
- **Future-Proof**: Scales to multi-region deployments without schema changes

### Negative

**Duplicate Prevention**:
- **Strict Matching**: UNIQUE constraint requires exact datetime match (e.g., 14:00:00 vs 14:00:01 are different)
- **Clock Skew Issues**: If system clock drifts, tolerance window may not catch near-duplicates
- **Database Dependency**: Duplicate detection requires database round-trip (adds latency)

**Timezone Handling**:
- **Schema Change Required**: Must add `timezone` column to `users` table
- **User Confusion**: Users may not understand why reminder times show in UTC initially
- **Conversion Overhead**: Every email requires pytz conversion (small performance cost)
- **Maintenance**: IANA timezone database updates needed for new DST rules

**Combined Challenges**:
- **Testing Complexity**: Must test both duplicate prevention and timezone edge cases
- **Partial Failures**: Timezone conversion can fail (invalid timezone string) independently of duplicate checks

## Alternatives Considered

### Alternative 1: Redis Cache for Duplicate Prevention
**Approach**: Store sent reminder keys in Redis with TTL, check cache before sending

**Why Rejected**:
- **External Dependency**: Adds Redis to infrastructure for MVP
- **Cache Eviction Risk**: If key evicted early (memory pressure), duplicate can slip through
- **No Audit Trail**: Redis doesn't provide historical record for debugging
- **Operational Overhead**: Redis cluster management adds complexity
- **Eventual Consistency**: Cache can diverge from database state

**When to Reconsider**: If duplicate checks become database bottleneck at scale (>100k users)

### Alternative 2: Store Times in User's Local Timezone
**Approach**: Store `reminder_time` in user's timezone (e.g., "2025-01-15 14:00 EST")

**Why Rejected**:
- **DST Nightmare**: Daylight saving time transitions create ambiguous times (fall back: 1:30 AM happens twice)
- **Migration Complexity**: If user changes timezone, must recompute all stored times
- **Calculation Errors**: Recurring tasks require complex timezone-aware math
- **Data Portability**: Exporting/importing data requires timezone context
- **Anti-Pattern**: Violates industry best practice (always store UTC)

### Alternative 3: Application-Level Duplicate Check Only (No DB Constraint)
**Approach**: Query `reminder_log` table before sending, skip if found

**Why Rejected**:
- **Race Condition**: Two concurrent processes can both pass check and send duplicate
- **No Enforcement**: Relies on application code correctness, easy to bypass accidentally
- **Testing Gap**: Hard to unit test race conditions reliably
- **Future Scaling**: Breaks when horizontal scaling adds multiple agent instances

**Why Constraint is Better**: Database guarantees atomicity via UNIQUE constraint

### Alternative 4: ISO 8601 String Storage (No Timezone Column)
**Approach**: Store timezone as part of datetime string (e.g., "2025-01-15T14:00:00-05:00")

**Why Rejected**:
- **PostgreSQL Anti-Pattern**: Database has native `TIMESTAMPTZ` type for this
- **Query Performance**: String comparisons slower than native datetime comparisons
- **Indexing Limitations**: Cannot efficiently index and sort string datetimes
- **Parsing Overhead**: Every read requires ISO 8601 parsing

## References

- Feature Spec: `specs/ai-reminder-agent/spec.md` (Section 3.2 "reminder_log table", Section 7 "Timezone Handling")
- Implementation Plan: `specs/ai-reminder-agent/plan.md` (Section "Critical Design Decisions > Decision 3 & 4")
- Related ADRs: None
- Evaluator Evidence: Task 3.7 "Timezone Utilities" and Task 3.5 "Duplicate Checker" in tasks.md

## Database Schema

```sql
-- Duplicate prevention via UNIQUE constraint
CREATE TABLE reminder_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id INTEGER NOT NULL REFERENCES tasks(id),
    reminder_datetime TIMESTAMP WITH TIME ZONE NOT NULL,
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    -- ... other fields ...
    CONSTRAINT unique_task_reminder UNIQUE(task_id, reminder_datetime)
);

-- User timezone support (future enhancement)
ALTER TABLE users ADD COLUMN timezone VARCHAR(50) DEFAULT 'UTC';
-- Example values: 'America/New_York', 'Europe/London', 'Asia/Tokyo'
```

## Edge Cases Handled

1. **Feb 31st Monthly Recurring**: Day doesn't exist → use Feb 28/29
2. **DST Spring Forward**: 2:30 AM doesn't exist → pytz adjusts to 3:30 AM
3. **DST Fall Back**: 1:30 AM happens twice → pytz uses first occurrence
4. **Invalid Timezone**: User sets "Invalid/Zone" → fallback to UTC
5. **Clock Skew**: System clock 30s fast → tolerance window catches it
6. **Leap Seconds**: PostgreSQL TIMESTAMPTZ handles natively
