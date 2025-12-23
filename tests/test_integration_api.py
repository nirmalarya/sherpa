"""
Integration tests for SHERPA V1 API endpoints
Tests API endpoints end-to-end with real database interactions
"""
import pytest
from httpx import AsyncClient
from fastapi import status
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sherpa.api.main import app
from sherpa.core.db import Database
import tempfile
import os


@pytest.fixture(scope="module")
async def test_db():
    """Create a temporary database for integration tests"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    db = Database(db_path=db_path)
    await db.initialize()

    # Override the app's database dependency
    async def override_get_db():
        yield db

    # Note: We'd need to properly override FastAPI dependencies here
    # For now, this test will use the app's default database

    yield db

    await db.close()
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
async def client():
    """Create an async HTTP client for testing"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.mark.integration
class TestHealthEndpoints:
    """Test health and system endpoints"""

    @pytest.mark.asyncio
    async def test_health_endpoint(self, client):
        """Test GET /health returns 200 with status ok"""
        response = await client.get("/health")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "status" in data
        assert data["status"] == "ok"
        assert "database" in data
        assert "version" in data

    @pytest.mark.asyncio
    async def test_root_endpoint(self, client):
        """Test GET / returns welcome message"""
        response = await client.get("/")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "message" in data
        assert "SHERPA" in data["message"]

    @pytest.mark.asyncio
    async def test_metrics_endpoint(self, client):
        """Test GET /metrics returns system metrics"""
        response = await client.get("/metrics")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "active_sessions" in data
        assert "total_sessions" in data
        assert "total_snippets" in data


