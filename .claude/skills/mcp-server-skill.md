# MCP Server Skill

## Purpose
Build Model Context Protocol (MCP) servers that expose task operations as tools for AI agents (Phase III).

## Technology Stack
- Official MCP SDK (Python)
- FastAPI integration
- OpenAI Agents SDK

## Architecture
```
┌─────────────────┐
│  OpenAI Agent   │
│  (Chat Logic)   │
└────────┬────────┘
         │ uses tools
         ▼
┌─────────────────┐
│   MCP Server    │
│  (Tool Defs)    │
└────────┬────────┘
         │ calls
         ▼
┌─────────────────┐
│  Database       │
│  (Tasks, etc.)  │
└─────────────────┘
```

## Pattern: MCP Server Implementation

### 1. Install Dependencies
```bash
pip install mcp
```

### 2. MCP Server Structure
```python
# mcp_server.py
from mcp.server import Server
from mcp.types import Tool, TextContent
from sqlmodel import Session, select
from models import Task
from database import get_session
from typing import Optional, List
import json

# Create MCP server instance
mcp_server = Server("todo-mcp-server")

# Tool 1: Add Task
@mcp_server.tool()
async def add_task(
    user_id: str,
    title: str,
    description: Optional[str] = None
) -> str:
    """
    Create a new task for the user.

    Args:
        user_id: The authenticated user's ID
        title: Task title (required)
        description: Optional task description

    Returns:
        JSON string with task details
    """
    with Session(engine) as session:
        task = Task(
            user_id=user_id,
            title=title,
            description=description,
            completed=False
        )
        session.add(task)
        session.commit()
        session.refresh(task)

        return json.dumps({
            "task_id": task.id,
            "status": "created",
            "title": task.title
        })

# Tool 2: List Tasks
@mcp_server.tool()
async def list_tasks(
    user_id: str,
    status: str = "all"
) -> str:
    """
    Retrieve tasks for the user.

    Args:
        user_id: The authenticated user's ID
        status: Filter by status ("all", "pending", "completed")

    Returns:
        JSON string with array of tasks
    """
    with Session(engine) as session:
        query = select(Task).where(Task.user_id == user_id)

        if status == "pending":
            query = query.where(Task.completed == False)
        elif status == "completed":
            query = query.where(Task.completed == True)

        tasks = session.exec(query).all()

        return json.dumps([
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "created_at": task.created_at.isoformat()
            }
            for task in tasks
        ])

# Tool 3: Complete Task
@mcp_server.tool()
async def complete_task(
    user_id: str,
    task_id: int
) -> str:
    """
    Mark a task as complete.

    Args:
        user_id: The authenticated user's ID
        task_id: The task ID to complete

    Returns:
        JSON string with updated task details
    """
    with Session(engine) as session:
        task = session.get(Task, task_id)

        if not task or task.user_id != user_id:
            return json.dumps({
                "error": "Task not found",
                "task_id": task_id
            })

        task.completed = True
        task.updated_at = datetime.utcnow()
        session.add(task)
        session.commit()
        session.refresh(task)

        return json.dumps({
            "task_id": task.id,
            "status": "completed",
            "title": task.title
        })

# Tool 4: Delete Task
@mcp_server.tool()
async def delete_task(
    user_id: str,
    task_id: int
) -> str:
    """
    Remove a task from the list.

    Args:
        user_id: The authenticated user's ID
        task_id: The task ID to delete

    Returns:
        JSON string with deletion confirmation
    """
    with Session(engine) as session:
        task = session.get(Task, task_id)

        if not task or task.user_id != user_id:
            return json.dumps({
                "error": "Task not found",
                "task_id": task_id
            })

        title = task.title
        session.delete(task)
        session.commit()

        return json.dumps({
            "task_id": task_id,
            "status": "deleted",
            "title": title
        })

# Tool 5: Update Task
@mcp_server.tool()
async def update_task(
    user_id: str,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None
) -> str:
    """
    Modify task title or description.

    Args:
        user_id: The authenticated user's ID
        task_id: The task ID to update
        title: New title (optional)
        description: New description (optional)

    Returns:
        JSON string with updated task details
    """
    with Session(engine) as session:
        task = session.get(Task, task_id)

        if not task or task.user_id != user_id:
            return json.dumps({
                "error": "Task not found",
                "task_id": task_id
            })

        if title is not None:
            task.title = title
        if description is not None:
            task.description = description

        task.updated_at = datetime.utcnow()
        session.add(task)
        session.commit()
        session.refresh(task)

        return json.dumps({
            "task_id": task.id,
            "status": "updated",
            "title": task.title
        })
```

