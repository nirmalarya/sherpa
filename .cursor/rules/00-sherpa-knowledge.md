# SHERPA Knowledge Base

This file contains organizational knowledge and best practices injected by SHERPA.
Use these patterns and snippets as reference when coding.

## Available Knowledge Snippets

### Git Commits

**Category:** git/commits

# Git Commit Patterns

## Category: git/commits
## Language: bash, git
## Tags: git, version-control, commits, best-practices

## Best Practices for Git Commits

### 1. Commit Message Format

```bash
# Conventional Commits format
<type>(<scope>): <subject>

<body>

<footer>

# Types:
# feat: A new feature
# fix: A bug fix
# docs: Documentation only changes
# style: Changes that don't affect code meaning (formatting, etc.)
# refactor: Code change that neither fixes a bug nor adds a feature
# perf: Code change that improves performance
# test: Adding or updating tests
# chore: Changes to build process or auxiliary tools

# Examples:
git commit -m "feat(auth): add JWT authentication

Implement JWT-based authentication system with:
- Token generation and validation
- Refresh token mechanism
- Middleware for protected routes

Closes #123"

git commit -m "fix(api): resolve null pointer exception in user endpoint

The user endpoint was throwing NPE when email field was missing.
Added validation to check for required fields.

Fixes #456"

git commit -m "docs: update API documentation for v2.0"

git commit -m "refactor(database): optimize query performance

Replaced N+1 queries with join operations.
Performance improvement: 10x faster on large datasets."
```

### 2. Atomic Commits

```bash
# Bad: Multiple unrelated changes
git add .
git commit -m "Fix bugs and add features"

# Good: Separate commits for each logical change
git add auth.py
git commit -m "feat(auth): add password reset functionality"

git add tests/test_auth.py
git commit -m "test(auth): add tests for password reset"

git add docs/api.md
git commit -m "docs(auth): document password reset endpoint"
```

### 3. Interactive Staging

```bash
# Stage specific parts of files
git add -p file.py

# Interactive commit
git commit --verbose

# Amend last commit (only if not pushed!)
git commit --amend

# Amend without changing message
git commit --amend --no-edit

# Fix commit message
git commit --amend -m "New commit message"
```

### 4. Branch Management

```bash
# Create feature branch
git checkout -b feature/user-authentication

# Work on feature with multiple commits
git commit -m "feat(auth): add login endpoint"
git commit -m "feat(auth): add logout endpoint"
git commit -m "test(auth): add authentication tests"

# Squash commits before merging (interactive rebase)
git rebase -i main

# In editor, change 'pick' to 'squash' for commits to combine
# pick abc123 feat(auth): add login endpoint
# squash def456 feat(auth): add logout endpoint
# squash ghi789 test(auth): add authentication tests

# Push feature branch
git push origin feature/user-authentication

# Create pull request, then merge
# After merge, delete branch
git checkout main
git pull
git branch -d feature/user-authentication
git push origin --delete feature/user-authentication
```

### 5. Commit Hooks

```bash
# .git/hooks/pre-commit
#!/bin/bash

# Run linter
echo "Running linter..."
npm run lint || exit 1

# Run tests
echo "Running tests..."
npm test || exit 1

# Check for debugging code
if grep -r "console.log" src/; then
    echo "Error: console.log() found in source files"
    exit 1
fi

echo "Pre-commit checks passed!"
```

```bash
# .git/hooks/commit-msg
#!/bin/bash

# Validate commit message format
commit_msg=$(cat "$1")

# Check for conventional commit format
if ! echo "$commit_msg" | grep -qE "^(feat|fix|docs|style|refactor|perf|test|chore)(\(.+\))?: .{1,}"; then
    echo "Error: Commit message must follow conventional commits format"
    echo "Format: type(scope): subject"
    echo "Example: feat(auth): add login functionality"
    exit 1
fi

# Check subject line length
subject=$(echo "$commit_msg" | head -n 1)
if [ ${#subject} -gt 72 ]; then
    echo "Error: Subject line too long (max 72 characters)"
    exit 1
fi
```

### 6. Useful Git Commands

```bash
# View commit history
git log --oneline --graph --all
git log --author="John Doe" --since="2 weeks ago"
git log --grep="fix" --oneline

# Show changes in commit
git show abc123
git show HEAD~2

# View file history
git log --follow -- path/to/file.py
git blame path/to/file.py

# Undo commits (careful!)
git reset --soft HEAD~1  # Keep changes staged
git reset --mixed HEAD~1 # Keep changes unstaged (default)
git reset --hard HEAD~1  # Discard changes (dangerous!)

# Revert a commit (creates new commit)
git revert abc123

# Cherry-pick specific commit
git cherry-pick abc123

# Stash changes
git stash save "Work in progress"
git stash list
git stash pop
git stash apply stash@{0}

# Clean up
git clean -fd  # Remove untracked files and directories
git gc         # Garbage collection
```

### 7. Git Workflow Examples

```bash
# Feature Branch Workflow
git checkout main
git pull origin main
git checkout -b feature/new-feature
# ... work and commit ...
git push origin feature/new-feature
# Create PR, review, merge

# Gitflow Workflow
# Main branches: main, develop
# Supporting branches: feature/, release/, hotfix/

# Start feature
git checkout develop
git checkout -b feature/my-feature
# ... work ...
git checkout develop
git merge --no-ff feature/my-feature
git branch -d feature/my-feature

# Create release
git checkout develop
git checkout -b release/1.2.0
# ... version bump, bug fixes ...
git checkout main
git merge --no-ff release/1.2.0
git tag -a v1.2.0 -m "Release version 1.2.0"
git checkout develop
git merge --no-ff release/1.2.0
git branch -d release/1.2.0

# Hotfix
git checkout main
git checkout -b hotfix/critical-bug
# ... fix ...
git checkout main
git merge --no-ff hotfix/critical-bug
git tag -a v1.2.1 -m "Hotfix version 1.2.1"
git checkout develop
git merge --no-ff hotfix/critical-bug
git branch -d hotfix/critical-bug
```

### 8. Commit Signing

```bash
# Configure GPG signing
git config --global user.signingkey YOUR_GPG_KEY
git config --global commit.gpgSign true

# Sign commits
git commit -S -m "feat: add secure feature"

# Verify signed commits
git log --show-signature
git verify-commit abc123
```

