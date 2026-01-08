"""Timezone utility functions for consistent datetime handling.

This module strips timezone information while preserving local time values.
All datetimes are stored as Pakistan local time (timezone-naive).
"""

from datetime import datetime, timezone, timedelta
from typing import Optional
import pytz


def get_pakistan_now() -> datetime:
    """Get current time in Pakistan timezone as timezone-naive datetime.

    Returns:
        datetime: Current Pakistan time without timezone info
    """
    pakistan_tz = pytz.timezone('Asia/Karachi')
    pakistan_aware = datetime.now(pakistan_tz)
    return pakistan_aware.replace(tzinfo=None)


def to_utc(dt: Optional[datetime]) -> Optional[datetime]:
    """Strip timezone info from datetime, preserving the local time value.

    Does NOT convert to UTC - just removes timezone information.
    The time value is kept as-is (Pakistan local time).

    Args:
        dt: Datetime that may or may not have timezone info

    Returns:
        Datetime without timezone info (naive), preserving local time

    Examples:
        >>> # Timezone-aware datetime (Pakistan time 18:34+05:00)
        >>> local_dt = datetime(2025, 12, 26, 18, 34, tzinfo=timezone(timedelta(hours=5)))
        >>> to_utc(local_dt)
        datetime(2025, 12, 26, 18, 34)  # Timezone stripped, time preserved as 18:34

        >>> # Already naive
        >>> naive_dt = datetime(2025, 12, 26, 18, 34)
        >>> to_utc(naive_dt)
        datetime(2025, 12, 26, 18, 34)  # Unchanged
    """
    if dt is None:
        return None

    # If datetime has timezone info, strip it while preserving local time
    if dt.tzinfo is not None:
        # Remove timezone info WITHOUT converting the time
        return dt.replace(tzinfo=None)

    # If naive, return as-is
    return dt


def from_utc_to_aware(dt: Optional[datetime]) -> Optional[datetime]:
    """Convert naive UTC datetime to timezone-aware UTC datetime.

    Used when returning datetimes from database to API responses.

    Args:
        dt: Naive datetime from database (assumed to be UTC)

    Returns:
        Timezone-aware datetime in UTC, or None if input is None

    Examples:
        >>> # Naive datetime from database
        >>> db_dt = datetime(2025, 12, 26, 10, 0)
        >>> from_utc_to_aware(db_dt)
        datetime(2025, 12, 26, 10, 0, tzinfo=timezone.utc)
    """
    if dt is None:
        return None

    # If already aware, return as-is
    if dt.tzinfo is not None:
        return dt

    # Add UTC timezone info
    return dt.replace(tzinfo=timezone.utc)
