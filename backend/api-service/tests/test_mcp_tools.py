import pytest
from datetime import datetime
from sqlmodel import Session, create_engine, SQLModel, select
from app.models import Task
from app.mcp_server import add_task, list_tasks, complete_task, delete_task, update_task


@pytest.fixture
def test_engine():
    """Create in-memory database for testing"""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def test_session(test_engine):
    """Create test session"""
    with Session(test_engine) as session:
        yield session


# ========== add_task TESTS ==========

def test_add_task_creates_task_with_valid_inputs(test_session):
    """Test add_task creates task with user_id, title, description"""
    result = add_task(
        session=test_session,
        user_id="user_123",
        title="Buy groceries",
        description="Milk, bread, eggs"
    )
    
    assert result["status"] == "pending"
    assert result["title"] == "Buy groceries"
    assert "task_id" in result
    
    # Verify in database
    task = test_session.get(Task, result["task_id"])
    assert task.title == "Buy groceries"
    assert task.description == "Milk, bread, eggs"
    assert task.completed is False


def test_add_task_rejects_empty_title(test_session):
    """Test add_task rejects empty title"""
    with pytest.raises(ValueError, match="title cannot be empty"):
        add_task(
            session=test_session,
            user_id="user_123",
            title=""
        )


# ========== list_tasks TESTS ==========

def test_list_tasks_returns_all_tasks_for_user(test_session):
    """Test list_tasks returns all tasks when status='all'"""
    task1 = Task(user_id="user_123", title="Task 1", completed=False)
    task2 = Task(user_id="user_123", title="Task 2", completed=True)
    test_session.add_all([task1, task2])
    test_session.commit()
    
    result = list_tasks(
        session=test_session,
        user_id="user_123",
        status="all"
    )
    
    assert result["count"] == 2
    assert len(result["tasks"]) == 2


def test_list_tasks_enforces_user_id_isolation(test_session):
    """Test User A cannot see User B's tasks"""
    task_a = Task(user_id="user_A", title="Task A", completed=False)
    task_b = Task(user_id="user_B", title="Task B", completed=False)
    test_session.add_all([task_a, task_b])
    test_session.commit()
    
    result_a = list_tasks(test_session, user_id="user_A", status="all")
    assert result_a["count"] == 1
    assert result_a["tasks"][0]["title"] == "Task A"


# ========== complete_task TESTS ==========

def test_complete_task_marks_task_as_completed(test_session):
    """Test complete_task sets completed=true"""
    task = Task(user_id="user_123", title="Test task", completed=False)
    test_session.add(task)
    test_session.commit()
    test_session.refresh(task)
    
    result = complete_task(
        session=test_session,
        user_id="user_123",
        task_id=task.id
    )
    
    assert result["status"] == "completed"
    test_session.refresh(task)
    assert task.completed is True


def test_complete_task_returns_404_for_nonexistent_task(test_session):
    """Test complete_task raises error for non-existent task"""
    with pytest.raises(ValueError, match="Task not found"):
        complete_task(
            session=test_session,
            user_id="user_123",
            task_id=999999
        )


# ========== delete_task TESTS ==========

def test_delete_task_deletes_task_from_database(test_session):
    """Test delete_task removes task from database"""
    task = Task(user_id="user_123", title="To delete", completed=False)
    test_session.add(task)
    test_session.commit()
    test_session.refresh(task)
    task_id = task.id
    
    result = delete_task(
        session=test_session,
        user_id="user_123",
        task_id=task_id
    )
    
    assert result["status"] == "deleted"
    deleted_task = test_session.get(Task, task_id)
    assert deleted_task is None


# ========== update_task TESTS ==========

def test_update_task_updates_title_only(test_session):
    """Test update_task updates title only"""
    task = Task(user_id="user_123", title="Old title", description="Old desc", completed=False)
    test_session.add(task)
    test_session.commit()
    test_session.refresh(task)
    
    result = update_task(
        session=test_session,
        user_id="user_123",
        task_id=task.id,
        title="New title"
    )
    
    assert result["title"] == "New title"
    test_session.refresh(task)
    assert task.title == "New title"
    assert task.description == "Old desc"  # Unchanged


def test_update_task_rejects_empty_title(test_session):
    """Test update_task rejects empty title"""
    task = Task(user_id="user_123", title="Title", completed=False)
    test_session.add(task)
    test_session.commit()
    test_session.refresh(task)
    
    with pytest.raises(ValueError, match="title cannot be empty"):
        update_task(
            session=test_session,
            user_id="user_123",
            task_id=task.id,
            title=""
        )
