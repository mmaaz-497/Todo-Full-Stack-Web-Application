"""Database connection and session management for FastAPI backend.

This module provides:
- Database engine creation with SQLModel
- Session management via dependency injection
- Connection pooling configuration
"""

from sqlmodel import SQLModel, create_engine, Session
from typing import Generator
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Create engine with connection pooling
# pool_size: Number of connections to keep open
# max_overflow: Number of additional connections if pool is full
# pool_pre_ping: Test connections before using them
# Note: sslmode should be set in DATABASE_URL if needed (e.g., ?sslmode=require)
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL query logging
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
)


def create_db_and_tables():
    """Create all database tables defined in SQLModel models.

    This should be called on application startup.
    """
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Dependency injection for database sessions.

    Usage in FastAPI endpoints:
        @app.get("/tasks")
        def get_tasks(session: Session = Depends(get_session)):
            # Use session here
            pass

    Yields:
        Session: SQLModel database session
    """
    with Session(engine) as session:
        yield session
