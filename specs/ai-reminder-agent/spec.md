# AI-Powered Task Reminder Agent Specification

**Feature**: AI Task Reminder Agent
**Version**: 1.0.0
**Date**: 2025-12-25
**Status**: Draft

---

## 1. Executive Summary

The AI-Powered Task Reminder Agent is an autonomous background service that monitors user tasks, calculates reminder schedules based on complex repeat rules, and sends intelligent, personalized reminder emails at the appropriate times. Built with Python and leveraging the Gemini LLM via OpenAI Agents SDK, this agent ensures users never miss important tasks while maintaining data security and email deliverability.

### Key Goals
- **Reliability**: Never miss a reminder; handle failures gracefully
- **Intelligence**: AI-generated, context-aware reminder messages
- **Scalability**: Support thousands of users and tasks
- **Security**: Protect user data; prevent unauthorized access
- **Extensibility**: Design for future SMS/push notification channels

---

## 2. System Context

### Technology Stack
- **Backend Framework**: FastAPI (Python)
- **Database**: PostgreSQL (Neon Serverless)
- **Authentication**: Better Auth
- **AI Framework**: OpenAI Agents SDK
- **LLM Provider**: Gemini API (via OpenAI-compatible interface)
- **Email Service**: SMTP (with verified sender domain) or SendGrid/AWS SES
- **Task Scheduler**: APScheduler or Celery Beat
- **Message Queue**: Redis (for Celery) or in-memory (for APScheduler)

### Integration Points
```
┌──────────────┐
│  Frontend    │
│  (Next.js)   │
└──────┬───────┘
       │
       ↓
┌──────────────────────────────────────────────────────┐
│            FastAPI Backend                           │
│  ┌────────────────┐         ┌───────────────────┐   │
│  │  Task CRUD API │←────────→│   PostgreSQL DB   │   │
│  └────────────────┘         └─────────┬─────────┘   │
│                                        │             │
│  ┌─────────────────────────────────────┼──────────┐ │
│  │   AI Reminder Agent Service         │          │ │
│  │  ┌──────────────────┐              ↓          │ │
│  │  │  Scheduler        │      ┌──────────────┐  │ │
│  │  │  (APScheduler/    │──────→│ Task Reader  │  │ │
│  │  │   Celery Beat)    │      └──────┬───────┘  │ │
│  │  └──────────────────┘             │          │ │
│  │                                    ↓          │ │
│  │                          ┌──────────────────┐ │ │
│  │                          │ Reminder         │ │ │
│  │                          │ Calculator       │ │ │
│  │                          └────────┬─────────┘ │ │
│  │                                   │           │ │
│  │                                   ↓           │ │
│  │                          ┌──────────────────┐ │ │
│  │                          │ AI Email         │ │ │
│  │                          │ Generator        │ │ │
│  │                          │ (Gemini)         │ │ │
│  │                          └────────┬─────────┘ │ │
│  │                                   │           │ │
│  │                                   ↓           │ │
│  │                          ┌──────────────────┐ │ │
│  │                          │ Email Sender     │ │ │
│  │                          │ (SMTP/SES)       │ │ │
│  │                          └────────┬─────────┘ │ │
│  │                                   │           │ │
│  │                          ┌────────▼─────────┐ │ │
│  │                          │ Delivery Tracker │ │ │
│  │                          └──────────────────┘ │ │
│  └──────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────┘
                   │
                   ↓
          ┌────────────────┐
          │  User's Email  │
          └────────────────┘
```

---

## 3. Data Model

### 3.1 Task Schema (Existing)
```python
class Task:
    id: UUID
    user_id: UUID
    name: str                    # Task title
    description: str | None      # Detailed description
    tag: str | None              # Category/tag
    due_date: datetime | None    # When task is due
    reminder_date: date | None   # Date to send reminder
    reminder_time: time | None   # Time to send reminder
    importance: Enum["High", "Medium", "Low"]
    repeat_type: Enum["None", "Daily", "Weekly", "Monthly"]
    created_at: datetime
    updated_at: datetime
    completed: bool
    completed_at: datetime | None
```

### 3.2 New Tables Required

#### reminder_log
Tracks all reminders sent to prevent duplicates and provide audit trail.

