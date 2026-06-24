"""Task model for reminder agent.

This is a copy of the Task model from the backend to avoid circular dependencies.
The reminder agent reads tasks from the same database as the backend.
"""

from sqlmodel import SQLModel, Field, Column
from sqlalchemy.dialects.postgresql import JSONB
from typing import Optional, List
from datetime import datetime
from enum import Enum


class PriorityEnum(str, Enum):
    """Task priority levels."""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class RecurrenceEnum(str, Enum):
    """Recurring task patterns."""
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class Task(SQLModel, table=True):
    """Task entity representing a todo item in the database.

    This model is shared between the backend and the reminder agent.
    Both services read/write to the same tasks table in PostgreSQL.
    """
    __tablename__ = "tasks"

    # Basic Level Fields
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    title: str = Field(min_length=1, max_length=200, nullable=False)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Intermediate Level Fields
    priority: str = Field(default=PriorityEnum.MEDIUM.value, nullable=False)
    tags: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSONB, nullable=False, server_default='[]')
    )

    # Advanced Level Fields
    due_date: Optional[datetime] = Field(default=None)
    reminder_time: Optional[datetime] = Field(default=None)
    recurrence_pattern: str = Field(default=RecurrenceEnum.NONE.value, nullable=False)
    last_completed_at: Optional[datetime] = Field(default=None)

    def is_overdue(self) -> bool:
        """Check if task is overdue (has due_date in past and not completed)."""
        if self.completed or not self.due_date:
            return False
        # Import here to avoid circular dependency
        import pytz
        pakistan_tz = pytz.timezone('Asia/Karachi')
        pakistan_now = datetime.now(pakistan_tz).replace(tzinfo=None)
        return pakistan_now > self.due_date
