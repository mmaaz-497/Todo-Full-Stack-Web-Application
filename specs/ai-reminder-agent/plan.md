# AI Task Reminder Agent - Implementation Plan

**Feature**: AI Task Reminder Agent
**Version**: 1.0.0
**Date**: 2025-12-25
**Status**: Planning

---

## Table of Contents
1. [System Architecture Overview](#1-system-architecture-overview)
2. [Agent Lifecycle Flow](#2-agent-lifecycle-flow)
3. [Phase 1: Foundation Setup](#phase-1-foundation-setup)
4. [Phase 2: Core Agent Logic](#phase-2-core-agent-logic)
5. [Phase 3: Scheduling & Repeat Logic](#phase-3-scheduling--repeat-logic)
6. [Phase 4: Email System](#phase-4-email-system)
7. [Phase 5: Testing & Production Readiness](#phase-5-testing--production-readiness)
8. [Critical Design Decisions](#critical-design-decisions)
9. [Deployment Strategy](#deployment-strategy)
10. [Rollback Plan](#rollback-plan)

---

## 1. System Architecture Overview

### 1.1 High-Level Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                          │
│                                                               │
│  ┌──────────────┐      ┌──────────────────────────────┐    │
│  │  Task CRUD   │      │    AI Reminder Agent         │    │
│  │  API Routes  │      │    (Separate Process)        │    │
│  └──────┬───────┘      └──────────┬───────────────────┘    │
│         │                          │                         │
│         └──────────┬───────────────┘                         │
│                    ▼                                         │
│           ┌─────────────────┐                                │
│           │  PostgreSQL DB  │                                │
│           │                 │                                │
│           │  Tables:        │                                │
│           │  - tasks        │                                │
│           │  - users        │                                │
│           │  - reminder_log │ (NEW)                         │
│           │  - agent_state  │ (NEW)                         │
│           └─────────────────┘                                │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │  External Services     │
              │  - Gemini API          │
              │  - SMTP Server         │
              └────────────────────────┘
```

### 1.2 Agent Service Architecture

```
reminder-agent/
├── config/
│   ├── __init__.py
│   ├── settings.py              # Environment config using pydantic-settings
│   └── constants.py             # Constants (polling intervals, limits)
│
├── models/
│   ├── __init__.py
│   ├── task.py                  # Task SQLModel (reuse from backend)
│   ├── reminder_log.py          # ReminderLog SQLModel
│   ├── agent_state.py           # AgentState SQLModel
│   └── email_content.py         # Email data models
│
├── services/
│   ├── __init__.py
│   ├── database.py              # DB connection & session management
│   ├── task_reader.py           # Query tasks needing reminders
│   ├── reminder_calculator.py   # Calculate next reminder datetime
│   ├── duplicate_checker.py     # Check if reminder already sent
│   ├── ai_email_generator.py   # Gemini integration for emails
│   ├── email_sender.py          # SMTP/SES email delivery
│   └── delivery_tracker.py      # Log reminder delivery status
│
├── jobs/
│   ├── __init__.py
│   └── reminder_processor.py    # Main scheduled job
│
├── utils/
│   ├── __init__.py
│   ├── logger.py                # Structured logging setup
│   ├── timezone.py              # Timezone conversion helpers
│   └── retry.py                 # Retry logic decorators
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Pytest fixtures
│   ├── test_calculator.py       # Reminder calculation tests
│   ├── test_ai_generator.py     # AI generation tests
│   ├── test_email_sender.py     # Email delivery tests
│   └── test_integration.py      # End-to-end tests
│
├── templates/
│   └── email_template.html      # HTML email template
│
├── main.py                      # Agent entry point
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
└── README.md                    # Setup & deployment docs
```

---

## 2. Agent Lifecycle Flow

### 2.1 Startup Sequence

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Load Environment Variables                                │
│    - DATABASE_URL                                            │
│    - GEMINI_API_KEY                                          │
│    - SMTP credentials                                        │
└───────────────────┬─────────────────────────────────────────┘
                    ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Initialize Database Connection                            │
│    - Test connection with pool_pre_ping                      │
│    - Create reminder_log & agent_state tables if missing     │
└───────────────────┬─────────────────────────────────────────┘
                    ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Validate External Services                                │
│    - Test Gemini API connection (ping endpoint)              │
│    - Test SMTP connection (optional, warn if fails)          │
└───────────────────┬─────────────────────────────────────────┘
                    ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Start APScheduler                                         │
│    - Schedule reminder_processor job (every 5 minutes)       │
│    - Schedule health_check job (every 1 minute)              │
└───────────────────┬─────────────────────────────────────────┘
                    ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. Update agent_state                                        │
│    - status = 'running'                                      │
│    - last_check_at = NOW()                                   │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Reminder Processing Flow

```
START: Reminder Processor Job (runs every 5 min)
  │
  ├──> 1. Update agent_state.last_check_at
  │
  ├──> 2. Query tasks needing reminders
  │     SELECT tasks WHERE:
  │       - completed = false
  │       - reminder_time IS NOT NULL
  │       - Calculate if reminder is due within next 5 min
  │
  ├──> 3. For each task:
  │     │
  │     ├──> 3.1. Calculate exact reminder datetime
  │     │     (Handle repeat_type: none/daily/weekly/monthly)
  │     │
  │     ├──> 3.2. Check for duplicates
  │     │     SELECT FROM reminder_log WHERE
  │     │       task_id = ? AND reminder_datetime = ?
  │     │
  │     ├──> 3.3. If duplicate exists → SKIP
  │     │
  │     ├──> 3.4. Fetch user data (email, name, timezone)
  │     │
  │     ├──> 3.5. Generate AI email content
  │     │     - Call Gemini API with task context
  │     │     - Fallback to template if API fails
  │     │
  │     ├──> 3.6. Send email via SMTP
  │     │     - Retry up to 3 times on failure
  │     │     - Apply rate limiting (100/min)
  │     │
  │     └──> 3.7. Log to reminder_log
  │           INSERT INTO reminder_log (
  │             task_id, user_id, reminder_datetime,
  │             email_to, email_subject, email_body,
  │             delivery_status, sent_at
  │           )
  │
  └──> 4. Update agent_state
        - tasks_processed += count
        - reminders_sent += successful_count
        - errors_count += error_count

END
```

### 2.3 Error Recovery Flow

```
Error Occurs
  │
  ├──> Gemini API Error
  │     └──> Fallback to template-based email
  │          Log warning, continue processing
  │
  ├──> SMTP Error (temporary)
  │     └──> Retry with exponential backoff (3 attempts)
  │          If all fail: log to reminder_log with status='failed'
  │          Schedule retry in next cycle
  │
  ├──> Database Connection Error
  │     └──> Retry connection 3 times with backoff
  │          If all fail: log critical error, pause agent
  │          Alert ops team (future: PagerDuty integration)
  │
  └──> Validation Error (invalid task data)
        └──> Log warning with task_id
             Skip task, continue processing others
```

---

## Phase 1: Foundation Setup

### 1.1 Database Schema Changes

**Objective**: Add new tables to support reminder tracking and agent health monitoring.

#### Step 1.1.1: Create Migration Script

**File**: `backend/migrations/001_add_reminder_tables.sql`

```sql
-- ============================================================
-- Migration: Add Reminder Agent Tables
-- Version: 001
-- Date: 2025-12-25
-- Description: Add reminder_log and agent_state tables
-- ============================================================

-- Table: reminder_log
-- Purpose: Track all sent reminders to prevent duplicates
CREATE TABLE IF NOT EXISTS reminder_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    user_id VARCHAR(255) NOT NULL,
    reminder_datetime TIMESTAMP WITH TIME ZONE NOT NULL,
    sent_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    email_to VARCHAR(255) NOT NULL,
    email_subject TEXT NOT NULL,
    email_body TEXT NOT NULL,
    delivery_status VARCHAR(50) DEFAULT 'sent',  -- sent, failed, bounced, retrying
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    next_retry_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Prevent duplicate reminders
    CONSTRAINT unique_task_reminder UNIQUE(task_id, reminder_datetime)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_reminder_log_task_id ON reminder_log(task_id);
CREATE INDEX IF NOT EXISTS idx_reminder_log_user_id ON reminder_log(user_id);
CREATE INDEX IF NOT EXISTS idx_reminder_log_status ON reminder_log(delivery_status);
CREATE INDEX IF NOT EXISTS idx_reminder_log_sent_at ON reminder_log(sent_at DESC);
CREATE INDEX IF NOT EXISTS idx_reminder_log_retry ON reminder_log(next_retry_at)
    WHERE delivery_status = 'retrying';

-- Table: agent_state
-- Purpose: Track agent health and execution metrics
CREATE TABLE IF NOT EXISTS agent_state (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    last_check_at TIMESTAMP WITH TIME ZONE NOT NULL,
    tasks_processed INTEGER DEFAULT 0,
    reminders_sent INTEGER DEFAULT 0,
    errors_count INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'running',  -- running, paused, error
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert initial state record
INSERT INTO agent_state (last_check_at, status, metadata)
VALUES (NOW(), 'initialized', '{"version": "1.0.0"}')
ON CONFLICT DO NOTHING;

COMMENT ON TABLE reminder_log IS 'Tracks all reminder emails sent to users';
COMMENT ON TABLE agent_state IS 'Tracks AI reminder agent health and metrics';
```

#### Step 1.1.2: Create SQLModel Models

**File**: `reminder-agent/models/reminder_log.py`

```python
"""SQLModel for reminder_log table."""

from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class DeliveryStatus(str, Enum):
    """Email delivery status."""
    SENT = "sent"
    FAILED = "failed"
    BOUNCED = "bounced"
    RETRYING = "retrying"


class ReminderLog(SQLModel, table=True):
    """Log of all reminder emails sent to users.

    Used to prevent duplicate reminders and provide audit trail.
    """
    __tablename__ = "reminder_log"

    id: Optional[str] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="tasks.id", index=True)
    user_id: str = Field(index=True)
    reminder_datetime: datetime = Field(nullable=False)
    sent_at: datetime = Field(default_factory=datetime.utcnow)
    email_to: str = Field(max_length=255)
    email_subject: str
    email_body: str
    delivery_status: str = Field(default=DeliveryStatus.SENT.value)
    error_message: Optional[str] = None
    retry_count: int = Field(default=0)
    next_retry_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

**File**: `reminder-agent/models/agent_state.py`

```python
"""SQLModel for agent_state table."""

from sqlmodel import SQLModel, Field, Column
from sqlalchemy.dialects.postgresql import JSONB
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class AgentStatus(str, Enum):
    """Agent execution status."""
    INITIALIZED = "initialized"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"


class AgentState(SQLModel, table=True):
    """Agent health and execution state.

    Tracks agent activity for monitoring and debugging.
    """
    __tablename__ = "agent_state"

    id: Optional[str] = Field(default=None, primary_key=True)
    last_check_at: datetime = Field(nullable=False)
    tasks_processed: int = Field(default=0)
    reminders_sent: int = Field(default=0)
    errors_count: int = Field(default=0)
    status: str = Field(default=AgentStatus.RUNNING.value)
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSONB, nullable=False, server_default='{}')
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

#### Step 1.1.3: Run Migration

```bash
# From backend directory
psql $DATABASE_URL < migrations/001_add_reminder_tables.sql
```

**Verification**:
```sql
-- Verify tables created
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('reminder_log', 'agent_state');

-- Verify indexes
SELECT indexname FROM pg_indexes
WHERE tablename = 'reminder_log';
```

---

### 1.2 Project Setup

#### Step 1.2.1: Create Project Structure

```bash
# From repository root
mkdir -p reminder-agent/{config,models,services,jobs,utils,tests,templates}
touch reminder-agent/{__init__.py,main.py,requirements.txt,.env.example}
touch reminder-agent/config/{__init__.py,settings.py,constants.py}
touch reminder-agent/models/{__init__.py,task.py,reminder_log.py,agent_state.py,email_content.py}
touch reminder-agent/services/{__init__.py,database.py,task_reader.py,reminder_calculator.py,duplicate_checker.py,ai_email_generator.py,email_sender.py,delivery_tracker.py}
touch reminder-agent/jobs/{__init__.py,reminder_processor.py}
touch reminder-agent/utils/{__init__.py,logger.py,timezone.py,retry.py}
touch reminder-agent/tests/{__init__.py,conftest.py,test_calculator.py,test_ai_generator.py,test_email_sender.py,test_integration.py}
```

#### Step 1.2.2: Define Dependencies

**File**: `reminder-agent/requirements.txt`

```txt
# Core Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0

# Database
sqlmodel==0.0.14
psycopg[binary]==3.1.18
asyncpg==0.29.0

# Configuration
pydantic-settings==2.1.0
python-dotenv==1.0.0

# Scheduling
apscheduler==3.10.4

# AI Integration
openai==1.3.0

# Email
aiosmtplib==3.0.1

# Templating
jinja2==3.1.2

# Utilities
python-dateutil==2.8.2
pytz==2023.3
tenacity==8.2.3

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
pytest-mock==3.12.0
freezegun==1.4.0  # For time-based tests
```

#### Step 1.2.3: Environment Configuration

**File**: `reminder-agent/.env.example`

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/todo_db

# Gemini AI Configuration
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SENDER_EMAIL=reminders@yourdomain.com
SENDER_NAME=Todo Reminder Bot

# Application Configuration
APP_URL=http://localhost:3000
APP_NAME=Todo Reminder Agent
ENVIRONMENT=development  # development, staging, production

# Agent Configuration
POLLING_INTERVAL_MINUTES=5
REMINDER_LOOKAHEAD_MINUTES=5  # How far ahead to check for reminders
EMAIL_RATE_LIMIT_PER_MINUTE=100
RETRY_MAX_ATTEMPTS=3
RETRY_BACKOFF_MULTIPLIER=2  # Exponential backoff: 1s, 2s, 4s...

# Logging Configuration
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT=json  # json or text
```

#### Step 1.2.4: Settings Management

**File**: `reminder-agent/config/settings.py`

```python
"""Application settings using pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal


class Settings(BaseSettings):
    """Agent configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Database
    database_url: str

    # Gemini AI
    gemini_api_key: str
    gemini_model: str = "gemini-1.5-flash"
    gemini_base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai/"

    # Email
    smtp_host: str
    smtp_port: int = 587
    smtp_user: str
    smtp_password: str
    sender_email: str
    sender_name: str = "Todo Reminder Bot"

    # Application
    app_url: str
    app_name: str = "Todo Reminder Agent"
    environment: Literal["development", "staging", "production"] = "development"

    # Agent Configuration
    polling_interval_minutes: int = 5
    reminder_lookahead_minutes: int = 5
    email_rate_limit_per_minute: int = 100
    retry_max_attempts: int = 3
    retry_backoff_multiplier: int = 2

    # Logging
    log_level: str = "INFO"
    log_format: Literal["json", "text"] = "json"

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment == "production"


# Global settings instance
settings = Settings()
```

**File**: `reminder-agent/config/constants.py`

```python
"""Application constants."""

# Time constants
SECONDS_PER_MINUTE = 60
MINUTES_PER_HOUR = 60
HOURS_PER_DAY = 24
DAYS_PER_WEEK = 7

# Email constants
MAX_EMAIL_SUBJECT_LENGTH = 200
MAX_EMAIL_BODY_LENGTH = 10000

# Reminder constants
MAX_TASKS_PER_BATCH = 1000
DUPLICATE_CHECK_TOLERANCE_SECONDS = 60  # Consider reminders within 1 min as duplicates

# Agent states
AGENT_HEALTHY_THRESHOLD_MINUTES = 10  # Alert if no check in 10 min
```

---

### 1.3 Logging Infrastructure

**File**: `reminder-agent/utils/logger.py`

```python
"""Structured logging configuration."""

import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict
from config.settings import settings


class JSONFormatter(logging.Formatter):
    """Format log records as JSON."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON string."""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        if hasattr(record, "task_id"):
            log_data["task_id"] = record.task_id
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "action"):
            log_data["action"] = record.action

        return json.dumps(log_data)


def setup_logging() -> logging.Logger:
    """Configure application logging.

    Returns:
        Logger: Configured root logger
    """
    # Create root logger
    logger = logging.getLogger("reminder-agent")
    logger.setLevel(getattr(logging, settings.log_level.upper()))

    # Remove existing handlers
    logger.handlers.clear()

    # Create console handler
    handler = logging.StreamHandler(sys.stdout)

    # Set formatter
    if settings.log_format == "json":
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Prevent propagation to root logger
    logger.propagate = False

    return logger


# Global logger instance
logger = setup_logging()
```

---

## Phase 2: Core Agent Logic

### 2.1 Database Connection Management

**File**: `reminder-agent/services/database.py`

```python
"""Database connection and session management."""

from sqlmodel import create_engine, Session, SQLModel
from contextlib import contextmanager
from typing import Generator
from config.settings import settings
from utils.logger import logger


# Create engine with connection pooling
engine = create_engine(
    settings.database_url,
    echo=False,  # Set to True for SQL logging in dev
    pool_size=10,
    max_overflow=5,
    pool_pre_ping=True,  # Test connections before use
    connect_args={"sslmode": "require"}
)


def init_db() -> None:
    """Initialize database tables.

    Creates tables if they don't exist.
    Should be called on agent startup.
    """
    try:
        SQLModel.metadata.create_all(engine)
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def test_connection() -> bool:
    """Test database connectivity.

    Returns:
        bool: True if connection successful
    """
    try:
        with Session(engine) as session:
            session.exec("SELECT 1")
        logger.info("Database connection test passed")
        return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """Get database session with automatic cleanup.

    Usage:
        with get_session() as session:
            results = session.exec(select(Task))

    Yields:
        Session: SQLModel database session
    """
    with Session(engine) as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
```

---

### 2.2 Task Reader Service

**File**: `reminder-agent/services/task_reader.py`

```python
"""Service to read tasks needing reminders from database."""

from sqlmodel import Session, select, and_, or_
from typing import List, Optional
from datetime import datetime, timedelta
from models.task import Task
from services.database import get_session
from config.settings import settings
from utils.logger import logger


class TaskReader:
    """Read and filter tasks that need reminders."""

    @staticmethod
    def get_tasks_needing_reminders() -> List[Task]:
        """Fetch tasks that need reminders within the lookahead window.

        Returns tasks where:
        - Not completed
        - Has reminder_time set
        - Reminder is due within next REMINDER_LOOKAHEAD_MINUTES

        Returns:
            List[Task]: Tasks needing reminders
        """
        try:
            with get_session() as session:
                now = datetime.utcnow()
                lookahead = now + timedelta(
                    minutes=settings.reminder_lookahead_minutes
                )

                # Build query
                statement = select(Task).where(
                    and_(
                        Task.completed == False,
                        Task.reminder_time.is_not(None)
                    )
                )

                tasks = session.exec(statement).all()

                # Filter in-memory for complex time logic
                # (Will optimize with better SQL in production)
                filtered_tasks = [
                    task for task in tasks
                    if TaskReader._should_send_reminder(task, now, lookahead)
                ]

                logger.info(
                    f"Found {len(filtered_tasks)} tasks needing reminders",
                    extra={"action": "task_query", "count": len(filtered_tasks)}
                )

                return filtered_tasks

        except Exception as e:
            logger.error(f"Error fetching tasks: {e}")
            return []

    @staticmethod
    def _should_send_reminder(
        task: Task,
        now: datetime,
        lookahead: datetime
    ) -> bool:
        """Check if task reminder should be sent now.

        Args:
            task: Task to check
            now: Current datetime
            lookahead: End of lookahead window

        Returns:
            bool: True if reminder should be sent
        """
        if not task.reminder_time:
            return False

        # For one-time tasks, direct comparison
        if task.recurrence_pattern == "none":
            return now <= task.reminder_time < lookahead

        # For recurring tasks, check if reminder_time (time component)
        # falls within current lookahead window
        # (Full logic implemented in ReminderCalculator)
        return True  # Let calculator handle complex logic

    @staticmethod
    def get_user_email(user_id: str) -> Optional[str]:
        """Fetch user email from database.

        Args:
            user_id: User ID

        Returns:
            Optional[str]: User email or None
        """
        # TODO: Implement after Better Auth integration
        # For now, return placeholder
        return f"{user_id}@example.com"
```

---

## Phase 3: Scheduling & Repeat Logic

### 3.1 Reminder Calculator Service

This is the most critical component. It handles all repeat type logic.

**File**: `reminder-agent/services/reminder_calculator.py`

```python
"""Calculate next reminder datetime for tasks."""

from datetime import datetime, date, time, timedelta
from typing import Optional
from dateutil.relativedelta import relativedelta
from models.task import Task
from utils.logger import logger
import pytz


class ReminderCalculator:
    """Calculate when to send reminders based on task settings."""

    @staticmethod
    def calculate_reminder_datetime(
        task: Task,
        now: Optional[datetime] = None
    ) -> Optional[datetime]:
        """Calculate the next reminder datetime for a task.

        Args:
            task: Task to calculate reminder for
            now: Current datetime (defaults to utcnow)

        Returns:
            Optional[datetime]: Next reminder datetime or None
        """
        if not task.reminder_time:
            return None

        now = now or datetime.utcnow()

        # Dispatch to specific handler based on recurrence pattern
        if task.recurrence_pattern == "none":
            return ReminderCalculator._calculate_one_time(task, now)
        elif task.recurrence_pattern == "daily":
            return ReminderCalculator._calculate_daily(task, now)
        elif task.recurrence_pattern == "weekly":
            return ReminderCalculator._calculate_weekly(task, now)
        elif task.recurrence_pattern == "monthly":
            return ReminderCalculator._calculate_monthly(task, now)
        else:
            logger.warning(
                f"Unknown recurrence pattern: {task.recurrence_pattern}",
                extra={"task_id": task.id}
            )
            return None

    @staticmethod
    def _calculate_one_time(task: Task, now: datetime) -> Optional[datetime]:
        """Calculate reminder for one-time task.

        Args:
            task: Task with recurrence_pattern='none'
            now: Current datetime

        Returns:
            Optional[datetime]: Reminder datetime if in future, else None
        """
        # reminder_time is the exact datetime to send
        if task.reminder_time > now:
            return task.reminder_time
        return None

    @staticmethod
    def _calculate_daily(task: Task, now: datetime) -> Optional[datetime]:
        """Calculate reminder for daily recurring task.

        Sends reminder at reminder_time every day until task completed.

        Args:
            task: Task with recurrence_pattern='daily'
            now: Current datetime

        Returns:
            Optional[datetime]: Next reminder datetime
        """
        # Extract time component from reminder_time
        reminder_time_obj = task.reminder_time.time()

        # Today's reminder datetime
        today_reminder = datetime.combine(now.date(), reminder_time_obj)

        if today_reminder > now:
            # Reminder hasn't happened today yet
            return today_reminder
        else:
            # Reminder already passed today, schedule for tomorrow
            tomorrow_reminder = today_reminder + timedelta(days=1)
            return tomorrow_reminder

    @staticmethod
    def _calculate_weekly(task: Task, now: datetime) -> Optional[datetime]:
        """Calculate reminder for weekly recurring task.

        Sends reminder on the same weekday as original reminder_time.

        Args:
            task: Task with recurrence_pattern='weekly'
            now: Current datetime

        Returns:
            Optional[datetime]: Next reminder datetime
        """
        # Get target weekday from original reminder_time
        target_weekday = task.reminder_time.weekday()  # 0=Monday, 6=Sunday
        reminder_time_obj = task.reminder_time.time()

        # Find next occurrence of target weekday
        days_until_target = (target_weekday - now.weekday()) % 7

        if days_until_target == 0:
            # Today is the target weekday
            today_reminder = datetime.combine(now.date(), reminder_time_obj)
            if today_reminder > now:
                return today_reminder
            else:
                # Already passed, schedule for next week
                next_week_reminder = today_reminder + timedelta(weeks=1)
                return next_week_reminder
        else:
            # Target weekday is in the future this week
            next_date = now.date() + timedelta(days=days_until_target)
            next_reminder = datetime.combine(next_date, reminder_time_obj)
            return next_reminder

    @staticmethod
    def _calculate_monthly(task: Task, now: datetime) -> Optional[datetime]:
        """Calculate reminder for monthly recurring task.

        Sends reminder on the same day of month as original reminder_time.
        Handles edge cases like Feb 31 → Feb 28/29.

        Args:
            task: Task with recurrence_pattern='monthly'
            now: Current datetime

        Returns:
            Optional[datetime]: Next reminder datetime
        """
        target_day = task.reminder_time.day
        reminder_time_obj = task.reminder_time.time()

        # Try to create reminder for this month
        try:
            this_month_date = now.date().replace(day=target_day)
        except ValueError:
            # Day doesn't exist in current month (e.g., Feb 31)
            # Use last day of month
            this_month_date = (
                now.date().replace(day=1) + relativedelta(months=1, days=-1)
            )

        this_month_reminder = datetime.combine(this_month_date, reminder_time_obj)

        if this_month_reminder > now:
            # Reminder hasn't happened this month yet
            return this_month_reminder
        else:
            # Already passed, schedule for next month
            try:
                next_month_date = (now.date() + relativedelta(months=1)).replace(day=target_day)
            except ValueError:
                # Day doesn't exist in next month
                next_month_date = (
                    now.date().replace(day=1) + relativedelta(months=2, days=-1)
                )

            next_month_reminder = datetime.combine(next_month_date, reminder_time_obj)
            return next_month_reminder

    @staticmethod
    def should_skip_reminder(task: Task, now: datetime) -> bool:
        """Check if reminder should be skipped.

        Skip conditions:
        - Task is completed
        - Reminder is more than 1 week past due_date (grace period)

        Args:
            task: Task to check
            now: Current datetime

        Returns:
            bool: True if should skip
        """
        if task.completed:
            return True

        if task.due_date and (now - task.due_date) > timedelta(weeks=1):
            logger.info(
                f"Skipping reminder for task {task.id}: > 1 week past due",
                extra={"task_id": task.id}
            )
            return True

        return False
```

---

### 3.2 Duplicate Checker Service

**File**: `reminder-agent/services/duplicate_checker.py`

```python
"""Check if reminder has already been sent."""

from datetime import datetime, timedelta
from sqlmodel import select, and_
from models.reminder_log import ReminderLog
from services.database import get_session
from config.constants import DUPLICATE_CHECK_TOLERANCE_SECONDS
from utils.logger import logger


class DuplicateChecker:
    """Prevent sending duplicate reminders."""

    @staticmethod
    def exists(task_id: int, reminder_datetime: datetime) -> bool:
        """Check if reminder already sent for this task and datetime.

        Uses tolerance window to account for slight timing differences.

        Args:
            task_id: Task ID
            reminder_datetime: Reminder datetime

        Returns:
            bool: True if duplicate exists
        """
        try:
            with get_session() as session:
                # Check for exact match or within tolerance window
                tolerance = timedelta(seconds=DUPLICATE_CHECK_TOLERANCE_SECONDS)
                start_window = reminder_datetime - tolerance
                end_window = reminder_datetime + tolerance

                statement = select(ReminderLog).where(
                    and_(
                        ReminderLog.task_id == task_id,
                        ReminderLog.reminder_datetime >= start_window,
                        ReminderLog.reminder_datetime <= end_window
                    )
                )

                result = session.exec(statement).first()

                if result:
                    logger.debug(
                        f"Duplicate reminder found for task {task_id}",
                        extra={"task_id": task_id, "reminder_datetime": reminder_datetime}
                    )
                    return True

                return False

        except Exception as e:
            logger.error(f"Error checking for duplicates: {e}")
            # Fail safe: assume no duplicate to avoid missing reminders
            return False
```

---

### 3.3 Timezone Utilities

**File**: `reminder-agent/utils/timezone.py`

```python
"""Timezone conversion utilities."""

from datetime import datetime
from typing import Optional
import pytz
from utils.logger import logger


def convert_to_user_timezone(
    dt: datetime,
    user_timezone: Optional[str] = None
) -> datetime:
    """Convert UTC datetime to user's timezone.

    Args:
        dt: UTC datetime
        user_timezone: Timezone string (e.g., 'America/New_York')

    Returns:
        datetime: Datetime in user's timezone
    """
    if not user_timezone:
        return dt  # Return UTC if no timezone specified

    try:
        utc_dt = dt.replace(tzinfo=pytz.UTC)
        user_tz = pytz.timezone(user_timezone)
        return utc_dt.astimezone(user_tz)
    except Exception as e:
        logger.warning(f"Failed to convert timezone: {e}. Using UTC.")
        return dt


def format_datetime_for_user(
    dt: datetime,
    user_timezone: Optional[str] = None
) -> str:
    """Format datetime for display in user's timezone.

    Args:
        dt: UTC datetime
        user_timezone: Timezone string

    Returns:
        str: Formatted datetime string
    """
    local_dt = convert_to_user_timezone(dt, user_timezone)
    return local_dt.strftime("%B %d, %Y at %I:%M %p")
```

---

## Phase 4: Email System

### 4.1 AI Email Generator

**File**: `reminder-agent/services/ai_email_generator.py`

```python
"""Generate personalized reminder emails using Gemini AI."""

from openai import OpenAI
from typing import Optional
from models.task import Task
from models.email_content import EmailContent
from config.settings import settings
from utils.logger import logger
from utils.timezone import format_datetime_for_user


class AIEmailGenerator:
    """Generate email content using Gemini AI."""

    def __init__(self):
        """Initialize Gemini client."""
        self.client = OpenAI(
            api_key=settings.gemini_api_key,
            base_url=settings.gemini_base_url
        )

    def generate(
        self,
        task: Task,
        user_name: Optional[str] = None,
        user_timezone: Optional[str] = None
    ) -> EmailContent:
        """Generate personalized reminder email.

        Args:
            task: Task to create reminder for
            user_name: User's name
            user_timezone: User's timezone

        Returns:
            EmailContent: Subject and body
        """
        try:
            # Generate email body using AI
            body = self._generate_body(task, user_name, user_timezone)

            # Generate subject line
            subject = self._generate_subject(task)

            return EmailContent(subject=subject, body=body)

        except Exception as e:
            logger.error(f"AI email generation failed: {e}. Using template.")
            return self._fallback_template(task, user_name, user_timezone)

    def _generate_body(
        self,
        task: Task,
        user_name: Optional[str],
        user_timezone: Optional[str]
    ) -> str:
        """Generate email body using Gemini.

        Args:
            task: Task to create reminder for
            user_name: User's name
            user_timezone: User's timezone

        Returns:
            str: Email body HTML
        """
        # Format dates for prompt
        due_date_str = (
            format_datetime_for_user(task.due_date, user_timezone)
            if task.due_date else "No due date set"
        )

        # Build prompt
        prompt = f"""
You are a professional task reminder assistant. Generate a concise,
motivating reminder email for the following task.

User: {user_name or 'there'}
Task Name: {task.title}
Description: {task.description or 'No description provided'}
Tags: {', '.join(task.tags) if task.tags else 'None'}
Due Date: {due_date_str}
Priority: {task.priority}
Recurrence: {task.recurrence_pattern}

Requirements:
- Professional but warm and friendly tone
- 2-3 sentences maximum
- Mention the task name and due date
- Add a brief motivational closing
- Output ONLY the email body text (no subject line)
- Do NOT include HTML tags - plain text only

Email body:
""".strip()

        # Call Gemini API
        response = self.client.chat.completions.create(
            model=settings.gemini_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=200
        )

        body_text = response.choices[0].message.content.strip()

        logger.info(
            f"Generated AI email for task {task.id}",
            extra={"task_id": task.id}
        )

        return body_text

    def _generate_subject(self, task: Task) -> str:
        """Generate email subject line.

        Args:
            task: Task to create subject for

        Returns:
            str: Subject line
        """
        # Priority-based emoji
        if task.priority == "HIGH":
            emoji = "🔴 URGENT"
        elif task.priority == "MEDIUM":
            emoji = "🟡"
        else:
            emoji = "📋"

        # Recurrence indicator
        if task.recurrence_pattern != "none":
            recurrence = f"[{task.recurrence_pattern.title()}]"
        else:
            recurrence = ""

        return f"{emoji} Reminder {recurrence}: {task.title}"

    def _fallback_template(
        self,
        task: Task,
        user_name: Optional[str],
        user_timezone: Optional[str]
    ) -> EmailContent:
        """Generate email using template (fallback when AI fails).

        Args:
            task: Task to create reminder for
            user_name: User's name
            user_timezone: User's timezone

        Returns:
            EmailContent: Subject and body
        """
        due_date_str = (
            format_datetime_for_user(task.due_date, user_timezone)
            if task.due_date else "No due date set"
        )

        body = f"""
Hi {user_name or 'there'},

This is a friendly reminder about your task: "{task.title}".

Due: {due_date_str}
Priority: {task.priority}

{f'Description: {task.description}' if task.description else ''}

Stay organized and keep up the great work!

Best regards,
{settings.sender_name}
""".strip()

        subject = self._generate_subject(task)

        return EmailContent(subject=subject, body=body)
```

**File**: `reminder-agent/models/email_content.py`

```python
"""Email content models."""

from pydantic import BaseModel


class EmailContent(BaseModel):
    """Email subject and body."""
    subject: str
    body: str
```

---

### 4.2 Email Sender Service

**File**: `reminder-agent/services/email_sender.py`

```python
"""Send emails via SMTP with retry logic."""

import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from models.task import Task
from models.email_content import EmailContent
from config.settings import settings
from utils.logger import logger


class EmailSender:
    """Send reminder emails via SMTP."""

    @staticmethod
    @retry(
        stop=stop_after_attempt(settings.retry_max_attempts),
        wait=wait_exponential(multiplier=settings.retry_backoff_multiplier, min=1, max=60),
        retry=retry_if_exception_type(aiosmtplib.SMTPException),
        reraise=True
    )
    async def send(
        to: str,
        subject: str,
        body: str,
        task: Task,
        user_name: Optional[str] = None
    ) -> bool:
        """Send email with retry logic.

        Args:
            to: Recipient email
            subject: Email subject
            body: Email body (plain text from AI)
            task: Task object for template data
            user_name: User's name

        Returns:
            bool: True if sent successfully
        """
        try:
            # Build HTML email from template
            html_body = EmailSender._build_html_email(
                body, task, user_name
            )

            # Create message
            message = MIMEMultipart("alternative")
            message["From"] = f"{settings.sender_name} <{settings.sender_email}>"
            message["To"] = to
            message["Subject"] = subject

            # Add plain text and HTML parts
            text_part = MIMEText(body, "plain")
            html_part = MIMEText(html_body, "html")

            message.attach(text_part)
            message.attach(html_part)

            # Send via SMTP
            await aiosmtplib.send(
                message,
                hostname=settings.smtp_host,
                port=settings.smtp_port,
                username=settings.smtp_user,
                password=settings.smtp_password,
                start_tls=True
            )

            logger.info(
                f"Email sent successfully to {to}",
                extra={"task_id": task.id, "email_to": to}
            )

            return True

        except aiosmtplib.SMTPException as e:
            logger.warning(
                f"SMTP error sending to {to}: {e}. Retrying...",
                extra={"task_id": task.id}
            )
            raise  # Retry via tenacity

        except Exception as e:
            logger.error(
                f"Unexpected error sending email: {e}",
                extra={"task_id": task.id}
            )
            return False

    @staticmethod
    def _build_html_email(
        ai_body: str,
        task: Task,
        user_name: Optional[str]
    ) -> str:
        """Build HTML email from template.

        Args:
            ai_body: AI-generated message
            task: Task object
            user_name: User's name

        Returns:
            str: HTML email body
        """
        # Read template
        with open("templates/email_template.html") as f:
            template_str = f.read()

        template = Template(template_str)

        # Render template
        html = template.render(
            user_name=user_name or "there",
            ai_message=ai_body,
            task_name=task.title,
            task_tag=', '.join(task.tags) if task.tags else "General",
            due_date=task.due_date.strftime("%B %d, %Y at %I:%M %p") if task.due_date else "No due date",
            importance=task.priority,
            importance_lower=task.priority.lower(),
            description=task.description,
            app_url=settings.app_url,
            task_id=task.id
        )

        return html
```

---

### 4.3 Email Template

**File**: `reminder-agent/templates/email_template.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Task Reminder</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
            margin: 0;
            padding: 0;
        }
        .container {
            max-width: 600px;
            margin: 20px auto;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px 20px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 24px;
            font-weight: 600;
        }
        .content {
            padding: 30px 20px;
        }
        .greeting {
            font-size: 16px;
            margin-bottom: 20px;
        }
        .ai-message {
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 15px 20px;
            margin: 20px 0;
            font-size: 15px;
            line-height: 1.6;
        }
        .task-details {
            background: #fff;
            border: 1px solid #e5e7eb;
            border-radius: 6px;
            padding: 20px;
            margin: 20px 0;
            border-left: 4px solid #10b981;
        }
        .task-details.high {
            border-left-color: #ef4444;
        }
        .task-details.medium {
            border-left-color: #f59e0b;
        }
        .task-details.low {
            border-left-color: #10b981;
        }
        .task-details h2 {
            margin: 0 0 15px 0;
            font-size: 20px;
            color: #1f2937;
        }
        .task-meta {
            display: flex;
            flex-direction: column;
            gap: 8px;
            font-size: 14px;
            color: #6b7280;
        }
        .task-meta-item {
            display: flex;
        }
        .task-meta-item strong {
            min-width: 100px;
            color: #374151;
        }
        .description {
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #e5e7eb;
            color: #4b5563;
        }
        .cta {
            text-align: center;
            margin: 30px 0;
        }
        .button {
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 30px;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 500;
            transition: transform 0.2s;
        }
        .button:hover {
            transform: translateY(-2px);
        }
        .footer {
            background: #f9fafb;
            padding: 20px;
            text-align: center;
            font-size: 12px;
            color: #6b7280;
            border-top: 1px solid #e5e7eb;
        }
        .footer a {
            color: #667eea;
            text-decoration: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📋 Task Reminder</h1>
        </div>

        <div class="content">
            <div class="greeting">
                Hi {{ user_name }},
            </div>

            <div class="ai-message">
                {{ ai_message }}
            </div>

            <div class="task-details {{ importance_lower }}">
                <h2>{{ task_name }}</h2>

                <div class="task-meta">
                    <div class="task-meta-item">
                        <strong>Tag:</strong>
                        <span>{{ task_tag }}</span>
                    </div>
                    <div class="task-meta-item">
                        <strong>Due Date:</strong>
                        <span>{{ due_date }}</span>
                    </div>
                    <div class="task-meta-item">
                        <strong>Priority:</strong>
                        <span>{{ importance }}</span>
                    </div>
                </div>

                {% if description %}
                <div class="description">
                    <strong>Description:</strong><br>
                    {{ description }}
                </div>
                {% endif %}
            </div>

            <div class="cta">
                <a href="{{ app_url }}/tasks/{{ task_id }}" class="button">
                    View Task
                </a>
            </div>
        </div>

        <div class="footer">
            <p>You're receiving this because you set a reminder for this task.</p>
            <p>
                <a href="{{ app_url }}/settings/notifications">Manage notification preferences</a>
            </p>
        </div>
    </div>
</body>
</html>
```

---

### 4.4 Delivery Tracker

**File**: `reminder-agent/services/delivery_tracker.py`

```python
"""Track email delivery status in reminder_log."""

from datetime import datetime
from models.reminder_log import ReminderLog, DeliveryStatus
from services.database import get_session
from utils.logger import logger


class DeliveryTracker:
    """Log reminder delivery attempts and status."""

    @staticmethod
    def log_success(
        task_id: int,
        user_id: str,
        reminder_datetime: datetime,
        email_to: str,
        email_subject: str,
        email_body: str
    ) -> None:
        """Log successful reminder delivery.

        Args:
            task_id: Task ID
            user_id: User ID
            reminder_datetime: Reminder datetime
            email_to: Recipient email
            email_subject: Email subject
            email_body: Email body
        """
        try:
            with get_session() as session:
                log_entry = ReminderLog(
                    task_id=task_id,
                    user_id=user_id,
                    reminder_datetime=reminder_datetime,
                    email_to=email_to,
                    email_subject=email_subject,
                    email_body=email_body,
                    delivery_status=DeliveryStatus.SENT.value,
                    sent_at=datetime.utcnow()
                )
                session.add(log_entry)
                session.commit()

                logger.info(
                    f"Logged successful delivery for task {task_id}",
                    extra={"task_id": task_id, "user_id": user_id}
                )

        except Exception as e:
            logger.error(f"Failed to log delivery: {e}")

    @staticmethod
    def log_failure(
        task_id: int,
        user_id: str,
        reminder_datetime: datetime,
        email_to: str,
        email_subject: str,
        email_body: str,
        error_message: str,
        retry_count: int = 0
    ) -> None:
        """Log failed reminder delivery.

        Args:
            task_id: Task ID
            user_id: User ID
            reminder_datetime: Reminder datetime
            email_to: Recipient email
            email_subject: Email subject
            email_body: Email body
            error_message: Error description
            retry_count: Number of retries attempted
        """
        try:
            with get_session() as session:
                log_entry = ReminderLog(
                    task_id=task_id,
                    user_id=user_id,
                    reminder_datetime=reminder_datetime,
                    email_to=email_to,
                    email_subject=email_subject,
                    email_body=email_body,
                    delivery_status=DeliveryStatus.FAILED.value,
                    error_message=error_message,
                    retry_count=retry_count,
                    sent_at=datetime.utcnow()
                )
                session.add(log_entry)
                session.commit()

                logger.error(
                    f"Logged failed delivery for task {task_id}: {error_message}",
                    extra={"task_id": task_id, "user_id": user_id}
                )

        except Exception as e:
            logger.error(f"Failed to log error: {e}")
```

---

## Phase 5: Testing & Production Readiness

### 5.1 Main Agent Job

**File**: `reminder-agent/jobs/reminder_processor.py`

```python
"""Main scheduled job to process reminders."""

from datetime import datetime
from services.task_reader import TaskReader
from services.reminder_calculator import ReminderCalculator
from services.duplicate_checker import DuplicateChecker
from services.ai_email_generator import AIEmailGenerator
from services.email_sender import EmailSender
from services.delivery_tracker import DeliveryTracker
from services.database import get_session
from models.agent_state import AgentState, AgentStatus
from utils.logger import logger


class ReminderProcessor:
    """Process reminders for all tasks."""

    def __init__(self):
        """Initialize processor with dependencies."""
        self.ai_generator = AIEmailGenerator()

    async def run(self) -> None:
        """Execute reminder processing cycle."""
        logger.info("Starting reminder processing cycle")

        tasks_processed = 0
        reminders_sent = 0
        errors_count = 0

        try:
            # 1. Update agent state
            self._update_agent_state(AgentStatus.RUNNING)

            # 2. Fetch tasks needing reminders
            tasks = TaskReader.get_tasks_needing_reminders()
            logger.info(f"Found {len(tasks)} tasks to process")

            # 3. Process each task
            for task in tasks:
                tasks_processed += 1

                try:
                    # Skip if task should not get reminder
                    now = datetime.utcnow()
                    if ReminderCalculator.should_skip_reminder(task, now):
                        continue

                    # Calculate reminder datetime
                    reminder_dt = ReminderCalculator.calculate_reminder_datetime(task, now)
                    if not reminder_dt:
                        continue

                    # Check for duplicates
                    if DuplicateChecker.exists(task.id, reminder_dt):
                        logger.debug(f"Skipping duplicate reminder for task {task.id}")
                        continue

                    # Get user info (TODO: integrate with Better Auth)
                    user_email = TaskReader.get_user_email(task.user_id)
                    if not user_email:
                        logger.warning(f"No email found for user {task.user_id}")
                        continue

                    # Generate AI email
                    email_content = self.ai_generator.generate(
                        task=task,
                        user_name=None,  # TODO: get from user table
                        user_timezone=None  # TODO: get from user table
                    )

                    # Send email
                    success = await EmailSender.send(
                        to=user_email,
                        subject=email_content.subject,
                        body=email_content.body,
                        task=task,
                        user_name=None
                    )

                    # Log delivery
                    if success:
                        DeliveryTracker.log_success(
                            task_id=task.id,
                            user_id=task.user_id,
                            reminder_datetime=reminder_dt,
                            email_to=user_email,
                            email_subject=email_content.subject,
                            email_body=email_content.body
                        )
                        reminders_sent += 1
                        logger.info(f"✅ Reminder sent: {task.title} → {user_email}")
                    else:
                        DeliveryTracker.log_failure(
                            task_id=task.id,
                            user_id=task.user_id,
                            reminder_datetime=reminder_dt,
                            email_to=user_email,
                            email_subject=email_content.subject,
                            email_body=email_content.body,
                            error_message="Email send failed after retries"
                        )
                        errors_count += 1

                except Exception as e:
                    logger.error(f"Error processing task {task.id}: {e}")
                    errors_count += 1

            # 4. Update final state
            self._update_agent_state(
                AgentStatus.RUNNING,
                tasks_processed=tasks_processed,
                reminders_sent=reminders_sent,
                errors_count=errors_count
            )

            logger.info(
                f"Cycle complete: {tasks_processed} processed, {reminders_sent} sent, {errors_count} errors"
            )

        except Exception as e:
            logger.critical(f"Critical error in reminder processor: {e}")
            self._update_agent_state(AgentStatus.ERROR, errors_count=1)

    def _update_agent_state(
        self,
        status: AgentStatus,
        tasks_processed: int = 0,
        reminders_sent: int = 0,
        errors_count: int = 0
    ) -> None:
        """Update agent state in database.

        Args:
            status: Agent status
            tasks_processed: Tasks processed this cycle
            reminders_sent: Reminders sent this cycle
            errors_count: Errors this cycle
        """
        try:
            with get_session() as session:
                # Get or create state record
                state = session.query(AgentState).first()
                if not state:
                    state = AgentState(
                        last_check_at=datetime.utcnow(),
                        status=status.value
                    )
                    session.add(state)
                else:
                    state.last_check_at = datetime.utcnow()
                    state.status = status.value
                    state.tasks_processed += tasks_processed
                    state.reminders_sent += reminders_sent
                    state.errors_count += errors_count
                    state.updated_at = datetime.utcnow()

                session.commit()

        except Exception as e:
            logger.error(f"Failed to update agent state: {e}")
```

---

### 5.2 Main Entry Point

**File**: `reminder-agent/main.py`

```python
"""AI Reminder Agent - Main entry point."""

import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from jobs.reminder_processor import ReminderProcessor
from services.database import init_db, test_connection
from config.settings import settings
from utils.logger import logger


async def startup():
    """Agent startup sequence."""
    logger.info("🚀 Starting AI Reminder Agent")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Polling interval: {settings.polling_interval_minutes} minutes")

    # 1. Test database connection
    if not test_connection():
        logger.critical("Database connection failed. Exiting.")
        raise SystemExit(1)

    # 2. Initialize database tables
    init_db()

    # 3. Validate Gemini API (optional)
    # TODO: Add API health check

    logger.info("✅ Startup complete")


async def main():
    """Main agent loop."""
    # Run startup
    await startup()

    # Create scheduler
    scheduler = AsyncIOScheduler()

    # Create processor
    processor = ReminderProcessor()

    # Schedule reminder processing job
    scheduler.add_job(
        processor.run,
        trigger=IntervalTrigger(minutes=settings.polling_interval_minutes),
        id="reminder_processor",
        name="Process Reminders",
        replace_existing=True
    )

    # Start scheduler
    scheduler.start()
    logger.info(f"⏰ Scheduler started (every {settings.polling_interval_minutes} min)")

    # Keep alive
    try:
        while True:
            await asyncio.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        logger.info("🛑 Shutting down gracefully...")
        scheduler.shutdown()
        logger.info("Goodbye!")


if __name__ == "__main__":
    asyncio.run(main())
```

---

### 5.3 Unit Tests

**File**: `reminder-agent/tests/test_calculator.py`

```python
"""Tests for ReminderCalculator."""

import pytest
from datetime import datetime, timedelta
from freezegun import freeze_time
from models.task import Task
from services.reminder_calculator import ReminderCalculator


class TestReminderCalculator:
    """Test reminder calculation for all repeat types."""

    @freeze_time("2025-01-15 10:00:00")
    def test_one_time_future(self):
        """One-time reminder in future should return reminder_time."""
        task = Task(
            id=1,
            user_id="user123",
            title="Test Task",
            reminder_time=datetime(2025, 1, 15, 14, 0, 0),
            recurrence_pattern="none",
            completed=False
        )

        result = ReminderCalculator.calculate_reminder_datetime(task)
        assert result == datetime(2025, 1, 15, 14, 0, 0)

    @freeze_time("2025-01-15 10:00:00")
    def test_one_time_past(self):
        """One-time reminder in past should return None."""
        task = Task(
            id=1,
            user_id="user123",
            title="Test Task",
            reminder_time=datetime(2025, 1, 14, 14, 0, 0),
            recurrence_pattern="none",
            completed=False
        )

        result = ReminderCalculator.calculate_reminder_datetime(task)
        assert result is None

    @freeze_time("2025-01-15 10:00:00")
    def test_daily_today_future(self):
        """Daily reminder today (not yet sent) should return today."""
        task = Task(
            id=1,
            user_id="user123",
            title="Test Task",
            reminder_time=datetime(2025, 1, 15, 14, 0, 0),
            recurrence_pattern="daily",
            completed=False
        )

        result = ReminderCalculator.calculate_reminder_datetime(task)
        assert result == datetime(2025, 1, 15, 14, 0, 0)

    @freeze_time("2025-01-15 16:00:00")
    def test_daily_today_past(self):
        """Daily reminder today (already sent) should return tomorrow."""
        task = Task(
            id=1,
            user_id="user123",
            title="Test Task",
            reminder_time=datetime(2025, 1, 15, 14, 0, 0),
            recurrence_pattern="daily",
            completed=False
        )

        result = ReminderCalculator.calculate_reminder_datetime(task)
        assert result == datetime(2025, 1, 16, 14, 0, 0)

    @freeze_time("2025-01-15 10:00:00")  # Wednesday
    def test_weekly_same_weekday_future(self):
        """Weekly reminder on same weekday (not yet sent) should return today."""
        task = Task(
            id=1,
            user_id="user123",
            title="Test Task",
            reminder_time=datetime(2025, 1, 15, 14, 0, 0),  # Wednesday
            recurrence_pattern="weekly",
            completed=False
        )

        result = ReminderCalculator.calculate_reminder_datetime(task)
        assert result == datetime(2025, 1, 15, 14, 0, 0)

    @freeze_time("2025-01-15 10:00:00")  # Wednesday
    def test_weekly_different_weekday(self):
        """Weekly reminder on different weekday should return next occurrence."""
        task = Task(
            id=1,
            user_id="user123",
            title="Test Task",
            reminder_time=datetime(2025, 1, 13, 14, 0, 0),  # Monday
            recurrence_pattern="weekly",
            completed=False
        )

        result = ReminderCalculator.calculate_reminder_datetime(task)
        # Next Monday is Jan 20
        assert result == datetime(2025, 1, 20, 14, 0, 0)

    @freeze_time("2025-01-15 10:00:00")
    def test_monthly_same_day_future(self):
        """Monthly reminder on same day (not yet sent) should return this month."""
        task = Task(
            id=1,
            user_id="user123",
            title="Test Task",
            reminder_time=datetime(2025, 1, 15, 14, 0, 0),
            recurrence_pattern="monthly",
            completed=False
        )

        result = ReminderCalculator.calculate_reminder_datetime(task)
        assert result == datetime(2025, 1, 15, 14, 0, 0)

    @freeze_time("2025-01-15 16:00:00")
    def test_monthly_same_day_past(self):
        """Monthly reminder on same day (already sent) should return next month."""
        task = Task(
            id=1,
            user_id="user123",
            title="Test Task",
            reminder_time=datetime(2025, 1, 15, 14, 0, 0),
            recurrence_pattern="monthly",
            completed=False
        )

        result = ReminderCalculator.calculate_reminder_datetime(task)
        assert result == datetime(2025, 2, 15, 14, 0, 0)

    @freeze_time("2025-02-15 10:00:00")
    def test_monthly_day_31_february(self):
        """Monthly reminder on day 31 in Feb should use last day (28/29)."""
        task = Task(
            id=1,
            user_id="user123",
            title="Test Task",
            reminder_time=datetime(2025, 1, 31, 14, 0, 0),
            recurrence_pattern="monthly",
            completed=False
        )

        result = ReminderCalculator.calculate_reminder_datetime(task)
        # Feb 2025 has 28 days
        assert result == datetime(2025, 2, 28, 14, 0, 0)
```

---

## Critical Design Decisions

### Decision 1: APScheduler vs Celery

**Context**: Need to schedule periodic reminder processing.

**Options**:
1. **APScheduler** (in-process)
   - ✅ Simple setup, no external dependencies
   - ✅ Sufficient for MVP (<50k users)
   - ❌ Single point of failure
   - ❌ Cannot scale horizontally

2. **Celery + Redis** (distributed)
   - ✅ Horizontal scaling
   - ✅ Fault tolerance
   - ❌ Complex setup (Redis, workers, beat scheduler)
   - ❌ Overkill for MVP

**Decision**: Start with **APScheduler** for MVP, migrate to Celery when scaling needed.

**Rationale**: YAGNI principle - don't add complexity until proven necessary.

---

### Decision 2: Gemini API Fallback Strategy

**Context**: Gemini API may fail or have rate limits.

**Options**:
1. **Skip reminder** if AI fails
   - ❌ Users miss reminders

2. **Template-based fallback**
   - ✅ Guarantee reminder delivery
   - ✅ Still professional
   - ❌ Less personalized

**Decision**: **Template-based fallback** with error logging.

**Rationale**: Reliability > Personalization. Users prefer generic reminder over no reminder.

---

### Decision 3: Timezone Handling

**Context**: Users in different timezones expect localized reminder times.

**Options**:
1. **Store all times in UTC, convert on display**
   - ✅ Standard practice
   - ✅ Avoids DST issues
   - ❌ Requires user timezone in DB

2. **Store times in user's local timezone**
   - ❌ Complex DST handling
   - ❌ Migration headaches

**Decision**: **UTC storage + user timezone conversion**.

**Rationale**: Industry best practice. Add `timezone` column to `users` table in future.

---

### Decision 4: Duplicate Prevention

**Context**: Must never send duplicate reminders.

**Options**:
1. **UNIQUE constraint on (task_id, reminder_datetime)**
   - ✅ Database-level guarantee
   - ✅ Race condition protection
   - ❌ Exact datetime matching only

2. **Application-level cache (Redis)**
   - ✅ Flexible matching (time windows)
   - ❌ Not durable (cache eviction)

**Decision**: **UNIQUE constraint + tolerance window** (check ±60 seconds).

**Rationale**: Database constraints are most reliable. Tolerance handles timing variations.

---

## Deployment Strategy

### Development Environment

```bash
# 1. Setup virtual environment
cd reminder-agent
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with real credentials

# 4. Run database migration
psql $DATABASE_URL < ../backend/migrations/001_add_reminder_tables.sql

# 5. Start agent
python main.py
```

### Production Deployment (Docker)

**Dockerfile**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run agent
CMD ["python", "main.py"]
```

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  reminder-agent:
    build:
      context: ./reminder-agent
      dockerfile: Dockerfile
    container_name: todo-reminder-agent
    restart: unless-stopped
    env_file:
      - ./reminder-agent/.env
    depends_on:
      - postgres
    networks:
      - todo-network
    healthcheck:
      test: ["CMD", "python", "-c", "from services.database import test_connection; exit(0 if test_connection() else 1)"]
      interval: 5m
      timeout: 10s
      retries: 3

networks:
  todo-network:
    external: true
```

---

## Rollback Plan

### If Agent Causes Issues

1. **Stop the agent**:
   ```bash
   docker stop todo-reminder-agent
   ```

2. **Verify no data corruption**:
   ```sql
   SELECT COUNT(*) FROM reminder_log;
   SELECT * FROM agent_state;
   ```

3. **Restore from backup** (if needed):
   ```bash
   # Restore database from snapshot
   pg_restore -d $DATABASE_URL backup.dump
   ```

4. **Rollback database migration**:
   ```sql
   DROP TABLE IF EXISTS reminder_log;
   DROP TABLE IF EXISTS agent_state;
   ```

---

## Next Steps After Implementation

1. **Monitor metrics** (first week):
   - Reminders sent/day
   - Email delivery success rate
   - Gemini API latency
   - Duplicate prevention hits

2. **User feedback collection**:
   - Survey: Email quality rating
   - Track: Unsubscribe rate
   - Monitor: Support tickets

3. **Performance optimization**:
   - Add database indexes if slow queries detected
   - Cache user data (email, timezone) in Redis
   - Batch email sending

4. **Future enhancements**:
   - SMS reminders (Twilio)
   - Push notifications (FCM)
   - User preferences UI
   - Smart scheduling (AI-suggested times)

---

**Document Status**: Ready for Implementation
**Next Action**: Review plan → Break into tasks (`/sp.tasks`)