```sql
CREATE TABLE reminder_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    reminder_datetime TIMESTAMP WITH TIME ZONE NOT NULL,
    sent_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    email_to VARCHAR(255) NOT NULL,
    email_subject TEXT NOT NULL,
    email_body TEXT NOT NULL,
    delivery_status VARCHAR(50) DEFAULT 'pending', -- pending, sent, failed, bounced
    error_message TEXT,
    retry_count INT DEFAULT 0,
    next_retry_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(task_id, reminder_datetime) -- Prevent duplicate reminders
);

CREATE INDEX idx_reminder_log_task ON reminder_log(task_id);
CREATE INDEX idx_reminder_log_user ON reminder_log(user_id);
CREATE INDEX idx_reminder_log_status ON reminder_log(delivery_status);
CREATE INDEX idx_reminder_log_sent_at ON reminder_log(sent_at);
```

#### agent_state
Tracks agent execution state and health.

```sql
CREATE TABLE agent_state (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    last_check_at TIMESTAMP WITH TIME ZONE NOT NULL,
    tasks_processed INT DEFAULT 0,
    reminders_sent INT DEFAULT 0,
    errors_count INT DEFAULT 0,
    status VARCHAR(50) DEFAULT 'running', -- running, paused, error
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

---

## 4. Agent Responsibilities

### 4.1 Core Functions

| Responsibility | Description | Frequency |
|---------------|-------------|-----------|
| **Task Polling** | Query database for tasks with upcoming reminders | Every 5 minutes |
| **Reminder Calculation** | Compute next reminder datetime based on rules | Per task |
| **Duplicate Prevention** | Check `reminder_log` before sending | Per reminder |
| **AI Email Generation** | Use Gemini to craft personalized emails | Per reminder |
| **Email Delivery** | Send via SMTP/SES with retry logic | Per reminder |
| **Status Tracking** | Log delivery status and errors | Per reminder |
| **Health Monitoring** | Update `agent_state` table | Every cycle |

### 4.2 Reminder Calculation Logic

#### One-Time Tasks (repeat_type = "None")
```python
if reminder_date and reminder_time:
    reminder_datetime = datetime.combine(reminder_date, reminder_time)
    if now < reminder_datetime <= now + polling_interval:
        send_reminder()
```

#### Daily Tasks (repeat_type = "Daily")
```python
# Send reminder at reminder_time every day until task is completed
if reminder_time:
    today_reminder = datetime.combine(date.today(), reminder_time)
    if now < today_reminder <= now + polling_interval:
        send_reminder()
```

#### Weekly Tasks (repeat_type = "Weekly")
```python
# Send reminder at reminder_time on the same weekday every week
if reminder_date and reminder_time:
    start_weekday = reminder_date.weekday()
    today = date.today()
    days_until_reminder = (start_weekday - today.weekday()) % 7
    next_reminder_date = today + timedelta(days=days_until_reminder)
    reminder_datetime = datetime.combine(next_reminder_date, reminder_time)
    if now < reminder_datetime <= now + polling_interval:
        send_reminder()
```

#### Monthly Tasks (repeat_type = "Monthly")
```python
# Send reminder on the same day of month at reminder_time
if reminder_date and reminder_time:
    target_day = reminder_date.day
    today = date.today()

    # Handle months with fewer days (e.g., Feb 31 → Feb 28/29)
    try:
        next_reminder_date = today.replace(day=target_day)
    except ValueError:
        # Day doesn't exist in current month, use last day
        next_reminder_date = today.replace(day=1) + relativedelta(months=1, days=-1)

    if next_reminder_date < today:
        next_reminder_date += relativedelta(months=1)

    reminder_datetime = datetime.combine(next_reminder_date, reminder_time)
    if now < reminder_datetime <= now + polling_interval:
        send_reminder()
```

#### Additional Rules
- **Skip if completed**: Never send reminders for completed tasks
- **Grace period**: Don't send reminders more than 1 week past due_date
- **Time zone handling**: Use user's time zone (default to UTC if not set)

---

## 5. AI Email Generation

### 5.1 Gemini Integration via OpenAI Agents SDK

```python
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

