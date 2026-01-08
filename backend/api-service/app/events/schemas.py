"""Event schemas for Kafka messages."""
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class TaskEventData(BaseModel):
    """Task data payload in TaskEvent."""

    title: str
    description: Optional[str] = None
    status: str  # pending, in_progress, completed
    priority: Optional[str] = None  # low, medium, high, urgent
    tags: List[str] = Field(default_factory=list)
    due_date: Optional[datetime] = None
    reminder_offset: Optional[str] = None
    recurrence_rule: Optional[Dict[str, Any]] = None
    parent_task_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None


class TaskEvent(BaseModel):
    """Event published when a task is created, updated, deleted, or completed."""

    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    schema_version: str = "1.0"
    event_type: str  # task.created, task.updated, task.deleted, task.completed
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    task_id: int
    user_id: int
    task_data: TaskEventData

    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "550e8400-e29b-41d4-a716-446655440000",
                "schema_version": "1.0",
                "event_type": "task.created",
                "timestamp": "2026-01-02T10:00:00Z",
                "task_id": 123,
                "user_id": 456,
                "task_data": {
                    "title": "Complete project proposal",
                    "description": "Finalize Q1 2026 project proposal",
                    "status": "pending",
                    "priority": "high",
                    "tags": ["work", "urgent"],
                    "due_date": "2026-01-10T17:00:00Z",
                    "reminder_offset": "1 day",
                    "recurrence_rule": {
                        "frequency": "weekly",
                        "interval": 1,
                        "days_of_week": [1]
                    },
                    "parent_task_id": None,
                    "created_at": "2026-01-02T10:00:00Z",
                    "updated_at": "2026-01-02T10:00:00Z",
                    "completed_at": None
                }
            }
        }


class ReminderEvent(BaseModel):
    """Event published when a task reminder is due."""

    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    schema_version: str = "1.0"
    event_type: str = "reminder.due"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    task_id: int
    user_id: int
    due_date: datetime
    task_title: str
    task_description: Optional[str] = None
    notification_channels: List[str] = Field(default=["email"])
    reminder_time: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "660e8400-e29b-41d4-a716-446655440001",
                "schema_version": "1.0",
                "event_type": "reminder.due",
                "timestamp": "2026-01-09T17:00:00Z",
                "task_id": 123,
                "user_id": 456,
                "due_date": "2026-01-10T17:00:00Z",
                "task_title": "Complete project proposal",
                "task_description": "Finalize Q1 2026 project proposal",
                "notification_channels": ["email"],
                "reminder_time": "2026-01-09T17:00:00Z"
            }
        }


class TaskSnapshot(BaseModel):
    """Minimal task data for WebSocket sync."""

    title: str
    status: str
    priority: Optional[str] = None
    due_date: Optional[datetime] = None
    updated_at: datetime


class TaskUpdateEvent(BaseModel):
    """Lightweight event for WebSocket real-time synchronization."""

    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    schema_version: str = "1.0"
    event_type: str = "task.sync"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_id: int
    operation: str  # create, update, delete
    task_id: int
    task_snapshot: TaskSnapshot

    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "770e8400-e29b-41d4-a716-446655440002",
                "schema_version": "1.0",
                "event_type": "task.sync",
                "timestamp": "2026-01-02T10:05:00Z",
                "user_id": 456,
                "operation": "update",
                "task_id": 123,
                "task_snapshot": {
                    "title": "Complete project proposal",
                    "status": "in_progress",
                    "priority": "high",
                    "due_date": "2026-01-10T17:00:00Z",
                    "updated_at": "2026-01-02T10:05:00Z"
                }
            }
        }
