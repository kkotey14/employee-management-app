import sqlite3
import bcrypt

# --- Set your new passwords here ---
new_passwords = {
    "admin": "admin123@",
    "Manager": "manager123@"
}

# --- Connect to the SQLite database ---
conn = sqlite3.connect("users.db")
cursor = conn.cursor()

# --- Loop through each user and update their password ---
for username, plain_password in new_passwords.items():
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    cursor.execute("UPDATE users SET password = ? WHERE username = ?", (hashed, username))
    print(f"Password updated for: {username}")

conn.commit()
conn.close()

