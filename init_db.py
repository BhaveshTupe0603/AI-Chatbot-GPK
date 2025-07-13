import sqlite3

conn = sqlite3.connect("chat.db")
cursor = conn.cursor()

# Make sure the table exists
cursor.execute('''
CREATE TABLE IF NOT EXISTS rides (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    ride_id TEXT UNIQUE,
    pickup TEXT,
    drop_location TEXT,  -- changed from `drop`
    ride_type TEXT,
    fare REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
''')

conn.commit()
conn.close()

print("✅ rides table ensured.")