### 9. Git Aliases

```bash
# Add to ~/.gitconfig or use git config --global

[alias]
    # Shortcuts
    co = checkout
    br = branch
    ci = commit
    st = status

    # Useful aliases
    unstage = reset HEAD --
    last = log -1 HEAD
    visual = log --oneline --graph --all --decorate

    # Amend staged changes to previous commit
    amend = commit --amend --no-edit

    # Show diff of staged changes
    staged = diff --staged

    # List all aliases
    aliases = config --get-regexp alias

    # Undo last commit but keep changes
    undo = reset --soft HEAD~1

    # Clean up merged branches
    cleanup = "!git branch --merged | grep -v '\\*\\|main\\|develop' | xargs -n 1 git branch -d"
```

### 10. Commit Message Templates

```bash
# Create template file: ~/.gitmessage
# <type>(<scope>): <subject>
#
# <body>
#
# <footer>
#
# Type: feat, fix, docs, style, refactor, perf, test, chore
# Scope: component or file name
# Subject: imperative, lowercase, no period at end
# Body: explain what and why (not how)
# Footer: reference issues, breaking changes

# Configure Git to use template
git config --global commit.template ~/.gitmessage
```

## Git Commit Checklist

- ✅ Write clear, descriptive commit messages
- ✅ Use conventional commit format
- ✅ Keep commits atomic (one logical change per commit)
- ✅ Don't commit commented-out code or debug statements
- ✅ Test code before committing
- ✅ Don't commit secrets or sensitive data
- ✅ Keep subject line under 72 characters
- ✅ Use imperative mood ("add feature" not "added feature")
- ✅ Reference issue numbers in commit messages
- ✅ Review changes before committing
- ✅ Use branches for features and fixes
- ✅ Squash commits before merging to main
- ✅ Sign important commits
- ✅ Pull before pushing
- ✅ Don't rewrite public history (pushed commits)


---

### Api Rest

**Category:** api/rest

# REST API Design Patterns

## Category: api/rest
## Language: python, javascript, typescript
## Tags: rest-api, http, fastapi, express, api-design

## Best Practices for REST API Design

### 1. RESTful Endpoint Structure

```
# Resource-based URLs
GET    /api/users              # List all users
GET    /api/users/:id          # Get specific user
POST   /api/users              # Create new user
PUT    /api/users/:id          # Update user (full replacement)
PATCH  /api/users/:id          # Update user (partial)
DELETE /api/users/:id          # Delete user

# Nested resources
GET    /api/users/:id/posts    # Get user's posts
POST   /api/users/:id/posts    # Create post for user
GET    /api/posts/:id/comments # Get post's comments

# Query parameters for filtering, sorting, pagination
GET    /api/users?role=admin&sort=created_at&page=2&limit=10
```

### 2. FastAPI REST Endpoints

```python
from fastapi import FastAPI, HTTPException, Query, Path, Body
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

app = FastAPI()

# Request/Response models
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    role: str = "user"

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    created_at: datetime

    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None

# List users with pagination
@app.get("/api/users", response_model=List[UserResponse])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    role: Optional[str] = Query(None),
    sort_by: str = Query("created_at")
):
    # Query database with filters
    query = "SELECT * FROM users"
    params = []

    if role:
        query += " WHERE role = ?"
        params.append(role)

    query += f" ORDER BY {sort_by} LIMIT ? OFFSET ?"
    params.extend([limit, skip])

    users = await db.fetch_all(query, params)
    return users

# Get single user
@app.get("/api/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str = Path(..., description="The ID of the user")):
    user = await db.fetch_one("SELECT * FROM users WHERE id = ?", user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Create user
@app.post("/api/users", response_model=UserResponse, status_code=201)
async def create_user(user: UserCreate):
    # Validate unique email
    existing = await db.fetch_one("SELECT id FROM users WHERE email = ?", user.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    user_id = str(uuid.uuid4())
    await db.execute(
        "INSERT INTO users (id, name, email, role, created_at) VALUES (?, ?, ?, ?, ?)",
        user_id, user.name, user.email, user.role, datetime.utcnow()
    )

    new_user = await db.fetch_one("SELECT * FROM users WHERE id = ?", user_id)
    return new_user

# Update user (partial)
@app.patch("/api/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, user: UserUpdate):
    # Check if user exists
    existing = await db.fetch_one("SELECT * FROM users WHERE id = ?", user_id)
    if not existing:
        raise HTTPException(status_code=404, detail="User not found")

    # Build update query dynamically
    update_data = user.dict(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    set_clause = ", ".join([f"{key} = ?" for key in update_data.keys()])
    values = list(update_data.values()) + [user_id]

    await db.execute(
        f"UPDATE users SET {set_clause} WHERE id = ?",
        *values
    )

    updated_user = await db.fetch_one("SELECT * FROM users WHERE id = ?", user_id)
    return updated_user

# Delete user
@app.delete("/api/users/{user_id}", status_code=204)
async def delete_user(user_id: str):
    result = await db.execute("DELETE FROM users WHERE id = ?", user_id)
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return None
```

### 3. Express.js REST Endpoints

```typescript
import express, { Request, Response, NextFunction } from 'express';
import { body, param, query, validationResult } from 'express-validator';

const app = express();
app.use(express.json());

// Validation middleware
const validate = (req: Request, res: Response, next: NextFunction) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ errors: errors.array() });
  }
  next();
};

// List users
app.get('/api/users',
  [
    query('page').optional().isInt({ min: 1 }),
    query('limit').optional().isInt({ min: 1, max: 100 }),
    validate
  ],
  async (req: Request, res: Response) => {
    const page = parseInt(req.query.page as string) || 1;
    const limit = parseInt(req.query.limit as string) || 10;
    const offset = (page - 1) * limit;

    try {
      const users = await User.findAll({ limit, offset });
      const total = await User.count();

      res.json({
        data: users,
        pagination: {
          page,
          limit,
          total,
          totalPages: Math.ceil(total / limit)
        }
      });
    } catch (error) {
      res.status(500).json({ error: 'Internal server error' });
    }
  }
);

// Get user
app.get('/api/users/:id',
  [param('id').isUUID(), validate],
  async (req: Request, res: Response) => {
    try {
      const user = await User.findByPk(req.params.id);
      if (!user) {
        return res.status(404).json({ error: 'User not found' });
      }
      res.json(user);
    } catch (error) {
      res.status(500).json({ error: 'Internal server error' });
    }
  }
);

// Create user
app.post('/api/users',
  [
    body('name').notEmpty().trim(),
    body('email').isEmail().normalizeEmail(),
    body('role').optional().isIn(['user', 'admin']),
    validate
  ],
  async (req: Request, res: Response) => {
    try {
      const user = await User.create(req.body);
      res.status(201).json(user);
    } catch (error) {
      if (error.name === 'SequelizeUniqueConstraintError') {
        return res.status(400).json({ error: 'Email already exists' });
      }
      res.status(500).json({ error: 'Internal server error' });
    }
  }
);
```

