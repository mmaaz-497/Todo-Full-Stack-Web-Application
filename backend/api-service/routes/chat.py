"""Chat API routes for AI chatbot functionality.

This module provides endpoints for interacting with the AI chatbot,
including conversation management and message handling.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from app.config import settings
from app.database import get_session
from app.models import Conversation, Message  # Import from app.models (models.py file)
from app.auth import verify_token as get_current_user_id  # Use the correct BetterAuth verification
from app.agent import create_agent, run_agent


router = APIRouter(prefix="/api", tags=["Chat"])


# ========== REQUEST/RESPONSE MODELS ==========

class ChatRequest(BaseModel):
    """Chat request schema"""
    conversation_id: Optional[int] = None
    message: str = Field(min_length=1, max_length=5000)


class ToolCall(BaseModel):
    """Tool call result"""
    tool: str
    args: dict
    result: dict


class ChatResponse(BaseModel):
    """Chat response schema"""
    conversation_id: int
    response: str
    tool_calls: List[ToolCall]


class ErrorResponse(BaseModel):
    """Error response schema"""
    error: str
    details: Optional[str] = None


# ========== CHAT ENDPOINT ==========

@router.post("/{user_id}/chat", response_model=ChatResponse)
async def chat(
    user_id: str,
    request: ChatRequest,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session),
):
    """Chat endpoint - Stateless conversation lifecycle

    Constitution Principles:
    - Stateless-First Architecture
    - Database Persistence Guarantee
    - Security and User Isolation

    Implements 7-step stateless flow:
    1. Receive request
    2. Load conversation history
    3. Append user message (in-memory)
    4. Persist user message
    5. Invoke AI agent
    6. Persist assistant message
    7. Return response
    """

    # STEP 1: Verify user_id matches token
    if user_id != current_user_id:
        raise HTTPException(status_code=403, detail="User ID mismatch")

    # STEP 2: Load conversation history
    if request.conversation_id:
        # Load existing conversation
        conversation = session.exec(
            select(Conversation).where(
                Conversation.id == request.conversation_id,
                Conversation.user_id == user_id
            )
        ).first()

        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # Load messages ordered by creation time
        messages = session.exec(
            select(Message)
            .where(Message.conversation_id == request.conversation_id)
            .order_by(Message.created_at.asc())
        ).all()

        history = [{"role": msg.role, "content": msg.content} for msg in messages]
    else:
        # Create new conversation
        conversation = Conversation(user_id=user_id)
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
        history = []

    # STEP 3: Append user message (in-memory only)
    history.append({"role": "user", "content": request.message})

    # STEP 4: Persist user message
    user_message = Message(
        conversation_id=conversation.id,
        user_id=user_id,
        role="user",
        content=request.message,
        created_at=datetime.utcnow()
    )
    session.add(user_message)
    conversation.updated_at = datetime.utcnow()
    session.commit()

    # STEP 5: Invoke AI agent
    try:
        agent = create_agent()  # Stateless - new agent per request
        agent_result = run_agent(
            agent=agent,
            user_message=request.message,
            user_id=user_id,
            conversation_history=history[:-1],  # Exclude current message
            session=session  # Pass database session for tool calls
        )
        response_text = agent_result["response"]
        tool_calls = agent_result.get("tool_calls", [])
    except Exception as e:
        error_msg = str(e)
        error_type = type(e).__name__

        # Check for quota/rate limit errors - provide helpful fallback
        if "ResourceExhausted" in error_type or "quota" in error_msg.lower() or "429" in error_msg:
            # Provide basic task management help as fallback
            msg_lower = request.message.lower()
            if "add" in msg_lower or "create" in msg_lower:
                response_text = "I can help you add tasks! However, the AI service quota is currently exceeded. To add a task manually, use the 'Add Task' button above. \n\nTo fix this: The administrator needs to add a new Gemini API key from a different Google Cloud project."
            elif "list" in msg_lower or "show" in msg_lower or "what" in msg_lower:
                response_text = "I can help you view your tasks! However, the AI service quota is exceeded. You can see all your tasks in the list above.\n\nTo enable AI features: The administrator needs to add a new API key from a different Google Cloud project."
            else:
                response_text = f"I understand you said: '{request.message}'\n\nHowever, the AI service quota has been exceeded. You can still manage tasks using the interface above.\n\n🔧 To fix: The administrator needs to create a new Gemini API key from a DIFFERENT Google Cloud project at https://console.cloud.google.com"
        # Check for invalid API key
        elif "API_KEY_INVALID" in error_msg or "expired" in error_msg.lower() or "invalid" in error_msg.lower():
            response_text = f"I received your message: '{request.message}'\n\n⚠️ The AI service has an API key issue. Please ask the administrator to update the Gemini API key.\n\nYou can still use the task management interface above."
        # Generic error
        else:
            response_text = f"I received: '{request.message}'\n\nBut encountered an issue: {error_msg[:150]}...\n\nPlease try again or use the task interface above."
        tool_calls = []

    # STEP 6: Persist assistant message
    assistant_message = Message(
        conversation_id=conversation.id,
        user_id=user_id,
        role="assistant",
        content=response_text,
        created_at=datetime.utcnow()
    )
    session.add(assistant_message)
    conversation.updated_at = datetime.utcnow()
    session.commit()

    # STEP 7: Return response (clear all in-memory state)
    return ChatResponse(
        conversation_id=conversation.id,
        response=response_text,
        tool_calls=[
            ToolCall(tool=call["tool"], args=call["args"], result=call["result"])
            for call in tool_calls
        ]
    )
