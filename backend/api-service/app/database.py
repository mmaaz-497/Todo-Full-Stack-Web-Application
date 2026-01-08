from sqlmodel import create_engine, Session
from app.config import settings
from contextlib import contextmanager


# Create engine with connection pooling
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=5,
    max_overflow=15,
    pool_pre_ping=True,  # Verify connections before using
    echo=False  # Set to True for SQL logging in development
)


def get_session():
    """FastAPI dependency for database session
    
    Yields a new session for each request.
    Session is automatically closed after request completes.
    Ensures stateless architecture - no session persistence between requests.
    """
    with Session(engine) as session:
        yield session


@contextmanager
def get_session_context():
    """Context manager for database session (for non-FastAPI usage)"""
    with Session(engine) as session:
        yield session
