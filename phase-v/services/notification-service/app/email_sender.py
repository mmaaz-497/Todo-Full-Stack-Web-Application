"""
Email notification sender using SMTP.

Handles:
- SMTP connection and authentication
- Email template rendering
- Email sending with retry logic
"""

import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
from typing import Dict, Optional
import logging

from .dapr_client import dapr_client

logger = logging.getLogger(__name__)

# Email templates directory
TEMPLATES_DIR = Path(__file__).parent / "templates"


class EmailSender:
    """SMTP email sender for task reminder notifications."""

    def __init__(self):
        """Initialize email sender with Jinja2 template environment."""
        self.template_env = Environment(
            loader=FileSystemLoader(TEMPLATES_DIR),
            autoescape=select_autoescape(['html', 'xml'])
        )
        self.smtp_config = None

    async def _load_smtp_config(self) -> bool:
        """
        Load SMTP configuration from Dapr Secrets.

        Returns:
            True if configuration loaded successfully, False otherwise
        """
        if self.smtp_config:
            return True  # Already loaded

        config = await dapr_client.get_smtp_credentials()
        if not config:
            logger.error("Failed to load SMTP credentials from Dapr Secrets")
            return False

        # Validate required fields
        required_fields = ["SMTP_HOST", "SMTP_PORT", "SMTP_USERNAME", "SMTP_PASSWORD", "SMTP_FROM_EMAIL"]
        missing_fields = [field for field in required_fields if field not in config]

        if missing_fields:
            logger.error(f"Missing SMTP configuration fields: {missing_fields}")
            return False

        self.smtp_config = config
        logger.info(f"SMTP configuration loaded: {config['SMTP_HOST']}:{config['SMTP_PORT']}")
        return True

    def render_email_template(
        self,
        template_name: str,
        context: Dict
    ) -> str:
        """
        Render email template with context variables.

        Args:
            template_name: Template filename (e.g., "reminder.html")
            context: Template variables (e.g., {"task_title": "Buy milk"})

        Returns:
            Rendered HTML string
        """
        try:
            template = self.template_env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            logger.error(f"Failed to render template {template_name}: {e}")
            return f"<p>Task Reminder: {context.get('task_title', 'N/A')}</p>"

    async def send_reminder_email(
        self,
        recipient_email: str,
        task_title: str,
        task_description: Optional[str],
        due_date: str,
        task_id: int
    ) -> bool:
        """
        Send task reminder email to user.

        Args:
            recipient_email: User's email address
            task_title: Task title
            task_description: Task description (optional)
            due_date: Task due date (ISO 8601 string)
            task_id: Task ID

        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Load SMTP configuration
            if not await self._load_smtp_config():
                return False

            # Render email template
            html_content = self.render_email_template(
                "reminder.html",
                {
                    "task_title": task_title,
                    "task_description": task_description or "No description",
                    "due_date": due_date,
                    "task_id": task_id
                }
            )

            # Create email message
            message = MIMEMultipart("alternative")
            message["From"] = self.smtp_config["SMTP_FROM_EMAIL"]
            message["To"] = recipient_email
            message["Subject"] = f"⏰ Reminder: {task_title}"

            # Plain text fallback
            text_content = f"""
Task Reminder

Task: {task_title}
Description: {task_description or 'No description'}
Due: {due_date}
Task ID: {task_id}

This is an automated reminder from your Todo AI Chatbot.
            """.strip()

            # Attach both plain text and HTML versions
            message.attach(MIMEText(text_content, "plain"))
            message.attach(MIMEText(html_content, "html"))

            # Send email via SMTP
            smtp_host = self.smtp_config["SMTP_HOST"]
            smtp_port = int(self.smtp_config["SMTP_PORT"])
            smtp_username = self.smtp_config["SMTP_USERNAME"]
            smtp_password = self.smtp_config["SMTP_PASSWORD"]

            async with aiosmtplib.SMTP(hostname=smtp_host, port=smtp_port) as smtp:
                await smtp.starttls()
                await smtp.login(smtp_username, smtp_password)
                await smtp.send_message(message)

            logger.info(
                f"Reminder email sent to {recipient_email} for task {task_id} ({task_title})"
            )
            return True

        except aiosmtplib.SMTPException as e:
            logger.error(f"SMTP error sending email to {recipient_email}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending email to {recipient_email}: {e}")
            return False


# Global email sender instance
email_sender = EmailSender()
