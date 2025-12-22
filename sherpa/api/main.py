"""
SHERPA V1 - Main FastAPI Application
Backend API server for the autonomous coding orchestrator
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from datetime import datetime

# Create FastAPI app
app = FastAPI(
    title="SHERPA V1 API",
    description="Autonomous Coding Orchestrator - Backend API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration - allow frontend on port 3001
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    print("🏔️  SHERPA V1 Backend Starting...")
    print("📊 API Documentation: http://localhost:8000/docs")
    print("⚛️  Frontend: http://localhost:3001")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("👋 SHERPA V1 Backend Shutting Down...")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "SHERPA V1 API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "sherpa-api",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


@app.get("/api/sessions")
async def get_sessions():
    """Get all coding sessions"""
    # TODO: Implement actual session retrieval from database
    return {
        "sessions": [],
        "total": 0,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/api/sessions")
async def create_session():
    """Create a new coding session"""
    # TODO: Implement session creation
    return {
        "id": "session-1",
        "status": "created",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """Get specific session details"""
    # TODO: Implement session retrieval
    return {
        "id": session_id,
        "status": "active",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/snippets")
async def get_snippets():
    """Get all code snippets"""
    # TODO: Implement snippet retrieval
    return {
        "snippets": [],
        "total": 0,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/config")
async def get_config():
    """Get configuration"""
    # TODO: Implement config retrieval
    return {
        "bedrock_configured": False,
        "azure_devops_configured": False,
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
