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
