# Todo Backend API (FastAPI)

RESTful API backend for the Todo Full-Stack Web Application built with FastAPI, SQLModel, and PostgreSQL.

## Features

- ✅ **User Authentication**: JWT token verification with Better Auth integration
- ✅ **Task CRUD Operations**: Complete Create, Read, Update, Delete functionality
- ✅ **Data Isolation**: Strict user data separation with ownership checks
- ✅ **Validation**: Pydantic models for request/response validation
- ✅ **Database ORM**: SQLModel for type-safe database operations
- ✅ **API Documentation**: Auto-generated Swagger/OpenAPI docs
- ✅ **CORS Configuration**: Secure cross-origin resource sharing
- ✅ **Health Checks**: Database connectivity monitoring

## Tech Stack

- **Framework**: FastAPI 0.104.1
- **ORM**: SQLModel 0.0.14
- **Database**: PostgreSQL (Neon Serverless)
- **Authentication**: JWT via python-jose
- **Server**: Uvicorn (ASGI)
- **Python**: 3.13+

## Project Structure

```
backend/
├── main.py              # FastAPI application entry point
├── models.py            # SQLModel database models
├── db.py                # Database connection and session management
├── auth.py              # JWT verification middleware
├── routes/
│   ├── __init__.py
│   ├── tasks.py         # Task CRUD endpoints
│   └── health.py        # Health check endpoint
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_auth_middleware.py
│   └── test_routes_tasks.py
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (not in git)
├── .env.example         # Environment template
└── README.md            # This file
```

## Installation

### Prerequisites

- Python 3.13+
- UV package manager (recommended) or pip
- Neon PostgreSQL database
- Better Auth service running on port 3001

### Setup Steps

1. **Install dependencies**:
   ```bash
   cd backend
   uv pip install -r requirements.txt
   ```

   Or with pip:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables**:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and set:
   ```env
   DATABASE_URL=postgresql://user:pass@host/database?sslmode=require
   BETTER_AUTH_SECRET=your-64-char-hex-secret-here
   CORS_ORIGINS=http://localhost:3000
   ENVIRONMENT=development
   ```

   **IMPORTANT**: `BETTER_AUTH_SECRET` must match the auth-service secret exactly.

3. **Verify database connection**:
   The application will create tables automatically on startup.

## Running the Server

### Development Mode

```bash
cd backend
python main.py
```

Or with Uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Server will start on http://localhost:8000

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### Authentication

All endpoints (except `/health` and `/`) require a JWT token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

### Endpoints

| Method | Endpoint                            | Description                  |
|--------|-------------------------------------|------------------------------|
| GET    | /                                   | API information              |
| GET    | /health                             | Health check                 |
| GET    | /docs                               | Swagger UI documentation     |
| GET    | /api/{user_id}/tasks                | List all user tasks          |
| POST   | /api/{user_id}/tasks                | Create new task              |
| GET    | /api/{user_id}/tasks/{id}           | Get single task              |
| PUT    | /api/{user_id}/tasks/{id}           | Update task                  |
| DELETE | /api/{user_id}/tasks/{id}           | Delete task                  |
| PATCH  | /api/{user_id}/tasks/{id}/complete  | Toggle task completion       |

### Example Requests

**Create Task**:
```bash
curl -X POST http://localhost:8000/api/{user_id}/tasks \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries",
    "description": "Milk, eggs, bread"
  }'
```

**List Tasks**:
```bash
curl http://localhost:8000/api/{user_id}/tasks \
  -H "Authorization: Bearer <token>"
```

**Toggle Complete**:
```bash
curl -X PATCH http://localhost:8000/api/{user_id}/tasks/1/complete \
  -H "Authorization: Bearer <token>"
```

## Database Models

### Task

```python
{
  "id": 1,
  "user_id": "user-uuid-123",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "created_at": "2025-12-19T10:00:00Z",
  "updated_at": "2025-12-19T10:00:00Z"
}
```

