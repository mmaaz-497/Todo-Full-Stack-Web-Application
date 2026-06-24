"""Kafka Producer Service for Event Publishing (Phase V)

This module implements the Kafka producer for publishing task events
to the event-driven architecture using aiokafka.
"""

import asyncio
from aiokafka import AIOKafkaProducer
import json
from datetime import datetime
from typing import Dict, Any, Optional
from uuid import uuid4
import os


class TaskEventProducer:
    """Async Kafka producer for publishing task events."""

    def __init__(self, bootstrap_servers: Optional[str] = None):
        """Initialize the Kafka producer."""
        self.bootstrap_servers = bootstrap_servers or os.getenv(
            "KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"
        )
        self.producer: Optional[AIOKafkaProducer] = None
        self.is_started = False

    async def start(self):
        """Start the Kafka producer."""
        if self.is_started:
            return

        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers.split(","),
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            compression_type='gzip',
            acks='all',
            enable_idempotence=True  # Ensures exactly-once semantics
        )

        await self.producer.start()
        self.is_started = True
        print(f"Kafka producer started with bootstrap servers: {self.bootstrap_servers}")

    async def stop(self):
        """Stop the Kafka producer."""
        if self.producer and self.is_started:
            await self.producer.stop()
            self.is_started = False
            print("Kafka producer stopped")

    async def publish_task_event(
        self,
        event_type: str,
        task_data: Dict[str, Any],
        user_id: str,
        source: str = "backend-api"
    ):
        """Publish a task event to Kafka."""
        if not self.is_started:
            raise RuntimeError("Kafka producer not started. Call start() first.")

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

        try:
            await self.producer.send_and_wait(
                topic="task-events",
                value=event,
                key=str(task_data.get("id", "")).encode('utf-8')
            )
            print(f"Published {event_type} event for task {task_data.get('id')}")
        except Exception as e:
            print(f"Error publishing task event: {e}")
            raise

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
        """Publish a reminder event to Kafka."""
        if not self.is_started:
            raise RuntimeError("Kafka producer not started. Call start() first.")

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

        try:
            await self.producer.send_and_wait(
                topic="reminders",
                value=event,
                key=str(task_id).encode('utf-8')
            )
            print(f"Published reminder event for task {task_id}")
        except Exception as e:
            print(f"Error publishing reminder event: {e}")
            raise

    async def publish_task_update(
        self,
        task_id: int,
        change_type: str,
        updated_fields: list,
        task_snapshot: Dict[str, Any],
        user_id: str
    ):
        """Publish a task update event to Kafka for real-time sync."""
        if not self.is_started:
            raise RuntimeError("Kafka producer not started. Call start() first.")

        event = {
            "update_id": str(uuid4()),
            "task_id": task_id,
            "change_type": change_type,
            "updated_fields": updated_fields,
            "task_snapshot": task_snapshot,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        }

        try:
            await self.producer.send_and_wait(
                topic="task-updates",
                value=event,
                key=str(task_id).encode('utf-8')
            )
            print(f"Published task update event for task {task_id}")
        except Exception as e:
            print(f"Error publishing task update event: {e}")
            raise

    async def publish_audit_log(
        self,
        event_type: str,
        resource_type: str,
        resource_id: int,
        user_id: str,
        payload: Dict[str, Any]
    ):
        """Publish an audit log event to Kafka."""
        if not self.is_started:
            raise RuntimeError("Kafka producer not started. Call start() first.")

        event = {
            "log_id": str(uuid4()),
            "event_type": event_type,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "user_id": user_id,
            "payload": payload,
            "timestamp": datetime.utcnow().isoformat()
        }

        try:
            await self.producer.send_and_wait(
                topic="audit-logs",
                value=event,
                key=f"{resource_type}-{resource_id}".encode('utf-8')
            )
            print(f"Published audit log event for {resource_type} {resource_id}")
        except Exception as e:
            print(f"Error publishing audit log event: {e}")
            raise


# Global instance
kafka_producer = TaskEventProducer()


async def initialize_kafka_producer():
    """Initialize the Kafka producer when the app starts."""
    await kafka_producer.start()


async def shutdown_kafka_producer():
    """Shutdown the Kafka producer when the app stops."""
    await kafka_producer.stop()