"""Reminder callback endpoints for Dapr Jobs API integration.

This module provides:
- Callback endpoint for Dapr Jobs API when reminders trigger
- Reminder event publishing to Kafka via Dapr Pub/Sub
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import logging

from app.events.publisher import DaprPublisher

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize event publisher
event_publisher = DaprPublisher()


class ReminderCallbackPayload(BaseModel):
    """
    Payload sent by Dapr Jobs API when a reminder job triggers.

    This matches the job_data structure created in reminder_scheduler.py
    """
    task_id: int
    user_id: int
    due_date: str  # ISO 8601 datetime string
    task_title: str
    task_description: Optional[str] = None
    reminder_time: str  # ISO 8601 datetime string


@router.post(
    "/api/reminders/callback",
    status_code=status.HTTP_200_OK,
    tags=["Reminders"],
    summary="Dapr Jobs API reminder callback",
    description="Triggered by Dapr Jobs API when a scheduled reminder is due"
)
async def reminder_callback(payload: ReminderCallbackPayload):
    """
    Handle reminder trigger from Dapr Jobs API.

    This endpoint is called automatically by Dapr when a scheduled reminder job executes.
    It publishes a reminder event to the 'reminders' Kafka topic, which will be consumed
    by the Notification Service to send email notifications.

    Args:
        payload: Reminder data from Dapr Jobs API

    Returns:
        dict: Success message

    Raises:
        HTTPException: If event publishing fails critically
    """
    try:
        logger.info(
            f"Reminder callback triggered for task {payload.task_id}, "
            f"user {payload.user_id}, due at {payload.due_date}"
        )

        # Parse ISO datetime strings
        due_date_dt = datetime.fromisoformat(payload.due_date.replace('Z', '+00:00'))
        reminder_time_dt = datetime.fromisoformat(payload.reminder_time.replace('Z', '+00:00'))

        # Publish reminder event to Kafka via Dapr Pub/Sub
        # The Notification Service consumes this topic and sends emails
        await event_publisher.publish_reminder_event(
            task_id=payload.task_id,
            user_id=payload.user_id,
            due_date=due_date_dt,
            task_title=payload.task_title,
            task_description=payload.task_description
        )

        logger.info(
            f"Reminder event published successfully for task {payload.task_id}"
        )

        return {
            "status": "success",
            "message": f"Reminder event published for task {payload.task_id}",
            "task_id": payload.task_id,
            "user_id": payload.user_id
        }

    except Exception as e:
        logger.error(
            f"Failed to process reminder callback for task {payload.task_id}: {e}"
        )
        # Return 200 anyway to prevent Dapr from retrying (we log the error)
        # In production, you might want to publish to DLQ instead
        return {
            "status": "error",
            "message": f"Failed to publish reminder event: {str(e)}",
            "task_id": payload.task_id
        }
