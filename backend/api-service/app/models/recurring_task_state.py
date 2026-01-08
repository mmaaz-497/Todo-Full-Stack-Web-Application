"""Recurring task state model for tracking occurrence generation."""
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class RecurringTaskState(SQLModel, table=True):
    """Tracks last generated occurrence for recurring tasks."""

    __tablename__ = "recurring_task_state"

    task_id: int = Field(primary_key=True, foreign_key="tasks.id")
    last_generated_at: datetime = Field(description="When last occurrence was generated")
    next_occurrence_due: Optional[datetime] = Field(
        default=None,
        description="Calculated next occurrence due date (cached)"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
