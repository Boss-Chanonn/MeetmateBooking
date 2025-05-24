# 📅 MeetMate - Beginner-Friendly Flask Application

**MeetMate** is a meeting room booking web application specifically designed for students learning Flask and database concepts. This version uses Python's built-in `sqlite3` module instead of SQLAlchemy ORM, making database operations transparent and easy to understand.

## 🎯 Learning Objectives

This project demonstrates:
- **Flask web framework fundamentals**
- **Raw SQL database operations** (without ORM abstraction)
- **User authentication and session management**
- **Form handling and validation**
- **Template rendering with Jinja2**
- **File organization and project structure**

## 🔧 Technologies Used

- **Backend**: Python Flask
- **Database**: SQLite with raw SQL queries
- **Frontend**: HTML, CSS, JavaScript (Bootstrap)
- **Authentication**: Flask sessions with password hashing

## 📁 Project Structure

```
MeetMate/
├── app_beginner.py         # Main Flask application
├── run_beginner.py         # Simple startup script
├── start.ps1               # Interactive launcher (Windows)
├── requirements.txt        # Python dependencies (flask, werkzeug)
├── COMPARISON.md           # Technical comparison documentation
├── QUICK_START.md          # 3-step setup guide
├── templates/              # HTML templates (17 files)
├── static/                 # CSS, JS, images
└── instance/               # SQLite database location
```

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

## 🔍 Code Structure Explanation

### Database Functions (`app_beginner.py`)

The application is organized into clear sections:

1. **Database Connection**
   ```python
   def get_database_connection():
       # Creates SQLite connection with proper configuration
   ```

2. **Helper Functions**
   ```python
   def get_user_by_id(user_id):
       # Raw SQL to find user by ID
       cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
   ```

3. **Authentication Decorators**
   ```python
   def login_required(f):
       # Ensures user is logged in before accessing protected routes
   ```

4. **Route Handlers**
   ```python
   @app.route('/login', methods=['GET', 'POST'])
   def login():
       # Handles user login with clear database queries
   ```

### Key Learning Features

- **Explicit SQL Queries**: Every database operation uses clear, readable SQL
- **Step-by-step Comments**: Each function explains what it does and why
- **Error Handling**: Proper try/catch blocks with rollback on errors
- **Security Best Practices**: Password hashing, session management, SQL injection prevention

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

## 📚 Learning Path

### Beginner Topics Covered

1. **Flask Basics**
   - Route handlers (`@app.route`)
   - Request methods (GET, POST)
   - Template rendering
   - Static files

2. **Database Operations**
   - Creating connections
   - Executing SQL queries
   - Handling results
   - Transaction management

3. **User Authentication**
   - Password hashing
   - Session management
   - Login decorators
   - Permission checking

4. **Form Handling**
   - Processing form data
   - Validation
   - Flash messages
   - Redirects

### Advanced Concepts (Optional)

5. **Security**
   - SQL injection prevention
   - Password security
   - Session security

6. **Error Handling**
   - Try/catch blocks
   - Database rollbacks
   - User-friendly error messages

## 🆚 Comparison with Original Version

| Feature | Original (`app.py`) | Beginner (`app_beginner.py`) |
|---------|-------------------|---------------------------|
| Database | SQLAlchemy ORM | Raw SQLite3 |
| Queries | Model.query.filter() | cursor.execute("SELECT...") |
| Dependencies | Flask, SQLAlchemy | Flask only |
| Learning Curve | Steeper (ORM abstraction) | Gentler (visible SQL) |
| Code Length | Shorter | Longer but clearer |

## 🛠️ Development Tips

### Adding New Features

1. **New Routes**: Add in the routes section with clear comments
2. **Database Changes**: Modify the `initialize_database()` function
3. **New Templates**: Add to the `templates/` directory
4. **Styling**: Modify files in `static/css/`

### Debugging

- **Database Issues**: Check the `instance/meetmate.db` file
- **Login Problems**: Verify user exists and password is correct
- **Permission Errors**: Check user role in database

### Common Tasks

**Add a new field to users table:**
```python
# In initialize_database() function
cursor.execute('''
    ALTER TABLE users ADD COLUMN new_field TEXT
''')
```

**Create a new route:**
```python
@app.route('/new_page')
@login_required  # If login is required
def new_page():
    # Your code here
    return render_template('new_template.html')
```

## 🧪 Testing the Application

1. **Register a new user** - Test user creation
2. **Login/logout** - Test authentication
3. **Book a room** - Test booking system
4. **Try admin features** - Test admin permissions
5. **Edit profile** - Test update operations

## 📖 Next Steps

After mastering this beginner version:

1. **Learn SQLAlchemy** - Compare with the original `app.py`
2. **Add features** - Implement room search, email notifications
3. **Improve UI** - Enhanced styling, responsive design
4. **Deploy** - Learn about production deployment
5. **Testing** - Write unit tests for your functions

## 🤝 Contributing

This is a learning project! Feel free to:
- Add comments for clarity
- Implement new features
- Improve error handling
- Enhance the user interface

---

**Happy Learning! 🎓**

*This beginner-friendly version prioritizes code clarity and learning over optimization.*
