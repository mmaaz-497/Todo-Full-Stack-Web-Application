"""Check if reminder has already been sent (duplicate prevention)."""

from datetime import datetime, timedelta
from sqlmodel import select, and_
from models.reminder_log import ReminderLog
from services.database import get_session
from config.constants import DUPLICATE_CHECK_TOLERANCE_SECONDS
from utils.logger import logger


class DuplicateChecker:
    """Prevent sending duplicate reminders."""

    @staticmethod
    def exists(task_id: int, reminder_datetime: datetime) -> bool:
        """Check if reminder already sent."""
        try:
            with get_session() as session:
                tolerance = timedelta(seconds=DUPLICATE_CHECK_TOLERANCE_SECONDS)
                start_window = reminder_datetime - tolerance
                end_window = reminder_datetime + tolerance

                statement = select(ReminderLog).where(
                    and_(
                        ReminderLog.task_id == task_id,
                        ReminderLog.reminder_datetime >= start_window,
                        ReminderLog.reminder_datetime <= end_window
                    )
                )

                result = session.exec(statement).first()
                return result is not None

        except Exception as e:
            logger.error(f"Error checking duplicates: {e}")
            return False  # Fail-safe
