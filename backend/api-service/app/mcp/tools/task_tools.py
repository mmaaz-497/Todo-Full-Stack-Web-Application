"""MCP Tools for Advanced Task Management Features (Phase V)

This module implements MCP tools for:
- Recurring tasks management
- Priority system
- Tags system
- Advanced search, filter, and sort
- Event publishing via Dapr
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlmodel import select
from uuid import uuid4
from app.models import Task, TaskCreate, TaskUpdate
from app.database import get_session
from app.dapr_client import DaprClient
import json


class TaskTools:
    """MCP Tools for advanced task management operations."""

    def __init__(self):
        self.dapr_client = DaprClient()

    async def create_recurring_task(
        self,
        title: str,
        description: str = "",
        recurrence_pattern: str = "daily",  # daily, weekly, monthly
        start_date: str = None,
        end_date: str = None,
        priority: str = "medium",
        tags: List[str] = None
    ) -> Dict[str, Any]:
        """
        Create a recurring task

        Args:
            title: Task title
            description: Task description
            recurrence_pattern: How often task repeats (daily/weekly/monthly)
            start_date: When to start (ISO format)
            end_date: When to stop recurring (optional)
            priority: Task priority (low/medium/high/urgent)
            tags: List of tags for the task
        """
        if tags is None:
            tags = []

        if recurrence_pattern not in ["daily", "weekly", "monthly"]:
            return {"error": "Recurrence pattern must be daily, weekly, or monthly"}

        if priority not in ["low", "medium", "high", "urgent"]:
            return {"error": "Priority must be low, medium, high, or urgent"}

        start = datetime.fromisoformat(start_date) if start_date else datetime.now()
        end = datetime.fromisoformat(end_date) if end_date else None

        # Create the recurring task
        task_data = TaskCreate(
            title=title,
            description=description,
            priority=priority,
            tags=tags,
            due_date=start,
            recurrence_pattern=recurrence_pattern
        )

        async with get_session() as session:
            task = Task(
                title=task_data.title,
                description=task_data.description,
                priority=task_data.priority,
                tags=task_data.tags,
                due_date=task_data.due_date,
                recurrence_pattern=task_data.recurrence_pattern,
                is_recurring=True,
                recurrence_end_date=end
            )
            session.add(task)
            await session.commit()
            await session.refresh(task)

        # Publish event to Kafka via Dapr
        await self._publish_task_event("created", task, "recurring-task-creator")

        return {
            "message": f"Created recurring task: {title} ({recurrence_pattern})",
            "task": task.dict()
        }

    async def set_task_priority(self, task_id: int, priority: str) -> Dict[str, Any]:
        """
        Set task priority

        Args:
            task_id: Task ID
            priority: Priority level (high/medium/low/urgent)
        """
        if priority not in ["high", "medium", "low", "urgent"]:
            return {"error": "Priority must be high, medium, low, or urgent"}

        async with get_session() as session:
            task = await session.get(Task, task_id)
            if not task:
                return {"error": f"Task with ID {task_id} not found"}

            old_priority = task.priority
            task.priority = priority
            await session.commit()
            await session.refresh(task)

        # Publish event to Kafka via Dapr
        await self._publish_task_event("updated", task, "priority-setter",
                                     metadata={"old_priority": old_priority, "new_priority": priority})

        return {
            "message": f"Set priority to {priority}",
            "task": task.dict()
        }

    async def add_tags_to_task(self, task_id: int, tags: List[str]) -> Dict[str, Any]:
        """
        Add tags to a task

        Args:
            task_id: Task ID
            tags: List of tag names (e.g., ["work", "urgent"])
        """
        async with get_session() as session:
            task = await session.get(Task, task_id)
            if not task:
                return {"error": f"Task with ID {task_id} not found"}

            # Add new tags, avoiding duplicates
            current_tags = set(task.tags)
            new_tags = set(tags)
            all_tags = list(current_tags.union(new_tags))

            task.tags = all_tags
            await session.commit()
            await session.refresh(task)

        # Publish event to Kafka via Dapr
        await self._publish_task_event("updated", task, "tag-adder",
                                     metadata={"added_tags": tags})

        return {
            "message": f"Added tags: {', '.join(tags)}",
            "task": task.dict()
        }

    async def remove_tag_from_task(self, task_id: int, tag_name: str) -> Dict[str, Any]:
        """
        Remove a tag from a task

        Args:
            task_id: Task ID
            tag_name: Tag name to remove
        """
        async with get_session() as session:
            task = await session.get(Task, task_id)
            if not task:
                return {"error": f"Task with ID {task_id} not found"}

            # Remove the tag
            current_tags = set(task.tags)
            current_tags.discard(tag_name)
            task.tags = list(current_tags)
            await session.commit()
            await session.refresh(task)

        # Publish event to Kafka via Dapr
        await self._publish_task_event("updated", task, "tag-remover",
                                     metadata={"removed_tag": tag_name})

        return {
            "message": f"Removed tag: {tag_name}",
            "task": task.dict()
        }

    async def search_tasks(
        self,
        query: str = None,
        status: str = None,
        priority: str = None,
        tags: List[str] = None,
        due_before: str = None,
        due_after: str = None,
        sort_by: str = "created_at",  # created_at, due_at, priority, title
        sort_order: str = "desc"  # asc, desc
    ) -> Dict[str, Any]:
        """
        Search and filter tasks with advanced options
        """
        if tags is None:
            tags = []

        async with get_session() as session:
            statement = select(Task)

            # Apply filters
            if query:
                # This is a simplified text search - in production you'd want full-text search
                statement = statement.where(Task.title.contains(query) | Task.description.contains(query))

            if status:
                statement = statement.where(Task.status == status)

            if priority:
                statement = statement.where(Task.priority == priority)

            if tags:
                # For PostgreSQL arrays, we use overlap operator
                for tag in tags:
                    statement = statement.where(Task.tags.any(tag))

            if due_before:
                due_before_dt = datetime.fromisoformat(due_before)
                statement = statement.where(Task.due_date <= due_before_dt)

            if due_after:
                due_after_dt = datetime.fromisoformat(due_after)
                statement = statement.where(Task.due_date >= due_after_dt)

            # Apply sorting
            if sort_by == "created_at":
                if sort_order == "asc":
                    statement = statement.order_by(Task.created_at.asc())
                else:
                    statement = statement.order_by(Task.created_at.desc())
            elif sort_by == "due_at":  # alias for due_date
                if sort_order == "asc":
                    statement = statement.order_by(Task.due_date.asc())
                else:
                    statement = statement.order_by(Task.due_date.desc())
            elif sort_by == "priority":
                if sort_order == "asc":
                    statement = statement.order_by(Task.priority.asc())
                else:
                    statement = statement.order_by(Task.priority.desc())
            elif sort_by == "title":
                if sort_order == "asc":
                    statement = statement.order_by(Task.title.asc())
                else:
                    statement = statement.order_by(Task.title.desc())

            results = await session.exec(statement)
            tasks = results.all()

        return {
            "count": len(tasks),
            "tasks": [task.dict() for task in tasks]
        }

    async def _publish_task_event(
        self,
        event_type: str,
        task: Task,
        source: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Publish task event to Kafka via Dapr
        """
        if metadata is None:
            metadata = {}

        event = {
            "event_id": str(uuid4()),
            "event_type": event_type,
            "task_id": task.id,
            "task_data": task.dict(),
            "user_id": getattr(task, 'user_id', 'unknown'),  # Assuming user_id exists
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": {
                "source": source,
                **metadata
            }
        }

        # Publish to Dapr pubsub component
        try:
            await self.dapr_client.publish_event(
                pubsub_name="kafka-pubsub",
                topic="task-events",
                data=event
            )
        except Exception as e:
            print(f"Error publishing event: {e}")
            # In production, you might want to implement retry logic or dead-letter queue