**Fields**:
- `id`: Auto-incrementing primary key
- `user_id`: Foreign key to users table (Better Auth)
- `title`: 1-200 characters, required
- `description`: Max 1000 characters, optional
- `completed`: Boolean, default false
- `created_at`: Auto-generated timestamp
- `updated_at`: Auto-updated on modifications

## Security

### Data Isolation

Every API endpoint:
1. Verifies JWT token signature
2. Extracts `user_id` from token claims
3. Compares with path parameter `{user_id}`
4. Filters database queries by `user_id`

**Result**: Users can ONLY access their own data.

### Input Validation

- Pydantic models validate all request data
- SQL injection prevented via SQLModel ORM (no raw SQL)
- XSS protection via JSON responses only
- CORS restricted to configured origins

### Error Handling

- 401 Unauthorized: Missing/invalid JWT token
- 403 Forbidden: User ID mismatch (ownership violation)
- 404 Not Found: Resource doesn't exist
- 400 Bad Request: Validation errors
- 503 Service Unavailable: Database connection failed

## Testing

### Run Tests

```bash
pytest tests/ -v --cov
```

### Test Coverage

Minimum 80% coverage required for:
- Task CRUD operations
- JWT verification
- User data isolation

### Test Files

- `test_models.py`: SQLModel validation tests
- `test_auth_middleware.py`: JWT verification tests
- `test_routes_tasks.py`: API endpoint integration tests

## Configuration

### Environment Variables

| Variable            | Description                          | Example                        |
|---------------------|--------------------------------------|--------------------------------|
| DATABASE_URL        | PostgreSQL connection string         | postgresql://user:pass@host/db |
| BETTER_AUTH_SECRET  | JWT signing/verification secret      | 64-char hex string             |
| CORS_ORIGINS        | Comma-separated allowed origins      | http://localhost:3000          |
| ENVIRONMENT         | Environment name                     | development / production       |

### CORS Configuration

By default, CORS allows requests from:
- http://localhost:3000 (Next.js frontend)

To add more origins:
```env
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
```

## Troubleshooting

### Database Connection Errors

```
Error: getaddrinfo ENOTFOUND ...
```

**Solutions**:
- Verify `DATABASE_URL` is correct
- Check internet connectivity
- Ensure Neon database is accessible
- Verify SSL mode is set (`sslmode=require`)

### JWT Verification Fails

```
401 Unauthorized: Invalid token
```

**Solutions**:
- Verify `BETTER_AUTH_SECRET` matches auth-service
- Check token hasn't expired (7-day default)
- Ensure Bearer token format: `Authorization: Bearer <token>`

### CORS Errors

```
Access to fetch at 'http://localhost:8000' has been blocked by CORS policy
```

**Solutions**:
- Add frontend URL to `CORS_ORIGINS` in `.env`
- Restart backend server after changing CORS config
- Check browser DevTools Network tab for exact error

## API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These provide interactive API documentation and testing interfaces.

## Development Workflow

1. Make changes to source files
2. Server auto-reloads (if using `--reload` flag)
3. Test changes at http://localhost:8000/docs
4. Run tests: `pytest tests/ -v`
5. Verify coverage: `pytest --cov=. tests/`

## Deployment

### Render/Railway/DigitalOcean

1. Push code to GitHub
2. Connect repository to hosting platform
3. Configure environment variables in platform dashboard
4. Deploy with build command: `uv pip install -r requirements.txt`
5. Start command: `uvicorn main:app --host 0.0.0.0 --port 8000`

### Environment Variables (Production)

Set these in your deployment platform:
- DATABASE_URL (use production Neon connection)
- BETTER_AUTH_SECRET (same as auth-service)
- CORS_ORIGINS (include production frontend URL)
- ENVIRONMENT=production

## License

Part of the Todo Full-Stack Web Application (Hackathon Phase II).
