# 🚀 MeetMate Quick Start Guide

## 🎯 About MeetMate

MeetMate is a beginner-friendly Flask application for booking meeting rooms. It uses Python's built-in `sqlite3` module with raw SQL queries, making it perfect for students learning web development and database fundamentals.

## ⚡ Quick Start (3 Steps)

### Step 1: Install Dependencies
```powershell
pip install flask werkzeug
```

### Step 2: Run the Application

#### Option A: Interactive Launcher (Recommended)
```powershell
.\start.ps1
```

#### Option B: Direct Python Command
```powershell
python app_beginner.py
```

#### Option C: Using the Startup Script
```powershell
python run_beginner.py
```

### Step 3: Open Your Browser
Visit: **http://127.0.0.1:5000**

## 🔑 Default Login Credentials

| User Type | Email | Password |
|-----------|-------|----------|
| **Admin** | `admin@meetmate.com` | `admin123` |
| **Regular User** | `user@meetmate.com` | `user123` |

## 📖 Learn More

- **`README.md`** - Complete application guide
- **`COMPARISON.md`** - Technical comparison documentation

## 🛠️ Troubleshooting

### Database Issues?
Delete the `instance/meetmate.db` file and restart the application - it will recreate the database with default data.

### Permission Errors?
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

**Ready to learn Flask? Start coding! 🎉**
