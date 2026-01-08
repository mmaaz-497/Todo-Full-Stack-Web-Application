from sqlmodel import create_engine, Session, SQLModel
from config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_size=5,
    max_overflow=15,
    pool_pre_ping=True,
    echo=False
)

def init_db():
    """Create tables if they don't exist"""
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
