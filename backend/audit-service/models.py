from sqlmodel import SQLModel, Field, JSON, Column
from datetime import datetime
from typing import Optional, Dict, Any

class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    event_id: str = Field(index=True, unique=True)
    event_type: str = Field(index=True)
    task_id: int = Field(index=True)
    user_id: str = Field(index=True)
    event_payload: Dict[str, Any] = Field(sa_column=Column(JSON))
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
