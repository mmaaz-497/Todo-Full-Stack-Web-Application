"""Audit Log Model (Phase V)

This module defines the AuditLog model for storing audit trails.
"""

from sqlmodel import SQLModel, Field
from sqlalchemy.dialects.postgresql import JSONB
from typing import Optional
from datetime import datetime


class AuditLog(SQLModel, table=True):
    """Audit log entity for storing system events."""

    __tablename__ = "audit_logs"

    log_id: Optional[int] = Field(default=None, primary_key=True)
    event_id: str  # UUID of the event
    user_id: Optional[str] = Field(default=None)  # User who triggered the event
    action_type: str  # Type of action (created, updated, deleted, etc.)
    resource_type: str  # Type of resource (task, user, etc.)
    resource_id: Optional[int] = Field(default=None)  # ID of the resource
    payload: dict = Field(sa_column=Field(type_=JSONB))  # Additional data about the event
    timestamp: datetime  # When the event occurred
    source_service: str  # Which service generated the event

    class Config:
        arbitrary_types_allowed = True