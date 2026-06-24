"""Application constants.

This module contains all hardcoded constants used throughout the application.
These values should NOT be configurable via environment variables.
"""

# ============================================================
# Time Constants
# ============================================================
SECONDS_PER_MINUTE = 60
MINUTES_PER_HOUR = 60
HOURS_PER_DAY = 24
DAYS_PER_WEEK = 7

# ============================================================
# Email Constants
# ============================================================
MAX_EMAIL_SUBJECT_LENGTH = 200
MAX_EMAIL_BODY_LENGTH = 10000

# ============================================================
# Reminder Constants
# ============================================================
# Maximum tasks to process in a single cycle
MAX_TASKS_PER_BATCH = 1000

# Tolerance window for duplicate detection (seconds)
# Reminders within ±60 seconds are considered duplicates
DUPLICATE_CHECK_TOLERANCE_SECONDS = 60

# Grace period after due date (days)
# Stop sending reminders if task is >7 days overdue
GRACE_PERIOD_DAYS = 7

# ============================================================
# Agent State Constants
# ============================================================
# Alert if agent hasn't checked in within this many minutes
AGENT_HEALTHY_THRESHOLD_MINUTES = 10

# ============================================================
# Retry Constants
# ============================================================
# Initial delay for exponential backoff (seconds)
RETRY_INITIAL_DELAY_SECONDS = 1

# Maximum delay for exponential backoff (seconds)
RETRY_MAX_DELAY_SECONDS = 60

# ============================================================
# Priority Emoji Mapping
# ============================================================
PRIORITY_EMOJIS = {
    "HIGH": "🔴 URGENT",
    "MEDIUM": "🟡",
    "LOW": "📋"
}

# ============================================================
# Recurrence Pattern Constants
# ============================================================
RECURRENCE_NONE = "none"
RECURRENCE_DAILY = "daily"
RECURRENCE_WEEKLY = "weekly"
RECURRENCE_MONTHLY = "monthly"

# Valid recurrence patterns
VALID_RECURRENCE_PATTERNS = [
    RECURRENCE_NONE,
    RECURRENCE_DAILY,
    RECURRENCE_WEEKLY,
    RECURRENCE_MONTHLY
]
