# AI Task Reminder Agent - Implementation Tasks

**Feature**: AI Task Reminder Agent
**Version**: 1.0.0
**Date**: 2025-12-25
**Status**: Ready for Implementation

---

## Task Execution Order

This document provides atomic, dependency-ordered tasks for implementing the AI Task Reminder Agent. Tasks are organized into 8 categories and numbered for sequential execution.

**Legend**:
- 🔴 **Blocker**: Must complete before dependent tasks
- 🟡 **Important**: Core functionality
- 🟢 **Enhancement**: Non-critical improvements
- 🔵 **Testing**: Validation tasks

---

## Category 1: Database Layer

### Task 1.1: Create Database Migration Script 🔴

**Priority**: Critical
**Estimated Effort**: 30 minutes
**Dependencies**: None

**Description**:
Create SQL migration script to add `reminder_log` and `agent_state` tables with proper indexes and constraints.

**Inputs**:
- Database schema design from `specs/ai-reminder-agent/plan.md`
- Existing `tasks` table schema from `backend/models.py`

**Steps**:
1. Create file `backend/migrations/001_add_reminder_tables.sql`
2. Add `reminder_log` table with columns:
   - `id` (UUID, primary key)
   - `task_id` (FK to tasks.id)
   - `user_id` (VARCHAR)
   - `reminder_datetime` (TIMESTAMPTZ)
   - `sent_at` (TIMESTAMPTZ)
   - `email_to`, `email_subject`, `email_body` (TEXT)
   - `delivery_status` (VARCHAR: sent/failed/bounced/retrying)
   - `error_message`, `retry_count`, `next_retry_at`
3. Add UNIQUE constraint on `(task_id, reminder_datetime)`
4. Create indexes on `task_id`, `user_id`, `delivery_status`, `sent_at`
5. Add `agent_state` table with columns:
   - `id`, `last_check_at`, `tasks_processed`, `reminders_sent`
   - `errors_count`, `status`, `metadata` (JSONB)
6. Add table comments for documentation

**Outputs**:
- `backend/migrations/001_add_reminder_tables.sql`

**Acceptance Criteria**:
- [ ] SQL script is valid PostgreSQL syntax
- [ ] UNIQUE constraint prevents duplicate reminders
- [ ] Indexes optimize common queries
- [ ] ON DELETE CASCADE maintains referential integrity

**Verification**:
```bash
# Dry run (check syntax)
psql $DATABASE_URL --dry-run < backend/migrations/001_add_reminder_tables.sql

# Verify tables created
psql $DATABASE_URL -c "SELECT table_name FROM information_schema.tables WHERE table_name IN ('reminder_log', 'agent_state');"
```

---

### Task 1.2: Run Database Migration 🔴

**Priority**: Critical
**Estimated Effort**: 15 minutes
**Dependencies**: Task 1.1

**Description**:
Execute migration script on Neon database and verify tables created.

**Inputs**:
- `backend/migrations/001_add_reminder_tables.sql`
- `DATABASE_URL` environment variable

**Steps**:
1. Backup current database (optional but recommended)
2. Run migration: `psql $DATABASE_URL < backend/migrations/001_add_reminder_tables.sql`
3. Verify tables exist
4. Verify indexes created
5. Insert test record to verify constraints

**Outputs**:
- New tables in Neon database: `reminder_log`, `agent_state`

**Acceptance Criteria**:
- [ ] Both tables created successfully
- [ ] All indexes present
- [ ] UNIQUE constraint prevents duplicate inserts
- [ ] Foreign key constraint works (delete task → cascade to reminder_log)

**Verification**:
```sql
-- Check tables
\dt reminder_log agent_state

-- Check indexes
SELECT indexname FROM pg_indexes WHERE tablename = 'reminder_log';

-- Test UNIQUE constraint
INSERT INTO reminder_log (task_id, user_id, reminder_datetime, email_to, email_subject, email_body)
VALUES (1, 'user123', NOW(), 'test@example.com', 'Test', 'Test');

-- Should fail (duplicate)
INSERT INTO reminder_log (task_id, user_id, reminder_datetime, email_to, email_subject, email_body)
VALUES (1, 'user123', NOW(), 'test@example.com', 'Test', 'Test');
```

---

### Task 1.3: Create SQLModel for ReminderLog 🟡

**Priority**: High
**Estimated Effort**: 20 minutes
**Dependencies**: Task 1.2

**Description**:
Create SQLModel class for `reminder_log` table with proper field types and validation.

**Inputs**:
- Database schema from Task 1.1
- `backend/models.py` as reference

**Steps**:
1. Create file `reminder-agent/models/reminder_log.py`
2. Define `DeliveryStatus` enum (SENT, FAILED, BOUNCED, RETRYING)
3. Create `ReminderLog` SQLModel class with fields matching database
4. Add type hints for all fields
5. Set default values (e.g., `delivery_status="sent"`)

**Outputs**:
- `reminder-agent/models/reminder_log.py`

**Acceptance Criteria**:
- [ ] All database columns mapped to model fields
- [ ] Field types match database types (UUID→str, TIMESTAMPTZ→datetime)
- [ ] DeliveryStatus enum matches database constraint
- [ ] Default values set appropriately

**Code Reference**:
```python
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class DeliveryStatus(str, Enum):
    SENT = "sent"
    FAILED = "failed"
    BOUNCED = "bounced"
    RETRYING = "retrying"

class ReminderLog(SQLModel, table=True):
    __tablename__ = "reminder_log"

    id: Optional[str] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="tasks.id", index=True)
    # ... (complete implementation in plan.md)
```

---

