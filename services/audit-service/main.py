"""Audit Service (Phase V)

This service consumes task events and stores them in the audit logs table.
"""

import asyncio
from aiokafka import AIOKafkaConsumer
import json
from typing import Dict, Any
import os
from fastapi import FastAPI, Request
from sqlmodel import create_engine, Session, select
# We'll define a simplified AuditLog model for this service to avoid circular imports
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy.dialects.postgresql import JSONB


class AuditLog(SQLModel, table=True):
    """Simplified Audit log entity for the audit service."""

    __tablename__ = "audit_logs"

    log_id: Optional[int] = Field(default=None, primary_key=True)
    event_id: str  # UUID of the event
    user_id: Optional[str] = Field(default=None)  # User who triggered the event
    action_type: str  # Type of action (created, updated, deleted, etc.)
    resource_type: str  # Type of resource (task, user, etc.)
    resource_id: Optional[int] = Field(default=None)  # ID of the resource
    payload: dict = Field(sa_column=Field(type_=JSONB))  # Additional data about the event
    timestamp: datetime  # When the event occurred
    source_service: str  # Which service generated the event
from datetime import datetime


app = FastAPI(title="Audit Service")


class AuditService:
    """Service to handle audit logging."""

    def __init__(self):
        self.kafka_bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        self.database_url = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/dbname")
        self.engine = create_engine(self.database_url)
        self.consumer = None

    async def start_consumer(self):
        """Start the Kafka consumer."""
        self.consumer = AIOKafkaConsumer(
            'task-events',  # Also listen to other audit-worthy events
            bootstrap_servers=self.kafka_bootstrap_servers.split(","),
            group_id='audit-service',
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            enable_auto_commit=True,
            auto_offset_reset='earliest'
        )

        await self.consumer.start()
        print("Audit Service consumer started")

        try:
            async for message in self.consumer:
                await self.store_audit_log(message.value)
        except Exception as e:
            print(f"Error in consumer loop: {e}")
        finally:
            await self.consumer.stop()

    async def store_audit_log(self, event: Dict[str, Any]):
        """Store event in audit_logs table."""
        print(f"Auditing event: {event.get('event_type')} for task {event.get('task_id')}")

        try:
            # Create audit log entry
            audit_log = AuditLog(
                event_id=event.get('event_id'),
                user_id=event.get('user_id'),
                action_type=event.get('event_type', 'unknown'),
                resource_type='task',
                resource_id=event.get('task_id'),
                payload=event.get('task_data', {}),
                timestamp=datetime.utcnow(),
                source_service='audit-service'
            )

            # Store in database
            with Session(self.engine) as session:
                session.add(audit_log)
                session.commit()

            print(f"Audit log stored for event {event.get('event_id')}")
        except Exception as e:
            print(f"Error storing audit log: {e}")


# Global service instance
audit_service = AuditService()


@app.on_event("startup")
async def startup_event():
    """Start the audit service."""
    print("Audit Service started")


@app.post("/dapr/subscribe")
async def dapr_subscribe():
    """Dapr subscription endpoint - tells Dapr what topics to subscribe to."""
    return [
        {
            "pubsubname": "kafka-pubsub",  # This should match your Dapr component name
            "topic": "task-events",
            "route": "/events/task"
        },
        {
            "pubsubname": "kafka-pubsub",
            "topic": "audit-logs",
            "route": "/events/audit"
        }
    ]


@app.post("/events/task")
async def handle_task_event(request: Request):
    """Handle task events from Dapr."""
    event = await request.json()
    event_data = event.get('data', {})

    print(f"Received task event via Dapr for audit: {event_data}")

    # Store in audit log
    try:
        # Create audit log entry
        audit_log_data = {
            "event_id": event_data.get('event_id'),
            "user_id": event_data.get('user_id'),
            "action_type": event_data.get('event_type', 'unknown'),
            "resource_type": 'task',
            "resource_id": event_data.get('task_id'),
            "payload": event_data.get('task_data', {}),
            "timestamp": datetime.utcnow().isoformat(),
            "source_service": 'dapr-audit-handler'
        }

        # In a real implementation, you'd store this in the database
        # For now, just print it
        print(f"Audit log would be stored: {audit_log_data}")

        return {"status": "SUCCESS"}
    except Exception as e:
        print(f"Error processing audit event: {e}")
        return {"status": "ERROR"}


@app.post("/events/audit")
async def handle_audit_event(request: Request):
    """Handle direct audit log events from Dapr."""
    event = await request.json()
    audit_data = event.get('data', {})

    print(f"Received direct audit event via Dapr: {audit_data}")

    # Store the audit log directly
    try:
        # In a real implementation, you'd store this in the database
        print(f"Direct audit log would be stored: {audit_data}")
        return {"status": "SUCCESS"}
    except Exception as e:
        print(f"Error processing direct audit event: {e}")
        return {"status": "ERROR"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "audit-service"}


# For direct Kafka consumption (non-Dapr)
async def run_consumer():
    """Run the Kafka consumer directly."""
    await audit_service.start_consumer()


if __name__ == "__main__":
    # This would be used if running the service standalone with Kafka
    # For Dapr integration, the service runs as an HTTP server
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)