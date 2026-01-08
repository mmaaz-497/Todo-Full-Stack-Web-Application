"""
Event consumer for reminder events.

Handles:
- Filtering for reminder.due events
- Idempotency checking
- Email notification sending
- Delivery status tracking
"""

from datetime import datetime
from typing import Dict
import logging

from .email_sender import email_sender
from .dapr_client import dapr_client

logger = logging.getLogger(__name__)


async def handle_reminder_event(event: Dict) -> Dict:
    """
    Handle reminder event from Kafka via Dapr subscription.

    Processing logic:
    1. Check if event is reminder.due
    2. Check idempotency (have we sent this notification?)
    3. Extract task and user details
    4. Send email notification
    5. Save delivery status

    Args:
        event: Reminder event from Kafka
            {
                "event_id": "uuid",
                "event_type": "reminder.due",
                "task_id": 123,
                "user_id": 456,
                "due_date": "2026-01-03T14:00:00Z",
                "task_title": "Team meeting",
                "task_description": "Weekly sync",
                "notification_channels": ["email"],
                "reminder_time": "2026-01-03T13:00:00Z"
            }

    Returns:
        dict: Response indicating success/retry/drop
            {"status": "SUCCESS" | "RETRY" | "DROP"}
    """
    try:
        event_id = event.get("event_id")
        event_type = event.get("event_type")
        task_id = event.get("task_id")
        user_id = event.get("user_id")

        logger.info(f"Received event: {event_type} for task {task_id} (event_id: {event_id})")

        # Filter: Only process reminder.due events
        if event_type != "reminder.due":
            logger.debug(f"Ignoring non-reminder event: {event_type}")
            return {"status": "DROP"}

        # Idempotency check: Have we already sent this notification?
        idempotency_key = f"notification:sent:{event_id}"
        already_sent = await dapr_client.get_state(idempotency_key)

        if already_sent:
            logger.info(f"Notification for event {event_id} already sent, skipping (idempotent)")
            return {"status": "SUCCESS"}  # Already done, don't retry

        # Extract task details
        task_title = event.get("task_title", "Untitled Task")
        task_description = event.get("task_description")
        due_date = event.get("due_date", "Unknown")
        notification_channels = event.get("notification_channels", ["email"])

        # Check if email notification is requested
        if "email" not in notification_channels:
            logger.info(f"Email notification not requested for task {task_id}, skipping")
            return {"status": "DROP"}

        # Get user email (in production, this would come from user service)
        # For now, we'll use a placeholder or derive from user_id
        # TODO: Integrate with user service to get actual email
        recipient_email = f"user{user_id}@example.com"  # Placeholder

        logger.info(f"Sending reminder email to {recipient_email} for task {task_id}")

        # Send email notification
        success = await email_sender.send_reminder_email(
            recipient_email=recipient_email,
            task_title=task_title,
            task_description=task_description,
            due_date=due_date,
            task_id=task_id
        )

        if not success:
            logger.error(f"Failed to send email notification for task {task_id}")
            return {"status": "RETRY"}  # Retry sending

        # Save idempotency state (mark notification as sent)
        delivery_status = {
            "sent_at": datetime.utcnow().isoformat(),
            "task_id": task_id,
            "user_id": user_id,
            "recipient_email": recipient_email,
            "channel": "email",
            "status": "delivered"
        }

        await dapr_client.save_state(idempotency_key, delivery_status)

        logger.info(
            f"Reminder notification sent successfully for task {task_id} to {recipient_email}"
        )
        return {"status": "SUCCESS"}

    except Exception as e:
        logger.error(f"Unexpected error handling reminder event {event.get('event_id')}: {e}")
        return {"status": "RETRY"}  # Retry on unexpected errors
