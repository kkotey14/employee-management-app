import sqlite3

# Connect to the database
conn = sqlite3.connect("users.db")
cursor = conn.cursor()

# Create the requests table
cursor.execute("""
CREATE TABLE IF NOT EXISTS requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    request TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
conn.close()

print("Requests table created successfully!")
