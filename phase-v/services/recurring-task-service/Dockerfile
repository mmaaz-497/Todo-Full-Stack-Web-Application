# Recurring Task Service Dockerfile
# Consumes task.completed events and generates next occurrences for recurring tasks

FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Expose port for Dapr subscription endpoint and health checks
# Dapr sidecar will be injected separately and listen on 3500
EXPOSE 8000

# Run FastAPI application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
