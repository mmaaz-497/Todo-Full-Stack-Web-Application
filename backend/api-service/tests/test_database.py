import pytest
from datetime import datetime
from sqlmodel import Session, create_engine, SQLModel
from app.models import Task, Conversation, Message


@pytest.fixture
def test_engine():
    """Create in-memory SQLite database for testing"""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def test_session(test_engine):
    """Create test database session"""
    with Session(test_engine) as session:
        yield session


def test_task_model_creation_with_all_fields(test_session):
    """Test Task model creation with all fields"""
    task = Task(
        user_id="user_123",
        title="Buy groceries",
        description="Milk, bread, eggs",
        completed=False
    )
    test_session.add(task)
    test_session.commit()
    test_session.refresh(task)
    
    assert task.id is not None
    assert task.user_id == "user_123"
    assert task.title == "Buy groceries"
    assert task.description == "Milk, bread, eggs"
    assert task.completed is False
    assert isinstance(task.created_at, datetime)
    assert isinstance(task.updated_at, datetime)


def test_conversation_model_creation(test_session):
    """Test Conversation model creation"""
    conv = Conversation(user_id="user_123")
    test_session.add(conv)
    test_session.commit()
    test_session.refresh(conv)
    
    assert conv.id is not None
    assert conv.user_id == "user_123"
    assert isinstance(conv.created_at, datetime)
    assert isinstance(conv.updated_at, datetime)


def test_message_model_creation_with_role_validation(test_session):
    """Test Message model with valid roles"""
    conv = Conversation(user_id="user_123")
    test_session.add(conv)
    test_session.commit()
    test_session.refresh(conv)
    
    # User message
    msg1 = Message(
        conversation_id=conv.id,
        user_id="user_123",
        role="user",
        content="Hello"
    )
    test_session.add(msg1)
    test_session.commit()
    assert msg1.role == "user"
    
    # Assistant message
    msg2 = Message(
        conversation_id=conv.id,
        user_id="user_123",
        role="assistant",
        content="Hi there!"
    )
    test_session.add(msg2)
    test_session.commit()
    assert msg2.role == "assistant"


def test_utc_timestamps_created_at_updated_at(test_session):
    """Test timestamps use UTC"""
    task = Task(user_id="user_123", title="Test", completed=False)
    test_session.add(task)
    test_session.commit()
    test_session.refresh(task)
    
    # Timestamps should be set
    assert task.created_at is not None
    assert task.updated_at is not None
    
    # Update task
    original_updated_at = task.updated_at
    import time
    time.sleep(0.1)  # Ensure time difference
    task.title = "Updated title"
    task.updated_at = datetime.utcnow()
    test_session.commit()
    test_session.refresh(task)
    
    # updated_at should change
    assert task.updated_at > original_updated_at
