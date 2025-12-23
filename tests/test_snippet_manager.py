"""
Unit tests for the SnippetManager module
"""
import pytest
from sherpa.core.snippet_manager import SnippetManager


@pytest.mark.unit
@pytest.mark.asyncio
class TestSnippetManager:
    """Test cases for SnippetManager"""

    async def test_create_snippet_manager(self, temp_db):
        """Test creating a SnippetManager instance"""
        manager = SnippetManager(db=temp_db)
        assert manager is not None

    async def test_load_built_in_snippets(self, temp_db):
        """Test loading built-in snippets"""
        manager = SnippetManager(db=temp_db)
        await manager.load_built_in_snippets()

        snippets = await temp_db.list_snippets(source='built-in')
        assert len(snippets) > 0

    async def test_get_snippet_by_category(self, temp_db, test_snippet):
        """Test retrieving snippets by category"""
        manager = SnippetManager(db=temp_db)
        snippets = await manager.get_snippets_by_category('testing')

        assert len(snippets) >= 1
        assert all(s['category'] == 'testing' for s in snippets)

    async def test_search_snippets(self, temp_db, sample_snippet_data):
        """Test searching snippets by keyword"""
        manager = SnippetManager(db=temp_db)

        # Create a snippet with searchable content
        await temp_db.create_snippet(sample_snippet_data)

        # Search for it
        results = await manager.search_snippets('error')

        assert len(results) > 0
        assert any('error' in r['content'].lower() or 'error' in r['name'].lower()
                  for r in results)

    async def test_get_snippet_hierarchy(self, temp_db):
        """Test snippet hierarchy resolution (local > project > org > built-in)"""
        manager = SnippetManager(db=temp_db)

        # Create snippets with same name but different sources
        await temp_db.create_snippet({
            'name': 'test-hierarchy',
            'category': 'test',
            'source': 'built-in',
            'content': 'Built-in content',
            'language': 'python'
        })

        await temp_db.create_snippet({
            'name': 'test-hierarchy',
            'category': 'test',
            'source': 'local',
            'content': 'Local content (should win)',
            'language': 'python'
        })

        # Get snippet - should return local version
        snippet = await manager.get_snippet_by_name('test-hierarchy')

        assert snippet is not None
        assert snippet['source'] == 'local'
        assert snippet['content'] == 'Local content (should win)'

    async def test_list_all_categories(self, temp_db, test_snippet):
        """Test listing all unique categories"""
        manager = SnippetManager(db=temp_db)

        categories = await manager.get_categories()

        assert len(categories) > 0
        assert 'testing' in categories

    async def test_format_snippet_for_prompt(self, temp_db, sample_snippet_data):
        """Test formatting a snippet for AI prompt injection"""
        manager = SnippetManager(db=temp_db)
        snippet_id = await temp_db.create_snippet(sample_snippet_data)

        formatted = await manager.format_snippet_for_prompt(snippet_id)

        assert 'python-error-handling' in formatted
        assert 'python' in formatted.lower()
        assert 'try:' in formatted or 'error' in formatted.lower()

    async def test_get_snippets_by_tags(self, temp_db):
        """Test filtering snippets by tags"""
        manager = SnippetManager(db=temp_db)

        # Create snippet with tags
        await temp_db.create_snippet({
            'name': 'tagged-snippet',
            'category': 'test',
            'source': 'built-in',
            'content': 'Content',
            'language': 'python',
            'tags': 'async,python,best-practices'
        })

        # Search by tag
        results = await manager.get_snippets_by_tag('async')

        assert len(results) >= 1
        assert any('async' in r.get('tags', '') for r in results)

    async def test_snippet_count(self, temp_db, test_snippet):
        """Test counting total snippets"""
        manager = SnippetManager(db=temp_db)
        count = await manager.count_snippets()

        assert count >= 1

    async def test_snippet_count_by_source(self, temp_db, test_snippet):
        """Test counting snippets by source"""
        manager = SnippetManager(db=temp_db)
        count = await manager.count_snippets(source='built-in')

        assert count >= 1
