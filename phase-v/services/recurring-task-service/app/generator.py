"""
Recurrence calculation logic for recurring tasks.

Supports:
- Daily recurrence (every N days)
- Weekly recurrence (specific days of week)
- Monthly recurrence (specific day of month)
"""

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


def calculate_next_occurrence(
    completed_at: datetime,
    recurrence_rule: Dict,
    original_due_date: Optional[datetime] = None
) -> Optional[datetime]:
    """
    Calculate next occurrence date based on recurrence rule.

    Args:
        completed_at: When the current occurrence was completed
        recurrence_rule: Recurrence rule dictionary
            {
                "frequency": "daily|weekly|monthly",
                "interval": int,  # e.g., 2 for every 2 days
                "days_of_week": [0-6],  # for weekly (0=Monday, 6=Sunday)
                "day_of_month": 1-31  # for monthly
            }
        original_due_date: Original due date (for time-of-day preservation)

    Returns:
        datetime: Next occurrence due date, or None if invalid rule

    Examples:
        # Daily: Every 2 days
        {"frequency": "daily", "interval": 2}
        → 2 days after completion

        # Weekly: Every Monday and Wednesday
        {"frequency": "weekly", "interval": 1, "days_of_week": [0, 2]}
        → Next Monday or Wednesday after completion

        # Monthly: 15th of every month
        {"frequency": "monthly", "interval": 1, "day_of_month": 15}
        → 15th of next month
    """
    try:
        frequency = recurrence_rule.get("frequency", "").lower()
        interval = recurrence_rule.get("interval", 1)

        if frequency == "daily":
            return _calculate_daily(completed_at, interval, original_due_date)
        elif frequency == "weekly":
            days_of_week = recurrence_rule.get("days_of_week", [])
            return _calculate_weekly(completed_at, interval, days_of_week, original_due_date)
        elif frequency == "monthly":
            day_of_month = recurrence_rule.get("day_of_month")
            return _calculate_monthly(completed_at, interval, day_of_month, original_due_date)
        else:
            logger.warning(f"Unknown recurrence frequency: {frequency}")
            return None

    except Exception as e:
        logger.error(f"Error calculating next occurrence: {e}")
        return None


def _calculate_daily(
    completed_at: datetime,
    interval: int,
    original_due_date: Optional[datetime]
) -> datetime:
    """
    Calculate next occurrence for daily recurrence.

    Args:
        completed_at: When task was completed
        interval: Days between occurrences
        original_due_date: Original due date for time preservation

    Returns:
        Next occurrence datetime
    """
    next_date = completed_at + timedelta(days=interval)

    # Preserve original time-of-day if available
    if original_due_date:
        next_date = next_date.replace(
            hour=original_due_date.hour,
            minute=original_due_date.minute,
            second=original_due_date.second
        )

    logger.info(f"Daily recurrence: {completed_at} + {interval} days = {next_date}")
    return next_date


def _calculate_weekly(
    completed_at: datetime,
    interval: int,
    days_of_week: list,
    original_due_date: Optional[datetime]
) -> Optional[datetime]:
    """
    Calculate next occurrence for weekly recurrence.

    Args:
        completed_at: When task was completed
        interval: Weeks between occurrences
        days_of_week: List of weekday numbers (0=Monday, 6=Sunday)
        original_due_date: Original due date for time preservation

    Returns:
        Next occurrence datetime, or None if invalid
    """
    if not days_of_week:
        logger.warning("Weekly recurrence requires days_of_week")
        return None

    # Sort days for easier processing
    sorted_days = sorted(days_of_week)

    # Find next matching weekday
    current_weekday = completed_at.weekday()
    next_date = None

    # Check days in current week
    for day in sorted_days:
        if day > current_weekday:
            days_ahead = day - current_weekday
            next_date = completed_at + timedelta(days=days_ahead)
            break

    # If no match in current week, go to first day of next week interval
    if not next_date:
        days_ahead = (7 - current_weekday) + sorted_days[0]
        # Add extra weeks if interval > 1
        if interval > 1:
            days_ahead += (interval - 1) * 7
        next_date = completed_at + timedelta(days=days_ahead)

    # Preserve original time-of-day
    if original_due_date:
        next_date = next_date.replace(
            hour=original_due_date.hour,
            minute=original_due_date.minute,
            second=original_due_date.second
        )

    logger.info(
        f"Weekly recurrence: next occurrence on weekday {next_date.weekday()} "
        f"at {next_date}"
    )
    return next_date


def _calculate_monthly(
    completed_at: datetime,
    interval: int,
    day_of_month: Optional[int],
    original_due_date: Optional[datetime]
) -> Optional[datetime]:
    """
    Calculate next occurrence for monthly recurrence.

    Args:
        completed_at: When task was completed
        interval: Months between occurrences
        day_of_month: Day of month (1-31)
        original_due_date: Original due date for time preservation

    Returns:
        Next occurrence datetime, or None if invalid
    """
    if not day_of_month:
        logger.warning("Monthly recurrence requires day_of_month")
        return None

    if day_of_month < 1 or day_of_month > 31:
        logger.warning(f"Invalid day_of_month: {day_of_month}")
        return None

    # Calculate next month
    next_date = completed_at + relativedelta(months=interval)

    # Set to specified day of month
    try:
        next_date = next_date.replace(day=day_of_month)
    except ValueError:
        # Day doesn't exist in that month (e.g., Feb 30)
        # Use last day of month instead
        last_day = (next_date.replace(day=1) + relativedelta(months=1) - timedelta(days=1)).day
        next_date = next_date.replace(day=min(day_of_month, last_day))
        logger.warning(
            f"Day {day_of_month} doesn't exist in {next_date.strftime('%B %Y')}, "
            f"using day {next_date.day}"
        )

    # Preserve original time-of-day
    if original_due_date:
        next_date = next_date.replace(
            hour=original_due_date.hour,
            minute=original_due_date.minute,
            second=original_due_date.second
        )

    logger.info(
        f"Monthly recurrence: day {day_of_month} of month {next_date.month} "
        f"= {next_date}"
    )
    return next_date
