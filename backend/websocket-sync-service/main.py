from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from contextlib import asynccontextmanager
import asyncio
import logging
from aiokafka import AIOKafkaConsumer
import json
from typing import Dict, List

from config import settings

logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

kafka_consumer = None
consumer_task = None

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        logger.info(f"WebSocket connected: user_id={user_id}")

    def disconnect(self, user_id: str, websocket: WebSocket):
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info(f"WebSocket disconnected: user_id={user_id}")

    async def broadcast_to_user(self, user_id: str, message: dict):
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id][:]:
                try:
                    await connection.send_json(message)
                except:
                    self.disconnect(user_id, connection)

manager = ConnectionManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    global kafka_consumer, consumer_task
    logger.info("Starting WebSocket Sync Service...")
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

app = FastAPI(title="WebSocket Sync Service", version="1.0.0", lifespan=lifespan)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "websocket-sync-service"}

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(user_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back for heartbeat
            await websocket.send_text(data)
    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)

async def consume_events():
    try:
        async for message in kafka_consumer:
            event_data = message.value
            user_id = event_data.get('user_id')
            if user_id:
                await manager.broadcast_to_user(user_id, event_data)
    except asyncio.CancelledError:
        logger.info("Consumer cancelled")
    except Exception as e:
        logger.error(f"Consumer error: {e}", exc_info=True)
