"""
Recurring Task Service - Main Application

FastAPI application with Dapr Pub/Sub subscription for task.completed events.
Generates next occurrences for recurring tasks.
"""

from fastapi import FastAPI, Request, Response, status
from pydantic import BaseModel
from typing import List, Dict
import logging
import os

from .consumer import handle_task_event

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Dapr configuration
PUBSUB_NAME = os.getenv("DAPR_PUBSUB", "kafka-pubsub")
TOPIC_NAME = os.getenv("DAPR_TOPIC", "task-events")

# Create FastAPI app
app = FastAPI(
    title="Recurring Task Service",
    description="Event-driven microservice for generating recurring task occurrences",
    version="1.0.0"
)


# Dapr subscription configuration
class DaprSubscription(BaseModel):
    """Dapr subscription configuration model."""
    pubsubname: str
    topic: str
    route: str


@app.get("/dapr/subscribe", response_model=List[DaprSubscription])
async def subscribe():
    """
    Dapr subscription endpoint.

    Dapr calls this endpoint to discover which topics this service subscribes to.
    Returns list of subscriptions that Dapr will automatically handle.

    Returns:
        List of subscription configurations
    """
    subscriptions = [
        {
            "pubsubname": PUBSUB_NAME,
            "topic": TOPIC_NAME,
            "route": "/events/task"
        }
    ]
    logger.info(f"Dapr subscription configured: {subscriptions}")
    return subscriptions


@app.post("/events/task")
async def task_event_handler(request: Request):
    """
    Handle task events from Kafka via Dapr.

    This endpoint receives events published to the 'task-events' topic.
    Dapr automatically calls this endpoint when new events arrive.

    Dapr CloudEvent format:
    {
        "id": "event-id",
        "source": "api-service",
        "type": "com.dapr.event.sent",
        "specversion": "1.0",
        "datacontenttype": "application/json",
        "data": {
            "event_id": "uuid",
            "event_type": "task.completed",
            "task_id": 123,
            "user_id": 456,
            "task_data": {...}
        }
    }

    Returns:
        Response with status:
        - 200: Event processed successfully
        - 200 with retry: Event failed, Dapr should retry
        - 200 with drop: Event intentionally dropped
    """
    try:
        # Parse CloudEvent from Dapr
        cloud_event = await request.json()
        logger.debug(f"Received CloudEvent: {cloud_event}")

        # Extract event data (nested in CloudEvent.data)
        event_data = cloud_event.get("data", {})

        if not event_data:
            logger.warning("Received empty event data")
            return {"status": "DROP"}

        # Process event
        result = await handle_task_event(event_data)

        # Return result to Dapr
        # Dapr interprets the response:
        # - "SUCCESS": Event processed, move to next
        # - "RETRY": Event failed, retry with backoff
        # - "DROP": Event intentionally dropped, don't retry
        logger.info(f"Event processing result: {result}")
        return result

    except Exception as e:
        logger.error(f"Error processing event: {e}")
        return {"status": "RETRY"}


@app.get("/health")
async def health_check():
    """
    Health check endpoint for Kubernetes probes.

    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "service": "recurring-task-service",
        "dapr_pubsub": PUBSUB_NAME,
        "dapr_topic": TOPIC_NAME
    }


@app.get("/")
async def root():
    """
    Root endpoint.

    Returns:
        Service information
    """
    return {
        "service": "Recurring Task Service",
        "version": "1.0.0",
        "description": "Generates next occurrences for recurring tasks",
        "endpoints": {
            "dapr_subscription": "/dapr/subscribe",
            "event_handler": "/events/task",
            "health": "/health"
        }
    }