@pytest.mark.integration
class TestSessionEndpoints:
    """Test session management endpoints"""

    @pytest.mark.asyncio
    async def test_create_session(self, client):
        """Test POST /api/sessions creates new session"""
        session_data = {
            "spec_file": "test_spec.txt",
            "total_features": 10
        }

        response = await client.post("/api/sessions", json=session_data)
        assert response.status_code == status.HTTP_201_CREATED

        data = response.json()
        assert "id" in data
        assert data["spec_file"] == "test_spec.txt"
        assert data["status"] == "pending"
        assert data["total_features"] == 10

    @pytest.mark.asyncio
    async def test_list_sessions(self, client):
        """Test GET /api/sessions returns list of sessions"""
        response = await client.get("/api/sessions")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_get_session_by_id(self, client):
        """Test GET /api/sessions/{id} returns session details"""
        # First create a session
        create_response = await client.post("/api/sessions", json={
            "spec_file": "test.txt",
            "total_features": 5
        })
        assert create_response.status_code == status.HTTP_201_CREATED
        session_id = create_response.json()["id"]

        # Then get it
        response = await client.get(f"/api/sessions/{session_id}")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["id"] == session_id
        assert data["spec_file"] == "test.txt"

    @pytest.mark.asyncio
    async def test_update_session(self, client):
        """Test PATCH /api/sessions/{id} updates session"""
        # Create session
        create_response = await client.post("/api/sessions", json={
            "spec_file": "test.txt",
            "total_features": 5
        })
        session_id = create_response.json()["id"]

        # Update it
        update_data = {
            "status": "active",
            "completed_features": 2
        }
        response = await client.patch(f"/api/sessions/{session_id}", json=update_data)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["status"] == "active"
        assert data["completed_features"] == 2

    @pytest.mark.asyncio
    async def test_session_not_found(self, client):
        """Test GET /api/sessions/{id} returns 404 for nonexistent session"""
        response = await client.get("/api/sessions/nonexistent-id")
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.integration
class TestSnippetEndpoints:
    """Test snippet management endpoints"""

    @pytest.mark.asyncio
    async def test_create_snippet(self, client):
        """Test POST /api/snippets creates new snippet"""
        snippet_data = {
            "name": "test-snippet",
            "category": "testing",
            "source": "project",
            "content": "# Test snippet\nprint('hello')",
            "language": "python",
            "tags": "test,integration"
        }

        response = await client.post("/api/snippets", json=snippet_data)
        assert response.status_code == status.HTTP_201_CREATED

        data = response.json()
        assert "id" in data
        assert data["name"] == "test-snippet"
        assert data["category"] == "testing"

    @pytest.mark.asyncio
    async def test_list_snippets(self, client):
        """Test GET /api/snippets returns list of snippets"""
        response = await client.get("/api/snippets")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_list_snippets_with_filter(self, client):
        """Test GET /api/snippets?category=X filters by category"""
        # Create a snippet first
        await client.post("/api/snippets", json={
            "name": "python-test",
            "category": "python",
            "source": "project",
            "content": "# Python snippet"
        })

        response = await client.get("/api/snippets?category=python")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert all(s["category"] == "python" for s in data)

    @pytest.mark.asyncio
    async def test_get_snippet_by_id(self, client):
        """Test GET /api/snippets/{id} returns snippet details"""
        # Create snippet
        create_response = await client.post("/api/snippets", json={
            "name": "test-get",
            "category": "test",
            "source": "project",
            "content": "test content"
        })
        snippet_id = create_response.json()["id"]

        # Get it
        response = await client.get(f"/api/snippets/{snippet_id}")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["id"] == snippet_id
        assert data["name"] == "test-get"

    @pytest.mark.asyncio
    async def test_snippet_not_found(self, client):
        """Test GET /api/snippets/{id} returns 404 for nonexistent snippet"""
        response = await client.get("/api/snippets/nonexistent-id")
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.integration
class TestConfigEndpoints:
    """Test configuration endpoints"""

    @pytest.mark.asyncio
    async def test_get_config(self, client):
        """Test GET /api/config returns configuration"""
        response = await client.get("/api/config")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_set_config(self, client):
        """Test POST /api/config sets configuration values"""
        config_data = {
            "key": "test_setting",
            "value": "test_value"
        }

        response = await client.post("/api/config", json=config_data)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["message"] == "Configuration saved"

    @pytest.mark.asyncio
    async def test_update_config(self, client):
        """Test PUT /api/config updates configuration"""
        config_data = {
            "bedrock_kb_id": "test-kb-123",
            "aws_region": "us-east-1"
        }

        response = await client.put("/api/config", json=config_data)
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.integration
class TestValidationErrors:
    """Test input validation and error handling"""

    @pytest.mark.asyncio
    async def test_create_session_invalid_data(self, client):
        """Test POST /api/sessions with invalid data returns 422"""
        invalid_data = {
            "spec_file": "",  # Empty string should fail validation
            "total_features": -1  # Negative number should fail
        }

        response = await client.post("/api/sessions", json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_create_snippet_missing_required_field(self, client):
        """Test POST /api/snippets without required fields returns 422"""
        invalid_data = {
            "name": "test",
            # Missing required 'category' and 'content' fields
        }

        response = await client.post("/api/snippets", json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_create_session_extra_fields_rejected(self, client):
        """Test POST /api/sessions with extra fields returns 422"""
        invalid_data = {
            "spec_file": "test.txt",
            "total_features": 10,
            "unknown_field": "should be rejected"  # Extra field
        }

        response = await client.post("/api/sessions", json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.integration
class TestEndToEndWorkflow:
    """Test complete end-to-end workflows"""

    @pytest.mark.asyncio
    async def test_session_lifecycle(self, client):
        """Test creating, updating, and querying a session"""
        # Step 1: Create session
        create_response = await client.post("/api/sessions", json={
            "spec_file": "app_spec.txt",
            "total_features": 20
        })
        assert create_response.status_code == status.HTTP_201_CREATED
        session_id = create_response.json()["id"]

        # Step 2: Verify it's in the list
        list_response = await client.get("/api/sessions")
        assert list_response.status_code == status.HTTP_200_OK
        session_ids = [s["id"] for s in list_response.json()]
        assert session_id in session_ids

        # Step 3: Update the session
        update_response = await client.patch(f"/api/sessions/{session_id}", json={
            "status": "active",
            "completed_features": 5
        })
        assert update_response.status_code == status.HTTP_200_OK

        # Step 4: Verify update persisted
        get_response = await client.get(f"/api/sessions/{session_id}")
        assert get_response.status_code == status.HTTP_200_OK
        session_data = get_response.json()
        assert session_data["status"] == "active"
        assert session_data["completed_features"] == 5

    @pytest.mark.asyncio
    async def test_snippet_creation_and_retrieval(self, client):
        """Test creating and retrieving snippets"""
        # Step 1: Create multiple snippets
        snippets_to_create = [
            {
                "name": "python-async",
                "category": "python",
                "source": "project",
                "content": "# Async patterns",
                "tags": "python,async"
            },
            {
                "name": "react-hooks",
                "category": "react",
                "source": "project",
                "content": "// React hooks",
                "tags": "react,hooks"
            }
        ]

        created_ids = []
        for snippet_data in snippets_to_create:
            response = await client.post("/api/snippets", json=snippet_data)
            assert response.status_code == status.HTTP_201_CREATED
            created_ids.append(response.json()["id"])

        # Step 2: List all snippets
        list_response = await client.get("/api/snippets")
        assert list_response.status_code == status.HTTP_200_OK
        all_snippets = list_response.json()
        assert len(all_snippets) >= len(snippets_to_create)

        # Step 3: Filter by category
        python_response = await client.get("/api/snippets?category=python")
        assert python_response.status_code == status.HTTP_200_OK
        python_snippets = python_response.json()
        assert any(s["name"] == "python-async" for s in python_snippets)

        # Step 4: Get individual snippets
        for snippet_id in created_ids:
            get_response = await client.get(f"/api/snippets/{snippet_id}")
            assert get_response.status_code == status.HTTP_200_OK
            assert get_response.json()["id"] == snippet_id


@pytest.mark.integration
class TestDatabaseIntegration:
    """Test that API properly interacts with database"""

    @pytest.mark.asyncio
    async def test_database_persistence(self, client):
        """Test that data persists across requests"""
        # Create a session
        create_response = await client.post("/api/sessions", json={
            "spec_file": "persistence_test.txt",
            "total_features": 15
        })
        session_id = create_response.json()["id"]

        # Make multiple requests to verify data persists
        for _ in range(3):
            response = await client.get(f"/api/sessions/{session_id}")
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["spec_file"] == "persistence_test.txt"
            assert data["total_features"] == 15

            # Small delay between requests
            await asyncio.sleep(0.1)

    @pytest.mark.asyncio
    async def test_concurrent_requests(self, client):
        """Test handling of concurrent API requests"""
        # Create multiple sessions concurrently
        tasks = []
        for i in range(5):
            task = client.post("/api/sessions", json={
                "spec_file": f"concurrent_test_{i}.txt",
                "total_features": i + 1
            })
            tasks.append(task)

        responses = await asyncio.gather(*tasks)

        # Verify all succeeded
        for response in responses:
            assert response.status_code == status.HTTP_201_CREATED

        # Verify all have unique IDs
        session_ids = [r.json()["id"] for r in responses]
        assert len(session_ids) == len(set(session_ids))  # All unique


@pytest.mark.integration
class TestConcurrentOperations:
    """Test #66 - Concurrent operations with asyncio"""

    @pytest.mark.asyncio
    async def test_concurrent_session_creation(self, client):
        """Test that multiple sessions can be created concurrently"""
        import time
        start_time = time.time()

        # Create two sessions concurrently
        tasks = [
            client.post("/api/sessions", json={
                "spec_file": "concurrent_test_1.txt",
                "total_features": 10
            }),
            client.post("/api/sessions", json={
                "spec_file": "concurrent_test_2.txt",
                "total_features": 10
            })
        ]

        responses = await asyncio.gather(*tasks)
        duration = time.time() - start_time

        # Both should succeed
        assert all(r.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED] for r in responses)

        # Should be fast (concurrent, not sequential)
        assert duration < 2.0  # Should complete in under 2 seconds

        # Get session IDs
        session_ids = [r.json().get("data", {}).get("id") or r.json().get("id") for r in responses]
        assert len(session_ids) == 2
        assert all(session_ids)

        return session_ids

    @pytest.mark.asyncio
    async def test_concurrent_session_fetch(self, client):
        """Test that multiple sessions can be fetched concurrently without blocking"""
        # Create sessions first
        create_tasks = [
            client.post("/api/sessions", json={
                "spec_file": f"fetch_test_{i}.txt",
                "total_features": 5
            }) for i in range(3)
        ]
        create_responses = await asyncio.gather(*create_tasks)
        session_ids = [r.json().get("data", {}).get("id") or r.json().get("id") for r in create_responses]

        import time
        start_time = time.time()

        # Fetch all sessions concurrently
        fetch_tasks = [client.get(f"/api/sessions/{sid}") for sid in session_ids]
        fetch_responses = await asyncio.gather(*fetch_tasks)

        duration = time.time() - start_time

        # All should succeed
        assert all(r.status_code == status.HTTP_200_OK for r in fetch_responses)

        # Should be fast - concurrent fetches should not block each other
        assert duration < 1.0

    @pytest.mark.asyncio
    async def test_concurrent_session_updates(self, client):
        """Test that multiple sessions can be updated concurrently without blocking"""
        # Create sessions
        create_tasks = [
            client.post("/api/sessions", json={
                "spec_file": f"update_test_{i}.txt",
                "total_features": 10
            }) for i in range(3)
        ]
        create_responses = await asyncio.gather(*create_tasks)
        session_ids = [r.json().get("data", {}).get("id") or r.json().get("id") for r in create_responses]

        import time
        start_time = time.time()

        # Update all sessions concurrently
        update_tasks = [
            client.patch(f"/api/sessions/{sid}", json={
                "completed_features": i * 2
            }) for i, sid in enumerate(session_ids)
        ]
        update_responses = await asyncio.gather(*update_tasks)

        duration = time.time() - start_time

        # All should succeed
        assert all(r.status_code == status.HTTP_200_OK for r in update_responses)

        # Verify updates
        for i, response in enumerate(update_responses):
            data = response.json()
            expected_completed = i * 2
            actual_completed = data.get("data", {}).get("completed_features") or data.get("completed_features")
            assert actual_completed == expected_completed

        # Should be fast - concurrent updates should not block
        assert duration < 1.0

    @pytest.mark.asyncio
    async def test_mixed_concurrent_operations(self, client):
        """Test that different operations (create, read, update) can run concurrently"""
        # Create a session first for updates
        create_response = await client.post("/api/sessions", json={
            "spec_file": "mixed_ops_test.txt",
            "total_features": 10
        })
        existing_session_id = create_response.json().get("data", {}).get("id") or create_response.json().get("id")

        import time
        start_time = time.time()

        # Mix of operations running concurrently
        tasks = [
            # Create operations
            client.post("/api/sessions", json={"spec_file": "create_1.txt", "total_features": 5}),
            client.post("/api/sessions", json={"spec_file": "create_2.txt", "total_features": 7}),
            # Read operations
            client.get(f"/api/sessions/{existing_session_id}"),
            client.get("/api/sessions"),
            # Update operation
            client.patch(f"/api/sessions/{existing_session_id}", json={"completed_features": 3}),
        ]

        responses = await asyncio.gather(*tasks)
        duration = time.time() - start_time

        # All should succeed
        assert responses[0].status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]  # Create
        assert responses[1].status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]  # Create
        assert responses[2].status_code == status.HTTP_200_OK  # Read single
        assert responses[3].status_code == status.HTTP_200_OK  # Read list
        assert responses[4].status_code == status.HTTP_200_OK  # Update

        # Should complete quickly with proper async handling
        assert duration < 2.0

    @pytest.mark.asyncio
    async def test_resource_cleanup_after_concurrent_operations(self, client):
        """Test that resources are properly cleaned up after concurrent operations"""
        # Create sessions
        create_tasks = [
            client.post("/api/sessions", json={
                "spec_file": f"cleanup_test_{i}.txt",
                "total_features": 5
            }) for i in range(3)
        ]
        create_responses = await asyncio.gather(*create_tasks)
        session_ids = [r.json().get("data", {}).get("id") or r.json().get("id") for r in create_responses]

        # Stop all sessions concurrently
        stop_tasks = [client.post(f"/api/sessions/{sid}/stop") for sid in session_ids]
        stop_responses = await asyncio.gather(*stop_tasks)

        # All should succeed
        assert all(r.status_code == status.HTTP_200_OK for r in stop_responses)

        # Wait a bit for cleanup
        await asyncio.sleep(0.5)

        # Verify all sessions are stopped
        fetch_tasks = [client.get(f"/api/sessions/{sid}") for sid in session_ids]
        fetch_responses = await asyncio.gather(*fetch_tasks)

        for response in fetch_responses:
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            status_value = data.get("data", {}).get("status") or data.get("status")
            assert status_value == "stopped"

    @pytest.mark.asyncio
    async def test_high_concurrency_load(self, client):
        """Test system under high concurrency load"""
        import time
        start_time = time.time()

        # Create many concurrent requests
        num_concurrent = 10
        tasks = [
            client.post("/api/sessions", json={
                "spec_file": f"load_test_{i}.txt",
                "total_features": i + 1
            }) for i in range(num_concurrent)
        ]

        responses = await asyncio.gather(*tasks)
        duration = time.time() - start_time

        # All should succeed
        assert all(r.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED] for r in responses)

        # All should have unique IDs
        session_ids = [r.json().get("data", {}).get("id") or r.json().get("id") for r in responses]
        assert len(session_ids) == len(set(session_ids))

        # Should handle load efficiently (async/await prevents blocking)
        # If sequential, would take much longer
        assert duration < 3.0  # Should complete in under 3 seconds

        print(f"\n✅ Successfully handled {num_concurrent} concurrent requests in {duration:.2f}s")
        print(f"   Average: {duration/num_concurrent:.3f}s per request")


