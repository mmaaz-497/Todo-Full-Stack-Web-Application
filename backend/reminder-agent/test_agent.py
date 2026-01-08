"""Manual test script to debug reminder agent."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import asyncio
from datetime import datetime, timedelta
from jobs.reminder_processor import ReminderProcessor
from services.task_reader import TaskReader
from services.database import test_connection
from utils.logger import logger

async def test_agent():
    """Test the reminder agent manually."""
    print("=" * 60)
    print("REMINDER AGENT DEBUG TEST")
    print("=" * 60)

    # 1. Test database connection
    print("\n[1/4] Testing database connection...")
    if not test_connection():
        print("[FAIL] Database connection FAILED")
        return
    print("[OK] Database connected")

    # 2. Fetch tasks needing reminders
    print("\n[2/4] Fetching tasks with reminders...")
    tasks = TaskReader.get_tasks_needing_reminders()
    print(f"Found {len(tasks)} tasks")

    for task in tasks:
        print(f"\n  Task ID: {task.id}")
        print(f"  Title: {task.title}")
        print(f"  User ID: {task.user_id}")
        print(f"  Reminder Time: {task.reminder_time}")
        print(f"  Current UTC Time: {datetime.utcnow()}")

        # Calculate time difference
        if task.reminder_time:
            diff = task.reminder_time - datetime.utcnow()
            minutes = diff.total_seconds() / 60
            print(f"  Time until reminder: {minutes:.1f} minutes")
            if minutes < -5:
                print(f"  [OVERDUE] Reminder is {abs(minutes):.1f} minutes overdue (outside grace period)")
            elif minutes < 0:
                print(f"  [OVERDUE] Reminder is {abs(minutes):.1f} minutes overdue (within grace period)")
            elif minutes < 5:
                print(f"  [DUE SOON] Reminder due in {minutes:.1f} minutes (within lookahead)")
            else:
                print(f"  [NOT YET] Reminder not yet due (too far in future)")

    # 3. Test email lookup
    print("\n[3/4] Testing email lookup...")
    if tasks:
        task = tasks[0]
        email = TaskReader.get_user_email(task.user_id)
        print(f"  User ID: {task.user_id}")
        print(f"  Email: {email}")
        if not email:
            print("  [FAIL] No email found for user")
        elif "@example.com" in email:
            print("  [FAIL] Using placeholder email (user lookup failed)")
        else:
            print("  [OK] Real email found")

    # 4. Run the processor
    print("\n[4/4] Running reminder processor...")
    processor = ReminderProcessor()
    await processor.run()

    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_agent())
