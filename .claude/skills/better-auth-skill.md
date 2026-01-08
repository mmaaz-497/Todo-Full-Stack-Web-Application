# Better Auth Integration Skill

## Purpose
Implement authentication using Better Auth with JWT tokens for securing the Todo application (Phase II+).

## Technology Stack
- Better Auth (JavaScript/TypeScript - Frontend)
- JWT validation (Python - Backend)
- Shared secret for token signing/verification

## Architecture
```
┌──────────────┐                    ┌──────────────┐
│   Frontend   │                    │   Backend    │
│  (Next.js)   │                    │  (FastAPI)   │
│              │                    │              │
│ Better Auth  │                    │ JWT Verify   │
│ (Issues JWT) │────────────────────▶ (Validates)  │
│              │  Authorization:     │              │
│              │  Bearer <token>     │              │
└──────────────┘                    └──────────────┘
        │                                   │
        │ BETTER_AUTH_SECRET (shared)      │
        └───────────────────────────────────┘
```

## Frontend Setup (Next.js)

### 1. Install Dependencies
```bash
npm install better-auth
```

### 2. Create Better Auth Instance
```typescript
// lib/auth.ts
import { BetterAuth } from "better-auth";
import { jwtPlugin } from "better-auth/plugins";

export const auth = BetterAuth({
  secret: process.env.BETTER_AUTH_SECRET!,
  database: {
    url: process.env.DATABASE_URL!,
    type: "postgres"
  },
  plugins: [
    jwtPlugin({
      // Enable JWT token generation
      enabled: true,
      // Token expires in 7 days
      expiresIn: "7d"
    })
  ],
  session: {
    cookieName: "todo-session",
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24 // Update every day
  }
});
```

### 3. Create Auth API Route
```typescript
// app/api/auth/[...all]/route.ts
import { auth } from "@/lib/auth";

export const { GET, POST } = auth.handler;
```

### 4. Create Auth Context
```typescript
// components/providers/auth-provider.tsx
"use client";

import { createContext, useContext, useEffect, useState } from "react";
import { auth } from "@/lib/auth";

interface User {
  id: string;
  email: string;
  name: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string, name: string) => Promise<void>;
  signOut: () => Promise<void>;
  getToken: () => Promise<string | null>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check session on mount
    checkSession();
  }, []);

  async function checkSession() {
    try {
      const session = await auth.getSession();
      setUser(session?.user || null);
    } catch (error) {
      console.error("Session check failed:", error);
    } finally {
      setLoading(false);
    }
  }

  async function signIn(email: string, password: string) {
    const result = await auth.signIn.email({
      email,
      password
    });

    if (result.error) {
      throw new Error(result.error.message);
    }

    setUser(result.data.user);
  }

  async function signUp(email: string, password: string, name: string) {
    const result = await auth.signUp.email({
      email,
      password,
      name
    });

    if (result.error) {
      throw new Error(result.error.message);
    }

    setUser(result.data.user);
  }

  async function signOut() {
    await auth.signOut();
    setUser(null);
  }

  async function getToken(): Promise<string | null> {
    try {
      const session = await auth.getSession();
      return session?.token || null;
    } catch (error) {
      console.error("Failed to get token:", error);
      return null;
    }
  }

  return (
    <AuthContext.Provider value={{ user, loading, signIn, signUp, signOut, getToken }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
```

### 5. Create API Client with JWT
```typescript
// lib/api.ts
import { useAuth } from "@/components/providers/auth-provider";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const { getToken } = useAuth();
  const token = await getToken();

  const headers = {
    "Content-Type": "application/json",
    ...(token && { Authorization: `Bearer ${token}` }),
    ...options.headers
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers
  });

  if (!response.ok) {
    if (response.status === 401) {
      // Token expired or invalid
      throw new Error("Unauthorized - please sign in again");
    }
    throw new Error(`API Error: ${response.statusText}`);
  }

  return response.json();
}

// Task API methods
export const tasksApi = {
  async list(userId: string, status: string = "all") {
    return apiRequest<Task[]>(`/api/${userId}/tasks?status=${status}`);
  },

  async create(userId: string, data: { title: string; description?: string }) {
    return apiRequest<Task>(`/api/${userId}/tasks`, {
      method: "POST",
      body: JSON.stringify(data)
    });
  },

  async update(userId: string, taskId: number, data: Partial<Task>) {
    return apiRequest<Task>(`/api/${userId}/tasks/${taskId}`, {
      method: "PUT",
      body: JSON.stringify(data)
    });
  },

  async delete(userId: string, taskId: number) {
    return apiRequest<void>(`/api/${userId}/tasks/${taskId}`, {
      method: "DELETE"
    });
  },

  async toggleComplete(userId: string, taskId: number) {
    return apiRequest<Task>(`/api/${userId}/tasks/${taskId}/complete`, {
      method: "PATCH"
    });
  }
};
```