### 4. HTTP Status Codes

```python
from fastapi import status

# Success codes
HTTP_200_OK = 200              # GET request successful
HTTP_201_CREATED = 201         # POST request created resource
HTTP_204_NO_CONTENT = 204      # DELETE successful, no content to return

# Client error codes
HTTP_400_BAD_REQUEST = 400     # Invalid request data
HTTP_401_UNAUTHORIZED = 401    # Authentication required
HTTP_403_FORBIDDEN = 403       # Authenticated but not authorized
HTTP_404_NOT_FOUND = 404       # Resource not found
HTTP_409_CONFLICT = 409        # Conflict (e.g., duplicate resource)
HTTP_422_UNPROCESSABLE_ENTITY = 422  # Validation failed
HTTP_429_TOO_MANY_REQUESTS = 429     # Rate limit exceeded

# Server error codes
HTTP_500_INTERNAL_SERVER_ERROR = 500  # Server error
HTTP_503_SERVICE_UNAVAILABLE = 503    # Service temporarily unavailable

# Usage
@app.post("/api/users", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    # ...
    return new_user
```

### 5. API Versioning

```python
# URL path versioning
from fastapi import APIRouter

v1_router = APIRouter(prefix="/api/v1")
v2_router = APIRouter(prefix="/api/v2")

@v1_router.get("/users")
async def get_users_v1():
    # Old implementation
    return {"version": "v1", "users": []}

@v2_router.get("/users")
async def get_users_v2():
    # New implementation with additional fields
    return {"version": "v2", "users": [], "metadata": {}}

app.include_router(v1_router)
app.include_router(v2_router)

# Header versioning
from fastapi import Header

@app.get("/api/users")
async def get_users(api_version: str = Header("1.0")):
    if api_version == "2.0":
        return {"version": "2.0", "users": []}
    return {"version": "1.0", "users": []}
```

### 6. Error Response Format

```python
from fastapi import HTTPException
from pydantic import BaseModel
from typing import List, Optional

class ErrorDetail(BaseModel):
    field: Optional[str]
    message: str
    code: str

class ErrorResponse(BaseModel):
    error: str
    details: Optional[List[ErrorDetail]] = None
    request_id: Optional[str] = None

# Custom exception handler
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "details": [
                {
                    "field": err["loc"][-1],
                    "message": err["msg"],
                    "code": "VALIDATION_ERROR"
                }
                for err in exc.errors()
            ],
            "request_id": request.state.request_id
        }
    )
```

### 7. API Documentation

```python
from fastapi import FastAPI

app = FastAPI(
    title="My API",
    description="A comprehensive REST API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.get(
    "/api/users/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID",
    description="Retrieve a single user by their unique identifier",
    responses={
        200: {"description": "User found"},
        404: {"description": "User not found"},
    },
    tags=["users"]
)
async def get_user(
    user_id: str = Path(..., description="The unique user ID")
):
    """
    Get a user by ID.

    - **user_id**: UUID of the user to retrieve
    """
    pass
```

### 8. HATEOAS (Hypermedia)

```python
class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    links: dict

    @classmethod
    def from_db(cls, user, request: Request):
        return cls(
            id=user.id,
            name=user.name,
            email=user.email,
            links={
                "self": f"{request.url.scheme}://{request.url.netloc}/api/users/{user.id}",
                "posts": f"{request.url.scheme}://{request.url.netloc}/api/users/{user.id}/posts",
                "update": {
                    "href": f"{request.url.scheme}://{request.url.netloc}/api/users/{user.id}",
                    "method": "PATCH"
                },
                "delete": {
                    "href": f"{request.url.scheme}://{request.url.netloc}/api/users/{user.id}",
                    "method": "DELETE"
                }
            }
        )
```

## REST API Checklist

- ✅ Use nouns for resource names, not verbs
- ✅ Use HTTP methods correctly (GET, POST, PUT, PATCH, DELETE)
- ✅ Return appropriate HTTP status codes
- ✅ Implement pagination for list endpoints
- ✅ Support filtering and sorting
- ✅ Version your API
- ✅ Validate input data
- ✅ Provide clear error messages
- ✅ Document your API (OpenAPI/Swagger)
- ✅ Implement rate limiting
- ✅ Use HTTPS in production
- ✅ Follow consistent naming conventions


---

### React Hooks

**Category:** react/hooks

# React Hooks Patterns

## Category: react/hooks
## Language: javascript, typescript
## Tags: react, hooks, state-management, useEffect, useState

## Best Practices for React Hooks

### 1. useState Hook

```typescript
import { useState } from 'react';

function Counter() {
  const [count, setCount] = useState(0);
  const [user, setUser] = useState<{ name: string; email: string } | null>(null);

  // Functional update pattern
  const increment = () => setCount(prev => prev + 1);

  // Object state update
  const updateUser = (name: string, email: string) => {
    setUser({ name, email });
  };

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={increment}>Increment</button>
    </div>
  );
}
```

### 2. useEffect Hook

```typescript
import { useState, useEffect } from 'react';

function UserProfile({ userId }: { userId: string }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    const fetchUser = async () => {
      try {
        setLoading(true);
        const response = await fetch(`/api/users/${userId}`);
        const data = await response.json();

        if (!cancelled) {
          setUser(data);
          setError(null);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err.message);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    fetchUser();

    // Cleanup function
    return () => {
      cancelled = true;
    };
  }, [userId]); // Dependency array

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  return <div>User: {user?.name}</div>;
}
```

### 3. Custom Hooks

