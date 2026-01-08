"""
WebSocket Sync Service - Main Application

FastAPI application with:
- WebSocket endpoint for real-time task synchronization
- Dapr Pub/Sub subscription for task-updates events
- JWT authentication for WebSocket connections
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Query
from typing import List
import logging
import os

from .connection_manager import connection_manager
from .consumer import handle_task_update_event
from .auth import verify_token

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Dapr configuration
PUBSUB_NAME = os.getenv("DAPR_PUBSUB", "kafka-pubsub")
TOPIC_NAME = os.getenv("DAPR_TOPIC", "task-updates")

# Create FastAPI app
app = FastAPI(
    title="WebSocket Sync Service",
    description="Real-time task synchronization via WebSocket",
    version="1.0.0"
)


@app.get("/dapr/subscribe")
async def subscribe():
    """
    Dapr subscription endpoint.

    Subscribe to task-updates Kafka topic for real-time broadcasting.

    Returns:
        List of subscription configurations
    """
    subscriptions = [
        {
            "pubsubname": PUBSUB_NAME,
            "topic": TOPIC_NAME,
            "route": "/events/task-updates"
        }
    ]
    logger.info(f"Dapr subscription configured: {subscriptions}")
    return subscriptions


@app.post("/events/task-updates")
async def task_updates_handler(request: Request):
    """
    Handle task-updates events from Kafka via Dapr.

    This endpoint receives events and broadcasts them to connected WebSocket clients.

    Dapr CloudEvent format:
    {
        "data": {
            "event_id": "uuid",
            "event_type": "task.sync",
            "user_id": 1,
            "operation": "create",
            "task_id": 123,
            "task_snapshot": {...}
        }
    }

    Returns:
        Response with status (SUCCESS/DROP)
    """
    try:
        cloud_event = await request.json()
        event_data = cloud_event.get("data", {})

        if not event_data:
            return {"status": "DROP"}

        result = await handle_task_update_event(event_data)
        return result

    except Exception as e:
        logger.error(f"Error processing task-updates event: {e}")
        return {"status": "DROP"}  # Don't retry WebSocket broadcasts


@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(..., description="JWT authentication token")
):
    """
    WebSocket endpoint for real-time task synchronization.

    Clients connect to this endpoint to receive real-time task updates.

    Connection flow:
    1. Client sends JWT token as query parameter
    2. Server validates token and extracts user_id
    3. Connection is registered for that user
    4. Server sends updates when task events occur
    5. Client can send ping/pong for keep-alive

    Args:
        websocket: WebSocket connection
        token: JWT authentication token (query parameter)

    Example connection (JavaScript):
        const ws = new WebSocket('ws://localhost:8000/ws?token=YOUR_JWT_TOKEN');

        ws.onmessage = (event) => {
            const update = JSON.parse(event.data);
            console.log('Task update:', update);
            // Update UI with task changes
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };

        ws.onclose = () => {
            console.log('WebSocket disconnected');
            // Attempt reconnection
        };
    """
    user_id = None

    try:
        # Validate JWT token and extract user_id
        user_id = verify_token(token)
        logger.info(f"WebSocket authentication successful for user {user_id}")

    except Exception as e:
        logger.error(f"WebSocket authentication failed: {e}")
        await websocket.close(code=1008, reason="Authentication failed")
        return

    # Accept connection and register
    await connection_manager.connect(websocket, user_id)

    # Send welcome message
    await websocket.send_json({
        "type": "connected",
        "user_id": user_id,
        "message": "WebSocket connection established"
    })

    try:
        # Keep connection alive and handle client messages
        while True:
            # Wait for messages from client
            data = await websocket.receive_json()

            # Handle ping/pong for keep-alive
            if data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})

            # Handle other message types if needed
            # For now, we're primarily server -> client (broadcasting)

    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)
        logger.info(f"WebSocket disconnected for user {user_id}")

    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
        connection_manager.disconnect(websocket)


@app.get("/health")
async def health_check():
    """
    Health check endpoint for Kubernetes probes.

    Returns:
        Health status and connection statistics
    """
    return {
        "status": "healthy",
        "service": "websocket-sync-service",
        "dapr_pubsub": PUBSUB_NAME,
        "dapr_topic": TOPIC_NAME,
        "active_users": len(connection_manager.get_active_users()),
        "total_connections": connection_manager.get_total_connections()
    }


@app.get("/stats")
async def get_stats():
    """
    Get WebSocket connection statistics.

    Returns:
        Connection statistics
    """
    return {
        "active_users": list(connection_manager.get_active_users()),
        "total_connections": connection_manager.get_total_connections(),
        "connections_by_user": {
            user_id: connection_manager.get_connection_count(user_id)
            for user_id in connection_manager.get_active_users()
        }
    }


@app.get("/")
async def root():
    """
    Root endpoint.

    Returns:
        Service information
    """
    return {
        "service": "WebSocket Sync Service",
        "version": "1.0.0",
        "description": "Real-time task synchronization via WebSocket",
        "endpoints": {
            "websocket": "/ws?token=JWT_TOKEN",
            "dapr_subscription": "/dapr/subscribe",
            "event_handler": "/events/task-updates",
            "stats": "/stats",
            "health": "/health"
        },
        "usage": "Connect to /ws with JWT token to receive real-time task updates"
    }
