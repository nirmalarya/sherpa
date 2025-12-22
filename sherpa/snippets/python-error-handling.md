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
