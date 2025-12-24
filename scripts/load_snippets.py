#!/usr/bin/env python3
"""
Load built-in snippets from markdown files into the database
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sherpa.core.db import get_db


# Mapping of snippet files to their metadata
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


async def load_snippets():
    """Load all built-in snippets into the database"""
    snippets_dir = Path(__file__).parent / "sherpa" / "snippets"

    if not snippets_dir.exists():
        print(f"❌ Snippets directory not found: {snippets_dir}")
        return

    print(f"📁 Loading snippets from: {snippets_dir}")

    # Get database connection
    db = await get_db()

    # Check if snippets already exist
    existing_snippets = await db.get_snippets()
    if existing_snippets:
        print(f"⚠️  Found {len(existing_snippets)} existing snippets in database")
        print("🗑️  Clearing existing snippets and reloading...")

        # Clear existing snippets
        conn = await db.connect()
        await conn.execute("DELETE FROM snippets")
        await conn.commit()
        print("✅ Cleared existing snippets")

    # Load each snippet
    loaded_count = 0
    for snippet_meta in BUILT_IN_SNIPPETS:
        snippet_file = snippets_dir / snippet_meta["file"]

        if not snippet_file.exists():
            print(f"⚠️  Snippet file not found: {snippet_file}")
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
            print(f"✅ Loaded: {snippet_meta['name']} ({snippet_meta['category']})")
            loaded_count += 1
        except Exception as e:
            print(f"❌ Failed to load {snippet_meta['name']}: {e}")

    print(f"\n🎉 Successfully loaded {loaded_count}/{len(BUILT_IN_SNIPPETS)} snippets into database")

    # Verify
    all_snippets = await db.get_snippets()
    print(f"✅ Total snippets in database: {len(all_snippets)}")

    # Show summary by category
    categories = {}
    for snippet in all_snippets:
        cat = snippet['category']
        categories[cat] = categories.get(cat, 0) + 1

    print("\n📊 Snippets by category:")
    for cat, count in sorted(categories.items()):
        print(f"   {cat}: {count}")


if __name__ == "__main__":
    asyncio.run(load_snippets())
