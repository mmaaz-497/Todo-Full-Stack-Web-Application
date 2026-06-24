"""AgentState database model.

This model tracks the health and execution state of the reminder agent.
It's used for monitoring and alerting - if the agent hasn't updated
this table recently, ops teams know something is wrong.
"""

from sqlmodel import SQLModel, Field, Column
from sqlalchemy.dialects.postgresql import JSONB
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class AgentStatus(str, Enum):
    """Agent execution status enumeration.

    Attributes:
        INITIALIZED: Agent started but not yet running jobs
        RUNNING: Agent actively processing reminders
        PAUSED: Agent intentionally paused (e.g., for maintenance)
        ERROR: Agent encountered critical error
    """
    INITIALIZED = "initialized"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"


class AgentState(SQLModel, table=True):
    """Agent health and execution state tracking.

    This table should have exactly ONE row (updated on each agent cycle).
    The last_check_at timestamp is our health check - if it's more than
    10 minutes old, the agent may have crashed.

    Attributes:
        id: Unique identifier (UUID auto-generated)
        last_check_at: Last time agent ran (health check timestamp)
        tasks_processed: Cumulative count of tasks processed
        reminders_sent: Cumulative count of reminders successfully sent
        errors_count: Cumulative count of errors encountered
        status: Current agent status (running/paused/error/initialized)
        agent_metadata: JSON field for additional context (version, etc.)
        created_at: Record creation timestamp
        updated_at: Last update timestamp
    """
    __tablename__ = "agent_state"

    # Primary key
    id: Optional[str] = Field(default=None, primary_key=True)

    # Health check timestamp (critical for monitoring)
    last_check_at: datetime = Field(nullable=False)

    # Cumulative metrics
    tasks_processed: int = Field(default=0)
    reminders_sent: int = Field(default=0)
    errors_count: int = Field(default=0)

    # Current status
    status: str = Field(default=AgentStatus.RUNNING.value)

    # Flexible metadata field for additional context
    # Example: {"version": "1.0.0", "deployment": "us-east-1"}
    agent_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSONB, nullable=False, server_default='{}')
    )

    # Audit timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
