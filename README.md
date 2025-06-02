# 👨‍💼 Employee Management Web App

A secure, role-based employee management system built with **Flask** and **SQLite**. Designed for small to mid-sized teams to handle logins, requests, approvals, and notifications with separate views for Admin, Manager, and Employee.

---

## 🔧 Features

- Role-based login (Admin, Manager, Employee)
- Secure session handling
- Request submission & approval workflow
- User-specific dashboards
- Notifications system
- Clean interface using HTML/CSS

---

## 🚀 Technologies

- Python, Flask
- SQLite
- HTML, CSS
- Jinja2 Templates

---

## 🛠️ Setup Instructions

Follow the steps below to run this app locally:

### 1. Clone the Repository

```bash
git clone https://github.com/kkotey14/employee-management-app.git
cd employee-management-app

2. Create & Activate a Virtual Environment

python3 -m venv venv
source venv/bin/activate      # macOS/Linux
# OR
venv\Scripts\activate         # Windows


3. Install Dependencies
pip install -r requirements.txt

4.Initialize the Database
python init_db.py
---

### 🔑 Default Admin Login

After running `init_db.py`, you can log in with:

- **Username:** `admin`  
- **Password:** `admin123`  
- **Role:** Admin

This account gives you full access to the system to:
- Manage employees and managers
- Approve requests
- Reset credentials (manually or using `reset_passwords.py`)

---

Let me know if you want this added directly to a full `README.md` and I’ll bundle it for you.

5.run the App
flask --app main run

### 🔐 How to Log In

Once the app is running, open your web browser and go to:

👉 `http://127.0.0.1:5000/login`
    
> This is the **local address** (also called `localhost`) where your Flask app runs on your computer. It means the site is hosted locally, just for you.

If you're not automatically taken to the login page, you can also go directly by typing `/login` at the end of the URL:
