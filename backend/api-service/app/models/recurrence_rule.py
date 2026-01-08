"""Recurrence rule model for recurring tasks."""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class RecurrenceRule(BaseModel):
    """Defines task recurrence pattern."""

    frequency: str = Field(..., description="Recurrence frequency: daily, weekly, monthly")
    interval: int = Field(default=1, ge=1, description="Every N days/weeks/months")
    days_of_week: Optional[List[int]] = Field(
        default=None,
        description="Days of week for weekly recurrence (0=Sunday, 6=Saturday)"
    )
    day_of_month: Optional[int] = Field(
        default=None,
        ge=1,
        le=31,
        description="Day of month for monthly recurrence (1-31)"
    )
    end_date: Optional[datetime] = Field(
        default=None,
        description="Stop generating occurrences after this date"
    )

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "frequency": "daily",
                    "interval": 1
                },
                {
                    "frequency": "weekly",
                    "interval": 1,
                    "days_of_week": [1, 3, 5]
                },
                {
                    "frequency": "monthly",
                    "interval": 1,
                    "day_of_month": 15
                }
            ]
        }