### Task 1.4: Create SQLModel for AgentState 🟡

**Priority**: High
**Estimated Effort**: 15 minutes
**Dependencies**: Task 1.2

**Description**:
Create SQLModel class for `agent_state` table to track agent health.

**Inputs**:
- Database schema from Task 1.1

**Steps**:
1. Create file `reminder-agent/models/agent_state.py`
2. Define `AgentStatus` enum (INITIALIZED, RUNNING, PAUSED, ERROR)
3. Create `AgentState` SQLModel with JSONB metadata field
4. Add helper methods (e.g., `is_healthy()`)

**Outputs**:
- `reminder-agent/models/agent_state.py`

**Acceptance Criteria**:
- [ ] AgentStatus enum matches database values
- [ ] JSONB field uses PostgreSQL dialect
- [ ] Default values set for counters

**Code Reference**: See `plan.md` Phase 1, Step 1.1.2

---

### Task 1.5: Create Task Query Service 🟡

**Priority**: High
**Estimated Effort**: 45 minutes
**Dependencies**: Task 1.3, Task 1.4

**Description**:
Implement `TaskReader` service to query tasks needing reminders with efficient SQL.

**Inputs**:
- `backend/models.py` (Task model)
- Reminder lookahead window from config

**Steps**:
1. Create file `reminder-agent/services/task_reader.py`
2. Implement `get_tasks_needing_reminders()` method
3. Build SQL query filtering:
   - `completed = false`
   - `reminder_time IS NOT NULL`
   - Tasks within lookahead window
4. Add in-memory filtering for complex recurrence logic
5. Implement `get_user_email()` method (placeholder for Better Auth)

**Outputs**:
- `reminder-agent/services/task_reader.py`

**Acceptance Criteria**:
- [ ] Returns only incomplete tasks with reminders
- [ ] Filters tasks within lookahead window (default 5 min)
- [ ] Handles database connection errors gracefully
- [ ] Logs query performance metrics

**Test Case**:
```python
# Should return tasks with reminder_time in next 5 minutes
now = datetime.utcnow()
tasks = TaskReader.get_tasks_needing_reminders()
assert all(task.reminder_time <= now + timedelta(minutes=5) for task in tasks)
```

---

## Category 2: Agent Core (AI Integration)

### Task 2.1: Setup Gemini Client Configuration 🔴

**Priority**: Critical
**Estimated Effort**: 20 minutes
**Dependencies**: None

**Description**:
Configure OpenAI SDK client to work with Gemini API using custom base URL.

**Inputs**:
- Gemini API key from user
- OpenAI SDK documentation

**Steps**:
1. Add to `reminder-agent/config/settings.py`:
   - `gemini_api_key`
   - `gemini_model` (default: "gemini-1.5-flash")
   - `gemini_base_url`
2. Add to `reminder-agent/.env.example`
3. Install `openai` package in `requirements.txt`

**Outputs**:
- Updated `config/settings.py`
- Updated `.env.example`

**Acceptance Criteria**:
- [ ] Settings validate Gemini API key is set
- [ ] Base URL points to Gemini endpoint
- [ ] Model name configurable

**Verification**:
```python
from config.settings import settings
assert settings.gemini_api_key
assert "generativelanguage.googleapis.com" in settings.gemini_base_url
```

---

### Task 2.2: Implement AI Email Generator 🟡

**Priority**: High
**Estimated Effort**: 60 minutes
**Dependencies**: Task 2.1

**Description**:
Create service to generate personalized reminder emails using Gemini AI.

**Inputs**:
- Task object with title, description, due_date, priority
- User name and timezone (optional)

**Steps**:
1. Create file `reminder-agent/services/ai_email_generator.py`
2. Initialize OpenAI client with Gemini base URL
3. Implement `generate()` method:
   - Build prompt with task context
   - Call Gemini API
   - Parse response
   - Generate subject line with priority emoji
4. Implement `_fallback_template()` for API failures
5. Add error handling and logging

**Outputs**:
- `reminder-agent/services/ai_email_generator.py`
- `reminder-agent/models/email_content.py` (EmailContent model)

**Acceptance Criteria**:
- [ ] Generates 2-3 sentence professional email body
- [ ] Subject line includes priority emoji (🔴 HIGH, 🟡 MEDIUM, 📋 LOW)
- [ ] Falls back to template if API fails
- [ ] Logs API latency and errors

**Test Cases**:
```python
# High priority task
task = Task(title="Submit taxes", priority="HIGH", due_date=...)
email = generator.generate(task)
assert "🔴 URGENT" in email.subject
assert len(email.body.split()) < 100  # Concise

# API failure fallback
# Mock Gemini API to raise exception
email = generator.generate(task)
assert email.body  # Should use template
```

---

### Task 2.3: Create Email Content Model 🟢

**Priority**: Medium
**Estimated Effort**: 10 minutes
**Dependencies**: None

**Description**:
Define Pydantic model for email subject and body.

**Inputs**:
- Email structure requirements

**Steps**:
1. Create file `reminder-agent/models/email_content.py`
2. Define `EmailContent` model with `subject` and `body` fields
3. Add validation for max lengths

**Outputs**:
- `reminder-agent/models/email_content.py`

**Code**:
```python
from pydantic import BaseModel, Field

class EmailContent(BaseModel):
    subject: str = Field(..., max_length=200)
    body: str
```

---

## Category 3: Reminder Logic (Scheduling)

### Task 3.1: Implement One-Time Reminder Calculator 🟡

**Priority**: High
**Estimated Effort**: 20 minutes
**Dependencies**: None

**Description**:
Implement logic to calculate reminder datetime for non-recurring tasks.

