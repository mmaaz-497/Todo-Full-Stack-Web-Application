# Todo Frontend (Next.js)

Modern, responsive frontend for the Todo Full-Stack Web Application built with Next.js 16, TypeScript, and Tailwind CSS.

## Features

- ✅ **User Authentication**: Signup, signin, and signout with Better Auth
- ✅ **Task Management**: Complete CRUD operations for tasks
- ✅ **Real-time Updates**: Optimistic UI updates with error handling
- ✅ **Responsive Design**: Works on mobile, tablet, and desktop
- ✅ **Type Safety**: Full TypeScript implementation
- ✅ **Modern UI**: Clean, accessible interface with Tailwind CSS
- ✅ **Protected Routes**: Authentication-required pages
- ✅ **Error Handling**: User-friendly error messages

## Tech Stack

- **Framework**: Next.js 16+ (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **HTTP Client**: Axios
- **Validation**: Zod schemas
- **Authentication**: Better Auth client
- **React**: 19+

## Project Structure

```
frontend/
├── app/
│   ├── layout.tsx          # Root layout
│   ├── page.tsx             # Home/landing page
│   ├── globals.css          # Global styles with Tailwind
│   ├── signin/
│   │   └── page.tsx         # Sign in page
│   ├── signup/
│   │   └── page.tsx         # Sign up page
│   └── tasks/
│       └── page.tsx         # Task management (main app)
├── lib/
│   ├── api.ts               # Backend API client
│   └── auth.ts              # Better Auth integration
├── components/              # Reusable components (future)
├── next.config.ts           # Next.js configuration
├── tailwind.config.ts       # Tailwind configuration
├── tsconfig.json            # TypeScript configuration
├── .env.local               # Environment variables (not in git)
├── .env.example             # Environment template
└── package.json             # Dependencies and scripts
```

## Installation

### Prerequisites

- Node.js 18+
- npm or yarn
- Backend API running on port 8000
- Better Auth service running on port 3001

### Setup Steps

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies** (if not already done):
   ```bash
   npm install
   ```

3. **Configure environment variables**:
   ```bash
   cp .env.example .env.local
   ```

   Edit `.env.local`:
   ```env
   NEXT_PUBLIC_AUTH_URL=http://localhost:3001
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

4. **Run development server**:
   ```bash
   npm run dev
   ```

   Open http://localhost:3000

## Available Scripts

```bash
npm run dev      # Start development server (http://localhost:3000)
npm run build    # Build production bundle
npm run start    # Start production server
npm run lint     # Run ESLint
```

## Pages

### Landing Page (/)

- Welcome screen with Sign In and Sign Up buttons
- Auto-redirects to /tasks if already authenticated
- Clean, modern design

### Sign Up (/signup)

- Email, password, and optional name fields
- Password confirmation validation
- Email uniqueness check
- Redirects to /tasks on success

### Sign In (/signin)

- Email and password fields
- JWT token storage in localStorage
- Error handling for invalid credentials
- Redirects to /tasks on success

### Tasks Page (/tasks)

**Main application interface with:**
- Task list display
- Create new task form
- Edit existing tasks (inline)
- Delete tasks (with confirmation)
- Mark tasks as complete/incomplete (checkbox)
- Real-time updates
- Loading states
- Error messages
- Empty state message

**Protected**: Requires authentication, redirects to /signin if not logged in.

## Features In Detail

### Authentication Flow

1. **Sign Up**:
   - User fills signup form
   - Frontend calls Better Auth `/api/auth/signup/email`
   - JWT token and user data stored in localStorage
   - Redirect to /tasks

2. **Sign In**:
   - User enters credentials
   - Frontend calls Better Auth `/api/auth/signin/email`
   - JWT token stored, user redirected to /tasks

3. **Sign Out**:
   - Calls Better Auth `/api/auth/signout`
   - Clears localStorage
   - Redirects to landing page

4. **Session Persistence**:
   - Token stored in localStorage
   - Automatically attached to API requests via axios interceptor
   - Auto-redirects to /signin if token expires (401 response)

### Task Management

**Create Task**:
- Click "Add New Task" button
- Fill title (required, 1-200 chars) and description (optional, max 1000 chars)
- Submit → Task appears in list immediately

**Update Task**:
- Click "Edit" on any task
- Modify title and/or description
- Click "Save" → Updates immediately

**Delete Task**:
- Click "Delete" on any task
- Confirm in dialog
- Task removed from list

**Toggle Complete**:
- Click checkbox next to task
- Completed tasks show strikethrough styling
- Status persists to database

### API Client (`lib/api.ts`)

Centralized HTTP client with:
- Automatic JWT token attachment
- Request/response interceptors
- Error handling
- Type-safe method signatures
- Auto-redirect on 401 Unauthorized

**Methods**:
```typescript
api.getTasks(userId)
api.createTask(userId, taskData)
api.getTask(userId, taskId)
api.updateTask(userId, taskId, taskData)
api.deleteTask(userId, taskId)
api.toggleComplete(userId, taskId)
```

### Auth Client (`lib/auth.ts`)

Better Auth integration with:
- Signup, signin, signout functions
- Token management
- User state retrieval
- Authentication status check

**Methods**:
```typescript
auth.signup({ email, password, name })
auth.signin({ email, password })
auth.signout()
auth.getCurrentUser()
auth.getToken()
auth.isAuthenticated()
```

## Styling

### Tailwind CSS

Custom configuration in `tailwind.config.ts`:
- Content paths for all components
- Color theme with CSS variables
- Responsive breakpoints
- Utility classes

### Design System

**Colors**:
- Primary: Indigo (buttons, links, focus states)
- Success: Green (completed tasks)
- Error: Red (error messages, delete actions)
- Neutral: Gray (text, backgrounds, borders)

**Components**:
- Forms: Clean inputs with focus states
- Buttons: Primary and secondary styles
- Cards: Elevated shadows for tasks
- States: Loading spinners, empty states

## Environment Variables

| Variable              | Description                    | Default                |
|-----------------------|--------------------------------|------------------------|
| NEXT_PUBLIC_AUTH_URL  | Better Auth service URL        | http://localhost:3001  |
| NEXT_PUBLIC_API_URL   | Backend API URL                | http://localhost:8000  |

**Note**: Variables prefixed with `NEXT_PUBLIC_` are exposed to the browser.

## TypeScript Configuration

Strict mode enabled with:
- ES2017 target
- ESNext modules
- Path aliases (`@/*` → `./`)
- JSX preserve (for React)
- Incremental compilation

## Troubleshooting

### Port Already in Use

```
Error: Port 3000 is already in use
```

**Solution**: Kill process on port 3000 or use different port:
```bash
npm run dev -- -p 3001
```

### Cannot Connect to Backend

```
Network Error: Failed to fetch
```

**Solutions**:
- Verify backend is running on port 8000
- Check `NEXT_PUBLIC_API_URL` in `.env.local`
- Verify CORS is configured in backend

### Authentication Fails

```
401 Unauthorized
```

**Solutions**:
- Verify Better Auth service is running on port 3001
- Check `NEXT_PUBLIC_AUTH_URL` in `.env.local`
- Ensure BETTER_AUTH_SECRET matches between auth-service and backend
- Clear localStorage and try signing in again

### Tasks Not Loading

**Solutions**:
- Check browser console for errors
- Verify JWT token in localStorage (`auth_token`)
- Ensure user ID from token matches API path parameter
- Check backend logs for errors

## Development Workflow

1. **Start all services**:
   ```bash
   # Terminal 1: Auth service
   cd auth-service && npm run dev

   # Terminal 2: Backend API
   cd backend && python main.py

   # Terminal 3: Frontend
   cd frontend && npm run dev
   ```

2. **Make changes**:
   - Edit files in `app/`, `lib/`, or `components/`
   - Next.js auto-reloads on save

3. **Test features**:
   - Create account at http://localhost:3000/signup
   - Sign in and manage tasks
   - Verify API calls in browser DevTools Network tab

## Deployment

### Vercel (Recommended)

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Complete frontend implementation"
   git push
   ```

2. **Connect to Vercel**:
   - Go to https://vercel.com
   - Import GitHub repository
   - Select `frontend` as root directory

3. **Configure environment variables**:
   - `NEXT_PUBLIC_AUTH_URL`: Your deployed auth service URL
   - `NEXT_PUBLIC_API_URL`: Your deployed backend API URL

4. **Deploy**:
   - Vercel auto-deploys on push
   - HTTPS enabled automatically

### Other Hosting Platforms

**Build for production**:
```bash
npm run build
```

**Start production server**:
```bash
npm start
```

Or deploy `./next` output directory to any Node.js hosting.

## Security Considerations

1. **Token Storage**:
   - JWT stored in localStorage (XSS risk mitigated by HTTPS + CSP)
   - Consider httpOnly cookies for enhanced security

2. **CORS**:
   - Backend must whitelist frontend domain
   - Use HTTPS in production

3. **Input Validation**:
   - Client-side validation for UX
   - Server-side validation is authoritative

4. **Secrets**:
   - Never commit `.env.local`
   - Use environment variables in deployment platform

## Performance Optimizations

- **Next.js App Router**: Server Components by default
- **Code Splitting**: Automatic page-based splitting
- **Image Optimization**: Use `next/image` for images
- **Caching**: Browser caching for static assets
- **Lazy Loading**: Components load on demand

## Accessibility

- Semantic HTML elements
- ARIA labels where needed
- Keyboard navigation support (Tab, Enter, Space)
- Focus indicators on interactive elements
- Screen reader friendly

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## License

Part of the Todo Full-Stack Web Application (Hackathon Phase II).
