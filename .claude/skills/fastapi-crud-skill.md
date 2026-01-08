# FastAPI CRUD Skill

## Purpose
Reusable implementation patterns for creating RESTful CRUD endpoints with FastAPI and SQLModel.

## Technology Stack
- FastAPI (async/await)
- SQLModel (Pydantic + SQLAlchemy)
- Neon PostgreSQL (serverless)

## Pattern: Full CRUD Endpoint Set

### 1. Database Model
```python
# models.py
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### 2. Pydantic Schemas
```python
# schemas.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    completed: Optional[bool] = None

class TaskResponse(BaseModel):
    id: int
    user_id: str
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

### 3. Database Session Dependency
```python
# database.py
from sqlmodel import create_engine, Session
from contextlib import contextmanager
import os

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, echo=False)

def get_session():
    with Session(engine) as session:
        yield session
```

### 4. CRUD Endpoints
```python
# routes/tasks.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from models import Task
from schemas import TaskCreate, TaskUpdate, TaskResponse
from database import get_session
from auth import get_current_user, User

router = APIRouter(prefix="/api/{user_id}/tasks", tags=["tasks"])

# CREATE
@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    user_id: str,
    task_data: TaskCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Verify user_id matches authenticated user
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Create task associated with authenticated user
    task = Task(**task_data.dict(), user_id=current_user.id)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

# READ (List)
@router.get("", response_model=List[TaskResponse])
async def list_tasks(
    user_id: str,
    status: Optional[str] = "all",  # all, pending, completed
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Build query
    query = select(Task).where(Task.user_id == current_user.id)

    # Apply filters
    if status == "pending":
        query = query.where(Task.completed == False)
    elif status == "completed":
        query = query.where(Task.completed == True)

    tasks = session.exec(query).all()
    return tasks

# READ (Single)
@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    user_id: str,
    task_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    task = session.get(Task, task_id)

    # Check task exists and belongs to user
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")

    return task

# UPDATE
@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    user_id: str,
    task_id: int,
    task_data: TaskUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    task = session.get(Task, task_id)

    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update only provided fields
    update_data = task_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    task.updated_at = datetime.utcnow()
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

# DELETE
@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    user_id: str,
    task_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    task = session.get(Task, task_id)

    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")

    session.delete(task)
    session.commit()
    return None

# PATCH (Toggle completion)
@router.patch("/{task_id}/complete", response_model=TaskResponse)
async def toggle_task_completion(
    user_id: str,
    task_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    task = session.get(Task, task_id)

    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")

    task.completed = not task.completed
    task.updated_at = datetime.utcnow()
    session.add(task)
    session.commit()
    session.refresh(task)
    return task
```

### 5. Main App Setup
```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import tasks
import os

app = FastAPI(title="Todo API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tasks.router)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

## Best Practices

### 1. Error Handling
- Use appropriate HTTP status codes
- Return clear error messages
- Don't leak sensitive information in errors

### 2. Validation
- Use Pydantic models for request validation
- Add field constraints (min/max length, patterns)
- Validate business rules in endpoint logic

### 3. Security
- Always validate user ownership
- Use JWT authentication on all endpoints
- Filter database queries by `current_user.id`

### 4. Performance
- Use async/await for I/O operations
- Add database indexes on foreign keys and frequently queried fields
- Implement pagination for list endpoints

### 5. Testing
```python
# tests/test_tasks.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_task():
    response = client.post(
        "/api/user123/tasks",
        json={"title": "Test Task"},
        headers={"Authorization": "Bearer <token>"}
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Test Task"

def test_list_tasks():
    response = client.get(
        "/api/user123/tasks",
        headers={"Authorization": "Bearer <token>"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

## Environment Variables
```env
# .env
DATABASE_URL=postgresql://user:password@host:5432/dbname
ALLOWED_ORIGINS=http://localhost:3000,https://your-app.vercel.app
BETTER_AUTH_SECRET=your-secret-key-here
```

## Usage in Phases
- **Phase II**: Core CRUD implementation
- **Phase III**: Extended with MCP tool integration
- **Phase IV**: Deployed in Kubernetes
- **Phase V**: Enhanced with event publishing to Kafka

## Checklist
- [ ] All endpoints have JWT authentication
- [ ] User isolation enforced (user_id validation)
- [ ] Input validation with Pydantic
- [ ] Proper error handling and status codes
- [ ] Database indexes on foreign keys
- [ ] CORS configured correctly
- [ ] Environment variables for secrets
- [ ] Unit and integration tests written
