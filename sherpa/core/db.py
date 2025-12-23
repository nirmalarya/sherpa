"""
SHERPA V1 - Database Module
SQLite database with aiosqlite for async operations
"""

import aiosqlite
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any


# Database path
DB_PATH = Path(__file__).parent.parent / "data" / "sherpa.db"


class Database:
    """Async SQLite database manager"""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._connection: Optional[aiosqlite.Connection] = None

    async def connect(self) -> aiosqlite.Connection:
        """Connect to database"""
        if self._connection is None:
            self._connection = await aiosqlite.connect(str(self.db_path))
            self._connection.row_factory = aiosqlite.Row
        return self._connection

    async def close(self):
        """Close database connection"""
        if self._connection:
            await self._connection.close()
            self._connection = None

    async def initialize(self):
        """Initialize database schema with migration support"""
        conn = await self.connect()

        # Check if snippets table needs migration (old schema: id as PK, new: composite PK)
        await self._migrate_snippets_table_if_needed(conn)

        # Sessions table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                spec_file TEXT,
                status TEXT NOT NULL,
                started_at TEXT NOT NULL,
                completed_at TEXT,
                total_features INTEGER DEFAULT 0,
                completed_features INTEGER DEFAULT 0,
                error_message TEXT,
                work_item_id TEXT,
                git_branch TEXT,
                metadata TEXT
            )
        """)

        # Snippets table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS snippets (
                id TEXT NOT NULL,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                source TEXT NOT NULL,
                content TEXT NOT NULL,
                language TEXT,
                tags TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                PRIMARY KEY (id, source)
            )
        """)

        # Work items table (Azure DevOps)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS work_items (
                id TEXT PRIMARY KEY,
                work_item_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                work_item_type TEXT,
                state TEXT,
                assigned_to TEXT,
                area_path TEXT,
                iteration_path TEXT,
                session_id TEXT,
                synced_at TEXT NOT NULL,
                metadata TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            )
        """)

        # Configuration table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS configuration (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # Session logs table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS session_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                level TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                metadata TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            )
        """)

        # Git commits table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS git_commits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                commit_hash TEXT NOT NULL,
                message TEXT NOT NULL,
                author TEXT,
                timestamp TEXT NOT NULL,
                files_changed INTEGER,
                work_item_id TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            )
        """)

        await conn.commit()
        print(f"✅ Database initialized: {self.db_path}")

    # Session operations
    async def create_session(self, session_data: Dict[str, Any]) -> str:
        """Create a new session"""
        conn = await self.connect()
        session_id = session_data.get('id', f"session-{datetime.utcnow().timestamp()}")

        await conn.execute("""
            INSERT INTO sessions (id, spec_file, status, started_at, total_features, completed_features, work_item_id, git_branch, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id,
            session_data.get('spec_file'),
            session_data.get('status', 'active'),
            datetime.utcnow().isoformat(),
            session_data.get('total_features', 0),
            session_data.get('completed_features', 0),
            session_data.get('work_item_id'),
            session_data.get('git_branch'),
            session_data.get('metadata')
        ))

        await conn.commit()
        return session_id

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by ID"""
        conn = await self.connect()
        cursor = await conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
        row = await cursor.fetchone()

        if row:
            return dict(row)
        return None

    async def get_sessions(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all sessions, optionally filtered by status"""
        conn = await self.connect()

        if status:
            cursor = await conn.execute("SELECT * FROM sessions WHERE status = ? ORDER BY started_at DESC", (status,))
        else:
            cursor = await conn.execute("SELECT * FROM sessions ORDER BY started_at DESC")

        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

    async def update_session(self, session_id: str, updates: Dict[str, Any]):
        """Update session"""
        conn = await self.connect()

        set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
        values = list(updates.values()) + [session_id]

        await conn.execute(f"UPDATE sessions SET {set_clause} WHERE id = ?", values)
        await conn.commit()

    # Snippet operations
    async def create_snippet(self, snippet_data: Dict[str, Any]) -> str:
        """Create a new snippet (allows same ID with different sources due to composite PK)"""
        conn = await self.connect()
        snippet_id = snippet_data.get('id') or f"snippet-{datetime.utcnow().timestamp()}"

        await conn.execute("""
            INSERT OR REPLACE INTO snippets (id, name, category, source, content, language, tags, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            snippet_id,
            snippet_data['name'],
            snippet_data['category'],
            snippet_data['source'],
            snippet_data['content'],
            snippet_data.get('language'),
            snippet_data.get('tags'),
            datetime.utcnow().isoformat(),
            datetime.utcnow().isoformat()
        ))

        await conn.commit()
        return snippet_id

    async def get_snippets(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all snippets with hierarchy resolution: local > project > org > built-in

        If a snippet exists in multiple sources, only return the highest priority version.
        """
        conn = await self.connect()

        if category:
            cursor = await conn.execute("SELECT * FROM snippets WHERE category = ? ORDER BY name", (category,))
        else:
            cursor = await conn.execute("SELECT * FROM snippets ORDER BY category, name")

        rows = await cursor.fetchall()
        all_snippets = [dict(row) for row in rows]

        # Apply hierarchy resolution to remove duplicates
        # Priority: local > project > org > built-in
        source_priority = {'local': 0, 'project': 1, 'org': 2, 'built-in': 3}

        # Group snippets by name (assuming snippets with same name but different sources are duplicates)
        snippets_by_name = {}
        for snippet in all_snippets:
            name = snippet['name']
            source = snippet['source']

            if name not in snippets_by_name:
                snippets_by_name[name] = snippet
            else:
                # Keep the snippet with higher priority (lower number = higher priority)
                current_priority = source_priority.get(snippets_by_name[name]['source'], 999)
                new_priority = source_priority.get(source, 999)

                if new_priority < current_priority:
                    snippets_by_name[name] = snippet

        # Return deduplicated snippets, maintaining category/name sort order
        deduplicated = list(snippets_by_name.values())
        deduplicated.sort(key=lambda s: (s['category'], s['name']))

        return deduplicated

    async def get_snippet(self, snippet_id: str) -> Optional[Dict[str, Any]]:
        """Get snippet by ID with hierarchy resolution: local > project > org > built-in"""
        conn = await self.connect()

        # Hierarchy order: local (highest) > project > org > built-in (lowest)
        source_priority = ['local', 'project', 'org', 'built-in']

        # Try to find snippet in priority order
        for source in source_priority:
            cursor = await conn.execute(
                "SELECT * FROM snippets WHERE id = ? AND source = ?",
                (snippet_id, source)
            )
            row = await cursor.fetchone()

            if row:
                return dict(row)

        # If no snippet found with any source, try without source filter (backward compatibility)
        cursor = await conn.execute("SELECT * FROM snippets WHERE id = ?", (snippet_id,))
        row = await cursor.fetchone()

        if row:
            return dict(row)
        return None

    # Configuration operations
    async def set_config(self, key: str, value: str):
        """Set configuration value"""
        conn = await self.connect()

        await conn.execute("""
            INSERT OR REPLACE INTO configuration (key, value, updated_at)
            VALUES (?, ?, ?)
        """, (key, value, datetime.utcnow().isoformat()))

        await conn.commit()

    async def get_config(self, key: str) -> Optional[str]:
        """Get configuration value"""
        conn = await self.connect()
        cursor = await conn.execute("SELECT value FROM configuration WHERE key = ?", (key,))
        row = await cursor.fetchone()

        if row:
            return row['value']
        return None

    async def get_all_config(self) -> Dict[str, str]:
        """Get all configuration"""
        conn = await self.connect()
        cursor = await conn.execute("SELECT key, value FROM configuration")
        rows = await cursor.fetchall()

        return {row['key']: row['value'] for row in rows}

    # Log operations
    async def add_log(self, session_id: str, level: str, message: str, metadata: Optional[str] = None):
        """Add session log"""
        conn = await self.connect()

        await conn.execute("""
            INSERT INTO session_logs (session_id, level, message, timestamp, metadata)
            VALUES (?, ?, ?, ?, ?)
        """, (session_id, level, message, datetime.utcnow().isoformat(), metadata))

        await conn.commit()

    async def get_logs(self, session_id: str) -> List[Dict[str, Any]]:
        """Get session logs"""
        conn = await self.connect()
        cursor = await conn.execute("""
            SELECT * FROM session_logs WHERE session_id = ? ORDER BY timestamp
        """, (session_id,))

        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

    # Git commit operations
    async def add_commit(self, session_id: str, commit_hash: str, message: str, author: Optional[str] = None, files_changed: Optional[int] = None, work_item_id: Optional[str] = None):
        """Add git commit to session"""
        conn = await self.connect()

        await conn.execute("""
            INSERT INTO git_commits (session_id, commit_hash, message, author, timestamp, files_changed, work_item_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (session_id, commit_hash, message, author, datetime.utcnow().isoformat(), files_changed, work_item_id))

        await conn.commit()

    async def get_commits(self, session_id: str) -> List[Dict[str, Any]]:
        """Get git commits for session"""
        conn = await self.connect()
        cursor = await conn.execute("""
            SELECT * FROM git_commits WHERE session_id = ? ORDER BY timestamp DESC
        """, (session_id,))

        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

    async def _migrate_snippets_table_if_needed(self, conn):
        """Migrate snippets table to support composite primary key (id, source)"""
        try:
            # Check if table exists
            cursor = await conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='snippets'"
            )
            table_exists = await cursor.fetchone()

            if not table_exists:
                # Table doesn't exist yet, will be created with new schema
                return

            # Check current schema
            cursor = await conn.execute("PRAGMA table_info(snippets)")
            columns = await cursor.fetchall()
            column_names = [col[1] for col in columns]

            # Check if migration needed (old schema has id as single PK)
            cursor = await conn.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='snippets'")
            current_schema = await cursor.fetchone()

            if current_schema and 'PRIMARY KEY (id, source)' in current_schema[0]:
                # Already migrated
                return

            print("🔄 Migrating snippets table to support hierarchy (composite PK)...")

            # Export existing data
            cursor = await conn.execute("SELECT * FROM snippets")
            existing_snippets = await cursor.fetchall()

            # Drop old table
            await conn.execute("DROP TABLE IF EXISTS snippets")

            # Create new table with composite PK
            await conn.execute("""
                CREATE TABLE snippets (
                    id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    source TEXT NOT NULL,
                    content TEXT NOT NULL,
                    language TEXT,
                    tags TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY (id, source)
                )
            """)

            # Re-insert existing data
            for snippet in existing_snippets:
                snippet_dict = dict(snippet)
                await conn.execute("""
                    INSERT OR REPLACE INTO snippets (id, name, category, source, content, language, tags, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    snippet_dict['id'],
                    snippet_dict['name'],
                    snippet_dict['category'],
                    snippet_dict['source'],
                    snippet_dict['content'],
                    snippet_dict.get('language'),
                    snippet_dict.get('tags'),
                    snippet_dict.get('created_at', datetime.utcnow().isoformat()),
                    snippet_dict.get('updated_at', datetime.utcnow().isoformat())
                ))

            await conn.commit()
            print(f"✅ Migration complete: {len(existing_snippets)} snippets preserved")

        except Exception as e:
            print(f"⚠️  Migration warning: {e}")
            # Don't fail initialization, just log the issue


# Global database instance
_db: Optional[Database] = None


async def get_db() -> Database:
    """Get global database instance"""
    global _db
    if _db is None:
        _db = Database()
        await _db.initialize()
    return _db


async def init_db():
    """Initialize database"""
    db = await get_db()
    return db


# Sync wrapper for initialization
def init_db_sync():
    """Synchronous database initialization"""
    asyncio.run(init_db())


if __name__ == "__main__":
    # Test database initialization
    async def test():
        db = Database()
        await db.initialize()

        # Test session creation
        session_id = await db.create_session({
            'spec_file': 'test_spec.txt',
            'status': 'active',
            'total_features': 100
        })
        print(f"✅ Created session: {session_id}")

        # Test session retrieval
        session = await db.get_session(session_id)
        print(f"✅ Retrieved session: {session}")

        # Test snippet creation
        snippet_id = await db.create_snippet({
            'name': 'test-snippet',
            'category': 'testing',
            'source': 'built-in',
            'content': 'print("Hello World")',
            'language': 'python'
        })
        print(f"✅ Created snippet: {snippet_id}")

        # Test configuration
        await db.set_config('bedrock_kb_id', 'test-kb-123')
        kb_id = await db.get_config('bedrock_kb_id')
        print(f"✅ Config test: {kb_id}")

        await db.close()
        print("✅ All database tests passed!")

    asyncio.run(test())