**Inputs**:
- Task with `recurrence_pattern="none"` and `reminder_time`

**Steps**:
1. Create file `reminder-agent/services/reminder_calculator.py`
2. Create `ReminderCalculator` class
3. Implement `_calculate_one_time()` method:
   - Return `reminder_time` if in future
   - Return `None` if in past

**Outputs**:
- `reminder-agent/services/reminder_calculator.py` (partial)

**Acceptance Criteria**:
- [ ] Returns reminder_time for future reminders
- [ ] Returns None for past reminders

**Test Case**:
```python
@freeze_time("2025-01-15 10:00:00")
def test_one_time_future():
    task = Task(reminder_time=datetime(2025, 1, 15, 14, 0))
    result = ReminderCalculator.calculate_reminder_datetime(task)
    assert result == datetime(2025, 1, 15, 14, 0)
```

---

### Task 3.2: Implement Daily Reminder Calculator 🟡

**Priority**: High
**Estimated Effort**: 30 minutes
**Dependencies**: Task 3.1

**Description**:
Implement logic for daily recurring tasks.

**Inputs**:
- Task with `recurrence_pattern="daily"` and `reminder_time`

**Steps**:
1. Add `_calculate_daily()` method to `ReminderCalculator`
2. Extract time component from `reminder_time`
3. Create today's reminder datetime
4. If reminder hasn't passed today, return it
5. Otherwise, return tomorrow's reminder

**Outputs**:
- Updated `reminder-agent/services/reminder_calculator.py`

**Acceptance Criteria**:
- [ ] Returns today's reminder if not yet sent
- [ ] Returns tomorrow's reminder if already passed today
- [ ] Time component matches original reminder_time

**Test Cases**:
```python
@freeze_time("2025-01-15 10:00:00")
def test_daily_today_future():
    task = Task(reminder_time=datetime(2025, 1, 15, 14, 0), recurrence_pattern="daily")
    result = ReminderCalculator.calculate_reminder_datetime(task)
    assert result == datetime(2025, 1, 15, 14, 0)

@freeze_time("2025-01-15 16:00:00")
def test_daily_today_past():
    task = Task(reminder_time=datetime(2025, 1, 15, 14, 0), recurrence_pattern="daily")
    result = ReminderCalculator.calculate_reminder_datetime(task)
    assert result == datetime(2025, 1, 16, 14, 0)
```

---

### Task 3.3: Implement Weekly Reminder Calculator 🟡

**Priority**: High
**Estimated Effort**: 40 minutes
**Dependencies**: Task 3.1

**Description**:
Implement logic for weekly recurring tasks using weekday matching.

**Inputs**:
- Task with `recurrence_pattern="weekly"` and `reminder_time`

**Steps**:
1. Add `_calculate_weekly()` method
2. Extract target weekday from original `reminder_time` (0=Mon, 6=Sun)
3. Calculate days until next occurrence of target weekday
4. If today is target weekday and time hasn't passed, return today
5. Otherwise, return next occurrence

**Outputs**:
- Updated `reminder-agent/services/reminder_calculator.py`

**Acceptance Criteria**:
- [ ] Correctly identifies target weekday
- [ ] Returns next occurrence of weekday
- [ ] Handles case where today is target weekday

**Test Cases**:
```python
@freeze_time("2025-01-15 10:00:00")  # Wednesday
def test_weekly_same_day_future():
    task = Task(reminder_time=datetime(2025, 1, 15, 14, 0), recurrence_pattern="weekly")
    result = ReminderCalculator.calculate_reminder_datetime(task)
    assert result == datetime(2025, 1, 15, 14, 0)

@freeze_time("2025-01-15 10:00:00")  # Wednesday
def test_weekly_different_day():
    task = Task(reminder_time=datetime(2025, 1, 13, 14, 0), recurrence_pattern="weekly")  # Monday
    result = ReminderCalculator.calculate_reminder_datetime(task)
    assert result == datetime(2025, 1, 20, 14, 0)  # Next Monday
```

---

### Task 3.4: Implement Monthly Reminder Calculator 🟡

**Priority**: High
**Estimated Effort**: 50 minutes
**Dependencies**: Task 3.1

**Description**:
Implement logic for monthly recurring tasks with edge case handling (Feb 31→28/29).

**Inputs**:
- Task with `recurrence_pattern="monthly"` and `reminder_time`

**Steps**:
1. Add `_calculate_monthly()` method
2. Extract target day-of-month from `reminder_time`
3. Try to create reminder for current month with target day
4. Handle `ValueError` if day doesn't exist (e.g., Feb 31):
   - Use last day of month instead
5. If reminder passed this month, calculate next month's reminder

**Outputs**:
- Updated `reminder-agent/services/reminder_calculator.py`

**Acceptance Criteria**:
- [ ] Returns current month's reminder if not passed
- [ ] Returns next month's reminder if passed
- [ ] Handles invalid days (Feb 31 → Feb 28/29)
- [ ] Uses `dateutil.relativedelta` for month arithmetic

**Test Cases**:
```python
@freeze_time("2025-02-15 10:00:00")
def test_monthly_day_31_february():
    task = Task(reminder_time=datetime(2025, 1, 31, 14, 0), recurrence_pattern="monthly")
    result = ReminderCalculator.calculate_reminder_datetime(task)
    assert result == datetime(2025, 2, 28, 14, 0)  # Last day of Feb

@freeze_time("2025-01-15 16:00:00")
def test_monthly_same_day_past():
    task = Task(reminder_time=datetime(2025, 1, 15, 14, 0), recurrence_pattern="monthly")
    result = ReminderCalculator.calculate_reminder_datetime(task)
    assert result == datetime(2025, 2, 15, 14, 0)
```