# Create global instance
task_tools = TaskTools()

# MCP Tool definitions
def mcp_tool(func):
    """Decorator to mark functions as MCP tools"""
    func.is_mcp_tool = True
    return func


@mcp_tool
async def create_recurring_task(
    title: str,
    description: str = "",
    recurrence_pattern: str = "daily",  # daily, weekly, monthly
    start_date: str = None,
    end_date: str = None
) -> Dict[str, Any]:
    """
    Create a recurring task

    Args:
        title: Task title
        description: Task description
        recurrence_pattern: How often task repeats (daily/weekly/monthly)
        start_date: When to start (ISO format)
        end_date: When to stop recurring (optional)
    """
    return await task_tools.create_recurring_task(
        title=title,
        description=description,
        recurrence_pattern=recurrence_pattern,
        start_date=start_date,
        end_date=end_date
    )


@mcp_tool
async def set_task_priority(task_id: int, priority: str) -> Dict[str, Any]:
    """
    Set task priority

    Args:
        task_id: Task ID
        priority: Priority level (high/medium/low/urgent)
    """
    return await task_tools.set_task_priority(task_id, priority)


@mcp_tool
async def add_tags_to_task(task_id: int, tags: List[str]) -> Dict[str, Any]:
    """
    Add tags to a task

    Args:
        task_id: Task ID
        tags: List of tag names (e.g., ["work", "urgent"])
    """
    return await task_tools.add_tags_to_task(task_id, tags)


@mcp_tool
async def remove_tag_from_task(task_id: int, tag_name: str) -> Dict[str, Any]:
    """
    Remove a tag from a task

    Args:
        task_id: Task ID
        tag_name: Tag name to remove
    """
    return await task_tools.remove_tag_from_task(task_id, tag_name)


@mcp_tool
async def search_tasks(
    query: str = None,
    status: str = None,
    priority: str = None,
    tags: List[str] = None,
    due_before: str = None,
    due_after: str = None,
    sort_by: str = "created_at",  # created_at, due_at, priority, title
    sort_order: str = "desc"  # asc, desc
) -> Dict[str, Any]:
    """
    Search and filter tasks with advanced options
    """
    return await task_tools.search_tasks(
        query=query,
        status=status,
        priority=priority,
        tags=tags,
        due_before=due_before,
        due_after=due_after,
        sort_by=sort_by,
        sort_order=sort_order
    )