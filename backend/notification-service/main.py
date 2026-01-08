from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio
import logging
from aiokafka import AIOKafkaConsumer
import json

from config import settings

logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

kafka_consumer = None
consumer_task = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global kafka_consumer, consumer_task
    logger.info("Starting Notification Service...")
    kafka_consumer = AIOKafkaConsumer(
        settings.KAFKA_TOPIC,
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        group_id=settings.KAFKA_GROUP_ID,
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='earliest',
        enable_auto_commit=True
    )
    await kafka_consumer.start()
    logger.info("Kafka consumer started")
    consumer_task = asyncio.create_task(consume_events())
    yield
    logger.info("Shutting down...")
    if consumer_task:
        consumer_task.cancel()
    if kafka_consumer:
        await kafka_consumer.stop()

app = FastAPI(title="Notification Service", version="1.0.0", lifespan=lifespan)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "notification-service"}

async def consume_events():
    try:
        async for message in kafka_consumer:
            event_data = message.value
            await send_notification(event_data)
    except asyncio.CancelledError:
        logger.info("Consumer cancelled")
    except Exception as e:
        logger.error(f"Consumer error: {e}", exc_info=True)

async def send_notification(event_data: dict):
    try:
        logger.info(f"Sending notification for task: {event_data.get('task_id')}")
        # In production, implement actual email sending here
    except Exception as e:
        logger.error(f"Failed to send notification: {e}", exc_info=True)
