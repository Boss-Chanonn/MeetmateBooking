# 📅 MeetMate - Beginner-Friendly Flask Application

**MeetMate** is a meeting room booking web application specifically designed for students learning Flask and database concepts. This version uses Python's built-in `sqlite3` module, making database operations transparent and easy to understand.

## 🔧 Technologies Used

- **Backend**: Python Flask
- **Database**: SQLite with raw SQL queries
- **Frontend**: HTML, CSS, JavaScript (Bootstrap)
- **Authentication**: Flask sessions with password hashing

## 🚀 Quick Start

### 1. Install Python Dependencies
```bash
pip install flask werkzeug
```

### 2. Run the Application
```bash
python run_beginner.py
```

### 3. Open Your Browser
Visit: http://127.0.0.1:5000

### 4. Login with Default Accounts
- **Admin**: `admin@meetmate.com` / `admin123`
- **User**: `user@meetmate.com` / `user123`

## 🗃️ Database Structure

The application uses three main tables:

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,           -- Hashed password for security
    firstname TEXT,
    lastname TEXT,
    dob TEXT,                        -- Date of birth
    address TEXT,
    role TEXT DEFAULT 'user'         -- 'user' or 'admin'
);
```

### Rooms Table
```sql
CREATE TABLE rooms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    location TEXT NOT NULL,
    capacity INTEGER NOT NULL
);
```

### Bookings Table
```sql
CREATE TABLE bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    room_id INTEGER NOT NULL,
    date TEXT NOT NULL,              -- YYYY-MM-DD format
    time_start TEXT NOT NULL,        -- HH:MM format
    time_end TEXT NOT NULL,          -- HH:MM format
    booking_admin_id INTEGER,        -- Admin who made booking (if applicable)
    notes TEXT,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (room_id) REFERENCES rooms (id)
);
```


## 🔑 Main Features

### For Regular Users
- ✅ Register new account
- ✅ Login/logout
- ✅ View and book available rooms
- ✅ Manage personal bookings
- ✅ Update profile information

### For Admin Users
- ✅ All user features
- ✅ View all users and bookings
- ✅ Add new meeting rooms
- ✅ Book rooms on behalf of users
- ✅ Create recurring bookings
- ✅ Edit user information