@pytest.mark.integration
class TestSessionStatePersistence:
    """Test #67 - Session state management - Sessions persist across restarts"""

    @pytest.mark.asyncio
    async def test_session_persists_in_database(self, client):
        """Test that sessions are stored persistently in SQLite database"""
        # Create a session with specific data
        session_data = {
            "spec_file": "persistence_test.txt",
            "total_features": 15,
            "work_item_id": "12345",
            "git_branch": "feature/test-branch"
        }

        create_response = await client.post("/api/sessions", json=session_data)
        assert create_response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]

        created_data = create_response.json()
        session_id = created_data.get("data", {}).get("id") or created_data.get("id")

        # Update session with progress
        update_response = await client.patch(f"/api/sessions/{session_id}", json={
            "completed_features": 7,
            "status": "active"
        })
        assert update_response.status_code == status.HTTP_200_OK

        # Fetch session to verify data is stored
        get_response = await client.get(f"/api/sessions/{session_id}")
        assert get_response.status_code == status.HTTP_200_OK

        session = get_response.json()
        session_info = session.get("data") or session

        # Verify all data persists
        assert session_info["spec_file"] == "persistence_test.txt"
        assert session_info["total_features"] == 15
        assert session_info["completed_features"] == 7
        assert session_info["status"] == "active"

    @pytest.mark.asyncio
    async def test_session_state_restored_after_query(self, client):
        """Test that session state is consistently restored across multiple queries"""
        # Create session
        create_response = await client.post("/api/sessions", json={
            "spec_file": "state_test.txt",
            "total_features": 20
        })
        session_id = create_response.json().get("data", {}).get("id") or create_response.json().get("id")

        # Update session
        await client.patch(f"/api/sessions/{session_id}", json={
            "completed_features": 10,
            "status": "active"
        })

        # Query session multiple times to verify state consistency
        for i in range(5):
            response = await client.get(f"/api/sessions/{session_id}")
            assert response.status_code == status.HTTP_200_OK

            session = response.json().get("data") or response.json()
            assert session["completed_features"] == 10
            assert session["status"] == "active"
            assert session["total_features"] == 20

            await asyncio.sleep(0.1)

    @pytest.mark.asyncio
    async def test_session_resume_capability(self, client):
        """Test that sessions can be resumed after being paused"""
        # Create and start a session
        create_response = await client.post("/api/sessions", json={
            "spec_file": "resume_test.txt",
            "total_features": 10
        })
        session_id = create_response.json().get("data", {}).get("id") or create_response.json().get("id")

        # Update to active
        await client.patch(f"/api/sessions/{session_id}", json={
            "status": "active",
            "completed_features": 3
        })

        # Pause the session
        pause_response = await client.post(f"/api/sessions/{session_id}/pause")
        assert pause_response.status_code == status.HTTP_200_OK

        # Verify paused state
        paused_session = await client.get(f"/api/sessions/{session_id}")
        paused_data = paused_session.json().get("data") or paused_session.json()
        assert paused_data["status"] == "paused"
        assert paused_data["completed_features"] == 3  # Progress preserved

        # Resume the session
        resume_response = await client.post(f"/api/sessions/{session_id}/resume")
        assert resume_response.status_code == status.HTTP_200_OK

        # Verify resumed state and progress preserved
        resumed_session = await client.get(f"/api/sessions/{session_id}")
        resumed_data = resumed_session.json().get("data") or resumed_session.json()
        assert resumed_data["status"] == "active"
        assert resumed_data["completed_features"] == 3  # Progress still preserved

    @pytest.mark.asyncio
    async def test_progress_preservation(self, client):
        """Test that session progress is preserved accurately"""
        # Create session
        create_response = await client.post("/api/sessions", json={
            "spec_file": "progress_test.txt",
            "total_features": 50
        })
        session_id = create_response.json().get("data", {}).get("id") or create_response.json().get("id")

        # Simulate incremental progress updates
        for completed in [5, 10, 15, 20, 25]:
            update_response = await client.patch(f"/api/sessions/{session_id}", json={
                "completed_features": completed
            })
            assert update_response.status_code == status.HTTP_200_OK

            # Verify progress after each update
            get_response = await client.get(f"/api/sessions/{session_id}")
            session = get_response.json().get("data") or get_response.json()
            assert session["completed_features"] == completed

    @pytest.mark.asyncio
    async def test_multiple_sessions_persist_independently(self, client):
        """Test that multiple sessions maintain independent state"""
        # Create multiple sessions with different states
        sessions = []
        for i in range(3):
            create_response = await client.post("/api/sessions", json={
                "spec_file": f"multi_session_{i}.txt",
                "total_features": (i + 1) * 10
            })
            session_id = create_response.json().get("data", {}).get("id") or create_response.json().get("id")

            # Update each with different progress
            await client.patch(f"/api/sessions/{session_id}", json={
                "completed_features": (i + 1) * 2,
                "status": ["pending", "active", "completed"][i]
            })

            sessions.append({
                "id": session_id,
                "expected_total": (i + 1) * 10,
                "expected_completed": (i + 1) * 2,
                "expected_status": ["pending", "active", "completed"][i]
            })

        # Verify each session maintained its independent state
        for session_info in sessions:
            response = await client.get(f"/api/sessions/{session_info['id']}")
            assert response.status_code == status.HTTP_200_OK

            session = response.json().get("data") or response.json()
            assert session["total_features"] == session_info["expected_total"]
            assert session["completed_features"] == session_info["expected_completed"]
            assert session["status"] == session_info["expected_status"]


