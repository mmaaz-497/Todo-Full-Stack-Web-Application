"""
Dapr HTTP client for Secrets Management and State operations.

Provides:
- Secrets retrieval for SMTP credentials
- State Management for idempotency tracking
"""

import httpx
import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Dapr configuration
DAPR_HTTP_URL = os.getenv("DAPR_HTTP_URL", "http://localhost:3500")
SECRET_STORE_NAME = os.getenv("DAPR_SECRET_STORE", "kubernetes-secrets")
STATE_STORE_NAME = os.getenv("DAPR_STATE_STORE", "postgres-statestore")


class DaprClient:
    """Client for Dapr Secrets and State Management operations."""

    def __init__(self, dapr_url: str = DAPR_HTTP_URL):
        """
        Initialize Dapr client.

        Args:
            dapr_url: Dapr HTTP endpoint URL
        """
        self.dapr_url = dapr_url
        self.secrets_url = f"{dapr_url}/v1.0/secrets/{SECRET_STORE_NAME}"
        self.state_url = f"{dapr_url}/v1.0/state/{STATE_STORE_NAME}"

    async def get_secret(self, secret_name: str) -> Optional[Dict[str, str]]:
        """
        Get secret from Dapr Secrets Management.

        Args:
            secret_name: Secret name (Kubernetes Secret resource name)

        Returns:
            Dict of secret key-value pairs, or None if not found

        Example:
            secrets = await client.get_secret("backend-secrets")
            smtp_host = secrets.get("SMTP_HOST")
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.secrets_url}/{secret_name}",
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"Secret {secret_name} not found")
                return None
            logger.error(f"Failed to get secret {secret_name}: HTTP {e.response.status_code}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting secret {secret_name}: {e}")
            return None

    async def get_smtp_credentials(self) -> Optional[Dict[str, str]]:
        """
        Get SMTP credentials from Kubernetes secrets via Dapr.

        Returns:
            Dict with SMTP configuration:
            {
                "SMTP_HOST": "smtp.gmail.com",
                "SMTP_PORT": "587",
                "SMTP_USERNAME": "your-email@gmail.com",
                "SMTP_PASSWORD": "your-app-password",
                "SMTP_FROM_EMAIL": "noreply@example.com"
            }
        """
        return await self.get_secret("backend-secrets")

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


# Global Dapr client instance
dapr_client = DaprClient()
