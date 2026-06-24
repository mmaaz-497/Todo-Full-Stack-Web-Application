"""Task reading service for fetching tasks needing reminders.

This service queries the database for tasks with upcoming reminders
within the configured lookahead window.
"""

from sqlmodel import Session, select, and_
from typing import List, Optional
from datetime import datetime, timedelta

from models import Task

from services.database import get_session
from config.settings import settings
from utils.logger import logger
from utils.timezone import convert_to_user_timezone
import pytz


class TaskReader:
    """Read and filter tasks that need reminders.

    This service implements a two-stage filtering approach:
    1. SQL query: Filter obvious cases (completed=false, has reminder_time)
    2. In-memory: Apply complex time window logic

    This approach optimizes database queries while allowing flexible
    time-based filtering.
    """

    @staticmethod
    def get_tasks_needing_reminders() -> List[Task]:
        """Fetch tasks that need reminders within the lookahead window.

        Query Strategy:
        1. SELECT tasks WHERE completed=false AND reminder_time IS NOT NULL
        2. Filter in-memory for time window matching

        The lookahead window is defined by REMINDER_LOOKAHEAD_MINUTES setting.
        Tasks with reminders due within [now, now + lookahead] are returned.

        Returns:
            List[Task]: Tasks needing reminders

        Example:
            >>> # At 2:00 PM with 5-minute lookahead
            >>> tasks = TaskReader.get_tasks_needing_reminders()
            >>> # Returns tasks with reminders between 2:00 PM - 2:05 PM
        """
        try:
            with get_session() as session:
                # Use Pakistan time since database stores Pakistan local time
                pakistan_tz = pytz.timezone('Asia/Karachi')
                now = datetime.now(pakistan_tz).replace(tzinfo=None)
                lookahead = now + timedelta(
                    minutes=settings.reminder_lookahead_minutes
                )

                # Build SQL query
                # Filters: not completed, has reminder time set
                statement = select(Task).where(
                    and_(
                        Task.completed == False,
                        Task.reminder_time.is_not(None)
                    )
                )

                tasks = session.exec(statement).all()

                # Apply time window filtering in-memory
                # This allows complex recurrence logic without complex SQL
                filtered_tasks = [
                    task for task in tasks
                    if TaskReader._should_process_now(task, now, lookahead)
                ]

                # Eagerly load all task attributes before session closes
                # This prevents "not bound to a Session" errors later
                for task in filtered_tasks:
                    # Access all attributes to load them into memory
                    _ = task.id, task.title, task.description, task.user_id
                    _ = task.priority, task.due_date, task.reminder_time
                    _ = task.recurrence_pattern, task.completed, task.tags

                logger.info(
                    f"📥 Found {len(filtered_tasks)} tasks needing reminders "
                    f"(out of {len(tasks)} total incomplete tasks)",
                    extra={
                        "action": "task_query",
                        "count": len(filtered_tasks),
                        "total": len(tasks)
                    }
                )

                # Make tasks available after session closes
                session.expunge_all()

                return filtered_tasks

        except Exception as e:
            logger.error(
                f"❌ Error fetching tasks: {e}",
                extra={"action": "task_query"}
            )
            return []

    @staticmethod
    def _should_process_now(
        task: Task,
        now: datetime,
        lookahead: datetime
    ) -> bool:
        """Check if task reminder should be processed in this cycle.

        Decision Logic:
        - One-time tasks: Check if reminder_time within [now, lookahead]
        - Recurring tasks: Always return True (ReminderCalculator decides timing)

        Args:
            task: Task to check
            now: Current datetime (UTC)
            lookahead: End of lookahead window (UTC)

        Returns:
            bool: True if task should be processed this cycle

        Example:
            >>> # One-time task with reminder at 2:03 PM
            >>> # Current time: 2:00 PM, lookahead: 2:05 PM
            >>> _should_process_now(task, now, lookahead)
            True  # Within window

            >>> # Current time: 2:06 PM (missed window)
            >>> _should_process_now(task, now + timedelta(minutes=6), lookahead)
            False  # Outside window
        """
        if not task.reminder_time:
            return False

        # For one-time tasks (recurrence_pattern = "none")
        # Check if reminder falls within current window
        # Include overdue reminders within grace period (5 minutes past due)
        if task.recurrence_pattern == "none":
            grace_period = now - timedelta(minutes=5)
            return grace_period <= task.reminder_time < lookahead

        # For recurring tasks (daily, weekly, monthly)
        # Always process - ReminderCalculator will determine exact timing
        # This is necessary because recurring logic is complex (e.g., "every Monday")
        return True

    @staticmethod
    def get_user_email(user_id: str) -> Optional[str]:
        """Fetch user email from Better Auth user table.

        Args:
            user_id: User ID

        Returns:
            Optional[str]: User email address, or None if user not found

        Raises:
            Exception: If database query fails (logged but not raised)

        Example:
            >>> email = TaskReader.get_user_email("user_abc123")
            >>> print(email)
            "user@example.com"
        """
        try:
            from models import User  # Import here to avoid circular dependency

            with get_session() as session:
                # Query user table for email address
                statement = select(User).where(User.id == user_id)
                user = session.exec(statement).first()

                if not user:
                    logger.warning(
                        f"User not found: {user_id}",
                        extra={"action": "user_lookup", "user_id": user_id}
                    )
                    return None

                if not user.email:
                    logger.warning(
                        f"User {user_id} has no email address",
                        extra={"action": "user_lookup", "user_id": user_id}
                    )
                    return None

                logger.debug(
                    f"Found email for user {user_id}: {user.email}",
                    extra={"action": "user_lookup", "user_id": user_id}
                )

                return user.email

        except Exception as e:
            logger.error(
                f"Error fetching user email for {user_id}: {e}",
                extra={"action": "user_lookup", "user_id": user_id}
            )
            return None

    @staticmethod
    def get_user_name(user_id: str) -> Optional[str]:
        """Fetch user display name from Better Auth user table.

        Args:
            user_id: User ID

        Returns:
            Optional[str]: User display name, or None if not found

        Example:
            >>> name = TaskReader.get_user_name("user_abc123")
            >>> print(name)
            "John Doe"
        """
        try:
            from models import User

            with get_session() as session:
                statement = select(User).where(User.id == user_id)
                user = session.exec(statement).first()

                if user and user.name:
                    return user.name

                return None

        except Exception as e:
            logger.error(
                f"Error fetching user name for {user_id}: {e}",
                extra={"action": "user_lookup", "user_id": user_id}
            )
            return None

    @staticmethod
    def get_user_timezone(user_id: str) -> Optional[str]:
        """Fetch user timezone from database.

        TODO: Add timezone column to users table and query it.

        Args:
            user_id: User ID

        Returns:
            Optional[str]: IANA timezone string (e.g., "America/New_York"),
                          or None to use UTC

        Example:
            >>> tz = get_user_timezone("user123")
            >>> if tz:
            ...     # Convert reminder time to user's local time
            ...     local_time = convert_to_user_timezone(utc_time, tz)
        """
        # TODO: Add timezone column to users table
        # For now, default to UTC (None)
        return None
