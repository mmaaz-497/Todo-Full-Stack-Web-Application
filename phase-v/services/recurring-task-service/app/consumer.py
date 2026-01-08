"""
Event consumer for task.completed events.

Handles:
- Filtering for recurring tasks
- Idempotency checking
- Next occurrence calculation
- New task event publishing
"""

from datetime import datetime
from typing import Dict
import logging

from .generator import calculate_next_occurrence
from .dapr_client import dapr_client

logger = logging.getLogger(__name__)


async def handle_task_event(event: Dict) -> Dict:
    """
    Handle task event from Kafka via Dapr subscription.

    Processing logic:
    1. Check if event is task.completed
    2. Check if task has recurrence_rule
    3. Check idempotency (have we processed this event?)
    4. Calculate next occurrence
    5. Publish task.created event for new occurrence
    6. Save idempotency state

    Args:
        event: Task event from Kafka
            {
                "event_id": "uuid",
                "event_type": "task.completed",
                "task_id": 123,
                "user_id": 456,
                "task_data": {...}
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
        task_data = event.get("task_data", {})

        logger.info(f"Received event: {event_type} for task {task_id} (event_id: {event_id})")

        # Filter: Only process task.completed events
        if event_type != "task.completed":
            logger.debug(f"Ignoring non-completion event: {event_type}")
            return {"status": "DROP"}

        # Check if task is recurring
        recurrence_rule = task_data.get("recurrence_rule")
        if not recurrence_rule:
            logger.debug(f"Task {task_id} is not recurring, skipping")
            return {"status": "DROP"}

        # Idempotency check: Have we already processed this event?
        idempotency_key = f"recurring-task:processed:{event_id}"
        already_processed = await dapr_client.get_state(idempotency_key)

        if already_processed:
            logger.info(f"Event {event_id} already processed, skipping (idempotent)")
            return {"status": "SUCCESS"}  # Already done, don't retry

        # Calculate next occurrence
        completed_at = datetime.utcnow()
        due_date_str = task_data.get("due_date")
        original_due_date = None

        if due_date_str:
            try:
                original_due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
            except Exception as e:
                logger.warning(f"Failed to parse due_date: {due_date_str}, error: {e}")

        next_due_date = calculate_next_occurrence(
            completed_at=completed_at,
            recurrence_rule=recurrence_rule,
            original_due_date=original_due_date
        )

        if not next_due_date:
            logger.error(f"Failed to calculate next occurrence for task {task_id}")
            return {"status": "DROP"}  # Invalid recurrence rule, don't retry

        logger.info(f"Next occurrence for task {task_id}: {next_due_date.isoformat()}")

        # Create task data for new occurrence
        new_task_data = {
            **task_data,
            "due_date": next_due_date.isoformat() + "Z",
            "status": "pending",  # Reset status
            "completed_at": None,  # Clear completion timestamp
            "parent_task_id": task_id  # Link to original recurring task
        }

        # Publish task.created event for new occurrence
        success = await dapr_client.publish_task_event(
            event_type="task.created",
            task_id=task_id,  # Note: API Service will assign new ID
            user_id=user_id,
            task_data=new_task_data
        )

        if not success:
            logger.error(f"Failed to publish task.created event for task {task_id}")
            return {"status": "RETRY"}  # Retry publishing

        # Save idempotency state (mark event as processed)
        await dapr_client.save_state(idempotency_key, {
            "processed_at": datetime.utcnow().isoformat(),
            "task_id": task_id,
            "next_due_date": next_due_date.isoformat()
        })

        logger.info(f"Successfully generated next occurrence for task {task_id}")
        return {"status": "SUCCESS"}

    except Exception as e:
        logger.error(f"Unexpected error handling event {event.get('event_id')}: {e}")
        return {"status": "RETRY"}  # Retry on unexpected errors