---

### Task 3.5: Implement Duplicate Checker 🟡

**Priority**: High
**Estimated Effort**: 30 minutes
**Dependencies**: Task 1.3

**Description**:
Create service to check if reminder already sent using `reminder_log` table.

**Inputs**:
- `task_id` and `reminder_datetime`
- Tolerance window (default: 60 seconds)

**Steps**:
1. Create file `reminder-agent/services/duplicate_checker.py`
2. Implement `exists()` method:
   - Query `reminder_log` for matching `task_id`
   - Check if `reminder_datetime` within tolerance window (±60s)
   - Return `True` if match found
3. Handle database errors gracefully (fail-safe: return `False`)

**Outputs**:
- `reminder-agent/services/duplicate_checker.py`

**Acceptance Criteria**:
- [ ] Queries reminder_log with time window
- [ ] Returns True for exact matches
- [ ] Returns True for matches within tolerance
- [ ] Returns False for non-duplicates
- [ ] Fails safe (returns False on error)

**Test Cases**:
```python
def test_duplicate_exists():
    # Insert reminder log entry
    log = ReminderLog(task_id=1, reminder_datetime=datetime(2025, 1, 15, 14, 0), ...)
    session.add(log)

    # Should detect duplicate
    assert DuplicateChecker.exists(1, datetime(2025, 1, 15, 14, 0)) == True

    # Should detect within tolerance (59s later)
    assert DuplicateChecker.exists(1, datetime(2025, 1, 15, 14, 0, 59)) == True

    # Should not detect outside tolerance (2 min later)
    assert DuplicateChecker.exists(1, datetime(2025, 1, 15, 14, 2, 0)) == False
```

---

### Task 3.6: Implement Grace Period Logic 🟢

**Priority**: Medium
**Estimated Effort**: 15 minutes
**Dependencies**: Task 3.1

**Description**:
Add logic to skip reminders for tasks more than 1 week past due.

**Inputs**:
- Task with `due_date`

**Steps**:
1. Add `should_skip_reminder()` method to `ReminderCalculator`
2. Check if task is completed → skip
3. Check if `due_date` is > 1 week in past → skip
4. Log skipped tasks for monitoring

**Outputs**:
- Updated `reminder-agent/services/reminder_calculator.py`

**Acceptance Criteria**:
- [ ] Skips completed tasks
- [ ] Skips tasks >1 week overdue
- [ ] Logs skip reason

---

### Task 3.7: Implement Timezone Utilities 🟢

**Priority**: Medium
**Estimated Effort**: 25 minutes
**Dependencies**: None

**Description**:
Create helper functions for timezone conversion.

**Inputs**:
- UTC datetime
- User timezone string (e.g., "America/New_York")

**Steps**:
1. Create file `reminder-agent/utils/timezone.py`
2. Implement `convert_to_user_timezone()` using `pytz`
3. Implement `format_datetime_for_user()` for email display
4. Handle invalid timezones gracefully

**Outputs**:
- `reminder-agent/utils/timezone.py`

**Acceptance Criteria**:
- [ ] Converts UTC to user timezone
- [ ] Formats datetime for email (e.g., "January 15, 2025 at 2:00 PM")
- [ ] Returns UTC if timezone invalid

---

## Category 4: Email System

### Task 4.1: Create HTML Email Template 🟡

**Priority**: High
**Estimated Effort**: 45 minutes
**Dependencies**: None

**Description**:
Design responsive HTML email template with Jinja2 placeholders.

**Inputs**:
- Email design from `plan.md`
- Brand colors and styling

**Steps**:
1. Create file `reminder-agent/templates/email_template.html`
2. Add HTML structure with:
   - Header with gradient background
   - AI-generated message section
   - Task details card (with priority-based border color)
   - "View Task" CTA button
   - Footer with unsubscribe link
3. Add inline CSS for email client compatibility
4. Add Jinja2 variables: `{{ user_name }}`, `{{ ai_message }}`, `{{ task_name }}`, etc.

**Outputs**:
- `reminder-agent/templates/email_template.html`

**Acceptance Criteria**:
- [ ] Responsive design (works on mobile)
- [ ] Priority colors: RED (high), ORANGE (medium), GREEN (low)
- [ ] All required Jinja2 variables present
- [ ] Inline CSS for compatibility
- [ ] Unsubscribe link included

**Testing**:
```bash
# Preview in browser
python -c "from jinja2 import Template; t=Template(open('templates/email_template.html').read()); print(t.render(user_name='John', task_name='Test', ...))"
```

---

### Task 4.2: Implement SMTP Email Sender 🟡

**Priority**: High
**Estimated Effort**: 50 minutes
**Dependencies**: Task 4.1

**Description**:
Create service to send emails via SMTP with retry logic.

**Inputs**:
- Recipient email, subject, body
- Task object for template rendering

**Steps**:
1. Create file `reminder-agent/services/email_sender.py`
2. Implement `send()` method with:
   - MIME multipart message (text + HTML)
   - SMTP connection with TLS
   - Template rendering with Jinja2
3. Add retry decorator using `tenacity`:
   - Max 3 attempts
   - Exponential backoff (1s, 2s, 4s)
   - Retry on SMTPException only
4. Add rate limiting (100 emails/minute)

**Outputs**:
- `reminder-agent/services/email_sender.py`

**Acceptance Criteria**:
- [ ] Sends multipart email (text + HTML)
- [ ] Uses STARTTLS for security
- [ ] Retries on temporary failures
- [ ] Logs all send attempts
- [ ] Respects rate limit