def generate_reminder_email(task: Task, user: User) -> EmailContent:
    """
    Generate personalized reminder email using Gemini.
    """
    prompt = f"""
You are a professional task reminder assistant. Generate a concise,
motivating reminder email for the following task.

User: {user.name}
Task Name: {task.name}
Description: {task.description or 'No description'}
Tag: {task.tag or 'General'}
Due Date: {task.due_date.strftime('%B %d, %Y') if task.due_date else 'No due date'}
Importance: {task.importance}
Repeat: {task.repeat_type}

Requirements:
- Professional but warm tone
- 2-3 sentences maximum
- Include task name, due date, and importance
- Add a brief motivational closing
- Do NOT include subject line (will be generated separately)

Email body:
"""

    response = client.chat.completions.create(
        model="gemini-2.0-flash",  # or gemini-2.0-pro
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=200
    )

    email_body = response.choices[0].message.content.strip()

    # Generate subject
    subject = f"⏰ Reminder: {task.name}"
    if task.importance == "High":
        subject = f"🔴 URGENT: {task.name}"
    elif task.importance == "Medium":
        subject = f"🟡 Reminder: {task.name}"

    return EmailContent(subject=subject, body=email_body)
```

### 5.2 Email Template

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #4F46E5; color: white; padding: 20px; border-radius: 8px 8px 0 0; }
        .content { background: #F9FAFB; padding: 20px; border: 1px solid #E5E7EB; }
        .task-details { background: white; padding: 15px; margin: 15px 0; border-left: 4px solid #4F46E5; }
        .importance-high { border-left-color: #EF4444; }
        .importance-medium { border-left-color: #F59E0B; }
        .importance-low { border-left-color: #10B981; }
        .footer { text-align: center; padding: 15px; color: #6B7280; font-size: 12px; }
        .button { background: #4F46E5; color: white; padding: 12px 24px; text-decoration: none;
                  border-radius: 6px; display: inline-block; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>📋 Task Reminder</h2>
        </div>
        <div class="content">
            <p>Hi {{user_name}},</p>

            {{ai_generated_message}}

            <div class="task-details importance-{{importance_lower}}">
                <h3>{{task_name}}</h3>
                <p><strong>Tag:</strong> {{task_tag}}</p>
                <p><strong>Due Date:</strong> {{due_date}}</p>
                <p><strong>Importance:</strong> {{importance}}</p>
                {{#if description}}
                <p><strong>Description:</strong> {{description}}</p>
                {{/if}}
            </div>

            <a href="{{app_url}}/tasks/{{task_id}}" class="button">View Task</a>
        </div>
        <div class="footer">
            <p>You're receiving this because you set a reminder for this task.</p>
            <p><a href="{{app_url}}/settings/notifications">Manage notification preferences</a></p>
        </div>
    </div>
</body>
</html>
```

---

## 6. System Architecture

### 6.1 Agent Service Components

```
reminder_agent/
├── __init__.py
├── main.py                    # Entry point, starts scheduler
├── config.py                  # Configuration management
├── scheduler.py               # APScheduler or Celery setup
├── models/
│   ├── __init__.py
│   ├── task.py               # Task model
│   ├── reminder_log.py       # ReminderLog model
│   └── agent_state.py        # AgentState model
├── services/
│   ├── __init__.py
│   ├── task_reader.py        # Query tasks from DB
│   ├── reminder_calculator.py # Calculate next reminder time
│   ├── duplicate_checker.py  # Check reminder_log
│   ├── ai_generator.py       # Gemini email generation
│   ├── email_sender.py       # SMTP/SES integration
│   └── delivery_tracker.py   # Log delivery status
├── jobs/
│   ├── __init__.py
│   └── reminder_job.py       # Main scheduled job
├── utils/
│   ├── __init__.py
│   ├── database.py           # DB connection pool
│   ├── logger.py             # Structured logging
│   └── timezone.py           # Timezone utilities
└── tests/
    ├── __init__.py
    ├── test_calculator.py
    ├── test_ai_generator.py
    └── test_integration.py
```

### 6.2 Main Execution Flow

```python
# main.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from jobs.reminder_job import process_reminders
import logging

logger = logging.getLogger(__name__)

async def start_agent():
    """
    Start the AI Reminder Agent.
    """
    scheduler = AsyncIOScheduler()

    # Run every 5 minutes
    scheduler.add_job(
        process_reminders,
        'interval',
        minutes=5,
        id='reminder_processor',
        replace_existing=True
    )

    scheduler.start()
    logger.info("🤖 AI Reminder Agent started")

    # Keep alive
    try:
        while True:
            await asyncio.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("🛑 AI Reminder Agent stopped")

if __name__ == "__main__":
    asyncio.run(start_agent())
```

