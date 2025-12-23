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
