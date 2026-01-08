# Audit Service Dockerfile
# Consumes all events from all topics and stores them for compliance and debugging

FROM python:3.11-slim

WORKDIR /app

# Install PostgreSQL client dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Expose port for Dapr subscription endpoint, query API, and health checks
# Dapr sidecar will be injected separately and listen on 3500
EXPOSE 8000

# Run FastAPI application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
