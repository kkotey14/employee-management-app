import sqlite3

def update_schema():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # Add the 'role' column to the 'users' table if it doesn't already exist
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")
        print("Added 'role' column to the 'users' table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("'role' column already exists.")
        else:
            raise e

    conn.commit()
    conn.close()

if __name__ == "__main__":
    update_schema()
