"""Timezone conversion utilities.

This module provides helper functions for handling timezone conversions
between UTC (storage) and user local timezones (display).

All datetimes in the database are stored in UTC. These utilities convert
to user timezones only for display purposes (emails, UI).

Usage:
    from utils.timezone import convert_to_user_timezone, format_datetime_for_user

    utc_dt = datetime.utcnow()
    user_tz = "Asia/Karachi"

    # Convert to user timezone
    local_dt = convert_to_user_timezone(utc_dt, user_tz)

    # Format for email display
    formatted = format_datetime_for_user(utc_dt, user_tz)
    # Output: "January 15, 2025 at 2:00 PM PKT"
"""

from datetime import datetime
from typing import Optional
import pytz
from utils.logger import logger


def convert_to_user_timezone(
    dt: datetime,
    user_timezone: Optional[str] = None
) -> datetime:
    """Convert UTC datetime to user's timezone.

    Args:
        dt: UTC datetime to convert
        user_timezone: IANA timezone string (e.g., 'America/New_York')
                      If None, returns original datetime unchanged

    Returns:
        datetime: Datetime in user's timezone, or original if timezone invalid

    Example:
        >>> utc_dt = datetime(2025, 1, 15, 19, 0, 0)  # 7 PM UTC
        >>> local_dt = convert_to_user_timezone(utc_dt, "America/New_York")
        >>> local_dt.hour
        14  # 2 PM EST (UTC-5)
    """
    # If no timezone specified, return UTC datetime unchanged
    if not user_timezone:
        return dt

    try:
        # Ensure datetime is timezone-aware (UTC)
        if dt.tzinfo is None:
            utc_dt = dt.replace(tzinfo=pytz.UTC)
        else:
            utc_dt = dt

        # Convert to user timezone
        user_tz = pytz.timezone(user_timezone)
        local_dt = utc_dt.astimezone(user_tz)

        return local_dt

    except pytz.exceptions.UnknownTimeZoneError:
        logger.warning(
            f"Invalid timezone '{user_timezone}', using UTC",
            extra={"action": "timezone_conversion"}
        )
        return dt
    except Exception as e:
        logger.error(
            f"Failed to convert timezone: {e}. Using UTC.",
            extra={"action": "timezone_conversion"}
        )
        return dt


def format_datetime_for_user(
    dt: datetime,
    user_timezone: Optional[str] = None,
    include_timezone: bool = True
) -> str:
    """Format datetime for display in user's timezone.

    Converts UTC datetime to user's local time and formats it in a
    human-readable format suitable for email display.

    Args:
        dt: UTC datetime to format
        user_timezone: IANA timezone string
        include_timezone: Whether to include timezone abbreviation (e.g., EST)

    Returns:
        str: Formatted datetime string

    Examples:
        >>> utc_dt = datetime(2025, 1, 15, 19, 0, 0)

        # With timezone
        >>> format_datetime_for_user(utc_dt, "America/New_York")
        'January 15, 2025 at 2:00 PM EST'

        # Without timezone
        >>> format_datetime_for_user(utc_dt, "America/New_York", include_timezone=False)
        'January 15, 2025 at 2:00 PM'

        # No user timezone (defaults to UTC)
        >>> format_datetime_for_user(utc_dt)
        'January 15, 2025 at 7:00 PM UTC'
    """
    # Convert to user timezone
    local_dt = convert_to_user_timezone(dt, user_timezone)

    # Format datetime
    # strftime codes:
    #   %B = full month name (January)
    #   %d = day of month (15)
    #   %Y = year (2025)
    #   %I = hour 12-hour format (02)
    #   %M = minute (00)
    #   %p = AM/PM
    formatted = local_dt.strftime("%B %d, %Y at %I:%M %p")

    # Add timezone abbreviation if requested
    if include_timezone:
        # %Z gives timezone abbreviation (EST, PDT, etc.)
        tz_abbr = local_dt.strftime("%Z")
        formatted = f"{formatted} {tz_abbr}"

    return formatted


def get_user_timezone_offset(user_timezone: Optional[str] = None) -> str:
    """Get timezone offset string (e.g., UTC-5, UTC+8).

    Args:
        user_timezone: IANA timezone string

    Returns:
        str: Timezone offset string

    Example:
        >>> get_user_timezone_offset("America/New_York")
        'UTC-5'  # During standard time

        >>> get_user_timezone_offset("Asia/Tokyo")
        'UTC+9'
    """
    if not user_timezone:
        return "UTC"

    try:
        tz = pytz.timezone(user_timezone)
        now = datetime.now(tz)

        # Get offset in hours
        offset_seconds = now.utcoffset().total_seconds()
        offset_hours = int(offset_seconds / 3600)

        # Format offset string
        if offset_hours >= 0:
            return f"UTC+{offset_hours}"
        else:
            return f"UTC{offset_hours}"  # Already has minus sign

    except Exception:
        return "UTC"
