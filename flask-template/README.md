# 📅 MeetMate - Meeting Room Booking Web Application

**MeetMate** is a simple web application developed as a student project for booking meeting rooms. The app allows users to register, login, book meeting rooms, and manage their bookings. Admins have special access to manage users and meeting rooms.

## 🔧 Technologies Used

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python Flask
- **Database**: SQLite
- **API**: RESTful API via Flask

## 📁 Project Structure

```
MeetMate/
├── app.py                  # Main Flask application file (all routes & logic)
├── direct_db_init.py       # Database initialization script (used by reset_db.ps1)
├── reset_db.ps1            # PowerShell script to reset the database
├── run.ps1                 # PowerShell script to run the application
├── update_schema.py        # Script to check and update the database schema
├── templates/              # HTML templates
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── booking.html
│   ├── admin.html
│   ├── admin_book.html     # Admin booking interface
│   └── admin_booking_confirm.html  # Admin booking confirmation
├── static/                 # Static assets (CSS, JS, Images)
│   ├── css/
│   ├── js/
│   └── images/
├── instance/               # SQLite database folder
│   └── meetmate.db
└── requirements.txt        # Python dependencies
```

## 🔑 Core Features

### 1. Authentication
- User registration via `/register`
- User login via `/login`
- Session-based login handling

### 2. User Functions
- View available meeting rooms
- Book rooms by selecting date/time
- Cancel existing bookings
- Edit personal profile

### 3. Admin Functions
- View all user bookings
- Edit user information
- Add new meeting rooms to the system
- Book rooms on behalf of clients

## 🗃️ Database Schema Overview

### Users Table
```sql
id, username, email, password, role
```

### Rooms Table
```sql
id, name, location, capacity
```

### Bookings Table
```sql
id, user_id, room_id, date, time_start, time_end, booking_admin_id
```

## 🚀 How to Run (Development)

1. Clone the repository
2. Set up a Python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   .\run.ps1
   ```
5. Visit `http://localhost:5000` in your browser

## 📌 Default Login Credentials

- **Admin User**:
  - Username: `admin`
  - Password: `admin123`
- **Test User**:
  - Username: `testuser`
  - Password: `password`

## 💾 Database Management

- To reset the database to its initial state:
  ```bash
  .\reset_db.ps1
  ```
- The database is stored in the `instance/meetmate.db` file
- Schema updates are checked automatically when running the application

## 📚 Future Improvements

- Add calendar view for bookings
- Send email confirmation on booking
- Responsive UI for mobile use
- Use Flask Blueprints to organize code better

---

Developed with ❤️ by software engineering students.
