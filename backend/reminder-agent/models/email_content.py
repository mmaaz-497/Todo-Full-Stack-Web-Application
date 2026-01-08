"""Email content models.

Pydantic models for email data structures (not database models).
"""

from pydantic import BaseModel, Field


class EmailContent(BaseModel):
    """Email subject and body content.

    This model represents the output of the AI email generator.
    It's not stored in the database - it's ephemeral data used
    during email composition.

    Attributes:
        subject: Email subject line (max 200 characters)
        body: Email body content (plain text from AI, will be wrapped in HTML template)

    Example:
        email = EmailContent(
            subject="🔴 URGENT: Submit quarterly taxes",
            body="Hey John! Just a quick reminder that your quarterly taxes are due tomorrow..."
        )
    """
    subject: str = Field(..., max_length=200, description="Email subject line")
    body: str = Field(..., description="Email body content (plain text)")

    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "subject": "🔴 URGENT: Submit quarterly taxes",
                "body": "Hey John! Just a quick reminder that your quarterly taxes "
                        "are due tomorrow at 5 PM. You've got this! 💪"
            }
        }
