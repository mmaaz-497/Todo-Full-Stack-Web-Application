"""User model for reminder agent.

This model mirrors the Better Auth user table to allow the reminder agent
to query user information (email, name) for sending reminders.

The user table is managed by Better Auth (auth-service), but the reminder
agent needs read-only access to fetch user details.
"""

from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class User(SQLModel, table=True):
    """User entity from Better Auth.

    This is a READ-ONLY model for the reminder agent. The user table
    is owned and managed by the auth-service. The reminder agent only
    reads from this table to get user email addresses and names.

    Attributes:
        id: User ID (primary key, managed by Better Auth)
        email: User email address (required, unique)
        emailVerified: Whether email has been verified
        name: User display name (optional)
        createdAt: Account creation timestamp
        updatedAt: Last update timestamp
        image: User profile image URL (optional)
    """
    __tablename__ = "user"

    # Primary key
    id: str = Field(primary_key=True)

    # Core fields
    email: str = Field(nullable=False)
    emailVerified: bool = Field(default=False, nullable=False)
    name: Optional[str] = Field(default=None)

    # Timestamps
    createdAt: datetime = Field(nullable=False)
    updatedAt: datetime = Field(nullable=False)

    # Optional fields
    image: Optional[str] = Field(default=None)
