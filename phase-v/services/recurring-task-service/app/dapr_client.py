"""
Dapr HTTP client for State Management and Pub/Sub operations.

Provides:
- State Management for idempotency tracking
- Pub/Sub for publishing new task occurrence events
"""

import httpx
import os
import logging
from datetime import datetime
from typing import Optional, Dict, Any
import uuid

logger = logging.getLogger(__name__)

# Dapr configuration
DAPR_HTTP_URL = os.getenv("DAPR_HTTP_URL", "http://localhost:3500")
STATE_STORE_NAME = os.getenv("DAPR_STATE_STORE", "postgres-statestore")
PUBSUB_NAME = os.getenv("DAPR_PUBSUB", "kafka-pubsub")


class DaprClient:
    """Client for Dapr State Management and Pub/Sub operations."""

    def __init__(self, dapr_url: str = DAPR_HTTP_URL):
        """
        Initialize Dapr client.

        Args:
            dapr_url: Dapr HTTP endpoint URL
        """
        self.dapr_url = dapr_url
        self.state_url = f"{dapr_url}/v1.0/state/{STATE_STORE_NAME}"
        self.pubsub_url = f"{dapr_url}/v1.0/publish/{PUBSUB_NAME}"

    async def save_state(self, key: str, value: Any) -> bool:
        """
        Save state to Dapr State Management.

        Args:
            key: State key
            value: State value (will be JSON serialized)

        Returns:
            True if successful, False otherwise
        """
        try:
            async with httpx.AsyncClient() as client:
                payload = [{"key": key, "value": value}]
                response = await client.post(
                    self.state_url,
                    json=payload,
                    timeout=10.0
                )
                response.raise_for_status()
                logger.info(f"State saved: {key}")
                return True

        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to save state for key {key}: HTTP {e.response.status_code}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error saving state for key {key}: {e}")
            return False

    async def get_state(self, key: str) -> Optional[Dict]:
        """
        Get state from Dapr State Management.

        Args:
            key: State key

        Returns:
            State value as dict, or None if not found
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.state_url}/{key}",
                    timeout=10.0
                )

                # 204 No Content means key doesn't exist
                if response.status_code == 204:
                    return None

                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            logger.error(f"Failed to get state for key {key}: HTTP {e.response.status_code}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting state for key {key}: {e}")
            return None

    async def publish_task_event(
        self,
        event_type: str,
        task_id: int,
        user_id: int,
        task_data: Dict
    ) -> bool:
        """
        Publish task event to Kafka via Dapr Pub/Sub.

        Args:
            event_type: Event type (e.g., "task.created")
            task_id: Task ID
            user_id: User ID
            task_data: Task data payload

        Returns:
            True if successful, False otherwise
        """
        try:
            event = {
                "event_id": str(uuid.uuid4()),
                "schema_version": "1.0",
                "event_type": event_type,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "task_id": task_id,
                "user_id": user_id,
                "task_data": task_data
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.pubsub_url}/task-events",
                    json=event,
                    timeout=10.0
                )
                response.raise_for_status()
                logger.info(
                    f"Published {event_type} event for task {task_id} "
                    f"(event_id: {event['event_id']})"
                )
                return True

        except httpx.HTTPStatusError as e:
            logger.error(
                f"Failed to publish {event_type} event for task {task_id}: "
                f"HTTP {e.response.status_code}"
            )
            return False
        except Exception as e:
            logger.error(
                f"Unexpected error publishing {event_type} event for task {task_id}: {e}"
            )
            return False


# Global Dapr client instance
dapr_client = DaprClient()