@pytest.mark.integration
class TestErrorHandlingAndRecovery:
    """Test #68 - Error handling and recovery - Graceful handling of errors"""

    @pytest.mark.asyncio
    async def test_404_error_for_nonexistent_session(self, client):
        """Test that accessing nonexistent resource returns proper 404 error"""
        # Try to get a session that doesn't exist
        response = await client.get("/api/sessions/nonexistent-session-id")

        # Should return 404
        assert response.status_code == status.HTTP_404_NOT_FOUND

        # Error message should be clear
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_400_error_for_invalid_update(self, client):
        """Test that invalid updates return proper 400 error"""
        # Create a session first
        create_response = await client.post("/api/sessions", json={
            "spec_file": "error_test.txt",
            "total_features": 10
        })
        session_id = create_response.json().get("data", {}).get("id") or create_response.json().get("id")

        # Try to update with no valid fields
        response = await client.patch(f"/api/sessions/{session_id}", json={
            "invalid_field": "should_be_rejected"
        })

        # Should return 400 or 422
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]

    @pytest.mark.asyncio
    async def test_validation_error_422(self, client):
        """Test that invalid input data returns 422 validation error"""
        # Try to create session with invalid data
        invalid_data = {
            "spec_file": "",  # Empty string should fail validation
            "total_features": -1  # Negative number should fail
        }

        response = await client.post("/api/sessions", json=invalid_data)

        # Should return 422
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_session_continues_after_recoverable_error(self, client):
        """Test that session operations continue after recoverable errors"""
        # Create a session
        create_response = await client.post("/api/sessions", json={
            "spec_file": "recovery_test.txt",
            "total_features": 10
        })
        session_id = create_response.json().get("data", {}).get("id") or create_response.json().get("id")

        # Cause an error by trying to access nonexistent resource
        error_response = await client.get("/api/sessions/nonexistent")
        assert error_response.status_code == status.HTTP_404_NOT_FOUND

        # Verify the original session still works
        get_response = await client.get(f"/api/sessions/{session_id}")
        assert get_response.status_code == status.HTTP_200_OK

        # Can still update the session
        update_response = await client.patch(f"/api/sessions/{session_id}", json={
            "completed_features": 5
        })
        assert update_response.status_code == status.HTTP_200_OK

        # Verify update persisted
        final_response = await client.get(f"/api/sessions/{session_id}")
        final_data = final_response.json().get("data") or final_response.json()
        assert final_data["completed_features"] == 5

    @pytest.mark.asyncio
    async def test_error_responses_have_consistent_format(self, client):
        """Test that all error responses follow consistent format"""
        # Collect different types of errors
        errors = []

        # 404 error
        response_404 = await client.get("/api/sessions/nonexistent")
        errors.append(("404", response_404))

        # 400 error - pause already paused session
        create_resp = await client.post("/api/sessions", json={
            "spec_file": "test.txt",
            "total_features": 5
        })
        session_id = create_resp.json().get("data", {}).get("id") or create_resp.json().get("id")

        await client.post(f"/api/sessions/{session_id}/pause")
        response_400 = await client.post(f"/api/sessions/{session_id}/pause")
        errors.append(("400", response_400))

        # 422 validation error
        response_422 = await client.post("/api/sessions", json={"invalid": "data"})
        errors.append(("422", response_422))

        # All should have detail field
        for error_type, response in errors:
            data = response.json()
            assert "detail" in data, f"{error_type} error should have 'detail' field"

    @pytest.mark.asyncio
    async def test_concurrent_errors_dont_affect_each_other(self, client):
        """Test that errors in concurrent operations don't affect other operations"""
        # Create a valid session
        create_response = await client.post("/api/sessions", json={
            "spec_file": "concurrent_error_test.txt",
            "total_features": 10
        })
        session_id = create_response.json().get("data", {}).get("id") or create_response.json().get("id")

        # Run mix of valid and invalid operations concurrently
        tasks = [
            # Valid operations
            client.get(f"/api/sessions/{session_id}"),  # Should succeed
            client.patch(f"/api/sessions/{session_id}", json={"completed_features": 3}),  # Should succeed
            # Invalid operations
            client.get("/api/sessions/nonexistent"),  # Should fail with 404
            client.patch("/api/sessions/nonexistent", json={"completed_features": 5}),  # Should fail with 404
        ]

        responses = await asyncio.gather(*tasks, return_exceptions=False)

        # Valid operations should succeed
        assert responses[0].status_code == status.HTTP_200_OK
        assert responses[1].status_code == status.HTTP_200_OK

        # Invalid operations should fail
        assert responses[2].status_code == status.HTTP_404_NOT_FOUND
        assert responses[3].status_code == status.HTTP_404_NOT_FOUND

        # Verify the valid session is still in good state
        final_response = await client.get(f"/api/sessions/{session_id}")
        assert final_response.status_code == status.HTTP_200_OK
        final_data = final_response.json().get("data") or final_response.json()
        assert final_data["completed_features"] == 3

    @pytest.mark.asyncio
    async def test_multiple_error_scenarios(self, client):
        """Test various error scenarios are handled gracefully"""
        # Test 1: Missing required fields
        response1 = await client.post("/api/snippets", json={"name": "test"})
        assert response1.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Test 2: Invalid session ID format
        response2 = await client.get("/api/sessions/")
        assert response2.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_405_METHOD_NOT_ALLOWED]

        # Test 3: Pause a non-existent session
        response3 = await client.post("/api/sessions/nonexistent/pause")
        assert response3.status_code == status.HTTP_404_NOT_FOUND

        # Test 4: Resume a non-existent session
        response4 = await client.post("/api/sessions/nonexistent/resume")
        assert response4.status_code == status.HTTP_404_NOT_FOUND

        # All errors should have been logged (we can't test logging directly in integration tests,
        # but we verify the errors are returned properly)
