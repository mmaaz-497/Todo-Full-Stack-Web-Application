"""
Event consumer for audit logging.

Handles:
- Multi-topic event consumption (task-events, reminders, task-updates)
- Event parsing and normalization
- Audit log insertion
- Error handling
"""

from datetime import datetime
from typing import Dict
import logging
from sqlmodel import Session

from .models import AuditLogEntry
from .database import engine

logger = logging.getLogger(__name__)


def parse_action_type(event_type: str) -> str:
    """
    Parse action type from event type.

    Args:
        event_type: Event type (e.g., "task.created")

    Returns:
        Action type for audit log
    """
    # Map event types to action types
    return event_type  # Keep as-is for now


def parse_resource_type(event_type: str) -> str:
    """
    Parse resource type from event type.

    Args:
        event_type: Event type (e.g., "task.created", "reminder.due")

    Returns:
        Resource type (e.g., "task", "reminder")
    """
    if event_type.startswith("task."):
        return "task"
    elif event_type.startswith("reminder."):
        return "reminder"
    else:
        return "unknown"


async def handle_audit_event(event: Dict, topic: str) -> Dict:
    """
    Handle event for audit logging.

    This function is called for ALL events from ALL topics.
    It stores the complete event for compliance and debugging.

    Args:
        event: Event from Kafka
            {
                "event_id": "uuid",
                "event_type": "task.created",
                "task_id": 123,
                "user_id": 456,
                ...
            }
        topic: Source topic name (task-events, reminders, task-updates)

    Returns:
        dict: Response indicating success/retry/drop
            {"status": "SUCCESS" | "RETRY" | "DROP"}
    """
    try:
        event_id = event.get("event_id")
        event_type = event.get("event_type")
        user_id = event.get("user_id")
        task_id = event.get("task_id")
        timestamp_str = event.get("timestamp")

        logger.info(f"Received audit event: {event_type} from topic {topic} (event_id: {event_id})")

        # Parse timestamp
        timestamp = datetime.utcnow()
        if timestamp_str:
            try:
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            except Exception as e:
                logger.warning(f"Failed to parse timestamp {timestamp_str}: {e}")

        # Determine source service from topic
        source_service_map = {
            "task-events": "api-service",
            "reminders": "api-service",
            "task-updates": "various"
        }
        source_service = source_service_map.get(topic, "unknown")

        # Create audit log entry
        audit_entry = AuditLogEntry(
            event_id=event_id,
            user_id=user_id,
            action_type=parse_action_type(event_type),
            resource_type=parse_resource_type(event_type),
            resource_id=task_id,
            event_data=event,  # Store full event as JSONB
            source_service=source_service,
            timestamp=timestamp
        )

        # Insert into database
        with Session(engine) as session:
            # Check if event_id already exists (idempotency)
            existing = session.query(AuditLogEntry).filter(
                AuditLogEntry.event_id == event_id
            ).first()

            if existing:
                logger.info(f"Event {event_id} already logged, skipping (idempotent)")
                return {"status": "SUCCESS"}

            session.add(audit_entry)
            session.commit()

        logger.info(f"Audit log created: {event_type} for user {user_id} (log_id: {audit_entry.log_id})")
        return {"status": "SUCCESS"}

    except Exception as e:
        logger.error(f"Error creating audit log for event {event.get('event_id')}: {e}")
        return {"status": "RETRY"}  # Retry on errors
