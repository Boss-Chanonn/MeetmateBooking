# MeetMate - Meeting Room Booking Application

**MeetMate** is a meeting room booking web application built with Flask and SQLite. This project demonstrates basic web development concepts including user authentication, database operations, and CRUD functionality.

## Technologies Used

- **Backend**: Python Flask
- **Database**: SQLite with raw SQL queries
- **Frontend**: HTML, CSS, JavaScript (Bootstrap)
- **Authentication**: Flask sessions with password hashing

## Quick Start

### 1. Install Python Dependencies
```bash
pip install flask werkzeug
```

### 2. Run the Application
```bash
python app.py
```

### 3. Open Your Browser
Visit: http://127.0.0.1:5000

### 4. Login with Default Accounts
- **Admin**: `admin@meetmate.com` / `admin123`
- **User**: `user@meetmate.com` / `user123`

## Database Structure

The application uses three main tables:

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    firstname TEXT,
    lastname TEXT,
    dob TEXT,
    address TEXT,
    role TEXT DEFAULT 'user'
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
    date TEXT NOT NULL,
    time_start TEXT NOT NULL,
    time_end TEXT NOT NULL,
    booking_admin_id INTEGER,
    notes TEXT,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (room_id) REFERENCES rooms (id)
);
```


## Main Features

### For Regular Users
- Register new account
- Login/logout
- View and book available rooms
- Manage personal bookings
- Update profile information

### For Admin Users
- All user features
- View all users and bookings
- Add new meeting rooms
- Book rooms on behalf of users
- Create recurring bookings
- Edit user information

