"""
Event consumer for task-updates.

Handles:
- Task update event consumption
- Broadcasting to WebSocket clients
- Event filtering by user
"""

from typing import Dict
import logging

from .connection_manager import connection_manager

logger = logging.getLogger(__name__)


async def handle_task_update_event(event: Dict) -> Dict:
    """
    Handle task update event and broadcast to WebSocket clients.

    Processing logic:
    1. Extract user_id from event
    2. Check if user has active WebSocket connections
    3. Broadcast update to all user's connections
    4. Return success

    Args:
        event: Task update event from Kafka
            {
                "event_id": "uuid",
                "event_type": "task.sync",
                "timestamp": "2026-01-03T10:00:00Z",
                "user_id": 1,
                "operation": "create | update | delete",
                "task_id": 123,
                "task_snapshot": {
                    "title": "Buy milk",
                    "status": "pending",
                    "updated_at": "2026-01-03T10:00:00Z"
                }
            }

    Returns:
        dict: Response indicating success/drop
            {"status": "SUCCESS" | "DROP"}
    """
    try:
        event_id = event.get("event_id")
        event_type = event.get("event_type")
        user_id = event.get("user_id")
        operation = event.get("operation")
        task_id = event.get("task_id")
        task_snapshot = event.get("task_snapshot", {})

        logger.info(
            f"Received task update event: {event_type} for user {user_id}, "
            f"task {task_id}, operation={operation} (event_id: {event_id})"
        )

        # Check if user has active connections
        connection_count = connection_manager.get_connection_count(user_id)

        if connection_count == 0:
            logger.debug(f"No active WebSocket connections for user {user_id}, skipping broadcast")
            return {"status": "DROP"}  # No connections, nothing to do

        # Prepare WebSocket message
        ws_message = {
            "type": "task_update",
            "operation": operation,
            "task_id": task_id,
            "task": task_snapshot,
            "timestamp": event.get("timestamp")
        }

        # Broadcast to all user's connections
        await connection_manager.send_personal_message(ws_message, user_id)

        logger.info(
            f"Broadcasted task update to {connection_count} connection(s) for user {user_id}"
        )
        return {"status": "SUCCESS"}

    except Exception as e:
        logger.error(f"Error handling task update event {event.get('event_id')}: {e}")
        # Don't retry WebSocket broadcasts - they're best-effort
        return {"status": "DROP"}
