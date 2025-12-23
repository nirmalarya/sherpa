#!/usr/bin/env python3
"""
Migrate database to support composite primary key (id, source) for snippets table.
This allows the same snippet ID to exist with different sources (local, project, org, built-in).
"""
import sqlite3
import os
from datetime import datetime

db_path = 'sherpa/data/sherpa.db'

def migrate():
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}. Will be created with new schema on first use.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if migration is needed by inspecting table structure
        cursor.execute("PRAGMA table_info(snippets)")
        columns = cursor.fetchall()
        print(f"Current snippets table has {len(columns)} columns")

        # Export existing snippets
        cursor.execute("SELECT * FROM snippets")
        existing_snippets = cursor.fetchall()
        column_names = [col[1] for col in columns]
        print(f"Found {len(existing_snippets)} existing snippets")

        # Drop the old table
        print("Dropping old snippets table...")
        cursor.execute("DROP TABLE IF EXISTS snippets")

        # Create new table with composite primary key
        print("Creating new snippets table with composite PK (id, source)...")
        cursor.execute("""
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

        # Re-insert existing snippets
        if existing_snippets:
            print(f"Re-inserting {len(existing_snippets)} snippets...")
            for snippet in existing_snippets:
                # Map old row to new structure
                snippet_dict = dict(zip(column_names, snippet))
                cursor.execute("""
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

        conn.commit()
        print("✅ Migration completed successfully!")
        print(f"   - Old table dropped")
        print(f"   - New table created with composite PK (id, source)")
        print(f"   - {len(existing_snippets)} snippets preserved")

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