**Test Cases**:
```python
@pytest.mark.asyncio
async def test_email_send_success(mock_smtp):
    sender = EmailSender()
    success = await sender.send(
        to="test@example.com",
        subject="Test",
        body="Test body",
        task=task
    )
    assert success == True
    assert mock_smtp.send_called

@pytest.mark.asyncio
async def test_email_send_retry(mock_smtp_fail_twice):
    # Should retry 3 times and eventually succeed
    success = await sender.send(...)
    assert success == True
    assert mock_smtp_fail_twice.attempts == 3
```

---

### Task 4.3: Implement Delivery Tracker 🟡

**Priority**: High
**Estimated Effort**: 30 minutes
**Dependencies**: Task 1.3, Task 4.2

**Description**:
Create service to log email delivery status to `reminder_log`.

**Inputs**:
- Task ID, user ID, reminder datetime
- Email details (to, subject, body)
- Delivery status (sent/failed)

**Steps**:
1. Create file `reminder-agent/services/delivery_tracker.py`
2. Implement `log_success()` method:
   - Insert record with `delivery_status="sent"`
3. Implement `log_failure()` method:
   - Insert record with `delivery_status="failed"`
   - Store error message
4. Handle UNIQUE constraint violations gracefully

**Outputs**:
- `reminder-agent/services/delivery_tracker.py`

**Acceptance Criteria**:
- [ ] Logs successful deliveries
- [ ] Logs failed deliveries with error details
- [ ] Handles duplicate key errors
- [ ] Commits transaction properly

---

## Category 5: Background Execution

### Task 5.1: Setup Project Structure 🔴

**Priority**: Critical
**Estimated Effort**: 20 minutes
**Dependencies**: None

**Description**:
Create directory structure for reminder agent project.

**Steps**:
```bash
mkdir -p reminder-agent/{config,models,services,jobs,utils,tests,templates}
touch reminder-agent/__init__.py
touch reminder-agent/main.py
touch reminder-agent/requirements.txt
touch reminder-agent/.env.example
# Create all subdirectory __init__.py files
```

**Outputs**:
- Complete directory structure

---

### Task 5.2: Create Requirements File 🔴

**Priority**: Critical
**Estimated Effort**: 15 minutes
**Dependencies**: Task 5.1

**Description**:
Define all Python dependencies with pinned versions.

**Steps**:
1. Create `reminder-agent/requirements.txt`
2. Add dependencies:
   - fastapi, uvicorn, sqlmodel, psycopg, asyncpg
   - pydantic-settings, python-dotenv
   - apscheduler
   - openai (for Gemini)
   - aiosmtplib, jinja2
   - python-dateutil, pytz
   - tenacity (retry logic)
   - pytest, pytest-asyncio, freezegun (testing)

**Outputs**:
- `reminder-agent/requirements.txt`

**Code**: See `plan.md` Phase 1, Step 1.2.2

---

### Task 5.3: Create Settings Configuration 🔴

**Priority**: Critical
**Estimated Effort**: 30 minutes
**Dependencies**: Task 5.2

**Description**:
Implement settings management using pydantic-settings.

**Inputs**:
- Environment variables list from `plan.md`

**Steps**:
1. Create file `reminder-agent/config/settings.py`
2. Define `Settings` class with pydantic-settings
3. Add all required fields with types and defaults
4. Add validation (e.g., `database_url` must start with "postgresql://")
5. Create global `settings` instance

**Outputs**:
- `reminder-agent/config/settings.py`
- `reminder-agent/.env.example`

**Acceptance Criteria**:
- [ ] All environment variables documented
- [ ] Type validation works
- [ ] Defaults set appropriately
- [ ] `.env.example` has all required vars

---

### Task 5.4: Implement Logging Infrastructure 🟡

**Priority**: High
**Estimated Effort**: 35 minutes
**Dependencies**: Task 5.3

**Description**:
Create structured logging system with JSON output.

**Inputs**:
- Log level from settings

**Steps**:
1. Create file `reminder-agent/utils/logger.py`
2. Implement `JSONFormatter` class
3. Implement `setup_logging()` function
4. Configure console handler with formatter
5. Create global logger instance

**Outputs**:
- `reminder-agent/utils/logger.py`

**Acceptance Criteria**:
- [ ] JSON logs in production
- [ ] Text logs in development
- [ ] Includes timestamp, level, module, function, line
- [ ] Supports extra fields (task_id, user_id, action)

**Test**:
```python
from utils.logger import logger
logger.info("Test message", extra={"task_id": 123, "action": "send_email"})
# Output: {"timestamp": "2025-01-15T10:00:00", "level": "INFO", "task_id": 123, ...}
```

---

### Task 5.5: Implement Database Service 🟡

**Priority**: High
**Estimated Effort**: 30 minutes
**Dependencies**: Task 5.3

**Description**:
Create database connection management with pooling.

**Inputs**:
- Database URL from settings

**Steps**:
1. Create file `reminder-agent/services/database.py`
2. Create SQLModel engine with connection pooling
3. Implement `init_db()` to create tables
4. Implement `test_connection()` for health checks
5. Implement `get_session()` context manager

**Outputs**:
- `reminder-agent/services/database.py`

**Acceptance Criteria**:
- [ ] Connection pool configured (size=10, overflow=5)
- [ ] pool_pre_ping enabled
- [ ] SSL mode required for Neon
- [ ] Auto-rollback on errors

---

### Task 5.6: Create Main Reminder Processor Job 🟡

