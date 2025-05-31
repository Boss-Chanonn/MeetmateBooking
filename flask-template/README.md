# MeetMate - Meeting Room Booking Application

**MeetMate** is a meeting room booking web application built with Flask and SQLite. This project is perfect for learning web development fundamentals and understanding how modern web applications work.

## What You'll Learn

By studying and running this project, you will learn:
- **Flask Web Framework**: How to build web applications with Python
- **Database Operations**: Creating, reading, updating, and deleting data with SQLite
- **User Authentication**: Login/logout systems and password security
- **HTML Templates**: Creating dynamic web pages
- **CSS Styling**: Making websites look professional
- **Form Handling**: Processing user input from web forms
- **Session Management**: Keeping users logged in
- **Admin Systems**: Building different user roles and permissions

## Technologies Used

- **Backend**: Python Flask
- **Database**: SQLite with raw SQL queries
- **Frontend**: HTML, CSS, JavaScript (Bootstrap)
- **Authentication**: Flask sessions with password hashing

## How to Run This Project

### Step 1: Download or Clone the Project
1. Download the project as a ZIP file and extract it, OR

### Step 2: Check Python Installation
Make sure Python is installed on your computer:
```bash
python --version
```
You should see something like `Python 3.x.x`. If not, download Python from https://www.python.org/

### Step 3: Install Required Packages
Open a terminal/command prompt in the project folder and run:
```bash
pip install flask
```

### Step 4: Run the Application
In the same terminal, run:
```bash
python app.py
```

You should see output like:
```
Database initialized with default data!
* Running on http://127.0.0.1:5000
```

### Step 5: Open the Website
Open your web browser and go to: **http://127.0.0.1:5000**

### Step 6: Login and Test
Use these accounts to test the application:
- **Admin**: Email: `admin@meetmate.com` | Password: `admin123`
- **Regular User**: Email: `user@meetmate.com` | Password: `user123`

### Troubleshooting
- **Can't install Flask?** Try: `python -m pip install flask`
- **Python not found?** Make sure Python is installed and added to your system PATH
- **Port already in use?** Close the terminal and try again, or restart your computer

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

## Project Structure

Understanding the project files:

```
flask-template/
├── app.py                  # Main application file (start here!)
├── requirements.txt        # List of required Python packages
├── README.md              # This file - project documentation
├── instance/
│   └── meetmate.db        # SQLite database file (created automatically)
├── static/
│   ├── css/               # Stylesheets for the website
│   ├── images/            # Pictures and logos
│   └── js/                # JavaScript files
└── templates/             # HTML page templates
    ├── base.html          # Main template (other pages extend this)
    ├── login.html         # Login page
    ├── dashboard.html     # User dashboard
    ├── admin.html         # Admin dashboard
    └── ...               # Other page templates
```

## Key Files to Explore

1. **`app.py`** - The heart of the application. Start reading here!
2. **`templates/base.html`** - The main HTML template
3. **`templates/login.html`** - Simple login form example
4. **`static/css/style.css`** - Main stylesheet
5. **Database tables** - Check the database structure section above

## Next Steps

After getting the project running:
1. Try logging in as both admin and regular user
2. Create a new booking
3. Look at the code in `app.py` to understand how it works
4. Modify the CSS to change the website's appearance
5. Add new features or improve existing ones

## Need Help?

- Read through `app.py` carefully - it has comments explaining the code
- Check the Flask documentation: https://flask.palletsprojects.com/
- Look at the HTML templates to understand the user interface