```typescript
import { useState, useEffect } from 'react';

// Custom hook for API fetching
function useFetch<T>(url: string) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await fetch(url);
        if (!response.ok) throw new Error('Network response was not ok');
        const json = await response.json();
        setData(json);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [url]);

  return { data, loading, error };
}

// Usage
function UserList() {
  const { data: users, loading, error } = useFetch<User[]>('/api/users');

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  return (
    <ul>
      {users?.map(user => <li key={user.id}>{user.name}</li>)}
    </ul>
  );
}
```

### 4. useContext for State Management

```typescript
import { createContext, useContext, useState, ReactNode } from 'react';

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);

  const login = async (email: string, password: string) => {
    const response = await fetch('/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    const data = await response.json();
    setUser(data.user);
  };

  const logout = () => {
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

// Usage in component
function LoginButton() {
  const { user, login, logout } = useAuth();

  if (user) {
    return <button onClick={logout}>Logout</button>;
  }

  return <button onClick={() => login('user@example.com', 'password')}>Login</button>;
}
```

### 5. useReducer for Complex State

```typescript
import { useReducer } from 'react';

interface State {
  count: number;
  error: string | null;
  loading: boolean;
}

type Action =
  | { type: 'increment' }
  | { type: 'decrement' }
  | { type: 'reset' }
  | { type: 'setError'; payload: string }
  | { type: 'setLoading'; payload: boolean };

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case 'increment':
      return { ...state, count: state.count + 1, error: null };
    case 'decrement':
      return { ...state, count: state.count - 1, error: null };
    case 'reset':
      return { ...state, count: 0, error: null };
    case 'setError':
      return { ...state, error: action.payload };
    case 'setLoading':
      return { ...state, loading: action.payload };
    default:
      return state;
  }
}

function Counter() {
  const [state, dispatch] = useReducer(reducer, {
    count: 0,
    error: null,
    loading: false
  });

  return (
    <div>
      <p>Count: {state.count}</p>
      {state.error && <p>Error: {state.error}</p>}
      <button onClick={() => dispatch({ type: 'increment' })}>+</button>
      <button onClick={() => dispatch({ type: 'decrement' })}>-</button>
      <button onClick={() => dispatch({ type: 'reset' })}>Reset</button>
    </div>
  );
}
```

### 6. useCallback and useMemo

```typescript
import { useState, useCallback, useMemo } from 'react';

function ExpensiveComponent() {
  const [count, setCount] = useState(0);
  const [items, setItems] = useState([1, 2, 3, 4, 5]);

  // Memoize expensive computation
  const sum = useMemo(() => {
    console.log('Computing sum...');
    return items.reduce((acc, item) => acc + item, 0);
  }, [items]); // Only recompute when items change

  // Memoize callback
  const handleClick = useCallback(() => {
    setCount(prev => prev + 1);
  }, []); // Never changes

  return (
    <div>
      <p>Sum: {sum}</p>
      <p>Count: {count}</p>
      <button onClick={handleClick}>Increment</button>
    </div>
  );
}
```

### 7. useRef for DOM and Mutable Values

```typescript
import { useRef, useEffect } from 'react';

function InputFocus() {
  const inputRef = useRef<HTMLInputElement>(null);
  const renderCount = useRef(0);

  useEffect(() => {
    // Focus input on mount
    inputRef.current?.focus();

    // Track render count
    renderCount.current++;
  });

  return (
    <div>
      <input ref={inputRef} type="text" />
      <p>Render count: {renderCount.current}</p>
    </div>
  );
}

// Timer example
function Timer() {
  const [seconds, setSeconds] = useState(0);
  const intervalRef = useRef<number | null>(null);

  const start = () => {
    if (intervalRef.current !== null) return;
    intervalRef.current = window.setInterval(() => {
      setSeconds(prev => prev + 1);
    }, 1000);
  };

  const stop = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  };

  const reset = () => {
    stop();
    setSeconds(0);
  };

  useEffect(() => {
    return () => stop(); // Cleanup on unmount
  }, []);

  return (
    <div>
      <p>Seconds: {seconds}</p>
      <button onClick={start}>Start</button>
      <button onClick={stop}>Stop</button>
      <button onClick={reset}>Reset</button>
    </div>
  );
}
```

### 8. Custom Hook for localStorage

```typescript
import { useState, useEffect } from 'react';

function useLocalStorage<T>(key: string, initialValue: T) {
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error(error);
      return initialValue;
    }
  });

  const setValue = (value: T | ((val: T) => T)) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.error(error);
    }
  };

  return [storedValue, setValue] as const;
}

// Usage
function Preferences() {
  const [theme, setTheme] = useLocalStorage('theme', 'light');

  return (
    <div>
      <p>Current theme: {theme}</p>
      <button onClick={() => setTheme('dark')}>Dark Mode</button>
      <button onClick={() => setTheme('light')}>Light Mode</button>
    </div>
  );
}
```

### 9. Custom Hook for Debouncing

```typescript
import { useState, useEffect } from 'react';

function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}

// Usage
function SearchComponent() {
  const [searchTerm, setSearchTerm] = useState('');
  const debouncedSearchTerm = useDebounce(searchTerm, 500);

  useEffect(() => {
    if (debouncedSearchTerm) {
      // Perform search API call
      console.log('Searching for:', debouncedSearchTerm);
    }
  }, [debouncedSearchTerm]);

  return (
    <input
      type="text"
      value={searchTerm}
      onChange={(e) => setSearchTerm(e.target.value)}
      placeholder="Search..."
    />
  );
}
```

## React Hooks Checklist

- ✅ Only call hooks at the top level (not in loops or conditions)
- ✅ Only call hooks from React functions
- ✅ Always include all dependencies in useEffect dependency array
- ✅ Use useCallback for functions passed to child components
- ✅ Use useMemo for expensive computations
- ✅ Clean up side effects in useEffect return function
- ✅ Use custom hooks to extract and reuse logic
- ✅ Keep components small and focused
- ✅ Use TypeScript for better type safety
- ✅ Test hooks with React Testing Library


---

### Security Auth

**Category:** security/auth

# Security & Authentication Patterns

## Category: security/auth
## Language: python, javascript
## Tags: authentication, authorization, security, jwt, oauth

## Best Practices for Authentication

### 1. Password Hashing (Python)