### 3. Integrate with OpenAI Agents SDK
```python
# chatbot.py
from openai import OpenAI
from mcp_server import mcp_server
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Convert MCP tools to OpenAI function format
def get_openai_tools():
    """Convert MCP tools to OpenAI Agents SDK format"""
    return [
        {
            "type": "function",
            "function": {
                "name": "add_task",
                "description": "Create a new task for the user",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string"},
                        "title": {"type": "string"},
                        "description": {"type": "string"}
                    },
                    "required": ["user_id", "title"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "list_tasks",
                "description": "Retrieve tasks from the list",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string"},
                        "status": {
                            "type": "string",
                            "enum": ["all", "pending", "completed"]
                        }
                    },
                    "required": ["user_id"]
                }
            }
        },
        # ... other tools
    ]

async def run_agent(user_id: str, user_message: str, conversation_history: List):
    """
    Run the OpenAI agent with MCP tools
    """
    # Add user message to history
    messages = conversation_history + [
        {"role": "user", "content": user_message}
    ]

    # Call OpenAI with tools
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=get_openai_tools(),
        tool_choice="auto"
    )

    assistant_message = response.choices[0].message

    # Handle tool calls
    if assistant_message.tool_calls:
        for tool_call in assistant_message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            # Add user_id to all tool calls
            function_args["user_id"] = user_id

            # Execute MCP tool
            if function_name == "add_task":
                result = await add_task(**function_args)
            elif function_name == "list_tasks":
                result = await list_tasks(**function_args)
            elif function_name == "complete_task":
                result = await complete_task(**function_args)
            elif function_name == "delete_task":
                result = await delete_task(**function_args)
            elif function_name == "update_task":
                result = await update_task(**function_args)

            # Add tool result to messages
            messages.append({
                "role": "assistant",
                "content": None,
                "tool_calls": [tool_call]
            })
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result
            })

        # Get final response after tool execution
        final_response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )

        return final_response.choices[0].message.content

    return assistant_message.content
```

### 4. Stateless Chat Endpoint
```python
# routes/chat.py
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from auth import get_current_user, User
from models import Conversation, Message
from chatbot import run_agent
from database import get_session
from sqlmodel import Session, select

router = APIRouter(prefix="/api/{user_id}/chat", tags=["chat"])

class ChatRequest(BaseModel):
    conversation_id: Optional[int] = None
    message: str

class ChatResponse(BaseModel):
    conversation_id: int
    response: str
    tool_calls: List[str] = []

@router.post("", response_model=ChatResponse)
async def chat(
    user_id: str,
    request: ChatRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Stateless chat endpoint:
    1. Fetch conversation history from DB
    2. Run agent with MCP tools
    3. Store user message and assistant response
    4. Return response (server holds no state)
    """
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Get or create conversation
    if request.conversation_id:
        conversation = session.get(Conversation, request.conversation_id)
        if not conversation or conversation.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        conversation = Conversation(user_id=current_user.id)
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

    # Fetch conversation history
    messages_query = select(Message).where(
        Message.conversation_id == conversation.id
    ).order_by(Message.created_at)
    history = session.exec(messages_query).all()

    # Build message array for agent
    message_array = [
        {"role": msg.role, "content": msg.content}
        for msg in history
    ]

    # Store user message
    user_message = Message(
        conversation_id=conversation.id,
        user_id=current_user.id,
        role="user",
        content=request.message
    )
    session.add(user_message)
    session.commit()

    # Run agent with MCP tools
    response_text = await run_agent(
        user_id=current_user.id,
        user_message=request.message,
        conversation_history=message_array
    )

    # Store assistant response
    assistant_message = Message(
        conversation_id=conversation.id,
        user_id=current_user.id,
        role="assistant",
        content=response_text
    )
    session.add(assistant_message)
    session.commit()

    return ChatResponse(
        conversation_id=conversation.id,
        response=response_text,
        tool_calls=[]  # Could track which tools were called
    )
```

## Best Practices

### 1. Tool Design
- Each tool should be atomic and focused
- Always include `user_id` parameter for isolation
- Return structured JSON strings
- Include error handling in tool responses

### 2. Security
- Validate `user_id` in every MCP tool
- Never trust tool arguments without validation
- Filter database queries by `user_id`

### 3. Stateless Architecture
- Server doesn't hold conversation state in memory
- All state persisted to database
- Conversation history fetched on each request
- Enables horizontal scaling

### 4. Testing
```python
# Test MCP tools directly
import asyncio

async def test_add_task():
    result = await add_task(
        user_id="test_user",
        title="Test Task",
        description="Testing MCP tool"
    )
    data = json.loads(result)
    assert data["status"] == "created"
    print(f"Created task: {data}")

asyncio.run(test_add_task())
```

## Database Models for Phase III
```python
# Add to models.py
class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    role: str = Field()  # "user" or "assistant"
    content: str = Field()
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

## Agent Behavior Patterns
```python
# System prompt for the agent
SYSTEM_PROMPT = """
You are a helpful assistant for managing todo tasks. You can:
- Add tasks when users mention creating or remembering something
- List tasks when users ask to see or show their tasks
- Mark tasks complete when users say done or finished
- Delete tasks when users say remove or cancel
- Update tasks when users want to change details

Always confirm actions with a friendly response.
"""
```

## Checklist
- [ ] MCP server with all 5 tools (add, list, complete, delete, update)
- [ ] Each tool validates user_id
- [ ] Tools return structured JSON
- [ ] OpenAI Agents SDK integration
- [ ] Stateless chat endpoint
- [ ] Conversation and Message models
- [ ] History fetched from database
- [ ] Tool calls logged (optional)
- [ ] Natural language understanding tested

## Usage in Phase III
This skill is the core of Phase III, enabling AI-powered task management through natural language.
