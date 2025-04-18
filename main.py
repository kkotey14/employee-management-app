from flask import Flask, render_template, request, redirect, url_for, session, abort
import sqlite3
import bcrypt
from datetime import datetime

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Change to a proper secret key

# Dummy CSRF token function: returns an empty string
app.jinja_env.globals['csrf_token'] = lambda: ''

# Dummy login_required decorator (no-op)
def login_required(func):
    return func

def get_db_connection():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    return conn

# ----------------------------
# Existing Routes (User & Manager)
# ----------------------------

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" in session:
        username = session["user"]
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        user_row = cursor.fetchone()
        if not user_row:
            conn.close()
            return "User not found", 404
        user_id = user_row[0]

        if request.method == "POST":
            requestType = request.form["requestType"]
            requestMessage = request.form["requestMessage"]
            startDate = request.form["startDate"]
            endDate = request.form["endDate"]
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            full_request = f"{requestType}: {requestMessage}"
            cursor.execute("""
                INSERT INTO requests (user_id, username, request, timestamp, status, start_date, end_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, username, full_request, timestamp, 'pending', startDate, endDate))
            conn.commit()

        cursor.execute("""
            SELECT request, timestamp, status, start_date, end_date FROM requests
            WHERE user_id = ? ORDER BY timestamp DESC
        """, (user_id,))
        user_requests = cursor.fetchall()
        conn.close()

        return render_template("HTML/dashboard.html", username=username, requests=user_requests)
    return redirect(url_for("login"))

@app.route("/create_request", methods=["GET","POST"])
def create_request():
    if "user" in session:
        username = session["user"]
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        user_row = cursor.fetchone()
        if not user_row:
            conn.close()
            return "User not found", 404
        user_id = user_row[0]

        if request.method == "POST":
            requestType = request.form["requestType"]
            requestMessage = request.form["requestMessage"]
            startDate = request.form["startDate"]
            endDate = request.form["endDate"]
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            full_request = f"{requestType}: {requestMessage}"
            cursor.execute("""
                INSERT INTO requests (user_id, username, request, timestamp, status, start_date, end_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, username, full_request, timestamp, 'pending', startDate, endDate))
            conn.commit()

        cursor.execute("SELECT * FROM requests WHERE user_id = ? AND status = 'pending' ORDER BY timestamp DESC", (user_id,))
        pending_requests = cursor.fetchall()
        conn.close()

        return render_template("HTML/create_request.html", username=username, requests=pending_requests)
    return redirect(url_for("login"))