```python
import bcrypt
from passlib.hash import bcrypt

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return bcrypt.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against a hash"""
    return bcrypt.verify(password, hashed)
```

### 2. JWT Token Generation (Python with FastAPI)

```python
from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Optional

SECRET_KEY = "your-secret-key-here"  # Store in env variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
```

### 3. JWT Authentication Middleware (FastAPI)

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload

# Usage in route
@app.get("/protected")
async def protected_route(user = Depends(get_current_user)):
    return {"message": "Access granted", "user": user}
```

### 4. CORS Configuration (FastAPI)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 5. Input Validation & Sanitization

```python
from pydantic import BaseModel, validator, EmailStr
import re

class UserRegistration(BaseModel):
    email: EmailStr
    username: str
    password: str

    @validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]{3,20}$', v):
            raise ValueError('Username must be 3-20 alphanumeric characters')
        return v

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain digit')
        return v
```

### 6. Rate Limiting

```python
from fastapi import Request, HTTPException
from datetime import datetime, timedelta
from collections import defaultdict

class RateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)

    async def check_rate_limit(self, request: Request):
        client_ip = request.client.host
        now = datetime.utcnow()
        minute_ago = now - timedelta(minutes=1)

        # Clean old requests
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if req_time > minute_ago
        ]

        if len(self.requests[client_ip]) >= self.requests_per_minute:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

        self.requests[client_ip].append(now)

rate_limiter = RateLimiter(requests_per_minute=60)

@app.get("/api/data")
async def get_data(request: Request):
    await rate_limiter.check_rate_limit(request)
    return {"data": "some data"}
```

### 7. OAuth2 Password Flow (FastAPI)

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
```

## Security Checklist

