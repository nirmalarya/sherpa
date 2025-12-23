"""
SHERPA V1 - Main FastAPI Application
Backend API server for the autonomous coding orchestrator
"""

from fastapi import FastAPI, HTTPException, Body, Request, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, ValidationError, validator
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.exceptions import HTTPException as StarletteHTTPException
import asyncio
from datetime import datetime
from typing import Optional, Dict, List, Any
from collections import defaultdict
import time
import sys
from pathlib import Path
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sherpa.core.db import get_db, DB_PATH
from sherpa.core.logging_config import get_logger
from sherpa.core.migrations import run_migrations, rollback_migrations, get_migration_status
from sherpa.core.config import get_settings
from sherpa.core.bedrock_client import get_bedrock_client
from sherpa.core.integrations.azure_devops_client import get_azure_devops_client

# Initialize logger
logger = get_logger("sherpa.api")


# Pydantic models with comprehensive validation
class CreateSessionRequest(BaseModel):
    spec_file: Optional[str] = Field(None, min_length=1, max_length=500, description="Path to spec file")
    total_features: int = Field(default=0, ge=0, le=10000, description="Total number of features")
    work_item_id: Optional[str] = Field(None, min_length=1, max_length=100, description="Azure DevOps work item ID")
    git_branch: Optional[str] = Field(None, min_length=1, max_length=200, description="Git branch name")

    class Config:
        # Reject extra fields not defined in the model
        extra = "forbid"

    @validator('spec_file', allow_reuse=True)
    def validate_spec_file(cls, v):
        if v is not None and v.strip() == '':
            raise ValueError('spec_file cannot be empty string')
        return v


class CreateSnippetRequest(BaseModel):
    id: Optional[str] = Field(None, min_length=1, max_length=100, description="Snippet ID")
    name: str = Field(..., min_length=1, max_length=200, description="Snippet name")
    category: str = Field(..., min_length=1, max_length=50, description="Snippet category")
    source: str = Field(default="project", pattern="^(built-in|org|project|local)$", description="Snippet source")
    content: str = Field(..., min_length=1, max_length=1000000, description="Snippet content")
    language: Optional[str] = Field(None, max_length=100, description="Programming language")
    tags: Optional[str] = Field(None, max_length=500, description="Comma-separated tags")

    class Config:
        extra = "forbid"

    @validator('name', 'category', 'content', allow_reuse=True)
    def validate_not_empty(cls, v):
        if v and v.strip() == '':
            raise ValueError('field cannot be empty string')
        return v


class AzureDevOpsConnectRequest(BaseModel):
    organization: str = Field(..., min_length=1, max_length=200, description="Azure DevOps organization")
    project: str = Field(..., min_length=1, max_length=200, description="Azure DevOps project")
    pat: str = Field(..., min_length=1, max_length=500, description="Personal Access Token")

    class Config:
        extra = "forbid"

    @validator('organization', 'project', 'pat', allow_reuse=True)
    def validate_not_empty(cls, v):
        if v.strip() == '':
            raise ValueError('field cannot be empty string')
        return v


class AzureDevOpsSaveConfigRequest(BaseModel):
    organization: str = Field(..., min_length=1, max_length=200, description="Azure DevOps organization")
    project: str = Field(..., min_length=1, max_length=200, description="Azure DevOps project")
    pat: str = Field(..., min_length=1, max_length=500, description="Personal Access Token")

    class Config:
        extra = "forbid"

    @validator('organization', 'project', 'pat', allow_reuse=True)
    def validate_not_empty(cls, v):
        if v.strip() == '':
            raise ValueError('field cannot be empty string')
        return v


class AzureDevOpsUpdateWorkItemRequest(BaseModel):
    updates: Dict[str, Any] = Field(..., description="Dictionary of field updates (e.g., {'State': 'Active', 'Title': 'New title'})")

    class Config:
        extra = "forbid"

    @validator('updates')
    def validate_updates_not_empty(cls, v):
        if not v:
            raise ValueError('updates dictionary cannot be empty')
        return v


class GenerateInstructionFilesRequest(BaseModel):
    target_directory: Optional[str] = Field(None, max_length=500, description="Target directory for generated files (defaults to current working directory)")

    class Config:
        extra = "forbid"

    @validator('target_directory', allow_reuse=True)
    def validate_target_directory(cls, v):
        if v is not None and v.strip() == '':
            raise ValueError('target_directory cannot be empty string')
        return v


class QuerySnippetsRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500, description="Search query text")
    max_results: int = Field(default=5, ge=1, le=20, description="Maximum number of results")
    min_score: float = Field(default=0.5, ge=0.0, le=1.0, description="Minimum relevance score")

    class Config:
        extra = "forbid"

    @validator('query', allow_reuse=True)
    def validate_query(cls, v):
        if v.strip() == '':
            raise ValueError('query cannot be empty string')
        return v


# Response Schema Classes for consistent API responses
class SuccessResponse(BaseModel):
    """Standard success response wrapper"""
    success: bool = True
    data: Any
    message: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class ErrorResponse(BaseModel):
    """Standard error response wrapper"""
    success: bool = False
    error: str
    message: str
    details: Optional[Any] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


def success_response(data: Any, message: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a consistent success response

    Args:
        data: The response data (can be dict, list, or any serializable type)
        message: Optional success message

    Returns:
        Dictionary following the standard success response format
    """
    return {
        "success": True,
        "data": data,
        "message": message,
        "timestamp": datetime.utcnow().isoformat()
    }


def error_response(error: str, message: str, details: Optional[Any] = None) -> Dict[str, Any]:
    """
    Create a consistent error response

    Args:
        error: Error type/category
        message: Human-readable error message
        details: Optional additional error details

    Returns:
        Dictionary following the standard error response format
    """
    return {
        "success": False,
        "error": error,
        "message": message,
        "details": details,
        "timestamp": datetime.utcnow().isoformat()
    }


# Create FastAPI app
app = FastAPI(
    title="SHERPA V1 API",
    description="Autonomous Coding Orchestrator - Backend API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# API Versioning Middleware - Add API-Version header to all responses
class APIVersionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        # Add API-Version header to all responses
        response.headers["API-Version"] = "1.0.0"
        return response


# Rate Limiting Middleware - Prevent API abuse
class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # Store request timestamps per client IP
        self.request_history: Dict[str, list] = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"

        # Get current timestamp
        current_time = time.time()

        # Clean up old requests outside the time window
        cutoff_time = current_time - self.window_seconds
        self.request_history[client_ip] = [
            timestamp for timestamp in self.request_history[client_ip]
            if timestamp > cutoff_time
        ]

        # Count requests in current window
        request_count = len(self.request_history[client_ip])

        # Calculate remaining requests and reset time
        # Reset time is when the oldest request in the window expires
        remaining = max(0, self.max_requests - request_count - 1)
        if self.request_history[client_ip]:
            oldest_request = self.request_history[client_ip][0]
            reset_time = int(oldest_request + self.window_seconds)
        else:
            reset_time = int(current_time + self.window_seconds)

        # Check if rate limit exceeded
        if request_count >= self.max_requests:
            retry_after = int(reset_time - current_time)
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Maximum {self.max_requests} requests per {self.window_seconds} seconds.",
                    "retry_after": retry_after
                },
                headers={
                    "X-RateLimit-Limit": str(self.max_requests),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_time),
                    "Retry-After": str(retry_after)
                }
            )

        # Add current request to history
        self.request_history[client_ip].append(current_time)

        # Process request
        response = await call_next(request)

        # Add rate limit headers to response
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_time)

        return response


# Global metrics storage
metrics_data = {
    "request_count": 0,
    "error_count": 0,
    "requests_by_endpoint": defaultdict(int),
    "errors_by_endpoint": defaultdict(int),
    "start_time": datetime.utcnow().isoformat()
}


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to track request metrics for monitoring"""

    async def dispatch(self, request: Request, call_next):
        # Increment total request count
        metrics_data["request_count"] += 1

        # Track requests by endpoint
        endpoint = f"{request.method} {request.url.path}"
        metrics_data["requests_by_endpoint"][endpoint] += 1

        # Process request
        try:
            response = await call_next(request)

            # Track errors (4xx and 5xx status codes)
            if response.status_code >= 400:
                metrics_data["error_count"] += 1
                metrics_data["errors_by_endpoint"][endpoint] += 1

            return response
        except Exception as e:
            # Track unhandled exceptions
            metrics_data["error_count"] += 1
            metrics_data["errors_by_endpoint"][endpoint] += 1
            raise


# Add middleware in correct order (they are applied in reverse for responses)
# Order: Metrics -> Rate Limit -> API Version -> CORS (CORS is applied last to responses)
app.add_middleware(APIVersionMiddleware)
app.add_middleware(RateLimitMiddleware, max_requests=100, window_seconds=60)
app.add_middleware(MetricsMiddleware)

# CORS configuration - allow frontend on ports 3001, 3002, 3003
# Added LAST so it's applied FIRST to responses (middleware wrapping order)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:3003",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
        "http://127.0.0.1:3003",
        "*",  # Allow all origins for now (remove in production)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],  # Expose all headers to the client
)


