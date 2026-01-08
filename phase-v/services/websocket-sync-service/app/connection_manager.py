"""
WebSocket connection manager.

Handles:
- WebSocket connection lifecycle
- User-to-connections mapping
- Broadcasting to specific users
- Connection health monitoring
"""

from fastapi import WebSocket
from typing import Dict, List, Set
import logging
import asyncio

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections for real-time task synchronization.

    Maintains a mapping of user_id to list of WebSocket connections.
    A user can have multiple connections (multiple browser tabs/devices).
    """

    def __init__(self):
        """Initialize connection manager."""
        # user_id -> list of WebSocket connections
        self.active_connections: Dict[int, List[WebSocket]] = {}
        # WebSocket -> user_id (reverse mapping for cleanup)
        self.connection_to_user: Dict[WebSocket, int] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        """
        Accept WebSocket connection and register it for a user.

        Args:
            websocket: WebSocket connection
            user_id: User ID who owns this connection
        """
        await websocket.accept()

        if user_id not in self.active_connections:
            self.active_connections[user_id] = []

        self.active_connections[user_id].append(websocket)
        self.connection_to_user[websocket] = user_id

        logger.info(
            f"WebSocket connected: user_id={user_id}, "
            f"total_connections_for_user={len(self.active_connections[user_id])}"
        )

    def disconnect(self, websocket: WebSocket):
        """
        Remove WebSocket connection from active connections.

        Args:
            websocket: WebSocket connection to remove
        """
        if websocket not in self.connection_to_user:
            return

        user_id = self.connection_to_user[websocket]

        # Remove from user's connections list
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)

            # Clean up empty user entry
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

        # Remove reverse mapping
        del self.connection_to_user[websocket]

        logger.info(
            f"WebSocket disconnected: user_id={user_id}, "
            f"remaining_connections_for_user={len(self.active_connections.get(user_id, []))}"
        )

    async def send_personal_message(self, message: dict, user_id: int):
        """
        Send message to all connections of a specific user.

        Args:
            message: Message to send (will be JSON serialized)
            user_id: User ID to send message to
        """
        if user_id not in self.active_connections:
            logger.debug(f"No active connections for user {user_id}")
            return

        connections = self.active_connections[user_id]
        logger.info(f"Broadcasting to user {user_id}: {len(connections)} connections")

        # Send to all user's connections concurrently
        tasks = []
        for connection in connections:
            tasks.append(self._send_json(connection, message))

        # Wait for all sends to complete
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _send_json(self, websocket: WebSocket, message: dict):
        """
        Send JSON message to a WebSocket connection.

        Handles disconnection gracefully.

        Args:
            websocket: WebSocket connection
            message: Message to send
        """
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending message to WebSocket: {e}")
            # Connection broken, clean up
            self.disconnect(websocket)

    def get_active_users(self) -> Set[int]:
        """
        Get set of user IDs with active connections.

        Returns:
            Set of user IDs
        """
        return set(self.active_connections.keys())

    def get_connection_count(self, user_id: int) -> int:
        """
        Get number of active connections for a user.

        Args:
            user_id: User ID

        Returns:
            Number of active connections
        """
        return len(self.active_connections.get(user_id, []))

    def get_total_connections(self) -> int:
        """
        Get total number of active WebSocket connections.

        Returns:
            Total connection count
        """
        return len(self.connection_to_user)


# Global connection manager instance
connection_manager = ConnectionManager()
