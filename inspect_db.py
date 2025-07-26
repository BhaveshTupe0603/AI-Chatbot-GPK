import sqlite3

conn = sqlite3.connect("chat.db")
cursor = conn.cursor()

# Step 1: Add new column
cursor.execute("ALTER TABLE complaints ADD COLUMN username TEXT")

# Step 2: Fill in usernames from users table
cursor.execute("""
    UPDATE complaints
    SET username = (
        SELECT username FROM users WHERE users.id = complaints.user_id
    )
""")

# Step 3: (Optional) Drop user_id column if you don't want it anymore
# ⚠️ WARNING: Only run this after verifying everything works.
# cursor.execute("CREATE TABLE complaints_new AS SELECT id, username, message, timestamp FROM complaints")
# cursor.execute("DROP TABLE complaints")
# cursor.execute("ALTER TABLE complaints_new RENAME TO complaints")

conn.commit()
conn.close()

print("✅ complaints table updated with username!")