# Global exception handler for request validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle Pydantic validation errors and return detailed error information
    """
    errors = []
    for error in exc.errors():
        error_detail = {
            "field": ".".join(str(loc) for loc in error["loc"][1:]) if len(error["loc"]) > 1 else str(error["loc"][0]),
            "message": error["msg"],
            "type": error["type"]
        }
        errors.append(error_detail)

    logger.warning(f"Validation error on {request.method} {request.url.path}: {errors}")

    return JSONResponse(
        status_code=400,
        content=error_response(
            error="Validation Error",
            message="Request validation failed",
            details=errors
        )
    )


# Global exception handler for generic HTTP exceptions
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Handle HTTP exceptions with consistent response format
    """
    # Map common status codes to error types
    error_type_map = {
        400: "Bad Request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        405: "Method Not Allowed",
        409: "Conflict",
        422: "Unprocessable Entity",
        429: "Rate Limit Exceeded",
        500: "Internal Server Error",
        502: "Bad Gateway",
        503: "Service Unavailable"
    }

    error_type = error_type_map.get(exc.status_code, f"HTTP {exc.status_code}")

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(
            error=error_type,
            message=str(exc.detail),
            details={"status_code": exc.status_code}
        )
    )


@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info("🏔️  SHERPA V1 Backend Starting...")
    logger.info("📊 API Documentation: http://localhost:8000/docs")
    logger.info("⚛️  Frontend: http://localhost:3001")

    # Initialize database
    try:
        db = await get_db()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}", exc_info=True)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("👋 SHERPA V1 Backend Shutting Down...")


@app.get("/")
async def root():
    """Root endpoint"""
    return success_response(
        data={
            "name": "SHERPA V1 API",
            "version": "1.0.0",
            "status": "running"
        },
        message="SHERPA V1 API is running"
    )


@app.get("/health")
async def health_check():
    """
    Enhanced health check endpoint with dependency status checking

    Returns:
        - 200: Service is healthy (all dependencies OK)
        - 503: Service is unhealthy (one or more dependencies failed)

    Response includes:
        - status: "ok" or "unhealthy"
        - version: API version
        - service: Service name
        - dependencies: Status of each dependency (database, etc.)
    """
    # Check database dependency
    db_status = "ok"
    db_message = "Database connection successful"

    try:
        db = await get_db()
        # Perform a simple query to verify database is accessible
        conn = await db.connect()
        cursor = await conn.execute("SELECT 1")
        await cursor.fetchone()
        db_status = "ok"
        db_message = "Database connection successful"
    except Exception as e:
        db_status = "error"
        db_message = f"Database connection failed: {str(e)}"
        logger.error(f"Health check - Database error: {e}", exc_info=True)

    # Determine overall status
    overall_status = "ok" if db_status == "ok" else "unhealthy"

    # Build dependencies status
    dependencies = {
        "database": {
            "status": db_status,
            "message": db_message,
            "type": "sqlite",
            "path": str(DB_PATH)
        }
    }

    # Build response data
    health_data = {
        "status": overall_status,
        "service": "sherpa-api",
        "version": "1.0.0",
        "dependencies": dependencies
    }

    # Return 503 if unhealthy, 200 if healthy
    if overall_status == "unhealthy":
        return JSONResponse(
            status_code=503,
            content=success_response(
                data=health_data,
                message="Service is unhealthy - one or more dependencies failed"
            )
        )

    return success_response(
        data=health_data,
        message="Service is healthy"
    )


@app.get("/metrics")
async def get_metrics():
    """
    Metrics endpoint for monitoring system health and performance

    Returns metrics in a format compatible with Prometheus and other monitoring tools:
    - Total request count
    - Error count and error rate
    - Active sessions count
    - Requests by endpoint
    - Errors by endpoint
    - Uptime information

    Response format supports both JSON and Prometheus text format
    """
    try:
        # Get active sessions count from database
        db = await get_db()
        sessions = await db.get_sessions(status="active")
        active_sessions = len(sessions)

        # Calculate error rate
        total_requests = metrics_data["request_count"]
        total_errors = metrics_data["error_count"]
        error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0.0

        # Calculate uptime
        start_time = datetime.fromisoformat(metrics_data["start_time"])
        uptime_seconds = (datetime.utcnow() - start_time).total_seconds()

        # Build Prometheus-style metrics text
        prometheus_metrics = []
        prometheus_metrics.append("# HELP sherpa_requests_total Total number of HTTP requests")
        prometheus_metrics.append("# TYPE sherpa_requests_total counter")
        prometheus_metrics.append(f"sherpa_requests_total {total_requests}")
        prometheus_metrics.append("")

        prometheus_metrics.append("# HELP sherpa_errors_total Total number of HTTP errors")
        prometheus_metrics.append("# TYPE sherpa_errors_total counter")
        prometheus_metrics.append(f"sherpa_errors_total {total_errors}")
        prometheus_metrics.append("")

        prometheus_metrics.append("# HELP sherpa_error_rate Error rate percentage")
        prometheus_metrics.append("# TYPE sherpa_error_rate gauge")
        prometheus_metrics.append(f"sherpa_error_rate {error_rate:.2f}")
        prometheus_metrics.append("")

        prometheus_metrics.append("# HELP sherpa_active_sessions Number of active coding sessions")
        prometheus_metrics.append("# TYPE sherpa_active_sessions gauge")
        prometheus_metrics.append(f"sherpa_active_sessions {active_sessions}")
        prometheus_metrics.append("")

        prometheus_metrics.append("# HELP sherpa_uptime_seconds Service uptime in seconds")
        prometheus_metrics.append("# TYPE sherpa_uptime_seconds counter")
        prometheus_metrics.append(f"sherpa_uptime_seconds {uptime_seconds:.0f}")
        prometheus_metrics.append("")

        # Add per-endpoint metrics
        prometheus_metrics.append("# HELP sherpa_requests_by_endpoint Requests per endpoint")
        prometheus_metrics.append("# TYPE sherpa_requests_by_endpoint counter")
        for endpoint, count in metrics_data["requests_by_endpoint"].items():
            # Escape quotes in endpoint name for Prometheus format
            endpoint_label = endpoint.replace('"', '\\"')
            prometheus_metrics.append(f'sherpa_requests_by_endpoint{{endpoint="{endpoint_label}"}} {count}')
        prometheus_metrics.append("")

        prometheus_metrics.append("# HELP sherpa_errors_by_endpoint Errors per endpoint")
        prometheus_metrics.append("# TYPE sherpa_errors_by_endpoint counter")
        for endpoint, count in metrics_data["errors_by_endpoint"].items():
            endpoint_label = endpoint.replace('"', '\\"')
            prometheus_metrics.append(f'sherpa_errors_by_endpoint{{endpoint="{endpoint_label}"}} {count}')
        prometheus_metrics.append("")

        prometheus_text = "\n".join(prometheus_metrics)

        # Build JSON response
        metrics_json = {
            "request_count": total_requests,
            "error_count": total_errors,
            "error_rate": round(error_rate, 2),
            "active_sessions": active_sessions,
            "uptime_seconds": int(uptime_seconds),
            "start_time": metrics_data["start_time"],
            "requests_by_endpoint": dict(metrics_data["requests_by_endpoint"]),
            "errors_by_endpoint": dict(metrics_data["errors_by_endpoint"]),
            "prometheus_format": prometheus_text
        }

        logger.info(f"Metrics requested - Requests: {total_requests}, Errors: {total_errors}, Active Sessions: {active_sessions}")

        return success_response(
            data=metrics_json,
            message="Metrics retrieved successfully"
        )

    except Exception as e:
        logger.error(f"Error retrieving metrics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sessions")
async def get_sessions(status: Optional[str] = None):
    """Get all coding sessions"""
    try:
        logger.debug(f"GET /api/sessions - status filter: {status}")
        db = await get_db()
        sessions = await db.get_sessions(status=status)
        logger.info(f"Retrieved {len(sessions)} sessions (status={status})")
        return success_response(
            data={
                "sessions": sessions,
                "total": len(sessions)
            },
            message=f"Retrieved {len(sessions)} sessions"
        )
    except Exception as e:
        logger.error(f"Error retrieving sessions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/sessions", status_code=201)
