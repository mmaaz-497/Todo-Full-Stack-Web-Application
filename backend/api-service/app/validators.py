"""
Validation utilities for API inputs.

Implements validation for:
- Recurrence rules (T089-T092)
- Due dates and reminders
- Search queries
"""

from typing import Dict, Any, Optional, List
from fastapi import HTTPException, status
from datetime import datetime


def validate_recurrence_rule(recurrence_rule: Optional[Dict[str, Any]]) -> None:
    """Validate recurrence_rule structure and values.

    Args:
        recurrence_rule: Recurrence rule dictionary

    Raises:
        HTTPException: If validation fails

    Validation Rules (T089-T092):
    - T090: frequency must be "daily", "weekly", or "monthly"
    - T091: days_of_week required for weekly (1-7, Monday=1)
    - T092: day_of_month required for monthly (1-31)
    """
    if not recurrence_rule:
        return

    # T090: Validate frequency values
    frequency = recurrence_rule.get("frequency", "").lower()
    valid_frequencies = ["daily", "weekly", "monthly"]

    if frequency not in valid_frequencies:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid recurrence frequency '{frequency}'. Must be one of: {', '.join(valid_frequencies)}"
        )

    # T091: Validate days_of_week for weekly recurrence
    if frequency == "weekly":
        days_of_week = recurrence_rule.get("days_of_week")
        if not days_of_week or not isinstance(days_of_week, list):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Weekly recurrence requires 'days_of_week' as array of integers (1-7, Monday=1)"
            )

        # Validate each day is 1-7
        for day in days_of_week:
            if not isinstance(day, int) or day < 1 or day > 7:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid day_of_week value '{day}'. Must be integer 1-7 (Monday=1, Sunday=7)"
                )

    # T092: Validate day_of_month for monthly recurrence
    if frequency == "monthly":
        day_of_month = recurrence_rule.get("day_of_month")
        if day_of_month is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Monthly recurrence requires 'day_of_month' (1-31)"
            )

        if not isinstance(day_of_month, int) or day_of_month < 1 or day_of_month > 31:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid day_of_month value '{day_of_month}'. Must be integer 1-31"
            )

    # Validate interval (optional, defaults to 1)
    interval = recurrence_rule.get("interval", 1)
    if not isinstance(interval, int) or interval < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid interval value '{interval}'. Must be positive integer"
        )


def validate_due_date(due_date: Optional[datetime]) -> None:
    """Validate due_date is in the future.

    Args:
        due_date: Due date to validate

    Raises:
        HTTPException: If due date is in the past
    """
    if not due_date:
        return

    # T093: Validate due_date is future timestamp
    if due_date <= datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="due_date must be in the future"
        )


def validate_reminder_offset(due_date: Optional[datetime], reminder_time: Optional[datetime]) -> None:
    """Validate reminder_time is before due_date.

    Args:
        due_date: Task due date
        reminder_time: Reminder trigger time

    Raises:
        HTTPException: If reminder validation fails
    """
    if not reminder_time or not due_date:
        return

    # T094: Validate reminder_time is before due_date
    if reminder_time >= due_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="reminder_time must be before due_date"
        )

    # Validate reminder is not in the past
    if reminder_time <= datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="reminder_time must be in the future"
        )


def validate_search_query(query: Optional[str]) -> str:
    """Validate and sanitize search query.

    Args:
        query: Search query string

    Returns:
        str: Sanitized query

    Raises:
        HTTPException: If query is invalid
    """
    if not query:
        return ""

    # Remove leading/trailing whitespace
    query = query.strip()

    # Minimum length check
    if len(query) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query must be at least 2 characters"
        )

    # Maximum length check (prevent DoS)
    if len(query) > 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query must be less than 200 characters"
        )

    return query


def validate_pagination(offset: int, limit: int) -> None:
    """Validate pagination parameters.

    Args:
        offset: Number of records to skip
        limit: Maximum number of records to return

    Raises:
        HTTPException: If pagination parameters are invalid
    """
    # Validate offset
    if offset < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="offset must be non-negative"
        )

    # Validate limit
    if limit < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="limit must be at least 1"
        )

    if limit > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="limit must be 100 or less"
        )
