"""
Snippet Manager for SHERPA V1

This module manages code snippets from multiple sources:
- Built-in snippets (sherpa/snippets/)
- Project snippets (./sherpa/snippets/)
- Local snippets (./sherpa/snippets.local/)
- Org snippets from S3 + Bedrock

Hierarchy: local > project > org > built-in
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from sherpa.core.logging_config import get_logger

logger = get_logger("sherpa.snippet_manager")


@dataclass
class Snippet:
    """Represents a code snippet with metadata"""
    id: str
    title: str
    category: str
    content: str
    source: str  # 'built-in', 'project', 'local', 'org'
    file_path: str
    language: Optional[str] = None
    tags: Optional[List[str]] = None


class SnippetManager:
    """
    Manages code snippets from multiple sources

    Loads and provides access to snippets from:
    - Built-in snippets (package installation)
    - Project snippets (current project)
    - Local snippets (developer overrides)
    - Organization snippets (S3 + Bedrock)
    """

    def __init__(self):
        """Initialize the snippet manager"""
        self.snippets: List[Snippet] = []
        self._loaded = False

    def load_snippets(self) -> None:
        """Load snippets from all sources"""
        if self._loaded:
            return

        logger.info("Loading snippets from all sources...")

        # Load in hierarchy order (lowest priority first)
        self.snippets = []
        self.snippets.extend(self._load_built_in_snippets())
        self.snippets.extend(self._load_project_snippets())
        self.snippets.extend(self._load_local_snippets())

        self._loaded = True
        logger.info(f"Loaded {len(self.snippets)} total snippets")

    def _load_built_in_snippets(self) -> List[Snippet]:
        """Load built-in snippets from package installation"""
        snippets = []

        # Get the path to the sherpa/snippets directory
        package_dir = Path(__file__).parent.parent
        snippets_dir = package_dir / "snippets"

        if not snippets_dir.exists():
            logger.warning(f"Built-in snippets directory not found: {snippets_dir}")
            return snippets

        # Load all .md files
        for snippet_file in snippets_dir.glob("*.md"):
            try:
                # Skip test files
                if snippet_file.name.startswith("test-") or snippet_file.name.startswith("snippet-"):
                    continue

                snippet = self._parse_snippet_file(snippet_file, source="built-in")
                if snippet:
                    snippets.append(snippet)
                    logger.debug(f"Loaded built-in snippet: {snippet.title}")
            except Exception as e:
                logger.error(f"Error loading built-in snippet {snippet_file}: {e}")

        logger.info(f"Loaded {len(snippets)} built-in snippets")
        return snippets

    def _load_project_snippets(self) -> List[Snippet]:
        """Load project-specific snippets from ./sherpa/snippets/"""
        snippets = []

        # Look for sherpa/snippets in current working directory
        project_dir = Path.cwd() / "sherpa" / "snippets"

        if not project_dir.exists():
            logger.debug(f"No project snippets directory found: {project_dir}")
            return snippets

        # Load all .md files
        for snippet_file in project_dir.glob("*.md"):
            try:
                # Skip test files
                if snippet_file.name.startswith("test-") or snippet_file.name.startswith("snippet-"):
                    continue

                snippet = self._parse_snippet_file(snippet_file, source="project")
                if snippet:
                    snippets.append(snippet)
                    logger.debug(f"Loaded project snippet: {snippet.title}")
            except Exception as e:
                logger.error(f"Error loading project snippet {snippet_file}: {e}")

        logger.info(f"Loaded {len(snippets)} project snippets")
        return snippets

    def _load_local_snippets(self) -> List[Snippet]:
        """Load local developer snippets from ./sherpa/snippets.local/"""
        snippets = []

        # Look for sherpa/snippets.local in current working directory
        local_dir = Path.cwd() / "sherpa" / "snippets.local"

        if not local_dir.exists():
            logger.debug(f"No local snippets directory found: {local_dir}")
            return snippets

        # Load all .md files
        for snippet_file in local_dir.glob("*.md"):
            try:
                snippet = self._parse_snippet_file(snippet_file, source="local")
                if snippet:
                    snippets.append(snippet)
                    logger.debug(f"Loaded local snippet: {snippet.title}")
            except Exception as e:
                logger.error(f"Error loading local snippet {snippet_file}: {e}")

        logger.info(f"Loaded {len(snippets)} local snippets")
        return snippets

    def _parse_snippet_file(self, file_path: Path, source: str) -> Optional[Snippet]:
        """
        Parse a snippet markdown file

        Expected format:
        # Title

        ## Category: category_name
        ## Language: python
        ## Tags: tag1, tag2, tag3

        Content here...
        """
        try:
            content = file_path.read_text(encoding='utf-8')

            # Extract title (first line starting with #)
            title = None
            category = None
            language = None
            tags = []

            lines = content.split('\n')
            for i, line in enumerate(lines):
                line = line.strip()

                if not title and line.startswith('# '):
                    title = line[2:].strip()
                elif line.startswith('## Category:'):
                    category = line.split(':', 1)[1].strip()
                elif line.startswith('## Language:'):
                    language = line.split(':', 1)[1].strip()
                elif line.startswith('## Tags:'):
                    tags_str = line.split(':', 1)[1].strip()
                    tags = [t.strip() for t in tags_str.split(',')]

            # Use filename as fallback title
            if not title:
                title = file_path.stem.replace('-', ' ').replace('_', ' ').title()

            # Use filename as fallback category
            if not category:
                # Extract category from filename (e.g., "python-async" -> "python")
                parts = file_path.stem.split('-')
                if len(parts) >= 2:
                    category = parts[0]
                else:
                    category = "general"

            # Create snippet ID
            snippet_id = f"{source}:{file_path.stem}"

            return Snippet(
                id=snippet_id,
                title=title,
                category=category,
                content=content,
                source=source,
                file_path=str(file_path),
                language=language,
                tags=tags if tags else None
            )

        except Exception as e:
            logger.error(f"Error parsing snippet file {file_path}: {e}")
            return None

    def get_all_snippets(self) -> List[Snippet]:
        """Get all loaded snippets"""
        if not self._loaded:
            self.load_snippets()
        return self.snippets

    def get_snippets_by_source(self, source: str) -> List[Snippet]:
        """Get snippets from a specific source"""
        if not self._loaded:
            self.load_snippets()
        return [s for s in self.snippets if s.source == source]

    def get_snippets_by_category(self, category: str) -> List[Snippet]:
        """Get snippets from a specific category"""
        if not self._loaded:
            self.load_snippets()
        return [s for s in self.snippets if s.category == category]

    def get_categories(self) -> List[str]:
        """Get all unique categories"""
        if not self._loaded:
            self.load_snippets()
        categories = set(s.category for s in self.snippets)
        return sorted(categories)

    def get_sources(self) -> Dict[str, int]:
        """Get snippet counts by source"""
        if not self._loaded:
            self.load_snippets()

        sources = {}
        for snippet in self.snippets:
            sources[snippet.source] = sources.get(snippet.source, 0) + 1

        return sources


# Singleton instance
_snippet_manager: Optional[SnippetManager] = None


def get_snippet_manager() -> SnippetManager:
    """Get or create the snippet manager singleton"""
    global _snippet_manager

    if _snippet_manager is None:
        _snippet_manager = SnippetManager()

    return _snippet_manager
