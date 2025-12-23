"""
Pytest configuration and fixtures for SHERPA V1 tests
"""
import pytest
import asyncio
import os
import tempfile
from pathlib import Path

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from sherpa.core.db import Database
from sherpa.core.config_manager import ConfigManager


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def temp_db():
    """Create a temporary database for testing"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    db = Database(db_path=db_path)
    await db.initialize()

    yield db

    await db.close()
    # Clean up
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
async def test_session(temp_db):
    """Create a test session in the database"""
    session_id = await temp_db.create_session({
        'spec_file': 'test_spec.txt',
        'status': 'active',
        'total_features': 10,
        'completed_features': 0
    })

    yield session_id

    # Cleanup happens automatically when temp_db is torn down


@pytest.fixture
async def test_snippet(temp_db):
    """Create a test snippet in the database"""
    snippet_id = await temp_db.create_snippet({
        'name': 'test-snippet',
        'category': 'testing',
        'source': 'built-in',
        'content': 'print("Test snippet")',
        'language': 'python',
        'tags': 'test,unit'
    })

    yield snippet_id


@pytest.fixture
def temp_config_dir():
    """Create a temporary directory for config files"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def mock_config(temp_config_dir):
    """Create a mock configuration"""
    config_path = os.path.join(temp_config_dir, 'config.json')
    config = ConfigManager(config_path=config_path)

    # Set some default test values
    config.set('bedrock_kb_id', 'test-kb-123')
    config.set('aws_region', 'us-east-1')

    yield config


@pytest.fixture
def sample_snippet_data():
    """Sample snippet data for testing"""
    return {
        'name': 'python-error-handling',
        'category': 'python',
        'language': 'python',
        'content': '''
# Error Handling Best Practices

```python
try:
    result = risky_operation()
except ValueError as e:
    logger.error(f"Value error: {e}")
    raise
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    return None
finally:
    cleanup()
```
        ''',
        'tags': 'error-handling,python,best-practices',
        'source': 'built-in'
    }


@pytest.fixture
def sample_session_data():
    """Sample session data for testing"""
    return {
        'spec_file': 'test_app.txt',
        'status': 'active',
        'total_features': 100,
        'completed_features': 25,
        'started_at': '2024-01-01T00:00:00',
        'azure_devops_work_item_id': None
    }
