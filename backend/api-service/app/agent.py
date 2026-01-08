from openai import OpenAI
from typing import List, Dict, Any, Optional
from app.config import settings
from app.mcp_server import add_task, list_tasks, complete_task, delete_task, update_task
from app.database import get_session
from sqlmodel import Session
import logging
import json

logger = logging.getLogger(__name__)

# Configure OpenAI client
logger.info(f"Configuring OpenAI with API key: {settings.OPENAI_API_KEY[:20]}... and model: {settings.OPENAI_MODEL_NAME}")
client = OpenAI(api_key=settings.OPENAI_API_KEY)


# System prompt for agent
SYSTEM_PROMPT = """You are a helpful task management assistant named TaskBot. You help users manage their todo tasks through natural conversation.

IMPORTANT: The user_id is ALWAYS provided automatically by the system. NEVER ask the user for their user_id. You already have it.

CAPABILITIES:
- Add new tasks
- List tasks (all, pending, or completed)
- Mark tasks as completed
- Delete tasks
- Update task details

BEHAVIOR RULES:
- Detect user intent from natural language
- Call the appropriate function to fulfill requests
- Provide friendly confirmation messages
- Ask clarifying questions when intent is ambiguous
- NEVER ask for user_id - it's provided automatically

RESPONSE STYLE:
- Conversational and friendly
- Confirm actions: "I've added 'Buy milk' to your list!"
- Translate errors into friendly messages
- NEVER expose technical errors to users
"""

# Define OpenAI function schemas
TASK_FUNCTIONS = [
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Create a new task for the user",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The title/name of the task"
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional detailed description of the task"
                    }
                },
                "required": ["title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "Retrieve the user's tasks. Use this to show tasks to the user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["all", "pending", "completed"],
                        "description": "Filter tasks by status. Default is 'all'"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "complete_task",
            "description": "Mark a task as completed",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "The ID of the task to mark as completed"
                    }
                },
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Delete a task permanently",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "The ID of the task to delete"
                    }
                },
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": "Update task title or description",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "The ID of the task to update"
                    },
                    "title": {
                        "type": "string",
                        "description": "New title for the task"
                    },
                    "description": {
                        "type": "string",
                        "description": "New description for the task"
                    }
                },
                "required": ["task_id"]
            }
        }
    }
]


def create_agent(tools: Optional[Dict] = None):
    """Create OpenAI-powered agent with function calling"""
    # Use real tools if not mocked
    if tools is None:
        tools = {
            "add_task": add_task,
            "list_tasks": list_tasks,
            "complete_task": complete_task,
            "delete_task": delete_task,
            "update_task": update_task
        }

    return {
        "client": client,
        "tools": tools,
        "model": settings.OPENAI_MODEL_NAME,
        "temperature": settings.OPENAI_TEMPERATURE,
        "max_tokens": settings.OPENAI_MAX_TOKENS
    }


def run_agent(
    agent: Dict,
    user_message: str,
    user_id: str,
    conversation_history: List[Dict[str, str]],
    session: Session = None
) -> Dict[str, Any]:
    """Execute agent with OpenAI function calling support"""
    client = agent["client"]
    tools = agent["tools"]
    model = agent["model"]

    # Get database session if not provided
    if session is None:
        session = next(get_session())

    try:
        # Build conversation messages
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Add conversation history
        for msg in conversation_history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        # Add current user message
        messages.append({
            "role": "user",
            "content": user_message
        })

        logger.info(f"Sending message to OpenAI: {user_message[:50]}...")

        # Track tool calls
        tool_calls_made = []
        max_iterations = 5  # Prevent infinite loops

        for iteration in range(max_iterations):
            # Call OpenAI API
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                tools=TASK_FUNCTIONS,
                tool_choice="auto",
                temperature=agent["temperature"],
                max_tokens=agent["max_tokens"]
            )

            assistant_message = response.choices[0].message

            # Check if we're done
            if assistant_message.tool_calls is None:
                # No more tool calls, return the response
                final_response = assistant_message.content or "I've processed your request!"
                logger.info(f"Final response: {final_response[:100]}...")

                return {
                    "response": final_response,
                    "tool_calls": tool_calls_made
                }

            # Add assistant message to conversation
            messages.append(assistant_message)

            # Process each tool call
            for tool_call in assistant_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                logger.info(f"Function call: {function_name}({function_args})")

                # Add session and user_id to function arguments
                function_args_with_deps = {
                    "session": session,
                    "user_id": user_id,
                    **function_args
                }

                # Execute the function
                try:
                    result = tools[function_name](**function_args_with_deps)
                    logger.info(f"Function result: {result}")

                    # Record the tool call (exclude session from args)
                    tool_calls_made.append({
                        "tool": function_name,
                        "args": function_args,  # Only the original args, not session/user_id
                        "result": result
                    })

                    # Add function result to messages
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": function_name,
                        "content": json.dumps(result)
                    })

                except Exception as e:
                    logger.error(f"Function execution error: {e}")
                    # Add error to messages
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": function_name,
                        "content": json.dumps({"error": str(e)})
                    })

        # If we hit max iterations, return what we have
        logger.warning(f"Hit max iterations ({max_iterations})")
        return {
            "response": "I've processed your request!",
            "tool_calls": tool_calls_made
        }

    except Exception as e:
        logger.error(f"ERROR in run_agent: {type(e).__name__}: {str(e)}")
        raise
