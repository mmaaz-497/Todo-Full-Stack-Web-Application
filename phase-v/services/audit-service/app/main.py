"""
Audit Service - Main Application

FastAPI application with multiple Dapr Pub/Sub subscriptions for audit logging.
Provides query API for retrieving audit logs.
"""

from fastapi import FastAPI, Request, Depends, Query
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime
import logging
import os

from .consumer import handle_audit_event
from .models import AuditLogEntry, AuditLogResponse, AuditLogQuery
from .database import create_db_and_tables, get_session

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Dapr configuration
PUBSUB_NAME = os.getenv("DAPR_PUBSUB", "kafka-pubsub")

# Create FastAPI app
app = FastAPI(
    title="Audit Service",
    description="Event-driven microservice for audit logging and compliance tracking",
    version="1.0.0"
)


@app.on_event("startup")
def on_startup():
    """Initialize database tables on startup."""
    create_db_and_tables()
    logger.info("Database tables created/verified")


@app.get("/dapr/subscribe")
async def subscribe():
    """
    Dapr subscription endpoint.

    Subscribe to multiple Kafka topics for comprehensive audit logging:
    - task-events: Task CRUD operations
    - reminders: Reminder notifications
    - task-updates: Real-time task updates

    Returns:
        List of subscription configurations
    """
    subscriptions = [
        {
            "pubsubname": PUBSUB_NAME,
            "topic": "task-events",
            "route": "/events/task-events"
        },
        {
            "pubsubname": PUBSUB_NAME,
            "topic": "reminders",
            "route": "/events/reminders"
        },
        {
            "pubsubname": PUBSUB_NAME,
            "topic": "task-updates",
            "route": "/events/task-updates"
        }
    ]
    logger.info(f"Dapr subscriptions configured: {len(subscriptions)} topics")
    return subscriptions


@app.post("/events/task-events")
async def task_events_handler(request: Request):
    """Handle events from task-events topic."""
    try:
        cloud_event = await request.json()
        event_data = cloud_event.get("data", {})

        if not event_data:
            return {"status": "DROP"}

        result = await handle_audit_event(event_data, topic="task-events")
        return result

    except Exception as e:
        logger.error(f"Error processing task-events: {e}")
        return {"status": "RETRY"}


@app.post("/events/reminders")
async def reminders_handler(request: Request):
    """Handle events from reminders topic."""
    try:
        cloud_event = await request.json()
        event_data = cloud_event.get("data", {})

        if not event_data:
            return {"status": "DROP"}

        result = await handle_audit_event(event_data, topic="reminders")
        return result

    except Exception as e:
        logger.error(f"Error processing reminders: {e}")
        return {"status": "RETRY"}


@app.post("/events/task-updates")
async def task_updates_handler(request: Request):
    """Handle events from task-updates topic."""
    try:
        cloud_event = await request.json()
        event_data = cloud_event.get("data", {})

        if not event_data:
            return {"status": "DROP"}

        result = await handle_audit_event(event_data, topic="task-updates")
        return result

    except Exception as e:
        logger.error(f"Error processing task-updates: {e}")
        return {"status": "RETRY"}


@app.get("/api/audit/logs", response_model=List[AuditLogResponse])
async def query_audit_logs(
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    action_type: Optional[str] = Query(None, description="Filter by action type (e.g., task.created)"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type (e.g., task)"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date (ISO 8601)"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date (ISO 8601)"),
    limit: int = Query(100, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    session: Session = Depends(get_session)
):
    """
    Query audit logs with filters.

    Supports filtering by:
    - user_id: User who performed the action
    - action_type: Type of action (task.created, task.updated, etc.)
    - resource_type: Type of resource (task, reminder)
    - start_date/end_date: Date range
    - limit/offset: Pagination

    Returns:
        List of audit log entries
    """
    try:
        # Build query
        query = select(AuditLogEntry)

        # Apply filters
        if user_id is not None:
            query = query.where(AuditLogEntry.user_id == user_id)

        if action_type:
            query = query.where(AuditLogEntry.action_type == action_type)

        if resource_type:
            query = query.where(AuditLogEntry.resource_type == resource_type)

        if start_date:
            query = query.where(AuditLogEntry.timestamp >= start_date)

        if end_date:
            query = query.where(AuditLogEntry.timestamp <= end_date)

        # Order by timestamp descending (newest first)
        query = query.order_by(AuditLogEntry.timestamp.desc())

        # Apply pagination
        query = query.offset(offset).limit(limit)

        # Execute query
        results = session.exec(query).all()

        logger.info(
            f"Audit log query: user_id={user_id}, action_type={action_type}, "
            f"resource_type={resource_type}, results={len(results)}"
        )

        return results

    except Exception as e:
        logger.error(f"Error querying audit logs: {e}")
        return []


@app.get("/api/audit/stats")
async def get_audit_stats(session: Session = Depends(get_session)):
    """
    Get audit log statistics.

    Returns:
        Summary statistics about audit logs
    """
    try:
        # Total log count
        total_count = session.query(AuditLogEntry).count()

        # Count by action type
        from sqlalchemy import func
        action_counts = session.query(
            AuditLogEntry.action_type,
            func.count(AuditLogEntry.log_id).label('count')
        ).group_by(AuditLogEntry.action_type).all()

        # Count by resource type
        resource_counts = session.query(
            AuditLogEntry.resource_type,
            func.count(AuditLogEntry.log_id).label('count')
        ).group_by(AuditLogEntry.resource_type).all()

        return {
            "total_logs": total_count,
            "action_type_distribution": {row[0]: row[1] for row in action_counts},
            "resource_type_distribution": {row[0]: row[1] for row in resource_counts}
        }

    except Exception as e:
        logger.error(f"Error getting audit stats: {e}")
        return {"error": str(e)}


@app.get("/health")
async def health_check():
    """Health check endpoint for Kubernetes probes."""
    return {
        "status": "healthy",
        "service": "audit-service",
        "dapr_pubsub": PUBSUB_NAME,
        "topics": ["task-events", "reminders", "task-updates"]
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Audit Service",
        "version": "1.0.0",
        "description": "Audit logging and compliance tracking for all system events",
        "endpoints": {
            "dapr_subscription": "/dapr/subscribe",
            "event_handlers": [
                "/events/task-events",
                "/events/reminders",
                "/events/task-updates"
            ],
            "query_api": "/api/audit/logs",
            "stats_api": "/api/audit/stats",
            "health": "/health"
        }
    }
