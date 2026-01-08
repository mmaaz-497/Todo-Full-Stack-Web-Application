"""Event publisher for Kafka via Dapr pub/sub."""
import uuid
import logging
from typing import Optional
from datetime import datetime

from app.dapr_client import DaprClient
from app.events.schemas import TaskEvent, ReminderEvent, TaskUpdateEvent, TaskEventData, TaskSnapshot

logger = logging.getLogger(__name__)


class DaprPublisher:
    """Publisher for Kafka events via Dapr pub/sub component."""

    def __init__(self, dapr_url: str = "http://localhost:3500"):
        """Initialize publisher.

        Args:
            dapr_url: Dapr sidecar HTTP endpoint
        """
        self.dapr_client = DaprClient(dapr_url)
        self.pubsub_name = "kafka-pubsub"  # Dapr component name

    async def publish_task_event(
        self,
        event_type: str,
        task_id: int,
        user_id: int,
        task_data: dict
    ) -> bool:
        """Publish task event to task-events topic.

        Args:
            event_type: task.created, task.updated, task.deleted, task.completed
            task_id: Task ID
            user_id: User ID
            task_data: Task data dictionary

        Returns:
            True if published successfully
        """
        try:
            # Create event with proper schema
            event = TaskEvent(
                event_type=event_type,
                task_id=task_id,
                user_id=user_id,
                task_data=TaskEventData(**task_data)
            )

            # Publish to Kafka via Dapr
            success = await self.dapr_client.publish_event(
                pubsub_name=self.pubsub_name,
                topic_name="task-events",
                data=event.model_dump(mode='json')
            )

            if success:
                logger.info(f"Published {event_type} event for task {task_id}")
            return success

        except Exception as e:
            logger.error(f"Failed to publish task event: {e}")
            return False

    async def publish_reminder_event(
        self,
        task_id: int,
        user_id: int,
        due_date: datetime,
        task_title: str,
        task_description: Optional[str] = None,
        reminder_time: Optional[datetime] = None
    ) -> bool:
        """Publish reminder event to reminders topic.

        Args:
            task_id: Task ID
            user_id: User ID
            due_date: Task due date
            task_title: Task title
            task_description: Task description
            reminder_time: When reminder should be sent

        Returns:
            True if published successfully
        """
        try:
            event = ReminderEvent(
                task_id=task_id,
                user_id=user_id,
                due_date=due_date,
                task_title=task_title,
                task_description=task_description,
                reminder_time=reminder_time or datetime.utcnow()
            )

            success = await self.dapr_client.publish_event(
                pubsub_name=self.pubsub_name,
                topic_name="reminders",
                data=event.model_dump(mode='json')
            )

            if success:
                logger.info(f"Published reminder event for task {task_id}")
            return success

        except Exception as e:
            logger.error(f"Failed to publish reminder event: {e}")
            return False

    async def publish_task_update_event(
        self,
        user_id: int,
        operation: str,
        task_id: int,
        task_snapshot: dict
    ) -> bool:
        """Publish task update event to task-updates topic for WebSocket sync.

        Args:
            user_id: User ID
            operation: create, update, delete
            task_id: Task ID
            task_snapshot: Minimal task data for UI update

        Returns:
            True if published successfully
        """
        try:
            event = TaskUpdateEvent(
                user_id=user_id,
                operation=operation,
                task_id=task_id,
                task_snapshot=TaskSnapshot(**task_snapshot)
            )

            success = await self.dapr_client.publish_event(
                pubsub_name=self.pubsub_name,
                topic_name="task-updates",
                data=event.model_dump(mode='json')
            )

            if success:
                logger.info(f"Published task update event for task {task_id}")
            return success

        except Exception as e:
            logger.error(f"Failed to publish task update event: {e}")
            return False

    async def publish_to_dlq(
        self,
        original_event: dict,
        error_message: str,
        retry_count: int,
        consumer_service: str
    ) -> bool:
        """Publish failed event to dead letter queue.

        Args:
            original_event: The original event that failed
            error_message: Error description
            retry_count: Number of retry attempts
            consumer_service: Service that failed to process event

        Returns:
            True if published successfully
        """
        try:
            dlq_event = {
                "dlq_id": str(uuid.uuid4()),
                "original_event_id": original_event.get("event_id"),
                "original_topic": original_event.get("_topic", "unknown"),
                "original_event": original_event,
                "error_context": {
                    "error_message": error_message,
                    "retry_count": retry_count,
                    "consumer_service": consumer_service,
                    "timestamp": datetime.utcnow().isoformat()
                },
                "timestamp": datetime.utcnow().isoformat()
            }

            success = await self.dapr_client.publish_event(
                pubsub_name=self.pubsub_name,
                topic_name="dlq-events",
                data=dlq_event
            )

            if success:
                logger.warning(f"Published event {original_event.get('event_id')} to DLQ")
            return success

        except Exception as e:
            logger.error(f"Failed to publish to DLQ: {e}")
            return False
