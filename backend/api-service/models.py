"""SQLModel database models for the Todo application.

This module defines:
- Task model with all fields and constraints (Basic + Intermediate + Advanced features)
- Pydantic request/response models for API endpoints
- Validation rules for task data
- Enums for priority and recurrence patterns
"""

from sqlmodel import SQLModel, Field, Column
from sqlalchemy.dialects.postgresql import JSONB, ARRAY, INTERVAL
from sqlalchemy import Text
from typing import Optional, List
from datetime import datetime, timedelta
from pydantic import validator, root_validator
from enum import Enum
from utils.timezone import get_pakistan_now

# Phase V imports
from app.models.priority import Priority
from app.models.recurrence_rule import RecurrenceRule


class PriorityEnum(str, Enum):
    """Task priority levels (Phase IV - kept for backward compatibility)."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    URGENT = "urgent"  # Phase V addition


class RecurrenceEnum(str, Enum):
    """Recurring task patterns (Phase IV - deprecated in favor of recurrence_rule JSONB)."""
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class Task(SQLModel, table=True):
    """Task entity representing a todo item in the database.

    Attributes:
        # Basic Level Fields
        id: Auto-incrementing primary key
        user_id: Foreign key to users table (managed by Better Auth)
        title: Task title (1-200 characters, required)
        description: Task description (max 1000 characters, optional)
        completed: Completion status (default: False)
        created_at: Auto-generated creation timestamp
        updated_at: Auto-updated modification timestamp

        # Intermediate Level Fields
        priority: Task priority (HIGH/MEDIUM/LOW, default: MEDIUM)
        tags: Array of user-defined tags (JSONB, max 10 tags)

        # Advanced Level Fields
        due_date: When task must be completed (timezone-aware)
        reminder_time: When to send notification (must be < due_date)
        recurrence_pattern: Recurring pattern (none/daily/weekly/monthly)
        last_completed_at: Last completion time for recurring tasks
    """
    __tablename__ = "tasks"

    # Basic Level Fields (Phase IV - existing)
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    title: str = Field(min_length=1, max_length=200, nullable=False)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: str = Field(default="pending", nullable=False)  # Phase V: pending, in_progress, completed
    created_at: datetime = Field(default_factory=get_pakistan_now)
    updated_at: datetime = Field(default_factory=get_pakistan_now)
    completed_at: Optional[datetime] = Field(default=None)  # Phase V addition

    # Phase IV backward compatibility
    completed: bool = Field(default=False, nullable=False)  # Deprecated: use status instead

    # Phase V Fields
    priority: Optional[str] = Field(default=None)  # low, medium, high, urgent
    tags: List[str] = Field(
        default_factory=list,
        sa_column=Column(ARRAY(Text), nullable=False, server_default='{}')  # Phase V: PostgreSQL TEXT[] array
    )
    due_date: Optional[datetime] = Field(default=None)  # Phase V: timezone-aware deadline
    reminder_offset: Optional[str] = Field(default=None)  # Phase V: ISO 8601 duration (e.g., "1 hour", "1 day")
    recurrence_rule: Optional[dict] = Field(
        default=None,
        sa_column=Column(JSONB)  # Phase V: JSONB recurrence pattern
    )
    parent_task_id: Optional[int] = Field(default=None, foreign_key="tasks.id")  # Phase V: link to parent task

    # Phase IV backward compatibility
    reminder_time: Optional[datetime] = Field(default=None)  # Deprecated: use reminder_offset instead
    recurrence_pattern: str = Field(default=RecurrenceEnum.NONE.value, nullable=False)  # Deprecated: use recurrence_rule instead
    last_completed_at: Optional[datetime] = Field(default=None)  # Deprecated: use completed_at instead

    def is_overdue(self) -> bool:
        """Check if task is overdue (has due_date in past and not completed)."""
        if self.completed or not self.due_date:
            return False
        return get_pakistan_now() > self.due_date


class TaskCreate(SQLModel):
    """Request model for creating a new task.

    Attributes:
        # Basic Level
        title: Task title (1-200 characters, required)
        description: Task description (max 1000 characters, optional)

        # Intermediate Level
        priority: Task priority (HIGH/MEDIUM/LOW, default: MEDIUM)
        tags: Array of tags (max 10, each max 30 chars)

        # Advanced Level
        due_date: When task must be completed
        reminder_time: When to send notification
        recurrence_pattern: Recurring pattern
    """

    # Basic Level
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)

    # Intermediate Level
    priority: str = Field(default=PriorityEnum.MEDIUM.value)
    tags: List[str] = Field(default_factory=list)

    # Advanced Level
    due_date: Optional[datetime] = None
    reminder_time: Optional[datetime] = None
    recurrence_pattern: str = Field(default=RecurrenceEnum.NONE.value)

    @validator("title")
    def title_not_empty(cls, v: str) -> str:
        """Validate that title is not empty or whitespace only."""
        if not v.strip():
            raise ValueError("Title cannot be empty or whitespace only")
        return v.strip()

    @validator("priority")
    def priority_valid(cls, v: str) -> str:
        """Validate priority is one of: HIGH, MEDIUM, LOW."""
        if v not in [e.value for e in PriorityEnum]:
            raise ValueError(f"Priority must be one of: {', '.join([e.value for e in PriorityEnum])}")
        return v

    @validator("tags")
    def tags_valid(cls, v: List[str]) -> List[str]:
        """Validate tags: max 10 tags, each max 30 chars, alphanumeric + hyphen/underscore."""
        if len(v) > 10:
            raise ValueError("Maximum 10 tags allowed")

        validated_tags = []
        for tag in v:
            # Normalize: lowercase, trim
            normalized = tag.lower().strip()

            # Validate length
            if len(normalized) > 30:
                raise ValueError(f"Tag '{tag}' exceeds 30 characters")

            # Validate format: alphanumeric + hyphen/underscore
            if not all(c.isalnum() or c in ['-', '_'] for c in normalized):
                raise ValueError(f"Tag '{tag}' contains invalid characters. Use only alphanumeric, hyphens, underscores")

            validated_tags.append(normalized)

        return validated_tags

    @validator("recurrence_pattern")
    def recurrence_valid(cls, v: str) -> str:
        """Validate recurrence pattern is one of: none, daily, weekly, monthly."""
        if v not in [e.value for e in RecurrenceEnum]:
            raise ValueError(f"Recurrence pattern must be one of: {', '.join([e.value for e in RecurrenceEnum])}")
        return v

    @root_validator(skip_on_failure=True)
    def reminder_before_due(cls, values):
        """Validate that reminder_time is before due_date if both are set."""
        reminder = values.get('reminder_time')
        due = values.get('due_date')

        if reminder and due:
            # Normalize both to timezone-naive for comparison
            # This handles cases where one is aware and one is naive
            reminder_naive = reminder.replace(tzinfo=None) if hasattr(reminder, 'tzinfo') and reminder.tzinfo else reminder
            due_naive = due.replace(tzinfo=None) if hasattr(due, 'tzinfo') and due.tzinfo else due

            if reminder_naive >= due_naive:
                raise ValueError('Reminder time must be before due date')

        return values


class TaskUpdate(SQLModel):
    """Request model for updating an existing task.

    Attributes:
        All fields are optional to support partial updates.
    """

    # Basic Level
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)

    # Intermediate Level
    priority: Optional[str] = None
    tags: Optional[List[str]] = None

    # Advanced Level
    due_date: Optional[datetime] = None
    reminder_time: Optional[datetime] = None
    recurrence_pattern: Optional[str] = None

    @validator("title")
    def title_not_empty(cls, v: Optional[str]) -> Optional[str]:
        """Validate that title is not empty or whitespace only if provided."""
        if v is not None and not v.strip():
            raise ValueError("Title cannot be empty or whitespace only")
        return v.strip() if v else None

    @validator("priority")
    def priority_valid(cls, v: Optional[str]) -> Optional[str]:
        """Validate priority if provided."""
        if v is not None and v not in [e.value for e in PriorityEnum]:
            raise ValueError(f"Priority must be one of: {', '.join([e.value for e in PriorityEnum])}")
        return v

    @validator("tags")
    def tags_valid(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate tags if provided."""
        if v is None:
            return v

        if len(v) > 10:
            raise ValueError("Maximum 10 tags allowed")

        validated_tags = []
        for tag in v:
            normalized = tag.lower().strip()
            if len(normalized) > 30:
                raise ValueError(f"Tag '{tag}' exceeds 30 characters")
            if not all(c.isalnum() or c in ['-', '_'] for c in normalized):
                raise ValueError(f"Tag '{tag}' contains invalid characters")
            validated_tags.append(normalized)

        return validated_tags

    @validator("recurrence_pattern")
    def recurrence_valid(cls, v: Optional[str]) -> Optional[str]:
        """Validate recurrence pattern if provided."""
        if v is not None and v not in [e.value for e in RecurrenceEnum]:
            raise ValueError(f"Recurrence pattern must be one of: {', '.join([e.value for e in RecurrenceEnum])}")
        return v

    @root_validator(skip_on_failure=True)
    def reminder_before_due(cls, values):
        """Validate that reminder_time is before due_date if both are set."""
        reminder = values.get('reminder_time')
        due = values.get('due_date')

        if reminder and due:
            # Normalize both to timezone-naive for comparison
            # This handles cases where one is aware and one is naive
            reminder_naive = reminder.replace(tzinfo=None) if hasattr(reminder, 'tzinfo') and reminder.tzinfo else reminder
            due_naive = due.replace(tzinfo=None) if hasattr(due, 'tzinfo') and due.tzinfo else due

            if reminder_naive >= due_naive:
                raise ValueError('Reminder time must be before due date')

        return values


class TaskResponse(SQLModel):
    """Response model for task data returned from API.

    Attributes:
        All Task fields plus computed is_overdue field
    """

    # Basic Level
    id: int
    user_id: str
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime

    # Intermediate Level
    priority: str
    tags: List[str]

    # Advanced Level
    due_date: Optional[datetime]
    reminder_time: Optional[datetime]
    recurrence_pattern: str
    last_completed_at: Optional[datetime]

    # Computed
    is_overdue: bool = False

    class Config:
        from_attributes = True
