"""Dapr Scheduler Service for Job Management (Phase V)

This module implements scheduling via Dapr Jobs API for reminders
and other timed operations.
"""

import asyncio
import httpx
from datetime import datetime
from typing import Dict, Any, Optional
import os


class DaprScheduler:
    """Service for scheduling jobs via Dapr Jobs API."""

    def __init__(self, dapr_http_port: Optional[int] = None):
        """Initialize the Dapr scheduler."""
        self.dapr_http_port = dapr_http_port or int(os.getenv("DAPR_HTTP_PORT", "3500"))
        self.dapr_url = f"http://localhost:{self.dapr_http_port}"

    async def schedule_reminder(
        self,
        job_name: str,
        schedule_time: datetime,
        task_id: int,
        user_id: str,
        task_title: str,
        task_description: str = ""
    ) -> bool:
        """
        Schedule a reminder using Dapr Jobs API.

        Args:
            job_name: Unique name for the job
            schedule_time: When the job should run
            task_id: Associated task ID
            user_id: User ID
            task_title: Task title for the reminder
            task_description: Task description for the reminder
        """
        async with httpx.AsyncClient() as client:
            try:
                # Format the schedule time as ISO string
                schedule_str = schedule_time.strftime("%Y-%m-%dT%H:%M:%SZ")

                job_data = {
                    "schedule": schedule_str,
                    "repeats": 0,  # One-time job for reminders
                    "data": {
                        "job_type": "reminder",
                        "task_id": task_id,
                        "user_id": user_id,
                        "task_title": task_title,
                        "task_description": task_description,
                        "scheduled_at": datetime.utcnow().isoformat()
                    }
                }

                response = await client.put(
                    f"{self.dapr_url}/v1.0-alpha1/jobs/{job_name}",
                    json=job_data,
                    timeout=30.0
                )

                if response.status_code != 204:
                    raise Exception(f"Dapr schedule job failed with status {response.status_code}: {response.text}")

                print(f"Dapr scheduled reminder job {job_name} for {schedule_str}")
                return True
            except httpx.RequestError as e:
                print(f"Error connecting to Dapr for job scheduling: {e}")
                raise
            except Exception as e:
                print(f"Error scheduling job via Dapr: {e}")
                raise

    async def cancel_scheduled_job(self, job_name: str) -> bool:
        """Cancel a scheduled job."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.delete(
                    f"{self.dapr_url}/v1.0-alpha1/jobs/{job_name}",
                    timeout=30.0
                )

                if response.status_code != 204:
                    raise Exception(f"Dapr cancel job failed with status {response.status_code}: {response.text}")

                print(f"Dapr canceled scheduled job {job_name}")
                return True
            except httpx.RequestError as e:
                print(f"Error connecting to Dapr for job cancellation: {e}")
                raise
            except Exception as e:
                print(f"Error canceling job via Dapr: {e}")
                raise

    async def schedule_recurring_task_generation(
        self,
        job_name: str,
        cron_schedule: str,
        task_id: int,
        user_id: str
    ) -> bool:
        """
        Schedule recurring task generation using a cron-like schedule.

        Args:
            job_name: Unique name for the job
            cron_schedule: Cron expression for scheduling
            task_id: Parent recurring task ID
            user_id: User ID
        """
        async with httpx.AsyncClient() as client:
            try:
                job_data = {
                    "schedule": cron_schedule,  # This would be a cron expression
                    "repeats": -1,  # Infinite repeats for recurring tasks
                    "data": {
                        "job_type": "recurring-task-generator",
                        "task_id": task_id,
                        "user_id": user_id,
                        "scheduled_at": datetime.utcnow().isoformat()
                    }
                }

                response = await client.put(
                    f"{self.dapr_url}/v1.0-alpha1/jobs/{job_name}",
                    json=job_data,
                    timeout=30.0
                )

                if response.status_code != 204:
                    raise Exception(f"Dapr schedule recurring job failed with status {response.status_code}: {response.text}")

                print(f"Dapr scheduled recurring task job {job_name}")
                return True
            except httpx.RequestError as e:
                print(f"Error connecting to Dapr for recurring job scheduling: {e}")
                raise
            except Exception as e:
                print(f"Error scheduling recurring job via Dapr: {e}")
                raise


# Global instance
dapr_scheduler = DaprScheduler()