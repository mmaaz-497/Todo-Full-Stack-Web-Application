from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from app.config import settings
from app.database import get_session
from app.models import Conversation, Message
from app.auth import verify_token
from app.agent import create_agent, run_agent


# FastAPI app initialization
app = FastAPI(
    title="Todo AI Chatbot API",
    version="1.0.0",
    docs_url="/docs"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_methods=["POST", "GET"],
    allow_headers=["Authorization", "Content-Type"],
)


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

@app.post("/api/{user_id}/chat", response_model=ChatResponse)
async def chat(
    user_id: str,
    request: ChatRequest,
    authenticated_user_id: str = Depends(verify_token),
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
    if user_id != authenticated_user_id:
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
    agent = create_agent()  # Stateless - new agent per request
    agent_result = run_agent(
        agent=agent,
        user_message=request.message,
        user_id=user_id,
        conversation_history=history[:-1]  # Exclude current message
    )
    
    response_text = agent_result["response"]
    tool_calls = agent_result.get("tool_calls", [])
    
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


# ========== HEALTH CHECK ==========

@app.get("/health")
async def health_check(session: Session = Depends(get_session)):
    """Health check endpoint"""
    try:
        # Check database connectivity
        session.exec(select(1)).first()
        
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }, 503


@app.get("/debug/env")
async def debug_env():
    """Debug endpoint to check environment settings"""
    return {
        "ENVIRONMENT": settings.ENVIRONMENT,
        "AUTH_ISSUER": settings.AUTH_ISSUER[:20] + "..." if len(settings.AUTH_ISSUER) > 20 else settings.AUTH_ISSUER,
        "DATABASE_URL": settings.DATABASE_URL[:20] + "...",
    }


# ========== ERROR HANDLERS ==========

@app.exception_handler(Exception)
async def generic_error_handler(request, exc):
    """Handle all unhandled exceptions"""
    # Log error with context
    print(f"Unhandled error: {exc}")
    
    return {
        "error": "Internal server error"
    }, 500
