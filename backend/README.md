# Todo Application - Backend Services

This directory contains all backend services for the Todo Full-Stack Web Application, consolidated into a single deployable unit using Docker Compose.

## Architecture

The backend consists of three microservices:

### 1. **api-service** (FastAPI - Python)
- **Port**: 8000
- **Purpose**: RESTful API for task management
- **Features**:
  - CRUD operations for tasks
  - Advanced features (priorities, tags, due dates, recurring tasks)
  - AI-powered chatbot with OpenAI integration
  - BetterAuth session verification

### 2. **auth-service** (Hono - TypeScript/Node.js)
- **Port**: 3001
- **Purpose**: Authentication and session management
- **Features**:
  - Email/password authentication with Better Auth
  - Session management (7-day expiration)
  - JWT + Bearer token support
  - Rate limiting & security headers

### 3. **reminder-agent** (Python Background Worker)
- **Port**: None (background process)
- **Purpose**: Scheduled email reminders
- **Features**:
  - 5-minute polling interval
  - AI-powered email generation with Google Gemini
  - Support for recurring tasks (daily/weekly/monthly)
  - SMTP email delivery with retry logic

### 4. **postgres** (PostgreSQL Database)
- **Port**: 5432
- **Purpose**: Shared database for all services
- **Version**: PostgreSQL 15 Alpine

## Directory Structure

```
backend/
├── docker-compose.yml          # Orchestrates all services
├── .env                        # Environment variables (create from .env.example)
├── .env.example               # Environment template
├── README.md                  # This file
│
├── api-service/               # FastAPI service
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py
│   ├── auth.py
│   ├── db.py
│   ├── models.py
│   ├── app/
│   ├── routes/
│   └── utils/
│
├── auth-service/              # Hono TypeScript service
│   ├── Dockerfile
│   ├── package.json
│   ├── tsconfig.json
│   ├── src/
│   └── drizzle/
│
└── reminder-agent/            # Python background worker
    ├── Dockerfile
    ├── requirements.txt
    ├── main.py
    ├── config/
    ├── jobs/
    ├── services/
    └── models/
```

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Git (to clone the repository)

### 1. Environment Setup

Create a `.env` file from the example:

```bash
cd backend
cp .env.example .env
```

Edit `.env` and configure your environment variables:

```env
# Database
DB_USER=postgres
DB_PASSWORD=your_secure_password
DB_NAME=todo_db

# Better Auth
BETTER_AUTH_SECRET=your-256-bit-secret-key
BETTER_AUTH_URL=http://localhost:3001

# AI Services
OPENAI_API_KEY=sk-your-openai-key
GEMINI_API_KEY=your-gemini-key

# Email (for reminders)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SENDER_EMAIL=noreply@yourdomain.com

# CORS
CORS_ORIGINS=http://localhost:3000
```

### 2. Development Mode

Start all services in development mode with hot reload:

```bash
docker-compose up
```

Or run in detached mode:

```bash
docker-compose up -d
```

### 3. Production Mode

For production deployment:

```bash
export BUILD_TARGET=prod
export ENVIRONMENT=production
export NODE_ENV=production
docker-compose up -d --build
```

## Service Management

### View Service Status

```bash
docker-compose ps
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api-service
docker-compose logs -f auth-service
docker-compose logs -f reminder-agent
docker-compose logs -f postgres
```

### Stop Services

```bash
docker-compose down
```

### Stop and Remove Volumes (Clean Start)

```bash
docker-compose down -v
```

### Rebuild Services

```bash
docker-compose up --build
```

### Restart a Specific Service

```bash
docker-compose restart api-service
```

## Health Checks

Once services are running, verify they're healthy:

### PostgreSQL
```bash
docker-compose exec postgres pg_isready -U postgres
```

### Auth Service
```bash
curl http://localhost:3001/health
```

### API Service
```bash
curl http://localhost:8000/health
```

### Reminder Agent
```bash
docker-compose logs reminder-agent | grep "Agent started"
```

## API Endpoints

### API Service (Port 8000)
- **Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Tasks API**: http://localhost:8000/api/{user_id}/tasks
- **Chat API**: http://localhost:8000/api/{user_id}/chat

