"""Main scheduled job to process reminders."""

from datetime import datetime
from sqlmodel import select
import pytz

from services.task_reader import TaskReader
from services.reminder_calculator import ReminderCalculator
from services.duplicate_checker import DuplicateChecker
from services.ai_email_generator import AIEmailGenerator
from services.email_sender import EmailSender
from services.delivery_tracker import DeliveryTracker
from services.database import get_session
from models.agent_state import AgentState, AgentStatus
from utils.logger import logger


class ReminderProcessor:
    """Process reminders for all tasks."""

    def __init__(self):
        """Initialize processor with dependencies."""
        self.ai_generator = AIEmailGenerator()

    async def run(self) -> None:
        """Execute reminder processing cycle."""
        logger.info("Starting reminder processing cycle")

        tasks_processed = 0
        reminders_sent = 0
        errors_count = 0

        try:
            # 1. Update agent state
            self._update_agent_state(AgentStatus.RUNNING)

            # 2. Fetch tasks needing reminders
            tasks = TaskReader.get_tasks_needing_reminders()
            logger.info(f"Found {len(tasks)} tasks to process")

            # 3. Process each task
            for task in tasks:
                tasks_processed += 1

                try:
                    # Skip if task should not get reminder
                    # Use Pakistan time since database stores Pakistan local time
                    pakistan_tz = pytz.timezone('Asia/Karachi')
                    now = datetime.now(pakistan_tz).replace(tzinfo=None)

                    if ReminderCalculator.should_skip_reminder(task, now):
                        continue

                    # Calculate reminder datetime
                    reminder_dt = ReminderCalculator.calculate_reminder_datetime(task, now)
                    if not reminder_dt:
                        continue

                    # Check for duplicates
                    if DuplicateChecker.exists(task.id, reminder_dt):
                        logger.debug(f"Skipping duplicate reminder for task {task.id}")
                        continue

                    # Get user info (TODO: integrate with Better Auth)
                    user_email = TaskReader.get_user_email(task.user_id)
                    if not user_email:
                        logger.warning(f"No email found for user {task.user_id}")
                        continue

                    # Generate AI email
                    email_content = self.ai_generator.generate(
                        task=task,
                        user_name=None,  # TODO: get from user table
                        user_timezone="Asia/Karachi"  # Pakistan timezone (UTC+5)
                    )

                    # Send email
                    email_sender = EmailSender()
                    success = await email_sender.send(
                        to=user_email,
                        subject=email_content.subject,
                        body=email_content.body,
                        task=task,
                        user_name=None
                    )

                    # Log delivery
                    if success:
                        DeliveryTracker.log_success(
                            task_id=task.id,
                            user_id=task.user_id,
                            reminder_datetime=reminder_dt,
                            email_to=user_email,
                            email_subject=email_content.subject,
                            email_body=email_content.body
                        )
                        reminders_sent += 1
                        logger.info(f"✅ Reminder sent: {task.title} → {user_email}")
                    else:
                        DeliveryTracker.log_failure(
                            task_id=task.id,
                            user_id=task.user_id,
                            reminder_datetime=reminder_dt,
                            email_to=user_email,
                            email_subject=email_content.subject,
                            email_body=email_content.body,
                            error_message="Email send failed after retries"
                        )
                        errors_count += 1

                except Exception as e:
                    logger.error(f"Error processing task {task.id}: {e}")
                    errors_count += 1

            # 4. Update final state
            self._update_agent_state(
                AgentStatus.RUNNING,
                tasks_processed=tasks_processed,
                reminders_sent=reminders_sent,
                errors_count=errors_count
            )

            logger.info(
                f"Cycle complete: {tasks_processed} processed, {reminders_sent} sent, {errors_count} errors"
            )

        except Exception as e:
            logger.critical(f"Critical error in reminder processor: {e}")
            self._update_agent_state(AgentStatus.ERROR, errors_count=1)

    def _update_agent_state(
        self,
        status: AgentStatus,
        tasks_processed: int = 0,
        reminders_sent: int = 0,
        errors_count: int = 0
    ) -> None:
        """Update agent state in database.

        Args:
            status: Agent status
            tasks_processed: Tasks processed this cycle
            reminders_sent: Reminders sent this cycle
            errors_count: Errors this cycle
        """
        try:
            with get_session() as session:
                # Get or create state record using SQLModel pattern
                # Use Pakistan time since database stores Pakistan local time
                pakistan_tz = pytz.timezone('Asia/Karachi')
                pakistan_now = datetime.now(pakistan_tz).replace(tzinfo=None)

                state = session.exec(select(AgentState)).first()
                if not state:
                    state = AgentState(
                        last_check_at=pakistan_now,
                        status=status.value
                    )
                    session.add(state)
                else:
                    state.last_check_at = pakistan_now
                    state.status = status.value
                    state.tasks_processed += tasks_processed
                    state.reminders_sent += reminders_sent
                    state.errors_count += errors_count
                    state.updated_at = pakistan_now

                session.commit()

        except Exception as e:
            logger.error(f"Failed to update agent state: {e}")
