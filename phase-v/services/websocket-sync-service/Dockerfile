# WebSocket Sync Service Dockerfile
# Consumes task-updates events and broadcasts to WebSocket clients for real-time sync

FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Expose port for WebSocket server and Dapr subscription endpoint
# Dapr sidecar will be injected separately and listen on 3500
EXPOSE 8000

# Run FastAPI application with WebSocket support
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