**Priority**: High
**Estimated Effort**: 60 minutes
**Dependencies**: Task 1.5, Task 2.2, Task 3.5, Task 4.3

**Description**:
Implement main job that orchestrates all services to process reminders.

**Inputs**:
- All service implementations

**Steps**:
1. Create file `reminder-agent/jobs/reminder_processor.py`
2. Create `ReminderProcessor` class
3. Implement `run()` method:
   - Update agent state
   - Fetch tasks needing reminders
   - For each task:
     - Calculate reminder datetime
     - Check duplicates
     - Generate AI email
     - Send email
     - Log delivery
   - Update final agent state with metrics
4. Add error handling per task (continue on failure)

**Outputs**:
- `reminder-agent/jobs/reminder_processor.py`

**Acceptance Criteria**:
- [ ] Processes all tasks in batch
- [ ] Handles per-task errors gracefully
- [ ] Updates agent_state metrics
- [ ] Logs summary (tasks processed, sent, errors)

---

### Task 5.7: Implement Main Entry Point with APScheduler 🟡

**Priority**: High
**Estimated Effort**: 40 minutes
**Dependencies**: Task 5.6

**Description**:
Create main script that starts APScheduler and runs agent.

**Inputs**:
- ReminderProcessor from Task 5.6
- Polling interval from settings

**Steps**:
1. Create file `reminder-agent/main.py`
2. Implement `startup()` function:
   - Test database connection
   - Initialize database tables
   - Validate Gemini API (optional)
3. Implement `main()` function:
   - Create AsyncIOScheduler
   - Schedule ReminderProcessor.run() every N minutes
   - Start scheduler
   - Keep-alive loop
4. Add graceful shutdown handler

**Outputs**:
- `reminder-agent/main.py`

**Acceptance Criteria**:
- [ ] Validates all dependencies on startup
- [ ] Exits with error if database unreachable
- [ ] Schedules job at configured interval
- [ ] Handles SIGINT/SIGTERM gracefully

**Usage**:
```bash
cd reminder-agent
python main.py
# Output: "🚀 Starting AI Reminder Agent"
#         "✅ Startup complete"
#         "⏰ Scheduler started (every 5 min)"
```

---

## Category 6: Security

### Task 6.1: Implement Environment Variable Validation 🟡

**Priority**: High
**Estimated Effort**: 20 minutes
**Dependencies**: Task 5.3

**Description**:
Add validation to ensure all required secrets are set.

**Steps**:
1. Update `config/settings.py`
2. Add validators for:
   - `database_url` (must be PostgreSQL)
   - `gemini_api_key` (must start with expected prefix)
   - `smtp_password` (must be non-empty)
3. Raise clear error messages if validation fails

**Outputs**:
- Updated `config/settings.py`

**Acceptance Criteria**:
- [ ] Raises ValidationError if DATABASE_URL missing
- [ ] Raises ValidationError if GEMINI_API_KEY missing
- [ ] Error messages are actionable

---

### Task 6.2: Implement Rate Limiting 🟢

**Priority**: Medium
**Estimated Effort**: 30 minutes
**Dependencies**: Task 4.2

**Description**:
Add rate limiting to prevent email abuse.

**Steps**:
1. Update `email_sender.py`
2. Track emails sent per minute
3. Sleep if rate limit exceeded
4. Log rate limit hits

**Outputs**:
- Updated `services/email_sender.py`

**Acceptance Criteria**:
- [ ] Max 100 emails/minute by default
- [ ] Configurable via settings
- [ ] Logs when throttling occurs

---

### Task 6.3: Add User Authorization Check 🟢

**Priority**: Medium
**Estimated Effort**: 25 minutes
**Dependencies**: Task 1.5

**Description**:
Verify agent only processes tasks for authenticated users.

**Steps**:
1. Update `task_reader.py`
2. Join with users table (Better Auth)
3. Filter out tasks for deleted/suspended users
4. Log skipped tasks

**Outputs**:
- Updated `services/task_reader.py`

**Acceptance Criteria**:
- [ ] Skips tasks for non-existent users
- [ ] Logs user lookup failures

---

### Task 6.4: Sanitize Email Content 🟢

**Priority**: Medium
**Estimated Effort**: 20 minutes
**Dependencies**: Task 2.2

**Description**:
Prevent XSS and injection attacks in emails.

**Steps**:
1. Update `ai_email_generator.py`
2. Escape HTML in task title/description
3. Validate email addresses before sending
4. Strip potentially malicious content

**Outputs**:
- Updated `services/ai_email_generator.py`

**Acceptance Criteria**:
- [ ] HTML entities escaped in user input
- [ ] Email addresses validated with regex
- [ ] Rejects invalid recipient addresses

---

## Category 7: Testing

### Task 7.1: Setup Test Infrastructure 🔴

**Priority**: Critical
**Estimated Effort**: 30 minutes
**Dependencies**: Task 5.2

**Description**:
Configure pytest with fixtures and test database.

**Steps**:
1. Create file `reminder-agent/tests/conftest.py`
2. Add pytest fixtures:
   - `test_db` (in-memory SQLite or test Postgres)
   - `mock_gemini_api`
   - `mock_smtp_server`
   - `sample_tasks`
3. Configure pytest.ini with asyncio mode

**Outputs**:
- `reminder-agent/tests/conftest.py`
- `reminder-agent/pytest.ini`

**Acceptance Criteria**:
- [ ] Fixtures available to all tests
- [ ] Test database isolated from production
- [ ] Async tests supported

---

### Task 7.2: Write Reminder Calculator Unit Tests 🔵

**Priority**: High
**Estimated Effort**: 60 minutes
**Dependencies**: Task 3.1-3.4, Task 7.1

