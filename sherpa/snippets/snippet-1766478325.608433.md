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
