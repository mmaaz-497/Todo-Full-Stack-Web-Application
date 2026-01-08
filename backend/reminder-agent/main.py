"""AI Reminder Agent - Main entry point."""

import sys
import os

# Ensure current directory is in Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from jobs.reminder_processor import ReminderProcessor
from services.database import init_db, test_connection
from config.settings import settings
from utils.logger import logger


async def startup():
    """Agent startup sequence."""
    logger.info("🚀 Starting AI Reminder Agent")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Polling interval: {settings.polling_interval_minutes} minutes")

    # 1. Test database connection
    if not test_connection():
        logger.critical("Database connection failed. Exiting.")
        raise SystemExit(1)

    # 2. Initialize database tables
    init_db()

    # 3. Validate Gemini API (optional)
    # TODO: Add API health check

    logger.info("✅ Startup complete")


async def main():
    """Main agent loop."""
    # Run startup
    await startup()

    # Create scheduler
    scheduler = AsyncIOScheduler()

    # Create processor
    processor = ReminderProcessor()

    # Schedule reminder processing job
    scheduler.add_job(
        processor.run,
        trigger=IntervalTrigger(minutes=settings.polling_interval_minutes),
        id="reminder_processor",
        name="Process Reminders",
        replace_existing=True
    )

    # Start scheduler
    scheduler.start()
    logger.info(f"⏰ Scheduler started (every {settings.polling_interval_minutes} min)")

    # Keep alive
    try:
        while True:
            await asyncio.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        logger.info("🛑 Shutting down gracefully...")
        scheduler.shutdown()
        logger.info("Goodbye!")


if __name__ == "__main__":
    asyncio.run(main())
