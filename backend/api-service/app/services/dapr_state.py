"""Dapr State Management Service (Phase V)

This module implements state management via Dapr for conversation history
and other stateful operations.
"""

import asyncio
import httpx
from typing import Dict, Any, Optional, Union
import json
import os


class DaprStateManager:
    """Service for managing state via Dapr state store."""

    def __init__(self, dapr_http_port: Optional[int] = None):
        """Initialize the Dapr state manager."""
        self.dapr_http_port = dapr_http_port or int(os.getenv("DAPR_HTTP_PORT", "3500"))
        self.dapr_url = f"http://localhost:{self.dapr_http_port}"

    async def save_state(
        self,
        store_name: str,
        key: str,
        value: Any,
        etag: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Save state via Dapr."""
        async with httpx.AsyncClient() as client:
            try:
                # Prepare the state item
                state_item = {
                    "key": key,
                    "value": value
                }

                if etag:
                    state_item["etag"] = etag
                if options:
                    state_item["options"] = options

                response = await client.post(
                    f"{self.dapr_url}/v1.0/state/{store_name}",
                    json=[state_item],
                    timeout=30.0
                )

                if response.status_code != 204:
                    raise Exception(f"Dapr save state failed with status {response.status_code}: {response.text}")

                print(f"Dapr saved state for key {key} in store {store_name}")
                return True
            except httpx.RequestError as e:
                print(f"Error connecting to Dapr: {e}")
                raise
            except Exception as e:
                print(f"Error saving state via Dapr: {e}")
                raise

    async def get_state(
        self,
        store_name: str,
        key: str,
        consistency: Optional[str] = None
    ) -> Optional[Any]:
        """Get state via Dapr."""
        try:
            url = f"{self.dapr_url}/v1.0/state/{store_name}/{key}"
            if consistency:
                url += f"?consistency={consistency}"

            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=30.0)

            if response.status_code == 204:
                # No content found
                return None
            elif response.status_code == 404:
                # Key not found
                return None
            elif response.status_code == 200:
                # Successfully retrieved
                return response.json()
            else:
                raise Exception(f"Dapr get state failed with status {response.status_code}: {response.text}")
        except httpx.RequestError as e:
            print(f"Error connecting to Dapr: {e}")
            raise
        except Exception as e:
            print(f"Error getting state via Dapr: {e}")
            raise

    async def save_conversation_state(
        self,
        conversation_id: str,
        messages: list,
        user_id: str
    ) -> bool:
        """Save conversation history to Dapr state store."""
        state_key = f"conversation-{user_id}-{conversation_id}"
        state_value = {
            "conversation_id": conversation_id,
            "user_id": user_id,
            "messages": messages,
            "updated_at": str(datetime.utcnow())
        }

        return await self.save_state(
            store_name="statestore",  # This should match your Dapr component name
            key=state_key,
            value=state_value
        )

    async def get_conversation_state(
        self,
        conversation_id: str,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get conversation history from Dapr state store."""
        state_key = f"conversation-{user_id}-{conversation_id}"
        return await self.get_state(
            store_name="statestore",
            key=state_key
        )

    async def save_user_preferences(
        self,
        user_id: str,
        preferences: Dict[str, Any]
    ) -> bool:
        """Save user preferences to Dapr state store."""
        state_key = f"user-preferences-{user_id}"
        state_value = {
            **preferences,
            "updated_at": str(datetime.utcnow())
        }

        return await self.save_state(
            store_name="statestore",
            key=state_key,
            value=state_value
        )

    async def get_user_preferences(
        self,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get user preferences from Dapr state store."""
        state_key = f"user-preferences-{user_id}"
        return await self.get_state(
            store_name="statestore",
            key=state_key
        )

    async def delete_state(
        self,
        store_name: str,
        key: str
    ) -> bool:
        """Delete state via Dapr."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.dapr_url}/v1.0/state/{store_name}/{key}",
                    timeout=30.0
                )

                if response.status_code == 204:
                    print(f"Dapr deleted state for key {key} in store {store_name}")
                    return True
                else:
                    raise Exception(f"Dapr delete state failed with status {response.status_code}: {response.text}")
        except httpx.RequestError as e:
            print(f"Error connecting to Dapr: {e}")
            raise
        except Exception as e:
            print(f"Error deleting state via Dapr: {e}")
            raise


from datetime import datetime


# Global instance
dapr_state_manager = DaprStateManager()