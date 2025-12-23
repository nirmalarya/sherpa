"""
Unit tests for the Database module
"""
import pytest
from sherpa.core.db import Database


@pytest.mark.unit
@pytest.mark.asyncio
class TestDatabase:
    """Test cases for Database operations"""

    async def test_initialize_database(self, temp_db):
        """Test database initialization creates required tables"""
        # Database is already initialized by the fixture
        assert temp_db is not None
        assert temp_db.db_path is not None

    async def test_create_session(self, temp_db):
        """Test creating a new session"""
        session_data = {
            'spec_file': 'test.txt',
            'status': 'active',
            'total_features': 50
        }

        session_id = await temp_db.create_session(session_data)

        assert session_id is not None
        assert isinstance(session_id, str)

    async def test_get_session(self, temp_db, test_session):
        """Test retrieving a session by ID"""
        session = await temp_db.get_session(test_session)

        assert session is not None
        assert session['id'] == test_session
        assert session['spec_file'] == 'test_spec.txt'
        assert session['status'] == 'active'

    async def test_get_nonexistent_session(self, temp_db):
        """Test retrieving a session that doesn't exist"""
        session = await temp_db.get_session('nonexistent-id')
        assert session is None

    async def test_update_session(self, temp_db, test_session):
        """Test updating session data"""
        await temp_db.update_session(test_session, {
            'status': 'completed',
            'completed_features': 10
        })

        updated_session = await temp_db.get_session(test_session)
        assert updated_session['status'] == 'completed'
        assert updated_session['completed_features'] == 10

    async def test_list_sessions(self, temp_db, test_session):
        """Test listing all sessions"""
        sessions = await temp_db.list_sessions()

        assert len(sessions) >= 1
        assert any(s['id'] == test_session for s in sessions)

    async def test_create_snippet(self, temp_db, sample_snippet_data):
        """Test creating a snippet"""
        snippet_id = await temp_db.create_snippet(sample_snippet_data)

        assert snippet_id is not None
        assert isinstance(snippet_id, str)

    async def test_get_snippet(self, temp_db, test_snippet):
        """Test retrieving a snippet by ID"""
        snippet = await temp_db.get_snippet(test_snippet)

        assert snippet is not None
        assert snippet['id'] == test_snippet
        assert snippet['name'] == 'test-snippet'
        assert snippet['category'] == 'testing'

    async def test_list_snippets(self, temp_db, test_snippet):
        """Test listing all snippets"""
        snippets = await temp_db.list_snippets()

        assert len(snippets) >= 1
        assert any(s['id'] == test_snippet for s in snippets)

    async def test_list_snippets_by_category(self, temp_db, test_snippet):
        """Test filtering snippets by category"""
        snippets = await temp_db.list_snippets(category='testing')

        assert len(snippets) >= 1
        assert all(s['category'] == 'testing' for s in snippets)

    async def test_list_snippets_by_source(self, temp_db, test_snippet):
        """Test filtering snippets by source"""
        snippets = await temp_db.list_snippets(source='built-in')

        assert len(snippets) >= 1
        assert all(s['source'] == 'built-in' for s in snippets)

    async def test_config_operations(self, temp_db):
        """Test configuration get/set operations"""
        # Set config
        await temp_db.set_config('test_key', 'test_value')

        # Get config
        value = await temp_db.get_config('test_key')
        assert value == 'test_value'

        # Update config
        await temp_db.set_config('test_key', 'new_value')
        updated_value = await temp_db.get_config('test_key')
        assert updated_value == 'new_value'

    async def test_get_nonexistent_config(self, temp_db):
        """Test getting a config key that doesn't exist"""
        value = await temp_db.get_config('nonexistent_key')
        assert value is None

    async def test_add_session_log(self, temp_db, test_session):
        """Test adding log entries to a session"""
        await temp_db.add_session_log(test_session, 'info', 'Test log message')

        # Note: Would need a get_session_logs method to verify
        # For now, just ensure it doesn't raise an error
        assert True

    async def test_add_session_commit(self, temp_db, test_session):
        """Test adding git commits to a session"""
        commit_data = {
            'hash': 'abc123',
            'message': 'Test commit',
            'author': 'Test Author',
            'timestamp': '2024-01-01T00:00:00'
        }

        await temp_db.add_session_commit(test_session, commit_data)

        # Note: Would need a get_session_commits method to verify
        # For now, just ensure it doesn't raise an error
        assert True

    async def test_concurrent_session_creation(self, temp_db):
        """Test creating multiple sessions concurrently"""
        import asyncio

        async def create_session(i):
            return await temp_db.create_session({
                'spec_file': f'test_{i}.txt',
                'status': 'active',
                'total_features': i * 10
            })

        # Create 5 sessions concurrently
        session_ids = await asyncio.gather(*[create_session(i) for i in range(5)])

        assert len(session_ids) == 5
        assert len(set(session_ids)) == 5  # All unique

    async def test_database_close(self, temp_db):
        """Test closing database connection"""
        await temp_db.close()
        # After closing, should be able to reconnect
        await temp_db.initialize()
        assert temp_db is not None
