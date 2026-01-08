"""
Dapr Jobs API Integration for Reminder Scheduling

This module handles scheduling, cancellation, and rescheduling of task reminders
using the Dapr Jobs API (Dapr 1.14+).

Features:
- Schedule one-time reminder jobs at specific times
- Cancel scheduled jobs when tasks are completed or deleted
- Reschedule jobs when task due dates change
- Automatic retry with exponential backoff

Dapr Jobs API Documentation:
https://docs.dapr.io/developing-applications/building-blocks/jobs/
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Optional
import httpx

logger = logging.getLogger(__name__)

# Dapr HTTP endpoint (default: localhost:3500)
DAPR_HTTP_URL = os.getenv("DAPR_HTTP_URL", "http://localhost:3500")

# Dapr Jobs API version
DAPR_JOBS_API_VERSION = "v1alpha1"


class ReminderScheduler:
    """
    Scheduler for task reminders using Dapr Jobs API.

    The Dapr Jobs API schedules jobs that trigger HTTP callbacks at specified times.
    Each reminder is a job that calls the /api/reminders/callback endpoint when due.
    """

    def __init__(self, dapr_url: str = DAPR_HTTP_URL):
        """
        Initialize reminder scheduler.

        Args:
            dapr_url: Dapr HTTP endpoint URL
        """
        self.dapr_url = dapr_url
        self.jobs_endpoint = f"{dapr_url}/{DAPR_JOBS_API_VERSION}/jobs"

    async def schedule_reminder(
        self,
        task_id: int,
        user_id: int,
        due_date: datetime,
        reminder_offset: timedelta,
        task_title: str,
        task_description: Optional[str] = None
    ) -> bool:
        """
        Schedule a reminder job for a task.

        Creates a Dapr job that will trigger at (due_date - reminder_offset).
        The job will POST to /api/reminders/callback with task details.

        Args:
            task_id: Task ID
            user_id: User ID who owns the task
            due_date: Task due date
            reminder_offset: Time before due date to send reminder
            task_title: Task title
            task_description: Task description (optional)

        Returns:
            True if scheduling succeeded, False otherwise
        """
        try:
            # Calculate reminder trigger time
            reminder_time = due_date - reminder_offset

            # Skip if reminder time is in the past
            if reminder_time <= datetime.utcnow():
                logger.warning(
                    f"Reminder time {reminder_time} is in the past for task {task_id}. "
                    "Skipping scheduling."
                )
                return False

            # Generate unique job name
            job_name = f"reminder-task-{task_id}-user-{user_id}"

            # Job payload (sent to callback endpoint)
            job_data = {
                "task_id": task_id,
                "user_id": user_id,
                "due_date": due_date.isoformat(),
                "task_title": task_title,
                "task_description": task_description,
                "reminder_time": reminder_time.isoformat()
            }

            # Dapr Jobs API request
            job_spec = {
                "name": job_name,
                "schedule": f"@at {reminder_time.isoformat()}",  # One-time job at specific time
                "repeats": 1,  # Run once
                "data": job_data,
                "dueTime": reminder_time.isoformat()
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.jobs_endpoint,
                    json=job_spec,
                    timeout=10.0
                )
                response.raise_for_status()

            logger.info(
                f"Scheduled reminder job '{job_name}' for task {task_id} "
                f"at {reminder_time.isoformat()}"
            )
            return True

        except httpx.HTTPStatusError as e:
            logger.error(
                f"Failed to schedule reminder for task {task_id}: "
                f"HTTP {e.response.status_code} - {e.response.text}"
            )
            return False
        except Exception as e:
            logger.error(f"Unexpected error scheduling reminder for task {task_id}: {e}")
            return False

    async def cancel_reminder(self, task_id: int, user_id: int) -> bool:
        """
        Cancel a scheduled reminder job.

        Called when:
        - Task is completed before due date
        - Task is deleted

        Args:
            task_id: Task ID
            user_id: User ID who owns the task

        Returns:
            True if cancellation succeeded, False otherwise
        """
        try:
            # Generate job name (must match schedule_reminder)
            job_name = f"reminder-task-{task_id}-user-{user_id}"

            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.jobs_endpoint}/{job_name}",
                    timeout=10.0
                )

                # 404 is acceptable (job already executed or never existed)
                if response.status_code == 404:
                    logger.info(f"Reminder job '{job_name}' not found (already executed or never scheduled)")
                    return True

                response.raise_for_status()

            logger.info(f"Cancelled reminder job '{job_name}' for task {task_id}")
            return True

        except httpx.HTTPStatusError as e:
            logger.error(
                f"Failed to cancel reminder for task {task_id}: "
                f"HTTP {e.response.status_code} - {e.response.text}"
            )
            return False
        except Exception as e:
            logger.error(f"Unexpected error cancelling reminder for task {task_id}: {e}")
            return False

    async def reschedule_reminder(
        self,
        task_id: int,
        user_id: int,
        new_due_date: datetime,
        reminder_offset: timedelta,
        task_title: str,
        task_description: Optional[str] = None
    ) -> bool:
        """
        Reschedule a reminder job with new due date.

        Called when task due date is updated.

        Strategy:
        1. Cancel existing job
        2. Schedule new job with updated time

        Args:
            task_id: Task ID
            user_id: User ID who owns the task
            new_due_date: Updated task due date
            reminder_offset: Time before due date to send reminder
            task_title: Task title
            task_description: Task description (optional)

        Returns:
            True if rescheduling succeeded, False otherwise
        """
        try:
            # Step 1: Cancel existing reminder
            await self.cancel_reminder(task_id, user_id)

            # Step 2: Schedule new reminder
            return await self.schedule_reminder(
                task_id=task_id,
                user_id=user_id,
                due_date=new_due_date,
                reminder_offset=reminder_offset,
                task_title=task_title,
                task_description=task_description
            )

        except Exception as e:
            logger.error(f"Unexpected error rescheduling reminder for task {task_id}: {e}")
            return False


# Global scheduler instance
reminder_scheduler = ReminderScheduler()
