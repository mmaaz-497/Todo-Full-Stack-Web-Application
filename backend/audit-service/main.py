from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio
import logging
from aiokafka import AIOKafkaConsumer
import json
from datetime import datetime

from config import settings
from database import engine, init_db, get_session
from models import AuditLog

# Configure logging
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

kafka_consumer = None
consumer_task = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    global kafka_consumer, consumer_task

    # Startup
    logger.info("Starting Audit Service...")
    init_db()

    # Start Kafka consumer
    kafka_consumer = AIOKafkaConsumer(
        settings.KAFKA_TOPIC,
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        group_id=settings.KAFKA_GROUP_ID,
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='earliest',
        enable_auto_commit=True
    )
    await kafka_consumer.start()
    logger.info(f"Kafka consumer started: topic={settings.KAFKA_TOPIC}")

    # Start consumer in background
    consumer_task = asyncio.create_task(consume_events())

    yield

    # Shutdown
    logger.info("Shutting down Audit Service...")
    if consumer_task:
        consumer_task.cancel()
    if kafka_consumer:
        await kafka_consumer.stop()

app = FastAPI(
    title="Audit Service",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "audit-service",
        "kafka_topic": settings.KAFKA_TOPIC
    }

async def consume_events():
    """Consume Kafka events and log to database"""
    try:
        async for message in kafka_consumer:
            event_data = message.value
            await process_event(event_data)
    except asyncio.CancelledError:
        logger.info("Consumer task cancelled")
    except Exception as e:
        logger.error(f"Consumer error: {e}", exc_info=True)

async def process_event(event_data: dict):
    """Process and log event to database"""
    try:
        # Extract event details
        event_id = event_data.get('event_id', f"{event_data.get('task_id')}_{datetime.utcnow().timestamp()}")
        event_type = event_data.get('event_type', 'unknown')
        task_id = event_data.get('task_id')
        user_id = event_data.get('user_id')

        # Create audit log
        audit_log = AuditLog(
            event_id=event_id,
            event_type=event_type,
            task_id=task_id,
            user_id=user_id,
            event_payload=event_data,
            timestamp=datetime.utcnow()
        )

        # Save to database
        session_gen = get_session()
        session = next(session_gen)
        try:
            session.add(audit_log)
            session.commit()
            logger.info(f"Logged event: {event_id} - {event_type}")
        finally:
            session.close()

    except Exception as e:
        logger.error(f"Failed to process event: {e}", exc_info=True)
