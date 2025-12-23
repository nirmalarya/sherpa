"""
SHERPA V1 - Database Migrations Module
Handles schema updates with version tracking and rollback support
"""

import aiosqlite
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Callable, Tuple, Optional
import json


class Migration:
    """Represents a single database migration"""

    def __init__(
        self,
        version: int,
        name: str,
        up: Callable,
        down: Callable,
        description: str = ""
    ):
        self.version = version
        self.name = name
        self.up = up  # Migration function
        self.down = down  # Rollback function
        self.description = description


class MigrationManager:
    """Manages database migrations with version tracking"""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.migrations: List[Migration] = []

    def register_migration(
        self,
        version: int,
        name: str,
        up: Callable,
        down: Callable,
        description: str = ""
    ):
        """Register a new migration"""
        migration = Migration(version, name, up, down, description)
        self.migrations.append(migration)
        # Keep migrations sorted by version
        self.migrations.sort(key=lambda m: m.version)

    async def initialize_migration_table(self, conn: aiosqlite.Connection):
        """Create migration tracking table if it doesn't exist"""
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                applied_at TEXT NOT NULL,
                rollback_available INTEGER DEFAULT 1
            )
        """)
        await conn.commit()

    async def get_current_version(self, conn: aiosqlite.Connection) -> int:
        """Get current schema version"""
        await self.initialize_migration_table(conn)

        cursor = await conn.execute(
            "SELECT MAX(version) as current_version FROM schema_migrations"
        )
        row = await cursor.fetchone()

        if row and row[0] is not None:
            return row[0]
        return 0

    async def get_applied_migrations(self, conn: aiosqlite.Connection) -> List[Dict]:
        """Get list of applied migrations"""
        await self.initialize_migration_table(conn)

        cursor = await conn.execute(
            "SELECT version, name, description, applied_at FROM schema_migrations ORDER BY version"
        )
        rows = await cursor.fetchall()

        return [
            {
                "version": row[0],
                "name": row[1],
                "description": row[2],
                "applied_at": row[3]
            }
            for row in rows
        ]

    async def migrate_up(self, conn: aiosqlite.Connection, target_version: Optional[int] = None) -> List[int]:
        """Apply pending migrations up to target version (or latest)"""
        current_version = await self.get_current_version(conn)
        applied_versions = []

        for migration in self.migrations:
            # Skip if already applied
            if migration.version <= current_version:
                continue

            # Stop if we've reached target version
            if target_version and migration.version > target_version:
                break

            print(f"🔄 Applying migration {migration.version}: {migration.name}")

            try:
                # Execute migration
                await migration.up(conn)

                # Record migration
                await conn.execute("""
                    INSERT INTO schema_migrations (version, name, description, applied_at)
                    VALUES (?, ?, ?, ?)
                """, (
                    migration.version,
                    migration.name,
                    migration.description,
                    datetime.utcnow().isoformat()
                ))

                await conn.commit()
                applied_versions.append(migration.version)
                print(f"✅ Migration {migration.version} applied successfully")

            except Exception as e:
                print(f"❌ Migration {migration.version} failed: {e}")
                await conn.rollback()
                raise

        return applied_versions

    async def migrate_down(self, conn: aiosqlite.Connection, target_version: int) -> List[int]:
        """Rollback migrations to target version"""
        current_version = await self.get_current_version(conn)
        rolled_back_versions = []

        if target_version >= current_version:
            print(f"ℹ️  Already at or below version {target_version}")
            return rolled_back_versions

        # Find migrations to rollback (in reverse order)
        migrations_to_rollback = [
            m for m in self.migrations
            if target_version < m.version <= current_version
        ]
        migrations_to_rollback.reverse()

        for migration in migrations_to_rollback:
            print(f"🔄 Rolling back migration {migration.version}: {migration.name}")

            try:
                # Execute rollback
                await migration.down(conn)

                # Remove migration record
                await conn.execute(
                    "DELETE FROM schema_migrations WHERE version = ?",
                    (migration.version,)
                )

                await conn.commit()
                rolled_back_versions.append(migration.version)
                print(f"✅ Migration {migration.version} rolled back successfully")

            except Exception as e:
                print(f"❌ Rollback {migration.version} failed: {e}")
                await conn.rollback()
                raise

        return rolled_back_versions

    async def get_pending_migrations(self, conn: aiosqlite.Connection) -> List[Migration]:
        """Get list of pending migrations"""
        current_version = await self.get_current_version(conn)
        return [m for m in self.migrations if m.version > current_version]

    async def migration_status(self, conn: aiosqlite.Connection) -> Dict:
        """Get migration status summary"""
        current_version = await self.get_current_version(conn)
        applied = await self.get_applied_migrations(conn)
        pending = await self.get_pending_migrations(conn)

        return {
            "current_version": current_version,
            "applied_count": len(applied),
            "pending_count": len(pending),
            "applied_migrations": applied,
            "pending_migrations": [
                {
                    "version": m.version,
                    "name": m.name,
                    "description": m.description
                }
                for m in pending
            ]
        }


# Example migrations
async def migration_001_up(conn: aiosqlite.Connection):
    """Add metadata column to sessions table"""
    # Check if column already exists
    cursor = await conn.execute("PRAGMA table_info(sessions)")
    columns = await cursor.fetchall()
    column_names = [col[1] for col in columns]

    if 'metadata' not in column_names:
        await conn.execute("ALTER TABLE sessions ADD COLUMN metadata TEXT")


async def migration_001_down(conn: aiosqlite.Connection):
    """Remove metadata column from sessions table"""
    # SQLite doesn't support DROP COLUMN directly in older versions
    # We need to recreate the table without the column

    # Backup data
    cursor = await conn.execute("""
        SELECT id, spec_file, status, started_at, completed_at,
               total_features, completed_features, error_message, work_item_id, git_branch
        FROM sessions
    """)
    sessions_data = await cursor.fetchall()

    # Drop and recreate table
    await conn.execute("DROP TABLE sessions")
    await conn.execute("""
        CREATE TABLE sessions (
            id TEXT PRIMARY KEY,
            spec_file TEXT,
            status TEXT NOT NULL,
            started_at TEXT NOT NULL,
            completed_at TEXT,
            total_features INTEGER DEFAULT 0,
            completed_features INTEGER DEFAULT 0,
            error_message TEXT,
            work_item_id TEXT,
            git_branch TEXT
        )
    """)

    # Restore data
    for session in sessions_data:
        await conn.execute("""
            INSERT INTO sessions (id, spec_file, status, started_at, completed_at,
                                total_features, completed_features, error_message,
                                work_item_id, git_branch)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, session)


