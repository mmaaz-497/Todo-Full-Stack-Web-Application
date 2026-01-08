from sqlmodel import Session, select
from models import Task
from datetime import datetime
from typing import Optional, Literal


def add_task(
    session: Session,
    user_id: str,
    title: str,
    description: Optional[str] = None
) -> dict:
    """Create new task for user
    
    Constitution Principle: MCP-First Tool Integration, Database Persistence Guarantee
    """
    # Validate inputs
    if not title or title.strip() == "":
        raise ValueError("Task title cannot be empty")
    
    if len(title) > 500:
        raise ValueError("Task title max length is 500 characters")
    
    if description and len(description) > 5000:
        raise ValueError("Task description max length is 5000 characters")
    
    # Create task
    task = Task(
        user_id=user_id,
        title=title.strip(),
        description=description.strip() if description else None,
        completed=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    session.add(task)
    session.commit()
    session.refresh(task)
    
    return {
        "task_id": task.id,
        "status": "pending",
        "title": task.title
    }


def list_tasks(
    session: Session,
    user_id: str,
    status: Literal["all", "pending", "completed"] = "all"
) -> dict:
    """Retrieve tasks for user with status filtering
    
    Constitution Principle: MCP-First Tool Integration, Security and User Isolation
    """
    # Build query with user_id filter
    query = select(Task).where(Task.user_id == user_id)
    
    # Apply status filter
    if status == "pending":
        query = query.where(Task.completed == False)
    elif status == "completed":
        query = query.where(Task.completed == True)
    
    # Order by newest first
    query = query.order_by(Task.created_at.desc())
    
    # Execute query
    tasks = session.exec(query).all()
    
    # Format response
    task_list = []
    for task in tasks:
        task_list.append({
            "task_id": task.id,
            "title": task.title,
            "description": task.description,
            "status": "completed" if task.completed else "pending",
            "created_at": task.created_at.isoformat()
        })
    
    return {
        "tasks": task_list,
        "count": len(task_list)
    }


def complete_task(
    session: Session,
    user_id: str,
    task_id: int
) -> dict:
    """Mark task as completed
    
    Constitution Principle: MCP-First Tool Integration, Security and User Isolation
    """
    # Query task with user_id ownership check
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id
    )
    task = session.exec(statement).first()
    
    if not task:
        raise ValueError("Task not found")
    
    # Update task (idempotent - no error if already completed)
    task.completed = True
    task.updated_at = datetime.utcnow()
    
    session.add(task)
    session.commit()
    session.refresh(task)
    
    return {
        "task_id": task.id,
        "status": "completed",
        "title": task.title
    }


def delete_task(
    session: Session,
    user_id: str,
    task_id: int
) -> dict:
    """Permanently delete task
    
    Constitution Principle: MCP-First Tool Integration, Security and User Isolation
    """
    # Query task with user_id ownership check
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id
    )
    task = session.exec(statement).first()
    
    if not task:
        raise ValueError("Task not found")
    
    # Store title before deletion (for response)
    title = task.title
    task_id_copy = task.id
    
    # Delete task
    session.delete(task)
    session.commit()
    
    return {
        "task_id": task_id_copy,
        "status": "deleted",
        "title": title
    }


def update_task(
    session: Session,
    user_id: str,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None
) -> dict:
    """Update task title or description
    
    Constitution Principle: MCP-First Tool Integration, Security and User Isolation
    """
    # Validate at least one field provided
    if title is None and description is None:
        raise ValueError("At least one field (title or description) must be provided")
    
    # Validate title not empty if provided
    if title is not None and (not title or title.strip() == ""):
        raise ValueError("Task title cannot be empty")
    
    if title and len(title) > 500:
        raise ValueError("Task title max length is 500 characters")
    
    if description and len(description) > 5000:
        raise ValueError("Task description max length is 5000 characters")
    
    # Query task with user_id ownership check
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id
    )
    task = session.exec(statement).first()
    
    if not task:
        raise ValueError("Task not found")
    
    # Update specified fields
    if title is not None:
        task.title = title.strip()
    if description is not None:
        task.description = description.strip()
    
    task.updated_at = datetime.utcnow()
    
    session.add(task)
    session.commit()
    session.refresh(task)
    
    return {
        "task_id": task.id,
        "status": "completed" if task.completed else "pending",
        "title": task.title,
        "description": task.description
    }
