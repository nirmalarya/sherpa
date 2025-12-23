import sqlite3

# Connect to database
conn = sqlite3.connect('sherpa/data/sherpa.db')
cursor = conn.cursor()

# Clear all sessions
cursor.execute("DELETE FROM sessions")
conn.commit()
conn.close()

print("Sessions cleared successfully")
