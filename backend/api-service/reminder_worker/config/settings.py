"""Application settings using pydantic-settings.

This module loads and validates all configuration from environment variables.
All settings are type-checked and validated at startup to fail fast if
configuration is invalid.

Usage:
    from config.settings import settings

    print(settings.database_url)
    print(settings.gemini_api_key)
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal


class Settings(BaseSettings):
    """Agent configuration loaded from environment variables.

    All fields are loaded from .env file or environment variables.
    Required fields will raise ValidationError if not set.

    Attributes:
        database_url: PostgreSQL connection string (required)
        gemini_api_key: Gemini API key for AI email generation (required)
        gemini_model: Gemini model name (default: gemini-1.5-flash)
        gemini_base_url: OpenAI-compatible API endpoint for Gemini
        smtp_host: SMTP server hostname (required)
        smtp_port: SMTP server port (default: 587 for STARTTLS)
        smtp_user: SMTP authentication username (required)
        smtp_password: SMTP authentication password (required)
        sender_email: Email address to send reminders from (required)
        sender_name: Display name for email sender
        app_url: Base URL of Todo application for email links (required)
        app_name: Application name shown in emails
        environment: Current environment (development/staging/production)
        polling_interval_minutes: How often to check for reminders
        reminder_lookahead_minutes: Time window for finding due reminders
        email_rate_limit_per_minute: Max emails per minute (rate limiting)
        retry_max_attempts: Max retry attempts for failed operations
        retry_backoff_multiplier: Exponential backoff multiplier for retries
        log_level: Logging verbosity level
        log_format: Log output format (json for production, text for dev)
    """

    # Pydantic settings configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,  # Allow GEMINI_API_KEY or gemini_api_key
        extra="ignore"  # Ignore extra environment variables
    )

    # ============================================================
    # Database Configuration
    # ============================================================
    database_url: str

    # ============================================================
    # Gemini AI Configuration
    # ============================================================
    gemini_api_key: str
    gemini_model: str = "gemini-1.5-flash"
    gemini_base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai/"

    # ============================================================
    # Email Configuration
    # ============================================================
    smtp_host: str
    smtp_port: int = 587
    smtp_user: str
    smtp_password: str
    sender_email: str
    sender_name: str = "Todo Reminder Bot"

    # ============================================================
    # Application Configuration
    # ============================================================
    app_url: str
    app_name: str = "Todo Reminder Agent"
    environment: Literal["development", "staging", "production"] = "development"

    # ============================================================
    # Agent Configuration
    # ============================================================
    polling_interval_minutes: int = 5
    reminder_lookahead_minutes: int = 5
    email_rate_limit_per_minute: int = 100
    retry_max_attempts: int = 3
    retry_backoff_multiplier: int = 2

    # ============================================================
    # Logging Configuration
    # ============================================================
    log_level: str = "INFO"
    log_format: Literal["json", "text"] = "json"

    # ============================================================
    # Helper Properties
    # ============================================================
    @property
    def is_production(self) -> bool:
        """Check if running in production environment.

        Returns:
            bool: True if environment is 'production'
        """
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment.

        Returns:
            bool: True if environment is 'development'
        """
        return self.environment == "development"


# Global settings instance - import this in other modules
settings = Settings()
