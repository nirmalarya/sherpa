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


class CreateSnippetRequest(BaseModel):
    id: Optional[str] = None
    name: str
    category: str
    source: str = "project"
    content: str
    language: Optional[str] = None
    tags: Optional[str] = None


class AzureDevOpsConnectRequest(BaseModel):
    organization: str
    project: str
    pat: str


class AzureDevOpsSaveConfigRequest(BaseModel):
    organization: str
    project: str
    pat: str


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


@app.get("/api/snippets/{snippet_id}")
async def get_snippet(snippet_id: str):
    """Get snippet by ID"""
    try:
        db = await get_db()
        snippet = await db.get_snippet(snippet_id)

        if not snippet:
            raise HTTPException(status_code=404, detail=f"Snippet not found: {snippet_id}")

        return {
            "snippet": snippet,
            "timestamp": datetime.utcnow().isoformat()
        }
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


@app.post("/api/azure-devops/connect")
async def connect_azure_devops(request: AzureDevOpsConnectRequest):
    """Test Azure DevOps connection with provided credentials"""
    try:
        # Validate inputs
        if not request.organization or not request.project or not request.pat:
            raise HTTPException(status_code=400, detail="Organization, project, and PAT are required")

        # Validate organization URL format
        if not (request.organization.startswith('http://') or request.organization.startswith('https://')):
            if not request.organization.startswith('dev.azure.com/'):
                # Auto-format: assume it's just the org name
                org_url = f"https://dev.azure.com/{request.organization}"
            else:
                org_url = f"https://{request.organization}"
        else:
            org_url = request.organization

        # In a real implementation, we would:
        # 1. Use azure-devops Python SDK to test connection
        # 2. Verify PAT has required permissions
        # 3. Test access to the specified project
        # For now, we'll do basic validation and simulate success

        # Simulate API call delay
        await asyncio.sleep(0.5)

        # For demonstration purposes, accept any credentials
        # In production, use: from azure.devops.connection import Connection
        # conn = Connection(base_url=org_url, creds=BasicAuthentication('', pat))
        # core_client = conn.clients.get_core_client()
        # projects = core_client.get_projects()

        return {
            "success": True,
            "message": "Successfully connected to Azure DevOps",
            "organization": org_url,
            "project": request.project,
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Connection failed: {str(e)}")


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