async def create_session(request: CreateSessionRequest):
    """Create a new coding session"""
    try:
        logger.info(f"POST /api/sessions - Creating new session with spec_file={request.spec_file}")
        db = await get_db()
        session_id = f"session-{int(datetime.utcnow().timestamp() * 1000)}"
        await db.create_session({
            'id': session_id,
            'spec_file': request.spec_file,
            'status': 'active',
            'total_features': request.total_features,
            'completed_features': 0,
            'work_item_id': request.work_item_id,
            'git_branch': request.git_branch
        })
        logger.info(f"Successfully created session: {session_id}")
        return success_response(
            data={
                "id": session_id,
                "status": "created"
            },
            message="Session created successfully"
        )
    except Exception as e:
        logger.error(f"Error creating session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """Get specific session details"""
    try:
        logger.debug(f"GET /api/sessions/{session_id}")
        db = await get_db()
        session = await db.get_session(session_id)
        if not session:
            logger.warning(f"Session not found: {session_id}")
            raise HTTPException(status_code=404, detail="Session not found")
        logger.info(f"Retrieved session: {session_id}")
        return success_response(
            data=session,
            message="Session retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving session {session_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/api/sessions/{session_id}")
async def update_session(session_id: str, request: Request):
    """Update session progress or status"""
    try:
        logger.debug(f"PATCH /api/sessions/{session_id}")
        db = await get_db()

        # Verify session exists
        session = await db.get_session(session_id)
        if not session:
            logger.warning(f"Session not found for update: {session_id}")
            raise HTTPException(status_code=404, detail="Session not found")

        # Parse request body
        body = await request.json()

        # Build updates dictionary - only allow specific fields
        allowed_fields = ['completed_features', 'status', 'error_message']
        updates = {k: v for k, v in body.items() if k in allowed_fields}

        if not updates:
            logger.warning(f"No valid fields to update for session: {session_id}")
            raise HTTPException(status_code=400, detail="No valid fields to update")

        # Update session
        await db.update_session(session_id, updates)
        logger.info(f"Updated session {session_id}: {updates}")

        # Get updated session
        updated_session = await db.get_session(session_id)

        return success_response(
            data=updated_session,
            message="Session updated successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating session {session_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sessions/{session_id}/progress")
async def get_session_progress(session_id: str):
    """Server-Sent Events endpoint for real-time session progress updates"""
    async def event_generator():
        """Generate SSE events for session progress"""
        try:
            db = await get_db()

            # Verify session exists
            session = await db.get_session(session_id)
            if not session:
                # Send error event and close
                yield f"event: error\ndata: {json.dumps({'error': 'Session not found'})}\n\n"
                return

            # Send initial connection event
            yield f"event: connected\ndata: {json.dumps({'session_id': session_id, 'timestamp': datetime.utcnow().isoformat()})}\n\n"

            # Simulate progress updates (in a real implementation, this would track actual progress)
            # For now, send periodic updates with current session state
            for i in range(10):  # Send 10 progress updates
                await asyncio.sleep(1)  # Wait 1 second between updates

                # Get latest session state
                session = await db.get_session(session_id)
                if not session:
                    break

                # Calculate progress percentage
                total = session.get('total_features', 0)
                completed = session.get('completed_features', 0)
                progress_percent = (completed / total * 100) if total > 0 else 0

                # Send progress event
                progress_data = {
                    'session_id': session_id,
                    'status': session.get('status', 'unknown'),
                    'total_features': total,
                    'completed_features': completed,
                    'progress_percent': round(progress_percent, 2),
                    'timestamp': datetime.utcnow().isoformat(),
                    'update_number': i + 1
                }
                yield f"event: progress\ndata: {json.dumps(progress_data)}\n\n"

                # Stop if session is no longer active
                if session.get('status') not in ['active', 'running']:
                    break

            # Send completion event
            yield f"event: complete\ndata: {json.dumps({'session_id': session_id, 'timestamp': datetime.utcnow().isoformat()})}\n\n"

        except Exception as e:
            # Send error event
            yield f"event: error\ndata: {json.dumps({'error': str(e), 'timestamp': datetime.utcnow().isoformat()})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable buffering in nginx
        }
    )


@app.post("/api/sessions/{session_id}/stop")
async def stop_session(session_id: str):
    """Stop a running session"""
    try:
        db = await get_db()

        # Verify session exists
        session = await db.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Update session status to stopped
        await db.update_session(session_id, {
            'status': 'stopped',
            'completed_at': datetime.utcnow().isoformat()
        })

        return {
            "id": session_id,
            "status": "stopped",
            "message": "Session stopped successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/sessions/{session_id}/pause")
async def pause_session(session_id: str):
    """Pause a running session"""
    try:
        db = await get_db()

        # Verify session exists
        session = await db.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Verify session is active (can only pause active sessions)
        current_status = session.get('status')
        if current_status == 'paused':
            raise HTTPException(status_code=400, detail="Session is already paused")
        if current_status not in ['active', 'running']:
            raise HTTPException(status_code=400, detail=f"Cannot pause session with status: {current_status}")

        # Update session status to paused
        await db.update_session(session_id, {
            'status': 'paused'
        })

        return {
            "id": session_id,
            "status": "paused",
            "message": "Session paused successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/sessions/{session_id}/resume")
async def resume_session(session_id: str):
    """Resume a paused session"""
    try:
        db = await get_db()

        # Verify session exists
        session = await db.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Verify session is paused (can only resume paused sessions)
        current_status = session.get('status')
        if current_status == 'active':
            raise HTTPException(status_code=400, detail="Session is already active")
        if current_status == 'running':
            raise HTTPException(status_code=400, detail="Session is already running")
        if current_status not in ['paused']:
            raise HTTPException(status_code=400, detail=f"Cannot resume session with status: {current_status}")

        # Update session status to active
        await db.update_session(session_id, {
            'status': 'active'
        })

        return {
            "id": session_id,
            "status": "active",
            "message": "Session resumed successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sessions/{session_id}/logs")
async def get_session_logs(session_id: str):
    """Get session logs"""
    try:
        db = await get_db()

        # Verify session exists
        session = await db.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Get logs for this session
        logs = await db.get_logs(session_id)

        return {
            "session_id": session_id,
            "logs": logs,
            "total": len(logs),
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sessions/{session_id}/commits")
async def get_session_commits(session_id: str):
    """Get git commits for session"""
    try:
        db = await get_db()

        # Verify session exists
        session = await db.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Get commits for this session
        commits = await db.get_commits(session_id)

        return {
            "session_id": session_id,
            "commits": commits,
            "total": len(commits),
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/snippets")
async def get_snippets(
    category: Optional[str] = None,
    source: Optional[str] = None
):
    """Get all code snippets from snippet manager"""
    try:
        from sherpa.core.snippet_manager import get_snippet_manager

        # Get snippet manager
        snippet_manager = get_snippet_manager()

        # Load snippets if not already loaded
        snippet_manager.load_snippets()

        # Get snippets
        if source:
            snippets = snippet_manager.get_snippets_by_source(source)
        elif category:
            snippets = snippet_manager.get_snippets_by_category(category)
        else:
            snippets = snippet_manager.get_all_snippets()

        # Convert to dict format
        snippets_data = [
            {
                "id": s.id,
                "title": s.title,
                "category": s.category,
                "content": s.content,
                "source": s.source,
                "file_path": s.file_path,
                "language": s.language,
                "tags": s.tags
            }
            for s in snippets
        ]

        return success_response(
            data={
                "snippets": snippets_data,
                "total": len(snippets_data)
            },
            message=f"Retrieved {len(snippets_data)} snippets"
        )
    except Exception as e:
        logger.error(f"Error getting snippets: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/snippets/{snippet_id}")
async def get_snippet(snippet_id: str):
    """Get snippet by ID"""
    try:
        db = await get_db()
        snippet = await db.get_snippet(snippet_id)

        if not snippet:
            raise HTTPException(status_code=404, detail=f"Snippet not found: {snippet_id}")

        return success_response(
            data=snippet,
            message="Snippet retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/snippets", status_code=201)
async def create_snippet(snippet: CreateSnippetRequest):
    """Create a new snippet and save to appropriate snippets directory based on source"""
    try:
        db = await get_db()

        # Prepare snippet data manually from Pydantic model
        snippet_data = {
            'id': snippet.id,
            'name': snippet.name,
            'category': snippet.category,
            'source': snippet.source,
            'content': snippet.content,
            'language': snippet.language,
            'tags': snippet.tags
        }

        # Create snippet in database
        snippet_id = await db.create_snippet(snippet_data)

        # Determine target directory based on source
        # local -> ./sherpa/snippets.local/
        # project -> ./sherpa/snippets/
        # org and built-in don't save to filesystem
        if snippet.source == "local":
            snippets_dir = Path(__file__).parent.parent / "snippets.local"
        else:
            snippets_dir = Path(__file__).parent.parent / "snippets"

        snippets_dir.mkdir(exist_ok=True)

        # Generate filename from snippet ID
        filename = f"{snippet_id}.md"
        file_path = snippets_dir / filename

        # Write content to markdown file
        with open(file_path, "w") as f:
            f.write(snippet_data['content'])

        # Retrieve the created snippet to return
        created_snippet = await db.get_snippet(snippet_id)

        return {
            "snippet_id": snippet_id,
            "snippet": created_snippet,
            "file_path": str(file_path),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/snippets/query")
async def query_snippets(request: QuerySnippetsRequest):
    """
    Query Bedrock Knowledge Base for relevant code snippets

    Performs semantic search using AWS Bedrock Knowledge Base to find
    relevant snippets based on the query text. Returns snippets with
    relevance scores and metadata.

    In development mode without AWS credentials, returns mock responses.
    """
    try:
        logger.info(f"POST /api/snippets/query - query='{request.query}', max_results={request.max_results}, min_score={request.min_score}")

        # Get or create Bedrock client
        db = await get_db()
        config = await db.get_all_config()
        kb_id = config.get('bedrock_kb_id')

        bedrock_client = get_bedrock_client(kb_id=kb_id)

        # Query Bedrock Knowledge Base
        results = await bedrock_client.query(
            query_text=request.query,
            max_results=request.max_results,
            min_score=request.min_score
        )

        logger.info(f"Bedrock query returned {len(results)} results for query: '{request.query}'")

        # Format results for API response
        formatted_results = []
        for result in results:
            formatted_results.append({
                'content': result.get('content', ''),
                'score': result.get('score', 0.0),
                'metadata': result.get('metadata', {}),
                'location': result.get('location', {}),
                'category': result.get('metadata', {}).get('category', 'general'),
                'tags': result.get('metadata', {}).get('tags', []),
                'language': result.get('metadata', {}).get('language', 'unknown')
            })

        return success_response(
            data={
                'query': request.query,
                'results': formatted_results,
                'total': len(formatted_results),
                'max_results': request.max_results,
                'min_score': request.min_score
            },
            message=f"Found {len(formatted_results)} relevant snippets"
        )

    except Exception as e:
        logger.error(f"Error querying snippets: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/snippets/load-builtin")
async def load_builtin_snippets():
    """Load built-in snippets from markdown files into database"""
    try:
        # Built-in snippets metadata
        BUILT_IN_SNIPPETS = [
            {
                "file": "security-auth.md",
                "id": "snippet-security-auth",
                "name": "Security & Authentication Patterns",
                "category": "security",
                "language": "python, javascript",
                "tags": "authentication, authorization, security, jwt, oauth"
            },
            {
                "file": "python-error-handling.md",
                "id": "snippet-python-error-handling",
                "name": "Python Error Handling Patterns",
                "category": "python",
                "language": "python",
                "tags": "error-handling, exceptions, logging, debugging"
            },
            {
                "file": "python-async.md",
                "id": "snippet-python-async",
                "name": "Python Async/Await Patterns",
                "category": "python",
                "language": "python",
                "tags": "async, asyncio, concurrency, async-await"
            },
            {
                "file": "react-hooks.md",
                "id": "snippet-react-hooks",
                "name": "React Hooks Patterns",
                "category": "react",
                "language": "javascript, typescript",
                "tags": "react, hooks, useState, useEffect, frontend"
            },
            {
                "file": "testing-unit.md",
                "id": "snippet-testing-unit",
                "name": "Unit Testing Patterns",
                "category": "testing",
                "language": "python, javascript",
                "tags": "testing, unit-tests, pytest, jest, tdd"
            },
            {
                "file": "api-rest.md",
                "id": "snippet-api-rest",
                "name": "REST API Best Practices",
                "category": "api",
                "language": "python, javascript",
                "tags": "api, rest, http, fastapi, express"
            },
            {
                "file": "git-commits.md",
                "id": "snippet-git-commits",
                "name": "Git Commit Best Practices",
                "category": "git",
                "language": "markdown",
                "tags": "git, commits, version-control, best-practices"
            }
        ]

        snippets_dir = Path(__file__).parent.parent / "snippets"

        if not snippets_dir.exists():
            raise HTTPException(status_code=500, detail=f"Snippets directory not found: {snippets_dir}")

        db = await get_db()

        # Check if snippets already exist
        existing_snippets = await db.get_snippets()
        if existing_snippets:
            # Clear existing snippets
            conn = await db.connect()
            await conn.execute("DELETE FROM snippets")
            await conn.commit()

        # Load each snippet
        loaded_count = 0
        errors = []

        for snippet_meta in BUILT_IN_SNIPPETS:
            snippet_file = snippets_dir / snippet_meta["file"]

            if not snippet_file.exists():
                errors.append(f"Snippet file not found: {snippet_file}")
                continue

            # Read snippet content
            with open(snippet_file, 'r') as f:
                content = f.read()

            # Create snippet in database
            snippet_data = {
                "id": snippet_meta["id"],
                "name": snippet_meta["name"],
                "category": snippet_meta["category"],
                "source": "built-in",
                "content": content,
                "language": snippet_meta["language"],
                "tags": snippet_meta["tags"]
            }

            try:
                await db.create_snippet(snippet_data)
                loaded_count += 1
            except Exception as e:
                errors.append(f"Failed to load {snippet_meta['name']}: {str(e)}")

        # Get final count
        all_snippets = await db.get_snippets()

        return {
            "status": "success",
            "loaded": loaded_count,
            "total_in_db": len(all_snippets),
            "errors": errors if errors else None,
            "timestamp": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/config")
async def get_config():
    """Get configuration"""
    try:
        db = await get_db()
        config = await db.get_all_config()

        return {
            "bedrock_configured": bool(config.get('bedrock_kb_id')),
            "azure_devops_configured": bool(config.get('azure_devops_org')),
            "config": config,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/config")
async def set_config_value(request: Request):
    """Set a configuration value"""
    try:
        body = await request.json()
        key = body.get('key')
        value = body.get('value')

        if not key:
            raise HTTPException(status_code=400, detail="key is required")

        if value is None:
            raise HTTPException(status_code=400, detail="value is required")

        db = await get_db()
        await db.set_config(key, value)

        return success_response(
            data={"key": key, "value": value},
            message=f"Configuration value set for key: {key}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting config: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/config")
async def update_config(request: Request):
    """Update configuration with config manager"""
    try:
        from sherpa.core.config_manager import get_config_manager

        body = await request.json()

        # Get config manager
        config_manager = get_config_manager()

        # Update configuration
        config_manager.update(body)

        return success_response(
            data=config_manager.get().dict(),
            message="Configuration updated successfully"
        )
    except Exception as e:
        logger.error(f"Error updating config: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/environment")
async def get_environment():
    """
    Get current environment configuration

    Returns environment settings including:
    - environment: current environment (development, staging, production)
    - debug: debug mode enabled/disabled
    - log_level: logging level
    - cors_origins: allowed CORS origins
    - api_rate_limit: API rate limit settings
    - database_path: database file path
    """
    try:
        settings = get_settings()
        config = settings.get_config_dict()

        logger.info(f"GET /api/environment - Current environment: {settings.environment.value}")

        return success_response(
            data=config,
            message=f"Environment configuration retrieved: {settings.environment.value}"
        )
    except Exception as e:
        logger.error(f"Error getting environment config: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/environment")
async def set_environment(request: Request):
    """
    Set environment configuration programmatically

    Request body:
    {
        "environment": "development" | "staging" | "production"
    }

    This endpoint allows changing the environment at runtime for testing purposes.
    In production, environment should be set via SHERPA_ENV environment variable.
    """
    try:
        body = await request.json()
        env = body.get('environment')

        if not env:
            raise HTTPException(status_code=400, detail="environment field is required")

        settings = get_settings()
        old_env = settings.environment.value

        # Set new environment
        try:
            settings.set_environment(env)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        new_env = settings.environment.value
        logger.info(f"POST /api/environment - Changed environment from {old_env} to {new_env}")

        return success_response(
            data=settings.get_config_dict(),
            message=f"Environment changed from {old_env} to {new_env}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting environment: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate")
async def generate_instruction_files(request: Optional[GenerateInstructionFilesRequest] = None):
    """
    Generate instruction files for interactive agents
    Creates:
    - .cursor/rules/00-sherpa-knowledge.md
    - CLAUDE.md
    - copilot-instructions.md

    Files are generated in the specified target_directory or current working directory
    with organizational knowledge snippets injected.
    """
    try:
        logger.info(f"POST /api/generate - Generating instruction files")

        # Determine target directory
        if request and request.target_directory:
            target_dir = Path(request.target_directory)
        else:
            target_dir = Path.cwd()

        logger.info(f"Target directory: {target_dir}")

        # Verify target directory exists
        if not target_dir.exists():
            logger.error(f"Target directory does not exist: {target_dir}")
            raise HTTPException(status_code=400, detail=f"Target directory does not exist: {target_dir}")

        # Get snippets from sherpa/snippets directory
        sherpa_root = Path(__file__).parent.parent
        snippets_dir = sherpa_root / "snippets"

        # Load all snippet files
        snippets = await load_snippets_for_generation(snippets_dir)

        logger.info(f"Loaded {len(snippets)} snippets from {snippets_dir}")

        # Create .cursor/rules/ directory
        cursor_rules_dir = target_dir / ".cursor" / "rules"
        cursor_rules_dir.mkdir(parents=True, exist_ok=True)

        # Generate files
        files_created = []

        # 1. Generate .cursor/rules/00-sherpa-knowledge.md
        cursor_rules_file = cursor_rules_dir / "00-sherpa-knowledge.md"
        await generate_cursor_rules_content(cursor_rules_file, snippets)
        files_created.append({
            "path": str(cursor_rules_file.relative_to(target_dir)),
            "size": cursor_rules_file.stat().st_size,
            "snippets": len(snippets)
        })
        logger.info(f"Created: {cursor_rules_file}")

        # 2. Generate CLAUDE.md
        claude_file = target_dir / "CLAUDE.md"
        await generate_claude_md_content(claude_file, snippets)
        files_created.append({
            "path": str(claude_file.relative_to(target_dir)),
            "size": claude_file.stat().st_size,
            "snippets": len(snippets)
        })
        logger.info(f"Created: {claude_file}")

        # 3. Generate copilot-instructions.md
        copilot_file = target_dir / "copilot-instructions.md"
        await generate_copilot_instructions_content(copilot_file, snippets)
        files_created.append({
            "path": str(copilot_file.relative_to(target_dir)),
            "size": copilot_file.stat().st_size,
            "snippets": len(snippets)
        })
        logger.info(f"Created: {copilot_file}")

        logger.info(f"Successfully generated {len(files_created)} instruction files")

        return success_response(
            data={
                "files": files_created,
                "total_files": len(files_created),
                "total_snippets": len(snippets),
                "target_directory": str(target_dir)
            },
            message=f"Successfully generated {len(files_created)} instruction files with {len(snippets)} snippets"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating instruction files: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


async def load_snippets_for_generation(snippets_dir: Path) -> list:
    """
    Load all snippet files from the snippets directory
    Returns list of dicts with snippet metadata and content
    """
    snippets = []

    if not snippets_dir.exists():
        logger.warning(f"Snippets directory does not exist: {snippets_dir}")
        return snippets

    # Find all .md files in snippets directory
    for snippet_file in snippets_dir.glob("*.md"):
        # Skip test files
        if snippet_file.name.startswith("test-") or snippet_file.name.startswith("snippet-"):
            continue

        try:
            content = snippet_file.read_text()

            # Extract metadata from content
            title = snippet_file.stem.replace("-", " ").title()
            category = extract_category_from_content(content)

            snippets.append({
                "name": snippet_file.stem,
                "title": title,
                "category": category,
                "content": content,
                "file": snippet_file.name
            })
            logger.debug(f"Loaded snippet: {snippet_file.name}")
        except Exception as e:
            logger.warning(f"Could not load {snippet_file.name}: {str(e)}")

    return snippets


def extract_category_from_content(content: str) -> str:
    """Extract category from snippet content"""
    for line in content.split("\n"):
        if line.startswith("## Category:"):
            return line.replace("## Category:", "").strip()
    return "general"


async def generate_cursor_rules_content(file_path: Path, snippets: list):
    """Generate .cursor/rules/00-sherpa-knowledge.md file"""
    content = """# SHERPA Knowledge Base

This file contains organizational knowledge and best practices injected by SHERPA.
Use these patterns and snippets as reference when coding.

"""

    if snippets:
        content += "## Available Knowledge Snippets\n\n"
        for snippet in snippets:
            content += f"### {snippet['title']}\n\n"
            content += f"**Category:** {snippet['category']}\n\n"
            content += snippet['content'] + "\n\n"
            content += "---\n\n"
    else:
        content += """## Default Configuration

No custom snippets found. Add snippets to `sherpa/snippets/` directory.

### Example Snippet Structure

Create `.md` files in `sherpa/snippets/` with this format:

```markdown
# Snippet Title

## Category: category/subcategory
## Language: python, javascript
## Tags: tag1, tag2, tag3

## Description

Your snippet content here...
```
"""

    file_path.write_text(content)


async def generate_claude_md_content(file_path: Path, snippets: list):
    """Generate CLAUDE.md file with injected knowledge"""
    content = """# Claude Development Instructions

This file contains development guidelines and organizational knowledge for Claude Code.

## Project Context

This project uses SHERPA to enhance development with organizational knowledge.

## Knowledge Base

"""

    if snippets:
        content += "The following knowledge snippets are available for reference:\n\n"
        for snippet in snippets:
            content += f"### {snippet['title']}\n\n"
            content += snippet['content'] + "\n\n"
    else:
        content += """No custom snippets loaded. Add snippets to `sherpa/snippets/` directory.

Run `sherpa generate` to regenerate this file after adding snippets.
"""

    content += """
## Development Guidelines

- Follow the patterns and best practices outlined in the knowledge snippets above
- Use organizational standards for code structure and naming conventions
- Refer to snippet examples when implementing similar functionality
- Keep code consistent with existing patterns

---

*Generated by SHERPA V1 - Autonomous Coding Orchestrator*
"""

    file_path.write_text(content)


async def generate_copilot_instructions_content(file_path: Path, snippets: list):
    """Generate copilot-instructions.md file"""
    content = """# GitHub Copilot Instructions

This file provides context and instructions for GitHub Copilot.

## Project Guidelines

This project uses SHERPA for knowledge management and follows organizational best practices.

## Code Patterns

"""

    if snippets:
        content += "Please follow these organizational patterns when suggesting code:\n\n"
        for snippet in snippets:
            content += f"### {snippet['title']}\n\n"
            content += f"Category: {snippet['category']}\n\n"
            # Include first 500 characters of each snippet as context
            snippet_preview = snippet['content'][:500]
            if len(snippet['content']) > 500:
                snippet_preview += "...\n\n[See full snippet in .cursor/rules/00-sherpa-knowledge.md]"
            content += snippet_preview + "\n\n"
    else:
        content += """No custom patterns loaded. Add snippets to `sherpa/snippets/` directory.

Run `sherpa generate` to regenerate this file.
"""

    content += """
## Instructions

- Follow organizational coding standards
- Use patterns from the knowledge base above
- Maintain consistency with existing code
- Prioritize security and best practices

---

*Generated by SHERPA V1*
"""

    file_path.write_text(content)


@app.post("/api/azure-devops/connect")
async def connect_azure_devops(request: AzureDevOpsConnectRequest):
    """Test Azure DevOps connection with provided credentials"""
    try:
        logger.info(f"POST /api/azure-devops/connect - organization={request.organization}, project={request.project}, pat=***REDACTED***")

        # Validate inputs
        if not request.organization or not request.project or not request.pat:
            logger.warning("Azure DevOps connection attempt with missing credentials")
            raise HTTPException(status_code=400, detail="Organization, project, and PAT are required")

        # Get Azure DevOps client
        azure_client = get_azure_devops_client()

        # Attempt to connect
        try:
            result = await azure_client.connect(
                organization=request.organization,
                project=request.project,
                pat=request.pat
            )

            logger.info(f"Successfully connected to Azure DevOps: {request.organization}/{request.project}")

            # Save configuration to database for future use
            db = await get_db()
            await db.set_config('azure_devops_org', request.organization)
            await db.set_config('azure_devops_project', request.project)
            await db.set_config('azure_devops_pat', request.pat)  # Note: In production, encrypt this!

            return {
                "success": True,
                "message": result.get("message", "Successfully connected to Azure DevOps"),
                "organization": request.organization,
                "project": request.project,
                "connection_status": result.get("connection_status", "connected"),
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as conn_error:
            logger.error(f"Azure DevOps connection failed: {str(conn_error)}")
            raise HTTPException(
                status_code=401,
                detail=f"Failed to connect to Azure DevOps: {str(conn_error)}"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Azure DevOps connection error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Connection error: {str(e)}")


@app.get("/api/azure-devops/work-items")
async def get_azure_devops_work_items(query: Optional[str] = None, top: int = 100):
    """Fetch work items from Azure DevOps"""
    try:
        logger.info(f"GET /api/azure-devops/work-items - query={query}, top={top}")

        # Get Azure DevOps client
        azure_client = get_azure_devops_client()

        # Check if connected
        if not azure_client.is_connected:
            # Try to restore connection from database
            db = await get_db()
            org = await db.get_config('azure_devops_org')
            project = await db.get_config('azure_devops_project')
            pat = await db.get_config('azure_devops_pat')

            if not org or not project or not pat:
                logger.warning("Azure DevOps not configured - credentials not found in database")
                raise HTTPException(
                    status_code=401,
                    detail="Azure DevOps not configured. Please connect first using POST /api/azure-devops/connect"
                )

            # Reconnect using stored credentials
            try:
                await azure_client.connect(
                    organization=org,
                    project=project,
                    pat=pat
                )
                logger.info(f"Reconnected to Azure DevOps: {org}/{project}")
            except Exception as conn_error:
                logger.error(f"Failed to reconnect to Azure DevOps: {str(conn_error)}")
                raise HTTPException(
                    status_code=401,
                    detail=f"Failed to reconnect to Azure DevOps: {str(conn_error)}"
                )

        # Fetch work items
        try:
            work_items = await azure_client.get_work_items(query=query, top=top)

            logger.info(f"Successfully fetched {len(work_items)} work items from Azure DevOps")

            return {
                "success": True,
                "work_items": work_items,
                "count": len(work_items),
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as fetch_error:
            logger.error(f"Failed to fetch work items: {str(fetch_error)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch work items: {str(fetch_error)}"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching work items: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error fetching work items: {str(e)}")


@app.post("/api/azure-devops/work-items/{work_item_id}/update")
async def update_azure_devops_work_item(work_item_id: int, request: AzureDevOpsUpdateWorkItemRequest):
    """
    Update a work item in Azure DevOps

    Args:
        work_item_id: ID of the work item to update
        request: Update request containing field updates

    Returns:
        Updated work item details
    """
    try:
        logger.info(f"POST /api/azure-devops/work-items/{work_item_id}/update - updates={list(request.updates.keys())}")

        # Get Azure DevOps client
        from sherpa.core.integrations.azure_devops_client import get_azure_devops_client
        azure_client = get_azure_devops_client()

        # Check if connected
        if not azure_client.is_connected:
            logger.info("Azure DevOps client not connected, attempting to reconnect...")

            # Try to restore connection from database
            db = await get_db()
            config = await db.get_all_config()

            org = config.get('azure_devops_org')
            project = config.get('azure_devops_project')
            pat = config.get('azure_devops_pat')

            if not org or not project or not pat:
                logger.warning("Azure DevOps credentials not found in database")
                raise HTTPException(
                    status_code=401,
                    detail="Azure DevOps not configured. Please connect first using POST /api/azure-devops/connect"
                )

            # Extract organization name from URL if needed
            if org.startswith('https://dev.azure.com/'):
                org_name = org.replace('https://dev.azure.com/', '').rstrip('/')
            elif org.startswith('http://dev.azure.com/'):
                org_name = org.replace('http://dev.azure.com/', '').rstrip('/')
            else:
                org_name = org

            # Reconnect
            try:
                await azure_client.connect(org_name, project, pat)
                logger.info("Successfully reconnected to Azure DevOps")
            except Exception as reconnect_error:
                logger.error(f"Failed to reconnect to Azure DevOps: {str(reconnect_error)}")
                raise HTTPException(
                    status_code=401,
                    detail=f"Failed to reconnect to Azure DevOps: {str(reconnect_error)}"
                )

        # Update work item
        try:
            result = await azure_client.update_work_item(work_item_id, request.updates)
            logger.info(f"Successfully updated work item {work_item_id}")

            return {
                "success": True,
                "work_item_id": work_item_id,
                "updates": request.updates,
                "result": result,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as update_error:
            logger.error(f"Failed to update work item {work_item_id}: {str(update_error)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to update work item: {str(update_error)}"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating work item {work_item_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error updating work item: {str(e)}")


@app.post("/api/azure-devops/work-items/{work_item_id}/comment")
async def add_comment_to_work_item(work_item_id: int, request: Request):
    """
    Add a comment to a work item in Azure DevOps

    Args:
        work_item_id: ID of the work item to add comment to
        request: Request body containing comment text

    Returns:
        Comment result details
    """
    try:
        body = await request.json()
        comment_text = body.get('comment', body.get('text', ''))

        if not comment_text:
            raise HTTPException(status_code=400, detail="Comment text is required")

        logger.info(f"POST /api/azure-devops/work-items/{work_item_id}/comment - comment length={len(comment_text)}")

        # Get Azure DevOps client
        from sherpa.core.integrations.azure_devops_client import get_azure_devops_client
        azure_client = get_azure_devops_client()

        # Check if connected
        if not azure_client.is_connected:
            logger.info("Azure DevOps client not connected, attempting to reconnect...")

            # Try to restore connection from database
            db = await get_db()
            config = await db.get_all_config()

            org = config.get('azure_devops_org')
            project = config.get('azure_devops_project')
            pat = config.get('azure_devops_pat')

            if not org or not project or not pat:
                logger.warning("Azure DevOps credentials not found in database")
                raise HTTPException(
                    status_code=401,
                    detail="Azure DevOps not configured. Please connect first using POST /api/azure-devops/connect"
                )

            # Extract organization name from URL if needed
            if org.startswith('https://dev.azure.com/'):
                org_name = org.replace('https://dev.azure.com/', '').rstrip('/')
            elif org.startswith('http://dev.azure.com/'):
                org_name = org.replace('http://dev.azure.com/', '').rstrip('/')
            else:
                org_name = org

            # Reconnect
            try:
                await azure_client.connect(org_name, project, pat)
                logger.info("Successfully reconnected to Azure DevOps")
            except Exception as reconnect_error:
                logger.error(f"Failed to reconnect to Azure DevOps: {str(reconnect_error)}")
                raise HTTPException(
                    status_code=401,
                    detail=f"Failed to reconnect to Azure DevOps: {str(reconnect_error)}"
                )

        # Add comment to work item
        try:
            result = await azure_client.add_comment(work_item_id, comment_text)
            logger.info(f"Successfully added comment to work item {work_item_id}")

            return {
                "success": True,
                "work_item_id": work_item_id,
                "comment": comment_text,
                "result": result,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as comment_error:
            logger.error(f"Failed to add comment to work item {work_item_id}: {str(comment_error)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to add comment: {str(comment_error)}"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding comment to work item {work_item_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error adding comment: {str(e)}")


@app.post("/api/azure-devops/work-items/{work_item_id}/convert-to-spec")
async def convert_work_item_to_spec(work_item_id: int):
    """
    Convert an Azure DevOps work item to app_spec.txt format

    Args:
        work_item_id: ID of the work item to convert

    Returns:
        Spec file content and metadata
    """
    try:
        logger.info(f"POST /api/azure-devops/work-items/{work_item_id}/convert-to-spec")

        # Get Azure DevOps client
        azure_client = get_azure_devops_client()

        # Check if connected
        if not azure_client.is_connected:
            logger.info("Azure DevOps client not connected, attempting to reconnect...")

            # Try to restore connection from database
            db = await get_db()
            config = await db.get_all_config()

            org = config.get('azure_devops_org')
            project = config.get('azure_devops_project')
            pat = config.get('azure_devops_pat')

            if not org or not project or not pat:
                logger.warning("Azure DevOps credentials not found in database")
                raise HTTPException(
                    status_code=401,
                    detail="Azure DevOps not configured. Please connect first using POST /api/azure-devops/connect"
                )

            # Extract organization name from URL if needed
            if org.startswith('https://dev.azure.com/'):
                org_name = org.replace('https://dev.azure.com/', '').rstrip('/')
            elif org.startswith('http://dev.azure.com/'):
                org_name = org.replace('http://dev.azure.com/', '').rstrip('/')
            else:
                org_name = org

            try:
                await azure_client.connect(org_name, project, pat)
                logger.info("Successfully reconnected to Azure DevOps")
            except Exception as reconnect_error:
                logger.error(f"Failed to reconnect to Azure DevOps: {str(reconnect_error)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to reconnect to Azure DevOps: {str(reconnect_error)}"
                )

        # Convert work item to spec
        try:
            spec_content = await azure_client.convert_work_item_to_spec(work_item_id)

            # Save spec to file
            import os
            specs_dir = "specs"
            os.makedirs(specs_dir, exist_ok=True)
            spec_filename = f"work_item_{work_item_id}_spec.txt"
            spec_path = os.path.join(specs_dir, spec_filename)

            with open(spec_path, 'w') as f:
                f.write(spec_content)

            logger.info(f"Successfully converted work item {work_item_id} to spec and saved to {spec_path}")

            return {
                "success": True,
                "work_item_id": work_item_id,
                "spec_content": spec_content,
                "spec_filename": spec_filename,
                "spec_path": spec_path,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as convert_error:
            logger.error(f"Failed to convert work item {work_item_id} to spec: {str(convert_error)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to convert work item to spec: {str(convert_error)}"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error converting work item {work_item_id} to spec: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error converting work item to spec: {str(e)}")


@app.post("/api/azure-devops/work-items/{work_item_id}/commits")
async def link_commit_to_work_item(work_item_id: int, request: Request):
    """
    Link a git commit to a work item in Azure DevOps

    Args:
        work_item_id: ID of the work item to link commit to
        request: Request body containing commit details

    Returns:
        Link result details
    """
    try:
        body = await request.json()
        commit_hash = body.get('commit_hash', body.get('hash', ''))
        commit_message = body.get('commit_message', body.get('message', ''))
        commit_url = body.get('commit_url', body.get('url', None))

        if not commit_hash:
            raise HTTPException(status_code=400, detail="commit_hash is required")

        if not commit_message:
            raise HTTPException(status_code=400, detail="commit_message is required")

        logger.info(f"POST /api/azure-devops/work-items/{work_item_id}/commits - commit={commit_hash[:7]}")

        # Get Azure DevOps client
        azure_client = get_azure_devops_client()

        # Check if connected
        if not azure_client.is_connected:
            logger.info("Azure DevOps client not connected, attempting to reconnect...")

            # Try to restore connection from database
            db = await get_db()
            config = await db.get_all_config()

            org = config.get('azure_devops_org')
            project = config.get('azure_devops_project')
            pat = config.get('azure_devops_pat')

            if not org or not project or not pat:
                logger.warning("Azure DevOps credentials not found in database")
                raise HTTPException(
                    status_code=401,
                    detail="Azure DevOps not configured. Please connect first using POST /api/azure-devops/connect"
                )

            # Extract organization name from URL if needed
            if org.startswith('https://dev.azure.com/'):
                org_name = org.replace('https://dev.azure.com/', '').rstrip('/')
            elif org.startswith('http://dev.azure.com/'):
                org_name = org.replace('http://dev.azure.com/', '').rstrip('/')
            else:
                org_name = org

            # Reconnect
            try:
                await azure_client.connect(org_name, project, pat)
                logger.info("Successfully reconnected to Azure DevOps")
            except Exception as reconnect_error:
                logger.error(f"Failed to reconnect to Azure DevOps: {str(reconnect_error)}")
                raise HTTPException(
                    status_code=401,
                    detail=f"Failed to reconnect to Azure DevOps: {str(reconnect_error)}"
                )

        # Link commit to work item
        try:
            result = await azure_client.link_commit(
                work_item_id=work_item_id,
                commit_hash=commit_hash,
                commit_message=commit_message,
                commit_url=commit_url
            )
            logger.info(f"Successfully linked commit {commit_hash} to work item {work_item_id}")

            return {
                "success": True,
                "work_item_id": work_item_id,
                "commit_hash": commit_hash,
                "commit_message": commit_message,
                "commit_url": result.get('commit_url'),
                "result": result,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as link_error:
            logger.error(f"Failed to link commit to work item {work_item_id}: {str(link_error)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to link commit: {str(link_error)}"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error linking commit to work item {work_item_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error linking commit: {str(e)}")


@app.post("/api/azure-devops/save-config")
async def save_azure_devops_config(request: AzureDevOpsSaveConfigRequest):
    """Save Azure DevOps configuration to database"""
    try:
        db = await get_db()

        # Validate inputs
        if not request.organization or not request.project or not request.pat:
            raise HTTPException(status_code=400, detail="Organization, project, and PAT are required")

        # Format organization URL
        if not (request.organization.startswith('http://') or request.organization.startswith('https://')):
            if not request.organization.startswith('dev.azure.com/'):
                org_url = f"https://dev.azure.com/{request.organization}"
            else:
                org_url = f"https://{request.organization}"
        else:
            org_url = request.organization

        # Save to database configuration
        await db.set_config('azure_devops_org', org_url)
        await db.set_config('azure_devops_project', request.project)
        await db.set_config('azure_devops_pat', request.pat)  # Note: In production, encrypt this!

        return {
            "success": True,
            "message": "Configuration saved successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save configuration: {str(e)}")


@app.get("/api/azure-devops/status")
async def get_azure_devops_status():
    """Get Azure DevOps sync status"""
    try:
        db = await get_db()

        # Get configuration to check if Azure DevOps is configured
        config = await db.get_all_config()

        if not config.get('azure_devops_org'):
            return {
                "configured": False,
                "last_sync": None,
                "status": "not_configured",
                "work_items_count": 0,
                "timestamp": datetime.utcnow().isoformat()
            }

        # Get last sync info from config (in production, track this properly)
        last_sync = config.get('azure_devops_last_sync')

        return {
            "configured": True,
            "last_sync": last_sync,
            "status": "success" if last_sync else "never_synced",
            "work_items_count": 0,  # In production, query actual count
            "organization": config.get('azure_devops_org'),
            "project": config.get('azure_devops_project'),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/azure-devops/sync")
async def sync_azure_devops():
    """Trigger manual sync with Azure DevOps (legacy endpoint)"""
    try:
        db = await get_db()

        # Get configuration to check if Azure DevOps is configured
        config = await db.get_all_config()

        if not config.get('azure_devops_org'):
            raise HTTPException(status_code=400, detail="Azure DevOps is not configured")

        # Simulate sync delay (in production, this would fetch work items from Azure DevOps)
        await asyncio.sleep(1.0)

        # Update last sync time
        sync_time = datetime.utcnow().isoformat()
        await db.set_config('azure_devops_last_sync', sync_time)

        return {
            "success": True,
            "message": "Sync completed successfully",
            "last_sync": sync_time,
            "work_items_synced": 0,  # In production, return actual count
            "timestamp": sync_time
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")


@app.get("/api/azure-devops/work-items/{work_item_id}/detect-changes")
async def detect_work_item_changes(work_item_id: int):
    """Detect if a work item has changed since last sync"""
    try:
        db = await get_db()
        azure_client = get_azure_devops_client()

        # Check if connected
        if not azure_client.is_connected:
            # Try to auto-reconnect using saved config
            config = await db.get_all_config()
            if config.get('azure_devops_org') and config.get('azure_devops_project') and config.get('azure_devops_pat'):
                await azure_client.connect(
                    config['azure_devops_org'],
                    config['azure_devops_project'],
                    config['azure_devops_pat']
                )
            else:
                raise HTTPException(status_code=400, detail="Azure DevOps not connected. Please connect first.")

        # Get last sync record
        last_sync = await db.get_last_sync("work_item", str(work_item_id), "azure_to_sherpa")
        last_sync_hash = last_sync['last_sync_hash'] if last_sync else None

        # Detect changes
        result = await azure_client.detect_work_item_changes(work_item_id, last_sync_hash)

        return {
            "success": True,
            "work_item_id": work_item_id,
            "has_changed": result["has_changed"],
            "current_hash": result["current_hash"],
            "last_sync_hash": last_sync_hash,
            "last_synced_at": last_sync['last_synced_at'] if last_sync else None,
            "work_item": result["work_item"],
            "timestamp": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to detect changes for work item {work_item_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to detect changes: {str(e)}")


@app.post("/api/azure-devops/work-items/{work_item_id}/sync-to-sherpa")
async def sync_work_item_to_sherpa(work_item_id: int, session_id: str = Body(..., embed=True)):
    """Sync work item from Azure DevOps to SHERPA"""
    try:
        db = await get_db()
        azure_client = get_azure_devops_client()

        # Check if connected
        if not azure_client.is_connected:
            # Try to auto-reconnect using saved config
            config = await db.get_all_config()
            if config.get('azure_devops_org') and config.get('azure_devops_project') and config.get('azure_devops_pat'):
                await azure_client.connect(
                    config['azure_devops_org'],
                    config['azure_devops_project'],
                    config['azure_devops_pat']
                )
            else:
                raise HTTPException(status_code=400, detail="Azure DevOps not connected. Please connect first.")

        # Verify session exists
        session = await db.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")

        # Perform sync
        result = await azure_client.sync_work_item_to_sherpa(work_item_id, session_id)

        # Record sync
        if result["success"]:
            await db.record_sync(
                entity_type="work_item",
                entity_id=str(work_item_id),
                source="azure_devops",
                destination="sherpa",
                sync_direction="azure_to_sherpa",
                status="success",
                sync_hash=result.get("sync_hash"),
                metadata=json.dumps({"session_id": session_id})
            )
        else:
            await db.record_sync(
                entity_type="work_item",
                entity_id=str(work_item_id),
                source="azure_devops",
                destination="sherpa",
                sync_direction="azure_to_sherpa",
                status="error",
                error_message=result.get("error"),
                metadata=json.dumps({"session_id": session_id})
            )

        return {
            **result,
            "timestamp": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to sync work item {work_item_id} to SHERPA: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to sync: {str(e)}")


@app.post("/api/azure-devops/sessions/{session_id}/sync-to-azure")
async def sync_session_to_azure(session_id: str, work_item_id: int = Body(..., embed=True)):
    """Sync SHERPA session to Azure DevOps work item"""
    try:
        db = await get_db()
        azure_client = get_azure_devops_client()

        # Check if connected
        if not azure_client.is_connected:
            # Try to auto-reconnect using saved config
            config = await db.get_all_config()
            if config.get('azure_devops_org') and config.get('azure_devops_project') and config.get('azure_devops_pat'):
                await azure_client.connect(
                    config['azure_devops_org'],
                    config['azure_devops_project'],
                    config['azure_devops_pat']
                )
            else:
                raise HTTPException(status_code=400, detail="Azure DevOps not connected. Please connect first.")

        # Get session
        session = await db.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")

        # Perform sync
        result = await azure_client.sync_sherpa_to_work_item(work_item_id, session)

        # Record sync
        if result["success"]:
            await db.record_sync(
                entity_type="session",
                entity_id=session_id,
                source="sherpa",
                destination="azure_devops",
                sync_direction="sherpa_to_azure",
                status="success",
                metadata=json.dumps({"work_item_id": work_item_id})
            )
        else:
            await db.record_sync(
                entity_type="session",
                entity_id=session_id,
                source="sherpa",
                destination="azure_devops",
                sync_direction="sherpa_to_azure",
                status="error",
                error_message=result.get("error"),
                metadata=json.dumps({"work_item_id": work_item_id})
            )

        return {
            **result,
            "timestamp": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to sync session {session_id} to Azure DevOps: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to sync: {str(e)}")


@app.get("/api/sync-status/{entity_type}/{entity_id}")
async def get_entity_sync_status(entity_type: str, entity_id: str):
    """Get sync status for an entity"""
    try:
        db = await get_db()

        # Validate entity_type
        valid_types = ["work_item", "session"]
        if entity_type not in valid_types:
            raise HTTPException(status_code=400, detail=f"Invalid entity_type. Must be one of: {valid_types}")

        # Get sync status
        sync_records = await db.get_sync_status(entity_type, entity_id)

        return {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "sync_records": sync_records,
            "total": len(sync_records),
            "last_sync": sync_records[0] if sync_records else None,
            "timestamp": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get sync status for {entity_type}/{entity_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get sync status: {str(e)}")


@app.get("/api/activity")
async def get_recent_activity(limit: int = 10):
    """Get recent activity events from sessions"""
    try:
        db = await get_db()

        # Get all sessions ordered by creation date
        all_sessions = await db.get_sessions()

        # Sort by started_at (most recent first)
        sorted_sessions = sorted(
            all_sessions,
            key=lambda s: s.get('started_at', ''),
            reverse=True
        )

        # Take the most recent sessions up to the limit
        recent_sessions = sorted_sessions[:limit]

        # Create activity events from sessions
        activity_events = []
        for session in recent_sessions:
            session_name = session.get('spec_file') or session.get('id', 'Unknown')
            status = session.get('status', 'unknown')
            started_at = session.get('started_at')
            completed_at = session.get('completed_at')

            # Determine event type and message
            if status == 'complete' and completed_at:
                event_type = "session_completed"
                message = f"Session '{session_name}' completed successfully"
                timestamp = completed_at
            elif status == 'error':
                event_type = "session_error"
                message = f"Session '{session_name}' encountered an error"
                timestamp = completed_at or started_at
            elif status == 'stopped':
                event_type = "session_stopped"
                message = f"Session '{session_name}' was stopped"
                timestamp = completed_at or started_at
            elif status == 'paused':
                event_type = "session_paused"
                message = f"Session '{session_name}' was paused"
                timestamp = started_at
            elif status == 'active':
                event_type = "session_started"
                message = f"Session '{session_name}' started"
                timestamp = started_at
            else:
                event_type = "session_event"
                message = f"Session '{session_name}' status: {status}"
                timestamp = started_at

            activity_events.append({
                "id": f"event-{session.get('id')}-{event_type}",
                "type": event_type,
                "message": message,
                "timestamp": timestamp,
                "session_id": session.get('id'),
                "session_name": session_name,
                "status": status
            })

        return {
            "events": activity_events,
            "total": len(activity_events),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/sessions/{session_id}/test-data")
async def add_test_data(session_id: str):
    """Add test logs and commits to a session for testing purposes"""
    try:
        db = await get_db()

        # Verify session exists
        session = await db.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        conn = await db.connect()

        # Add test logs with different levels
        test_logs = [
            ("INFO", f"Session {session_id} started"),
            ("INFO", "Initializing autonomous coding agent..."),
            ("INFO", "Loading knowledge snippets from database"),
            ("INFO", "Found 7 built-in snippets"),
            ("WARNING", "No local snippets found in ./sherpa/snippets.local/"),
            ("INFO", "Starting feature implementation"),
            ("INFO", "Implementing feature 1: Backend FastAPI server initialization"),
            ("INFO", "Running tests for feature 1"),
            ("INFO", "✅ Feature 1 tests passed"),
            ("INFO", "Implementing feature 2: SQLite database with aiosqlite"),
            ("ERROR", "Failed to connect to database on first attempt"),
            ("INFO", "Retrying database connection..."),
            ("INFO", "✅ Database connection successful"),
            ("INFO", "Running tests for feature 2"),
            ("INFO", "✅ Feature 2 tests passed"),
            ("INFO", "Committing changes to git"),
            ("INFO", "Progress: 2/50 features completed (4%)"),
        ]

        for level, message in test_logs:
            await conn.execute("""
                INSERT INTO session_logs (session_id, level, message, timestamp)
                VALUES (?, ?, ?, ?)
            """, (session_id, level, message, datetime.utcnow().isoformat()))

        # Add test git commits
        test_commits = [
            {
                "hash": "a1b2c3d",
                "message": "Implement backend FastAPI server initialization\n\n- Added main.py with FastAPI app\n- Configured CORS for frontend\n- Added health check endpoint",
                "author": "Autonomous Agent",
                "files_changed": 3
            },
            {
                "hash": "e4f5g6h",
                "message": "Implement SQLite database with aiosqlite\n\n- Created database schema\n- Added sessions table\n- Added snippets table\n- Implemented async database operations",
                "author": "Autonomous Agent",
                "files_changed": 5
            },
            {
                "hash": "i7j8k9l",
                "message": "Add session logs and git commits tables\n\n- Extended database schema\n- Added session_logs table for tracking\n- Added git_commits table for version control",
                "author": "Autonomous Agent",
                "files_changed": 2
            },
        ]

        for commit in test_commits:
            await conn.execute("""
                INSERT INTO git_commits (session_id, commit_hash, message, author, timestamp, files_changed)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                commit['hash'],
                commit['message'],
                commit['author'],
                datetime.utcnow().isoformat(),
                commit['files_changed']
            ))

        await conn.commit()

        # Get counts to verify
        logs = await db.get_logs(session_id)
        commits = await db.get_commits(session_id)

        return {
            "success": True,
            "message": "Test data added successfully",
            "logs_added": len(test_logs),
            "commits_added": len(test_commits),
            "total_logs": len(logs),
            "total_commits": len(commits),
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/file-sources")
async def get_file_sources():
    """Get configured file source paths"""
    try:
        db = await get_db()
        conn = await db.connect()

        # Get file_sources from configuration
        cursor = await conn.execute(
            "SELECT value FROM configuration WHERE key = ?",
            ("file_sources",)
        )
        row = await cursor.fetchone()

        if row:
            import json
            file_sources = json.loads(row[0])
        else:
            file_sources = []

        return {
            "file_sources": file_sources
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/file-sources")
async def add_file_source(request: Request):
    """Add a new file source path"""
    try:
        data = await request.json()
        path = data.get('path', '').strip()

        if not path:
            raise HTTPException(status_code=400, detail="Path is required")

        # Validate path format (basic validation)
        import os
        if not path.startswith('./') and not path.startswith('/') and not os.path.isabs(path):
            raise HTTPException(
                status_code=400,
                detail="Path must be absolute or start with ./"
            )

        db = await get_db()
        conn = await db.connect()

        # Get existing file sources
        cursor = await conn.execute(
            "SELECT value FROM configuration WHERE key = ?",
            ("file_sources",)
        )
        row = await cursor.fetchone()

        import json
        if row:
            file_sources = json.loads(row[0])
        else:
            file_sources = []

        # Check if path already exists
        if path in file_sources:
            raise HTTPException(status_code=400, detail="Path already exists")

        # Add new path
        file_sources.append(path)

        # Save back to database
        await conn.execute("""
            INSERT OR REPLACE INTO configuration (key, value, updated_at)
            VALUES (?, ?, ?)
        """, ("file_sources", json.dumps(file_sources), datetime.utcnow().isoformat()))

        await conn.commit()

        return {
            "success": True,
            "message": "File source added successfully",
            "path": path,
            "file_sources": file_sources
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/file-sources")
async def remove_file_source(request: Request):
    """Remove a file source path"""
    try:
        data = await request.json()
        path = data.get('path', '').strip()

        if not path:
            raise HTTPException(status_code=400, detail="Path is required")

        db = await get_db()
        conn = await db.connect()

        # Get existing file sources
        cursor = await conn.execute(
            "SELECT value FROM configuration WHERE key = ?",
            ("file_sources",)
        )
        row = await cursor.fetchone()

        import json
        if not row:
            raise HTTPException(status_code=404, detail="No file sources configured")

        file_sources = json.loads(row[0])

        # Remove path if it exists
        if path not in file_sources:
            raise HTTPException(status_code=404, detail="Path not found")

        file_sources.remove(path)

        # Save back to database
        await conn.execute("""
            INSERT OR REPLACE INTO configuration (key, value, updated_at)
            VALUES (?, ?, ?)
        """, ("file_sources", json.dumps(file_sources), datetime.utcnow().isoformat()))

        await conn.commit()

        return {
            "success": True,
            "message": "File source removed successfully",
            "file_sources": file_sources
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/migrations/status")
async def get_migrations_status():
    """Get current migration status"""
    try:
        logger.info("GET /api/migrations/status - Fetching migration status")
        status = await get_migration_status(DB_PATH)
        logger.info(f"Migration status: version={status['current_version']}, pending={status['pending_count']}")
        return {
            "status": "success",
            "migrations": status,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting migration status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/migrations/run")
async def run_db_migrations(request: Request):
    """Run pending database migrations"""
    try:
        logger.info("POST /api/migrations/run - Running migrations")

        # Get optional target version from request body
        body = await request.json() if request.headers.get("content-length") else {}
        target_version = body.get('target_version', None)

        if target_version:
            logger.info(f"Running migrations up to version {target_version}")
        else:
            logger.info("Running all pending migrations")

        result = await run_migrations(DB_PATH, target_version)

        logger.info(f"Migrations completed: applied {len(result['applied_versions'])} migrations")

        return {
            "status": "success",
            "result": result,
            "message": f"Applied {len(result['applied_versions'])} migration(s)",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error running migrations: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Migration failed: {str(e)}")


@app.post("/api/migrations/rollback")
async def rollback_db_migrations(request: Request):
    """Rollback database migrations to target version"""
    try:
        logger.info("POST /api/migrations/rollback - Rolling back migrations")

        # Get target version from request body (required)
        body = await request.json()
        target_version = body.get('target_version')

        if target_version is None:
            raise HTTPException(status_code=400, detail="target_version is required")

        logger.info(f"Rolling back migrations to version {target_version}")

        result = await rollback_migrations(DB_PATH, target_version)

        logger.info(f"Rollback completed: rolled back {len(result['rolled_back_versions'])} migrations")

        return {
            "status": "success",
            "result": result,
            "message": f"Rolled back {len(result['rolled_back_versions'])} migration(s)",
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rolling back migrations: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Rollback failed: {str(e)}")


# ============================================================================
# API VERSIONING - V1 ROUTER
# ============================================================================
# Create a v1 router that includes all API endpoints
# This allows accessing endpoints via both /api/... and /api/v1/...
# For backward compatibility, we keep both routes active

# Create v1 router
v1_router = APIRouter(prefix="/v1")

# Sessions endpoints
v1_router.add_api_route("/sessions", get_sessions, methods=["GET"])
v1_router.add_api_route("/sessions", create_session, methods=["POST"], status_code=201)
v1_router.add_api_route("/sessions/{session_id}", get_session, methods=["GET"])
v1_router.add_api_route("/sessions/{session_id}", update_session, methods=["PATCH"])
v1_router.add_api_route("/sessions/{session_id}/progress", get_session_progress, methods=["GET"])
v1_router.add_api_route("/sessions/{session_id}/stop", stop_session, methods=["POST"])
v1_router.add_api_route("/sessions/{session_id}/pause", pause_session, methods=["POST"])
v1_router.add_api_route("/sessions/{session_id}/resume", resume_session, methods=["POST"])
v1_router.add_api_route("/sessions/{session_id}/logs", get_session_logs, methods=["GET"])
v1_router.add_api_route("/sessions/{session_id}/commits", get_session_commits, methods=["GET"])
v1_router.add_api_route("/sessions/{session_id}/test-data", add_test_data, methods=["POST"])

# Snippets endpoints
v1_router.add_api_route("/snippets", get_snippets, methods=["GET"])
v1_router.add_api_route("/snippets/{snippet_id}", get_snippet, methods=["GET"])
v1_router.add_api_route("/snippets", create_snippet, methods=["POST"], status_code=201)
v1_router.add_api_route("/snippets/query", query_snippets, methods=["POST"])
v1_router.add_api_route("/snippets/load-builtin", load_builtin_snippets, methods=["POST"])

# Config endpoints
v1_router.add_api_route("/config", get_config, methods=["GET"])
v1_router.add_api_route("/config", set_config_value, methods=["POST"])

# Environment endpoints
v1_router.add_api_route("/environment", get_environment, methods=["GET"])
v1_router.add_api_route("/environment", set_environment, methods=["POST"])

# Azure DevOps endpoints
v1_router.add_api_route("/azure-devops/connect", connect_azure_devops, methods=["POST"])
v1_router.add_api_route("/azure-devops/save-config", save_azure_devops_config, methods=["POST"])
v1_router.add_api_route("/azure-devops/status", get_azure_devops_status, methods=["GET"])
v1_router.add_api_route("/azure-devops/sync", sync_azure_devops, methods=["POST"])

# Activity endpoints
v1_router.add_api_route("/activity", get_recent_activity, methods=["GET"])

# File sources endpoints
v1_router.add_api_route("/file-sources", get_file_sources, methods=["GET"])
v1_router.add_api_route("/file-sources", add_file_source, methods=["POST"])
v1_router.add_api_route("/file-sources", remove_file_source, methods=["DELETE"])

# Migrations endpoints
v1_router.add_api_route("/migrations/status", get_migrations_status, methods=["GET"])
v1_router.add_api_route("/migrations/run", run_db_migrations, methods=["POST"])
v1_router.add_api_route("/migrations/rollback", rollback_db_migrations, methods=["POST"])

# Include v1 router under /api/v1 prefix
app.include_router(v1_router, prefix="/api")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
