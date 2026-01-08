"""Priority enum for task priority levels."""
from enum import Enum


class Priority(str, Enum):
    """Task priority levels."""

    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"

    def __str__(self) -> str:
        return self.value
