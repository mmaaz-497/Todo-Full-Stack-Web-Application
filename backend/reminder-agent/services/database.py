"""Database connection and session management.

This module provides database connectivity with connection pooling
for the reminder agent. All database operations should use the
get_session() context manager to ensure proper cleanup.

Usage:
    from services.database import get_session, init_db, test_connection

    # Initialize tables on startup
    init_db()

    # Use in agent code
    with get_session() as session:
        tasks = session.exec(select(Task)).all()
"""

from sqlmodel import create_engine, Session, SQLModel, text
from contextlib import contextmanager
from typing import Generator
from config.settings import settings
from utils.logger import logger


# Create database engine with connection pooling
#
# Configuration:
# - pool_size=10: Maintain 10 permanent database connections
# - max_overflow=5: Allow up to 5 additional connections (15 total max)
# - pool_pre_ping=True: Test connection before use (handles stale connections)
# - connect_args: SSL required for Neon serverless PostgreSQL
  # Modify database URL to use psycopg (version 3) driver
database_url = settings.database_url.replace("postgresql://", "postgresql+psycopg://")

engine = create_engine(
      database_url,
      echo=False,
      pool_size=10,
      max_overflow=5,
      pool_pre_ping=True,
      connect_args={"prepare_threshold": 0}
  )


def init_db() -> None:
    """Initialize database tables for reminder agent.

    Creates tables for all SQLModel models DEFINED IN THIS AGENT:
    - models.reminder_log.ReminderLog
    - models.agent_state.AgentState

    NOTE: Does NOT create the 'user' table - that is managed by auth-service.
    The User model is imported for querying only.

    This is idempotent - safe to call multiple times.
    Should be called once on agent startup.

    Raises:
        Exception: If database connection or table creation fails
    """
    try:
        # Import User model to register it with SQLModel metadata
        # This allows queries but won't create the table
        from models import User  # noqa: F401

        # Create only tables for agent-owned models (ReminderLog, AgentState)
        # The User table already exists from auth-service migrations
        SQLModel.metadata.create_all(engine)
        logger.info("✅ Database tables initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        raise


def test_connection() -> bool:
    """Test database connectivity.

    Attempts to connect to the database and execute a simple query.
    Use this for health checks and startup validation.

    Returns:
        bool: True if connection successful, False otherwise

    Example:
        >>> if not test_connection():
        ...     logger.critical("Cannot connect to database!")
        ...     sys.exit(1)
    """
    try:
        with Session(engine) as session:
            # Execute simple query to test connection
            session.exec(text("SELECT 1"))
        logger.info("✅ Database connection test passed")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection test failed: {e}")
        return False


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """Get database session with automatic cleanup.

    This context manager handles the complete session lifecycle:
    1. Creates a new session
    2. Yields session for use
    3. Commits changes on success
    4. Rolls back on exception
    5. Always closes session

    Usage:
        with get_session() as session:
            task = session.get(Task, task_id)
            task.completed = True
            # Automatic commit on exit
            # Automatic rollback if exception raised
            # Session always closed

    Yields:
        Session: SQLModel database session

    Example:
        >>> from sqlmodel import select
        >>> with get_session() as session:
        ...     tasks = session.exec(select(Task)).all()
        ...     print(f"Found {len(tasks)} tasks")
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