```python
# jobs/reminder_job.py
from services.task_reader import TaskReader
from services.reminder_calculator import ReminderCalculator
from services.duplicate_checker import DuplicateChecker
from services.ai_generator import AIEmailGenerator
from services.email_sender import EmailSender
from services.delivery_tracker import DeliveryTracker
import logging

logger = logging.getLogger(__name__)

async def process_reminders():
    """
    Main job: Find tasks, calculate reminders, send emails.
    """
    try:
        # 1. Read tasks with upcoming reminders
        tasks = await TaskReader.get_tasks_needing_reminders()
        logger.info(f"📥 Found {len(tasks)} tasks to process")

        # 2. Process each task
        for task in tasks:
            try:
                # Calculate next reminder datetime
                reminder_dt = ReminderCalculator.calculate(task)
                if not reminder_dt:
                    continue

                # Check for duplicates
                if await DuplicateChecker.exists(task.id, reminder_dt):
                    logger.debug(f"⏭️ Skipping duplicate: {task.id} @ {reminder_dt}")
                    continue

                # Get user info
                user = await TaskReader.get_user(task.user_id)

                # Generate AI email
                email = await AIEmailGenerator.generate(task, user)

                # Send email
                success = await EmailSender.send(
                    to=user.email,
                    subject=email.subject,
                    body=email.body,
                    task=task,
                    user=user
                )

                # Track delivery
                await DeliveryTracker.log(
                    task_id=task.id,
                    user_id=task.user_id,
                    reminder_datetime=reminder_dt,
                    email_to=user.email,
                    email_subject=email.subject,
                    email_body=email.body,
                    status='sent' if success else 'failed'
                )

                logger.info(f"✅ Reminder sent: {task.name} → {user.email}")

            except Exception as e:
                logger.error(f"❌ Error processing task {task.id}: {str(e)}")
                await DeliveryTracker.log_error(task.id, str(e))

        # Update agent state
        await AgentState.update(tasks_processed=len(tasks))

    except Exception as e:
        logger.critical(f"🚨 Critical error in reminder job: {str(e)}")
        await AgentState.update(status='error', errors_count=1)
```

---

## 7. Security & Privacy

### 7.1 Database Access
- **Principle of Least Privilege**: Agent uses separate DB user with read-only access to `tasks` and `users` tables
- **Connection Pooling**: Use SQLAlchemy with connection pooling to prevent connection exhaustion
- **Secrets Management**: Store DB credentials in environment variables or secrets manager (e.g., AWS Secrets Manager)

```python
# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    GEMINI_API_KEY: str
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASSWORD: str
    SENDER_EMAIL: str
    APP_URL: str

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

### 7.2 Email Security
- **SPF/DKIM/DMARC**: Configure DNS records for sender domain
- **Rate Limiting**: Max 100 emails/minute to prevent spam flags
- **Unsubscribe Link**: Include in every email (future: user preferences table)
- **Data Minimization**: Only include necessary task info in emails
- **TLS Encryption**: Use STARTTLS for SMTP connections

### 7.3 API Key Protection
- **Gemini API Key**: Store in environment variable, never log
- **Rotation Policy**: Rotate API keys every 90 days
- **Usage Monitoring**: Track API calls to detect anomalies

### 7.4 Data Retention
- **Reminder Logs**: Retain for 90 days, then archive or delete
- **PII Handling**: Anonymize email addresses in logs after 30 days

---

## 8. Error Handling & Resilience

### 8.1 Failure Scenarios & Mitigations

| Failure | Detection | Recovery |
|---------|-----------|----------|
| **Database unreachable** | Connection timeout | Retry 3x with exponential backoff; alert ops |
| **Gemini API error** | HTTP 5xx or timeout | Fallback to template-based email; retry after 1 min |
| **Email delivery failure** | SMTP error code | Log to `reminder_log`, retry 3x over 1 hour |
| **Invalid task data** | Validation error | Log warning, skip task, notify dev team |
| **Duplicate reminders** | UNIQUE constraint violation | Log as info, continue processing |

### 8.2 Retry Logic

```python
# services/email_sender.py
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