- ✅ Never store passwords in plain text
- ✅ Use environment variables for secrets
- ✅ Implement rate limiting
- ✅ Validate and sanitize all inputs
- ✅ Use HTTPS in production
- ✅ Set secure cookie flags (httpOnly, secure, sameSite)
- ✅ Implement CSRF protection
- ✅ Use parameterized queries to prevent SQL injection
- ✅ Keep dependencies updated
- ✅ Implement proper error handling (don't leak sensitive info)


---

### Python Error Handling

**Category:** python/error-handling

# Python Error Handling Patterns

## Category: python/error-handling
## Language: python
## Tags: error-handling, exceptions, logging, debugging

## Best Practices for Error Handling

### 1. Custom Exception Classes

```python
class AppException(Exception):
    """Base exception for application"""
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class ValidationError(AppException):
    """Raised when validation fails"""
    pass

class DatabaseError(AppException):
    """Raised when database operation fails"""
    pass

class AuthenticationError(AppException):
    """Raised when authentication fails"""
    pass

# Usage
def validate_user_input(data):
    if not data.get('email'):
        raise ValidationError("Email is required", error_code="VAL_001")
```

### 2. Contextual Exception Handling

```python
from contextlib import contextmanager
import logging

@contextmanager
def handle_database_errors(operation_name: str):
    """Context manager for database operations"""
    try:
        yield
    except Exception as e:
        logging.error(f"Database error in {operation_name}: {str(e)}")
        raise DatabaseError(f"Failed to {operation_name}") from e

# Usage
async def save_user(user_data):
    with handle_database_errors("save user"):
        async with database.transaction():
            await database.execute(query, user_data)
```

### 3. Graceful Degradation

```python
import logging
from typing import Optional

def fetch_user_profile(user_id: str) -> dict:
    """Fetch user profile with fallback"""
    try:
        # Try primary data source
        return fetch_from_database(user_id)
    except DatabaseError as e:
        logging.warning(f"Database unavailable, using cache: {e}")
        try:
            # Fallback to cache
            return fetch_from_cache(user_id)
        except Exception as cache_error:
            logging.error(f"Cache also unavailable: {cache_error}")
            # Return minimal default data
            return {"id": user_id, "name": "Unknown", "available": False}
```

### 4. Retry with Exponential Backoff

```python
import time
import logging
from functools import wraps

def retry_with_backoff(max_retries=3, base_delay=1, max_delay=60):
    """Decorator for retrying with exponential backoff"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries >= max_retries:
                        logging.error(f"Max retries ({max_retries}) exceeded")
                        raise

                    delay = min(base_delay * (2 ** retries), max_delay)
                    logging.warning(f"Attempt {retries} failed: {e}. Retrying in {delay}s...")
                    time.sleep(delay)
        return wrapper
    return decorator

# Usage
@retry_with_backoff(max_retries=5, base_delay=2)
async def call_external_api(endpoint: str):
    response = await http_client.get(endpoint)
    response.raise_for_status()
    return response.json()
```

### 5. FastAPI Exception Handlers

```python
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import logging

app = FastAPI()

@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=400,
        content={
            "error": "Validation Error",
            "message": exc.message,
            "code": exc.error_code
        }
    )

@app.exception_handler(DatabaseError)
async def database_exception_handler(request: Request, exc: DatabaseError):
    logging.error(f"Database error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Database Error",
            "message": "An error occurred while processing your request"
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logging.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred"
        }
    )
```

### 6. Structured Logging

```python
import logging
import json
from datetime import datetime

class StructuredLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(message)s'))
        self.logger.addHandler(handler)

    def log(self, level: str, message: str, **kwargs):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "message": message,
            **kwargs
        }
        self.logger.log(
            getattr(logging, level.upper()),
            json.dumps(log_entry)
        )

    def info(self, message: str, **kwargs):
        self.log("info", message, **kwargs)

    def error(self, message: str, **kwargs):
        self.log("error", message, **kwargs)

# Usage
logger = StructuredLogger("app")
logger.info("User logged in", user_id="123", ip="192.168.1.1")
logger.error("Failed to save data", error="Connection timeout", retry_count=3)
```

### 7. Error Recovery Patterns

```python
from typing import Tuple, Optional
import asyncio

async def execute_with_recovery(
    primary_func,
    fallback_func=None,
    timeout: float = 30.0
) -> Tuple[bool, Optional[any], Optional[Exception]]:
    """
    Execute function with timeout and optional fallback
    Returns: (success, result, error)
    """
    try:
        # Try primary function with timeout
        result = await asyncio.wait_for(primary_func(), timeout=timeout)
        return True, result, None
    except asyncio.TimeoutError as e:
        logging.warning(f"Primary function timed out after {timeout}s")
        if fallback_func:
            try:
                result = await fallback_func()
                return True, result, None
            except Exception as fallback_error:
                return False, None, fallback_error
        return False, None, e
    except Exception as e:
        logging.error(f"Primary function failed: {e}")
        if fallback_func:
            try:
                result = await fallback_func()
                return True, result, None
            except Exception as fallback_error:
                return False, None, fallback_error
        return False, None, e

# Usage
success, data, error = await execute_with_recovery(
    primary_func=lambda: fetch_from_api(),
    fallback_func=lambda: fetch_from_cache(),
    timeout=10.0
)
if not success:
    logging.error(f"Both primary and fallback failed: {error}")
```

## Error Handling Checklist

- ✅ Use specific exception types
- ✅ Always log errors with context
- ✅ Never expose sensitive data in error messages
- ✅ Implement proper error recovery
- ✅ Use structured logging for better analysis
- ✅ Set up error monitoring/alerting
- ✅ Test error paths
- ✅ Document expected exceptions
- ✅ Clean up resources in finally blocks or use context managers
- ✅ Provide meaningful error messages to users


---

### Python Async

**Category:** python/async

# Python Async/Await Patterns

## Category: python/async
## Language: python
## Tags: async, await, asyncio, concurrency, performance

## Best Practices for Async Programming

### 1. Basic Async/Await Pattern

```python
import asyncio
from typing import List

async def fetch_data(url: str) -> dict:
    """Async function to fetch data"""
    # Simulate async I/O operation
    await asyncio.sleep(1)
    return {"url": url, "data": "some data"}

async def main():
    # Sequential execution
    result1 = await fetch_data("https://api.example.com/1")
    result2 = await fetch_data("https://api.example.com/2")

    # Concurrent execution
    results = await asyncio.gather(
        fetch_data("https://api.example.com/1"),
        fetch_data("https://api.example.com/2"),
        fetch_data("https://api.example.com/3")
    )

if __name__ == "__main__":
    asyncio.run(main())
```

### 2. Async Context Managers

```python
import aiosqlite

class DatabaseConnection:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = None

    async def __aenter__(self):
        self.connection = await aiosqlite.connect(self.db_path)
        return self.connection

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            await self.connection.close()

# Usage
async def query_database():
    async with DatabaseConnection("app.db") as conn:
        cursor = await conn.execute("SELECT * FROM users")
        rows = await cursor.fetchall()
        return rows
```

### 3. Async Generators

```python
from typing import AsyncGenerator

async def paginated_fetch(total_pages: int) -> AsyncGenerator[dict, None]:
    """Async generator for pagination"""
    for page in range(1, total_pages + 1):
        # Simulate fetching page
        await asyncio.sleep(0.5)
        yield {
            "page": page,
            "data": [f"item_{i}" for i in range(10)]
        }

# Usage
async def process_all_pages():
    async for page_data in paginated_fetch(total_pages=5):
        print(f"Processing page {page_data['page']}")
        # Process page data
```

### 4. Task Management and Cancellation

```python
async def long_running_task(task_id: str):
    try:
        for i in range(10):
            print(f"Task {task_id}: Step {i}")
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        print(f"Task {task_id} was cancelled")
        # Cleanup code here
        raise

async def task_manager():
    # Create tasks
    task1 = asyncio.create_task(long_running_task("1"))
    task2 = asyncio.create_task(long_running_task("2"))

    # Wait a bit then cancel
    await asyncio.sleep(3)
    task1.cancel()

    # Wait for tasks to complete or be cancelled
    results = await asyncio.gather(task1, task2, return_exceptions=True)
    print(f"Results: {results}")
```

### 5. Async Queue for Producer-Consumer

```python
import asyncio
from asyncio import Queue

async def producer(queue: Queue, producer_id: int):
    """Produce items and put in queue"""
    for i in range(5):
        item = f"Producer-{producer_id}-Item-{i}"
        await queue.put(item)
        print(f"Produced: {item}")
        await asyncio.sleep(0.5)

async def consumer(queue: Queue, consumer_id: int):
    """Consume items from queue"""
    while True:
        try:
            item = await asyncio.wait_for(queue.get(), timeout=3.0)
            print(f"Consumer-{consumer_id} processing: {item}")
            await asyncio.sleep(1)
            queue.task_done()
        except asyncio.TimeoutError:
            print(f"Consumer-{consumer_id} timed out")
            break

async def producer_consumer_pattern():
    queue = Queue(maxsize=10)

    # Start producers and consumers
    producers = [asyncio.create_task(producer(queue, i)) for i in range(2)]
    consumers = [asyncio.create_task(consumer(queue, i)) for i in range(3)]

    # Wait for producers to finish
    await asyncio.gather(*producers)

    # Wait for queue to be processed
    await queue.join()

    # Cancel consumers
    for c in consumers:
        c.cancel()
```

### 6. Async Locking and Synchronization

```python
import asyncio

class SharedResource:
    def __init__(self):
        self.value = 0
        self.lock = asyncio.Lock()

    async def increment(self, worker_id: int):
        """Thread-safe increment"""
        async with self.lock:
            current = self.value
            await asyncio.sleep(0.1)  # Simulate work
            self.value = current + 1
            print(f"Worker {worker_id}: {self.value}")

async def concurrent_increments():
    resource = SharedResource()
    tasks = [
        asyncio.create_task(resource.increment(i))
        for i in range(10)
    ]
    await asyncio.gather(*tasks)
    print(f"Final value: {resource.value}")
```

### 7. FastAPI with Async Database Operations

```python
from fastapi import FastAPI, HTTPException
import aiosqlite
from typing import List, Optional

app = FastAPI()

# Database connection pool
class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._connection: Optional[aiosqlite.Connection] = None

    async def connect(self):
        if self._connection is None:
            self._connection = await aiosqlite.connect(self.db_path)
            self._connection.row_factory = aiosqlite.Row
        return self._connection

    async def close(self):
        if self._connection:
            await self._connection.close()
            self._connection = None

db = Database("app.db")

@app.on_event("startup")
async def startup():
    await db.connect()

@app.on_event("shutdown")
async def shutdown():
    await db.close()

@app.get("/users")
async def get_users() -> List[dict]:
    conn = await db.connect()
    cursor = await conn.execute("SELECT * FROM users")
    rows = await cursor.fetchall()
    return [dict(row) for row in rows]

@app.post("/users")
async def create_user(name: str, email: str):
    conn = await db.connect()
    try:
        await conn.execute(
            "INSERT INTO users (name, email) VALUES (?, ?)",
            (name, email)
        )
        await conn.commit()
        return {"status": "created"}
    except Exception as e:
        await conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
```

### 8. Concurrent API Calls with Timeout

```python
import httpx
import asyncio
from typing import List, Dict

async def fetch_with_timeout(
    client: httpx.AsyncClient,
    url: str,
    timeout: float = 5.0
) -> Dict:
    """Fetch URL with timeout"""
    try:
        response = await asyncio.wait_for(
            client.get(url),
            timeout=timeout
        )
        return {"url": url, "status": response.status_code, "data": response.json()}
    except asyncio.TimeoutError:
        return {"url": url, "status": "timeout", "data": None}
    except Exception as e:
        return {"url": url, "status": "error", "data": str(e)}

async def fetch_multiple_apis(urls: List[str]):
    """Fetch multiple APIs concurrently"""
    async with httpx.AsyncClient() as client:
        tasks = [fetch_with_timeout(client, url) for url in urls]
        results = await asyncio.gather(*tasks)
        return results

# Usage
urls = [
    "https://api.example.com/endpoint1",
    "https://api.example.com/endpoint2",
    "https://api.example.com/endpoint3"
]
results = asyncio.run(fetch_multiple_apis(urls))
```

### 9. Async Semaphore for Rate Limiting

```python
import asyncio

class RateLimiter:
    def __init__(self, max_concurrent: int = 5, delay: float = 0.1):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.delay = delay

    async def execute(self, coro):
        """Execute coroutine with rate limiting"""
        async with self.semaphore:
            result = await coro
            await asyncio.sleep(self.delay)
            return result

async def api_call(item_id: int):
    """Simulated API call"""
    await asyncio.sleep(0.5)
    return f"Result for item {item_id}"

async def process_items_with_rate_limit():
    limiter = RateLimiter(max_concurrent=3, delay=0.2)

    tasks = [
        limiter.execute(api_call(i))
        for i in range(20)
    ]

    results = await asyncio.gather(*tasks)
    return results
```

## Async Best Practices Checklist

- ✅ Use `async`/`await` for I/O-bound operations
- ✅ Don't use `asyncio.sleep()` in production (use for testing)
- ✅ Use `asyncio.gather()` for concurrent operations
- ✅ Implement proper error handling in async code
- ✅ Use async context managers for resources
- ✅ Cancel tasks properly to avoid resource leaks
- ✅ Use semaphores for rate limiting
- ✅ Avoid blocking operations in async code
- ✅ Use `asyncio.create_task()` for background tasks
- ✅ Test async code thoroughly


---

### Testing Unit

**Category:** testing/unit

# Unit Testing Patterns

## Category: testing/unit
## Language: python, javascript, typescript
## Tags: testing, pytest, jest, unit-tests, tdd

## Best Practices for Unit Testing

### 1. Python Unit Tests with pytest

```python
import pytest
from datetime import datetime

# Function to test
def calculate_discount(price: float, discount_percent: float) -> float:
    if discount_percent < 0 or discount_percent > 100:
        raise ValueError("Discount must be between 0 and 100")
    return price * (1 - discount_percent / 100)

# Tests
def test_calculate_discount_valid():
    assert calculate_discount(100, 10) == 90
    assert calculate_discount(50, 20) == 40

def test_calculate_discount_zero():
    assert calculate_discount(100, 0) == 100

def test_calculate_discount_invalid():
    with pytest.raises(ValueError):
        calculate_discount(100, -10)
    with pytest.raises(ValueError):
        calculate_discount(100, 150)

# Parametrized tests
@pytest.mark.parametrize("price,discount,expected", [
    (100, 10, 90),
    (50, 20, 40),
    (200, 50, 100),
])
def test_calculate_discount_parametrized(price, discount, expected):
    assert calculate_discount(price, discount) == expected
```

### 2. Testing Async Functions (Python)

```python
import pytest
import asyncio

async def fetch_user(user_id: str) -> dict:
    await asyncio.sleep(0.1)  # Simulate async operation
    return {"id": user_id, "name": "Test User"}

@pytest.mark.asyncio
async def test_fetch_user():
    result = await fetch_user("123")
    assert result["id"] == "123"
    assert result["name"] == "Test User"

@pytest.mark.asyncio
async def test_fetch_user_concurrent():
    results = await asyncio.gather(
        fetch_user("1"),
        fetch_user("2"),
        fetch_user("3")
    )
    assert len(results) == 3
    assert all(r["name"] == "Test User" for r in results)
```

### 3. Fixtures and Mocking (Python)

```python
import pytest
from unittest.mock import Mock, patch, AsyncMock

# Fixtures
@pytest.fixture
def sample_user():
    return {"id": "123", "name": "Test User", "email": "test@example.com"}

@pytest.fixture
async def db_connection():
    # Setup
    conn = await create_connection()
    yield conn
    # Teardown
    await conn.close()

# Using fixtures
def test_user_creation(sample_user):
    assert sample_user["name"] == "Test User"

# Mocking
def test_api_call_with_mock():
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = {"status": "ok"}
        mock_get.return_value.status_code = 200

        response = make_api_call()
        assert response["status"] == "ok"
        mock_get.assert_called_once()

# Async mocking
@pytest.mark.asyncio
async def test_async_api_call():
    with patch('httpx.AsyncClient.get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value.json.return_value = {"data": "test"}

        result = await fetch_api_data()
        assert result["data"] == "test"
```

### 4. JavaScript/TypeScript Tests with Jest

```typescript
// Function to test
function add(a: number, b: number): number {
  return a + b;
}

function fetchUser(id: string): Promise<User> {
  return fetch(`/api/users/${id}`).then(res => res.json());
}

// Basic tests
describe('add function', () => {
  test('adds two positive numbers', () => {
    expect(add(2, 3)).toBe(5);
  });

  test('adds negative numbers', () => {
    expect(add(-2, -3)).toBe(-5);
  });

  test('adds zero', () => {
    expect(add(0, 5)).toBe(5);
  });
});

// Testing arrays and objects
describe('User operations', () => {
  test('user object has required fields', () => {
    const user = { id: '1', name: 'John', email: 'john@example.com' };
    expect(user).toHaveProperty('id');
    expect(user).toHaveProperty('name');
    expect(user).toMatchObject({
      id: '1',
      name: 'John'
    });
  });

  test('array contains user', () => {
    const users = [
      { id: '1', name: 'John' },
      { id: '2', name: 'Jane' }
    ];
    expect(users).toContainEqual({ id: '1', name: 'John' });
    expect(users).toHaveLength(2);
  });
});
```

### 5. Testing Async Code (Jest)

```typescript
// Async function to test
async function fetchData(): Promise<string> {
  return new Promise((resolve) => {
    setTimeout(() => resolve('data'), 100);
  });
}

describe('Async tests', () => {
  test('fetches data successfully', async () => {
    const data = await fetchData();
    expect(data).toBe('data');
  });

  test('handles promise rejection', async () => {
    const failingFetch = () => Promise.reject(new Error('Failed'));
    await expect(failingFetch()).rejects.toThrow('Failed');
  });
});
```

### 6. Mocking in Jest

```typescript
import { fetchUser } from './api';

// Mock the module
jest.mock('./api');

describe('User fetching', () => {
  test('mocks fetch user', async () => {
    const mockUser = { id: '1', name: 'John' };
    (fetchUser as jest.Mock).mockResolvedValue(mockUser);

    const user = await fetchUser('1');
    expect(user).toEqual(mockUser);
    expect(fetchUser).toHaveBeenCalledWith('1');
  });

  test('mocks multiple calls with different values', async () => {
    (fetchUser as jest.Mock)
      .mockResolvedValueOnce({ id: '1', name: 'John' })
      .mockResolvedValueOnce({ id: '2', name: 'Jane' });

    const user1 = await fetchUser('1');
    const user2 = await fetchUser('2');

    expect(user1.name).toBe('John');
    expect(user2.name).toBe('Jane');
  });
});

// Spy on methods
describe('Spying', () => {
  test('spies on console.log', () => {
    const consoleSpy = jest.spyOn(console, 'log');

    console.log('test message');

    expect(consoleSpy).toHaveBeenCalledWith('test message');
    consoleSpy.mockRestore();
  });
});
```

### 7. React Component Testing

```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Counter from './Counter';

describe('Counter Component', () => {
  test('renders initial count', () => {
    render(<Counter />);
    expect(screen.getByText(/count: 0/i)).toBeInTheDocument();
  });

  test('increments count on button click', () => {
    render(<Counter />);
    const button = screen.getByRole('button', { name: /increment/i });

    fireEvent.click(button);
    expect(screen.getByText(/count: 1/i)).toBeInTheDocument();
  });

  test('user interaction with userEvent', async () => {
    render(<Counter />);
    const button = screen.getByRole('button', { name: /increment/i });

    await userEvent.click(button);
    await userEvent.click(button);

    expect(screen.getByText(/count: 2/i)).toBeInTheDocument();
  });
});

// Testing async components
describe('UserProfile Component', () => {
  test('loads and displays user data', async () => {
    const mockUser = { name: 'John Doe', email: 'john@example.com' };

    global.fetch = jest.fn(() =>
      Promise.resolve({
        json: () => Promise.resolve(mockUser),
      })
    ) as jest.Mock;

    render(<UserProfile userId="123" />);

    // Initially shows loading
    expect(screen.getByText(/loading/i)).toBeInTheDocument();

    // Wait for user data to load
    await waitFor(() => {
      expect(screen.getByText(mockUser.name)).toBeInTheDocument();
    });

    expect(global.fetch).toHaveBeenCalledWith('/api/users/123');
  });
});
```

### 8. Testing with Fixtures and Setup/Teardown

```python
import pytest

class TestDatabase:
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        # Setup before each test
        self.db = create_test_database()
        yield
        # Teardown after each test
        self.db.cleanup()

    def test_insert_user(self):
        user_id = self.db.insert_user("test@example.com")
        assert user_id is not None

    def test_query_user(self):
        self.db.insert_user("test@example.com")
        user = self.db.get_user_by_email("test@example.com")
        assert user["email"] == "test@example.com"

# Module-level fixtures
@pytest.fixture(scope="module")
def database():
    db = create_database()
    db.migrate()
    yield db
    db.drop_all_tables()

def test_with_module_fixture(database):
    assert database.is_connected()
```

### 9. Code Coverage

```bash
# Python with pytest
pytest --cov=myapp --cov-report=html tests/

# JavaScript with Jest
jest --coverage

# TypeScript with Jest
jest --coverage --collectCoverageFrom='src/**/*.{ts,tsx}'
```

```python
# .coveragerc configuration
[run]
source = myapp
omit =
    */tests/*
    */migrations/*
    */__init__.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
```

## Testing Checklist

- ✅ Write tests before or alongside code (TDD)
- ✅ Test one thing per test
- ✅ Use descriptive test names
- ✅ Follow AAA pattern: Arrange, Act, Assert
- ✅ Mock external dependencies
- ✅ Test edge cases and error conditions
- ✅ Aim for high code coverage (80%+)
- ✅ Keep tests fast and independent
- ✅ Use fixtures for common setup
- ✅ Run tests in CI/CD pipeline


---

### None

**Category:** general

# TypeScript Best Practices

## Overview
This snippet contains best practices for writing TypeScript code.

## Key Principles

1. **Use Strict Mode**
   - Always enable strict mode in tsconfig.json
   - Catches common errors at compile time

2. **Proper Type Annotations**
   - Avoid using 'any' type
   - Use interfaces for object shapes
   - Use type aliases for unions

3. **Error Handling**
   - Use custom error types
   - Handle async errors with try/catch

## Example Code

```typescript
interface User {
    id: string;
    name: string;
    email: string;
}

async function getUser(id: string): Promise<User> {
    try {
        const response = await fetch(`/api/users/${id}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Failed to fetch user:', error);
        throw error;
    }
}
```

## Resources
- TypeScript Handbook: https://www.typescriptlang.org/docs/
- Effective TypeScript: https://effectivetypescript.com/


---

