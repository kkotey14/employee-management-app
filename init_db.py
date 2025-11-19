import sqlite3
import bcrypt

def init_db():
    conn = sqlite3.connect("/tmp/users.db")
    cursor = conn.cursor()

    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            first_name TEXT,
            last_name TEXT
        )
    """)

    # Create requests table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            request TEXT NOT NULL,
            status TEXT DEFAULT 'Pending',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (username) REFERENCES users (username)
        )
    """)

    conn.commit()
    conn.close()

def seed_admin():
    conn = sqlite3.connect("/tmp/users.db")
    cursor = conn.cursor()

    admin_password = bcrypt.hashpw("admin_password".encode("utf-8"), bcrypt.gensalt())
    try:
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ("admin", admin_password, "admin")
        )
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # Admin already exists

    conn.close()

if __name__ == "__main__":
    init_db()
    seed_admin()
    print("Database initialized and admin user seeded.")