async def migration_002_up(conn: aiosqlite.Connection):
    """Add priority column to work_items table"""
    cursor = await conn.execute("PRAGMA table_info(work_items)")
    columns = await cursor.fetchall()
    column_names = [col[1] for col in columns]

    if 'priority' not in column_names:
        await conn.execute("ALTER TABLE work_items ADD COLUMN priority INTEGER DEFAULT 2")


async def migration_002_down(conn: aiosqlite.Connection):
    """Remove priority column from work_items table"""
    # Backup data
    cursor = await conn.execute("""
        SELECT id, work_item_id, title, description, work_item_type, state,
               assigned_to, area_path, iteration_path, session_id, synced_at, metadata
        FROM work_items
    """)
    items_data = await cursor.fetchall()

    # Drop and recreate table
    await conn.execute("DROP TABLE work_items")
    await conn.execute("""
        CREATE TABLE work_items (
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

    # Restore data
    for item in items_data:
        await conn.execute("""
            INSERT INTO work_items (id, work_item_id, title, description, work_item_type,
                                   state, assigned_to, area_path, iteration_path,
                                   session_id, synced_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, item)


def create_migration_manager(db_path: Path) -> MigrationManager:
    """Create and configure migration manager with all migrations"""
    manager = MigrationManager(db_path)

    # Register migrations in order
    # Note: Version 0 is the base schema, so we start from 1

    manager.register_migration(
        version=1,
        name="add_metadata_to_sessions",
        up=migration_001_up,
        down=migration_001_down,
        description="Add metadata column to sessions table for additional session data"
    )

    manager.register_migration(
        version=2,
        name="add_priority_to_work_items",
        up=migration_002_up,
        down=migration_002_down,
        description="Add priority column to work_items table for prioritization"
    )

    return manager


# Helper function for API/CLI usage
async def run_migrations(db_path: Path, target_version: Optional[int] = None) -> Dict:
    """Run migrations and return status"""
    manager = create_migration_manager(db_path)

    async with aiosqlite.connect(str(db_path)) as conn:
        conn.row_factory = aiosqlite.Row

        # Get status before
        status_before = await manager.migration_status(conn)

        # Run migrations
        applied_versions = await manager.migrate_up(conn, target_version)

        # Get status after
        status_after = await manager.migration_status(conn)

        return {
            "success": True,
            "applied_versions": applied_versions,
            "before": status_before,
            "after": status_after
        }


async def rollback_migrations(db_path: Path, target_version: int) -> Dict:
    """Rollback migrations and return status"""
    manager = create_migration_manager(db_path)

    async with aiosqlite.connect(str(db_path)) as conn:
        conn.row_factory = aiosqlite.Row

        # Get status before
        status_before = await manager.migration_status(conn)

        # Rollback migrations
        rolled_back_versions = await manager.migrate_down(conn, target_version)

        # Get status after
        status_after = await manager.migration_status(conn)

        return {
            "success": True,
            "rolled_back_versions": rolled_back_versions,
            "before": status_before,
            "after": status_after
        }


async def get_migration_status(db_path: Path) -> Dict:
    """Get current migration status"""
    manager = create_migration_manager(db_path)

    async with aiosqlite.connect(str(db_path)) as conn:
        conn.row_factory = aiosqlite.Row
        return await manager.migration_status(conn)