class EmailSender:
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=60, max=3600),
        reraise=True
    )
    async def send(self, to: str, subject: str, body: str, **kwargs) -> bool:
        """
        Send email with retry logic.
        """
        try:
            # SMTP send logic here
            await self._send_smtp(to, subject, body, **kwargs)
            return True
        except SMTPException as e:
            logger.warning(f"📧 Email send failed to {to}: {e}. Retrying...")
            raise
```

### 8.3 Monitoring & Alerts

**Metrics to Track**:
- Reminders sent/hour
- Email delivery success rate
- Gemini API latency & error rate
- Duplicate prevention hits
- Agent job execution time

**Alert Conditions**:
- Email delivery rate < 95% over 1 hour
- Gemini API error rate > 5% over 10 minutes
- Agent job hasn't run in 10 minutes
- Database connection errors > 3 in 5 minutes

---

## 9. Scalability Considerations

### 9.1 Current Scale
- **Users**: Up to 10,000
- **Tasks per user**: Average 20
- **Active reminders**: ~50,000
- **Emails/day**: ~5,000

### 9.2 Scaling Strategy

#### Vertical Scaling (0-50k users)
- Single agent instance with APScheduler
- PostgreSQL connection pool (10-20 connections)
- In-memory deduplication cache (Redis optional)

#### Horizontal Scaling (50k-500k users)
- **Switch to Celery + Redis**:
  - Multiple worker instances
  - Distributed task queue
  - Shared Redis cache for deduplication
- **Database optimizations**:
  - Read replicas for task queries
  - Partition `reminder_log` by month
  - Index on `reminder_date`, `reminder_time`, `completed`
- **Email service**: Upgrade to SendGrid/AWS SES for better throughput

#### Enterprise Scale (500k+ users)
- **Event-driven architecture**:
  - Apache Kafka for task events
  - Dedicated microservice per function
- **Distributed caching**: Redis Cluster
- **Database sharding**: Partition by user_id
- **Multi-region deployment**: Email sending closer to users

---

## 10. Testing Strategy

### 10.1 Unit Tests
- `test_calculator.py`: All repeat type scenarios
- `test_ai_generator.py`: Mock Gemini API, verify prompts
- `test_duplicate_checker.py`: Verify UNIQUE constraint handling
- `test_email_sender.py`: Mock SMTP, test retry logic

### 10.2 Integration Tests
- End-to-end flow: Task creation → Reminder calculation → Email delivery
- Database transaction integrity
- Gemini API real calls (with rate limits)
- SMTP test server (MailHog/Ethereal)

### 10.3 Performance Tests
- Process 10,000 tasks in < 5 minutes
- Handle 100 concurrent email sends
- Database query optimization (< 100ms per query)

### 10.4 Test Cases

| Test Case | Input | Expected Output |
|-----------|-------|-----------------|
| Daily reminder at 9 AM | Task with repeat_type="Daily", reminder_time=09:00 | Reminder sent today at 9 AM, tomorrow at 9 AM, etc. |
| Weekly reminder on Monday | Task with repeat_type="Weekly", reminder_date=Monday | Reminder sent every Monday at reminder_time |
| Monthly reminder on 31st (Feb) | Task with reminder_date=31st, current month=Feb | Reminder sent on Feb 28/29 |
| Completed task | Task with completed=True | No reminder sent |
| Duplicate prevention | Same task_id + reminder_datetime already in log | Skip sending |
| Gemini API timeout | API takes > 10s | Fallback to template, log error |
| Invalid email address | User email = "invalid" | Log error, mark as failed |

---

## 11. Deployment & Operations

### 11.1 Environment Variables
```bash
# .env
DATABASE_URL=postgresql://user:pass@neon.tech:5432/todos
GEMINI_API_KEY=AIza...
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=reminders@yourdomain.com
SMTP_PASSWORD=app-password
SENDER_EMAIL=reminders@yourdomain.com
APP_URL=https://yourdomain.com
LOG_LEVEL=INFO
POLLING_INTERVAL_MINUTES=5
EMAIL_RATE_LIMIT=100  # per minute
RETRY_MAX_ATTEMPTS=3
```

### 11.2 Startup Script
```bash
#!/bin/bash
# start-reminder-agent.sh

cd /app/reminder-agent
source venv/bin/activate

# Health check
python -c "from utils.database import check_connection; check_connection()" || exit 1