**Description**:
Test all recurrence patterns with time-frozen scenarios.

**Steps**:
1. Create file `reminder-agent/tests/test_calculator.py`
2. Write tests for:
   - One-time reminders (future, past)
   - Daily reminders (today future, today past)
   - Weekly reminders (same weekday, different weekday)
   - Monthly reminders (same day, different day, Feb 31)
3. Use `freezegun` to freeze time

**Outputs**:
- `reminder-agent/tests/test_calculator.py`

**Acceptance Criteria**:
- [ ] 8+ test cases covering all scenarios
- [ ] Uses `@freeze_time` decorator
- [ ] All tests pass
- [ ] Coverage > 90% for calculator.py

**Reference**: See `plan.md` Phase 5, Section 5.3

---

### Task 7.3: Write AI Email Generator Unit Tests 🔵

**Priority**: High
**Estimated Effort**: 40 minutes
**Dependencies**: Task 2.2, Task 7.1

**Description**:
Test email generation with mocked Gemini API.

**Steps**:
1. Create file `reminder-agent/tests/test_ai_generator.py`
2. Mock Gemini API responses
3. Test:
   - Successful generation
   - Priority-based subject lines
   - Fallback on API failure
   - Error handling

**Outputs**:
- `reminder-agent/tests/test_ai_generator.py`

**Acceptance Criteria**:
- [ ] Tests all priority levels (HIGH, MEDIUM, LOW)
- [ ] Tests fallback template
- [ ] Verifies subject emoji (🔴, 🟡, 📋)
- [ ] Coverage > 85%

---

### Task 7.4: Write Email Sender Unit Tests 🔵

**Priority**: High
**Estimated Effort**: 45 minutes
**Dependencies**: Task 4.2, Task 7.1

**Description**:
Test SMTP sending with retry logic.

**Steps**:
1. Create file `reminder-agent/tests/test_email_sender.py`
2. Mock SMTP server
3. Test:
   - Successful send
   - Retry on temporary failure
   - Give up after max attempts
   - Multipart message format

**Outputs**:
- `reminder-agent/tests/test_email_sender.py`

**Acceptance Criteria**:
- [ ] Tests retry logic (3 attempts)
- [ ] Tests exponential backoff timing
- [ ] Verifies HTML + text parts included
- [ ] Coverage > 85%

---

### Task 7.5: Write Integration Tests 🔵

**Priority**: High
**Estimated Effort**: 60 minutes
**Dependencies**: Task 5.6, Task 7.1

**Description**:
Test end-to-end flow from task query to email delivery.

**Steps**:
1. Create file `reminder-agent/tests/test_integration.py`
2. Setup test database with sample tasks
3. Test complete flow:
   - Task fetch → Calculator → Duplicate check → AI generation → Email send → Delivery log
4. Verify database state after processing

**Outputs**:
- `reminder-agent/tests/test_integration.py`

**Acceptance Criteria**:
- [ ] Tests complete reminder cycle
- [ ] Verifies reminder_log entries created
- [ ] Tests duplicate prevention
- [ ] Verifies agent_state updated

**Test Case**:
```python
@pytest.mark.asyncio
async def test_end_to_end_reminder(test_db, mock_gemini, mock_smtp):
    # Setup: Create task with reminder in 2 minutes
    task = Task(
        user_id="user123",
        title="Test Task",
        reminder_time=datetime.utcnow() + timedelta(minutes=2),
        recurrence_pattern="none"
    )
    test_db.add(task)

    # Execute
    processor = ReminderProcessor()
    await processor.run()

    # Verify
    log = test_db.query(ReminderLog).filter_by(task_id=task.id).first()
    assert log is not None
    assert log.delivery_status == "sent"
    assert mock_smtp.send_called
```

---

### Task 7.6: Write Duplicate Prevention Tests 🔵

**Priority**: High
**Estimated Effort**: 30 minutes
**Dependencies**: Task 3.5, Task 7.1

**Description**:
Verify duplicate reminders are never sent.

**Steps**:
1. Add to `test_integration.py`
2. Test scenarios:
   - Same task, same datetime → skip second
   - Same task, different datetime → send both
   - Database UNIQUE constraint enforced

**Outputs**:
- Updated `reminder-agent/tests/test_integration.py`

**Acceptance Criteria**:
- [ ] Duplicate within 60s tolerance → skipped
- [ ] Different datetime → sent
- [ ] UNIQUE constraint violation handled gracefully

---

## Category 8: Deployment

### Task 8.1: Create Dockerfile 🟡

**Priority**: High
**Estimated Effort**: 25 minutes
**Dependencies**: Task 5.2

**Description**:
Create Docker image for reminder agent.

**Steps**:
1. Create `reminder-agent/Dockerfile`
2. Use `python:3.11-slim` base image
3. Copy requirements and install dependencies
4. Copy application code
5. Set CMD to run `main.py`

**Outputs**:
- `reminder-agent/Dockerfile`

**Code**: See `plan.md` Deployment Strategy

**Build Test**:
```bash
cd reminder-agent
docker build -t todo-reminder-agent .
docker run --env-file .env todo-reminder-agent
```

---

### Task 8.2: Create Docker Compose Configuration 🟡

**Priority**: High
**Estimated Effort**: 20 minutes
**Dependencies**: Task 8.1

**Description**:
Configure docker-compose for easy deployment.

**Steps**:
1. Create `docker-compose.yml` in project root
2. Define `reminder-agent` service
3. Add health check
4. Configure restart policy
5. Add to `todo-network`

**Outputs**:
- `docker-compose.yml`