### Auth Service (Port 3001)
- **Health Check**: http://localhost:3001/health
- **Sign Up**: POST http://localhost:3001/api/auth/signup/email
- **Sign In**: POST http://localhost:3001/api/auth/signin/email
- **Get Session**: GET http://localhost:3001/api/auth/session

## Database Access

### Connect to PostgreSQL

```bash
docker-compose exec postgres psql -U postgres -d todo_db
```

### Run Database Migrations

#### Auth Service Migrations (Drizzle)
```bash
docker-compose exec auth-service npm run migrate:push
```

#### API Service Migrations (Alembic)
```bash
docker-compose exec api-service alembic upgrade head
```

## Troubleshooting

### Services Won't Start

1. Check if ports are already in use:
```bash
netstat -ano | findstr :3001
netstat -ano | findstr :8000
netstat -ano | findstr :5432
```

2. Check Docker logs:
```bash
docker-compose logs
```

### Database Connection Issues

1. Verify PostgreSQL is healthy:
```bash
docker-compose ps postgres
```

2. Check database connectivity:
```bash
docker-compose exec postgres pg_isready
```

### Auth Service Not Responding

1. Check if it's waiting for database:
```bash
docker-compose logs auth-service
```

2. Verify database migrations ran:
```bash
docker-compose exec auth-service npm run migrate:push
```

### API Service Can't Reach Auth Service

1. Verify both services are on the same network:
```bash
docker network inspect backend_backend-network
```

2. Test internal connectivity:
```bash
docker-compose exec api-service curl http://auth-service:3001/health
```

## Development Tips

### Hot Reload

All services support hot reload in development mode:
- **api-service**: Changes to Python files auto-reload (uvicorn --reload)
- **auth-service**: Changes to TypeScript files auto-reload (tsx watch)
- **reminder-agent**: Restart required (Python worker)

### Running Tests

```bash
# API Service tests
docker-compose exec api-service pytest

# Auth Service tests
docker-compose exec auth-service npm test
```

### Accessing Service Shells

```bash
# API Service (Python)
docker-compose exec api-service bash

# Auth Service (Node.js)
docker-compose exec auth-service sh

# Reminder Agent (Python)
docker-compose exec reminder-agent bash

# PostgreSQL
docker-compose exec postgres bash
```

## Production Deployment

### On VPS/Cloud

1. Clone repository:
```bash
git clone <your-repo>
cd backend
```

2. Configure environment:
```bash
cp .env.example .env
nano .env  # Edit with production values
```

3. Deploy:
```bash
export BUILD_TARGET=prod
export ENVIRONMENT=production
docker-compose up -d --build
```

4. Verify:
```bash
docker-compose ps
docker-compose logs -f
```

### Environment Variables for Production

Update these in `.env` for production:

```env
# Use strong passwords
DB_PASSWORD=<strong-random-password>
BETTER_AUTH_SECRET=<256-bit-secret>

# Production URLs
BETTER_AUTH_URL=https://your-domain.com
CORS_ORIGINS=https://your-frontend-domain.com

# Build targets
BUILD_TARGET=prod
ENVIRONMENT=production
NODE_ENV=production
```

## Network Architecture

All services communicate via the `backend-network` Docker network:

```
┌─────────────────────────────────────────┐
│         backend-network                 │
│                                         │
│  ┌──────────┐    ┌──────────────┐     │
│  │ postgres │◄───│ auth-service │     │
│  │  :5432   │    │    :3001     │     │
│  └────▲─────┘    └──────▲───────┘     │
│       │                 │              │
│       │  ┌──────────────┴──────┐      │
│       ├──│   api-service       │      │
│       │  │      :8000          │      │
│       │  └─────────────────────┘      │
│       │                               │
│       │  ┌──────────────────┐         │
│       └──│ reminder-agent   │         │
│          │   (no port)      │         │
│          └──────────────────┘         │
└─────────────────────────────────────────┘
```

- API service calls auth-service: `http://auth-service:3001`
- All services connect to database: `postgresql://user:pass@postgres:5432/todo_db`

## Support

For issues or questions:
1. Check the logs: `docker-compose logs -f <service-name>`
2. Review this README
3. Check individual service READMEs in their directories

## License

[Your License Here]