# Start agent
python main.py
```

### 11.3 Docker Deployment
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY reminder-agent/ ./reminder-agent/

ENV PYTHONUNBUFFERED=1

CMD ["python", "reminder-agent/main.py"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  reminder-agent:
    build: .
    container_name: todo-reminder-agent
    restart: unless-stopped
    env_file:
      - .env
    depends_on:
      - redis
    networks:
      - todo-network

  redis:
    image: redis:7-alpine
    container_name: todo-redis
    restart: unless-stopped
    networks:
      - todo-network

networks:
  todo-network:
    external: true
```

### 11.4 Health Check Endpoint
```python
# Add to FastAPI backend
from fastapi import APIRouter
from services.agent_state import AgentState

router = APIRouter()

@router.get("/health/reminder-agent")
async def agent_health():
    """
    Check if reminder agent is running.
    """
    state = await AgentState.get_latest()

    if not state:
        return {"status": "error", "message": "No agent state found"}

    time_since_last_check = (datetime.utcnow() - state.last_check_at).total_seconds()

    if time_since_last_check > 600:  # 10 minutes
        return {"status": "error", "message": "Agent hasn't run in 10+ minutes"}

    return {
        "status": "healthy",
        "last_check": state.last_check_at.isoformat(),
        "tasks_processed": state.tasks_processed,
        "reminders_sent": state.reminders_sent
    }
```

---

## 12. Future Enhancements

### 12.1 Phase 2: Multi-Channel Notifications
- **SMS Reminders**: Twilio integration
- **Push Notifications**: Firebase Cloud Messaging (FCM)
- **In-App Notifications**: WebSocket real-time alerts

### 12.2 Phase 3: Advanced AI Features
- **Smart Scheduling**: Gemini suggests optimal reminder times based on user behavior
- **Priority Ranking**: AI reorders tasks by urgency and user patterns
- **Natural Language Reminders**: "Remind me to finish this tomorrow morning" → parsed into structured data

### 12.3 Phase 4: User Preferences
- **Notification Settings**: Per-user control over email/SMS/push
- **Quiet Hours**: Don't send reminders between 10 PM - 7 AM
- **Custom Templates**: User-defined email templates
- **Digest Mode**: Single daily summary email instead of individual reminders

---

## 13. Acceptance Criteria

### Must Have (MVP)
- ✅ Agent polls database every 5 minutes
- ✅ Correctly calculates reminders for all repeat types (None, Daily, Weekly, Monthly)
- ✅ Prevents duplicate reminders using `reminder_log` table
- ✅ Generates professional emails using Gemini API
- ✅ Sends emails via SMTP with retry logic
- ✅ Logs all delivery attempts with status
- ✅ Handles completed tasks (never send reminders)
- ✅ Configurable via environment variables
- ✅ Health check endpoint shows agent status
- ✅ Error handling with fallback to template-based emails

### Should Have (Post-MVP)
- ⚠️ Redis caching for deduplication
- ⚠️ Celery for distributed processing
- ⚠️ Email templates with HTML styling
- ⚠️ User time zone support
- ⚠️ Unsubscribe link in emails

### Nice to Have (Future)
- 💡 SMS notifications
- 💡 Push notifications
- 💡 AI-suggested optimal reminder times
- 💡 User preference management UI

---

## 14. Non-Functional Requirements

### Performance
- **Response Time**: Email generation < 2 seconds
- **Throughput**: Process 1000 tasks in < 5 minutes
- **Database Query Time**: < 100ms per query

### Reliability
- **Uptime**: 99.5% (excluding planned maintenance)
- **Email Delivery Rate**: > 95%
- **Max Duplicate Rate**: < 0.1%

### Security
- **Data Encryption**: TLS for SMTP, encrypted DB connections
- **Access Control**: Separate DB user with read-only permissions
- **Audit Logging**: All reminder actions logged with timestamps

### Maintainability
- **Code Coverage**: > 80%
- **Documentation**: Inline docstrings + README
- **Logging**: Structured JSON logs (timestamp, level, task_id, user_id, action)

---

## 15. Dependencies

### Python Packages
```txt
# requirements.txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
asyncpg==0.29.0
pydantic-settings==2.1.0
apscheduler==3.10.4
openai==1.3.0
aiosmtplib==3.0.1
jinja2==3.1.2
tenacity==8.2.3
redis==5.0.1
python-dateutil==2.8.2
```

