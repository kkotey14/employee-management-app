import sqlite3
import csv

def backup_users():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    with open("backup_users.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([i[0] for i in cursor.description])  # Write headers
        writer.writerows(users)

    conn.close()
    print("Backup completed: backup_users.csv")

if __name__ == "__main__":
    backup_users()
