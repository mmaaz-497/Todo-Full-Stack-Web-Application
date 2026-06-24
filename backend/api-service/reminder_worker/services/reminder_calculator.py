"""Calculate next reminder datetime for tasks.

This is the core scheduling logic module. It handles four recurrence patterns:
1. One-time (none): Simple datetime comparison
2. Daily: Same time every day
3. Weekly: Same weekday every week
4. Monthly: Same day-of-month every month (with edge case handling)

The calculator is timezone-aware and handles edge cases like:
- Feb 31st → Feb 28/29 (last day of month)
- DST transitions (handled by pytz in timezone utils)
- Tasks past due date (grace period)
"""

from datetime import datetime, date, time, timedelta
from typing import Optional
from dateutil.relativedelta import relativedelta
import pytz

from models import Task

from utils.logger import logger
from config.constants import GRACE_PERIOD_DAYS


class ReminderCalculator:
    """Calculate when to send reminders based on task settings.

    This class implements the scheduling algorithm for all recurrence patterns.
    It's stateless - all calculations based on task data and current time.
    """

    @staticmethod
    def calculate_reminder_datetime(
        task: Task,
        now: Optional[datetime] = None
    ) -> Optional[datetime]:
        """Calculate the next reminder datetime for a task.

        This is the main entry point for reminder scheduling logic.
        Dispatches to specific handlers based on recurrence_pattern.

        Args:
            task: Task to calculate reminder for
            now: Current datetime (defaults to utcnow(), override for testing)

        Returns:
            Optional[datetime]: Next reminder datetime (UTC), or None if:
                - Task has no reminder_time set
                - One-time reminder already passed
                - Unknown recurrence pattern

        Example:
            >>> task = Task(reminder_time=datetime(2025, 1, 15, 14, 0), recurrence_pattern="daily")
            >>> next_reminder = ReminderCalculator.calculate_reminder_datetime(task)
            >>> # Returns today at 2 PM if not yet sent, tomorrow at 2 PM if already sent
        """
        if not task.reminder_time:
            return None

        # Use Pakistan time since database stores Pakistan local time
        if now is None:
            pakistan_tz = pytz.timezone('Asia/Karachi')
            now = datetime.now(pakistan_tz).replace(tzinfo=None)

        # Dispatch to appropriate handler based on recurrence pattern
        if task.recurrence_pattern == "none":
            return ReminderCalculator._calculate_one_time(task, now)
        elif task.recurrence_pattern == "daily":
            return ReminderCalculator._calculate_daily(task, now)
        elif task.recurrence_pattern == "weekly":
            return ReminderCalculator._calculate_weekly(task, now)
        elif task.recurrence_pattern == "monthly":
            return ReminderCalculator._calculate_monthly(task, now)
        else:
            logger.warning(
                f"Unknown recurrence pattern: {task.recurrence_pattern}",
                extra={"task_id": task.id, "pattern": task.recurrence_pattern}
            )
            return None

    @staticmethod
    def _calculate_one_time(task: Task, now: datetime) -> Optional[datetime]:
        """Calculate reminder for one-time (non-recurring) task.

        Logic:
        - If reminder_time is in the future OR recently past (grace period) → return it
        - If reminder_time is too old → return None (already missed)

        Grace period: 5 minutes past due (matches task_reader time window)

        Args:
            task: Task with recurrence_pattern='none'
            now: Current datetime

        Returns:
            Optional[datetime]: reminder_time if within grace period, None if too old

        Example:
            >>> # Reminder at 2 PM today
            >>> task.reminder_time = datetime(2025, 1, 15, 14, 0)

            >>> # Current time: 1 PM (before reminder)
            >>> _calculate_one_time(task, datetime(2025, 1, 15, 13, 0))
            datetime(2025, 1, 15, 14, 0)  # Return reminder time

            >>> # Current time: 2:03 PM (3 min overdue, within grace)
            >>> _calculate_one_time(task, datetime(2025, 1, 15, 14, 3))
            datetime(2025, 1, 15, 14, 0)  # Still return it

            >>> # Current time: 3 PM (60 min overdue, outside grace)
            >>> _calculate_one_time(task, datetime(2025, 1, 15, 15, 0))
            None  # Too old, skipped
        """
        from datetime import timedelta

        # Allow grace period of 5 minutes for overdue reminders
        # This matches the time window in task_reader.py
        grace_period = now - timedelta(minutes=5)

        # Return reminder_time if it's in future or within grace period
        if task.reminder_time >= grace_period:
            return task.reminder_time
        return None

    @staticmethod
    def _calculate_daily(task: Task, now: datetime) -> Optional[datetime]:
        """Calculate reminder for daily recurring task.

        Logic:
        - Extract time component from reminder_time
        - If that time hasn't occurred today → return today at that time
        - If that time already passed today → return tomorrow at that time

        Args:
            task: Task with recurrence_pattern='daily'
            now: Current datetime

        Returns:
            Optional[datetime]: Next occurrence of reminder time

        Example:
            >>> # Reminder at 9 AM every day
            >>> task.reminder_time = datetime(2025, 1, 15, 9, 0)

            >>> # Current time: 8 AM (before 9 AM)
            >>> _calculate_daily(task, datetime(2025, 1, 15, 8, 0))
            datetime(2025, 1, 15, 9, 0)  # Today at 9 AM

            >>> # Current time: 10 AM (after 9 AM)
            >>> _calculate_daily(task, datetime(2025, 1, 15, 10, 0))
            datetime(2025, 1, 16, 9, 0)  # Tomorrow at 9 AM
        """
        # Extract time component (hour, minute, second)
        reminder_time_obj = task.reminder_time.time()

        # Combine with today's date
        today_reminder = datetime.combine(now.date(), reminder_time_obj)

        if today_reminder > now:
            # Reminder hasn't happened yet today
            return today_reminder
        else:
            # Reminder already passed today, schedule for tomorrow
            tomorrow_reminder = today_reminder + timedelta(days=1)
            return tomorrow_reminder

    @staticmethod
    def _calculate_weekly(task: Task, now: datetime) -> Optional[datetime]:
        """Calculate reminder for weekly recurring task.

        Logic:
        - Reminder occurs on the same weekday as the original reminder_time
        - If today is that weekday and time hasn't passed → return today
        - Otherwise → return next occurrence of that weekday

        Args:
            task: Task with recurrence_pattern='weekly'
            now: Current datetime

        Returns:
            Optional[datetime]: Next occurrence of reminder on target weekday

        Example:
            >>> # Reminder on Monday at 9 AM
            >>> task.reminder_time = datetime(2025, 1, 13, 9, 0)  # Monday

            >>> # Today is Wednesday
            >>> _calculate_weekly(task, datetime(2025, 1, 15, 10, 0))
            datetime(2025, 1, 20, 9, 0)  # Next Monday

            >>> # Today is Monday at 8 AM (before 9 AM)
            >>> _calculate_weekly(task, datetime(2025, 1, 13, 8, 0))
            datetime(2025, 1, 13, 9, 0)  # Today at 9 AM
        """
        # Get target weekday (0=Monday, 6=Sunday)
        target_weekday = task.reminder_time.weekday()
        reminder_time_obj = task.reminder_time.time()

        # Calculate days until next target weekday
        # Example: Today is Wed (2), target is Mon (0)
        # (0 - 2) % 7 = -2 % 7 = 5 days until next Monday
        days_until_target = (target_weekday - now.weekday()) % 7

        if days_until_target == 0:
            # Today is the target weekday
            today_reminder = datetime.combine(now.date(), reminder_time_obj)

            if today_reminder > now:
                # Time hasn't passed yet today
                return today_reminder
            else:
                # Time already passed, schedule for next week
                next_week_reminder = today_reminder + timedelta(weeks=1)
                return next_week_reminder
        else:
            # Target weekday is in the future this week
            next_date = now.date() + timedelta(days=days_until_target)
            next_reminder = datetime.combine(next_date, reminder_time_obj)
            return next_reminder

    @staticmethod
    def _calculate_monthly(task: Task, now: datetime) -> Optional[datetime]:
        """Calculate reminder for monthly recurring task.

        Logic:
        - Reminder occurs on the same day-of-month as original reminder_time
        - Handle edge case: day doesn't exist in some months (e.g., Feb 31)
        - If that day doesn't exist, use last day of month

        Args:
            task: Task with recurrence_pattern='monthly'
            now: Current datetime

        Returns:
            Optional[datetime]: Next occurrence of reminder on target day-of-month

        Example:
            >>> # Reminder on 31st of each month at 10 AM
            >>> task.reminder_time = datetime(2025, 1, 31, 10, 0)

            >>> # Current month: February (no day 31)
            >>> _calculate_monthly(task, datetime(2025, 2, 15, 9, 0))
            datetime(2025, 2, 28, 10, 0)  # Last day of Feb (28 in 2025)

            >>> # Current month: March (has day 31)
            >>> _calculate_monthly(task, datetime(2025, 3, 15, 9, 0))
            datetime(2025, 3, 31, 10, 0)  # March 31st
        """
        target_day = task.reminder_time.day
        reminder_time_obj = task.reminder_time.time()

        # Try to create reminder for current month
        try:
            this_month_date = now.date().replace(day=target_day)
        except ValueError:
            # Day doesn't exist in current month (e.g., Feb 31)
            # Use last day of month instead
            # Strategy: Go to first day of next month, then subtract 1 day
            first_of_next_month = (now.date().replace(day=1) +
                                   relativedelta(months=1))
            this_month_date = first_of_next_month - timedelta(days=1)

        this_month_reminder = datetime.combine(this_month_date, reminder_time_obj)

        if this_month_reminder > now:
            # Reminder hasn't happened this month yet
            return this_month_reminder
        else:
            # Reminder already passed this month, schedule for next month
            try:
                # Try to use same day next month
                next_month_date = (now.date() + relativedelta(months=1)).replace(day=target_day)
            except ValueError:
                # Day doesn't exist in next month either
                first_of_month_after_next = (now.date().replace(day=1) +
                                             relativedelta(months=2))
                next_month_date = first_of_month_after_next - timedelta(days=1)

            next_month_reminder = datetime.combine(next_month_date, reminder_time_obj)
            return next_month_reminder

    @staticmethod
    def should_skip_reminder(task: Task, now: datetime) -> bool:
        """Check if reminder should be skipped.

        Skip Conditions:
        1. Task is completed
        2. Task is more than GRACE_PERIOD_DAYS past due date

        The grace period prevents sending reminders for very overdue tasks
        (user likely abandoned them).

        Args:
            task: Task to check
            now: Current datetime

        Returns:
            bool: True if should skip, False if should send

        Example:
            >>> # Completed task
            >>> task.completed = True
            >>> should_skip_reminder(task, now)
            True

            >>> # Task 10 days overdue (grace period is 7 days)
            >>> task.completed = False
            >>> task.due_date = now - timedelta(days=10)
            >>> should_skip_reminder(task, now)
            True  # More than 7 days overdue, skip
        """
        # Skip if task is completed
        if task.completed:
            return True

        # Skip if task is way overdue (beyond grace period)
        if task.due_date:
            days_overdue = (now - task.due_date).days
            if days_overdue > GRACE_PERIOD_DAYS:
                logger.info(
                    f"⏭️ Skipping reminder for task {task.id}: "
                    f"{days_overdue} days overdue (grace period: {GRACE_PERIOD_DAYS} days)",
                    extra={"task_id": task.id, "days_overdue": days_overdue}
                )
                return True

        return False
