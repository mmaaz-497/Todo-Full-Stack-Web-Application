# AI Task Reminder Agent - Complete Implementation

This document contains the complete implementation of the AI Task Reminder Agent with all core modules.

## 📁 Project Structure

```
reminder-agent/
├── config/
│   ├── __init__.py ✅
│   ├── settings.py ✅
│   └── constants.py ✅
├── models/
│   ├── __init__.py
│   ├── reminder_log.py ✅
│   ├── agent_state.py ✅
│   └── email_content.py ✅
├── services/
│   ├── __init__.py
│   ├── database.py (see below)
│   ├── task_reader.py (see below)
│   ├── reminder_calculator.py (see below)
│   ├── duplicate_checker.py (see below)
│   ├── ai_email_generator.py (see below)
│   ├── email_sender.py (see below)
│   └── delivery_tracker.py (see below)
├── jobs/
│   ├── __init__.py
│   └── reminder_processor.py (see below)
├── utils/
│   ├── __init__.py
│   ├── logger.py ✅
│   └── timezone.py ✅
├── templates/
│   └── email_template.html (see below)
├── main.py (see below)
├── requirements.txt ✅
└── .env.example ✅
```

---

## 🗄️ services/database.py

```python
"""Database connection and session management.

This module provides database connectivity with connection pooling
for the reminder agent.

Usage:
    from services.database import get_session, init_db, test_connection

    # Initialize tables on startup
    init_db()

    # Use in agent code
    with get_session() as session:
        tasks = session.exec(select(Task)).all()
"""

from sqlmodel import create_engine, Session, SQLModel
from contextlib import contextmanager
from typing import Generator
from config.settings import settings
from utils.logger import logger


# Create database engine with connection pooling
# pool_size: Number of permanent connections
# max_overflow: Additional connections if pool exhausted
# pool_pre_ping: Test connection before using (handles stale connections)
engine = create_engine(
    settings.database_url,
    echo=False,  # Set to True to log SQL queries (debugging)
    pool_size=10,  # 10 permanent connections
    max_overflow=5,  # Up to 15 total connections
    pool_pre_ping=True,  # Test connection health before use
    connect_args={"sslmode": "require"}  # Required for Neon
)


def init_db() -> None:
    """Initialize database tables.

    Creates tables if they don't exist. Should be called on agent startup.
    This is idempotent - safe to call multiple times.

    Raises:
        Exception: If database connection or table creation fails
    """
    try:
        SQLModel.metadata.create_all(engine)
        logger.info("✅ Database tables initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        raise


def test_connection() -> bool:
    """Test database connectivity.

    Returns:
        bool: True if connection successful, False otherwise

    Example:
        if not test_connection():
            logger.critical("Cannot connect to database!")
            sys.exit(1)
    """
    try:
        with Session(engine) as session:
            # Execute simple query to test connection
            session.exec("SELECT 1")
        logger.info("✅ Database connection test passed")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection test failed: {e}")
        return False


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """Get database session with automatic cleanup.

    This context manager handles session lifecycle:
    - Creates session
    - Commits on success
    - Rolls back on error
    - Always closes session

    Usage:
        with get_session() as session:
            tasks = session.exec(select(Task)).all()
            # Automatic commit on exit
            # Automatic rollback on exception
            # Automatic close always

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

## 📊 services/task_reader.py

```python
"""Task reading service for fetching tasks needing reminders.

This service queries the database for tasks with upcoming reminders
and returns them for processing by the agent.
"""

from sqlmodel import Session, select, and_
from typing import List, Optional
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from backend (reuse existing Task model)
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'backend'))
from models import Task

from services.database import get_session
from config.settings import settings
from utils.logger import logger


class TaskReader:
    """Read and filter tasks that need reminders."""

    @staticmethod
    def get_tasks_needing_reminders() -> List[Task]:
        """Fetch tasks that need reminders within the lookahead window.

        Query logic:
        1. Task must not be completed
        2. Task must have reminder_time set
        3. Reminder must be due within next REMINDER_LOOKAHEAD_MINUTES

        Returns:
            List[Task]: Tasks needing reminders

        Example:
            >>> tasks = TaskReader.get_tasks_needing_reminders()
            >>> for task in tasks:
            ...     print(f"Reminder for: {task.title}")
        """
        try:
            with get_session() as session:
                now = datetime.utcnow()
                lookahead = now + timedelta(
                    minutes=settings.reminder_lookahead_minutes
                )

                # Build SQL query
                # SELECT * FROM tasks WHERE
                #   completed = false
                #   AND reminder_time IS NOT NULL
                statement = select(Task).where(
                    and_(
                        Task.completed == False,
                        Task.reminder_time.is_not(None)
                    )
                )

                tasks = session.exec(statement).all()

                # Filter in-memory for complex time logic
                # (More efficient SQL query can be implemented later)
                filtered_tasks = [
                    task for task in tasks
                    if TaskReader._should_process_now(task, now, lookahead)
                ]

                logger.info(
                    f"📥 Found {len(filtered_tasks)} tasks needing reminders",
                    extra={"action": "task_query", "count": len(filtered_tasks)}
                )

                return filtered_tasks

        except Exception as e:
            logger.error(f"❌ Error fetching tasks: {e}", extra={"action": "task_query"})
            return []

    @staticmethod
    def _should_process_now(
        task: Task,
        now: datetime,
        lookahead: datetime
    ) -> bool:
        """Check if task reminder should be processed in this cycle.

        For one-time tasks: Check if reminder_time within window
        For recurring tasks: Always return True (calculator decides)

        Args:
            task: Task to check
            now: Current datetime
            lookahead: End of lookahead window

        Returns:
            bool: True if task should be processed
        """
        if not task.reminder_time:
            return False

        # For one-time tasks (recurrence_pattern = "none")
        if task.recurrence_pattern == "none":
            return now <= task.reminder_time < lookahead

        # For recurring tasks, let ReminderCalculator decide timing
        return True

    @staticmethod
    def get_user_email(user_id: str) -> Optional[str]:
        """Fetch user email from database.

        TODO: Integrate with Better Auth user table

        Args:
            user_id: User ID

        Returns:
            Optional[str]: User email or None

        Note:
            Currently returns placeholder. In production, query:
            SELECT email FROM users WHERE id = user_id
        """
        # TODO: Implement Better Auth integration
        # For now, return placeholder
        # In production:
        # with get_session() as session:
        #     user = session.exec(select(User).where(User.id == user_id)).first()
        #     return user.email if user else None

        return f"{user_id}@example.com"
```

---

I'll continue with the remaining implementation files. Due to length, let me create them as separate files:
