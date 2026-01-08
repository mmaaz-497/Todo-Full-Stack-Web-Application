#!/bin/bash
set -e

echo "Creating remaining microservices..."

# Create recurring-task-service files
cat > backend/recurring-task-service/requirements.txt <<'EOF'
fastapi==0.115.0
uvicorn==0.31.1
sqlmodel==0.0.22
psycopg[binary]==3.2.3
aiokafka==0.11.0
python-dateutil==2.9.0
pydantic-settings==2.5.2
python-dotenv==1.0.1
EOF

cat > backend/recurring-task-service/Dockerfile <<'EOF'
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser
EXPOSE 8001
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
EOF

cat > backend/recurring-task-service/config.py <<'EOF'
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    KAFKA_BOOTSTRAP_SERVERS: str = "kafka-cluster-kafka-bootstrap.kafka.svc.cluster.local:9092"
    KAFKA_TOPIC: str = "task-events"
    KAFKA_GROUP_ID: str = "recurring-task-service-group"
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
EOF

cat > backend/recurring-task-service/main.py <<'EOF'
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
EOF

# Create notification-service files
cat > backend/notification-service/requirements.txt <<'EOF'
fastapi==0.115.0
uvicorn==0.31.1
sqlmodel==0.0.22
psycopg[binary]==3.2.3
aiokafka==0.11.0
aiosmtplib==3.0.0
jinja2==3.1.0
pydantic-settings==2.5.2
python-dotenv==1.0.1
EOF

cat > backend/notification-service/Dockerfile <<'EOF'
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser
EXPOSE 8002
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
EOF

cat > backend/notification-service/config.py <<'EOF'
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    KAFKA_BOOTSTRAP_SERVERS: str = "kafka-cluster-kafka-bootstrap.kafka.svc.cluster.local:9092"
    KAFKA_TOPIC: str = "reminders"
    KAFKA_GROUP_ID: str = "notification-service-group"
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "noreply@todo.local"
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
EOF

cat > backend/notification-service/main.py <<'EOF'
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
EOF

# Create websocket-sync-service files
cat > backend/websocket-sync-service/requirements.txt <<'EOF'
fastapi==0.115.0
uvicorn==0.31.1
websockets==12.0
aiokafka==0.11.0
pydantic-settings==2.5.2
python-dotenv==1.0.1
EOF

cat > backend/websocket-sync-service/Dockerfile <<'EOF'
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser
EXPOSE 8004
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8004"]
EOF

cat > backend/websocket-sync-service/config.py <<'EOF'
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    KAFKA_BOOTSTRAP_SERVERS: str = "kafka-cluster-kafka-bootstrap.kafka.svc.cluster.local:9092"
    KAFKA_TOPIC: str = "task-updates"
    KAFKA_GROUP_ID: str = "websocket-sync-service-group"
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
EOF

cat > backend/websocket-sync-service/main.py <<'EOF'
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
EOF

echo "All services created successfully!"
