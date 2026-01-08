"""
Advanced search and filter endpoints for tasks.

Implements Phase V Advanced Management Features (T098-T104):
- T098: Keyword search using PostgreSQL LIKE query
- T099: Priority filter using WHERE priority = clause
- T100: Tags filter using PostgreSQL array containment @> operator
- T101: Status filter
- T102: Due date range filter
- T103: Sort by due_date, priority, created_at
- T104: Pagination support (offset, limit)
"""

from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session, select, or_, and_, func, case
from typing import List, Optional
from datetime import datetime

from db import get_session
from models import Task, TaskResponse
from auth import get_current_user_id, verify_user_ownership
from app.validators import validate_search_query, validate_pagination

router = APIRouter()


@router.get("/api/{user_id}/tasks/search", response_model=List[TaskResponse], tags=["Search"])
async def search_tasks(
    user_id: str,
    # T098: Keyword search parameter
    q: Optional[str] = Query(None, description="Search keyword in title and description"),
    # T099: Priority filter
    priority: Optional[str] = Query(None, description="Filter by priority: LOW, MEDIUM, HIGH, URGENT"),
    # T100: Tags filter
    tags: Optional[List[str]] = Query(None, description="Filter by tags (contains all specified tags)"),
    # T101: Status filter
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status: pending, completed, overdue"),
    # T102: Due date range filter
    due_date_from: Optional[datetime] = Query(None, description="Filter tasks due after this date"),
    due_date_to: Optional[datetime] = Query(None, description="Filter tasks due before this date"),
    # T103: Sort parameter
    sort_by: str = Query("created_at", description="Sort by: due_date, priority, created_at"),
    sort_order: str = Query("desc", description="Sort order: asc or desc"),
    # T104: Pagination
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records to return"),
    # Auth
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session),
):
    """Advanced task search with filters, sorting, and pagination.

    Features:
    - T098: Full-text keyword search in title and description
    - T099: Filter by priority level
    - T100: Filter by multiple tags (AND logic)
    - T101: Filter by status (pending/completed/overdue)
    - T102: Filter by due date range
    - T103: Sort by due_date, priority, or created_at
    - T104: Paginated results

    Args:
        user_id: User ID from path
        q: Search keyword
        priority: Priority filter (LOW/MEDIUM/HIGH/URGENT)
        tags: Tag filters (contains all)
        status_filter: Status filter (pending/completed/overdue)
        due_date_from: Start of due date range
        due_date_to: End of due date range
        sort_by: Field to sort by
        sort_order: Sort direction (asc/desc)
        offset: Pagination offset
        limit: Pagination limit
        current_user_id: Authenticated user ID
        session: Database session

    Returns:
        List[TaskResponse]: Filtered and sorted tasks
    """
    verify_user_ownership(user_id, current_user_id)

    # Validate inputs
    if q:
        q = validate_search_query(q)
    validate_pagination(offset, limit)

    # Start building query
    query = select(Task).where(Task.user_id == user_id)

    # T098: Keyword search using LIKE (case-insensitive)
    if q:
        search_pattern = f"%{q}%"
        query = query.where(
            or_(
                Task.title.ilike(search_pattern),
                Task.description.ilike(search_pattern)
            )
        )

    # T099: Priority filter
    if priority:
        priority_upper = priority.upper()
        if priority_upper in ["LOW", "MEDIUM", "HIGH", "URGENT"]:
            query = query.where(Task.priority == priority_upper)

    # T100: Tags filter using array containment
    if tags:
        # PostgreSQL array containment: tags column must contain ALL specified tags
        # Using @> operator via func.jsonb_path_query_array or direct JSONB query
        for tag in tags:
            # Each tag must exist in the tags array
            query = query.where(
                func.jsonb_exists(Task.tags, tag)
            )

    # T101: Status filter
    if status_filter:
        status_lower = status_filter.lower()
        if status_lower == "completed":
            query = query.where(Task.completed == True)
        elif status_lower == "pending":
            query = query.where(Task.completed == False)
        elif status_lower == "overdue":
            # Overdue: not completed AND due_date is in the past
            query = query.where(
                and_(
                    Task.completed == False,
                    Task.due_date.isnot(None),
                    Task.due_date < datetime.utcnow()
                )
            )

    # T102: Due date range filter
    if due_date_from:
        query = query.where(Task.due_date >= due_date_from)
    if due_date_to:
        query = query.where(Task.due_date <= due_date_to)

    # T103: Sorting
    sort_column = Task.created_at  # Default
    if sort_by == "due_date":
        # Sort NULL due_dates last
        sort_column = case(
            (Task.due_date.is_(None), datetime.max),
            else_=Task.due_date
        )
    elif sort_by == "priority":
        # Sort by priority (URGENT > HIGH > MEDIUM > LOW)
        priority_order = case(
            (Task.priority == "URGENT", 4),
            (Task.priority == "HIGH", 3),
            (Task.priority == "MEDIUM", 2),
            (Task.priority == "LOW", 1),
            else_=0
        )
        sort_column = priority_order
    elif sort_by == "created_at":
        sort_column = Task.created_at

    if sort_order.lower() == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    # T104: Pagination
    query = query.offset(offset).limit(limit)

    # Execute query
    tasks = session.exec(query).all()

    # Add computed fields
    response_tasks = []
    for task in tasks:
        task_dict = task.dict()
        task_dict['is_overdue'] = task.is_overdue()
        response_tasks.append(TaskResponse(**task_dict))

    return response_tasks


@router.get("/api/{user_id}/tasks/filter", response_model=List[TaskResponse], tags=["Search"])
async def filter_tasks(
    user_id: str,
    # Simpler filter endpoint with common filters
    priority: Optional[str] = Query(None, description="Filter by priority"),
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    # Pagination
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    # Auth
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session),
):
    """Simple filter endpoint for backward compatibility.

    Args:
        user_id: User ID from path
        priority: Priority filter
        tags: Comma-separated tags
        status_filter: Status filter
        offset: Pagination offset
        limit: Pagination limit
        current_user_id: Authenticated user ID
        session: Database session

    Returns:
        List[TaskResponse]: Filtered tasks
    """
    # Convert tags string to list
    tags_list = None
    if tags:
        tags_list = [tag.strip() for tag in tags.split(",") if tag.strip()]

    # Call main search endpoint
    return await search_tasks(
        user_id=user_id,
        q=None,
        priority=priority,
        tags=tags_list,
        status_filter=status_filter,
        due_date_from=None,
        due_date_to=None,
        sort_by="created_at",
        sort_order="desc",
        offset=offset,
        limit=limit,
        current_user_id=current_user_id,
        session=session
    )
