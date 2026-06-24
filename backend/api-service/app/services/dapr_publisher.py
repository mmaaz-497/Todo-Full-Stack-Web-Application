"""Dapr Publisher Service for Event Publishing (Phase V)

This module implements the Dapr publisher for publishing events
through Dapr pub/sub components instead of direct Kafka access.
"""

import asyncio
import httpx
from typing import Dict, Any, Optional
from datetime import datetime
from uuid import uuid4
import os


class DaprPublisher:
    """Service for publishing events via Dapr pub/sub."""

    def __init__(self, dapr_http_port: Optional[int] = None):
        """Initialize the Dapr publisher."""
        self.dapr_http_port = dapr_http_port or int(os.getenv("DAPR_HTTP_PORT", "3500"))
        self.dapr_url = f"http://localhost:{self.dapr_http_port}"

    async def publish_event(
        self,
        pubsub_name: str,
        topic: str,
        data: Dict[str, Any]
    ):
        """Publish an event via Dapr."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.dapr_url}/v1.0/publish/{pubsub_name}/{topic}",
                    json=data,
                    timeout=30.0  # 30 second timeout
                )

                if response.status_code not in [200, 204]:
                    raise Exception(f"Dapr publish failed with status {response.status_code}: {response.text}")

                print(f"Dapr published to {pubsub_name}/{topic}")
            except httpx.RequestError as e:
                print(f"Error connecting to Dapr: {e}")
                raise
            except Exception as e:
                print(f"Error publishing event via Dapr: {e}")
                raise

    async def publish_task_event(
        self,
        event_type: str,
        task_data: Dict[str, Any],
        user_id: str,
        source: str = "backend-api"
    ):
        """Publish a task event via Dapr."""
        event = {
            "event_id": str(uuid4()),
            "event_type": event_type,
            "task_id": task_data.get("id"),
            "task_data": task_data,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": {
                "source": source,
                "created_at": datetime.utcnow().isoformat()
            }
        }

        await self.publish_event(
            pubsub_name="kafka-pubsub",  # This should match your Dapr component name
            topic="task-events",
            data=event
        )

    async def publish_reminder(
        self,
        task_id: int,
        title: str,
        description: str,
        due_at: datetime,
        remind_at: datetime,
        user_id: str,
        user_email: str
    ):
        """Publish a reminder event via Dapr."""
        event = {
            "reminder_id": str(uuid4()),
            "task_id": task_id,
            "title": title,
            "description": description,
            "due_at": due_at.isoformat() if hasattr(due_at, 'isoformat') else str(due_at),
            "remind_at": remind_at.isoformat() if hasattr(remind_at, 'isoformat') else str(remind_at),
            "user_id": user_id,
            "user_email": user_email,
            "notification_channels": ["email"],
            "timestamp": datetime.utcnow().isoformat()
        }

        await self.publish_event(
            pubsub_name="kafka-pubsub",
            topic="reminders",
            data=event
        )

    async def publish_task_update(
        self,
        task_id: int,
        change_type: str,
        updated_fields: list,
        task_snapshot: Dict[str, Any],
        user_id: str
    ):
        """Publish a task update event via Dapr."""
        event = {
            "update_id": str(uuid4()),
            "task_id": task_id,
            "change_type": change_type,
            "updated_fields": updated_fields,
            "task_snapshot": task_snapshot,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        }

        await self.publish_event(
            pubsub_name="kafka-pubsub",
            topic="task-updates",
            data=event
        )

    async def publish_audit_log(
        self,
        event_type: str,
        resource_type: str,
        resource_id: int,
        user_id: str,
        payload: Dict[str, Any]
    ):
        """Publish an audit log event via Dapr."""
        event = {
            "log_id": str(uuid4()),
            "event_type": event_type,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "user_id": user_id,
            "payload": payload,
            "timestamp": datetime.utcnow().isoformat()
        }

        await self.publish_event(
            pubsub_name="kafka-pubsub",
            topic="audit-logs",
            data=event
        )


# Global instance
dapr_publisher = DaprPublisher()