### External Services
- **Neon PostgreSQL**: Database hosting
- **Gemini API**: LLM for email generation
- **SMTP Provider**: Gmail/SendGrid/AWS SES for email delivery
- **Redis** (optional): Caching and deduplication

---

## 16. Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Gemini API rate limits | High | Medium | Implement exponential backoff, fallback to templates |
| Email deliverability issues | High | Medium | Use verified sender domain, monitor bounce rates |
| Database connection pool exhaustion | High | Low | Configure max connections, implement connection retry |
| Duplicate reminders due to race condition | Medium | Low | Use database UNIQUE constraint + Redis lock |
| Time zone confusion | Medium | Medium | Store all datetimes in UTC, convert for display only |
| Agent process crashes | High | Low | Docker restart policy, health monitoring |

---

## 17. Open Questions

1. **User Time Zones**: Should we store user time zones in DB or default to UTC?
   - **Recommendation**: Add `timezone` column to `users` table (e.g., "America/New_York")

2. **Email Provider**: SMTP or transactional service (SendGrid/SES)?
   - **Recommendation**: Start with SMTP (Gmail App Password), migrate to SES for scale

3. **Reminder Window**: If user sets reminder for 2:00 PM and agent runs at 2:03 PM, should it still send?
   - **Recommendation**: Yes, send if within `polling_interval + 5 minutes` grace period

4. **Completed Recurring Tasks**: If user completes a daily task, should future reminders stop?
   - **Recommendation**: Yes, set `completed=true` to stop all future reminders

5. **AI Fallback**: If Gemini API fails, use template or skip reminder?
   - **Recommendation**: Use template-based fallback to ensure reminder is sent

---

## 18. Success Metrics

### Week 1 (MVP Launch)
- Agent runs without crashes for 7 days
- 100+ reminders sent successfully
- 0 duplicate reminders detected
- < 5% email delivery failures

### Month 1
- 1,000+ active users receiving reminders
- > 95% email delivery success rate
- Average email generation time < 2s
- User-reported bugs < 5

### Month 3
- 10,000+ active users
- Support for all repeat types validated in production
- AI-generated email quality rated 4.5+/5 by user surveys
- Zero security incidents

---

## Appendix A: Sample Queries

### Get tasks needing reminders (within next 5 minutes)
```sql
SELECT t.*, u.email, u.name, u.timezone
FROM tasks t
JOIN users u ON t.user_id = u.id
WHERE t.completed = false
  AND t.reminder_date IS NOT NULL
  AND t.reminder_time IS NOT NULL
  AND (
    -- One-time reminders
    (t.repeat_type = 'None'
     AND TIMESTAMP WITH TIME ZONE (t.reminder_date || ' ' || t.reminder_time)
         BETWEEN NOW() AND NOW() + INTERVAL '5 minutes')

    -- Daily reminders
    OR (t.repeat_type = 'Daily'
        AND CURRENT_TIME BETWEEN t.reminder_time AND t.reminder_time + INTERVAL '5 minutes')

    -- Weekly/Monthly handled in application logic
    OR (t.repeat_type IN ('Weekly', 'Monthly'))
  )
ORDER BY t.reminder_date, t.reminder_time;
```

### Check for duplicate reminder
```sql
SELECT EXISTS(
  SELECT 1 FROM reminder_log
  WHERE task_id = $1
    AND reminder_datetime = $2
) AS exists;
```

---

## Appendix B: Email Subject Line Strategy

| Importance | Repeat Type | Subject Format | Example |
|------------|-------------|----------------|---------|
| High | Any | 🔴 URGENT: {task_name} | 🔴 URGENT: Submit tax documents |
| Medium | None | 🟡 Reminder: {task_name} | 🟡 Reminder: Team meeting prep |
| Medium | Daily | 🟡 Daily: {task_name} | 🟡 Daily: Morning meditation |
| Low | Weekly | 📅 Weekly: {task_name} | 📅 Weekly: Grocery shopping |
| Low | Monthly | 📆 Monthly: {task_name} | 📆 Monthly: Pay rent |

---

**Document Status**: Draft for Review
**Next Steps**:
1. Review with backend team
2. Validate Gemini API integration approach
3. Confirm email provider selection
4. Create implementation plan and task breakdown
