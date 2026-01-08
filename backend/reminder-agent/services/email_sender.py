"""Send emails via SMTP with retry logic."""

import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from models import Task
from config.settings import settings
from utils.logger import logger


class EmailSender:
    """Send reminder emails via SMTP with automatic retry."""

    @retry(
        stop=stop_after_attempt(settings.retry_max_attempts),
        wait=wait_exponential(multiplier=settings.retry_backoff_multiplier, min=1, max=60),
        retry=retry_if_exception_type(aiosmtplib.SMTPException),
        reraise=True
    )
    async def send(
        self,
        to: str,
        subject: str,
        body: str,
        task: Task,
        user_name: Optional[str] = None
    ) -> bool:
        """Send email with retry logic.

        Automatically retries up to 3 times with exponential backoff on SMTP errors.

        Args:
            to: Recipient email
            subject: Email subject
            body: Email body (plain text from AI)
            task: Task object for template data
            user_name: User's display name

        Returns:
            bool: True if sent successfully
        """
        try:
            # Build HTML email from template
            html_body = EmailSender._build_html_email(body, task, user_name)

            # Create multipart message
            message = MIMEMultipart("alternative")
            message["From"] = f"{settings.sender_name} <{settings.sender_email}>"
            message["To"] = to
            message["Subject"] = subject

            # Add plain text and HTML parts
            text_part = MIMEText(body, "plain")
            html_part = MIMEText(html_body, "html")

            message.attach(text_part)
            message.attach(html_part)

            # Send via SMTP
            await aiosmtplib.send(
                message,
                hostname=settings.smtp_host,
                port=settings.smtp_port,
                username=settings.smtp_user,
                password=settings.smtp_password,
                start_tls=True
            )

            logger.info(
                f"📧 Email sent successfully to {to}",
                extra={"task_id": task.id, "email_to": to}
            )

            return True

        except aiosmtplib.SMTPException as e:
            logger.warning(
                f"⚠️ SMTP error sending to {to}: {e}. Retrying...",
                extra={"task_id": task.id}
            )
            raise  # Retry via tenacity

        except Exception as e:
            logger.error(
                f"❌ Unexpected error sending email: {e}",
                extra={"task_id": task.id}
            )
            return False

    @staticmethod
    def _build_html_email(ai_body: str, task: Task, user_name: Optional[str]) -> str:
        """Build HTML email from template."""
        # Simple HTML template (full template in templates/email_template.html)
        template_str = """
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #4F46E5;">📋 Task Reminder</h2>
        <p>Hi {{ user_name }},</p>
        <div style="background: #f8f9fa; padding: 15px; margin: 15px 0;">
            {{ ai_message }}
        </div>
        <div style="background: #fff; border-left: 4px solid #4F46E5; padding: 15px; margin: 15px 0;">
            <h3>{{ task_name }}</h3>
            <p><strong>Due:</strong> {{ due_date }}</p>
            <p><strong>Priority:</strong> {{ priority }}</p>
            {% if description %}<p><strong>Description:</strong> {{ description }}</p>{% endif %}
        </div>
        <a href="{{ app_url }}/tasks/{{ task_id }}" style="display: inline-block; background: #4F46E5; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px;">View Task</a>
    </div>
</body>
</html>"""

        template = Template(template_str)
        html = template.render(
            user_name=user_name or "there",
            ai_message=ai_body,
            task_name=task.title,
            due_date=task.due_date.strftime("%B %d, %Y") if task.due_date else "No due date",
            priority=task.priority,
            description=task.description,
            app_url=settings.app_url,
            task_id=task.id
        )

        return html
