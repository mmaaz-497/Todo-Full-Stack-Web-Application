"""Notification Service (Phase V)

This service consumes reminder events and sends email notifications.
"""

import asyncio
from aiokafka import AIOKafkaConsumer
import json
from typing import Dict, Any
import os
from fastapi import FastAPI, Request
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


app = FastAPI(title="Notification Service")


class NotificationService:
    """Service to handle sending notifications."""

    def __init__(self):
        self.kafka_bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("SMTP_FROM_EMAIL", "noreply@yourdomain.com")
        self.consumer = None

    async def start_consumer(self):
        """Start the Kafka consumer."""
        self.consumer = AIOKafkaConsumer(
            'reminders',
            bootstrap_servers=self.kafka_bootstrap_servers.split(","),
            group_id='notification-service',
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            enable_auto_commit=True,
            auto_offset_reset='earliest'
        )

        await self.consumer.start()
        print("Notification Service consumer started")

        try:
            async for message in self.consumer:
                await self.handle_reminder(message.value)
        except Exception as e:
            print(f"Error in consumer loop: {e}")
        finally:
            await self.consumer.stop()

    async def send_email(self, to_email: str, subject: str, body: str):
        """Send an email using SMTP."""
        try:
            msg = MIMEMultipart()
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email

            # Add body to email
            msg.attach(MIMEText(body, 'html'))

            # Create SMTP client and send email
            smtp = aiosmtplib.SMTP()
            await smtp.connect(self.smtp_host, self.smtp_port, use_tls=True)
            await smtp.login(self.smtp_username, self.smtp_password)
            await smtp.send_message(msg)
            await smtp.quit()

            print(f"Email sent successfully to {to_email}")
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False

    async def handle_reminder(self, reminder: Dict[str, Any]):
        """Process reminder event and send notification."""
        print(f"Processing reminder for task {reminder.get('task_id')}")

        user_email = reminder.get('user_email')
        if not user_email:
            print("No user email found, skipping notification")
            return

        # Prepare email content
        task_title = reminder.get('title', 'Untitled Task')
        task_description = reminder.get('description', '')
        due_at = reminder.get('due_at', 'Not specified')

        subject = f"Reminder: {task_title}"
        body = f"""
        <html>
        <body>
            <h2>Task Reminder</h2>
            <p>Your task <strong>{task_title}</strong> is due soon!</p>
            <p><strong>Due Date:</strong> {due_at}</p>
            {f'<p><strong>Description:</strong> {task_description}</p>' if task_description else ''}
            <p>This is an automated reminder from your task management system.</p>
        </body>
        </html>
        """

        # Send the email
        success = await self.send_email(user_email, subject, body)

        if success:
            print(f"Reminder sent successfully for task {reminder.get('task_id')}")
        else:
            print(f"Failed to send reminder for task {reminder.get('task_id')}")


# Global service instance
notification_service = NotificationService()


@app.on_event("startup")
async def startup_event():
    """Start the notification service."""
    print("Notification Service started")


@app.post("/dapr/subscribe")
async def dapr_subscribe():
    """Dapr subscription endpoint - tells Dapr what topics to subscribe to."""
    return [
        {
            "pubsubname": "kafka-pubsub",  # This should match your Dapr component name
            "topic": "reminders",
            "route": "/events/reminder"
        }
    ]


@app.post("/events/reminder")
async def handle_reminder_event(request: Request):
    """Handle reminder events from Dapr."""
    event = await request.json()
    reminder = event.get('data', {})

    print(f"Received reminder event via Dapr: {reminder}")

    # Process the reminder
    user_email = reminder.get('user_email')
    if not user_email:
        print("No user email found, skipping notification")
        return {"status": "SKIPPED"}

    # Prepare email content
    task_title = reminder.get('title', 'Untitled Task')
    task_description = reminder.get('description', '')
    due_at = reminder.get('due_at', 'Not specified')

    subject = f"Reminder: {task_title}"
    body = f"""
    <html>
    <body>
        <h2>Task Reminder</h2>
        <p>Your task <strong>{task_title}</strong> is due soon!</p>
        <p><strong>Due Date:</strong> {due_at}</p>
        {f'<p><strong>Description:</strong> {task_description}</p>' if task_description else ''}
        <p>This is an automated reminder from your task management system.</p>
    </body>
    </html>
    """

    # Send the email
    success = await notification_service.send_email(user_email, subject, body)

    if success:
        print(f"Dapr reminder processed successfully for task {reminder.get('task_id')}")
        return {"status": "SUCCESS"}
    else:
        print(f"Failed to process Dapr reminder for task {reminder.get('task_id')}")
        return {"status": "ERROR"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "notification-service"}


# For direct Kafka consumption (non-Dapr)
async def run_consumer():
    """Run the Kafka consumer directly."""
    await notification_service.start_consumer()


if __name__ == "__main__":
    # This would be used if running the service standalone with Kafka
    # For Dapr integration, the service runs as an HTTP server
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)