### 6. Login/Signup Pages
```typescript
// app/login/page.tsx
"use client";

import { useState } from "react";
import { useAuth } from "@/components/providers/auth-provider";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const { signIn } = useAuth();
  const router = useRouter();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");

    try {
      await signIn(email, password);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message);
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
      />
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
      />
      {error && <p className="error">{error}</p>}
      <button type="submit">Sign In</button>
    </form>
  );
}
```

## Backend Setup (FastAPI)

### 1. Install Dependencies
```bash
pip install pyjwt cryptography
```

### 2. JWT Validation Middleware
```python
# auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
import jwt
import os
from datetime import datetime

security = HTTPBearer()

BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET")
if not BETTER_AUTH_SECRET:
    raise ValueError("BETTER_AUTH_SECRET environment variable not set")

class User:
    def __init__(self, id: str, email: str, name: str):
        self.id = id
        self.email = email
        self.name = name

async def get_current_user(
    credentials: HTTPAuthCredentials = Depends(security)
) -> User:
    """
    Validate JWT token and extract user information.
    """
    token = credentials.credentials

    try:
        # Decode JWT token with shared secret
        payload = jwt.decode(
            token,
            BETTER_AUTH_SECRET,
            algorithms=["HS256"]
        )

        # Extract user information
        user_id = payload.get("sub")  # Subject (user ID)
        email = payload.get("email")
        name = payload.get("name")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID"
            )

        # Check expiration
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired"
            )

        return User(id=user_id, email=email, name=name)

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
```

### 3. Use in Endpoints
```python
# routes/tasks.py
from auth import get_current_user, User

@router.post("/api/{user_id}/tasks")
async def create_task(
    user_id: str,
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user)  # JWT validation
):
    # CRITICAL: Verify user_id in URL matches authenticated user
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Safe to proceed - user is authenticated and authorized
    task = Task(**task_data.dict(), user_id=current_user.id)
    # ... save to database
```

## Environment Configuration

### Frontend (.env.local)
```env
BETTER_AUTH_SECRET=your-super-secret-key-min-32-chars
DATABASE_URL=postgresql://user:pass@host:5432/db
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend (.env)
```env
BETTER_AUTH_SECRET=your-super-secret-key-min-32-chars
DATABASE_URL=postgresql://user:pass@host:5432/db
ALLOWED_ORIGINS=http://localhost:3000,https://your-app.vercel.app
```

**CRITICAL**: Both frontend and backend MUST use the exact same `BETTER_AUTH_SECRET`.

## Security Checklist
- [ ] `BETTER_AUTH_SECRET` is identical in frontend and backend
- [ ] Secret is at least 32 characters long
- [ ] Secret is not committed to git (.env in .gitignore)
- [ ] JWT tokens expire (7 days recommended)
- [ ] Tokens sent in Authorization header, not URL params
- [ ] Backend validates token on every request
- [ ] User ID verified against URL parameter
- [ ] HTTPS used in production

## Testing Authentication

### 1. Test Token Generation (Frontend)
```typescript
async function testAuth() {
  await signIn("test@example.com", "password123");
  const token = await getToken();
  console.log("JWT Token:", token);
}
```

### 2. Test Token Validation (Backend)
```bash
# Get token from frontend, then test endpoint
curl -X GET http://localhost:8000/api/user123/tasks \
  -H "Authorization: Bearer <your-jwt-token>"

# Should return 200 if valid, 401 if invalid/expired
```

## Common Issues

### Issue: "Invalid token"
- **Cause**: Different secrets in frontend and backend
- **Fix**: Ensure `BETTER_AUTH_SECRET` is identical in both `.env` files

### Issue: "Token expired"
- **Cause**: Token expiration time passed
- **Fix**: Sign in again to get fresh token, or implement refresh token logic

### Issue: "Forbidden" (403)
- **Cause**: `user_id` in URL doesn't match authenticated user
- **Fix**: Ensure frontend uses `current_user.id` in API calls

## Usage in Phases
- **Phase II**: Core authentication implementation
- **Phase III**: Extends to protect chat endpoint and MCP tools
- **Phase IV**: JWT stored in Kubernetes Secrets
- **Phase V**: Same JWT used across microservices via Dapr

## Best Practices
1. Always validate user_id matches token
2. Use httpOnly cookies for token storage (not localStorage)
3. Implement token refresh for better UX
4. Add CSRF protection
5. Use HTTPS in production
6. Rotate secrets regularly
7. Log failed authentication attempts