@app.route("/request_history", methods=["GET","POST"])
def request_history():
    if "user" in session:
        username = session["user"]
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        user_row = cursor.fetchone()
        if not user_row:
            conn.close()
            return "User not found", 404
        user_id = user_row[0]

        if request.method == "POST":
            requestType = request.form["requestType"]
            requestMessage = request.form["requestMessage"]
            startDate = request.form["startDate"]
            endDate = request.form["endDate"]
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            full_request = f"{requestType}: {requestMessage}"
            cursor.execute("""
                INSERT INTO requests (user_id, username, request, timestamp, status, start_date, end_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, username, full_request, timestamp, 'pending', startDate, endDate))
            conn.commit()

        cursor.execute("""
            SELECT request, timestamp, status, start_date, end_date FROM requests
            WHERE user_id = ? ORDER BY timestamp DESC
        """, (user_id,))
        user_requests = cursor.fetchall()
        conn.close()

        return render_template("HTML/request_history.html", username=username, requests=user_requests)
    return redirect(url_for("login"))

@app.route("/clear_requests", methods=["POST"])
def clear_requests():
    if "user" in session and session.get("role") == "manager":
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM requests")
            conn.commit()
            conn.close()
            return redirect(url_for("manager_dashboard"))
        except Exception as e:
            return f"An error occurred: {str(e)}", 500
    return redirect(url_for("login"))

@app.route("/manager_dashboard")
def manager_dashboard():
    if "user" in session and session.get("role") == "manager":
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        # Include start_date and end_date in the select query.
        cursor.execute("""
            SELECT id, username, request, timestamp, status, start_date, end_date 
            FROM requests 
            ORDER BY timestamp DESC""")
        all_requests = cursor.fetchall()
        conn.close()
        
        processed_requests = []
        now = datetime.now()
        for req in all_requests:
            req_id, req_username, req_text, req_timestamp, req_status, start_date, end_date = req
            notification = None
            # You can optionally compute the difference if you want to show the number of days off.
            if req_status == "pending_manager":
                try:
                    req_time = datetime.strptime(req_timestamp, '%Y-%m-%d %H:%M:%S')
                    if (now - req_time).total_seconds() > 3 * 3600:
                        notification = "This request has been pending for over 3 hours."
                except Exception:
                    pass
            elif req_status == "accepted":
                notification = "Admin has accepted this request. Please review."
            processed_requests.append({
                "id": req_id,
                "username": req_username,
                "request": req_text,
                "timestamp": req_timestamp,
                "status": req_status,
                "start_date": start_date,
                "end_date": end_date,
                "notification": notification
            })
        
        return render_template("HTML/manager_dashboard.html", requests=processed_requests)
    return redirect(url_for("login"))

@app.route("/update_request/<int:request_id>/<action>", methods=['POST'])
@login_required
def update_request(request_id, action):
    # Check if the user is authenticated and has the required role
    if "user" in session and session.get("role") in ["manager", "admin"]:
        # Map various action names to the correct status
        if action in ["accept", "approve"]:
            new_status = "accepted"
        elif action in ["decline", "reject"]:
            new_status = "declined"
        else:
            abort(400, "Invalid action specified.")

        # Update the database
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE requests SET status = ? WHERE id = ?", (new_status, request_id))
        conn.commit()
        conn.close()
        
        # Redirect based on the user's role
        if session.get("role") == "manager":
            return redirect(url_for("manager_dashboard"))
        elif session.get("role") == "admin":
            return redirect(url_for("admin_requests"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        try:
            conn = sqlite3.connect("users.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()
            conn.close()
            if user:
                hashed_password = user[2]
                if isinstance(hashed_password, str):
                    hashed_password = hashed_password.encode("utf-8")
                if bcrypt.checkpw(password.encode("utf-8"), hashed_password):
                    session["user"] = username
                    session["role"] = user[3]
                    if user[3] == "admin":
                        return redirect(url_for("admin_panel"))
                    elif user[3] == "manager":
                        return redirect(url_for("manager_dashboard"))
                    else:
                        return redirect(url_for("dashboard"))
                else:
                    return "Invalid credentials", 401
            else:
                return "Invalid credentials", 401
        except Exception as e:
            return f"An error occurred: {str(e)}", 500
    return render_template("HTML/login.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    session.pop("role", None)
    return redirect(url_for("login"))

# ----------------------------
# Admin Routes
# ----------------------------

@app.route("/admin_panel")
def admin_panel():
    if "user" in session and session.get("role") == "admin":
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, role FROM users")
        all_users = cursor.fetchall()
        conn.close()
        return render_template("HTML/admin_panel.html", users=all_users)
    return redirect(url_for("login"))

@app.route("/add_user", methods=["GET", "POST"])
def add_user():
    if "user" in session and session.get("role") == "admin":
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            role = request.form["role"]
            hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            conn = sqlite3.connect("users.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                           (username, hashed_password, role))
            conn.commit()
            conn.close()
            return redirect(url_for("admin_panel"))
        return render_template("HTML/create_user.html")
    return redirect(url_for("login"))

@app.route("/edit_user/<int:user_id>", methods=["GET", "POST"])
def edit_user(user_id):
    if "user" in session and session.get("role") == "admin":
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        if request.method == "POST":
            username = request.form["username"]
            role = request.form["role"]
            cursor.execute("UPDATE users SET username = ?, role = ? WHERE id = ?",
                           (username, role, user_id))
            conn.commit()
            conn.close()
            return redirect(url_for("admin_panel"))
        else:
            cursor.execute("SELECT id, username, role FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            conn.close()
            if user:
                return render_template("HTML/edit_user.html", user=user)
            else:
                return "User not found", 404
    return redirect(url_for("login"))

@app.route("/delete_user/<int:user_id>")
def delete_user(user_id):
    if "user" in session and session.get("role") == "admin":
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()
        return redirect(url_for("admin_panel"))
    return redirect(url_for("login"))


@app.route("/admin_requests")
def admin_requests():
    if "user" in session and session.get("role") == "admin":
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, request, timestamp, status, start_date, end_date FROM requests ORDER BY timestamp DESC")
        all_requests = cursor.fetchall()
        conn.close()
        return render_template("HTML/admin_requests.html", requests=all_requests)
    return redirect(url_for("login"))

@app.route("/share_request/<int:request_id>")
def share_request(request_id):
    if "user" in session and session.get("role") == "admin":
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE requests SET status = ? WHERE id = ?", ("pending_manager", request_id))
        conn.commit()
        conn.close()
        return redirect(url_for("admin_requests"))
    return redirect(url_for("login"))



def get_user(username):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user

if __name__ == "__main__":
    app.run(debug=True)
