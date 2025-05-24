# 🚀 MeetMate Quick Start Guide

## 🎯 Choose Your Version

MeetMate now comes in **two versions** designed for different learning levels:

### 📚 Beginner-Friendly Version
- **File**: `app_beginner.py`
- **Best for**: Students learning Flask and databases
- **Uses**: Raw SQL queries with sqlite3
- **Advantage**: See exactly how database operations work

### 🚀 Original Version  
- **File**: `app.py`
- **Best for**: Advanced users and production apps
- **Uses**: SQLAlchemy ORM
- **Advantage**: Industry-standard patterns

## ⚡ Quick Start (3 Steps)

### Step 1: Install Dependencies
```powershell
pip install flask werkzeug
```

### Step 2: Choose How to Run

#### Option A: Interactive Launcher (Recommended)
```powershell
.\start.ps1
```
*Then select your preferred version from the menu*

#### Option B: Direct Commands
```powershell
# Beginner version
python app_beginner.py

# Original version  
python app.py
```

### Step 3: Open Your Browser
Visit: **http://127.0.0.1:5000**

## 🔑 Default Login Credentials

| User Type | Username | Password |
|-----------|----------|----------|
| **Admin** | `admin` | `admin123` |
| **Regular User** | `testuser` | `user123` |

## 📖 Learn More

- **`README_beginner.md`** - Complete beginner guide
- **`COMPARISON.md`** - Side-by-side version comparison  
- **`REFACTORING_SUMMARY.md`** - What was changed and why

## 🛠️ Troubleshooting

### Database Issues?
```powershell
.\reset_db.ps1
```

### Want to Compare Versions?
```powershell
.\start.ps1 -Version comparison
```

### Permission Errors?
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 🎓 Learning Path

1. **Start with beginner version** - Understand the basics
2. **Read the comparison guide** - See the differences  
3. **Try the original version** - Learn advanced patterns
4. **Experiment** - Add your own features!

---

**Ready to learn Flask? Pick your version and start coding! 🎉**
