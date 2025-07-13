import sqlite3

conn = sqlite3.connect("chat.db")
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(complaints);")
columns = cursor.fetchall()

for col in columns:
    print(f"Column: {col[1]} | Type: {col[2]} | Not Null: {col[3]} | Default: {col[4]}")

conn.close()
