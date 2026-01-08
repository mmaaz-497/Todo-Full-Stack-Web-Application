"""Task CRUD API endpoints for FastAPI backend.

This module implements all REST API endpoints with:
- Basic Level: CRUD operations
- Intermediate Level: Filters, search, sort by priority/tags
- Advanced Level: Recurring tasks, due dates, reminders
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select, func, or_, case
from sqlalchemy import and_
from typing import List, Optional
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from db import get_session
from models import Task, TaskCreate, TaskUpdate, TaskResponse, RecurrenceEnum
from auth import get_current_user_id, verify_user_ownership
from utils.timezone import to_utc, get_pakistan_now
from app.events.publisher import DaprPublisher
from app.jobs.reminder_scheduler import reminder_scheduler
from app.validators import validate_recurrence_rule, validate_due_date, validate_reminder_offset

router = APIRouter()

# Initialize event publisher (uses DAPR_HTTP_URL env var or defaults to localhost:3500)
event_publisher = DaprPublisher()


# ============================================================================
# HELPER: Convert Task model to event data format
# ============================================================================
def task_to_event_data(task: Task) -> dict:
    """Convert Task model to TaskEventData schema for Kafka events.

    Maps Phase IV fields to Phase V event schema:
    - completed (bool) → status (pending/in_progress/completed)
    - reminder_time → reminder_offset (ISO 8601 duration)
    - recurrence_pattern → recurrence_rule (JSONB structure)
    """
    # Map completed boolean to status string
    status = "completed" if task.completed else "pending"

    # Convert reminder_time to reminder_offset (simplified - just use as-is for now)
    reminder_offset = None
    if task.reminder_time and task.due_date:
        # Calculate offset as duration string
        offset_seconds = int((task.due_date - task.reminder_time).total_seconds())
        reminder_offset = f"{offset_seconds} seconds"

    # Convert recurrence_pattern to recurrence_rule
    recurrence_rule = None
    if task.recurrence_pattern and task.recurrence_pattern != "NONE":
        recurrence_rule = {
            "frequency": task.recurrence_pattern.lower(),
            "interval": 1
        }

    return {
        "title": task.title,
        "description": task.description,
        "status": status,
        "priority": task.priority,
        "tags": task.tags or [],
        "due_date": task.due_date,
        "reminder_offset": reminder_offset,
        "recurrence_rule": recurrence_rule,
        "parent_task_id": None,  # Not yet implemented in Phase IV
        "created_at": task.created_at,
        "updated_at": task.updated_at,
        "completed_at": task.last_completed_at if task.completed else None
    }


# ============================================================================
# INTERMEDIATE FEATURE: List tasks with filters and sorting
# ============================================================================
@router.get("/api/{user_id}/tasks", response_model=List[TaskResponse], tags=["Tasks"])
async def list_tasks(
    user_id: str,
    # Intermediate: Filter parameters
    priority: Optional[str] = Query(None, description="Filter by priority: HIGH, MEDIUM, LOW, or all"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags (AND logic)"),
    status: str = Query("all", description="Filter by status: all, pending, completed"),
    # Intermediate: Sort parameter
    sort: str = Query("created_date", description="Sort by: created_date, due_date, priority, title"),
    # Auth
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session),
):
    """List all tasks for the authenticated user with filters and sorting.

    Intermediate Features:
    - Filter by priority (HIGH/MEDIUM/LOW)
    - Filter by tags (multiple tags = AND logic)
    - Filter by status (all/pending/completed)
    - Sort by created_date, due_date, priority, title

    Args:
        user_id: User ID from path parameter
        priority: Filter by priority level
        tags: Filter by tags (multiple allowed)
        status: Filter by completion status
        sort: Sort order
        current_user_id: User ID extracted from JWT token
        session: Database session

    Returns:
        List[TaskResponse]: Filtered and sorted tasks
    """
    verify_user_ownership(user_id, current_user_id)

    # Base query: filter by user_id
    query = select(Task).where(Task.user_id == user_id)

    # INTERMEDIATE: Apply priority filter
    if priority and priority != "all":
        query = query.where(Task.priority == priority)

    # INTERMEDIATE: Apply tags filter (AND logic - task must have ALL specified tags)
    if tags:
        for tag in tags:
            query = query.where(Task.tags.contains([tag]))

    # INTERMEDIATE: Apply status filter
    if status == "completed":
        query = query.where(Task.completed == True)
    elif status == "pending":
        query = query.where(Task.completed == False)

    # INTERMEDIATE: Apply sorting
    if sort == "due_date":
        # Sort by due date: nearest first, nulls last
        query = query.order_by(Task.due_date.asc().nulls_last())
    elif sort == "priority":
        # Sort by priority: HIGH → MEDIUM → LOW
        query = query.order_by(
            case(
                (Task.priority == "HIGH", 1),
                (Task.priority == "MEDIUM", 2),
                (Task.priority == "LOW", 3),
                else_=4
            )
        )
    elif sort == "title":
        # Sort alphabetically by title
        query = query.order_by(Task.title.asc())
    else:  # default: created_date
        # Sort by creation date: newest first
        query = query.order_by(Task.created_at.desc())

    # Execute query
    tasks = session.exec(query).all()

    # Add computed is_overdue field
    response_tasks = []
    for task in tasks:
        task_dict = task.dict()
        task_dict['is_overdue'] = task.is_overdue()
        response_tasks.append(TaskResponse(**task_dict))

    return response_tasks


# ============================================================================
# INTERMEDIATE FEATURE: Search tasks by keyword
# ============================================================================
@router.get("/api/{user_id}/tasks/search", response_model=List[TaskResponse], tags=["Tasks"])
async def search_tasks(
    user_id: str,
    q: str = Query(..., min_length=1, description="Search query (matches title or description)"),
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session),
):
    """Search tasks by keyword in title or description.

    Intermediate Feature: Case-insensitive partial matching.

    Args:
        user_id: User ID from path parameter
        q: Search query string
        current_user_id: User ID extracted from JWT token
        session: Database session

    Returns:
        List[TaskResponse]: Matching tasks
    """
    verify_user_ownership(user_id, current_user_id)

    # Search in title or description (case-insensitive)
    query = select(Task).where(
        Task.user_id == user_id,
        or_(
            Task.title.ilike(f"%{q}%"),
            Task.description.ilike(f"%{q}%")
        )
    )

    tasks = session.exec(query).all()

    # Add computed is_overdue field
    response_tasks = []
    for task in tasks:
        task_dict = task.dict()
        task_dict['is_overdue'] = task.is_overdue()
        response_tasks.append(TaskResponse(**task_dict))

    return response_tasks


# ============================================================================
# INTERMEDIATE FEATURE: Get unique tags for autocomplete
# ============================================================================
@router.get("/api/{user_id}/tags", response_model=List[str], tags=["Tags"])
async def get_user_tags(
    user_id: str,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session),
):
    """Get all unique tags used by the authenticated user.

    Intermediate Feature: Tag autocomplete support.

    Args:
        user_id: User ID from path parameter
        current_user_id: User ID extracted from JWT token
        session: Database session

    Returns:
        List[str]: Sorted list of unique tags
    """
    verify_user_ownership(user_id, current_user_id)

    # Query all unique tags from JSONB array
    # Uses PostgreSQL jsonb_array_elements_text to expand array
    query = select(func.jsonb_array_elements_text(Task.tags)).where(
        Task.user_id == user_id
    ).distinct()

    tags = session.exec(query).all()

    return sorted(tags)


# ============================================================================
# BASIC + INTERMEDIATE + ADVANCED: Create task
# ============================================================================
@router.post(
    "/api/{user_id}/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Tasks"],
)
async def create_task(
    user_id: str,
    task_data: TaskCreate,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session),
):
    """Create a new task with Basic, Intermediate, and Advanced features.

    Basic: title, description
    Intermediate: priority, tags
    Advanced: due_date, reminder_time, recurrence_pattern

    Args:
        user_id: User ID from path parameter
        task_data: Task creation data
        current_user_id: User ID extracted from JWT token
        session: Database session

    Returns:
        TaskResponse: Created task
    """
    verify_user_ownership(user_id, current_user_id)

    # T089-T092: Validate recurrence rule if provided
    if hasattr(task_data, 'recurrence_rule') and task_data.recurrence_rule:
        validate_recurrence_rule(task_data.recurrence_rule)

    # T093: Validate due_date is in future
    if task_data.due_date:
        validate_due_date(task_data.due_date)

    # T094: Validate reminder_offset
    if task_data.due_date and task_data.reminder_time:
        validate_reminder_offset(task_data.due_date, task_data.reminder_time)

    # Create new task with all fields
    task = Task(
        user_id=user_id,
        title=task_data.title,
        description=task_data.description,
        completed=False,
        # Intermediate features
        priority=task_data.priority,
        tags=task_data.tags,
        # Advanced features (strip timezone, keep Pakistan local time)
        due_date=to_utc(task_data.due_date),
        reminder_time=to_utc(task_data.reminder_time),
        recurrence_pattern=task_data.recurrence_pattern,
        # Timestamps (Pakistan local time)
        created_at=get_pakistan_now(),
        updated_at=get_pakistan_now(),
    )

    session.add(task)
    session.commit()
    session.refresh(task)

    # Publish task.created event to Kafka via Dapr
    try:
        await event_publisher.publish_task_event(
            event_type="task.created",
            task_id=task.id,
            user_id=int(user_id),
            task_data=task_to_event_data(task)
        )
    except Exception as e:
        # Log error but don't fail request - event publishing is best-effort
        print(f"Failed to publish task.created event for task {task.id}: {e}")

    # Schedule reminder via Dapr Jobs API if due_date and reminder_time are set
    if task.due_date and task.reminder_time:
        try:
            reminder_offset = task.due_date - task.reminder_time
            await reminder_scheduler.schedule_reminder(
                task_id=task.id,
                user_id=int(user_id),
                due_date=task.due_date,
                reminder_offset=reminder_offset,
                task_title=task.title,
                task_description=task.description
            )
        except Exception as e:
            # Log error but don't fail request - reminder scheduling is best-effort
            print(f"Failed to schedule reminder for task {task.id}: {e}")

    # Add computed field
    task_dict = task.dict()
    task_dict['is_overdue'] = task.is_overdue()

    return TaskResponse(**task_dict)


# ============================================================================
# BASIC: Get single task
# ============================================================================
@router.get("/api/{user_id}/tasks/{id}", response_model=TaskResponse, tags=["Tasks"])
async def get_task(
    user_id: str,
    id: int,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session),
):
    """Get a single task by ID."""
    verify_user_ownership(user_id, current_user_id)

    statement = select(Task).where(Task.id == id, Task.user_id == user_id)
    task = session.exec(statement).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Add computed field
    task_dict = task.dict()
    task_dict['is_overdue'] = task.is_overdue()

    return TaskResponse(**task_dict)


# ============================================================================
# BASIC + INTERMEDIATE + ADVANCED: Update task
# ============================================================================
@router.put("/api/{user_id}/tasks/{id}", response_model=TaskResponse, tags=["Tasks"])
async def update_task(
    user_id: str,
    id: int,
    task_data: TaskUpdate,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session),
):
    """Update an existing task (partial updates supported)."""
    verify_user_ownership(user_id, current_user_id)

    statement = select(Task).where(Task.id == id, Task.user_id == user_id)
    task = session.exec(statement).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Update fields if provided (partial update)
    # Basic fields
    if task_data.title is not None:
        task.title = task_data.title
    if task_data.description is not None:
        task.description = task_data.description

    # Intermediate fields
    if task_data.priority is not None:
        task.priority = task_data.priority
    if task_data.tags is not None:
        task.tags = task_data.tags

    # Advanced fields (strip timezone, keep Pakistan local time)
    if task_data.due_date is not None:
        task.due_date = to_utc(task_data.due_date)
    if task_data.reminder_time is not None:
        task.reminder_time = to_utc(task_data.reminder_time)
    if task_data.recurrence_pattern is not None:
        task.recurrence_pattern = task_data.recurrence_pattern

    # Update timestamp (Pakistan local time)
    task.updated_at = get_pakistan_now()

    session.add(task)
    session.commit()
    session.refresh(task)

    # Publish task.updated event to Kafka via Dapr
    try:
        await event_publisher.publish_task_event(
            event_type="task.updated",
            task_id=task.id,
            user_id=int(user_id),
            task_data=task_to_event_data(task)
        )
    except Exception as e:
        # Log error but don't fail request - event publishing is best-effort
        print(f"Failed to publish task.updated event for task {task.id}: {e}")

    # Reschedule reminder if due_date or reminder_time was updated
    if (task_data.due_date is not None or task_data.reminder_time is not None) and task.due_date and task.reminder_time:
        try:
            reminder_offset = task.due_date - task.reminder_time
            await reminder_scheduler.reschedule_reminder(
                task_id=task.id,
                user_id=int(user_id),
                new_due_date=task.due_date,
                reminder_offset=reminder_offset,
                task_title=task.title,
                task_description=task.description
            )
        except Exception as e:
            # Log error but don't fail request - reminder rescheduling is best-effort
            print(f"Failed to reschedule reminder for task {task.id}: {e}")

    # Add computed field
    task_dict = task.dict()
    task_dict['is_overdue'] = task.is_overdue()

    return TaskResponse(**task_dict)


# ============================================================================
# BASIC: Delete task
# ============================================================================
@router.delete(
    "/api/{user_id}/tasks/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Tasks"],
)
async def delete_task(
    user_id: str,
    id: int,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session),
):
    """Delete a task."""
    verify_user_ownership(user_id, current_user_id)

    statement = select(Task).where(Task.id == id, Task.user_id == user_id)
    task = session.exec(statement).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Capture task data before deletion for event publishing
    task_data_for_event = task_to_event_data(task)
    task_id_for_event = task.id
    has_reminder = task.due_date is not None and task.reminder_time is not None

    session.delete(task)
    session.commit()

    # Publish task.deleted event to Kafka via Dapr
    try:
        await event_publisher.publish_task_event(
            event_type="task.deleted",
            task_id=task_id_for_event,
            user_id=int(user_id),
            task_data=task_data_for_event
        )
    except Exception as e:
        # Log error but don't fail request - event publishing is best-effort
        print(f"Failed to publish task.deleted event for task {task_id_for_event}: {e}")

    # Cancel reminder if task had one scheduled
    if has_reminder:
        try:
            await reminder_scheduler.cancel_reminder(
                task_id=task_id_for_event,
                user_id=int(user_id)
            )
        except Exception as e:
            # Log error but don't fail request - reminder cancellation is best-effort
            print(f"Failed to cancel reminder for task {task_id_for_event}: {e}")


# ============================================================================
# BASIC + ADVANCED: Toggle completion (with recurring task logic)
# ============================================================================
@router.patch(
    "/api/{user_id}/tasks/{id}/complete",
    response_model=dict,
    tags=["Tasks"],
)
async def toggle_complete(
    user_id: str,
    id: int,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session),
):
    """Toggle task completion status.

    Advanced Feature: If task is recurring and being marked complete,
    automatically create next occurrence.

    Returns:
        dict: {
            "task": Updated task,
            "next_occurrence": Newly created task (if recurring) or null
        }
    """
    verify_user_ownership(user_id, current_user_id)

    statement = select(Task).where(Task.id == id, Task.user_id == user_id)
    task = session.exec(statement).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Toggle completion status
    task.completed = not task.completed

    # Update timestamp (Pakistan local time)
    task.updated_at = get_pakistan_now()

    next_occurrence = None

    # ADVANCED FEATURE: Handle recurring tasks
    if task.completed and task.recurrence_pattern != RecurrenceEnum.NONE.value:
        next_occurrence = create_recurring_instance(task, session)

    session.add(task)
    session.commit()
    session.refresh(task)

    # Publish task.completed event to Kafka via Dapr
    if task.completed:
        try:
            await event_publisher.publish_task_event(
                event_type="task.completed",
                task_id=task.id,
                user_id=int(user_id),
                task_data=task_to_event_data(task)
            )
        except Exception as e:
            # Log error but don't fail request - event publishing is best-effort
            print(f"Failed to publish task.completed event for task {task.id}: {e}")

        # Cancel reminder when task is completed
        if task.due_date and task.reminder_time:
            try:
                await reminder_scheduler.cancel_reminder(
                    task_id=task.id,
                    user_id=int(user_id)
                )
            except Exception as e:
                # Log error but don't fail request - reminder cancellation is best-effort
                print(f"Failed to cancel reminder for completed task {task.id}: {e}")

    # If next occurrence was created, publish task.created event for it
    if next_occurrence:
        try:
            await event_publisher.publish_task_event(
                event_type="task.created",
                task_id=next_occurrence.id,
                user_id=int(user_id),
                task_data=task_to_event_data(next_occurrence)
            )
        except Exception as e:
            # Log error but don't fail request - event publishing is best-effort
            print(f"Failed to publish task.created event for recurring task {next_occurrence.id}: {e}")

    # Prepare response
    task_dict = task.dict()
    task_dict['is_overdue'] = task.is_overdue()
    task_response = TaskResponse(**task_dict)

    next_occurrence_response = None
    if next_occurrence:
        next_dict = next_occurrence.dict()
        next_dict['is_overdue'] = next_occurrence.is_overdue()
        next_occurrence_response = TaskResponse(**next_dict)

    return {
        "task": task_response,
        "next_occurrence": next_occurrence_response
    }


# ============================================================================
# ADVANCED FEATURE: Create next recurring instance
# ============================================================================
def create_recurring_instance(completed_task: Task, session: Session) -> Optional[Task]:
    """Create next instance of a recurring task.

    Advanced Feature: Calculates next due date based on recurrence pattern
    and creates a new task with copied attributes.

    Args:
        completed_task: The task that was just completed
        session: Database session

    Returns:
        Task: Newly created task instance or None if not recurring
    """
    if not completed_task.due_date:
        # Can't create recurring instance without due date
        return None

    # Calculate next due date based on recurrence pattern
    if completed_task.recurrence_pattern == RecurrenceEnum.DAILY.value:
        next_due = completed_task.due_date + timedelta(days=1)
    elif completed_task.recurrence_pattern == RecurrenceEnum.WEEKLY.value:
        next_due = completed_task.due_date + timedelta(weeks=1)
    elif completed_task.recurrence_pattern == RecurrenceEnum.MONTHLY.value:
        next_due = completed_task.due_date + relativedelta(months=1)
    else:
        return None

    # Calculate next reminder time (maintain same offset from due date)
    next_reminder = None
    if completed_task.reminder_time and completed_task.due_date:
        reminder_offset = completed_task.due_date - completed_task.reminder_time
        next_reminder = next_due - reminder_offset

    # Create new task instance with copied attributes
    new_task = Task(
        user_id=completed_task.user_id,
        title=completed_task.title,
        description=completed_task.description,
        priority=completed_task.priority,
        tags=completed_task.tags.copy() if completed_task.tags else [],
        due_date=next_due,
        reminder_time=next_reminder,
        recurrence_pattern=completed_task.recurrence_pattern,
        completed=False,  # New instance starts incomplete
        created_at=get_pakistan_now(),
        updated_at=get_pakistan_now(),
    )

    # Update last completed timestamp on original task (Pakistan local time)
    completed_task.last_completed_at = get_pakistan_now()

    # Save new task
    session.add(new_task)
    session.commit()
    session.refresh(new_task)

    return new_task
