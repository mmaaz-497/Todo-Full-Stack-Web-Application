"""Dapr HTTP client for pub/sub, state management, and service invocation."""
import httpx
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class DaprClient:
    """HTTP client for Dapr sidecar communication."""

    def __init__(self, dapr_url: str = "http://localhost:3500"):
        """Initialize Dapr client.

        Args:
            dapr_url: Dapr sidecar HTTP endpoint (default: http://localhost:3500)
        """
        self.dapr_url = dapr_url
        self.timeout = 10.0  # seconds

    async def publish_event(
        self,
        pubsub_name: str,
        topic_name: str,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, str]] = None
    ) -> bool:
        """Publish event to Kafka topic via Dapr pub/sub.

        Args:
            pubsub_name: Name of Dapr pub/sub component
            topic_name: Kafka topic name
            data: Event payload (will be JSON serialized)
            metadata: Optional metadata for the event

        Returns:
            True if successful, False otherwise

        Raises:
            httpx.HTTPError: If Dapr sidecar is unreachable or returns error
        """
        url = f"{self.dapr_url}/v1.0/publish/{pubsub_name}/{topic_name}"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json=data,
                    headers={"Content-Type": "application/json"},
                    timeout=self.timeout
                )
                response.raise_for_status()
                logger.info(f"Published event to {topic_name}: {data.get('event_id', 'unknown')}")
                return True

        except httpx.HTTPError as e:
            logger.error(f"Failed to publish event to {topic_name}: {e}")
            raise

    async def get_state(
        self,
        store_name: str,
        key: str
    ) -> Optional[Any]:
        """Get state from Dapr state store.

        Args:
            store_name: Name of Dapr state store component
            key: State key

        Returns:
            State value or None if not found
        """
        url = f"{self.dapr_url}/v1.0/state/{store_name}/{key}"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=self.timeout)
                response.raise_for_status()
                return response.json() if response.content else None

        except httpx.HTTPError as e:
            logger.error(f"Failed to get state {key} from {store_name}: {e}")
            return None

    async def save_state(
        self,
        store_name: str,
        key: str,
        value: Any,
        metadata: Optional[Dict[str, str]] = None
    ) -> bool:
        """Save state to Dapr state store.

        Args:
            store_name: Name of Dapr state store component
            key: State key
            value: State value (will be JSON serialized)
            metadata: Optional metadata (e.g., ttlInSeconds)

        Returns:
            True if successful, False otherwise
        """
        url = f"{self.dapr_url}/v1.0/state/{store_name}"

        payload = [
            {
                "key": key,
                "value": value,
                "metadata": metadata or {}
            }
        ]

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json=payload,
                    timeout=self.timeout
                )
                response.raise_for_status()
                logger.info(f"Saved state {key} to {store_name}")
                return True

        except httpx.HTTPError as e:
            logger.error(f"Failed to save state {key} to {store_name}: {e}")
            return False

    async def invoke_service(
        self,
        app_id: str,
        method: str,
        data: Optional[Dict[str, Any]] = None,
        http_verb: str = "POST"
    ) -> Optional[Dict[str, Any]]:
        """Invoke another service via Dapr service invocation.

        Args:
            app_id: Target service app ID (from dapr.io/app-id annotation)
            method: HTTP method path (e.g., "/api/validate")
            data: Request payload
            http_verb: HTTP verb (GET, POST, PUT, DELETE)

        Returns:
            Response data or None if failed
        """
        url = f"{self.dapr_url}/v1.0/invoke/{app_id}/method{method}"

        try:
            async with httpx.AsyncClient() as client:
                if http_verb.upper() == "GET":
                    response = await client.get(url, timeout=self.timeout)
                elif http_verb.upper() == "POST":
                    response = await client.post(url, json=data, timeout=self.timeout)
                elif http_verb.upper() == "PUT":
                    response = await client.put(url, json=data, timeout=self.timeout)
                elif http_verb.upper() == "DELETE":
                    response = await client.delete(url, timeout=self.timeout)
                else:
                    raise ValueError(f"Unsupported HTTP verb: {http_verb}")

                response.raise_for_status()
                return response.json() if response.content else None

        except httpx.HTTPError as e:
            logger.error(f"Failed to invoke {app_id}{method}: {e}")
            return None