**Code**: See `plan.md` Deployment Strategy

**Test**:
```bash
docker-compose up -d reminder-agent
docker-compose ps  # Should show healthy
docker-compose logs -f reminder-agent
```

---

### Task 8.3: Create Startup Script 🟢

**Priority**: Medium
**Estimated Effort**: 15 minutes
**Dependencies**: Task 5.7

**Description**:
Create bash script for manual startup with validation.

**Steps**:
1. Create `reminder-agent/start.sh`
2. Check environment variables set
3. Test database connection
4. Start agent

**Outputs**:
- `reminder-agent/start.sh`

**Code**:
```bash
#!/bin/bash
set -e

echo "Starting AI Reminder Agent..."

# Check .env exists
if [ ! -f .env ]; then
    echo "Error: .env file not found"
    exit 1
fi

# Activate venv
source venv/bin/activate

# Test database
python -c "from services.database import test_connection; exit(0 if test_connection() else 1)"

# Start agent
python main.py
```

---

### Task 8.4: Add Health Check Endpoint to FastAPI Backend 🟢

**Priority**: Medium
**Estimated Effort**: 30 minutes
**Dependencies**: Task 1.4

**Description**:
Add API endpoint to check agent health.

**Steps**:
1. Update `backend/routes/health.py`
2. Add `/health/reminder-agent` endpoint
3. Query `agent_state` table
4. Check last_check_at < 10 minutes ago
5. Return status JSON

**Outputs**:
- Updated `backend/routes/health.py`

**Acceptance Criteria**:
- [ ] Returns "healthy" if agent checked in recently
- [ ] Returns "error" if no check in 10+ minutes
- [ ] Returns agent metrics (tasks_processed, reminders_sent)

**Test**:
```bash
curl http://localhost:8000/health/reminder-agent
# {"status": "healthy", "last_check": "2025-01-15T10:00:00", ...}
```

---

### Task 8.5: Create Deployment Documentation 🟢

**Priority**: Medium
**Estimated Effort**: 40 minutes
**Dependencies**: Task 8.1, Task 8.2

**Description**:
Write README with setup and deployment instructions.

**Steps**:
1. Create `reminder-agent/README.md`
2. Document:
   - Prerequisites
   - Local development setup
   - Environment variables
   - Running tests
   - Docker deployment
   - Troubleshooting

**Outputs**:
- `reminder-agent/README.md`

**Sections**:
```markdown
# AI Task Reminder Agent

## Prerequisites
- Python 3.11+
- PostgreSQL (Neon)
- Gemini API key
- SMTP credentials

## Quick Start
### Local Development
1. Clone repository
2. Create virtual environment
3. Install dependencies
4. Configure .env
5. Run migrations
6. Start agent

### Docker Deployment
1. Build image
2. Configure .env
3. Run docker-compose

## Configuration
[Environment variables table]

## Troubleshooting
[Common issues and solutions]
```

---

### Task 8.6: Create Rollback Procedure 🟢

**Priority**: Medium
**Estimated Effort**: 20 minutes
**Dependencies**: Task 8.2

**Description**:
Document rollback steps in case of issues.

**Steps**:
1. Create `reminder-agent/ROLLBACK.md`
2. Document:
   - How to stop agent
   - Database state verification
   - Migration rollback SQL
   - Restoration from backup

**Outputs**:
- `reminder-agent/ROLLBACK.md`

**Code**: See `plan.md` Rollback Plan

---

## Task Summary

**Total Tasks**: 46
**Estimated Total Effort**: ~21 hours

### By Category:
- 🗄️ Database Layer: 5 tasks (~3 hours)
- 🤖 Agent Core: 3 tasks (~1.5 hours)
- ⏰ Reminder Logic: 7 tasks (~3.5 hours)
- 📧 Email System: 3 tasks (~2 hours)
- ⚙️ Background Execution: 7 tasks (~4 hours)
- 🔒 Security: 4 tasks (~2 hours)
- 🧪 Testing: 6 tasks (~4.5 hours)
- 🚀 Deployment: 6 tasks (~3 hours)

### Critical Path (Must Complete First):
1. Task 1.1 → 1.2 (Database migration)
2. Task 5.1 → 5.2 → 5.3 (Project setup)
3. Task 1.3, 1.4 (SQLModels)
4. Task 2.1 (Gemini config)
5. Task 5.4, 5.5 (Logging, Database service)

### Recommended Order:
**Week 1** (Foundation):
- Tasks 1.1-1.5 (Database layer)
- Tasks 5.1-5.5 (Project setup)

**Week 2** (Core Logic):
- Tasks 2.1-2.3 (AI integration)
- Tasks 3.1-3.7 (Reminder logic)

**Week 3** (Email & Execution):
- Tasks 4.1-4.3 (Email system)
- Tasks 5.6-5.7 (Background execution)

**Week 4** (Security & Testing):
- Tasks 6.1-6.4 (Security)
- Tasks 7.1-7.6 (Testing)

**Week 5** (Deployment):
- Tasks 8.1-8.6 (Deployment)

---

## Validation Checklist

Before marking feature complete:
- [ ] All 46 tasks completed
- [ ] All unit tests passing (coverage > 80%)
- [ ] Integration tests passing
- [ ] Deployed to staging environment
- [ ] Sent test reminders successfully
- [ ] No duplicate reminders detected
- [ ] Agent health endpoint returning "healthy"
- [ ] Documentation complete
- [ ] Rollback procedure tested

---

**Document Status**: Ready for Implementation
**Next Action**: Begin with Critical Path tasks (1.1, 5.1-5.3)
