"""FastAPI backend application entry point.

This module:
- Initializes the FastAPI application
- Configures CORS middleware
- Registers API routes
- Creates database tables on startup
- Provides OpenAPI/Swagger documentation
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

from db import create_db_and_tables
from routes import tasks, health, chat, reminders, search

# Load environment variables
load_dotenv()

# CORS configuration
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

# Create FastAPI application
app = FastAPI(
    title="Todo API",
    description="RESTful API for Todo Full-Stack Web Application (Phase II)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    """Initialize database tables on application startup."""
    create_db_and_tables()
    print("[OK] Database tables created successfully")
    print(f"[OK] CORS origins configured: {CORS_ORIGINS}")


# Register routers
app.include_router(health.router)
app.include_router(tasks.router)
app.include_router(search.router)  # Phase V: Advanced search and filtering
app.include_router(chat.router)
app.include_router(reminders.router)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint providing API information.

    Returns:
        dict: Welcome message and documentation links
    """
    return {
        "message": "Welcome to Todo API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
