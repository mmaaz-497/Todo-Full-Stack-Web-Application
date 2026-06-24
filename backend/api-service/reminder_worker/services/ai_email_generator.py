"""Generate personalized reminder emails using Gemini AI."""

from openai import OpenAI
from typing import Optional

from models import Task
from models.email_content import EmailContent
from config.settings import settings
from config.constants import PRIORITY_EMOJIS
from utils.logger import logger
from utils.timezone import format_datetime_for_user


class AIEmailGenerator:
    """Generate email content using Gemini AI with template fallback."""

    def __init__(self):
        """Initialize Gemini client via OpenAI SDK."""
        self.client = OpenAI(
            api_key=settings.gemini_api_key,
            base_url=settings.gemini_base_url
        )

    def generate(
        self,
        task: Task,
        user_name: Optional[str] = None,
        user_timezone: Optional[str] = None
    ) -> EmailContent:
        """Generate personalized reminder email.

        Args:
            task: Task to create reminder for
            user_name: User's display name
            user_timezone: User's timezone

        Returns:
            EmailContent: Subject and body
        """
        try:
            # Generate email body using Gemini
            body = self._generate_body_with_ai(task, user_name, user_timezone)
            subject = self._generate_subject(task)

            return EmailContent(subject=subject, body=body)

        except Exception as e:
            logger.warning(f"⚠️ AI email generation failed: {e}. Using template fallback.")
            return self._fallback_template(task, user_name, user_timezone)

    def _generate_body_with_ai(
        self,
        task: Task,
        user_name: Optional[str],
        user_timezone: Optional[str]
    ) -> str:
        """Generate email body using Gemini API."""
        # Format dates for prompt
        due_date_str = (
            format_datetime_for_user(task.due_date, user_timezone)
            if task.due_date else "No due date set"
        )

        # Build prompt for Gemini
        prompt = f"""You are a professional task reminder assistant. Generate a concise,
motivating reminder email for the following task.

User: {user_name or 'there'}
Task Name: {task.title}
Description: {task.description or 'No description provided'}
Tags: {', '.join(task.tags) if task.tags else 'None'}
Due Date: {due_date_str}
Priority: {task.priority}
Recurrence: {task.recurrence_pattern}

Requirements:
- Professional but warm and friendly tone
- 2-3 sentences maximum
- Mention the task name and due date
- Add a brief motivational closing
- Output ONLY the email body text (no subject line)
- Do NOT include HTML tags - plain text only

Email body:""".strip()

        # Call Gemini API
        response = self.client.chat.completions.create(
            model=settings.gemini_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=200,
            timeout=10
        )

        body_text = response.choices[0].message.content.strip()

        logger.info(
            f"✨ Generated AI email for task {task.id}",
            extra={"task_id": task.id}
        )

        return body_text

    def _generate_subject(self, task: Task) -> str:
        """Generate email subject line with priority emoji."""
        # Get priority emoji
        emoji = PRIORITY_EMOJIS.get(task.priority, "📋")

        # Add recurrence indicator
        if task.recurrence_pattern != "none":
            recurrence = f"[{task.recurrence_pattern.title()}]"
        else:
            recurrence = ""

        return f"{emoji} Reminder {recurrence}: {task.title}".strip()

    def _fallback_template(
        self,
        task: Task,
        user_name: Optional[str],
        user_timezone: Optional[str]
    ) -> EmailContent:
        """Generate email using template (fallback when AI fails)."""
        due_date_str = (
            format_datetime_for_user(task.due_date, user_timezone)
            if task.due_date else "No due date set"
        )

        body = f"""Hi {user_name or 'there'},

This is a friendly reminder about your task: "{task.title}".

Due: {due_date_str}
Priority: {task.priority}

{f'Description: {task.description}' if task.description else ''}

Stay organized and keep up the great work!

Best regards,
{settings.sender_name}""".strip()

        subject = self._generate_subject(task)

        return EmailContent(subject=subject, body=body)
