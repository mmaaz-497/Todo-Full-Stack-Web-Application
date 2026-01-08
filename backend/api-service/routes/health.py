"""Health check endpoint for backend API.

This module provides a simple health check endpoint to verify:
- Server is running
- Database connection is working
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from db import get_session

router = APIRouter()


@router.get("/health", tags=["Health"])
async def health_check(session: Session = Depends(get_session)):
    """Health check endpoint.

    Returns:
        dict: Health status and message

    Raises:
        HTTPException: If database connection fails
    """
    try:
        # Test database connection with a simple query
        session.exec(select(1)).one()

        return {
            "status": "healthy",
            "message": "Backend API is running and database is connected",
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}",
        )
