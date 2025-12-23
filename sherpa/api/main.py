"""
SHERPA V1 - Main FastAPI Application
Backend API server for the autonomous coding orchestrator
"""

from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
from datetime import datetime
from typing import Optional
import sys
from pathlib import Path
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sherpa.core.db import get_db


# Pydantic models
class CreateSessionRequest(BaseModel):
    spec_file: Optional[str] = None
    total_features: int = 0
    work_item_id: Optional[str] = None
    git_branch: Optional[str] = None


# Create FastAPI app
app = FastAPI(
    title="SHERPA V1 API",
    description="Autonomous Coding Orchestrator - Backend API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration - allow frontend on ports 3001, 3002, 3003
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:3003",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
        "http://127.0.0.1:3003",
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

    # Initialize database
    try:
        db = await get_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")


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
async def get_sessions(status: Optional[str] = None):
    """Get all coding sessions"""
    try:
        db = await get_db()
        sessions = await db.get_sessions(status=status)
        return {
            "sessions": sessions,
            "total": len(sessions),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/sessions", status_code=201)
async def create_session(request: CreateSessionRequest):
    """Create a new coding session"""
    try:
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
        return {
            "id": session_id,
            "status": "created",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """Get specific session details"""
    try:
        db = await get_db()
        session = await db.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session
    except HTTPException:
        raise
    except Exception as e:
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


@app.get("/api/snippets")
async def get_snippets(category: Optional[str] = None):
    """Get all code snippets"""
    try:
        db = await get_db()
        snippets = await db.get_snippets(category=category)
        return {
            "snippets": snippets,
            "total": len(snippets),
            "timestamp": datetime.utcnow().isoformat()
        }
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
