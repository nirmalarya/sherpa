#!/usr/bin/env python
import sqlite3
import json

# Connect to database
conn = sqlite3.connect('sherpa/data/sherpa.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Get all snippets
cursor.execute("SELECT id, name, category, source FROM snippets ORDER BY name")
rows = cursor.fetchall()

print(f"Total snippets in database: {len(rows)}")
print("\nSnippets:")
for row in rows:
    print(f"  - {row['name']} ({row['category']}, {row['source']}, id={row['id']})")

# Check for duplicates by name
from collections import Counter
names = [row['name'] for row in rows]
name_counts = Counter(names)
duplicates = {name: count for name, count in name_counts.items() if count > 1}

if duplicates:
    print(f"\n⚠️  DUPLICATES FOUND:")
    for name, count in duplicates.items():
        print(f"  - '{name}' appears {count} times")
else:
    print("\n✅ No duplicates found")

conn.close()
