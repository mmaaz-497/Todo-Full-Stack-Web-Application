"""Track email delivery status in reminder_log."""

from datetime import datetime
import pytz

from models.reminder_log import ReminderLog, DeliveryStatus
from services.database import get_session
from utils.logger import logger


class DeliveryTracker:
    """Log reminder delivery attempts and status."""

    @staticmethod
    def log_success(
        task_id: int,
        user_id: str,
        reminder_datetime: datetime,
        email_to: str,
        email_subject: str,
        email_body: str
    ) -> None:
        """Log successful reminder delivery."""
        try:
            with get_session() as session:
                # Use Pakistan time since database stores Pakistan local time
                pakistan_tz = pytz.timezone('Asia/Karachi')
                pakistan_now = datetime.now(pakistan_tz).replace(tzinfo=None)

                log_entry = ReminderLog(
                    task_id=task_id,
                    user_id=user_id,
                    reminder_datetime=reminder_datetime,
                    email_to=email_to,
                    email_subject=email_subject,
                    email_body=email_body,
                    delivery_status=DeliveryStatus.SENT.value,
                    sent_at=pakistan_now
                )
                session.add(log_entry)
                session.commit()

                logger.info(f"✅ Logged successful delivery for task {task_id}")

        except Exception as e:
            logger.error(f"Failed to log delivery: {e}")

    @staticmethod
    def log_failure(
        task_id: int,
        user_id: str,
        reminder_datetime: datetime,
        email_to: str,
        email_subject: str,
        email_body: str,
        error_message: str
    ) -> None:
        """Log failed reminder delivery."""
        try:
            with get_session() as session:
                # Use Pakistan time since database stores Pakistan local time
                pakistan_tz = pytz.timezone('Asia/Karachi')
                pakistan_now = datetime.now(pakistan_tz).replace(tzinfo=None)

                log_entry = ReminderLog(
                    task_id=task_id,
                    user_id=user_id,
                    reminder_datetime=reminder_datetime,
                    email_to=email_to,
                    email_subject=email_subject,
                    email_body=email_body,
                    delivery_status=DeliveryStatus.FAILED.value,
                    error_message=error_message,
                    sent_at=pakistan_now
                )
                session.add(log_entry)
                session.commit()

                logger.error(f"❌ Logged failed delivery for task {task_id}: {error_message}")

        except Exception as e:
            logger.error(f"Failed to log error: {e}")
