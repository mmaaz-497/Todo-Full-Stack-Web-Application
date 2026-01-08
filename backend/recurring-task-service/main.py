from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio
import logging
from aiokafka import AIOKafkaConsumer
import json
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from config import settings

logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

kafka_consumer = None
consumer_task = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global kafka_consumer, consumer_task
    logger.info("Starting Recurring Task Service...")
    kafka_consumer = AIOKafkaConsumer(
        settings.KAFKA_TOPIC,
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        group_id=settings.KAFKA_GROUP_ID,
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='earliest',
        enable_auto_commit=True
    )
    await kafka_consumer.start()
    logger.info(f"Kafka consumer started")
    consumer_task = asyncio.create_task(consume_events())
    yield
    logger.info("Shutting down...")
    if consumer_task:
        consumer_task.cancel()
    if kafka_consumer:
        await kafka_consumer.stop()

app = FastAPI(title="Recurring Task Service", version="1.0.0", lifespan=lifespan)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "recurring-task-service"}

async def consume_events():
    try:
        async for message in kafka_consumer:
            event_data = message.value
            if event_data.get('event_type') == 'task.completed':
                await process_recurring_task(event_data)
    except asyncio.CancelledError:
        logger.info("Consumer cancelled")
    except Exception as e:
        logger.error(f"Consumer error: {e}", exc_info=True)

async def process_recurring_task(event_data: dict):
    try:
        recurrence_rule = event_data.get('recurrence_rule')
        if not recurrence_rule:
            return

        logger.info(f"Processing recurring task: {event_data.get('task_id')}")
        # Calculate next occurrence (simplified)
        # In production, implement full recurrence logic here

    except Exception as e:
        logger.error(f"Failed to process recurring task: {e}", exc_info=True)
