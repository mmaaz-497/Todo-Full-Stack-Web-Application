"""Recurring Task Service (Phase V)

This service consumes task completion events and creates next occurrences
for recurring tasks.
"""

import asyncio
from aiokafka import AIOKafkaConsumer
import json
from datetime import datetime, timedelta
from typing import Dict, Any
import os
from fastapi import FastAPI, Request
import httpx


app = FastAPI(title="Recurring Task Service")


class RecurringTaskService:
    """Service to handle recurring task logic."""

    def __init__(self):
        self.kafka_bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        self.backend_service_url = os.getenv("BACKEND_SERVICE_URL", "http://backend-service:8000")
        self.consumer = None

    async def start_consumer(self):
        """Start the Kafka consumer."""
        self.consumer = AIOKafkaConsumer(
            'task-events',
            bootstrap_servers=self.kafka_bootstrap_servers.split(","),
            group_id='recurring-task-service',
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            enable_auto_commit=True,
            auto_offset_reset='earliest'
        )

        await self.consumer.start()
        print("Recurring Task Service consumer started")

        try:
            async for message in self.consumer:
                await self.handle_event(message.value)
        except Exception as e:
            print(f"Error in consumer loop: {e}")
        finally:
            await self.consumer.stop()

    async def handle_event(self, event: Dict[str, Any]):
        """Process task events for recurring tasks."""
        print(f"Received event: {event.get('event_type')} for task {event.get('task_id')}")

        if event.get('event_type') != 'completed':
            return

        task_data = event.get('task_data', {})

        # Check if this is a recurring task
        is_recurring = task_data.get('is_recurring', False)
        recurrence_pattern = task_data.get('recurrence_pattern')

        if not is_recurring or not recurrence_pattern:
            return

        print(f"Processing recurring task completion: {task_data.get('title')}")

        # Calculate next occurrence
        current_due = task_data.get('due_date')
        if current_due:
            try:
                current_due_dt = datetime.fromisoformat(current_due.replace('Z', '+00:00'))
                next_due = self.calculate_next_occurrence(current_due_dt, recurrence_pattern)

                if next_due:
                    # Create next task via API call to backend
                    await self.create_next_task(task_data, next_due)

            except Exception as e:
                print(f"Error calculating next occurrence: {e}")

    def calculate_next_occurrence(self, current_due: datetime, pattern: str) -> datetime:
        """Calculate next due date based on recurrence pattern."""
        if pattern == 'daily':
            return current_due + timedelta(days=1)
        elif pattern == 'weekly':
            return current_due + timedelta(weeks=1)
        elif pattern == 'monthly':
            # Simple monthly calculation - add ~30 days
            # In production, you'd want to handle months properly (28/29/30/31 days)
            return current_due + timedelta(days=30)
        elif pattern == 'yearly':
            return current_due + timedelta(days=365)
        else:
            # For more complex patterns, you might have a recurrence_rule field with detailed configuration
            recurrence_rule = current_due.get('recurrence_rule') if isinstance(current_due, dict) else None
            if recurrence_rule:
                # Handle complex recurrence rules defined in the recurrence_rule field
                # This would require more complex logic based on the rule definition
                print(f"Complex recurrence rule not yet implemented: {recurrence_rule}")
            return None

    async def create_next_task(self, parent_task: Dict[str, Any], next_due: datetime):
        """Create the next occurrence of a recurring task via API call."""
        task_payload = {
            "title": parent_task.get('title'),
            "description": parent_task.get('description', ''),
            "priority": parent_task.get('priority', 'medium'),
            "tags": parent_task.get('tags', []),
            "due_date": next_due.isoformat(),
            "is_recurring": parent_task.get('is_recurring', False),
            "recurrence_pattern": parent_task.get('recurrence_pattern'),
            "parent_task_id": parent_task.get('id'),  # Link to parent task
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.backend_service_url}/api/tasks/",
                    json=task_payload,
                    headers={"Content-Type": "application/json"},
                    timeout=30.0
                )

                if response.status_code in [200, 201]:
                    print(f"Successfully created next occurrence for task {parent_task.get('id')}")
                else:
                    print(f"Failed to create next occurrence: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error creating next occurrence via API: {e}")


# Global service instance
recurring_task_service = RecurringTaskService()


@app.on_event("startup")
async def startup_event():
    """Start the recurring task service."""
    # Note: In a real implementation, you'd probably run this in a background task
    # For now, we'll just print a message
    print("Recurring Task Service started")


@app.post("/dapr/subscribe")
async def dapr_subscribe():
    """Dapr subscription endpoint - tells Dapr what topics to subscribe to."""
    return [
        {
            "pubsubname": "kafka-pubsub",  # This should match your Dapr component name
            "topic": "task-events",
            "route": "/events/task"
        }
    ]


@app.post("/events/task")
async def handle_task_event(request: Request):
    """Handle task events from Dapr."""
    event = await request.json()
    print(f"Received task event via Dapr: {event}")

    # Process the event
    if event.get('data', {}).get('event_type') == 'completed':
        task_data = event['data'].get('task_data', {})
        is_recurring = task_data.get('is_recurring', False)
        recurrence_pattern = task_data.get('recurrence_pattern')

        if is_recurring and recurrence_pattern:
            # Calculate and create next occurrence
            current_due_str = task_data.get('due_date')
            if current_due_str:
                try:
                    current_due = datetime.fromisoformat(current_due_str.replace('Z', '+00:00'))
                    next_due = recurring_task_service.calculate_next_occurrence(current_due, recurrence_pattern)

                    if next_due:
                        await recurring_task_service.create_next_task(task_data, next_due)

                except Exception as e:
                    print(f"Error processing recurring task: {e}")

    return {"status": "SUCCESS"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "recurring-task-service"}


# For direct Kafka consumption (non-Dapr)
async def run_consumer():
    """Run the Kafka consumer directly."""
    await recurring_task_service.start_consumer()


if __name__ == "__main__":
    # This would be used if running the service standalone with Kafka
    # For Dapr integration, the service runs as an HTTP server
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)