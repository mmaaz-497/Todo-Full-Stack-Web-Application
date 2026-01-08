"""
SQLModel models for Audit Service.

Defines:
- AuditLogEntry: Audit log record
"""

from sqlmodel import SQLModel, Field, Column, JSON
from datetime import datetime
from typing import Optional, Dict, Any


class AuditLogEntry(SQLModel, table=True):
    """
    Audit log entry for tracking all system events.

    Stores complete event data for compliance, debugging, and analytics.
    """
    __tablename__ = "audit_logs"

    log_id: Optional[int] = Field(default=None, primary_key=True)
    event_id: str = Field(index=True, unique=True, max_length=255)
    user_id: Optional[int] = Field(default=None, index=True)
    action_type: str = Field(index=True, max_length=50)
    resource_type: str = Field(index=True, max_length=50)
    resource_id: Optional[int] = Field(default=None)
    event_data: Dict[str, Any] = Field(sa_column=Column(JSON))
    source_service: Optional[str] = Field(default=None, max_length=100)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AuditLogQuery(SQLModel):
    """Query parameters for audit log retrieval."""
    user_id: Optional[int] = None
    action_type: Optional[str] = None
    resource_type: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = Field(default=100, le=1000)
    offset: int = Field(default=0, ge=0)


class AuditLogResponse(SQLModel):
    """Response model for audit log entries."""
    log_id: int
    event_id: str
    user_id: Optional[int]
    action_type: str
    resource_type: str
    resource_id: Optional[int]
    event_data: Dict[str, Any]
    source_service: Optional[str]
    timestamp: datetime
    created_at: datetime
