# -*- coding: utf-8 -*-
"""
MeetMate - Meeting Room Booking Application
Flask web application for booking meeting rooms
"""

import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, date, time
import calendar
from functools import wraps

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'meetmate_secret_key_v2_2025'

# ============================================================================
# DATABASE FUNCTIONS
# ============================================================================

def get_database_path():
    """Get database file path"""
    # Get the directory where our app.py file is located
    app_directory = app.root_path
    
    # Create 'instance' subdirectory for our database
    instance_directory = os.path.join(app_directory, 'instance')
    os.makedirs(instance_directory, exist_ok=True)
    
    # Full path to our database file
    database_path = os.path.join(instance_directory, 'meetmate.db')
    
    return database_path

def get_database_connection():
    """Connect to SQLite database"""
    db_path = get_database_path()
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection

def initialize_database():
    """Create database tables"""
    connection = get_database_connection()
    cursor = connection.cursor()
    
    try:
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                firstname TEXT,
                lastname TEXT,
                dob TEXT,
                address TEXT,
                role TEXT DEFAULT 'user'
            )
        ''')
        
        # Rooms table  
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rooms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                location TEXT NOT NULL,
                capacity INTEGER NOT NULL,
                room_type TEXT DEFAULT 'conference'
            )
        ''')
        
        # Add room_type column if it doesn't exist (for existing databases)
        try:
            cursor.execute('ALTER TABLE rooms ADD COLUMN room_type TEXT DEFAULT "conference"')
        except sqlite3.OperationalError:
            # Column already exists, ignore
            pass
        
        # Bookings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                room_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                time_start TEXT NOT NULL,
                time_end TEXT NOT NULL,
                booking_admin_id INTEGER,
                notes TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (room_id) REFERENCES rooms (id),
                FOREIGN KEY (booking_admin_id) REFERENCES users (id)
            )
        ''')
        
        connection.commit()
        create_default_data_if_needed(cursor, connection)
        print("Database initialized successfully!")
        
    except Exception as error:
        print(f"Error initializing database: {error}")
        connection.rollback()
    finally:
        connection.close()

def create_default_data_if_needed(cursor, connection):
    """Create default admin user and sample rooms if database is empty"""
    # Check if users exist
    cursor.execute("SELECT COUNT(*) as count FROM users")
    user_count = cursor.fetchone()['count']
    
    if user_count == 0:
        print("Creating default users...")
        
        # admin user - password is admin123
        admin_password = generate_password_hash('admin123')
        cursor.execute('''
            INSERT INTO users (username, email, password, firstname, lastname, role)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ('admin', 'admin@meetmate.com', admin_password, 'Admin', 'User', 'admin'))
        
        # regular test user
        user_password = generate_password_hash('user123')
        cursor.execute('''
            INSERT INTO users (username, email, password, firstname, lastname, role)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ('testuser', 'user@meetmate.com', user_password, 'Test', 'User', 'user'))
        
        print("Default users created")
      # Check if rooms exist
    cursor.execute("SELECT COUNT(*) as count FROM rooms")
    room_count = cursor.fetchone()['count']
    
    if room_count == 0:
        print("Creating sample rooms...")
        
        rooms = [
            # Circle Table rooms (6 rooms, capacity 6-8)
            ('Circle Table - Room A', 'Floor 1, East Wing', 6, 'Circle Table'),
            ('Circle Table - Room B', 'Floor 1, West Wing', 8, 'Circle Table'),
            ('Circle Table - Room C', 'Floor 2, East Wing', 6, 'Circle Table'),
            ('Circle Table - Room D', 'Floor 2, West Wing', 8, 'Circle Table'),
            ('Circle Table - Room E', 'Floor 3, Center', 7, 'Circle Table'),
            ('Circle Table - Room F', 'Floor 3, East Wing', 7, 'Circle Table'),
            
            # Long Table rooms (6 rooms, capacity 12-16)
            ('Long Table - Room A', 'Floor 1, Conference Wing', 12, 'Long Table'),
            ('Long Table - Room B', 'Floor 2, Conference Wing', 14, 'Long Table'),
            ('Long Table - Room C', 'Floor 3, Conference Wing', 16, 'Long Table'),
            ('Long Table - Room D', 'Floor 1, Executive Wing', 14, 'Long Table'),
            ('Long Table - Room E', 'Floor 2, Executive Wing', 15, 'Long Table'),
            ('Long Table - Room F', 'Floor 3, Executive Wing', 13, 'Long Table'),
            
            # Square Table rooms (6 rooms, capacity 4-6)
            ('Square Table - Room A', 'Floor 1, Collaboration Zone', 4, 'Square Table'),
            ('Square Table - Room B', 'Floor 1, Innovation Hub', 6, 'Square Table'),
            ('Square Table - Room C', 'Floor 2, Collaboration Zone', 4, 'Square Table'),
            ('Square Table - Room D', 'Floor 2, Innovation Hub', 5, 'Square Table'),
            ('Square Table - Room E', 'Floor 3, Team Area', 6, 'Square Table'),
            ('Square Table - Room F', 'Floor 3, Collaboration Zone', 5, 'Square Table')
        ]
        
        for name, location, capacity, room_type in rooms:
            cursor.execute('''
                INSERT INTO rooms (name, location, capacity, room_type)
                VALUES (?, ?, ?, ?)
            ''', (name, location, capacity, room_type))
        
        print("Sample rooms created (18 total: 6 of each type)")    
    connection.commit()

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
def get_user_by_id(user_id):
    """Get user by ID"""
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    connection.close()
    
    if user:
        return dict(user)
    return None

def get_user_by_username(username):
    """Get user by username"""
    connection = get_database_connection()
    cursor = connection.cursor()
    
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    
    connection.close()
    
    if user:
        return dict(user)
    return None

def get_user_by_email(email):
    """Get user by email"""
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    connection.close()
    
    if user:
        return dict(user)
    return None

def get_all_rooms():
    """Get all meeting rooms"""
    conn = get_database_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rooms ORDER BY name")
    rooms = cursor.fetchall()
    conn.close()
    return [dict(room) for room in rooms]

def get_room_by_id(room_id):
    """Get room by ID"""
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM rooms WHERE id = ?", (room_id,))
    room = cursor.fetchone()
    connection.close()
    if room:
        return dict(room)
    return None

def get_user_bookings(user_id):
    """Get all bookings for a user"""
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute('''
        SELECT 
            b.id,
            b.date,
            b.time_start,
            b.time_end,
            b.notes,
            r.name as room_name,
            r.location as room_location
        FROM bookings b
        JOIN rooms r ON b.room_id = r.id
        WHERE b.user_id = ?
        ORDER BY b.date, b.time_start
    ''', (user_id,))
    bookings = cursor.fetchall()
    connection.close()
    return [dict(booking) for booking in bookings]

def check_room_availability(room_id, date, time_start, time_end, exclude_booking_id=None):
    """Check if room is available for booking"""
    connection = get_database_connection()
    cursor = connection.cursor()
    
    query = '''
        SELECT COUNT(*) as count
        FROM bookings 
        WHERE room_id = ? 
        AND date = ? 
        AND (
            (time_start <= ? AND time_end > ?) OR
            (time_start < ? AND time_end >= ?) OR
            (time_start >= ? AND time_end <= ?)
        )
    '''
    
    params = [room_id, date, time_start, time_start, time_end, time_end, time_start, time_end]
    
    if exclude_booking_id:
        query += " AND id != ?"
        params.append(exclude_booking_id)
    
    cursor.execute(query, params)
    result = cursor.fetchone()
    connection.close()
    
    return result['count'] == 0

def create_booking(user_id, room_id, date, time_start, time_end, admin_id=None, notes=None):
    """Create a new booking"""
    connection = get_database_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO bookings (user_id, room_id, date, time_start, time_end, booking_admin_id, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, room_id, date, time_start, time_end, admin_id, notes))
        
        booking_id = cursor.lastrowid
        connection.commit()
        connection.close()
        return booking_id
        
    except Exception as error:
        print(f"Error creating booking: {error}")
        connection.rollback()
        connection.close()
        return None

def get_rooms_by_type(room_type):
    """Get all rooms of a specific type"""
    conn = get_database_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rooms WHERE room_type = ? ORDER BY name", (room_type,))
    rooms = cursor.fetchall()
    conn.close()
    return [dict(room) for room in rooms]

def get_available_rooms_by_type(room_type, date, time_start, time_end):
    """Get available rooms of a specific type for given date and time"""
    rooms = get_rooms_by_type(room_type)
    available_rooms = []
    
    for room in rooms:
        if check_room_availability(room['id'], date, time_start, time_end):
            available_rooms.append(room)
    
    return available_rooms

def get_all_room_types():
    """Get all distinct room types in custom order"""
    conn = get_database_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT room_type FROM rooms")
    types = cursor.fetchall()
    conn.close()
    
    # Define custom order: Square Table, Circle Table, Long Table
    room_types = [row['room_type'] for row in types]
    custom_order = ['Square Table', 'Circle Table', 'Long Table']
    
    # Return room types in custom order, only including types that exist in DB
    ordered_types = []
    for room_type in custom_order:
        if room_type in room_types:
            ordered_types.append(room_type)
    
    # Add any additional room types not in our custom order (future-proofing)
    for room_type in room_types:
        if room_type not in ordered_types:
            ordered_types.append(room_type)
    
    return ordered_types

# ============================================================================
# AUTHENTICATION DECORATORS
# ============================================================================

def login_required(f):
    """Decorator to ensure user is logged in"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'error')
            return redirect(url_for('login'))
        
        user = get_user_by_id(session['user_id'])
        if not user:
            session.clear()
            flash('Your account is no longer valid. Please login again.', 'warning')
            return redirect(url_for('login'))
        
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to ensure user is admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash('Admin access required for this page', 'error')
            return redirect(url_for('dashboard'))
        
        user=get_user_by_id(session['user_id'])
        if not user or user['role'] != 'admin':
            session.clear()
            flash('Admin session expired. Please login again.', 'warning')
            return redirect(url_for('login'))
        
        return f(*args, **kwargs)
    return decorated_function

# ============================================================================
# ROUTES - MAIN APPLICATION
# ============================================================================

@app.route('/')
def index():
    """Home page"""
    # Clear all sessions when accessing home page
    session.clear()
    # Get all rooms to display on homepage
    rooms = get_all_rooms()
    return render_template('home.html', rooms=rooms)

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')

# ============================================================================
# ROUTES - AUTHENTICATION
# ============================================================================

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'GET':
        return render_template('register.html')
    
    # Get form data
    email = request.form['email'].strip()
    password = request.form['password']
    confirm_password = request.form['confirm_password']
    firstname = request.form.get('firstname', '').strip()
    lastname = request.form.get('lastname', '').strip()
    dob = request.form.get('dob', '').strip()
    address = request.form.get('address', '').strip()
    
    # Basic validation
    if not email or not password or not confirm_password:
        flash('Email, password, and confirm password are required', 'error')
        return redirect(url_for('register'))
    
    if password != confirm_password:
        flash('Passwords do not match', 'error')
        return redirect(url_for('register'))
    
    # Check if email already exists
    if get_user_by_email(email):
        flash('Email already registered. Please use a different email.', 'error')
        return redirect(url_for('register'))
    
    # Create username from email
    username = email.split('@')[0]
    base_username = username
    counter = 1
    while get_user_by_username(username):
        username = f"{base_username}{counter}"
        counter += 1
    
    # Create user account
    connection = get_database_connection()
    cursor = connection.cursor()
    
    try:
        password_hash = generate_password_hash(password)
        cursor.execute('''
            INSERT INTO users (username, email, password, firstname, lastname, dob, address, role)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (username, email, password_hash, firstname, lastname, dob, address, 'user'))
        
        connection.commit()
        flash('Registration successful! You can now login with your email address.', 'success')
        return redirect(url_for('login'))
        
    except Exception as error:
        connection.rollback()
        flash(f'Registration failed: {error}', 'error')
        return redirect(url_for('register'))
        
    finally:
        connection.close()

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if 'user_id' in session:
        # If user is already logged in, redirect based on role
        if session.get('role') == 'admin':
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('booking'))
    
    if request.method == 'GET':
        return render_template('login.html')
    
    # Process login
    email = request.form['email'].strip()
    password = request.form['password']
    
    user = get_user_by_email(email)
    
    if not user or not check_password_hash(user['password'], password):
        flash('Invalid email or password', 'error')
        return redirect(url_for('login'))
    
    # Login successful
    session.clear()
    session['user_id'] = user['id']
    session['username'] = user['username']
    session['role'] = user['role']
    
    flash(f'Welcome back, {user["username"]}!', 'success')
      # Redirect based on user role
    if user['role'] == 'admin':
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('booking'))

@app.route('/logout')
def logout():
    """Log out user"""
    session.clear()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('index'))

# ============================================================================
# ROUTES - USER DASHBOARD & BOOKING
# ============================================================================

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard page"""
    connection = get_database_connection()
    cursor = connection.cursor()
    
    # Get current user's ID from session
    user_id = session['user_id']
    
    # Get current user information
    user = get_user_by_id(user_id)
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('logout'))
    
    # Get current date and time for comparison
    now = datetime.now()
    current_date = now.date()
    current_time = now.time()
    
    # Initialize variables for today's and upcoming bookings
    today_bookings = []
    upcoming_bookings = []
    today_date = ''
    user_today_bookings = []
    user_upcoming_bookings = []
    
    # Only fetch today's and upcoming bookings if user is admin
    if session.get('role') == 'admin':
        # Get today's date for filtering
        from datetime import date, timedelta
        today = date.today()
        today_str = today.strftime('%Y-%m-%d')
        today_date = today.strftime('%B %d, %Y')
        
        # Calculate date range for upcoming bookings (next 7 days excluding today)
        tomorrow = today + timedelta(days=1)
        next_week = today + timedelta(days=7)
        tomorrow_str = tomorrow.strftime('%Y-%m-%d')
        next_week_str = next_week.strftime('%Y-%m-%d')
        
        # Get today's bookings with user and room information
        cursor.execute('''
            SELECT 
                b.id,
                b.date,
                b.time_start,
                b.time_end,
                b.notes,
                u.username,
                r.name as room_name,
                admin.username as admin_name
            FROM bookings b
            JOIN users u ON b.user_id = u.id
            JOIN rooms r ON b.room_id = r.id
            LEFT JOIN users admin ON b.booking_admin_id = admin.id
            WHERE b.date = ?
            ORDER BY b.time_start
        ''', (today_str,))
        
        for row in cursor.fetchall():
            booking = dict(row)
            # Determine who made the booking
            if booking['admin_name']:
                booking['booked_by'] = f"Admin: {booking['admin_name']}"
            else:
                booking['booked_by'] = "Self"
            
            # Add time-based logic for today's bookings
            booking_date = date.fromisoformat(booking['date'])
            booking_start_time = time.fromisoformat(booking['time_start'] + ':00' if len(booking['time_start']) == 5 else booking['time_start'])
            
            if booking_date == current_date:
                booking['can_cancel'] = current_time < booking_start_time
                booking['status'] = 'Complete' if current_time >= booking_start_time else None
            else:
                booking['can_cancel'] = True
                booking['status'] = None
                
            today_bookings.append(booking)
        
        # Get upcoming bookings (next 7 days)
        cursor.execute('''
            SELECT 
                b.id,
                b.date,
                b.time_start,
                b.time_end,
                b.notes,
                u.username,
                r.name as room_name,
                admin.username as admin_name
            FROM bookings b
            JOIN users u ON b.user_id = u.id
            JOIN rooms r ON b.room_id = r.id
            LEFT JOIN users admin ON b.booking_admin_id = admin.id
            WHERE b.date >= ? AND b.date <= ?
            ORDER BY b.date, b.time_start
            LIMIT 10
        ''', (tomorrow_str, next_week_str))
        
        for row in cursor.fetchall():
            booking = dict(row)
            # Determine who made the booking
            if booking['admin_name']:
                booking['booked_by'] = f"Admin: {booking['admin_name']}"
            else:
                booking['booked_by'] = "Self"
              # Format the date for display
            booking_date = date.fromisoformat(booking['date'])
            booking['formatted_date'] = booking_date.strftime('%a, %b %d')
            
            # Add time-based logic for upcoming bookings (all future bookings can be cancelled)
            booking['can_cancel'] = True
            booking['status'] = None
            
            upcoming_bookings.append(booking)
    else:
        # For regular users, get their today's and upcoming bookings
        from datetime import date, timedelta
        today = date.today()
        today_str = today.strftime('%Y-%m-%d')
        today_date = today.strftime('%B %d, %Y')
        
        # Calculate date range for upcoming bookings (next 7 days excluding today)
        tomorrow = today + timedelta(days=1)
        next_week = today + timedelta(days=7)
        tomorrow_str = tomorrow.strftime('%Y-%m-%d')
        next_week_str = next_week.strftime('%Y-%m-%d')
        
        # Get user's today's bookings
        cursor.execute('''
            SELECT 
                b.id,
                b.date,
                b.time_start,
                b.time_end,
                b.notes,
                r.name as room_name,
                r.location as room_location
            FROM bookings b
            JOIN rooms r ON b.room_id = r.id
            WHERE b.user_id = ? AND b.date = ?
            ORDER BY b.time_start
        ''', (user_id, today_str))
        
        for row in cursor.fetchall():
            booking = dict(row)
            
            # Add time-based logic for today's bookings
            booking_date = date.fromisoformat(booking['date'])
            booking_start_time = time.fromisoformat(booking['time_start'] + ':00' if len(booking['time_start']) == 5 else booking['time_start'])
            
            if booking_date == current_date:
                booking['can_cancel'] = current_time < booking_start_time
                booking['status'] = 'Complete' if current_time >= booking_start_time else None
            else:
                booking['can_cancel'] = True
                booking['status'] = None
                
            user_today_bookings.append(booking)
        
        # Get user's upcoming bookings (next 7 days)
        cursor.execute('''
            SELECT 
                b.id,
                b.date,
                b.time_start,
                b.time_end,
                b.notes,
                r.name as room_name,
                r.location as room_location
            FROM bookings b
            JOIN rooms r ON b.room_id = r.id
            WHERE b.user_id = ? AND b.date >= ? AND b.date <= ?
            ORDER BY b.date, b.time_start
            LIMIT 10
        ''', (user_id, tomorrow_str, next_week_str))
        
        for row in cursor.fetchall():
            booking = dict(row)
            # Format the date for display
            booking_date = date.fromisoformat(booking['date'])
            booking['formatted_date'] = booking_date.strftime('%a, %b %d')
            
            # Add time-based logic for upcoming bookings (all future bookings can be cancelled)
            booking['can_cancel'] = True
            booking['status'] = None
            
            user_upcoming_bookings.append(booking)
    
    connection.close()
      # Show the dashboard with user's bookings and today's overview
    return render_template('dashboard.html',
                         user=user,
                         today_bookings=today_bookings,
                         today_date=today_date,
                         upcoming_bookings=upcoming_bookings,
                         user_today_bookings=user_today_bookings,
                         user_upcoming_bookings=user_upcoming_bookings)

@app.route('/booking', methods=['GET', 'POST'])
@login_required
def booking():
    """Room type selection page - first step of booking"""
    # If user is admin, redirect to admin booking page
    if session.get('role') == 'admin':
        return redirect(url_for('admin_book'))
    
    if request.method == 'GET':
        # Show room type selection
        room_types = get_all_room_types()
        current_date = datetime.now().strftime('%Y-%m-%d')
        return render_template('booking.html', room_types=room_types, current_date=current_date)
    
    # Process room type selection (POST request)
    room_type = request.form.get('room_type')
    date = request.form.get('date')
    time_start = request.form.get('time_start')
    time_end = request.form.get('time_end')
    
    if not all([room_type, date, time_start, time_end]):
        flash('Please fill in all required fields.', 'error')
        return redirect(url_for('booking'))
    
    # Validate booking duration (must be 1-8 hours)
    try:
        start_hour = int(time_start.split(':')[0])
        end_hour = int(time_end.split(':')[0])
        duration = end_hour - start_hour
        
        if duration < 1 or duration > 8:
            flash(f'Booking duration must be between 1 and 8 hours (you selected {duration} hours)', 'error')
            return redirect(url_for('booking'))
    except (ValueError, IndexError):
        flash('Invalid time format. Please try again.', 'error')
        return redirect(url_for('booking'))
    
    # Store booking details in session and redirect to room selection
    session['booking_data'] = {
        'room_type': room_type,
        'date': date,
        'time_start': time_start,
        'time_end': time_end,
        'duration': duration
    }
    
    return redirect(url_for('select_room'))

@app.route('/select_room', methods=['GET', 'POST'])
@login_required
def select_room():
    """Room selection page - second step of booking"""
    if 'booking_data' not in session:
        flash('Please start the booking process from the beginning.', 'error')
        return redirect(url_for('booking'))
    
    booking_data = session['booking_data']
    
    if request.method == 'GET':
        # Show available rooms of selected type
        available_rooms = get_available_rooms_by_type(
            booking_data['room_type'],
            booking_data['date'],
            booking_data['time_start'],
            booking_data['time_end']
        )
        
        if not available_rooms:
            flash(f'No {booking_data["room_type"]} rooms are available for the selected date and time. Please choose a different time.', 'error')
            return redirect(url_for('booking'))
        
        return render_template('select_room.html', 
                             rooms=available_rooms, 
                             booking_data=booking_data)
    
    # Process room selection (POST request)
    room_id = request.form.get('room_id')
    
    if not room_id:
        flash('Please select a room.', 'error')
        return redirect(url_for('select_room'))
      # Double-check room availability
    if not check_room_availability(room_id, booking_data['date'], 
                                 booking_data['time_start'], booking_data['time_end']):
        flash('This room is no longer available. Please select a different room.', 'error')
        return redirect(url_for('select_room'))
      # Update booking data with selected room
    session['booking_data']['room_id'] = room_id
    
    # Get room details for confirmation page
    room = get_room_by_id(room_id)
    
    # Show booking confirmation page
    return render_template(
        'booking_confirm.html',
        room=room,
        booking_date=booking_data['date'],
        time_start=booking_data['time_start'],
        time_end=booking_data['time_end'],
        duration=booking_data['duration']
    )

@app.route('/confirm_booking', methods=['POST'])
@login_required
def confirm_booking():
    """Process booking confirmation"""
    # Check if booking data exists in session
    if 'booking_data' not in session:
        # Try to get data from form as fallback
        room_id = request.form.get('room_id')
        date = request.form.get('date')
        time_start = request.form.get('time_start')
        time_end = request.form.get('time_end')
        
        if all([room_id, date, time_start, time_end]):
            # Reconstruct session data from form
            start_hour = int(time_start.split(':')[0])
            end_hour = int(time_end.split(':')[0])
            duration = end_hour - start_hour
            
            session['booking_data'] = {
                'room_id': room_id,
                'date': date,
                'time_start': time_start,
                'time_end': time_end,
                'duration': duration
            }
        else:
            flash('Booking information not found. Please start the booking process again.', 'error')
            return redirect(url_for('booking'))
    
    # Get user's choice (confirm or cancel)
    action = request.form.get('action')
    
    if action == 'cancel':
        # User cancelled the booking
        session.pop('booking_data', None)  # Remove booking data from session
        flash('Booking cancelled', 'info')
        return redirect(url_for('booking'))
      # User confirmed the booking - proceed to payment page
    booking_data = session['booking_data']
    
    # Ensure room_id is available
    if 'room_id' not in booking_data:
        # Try to get room_id from form data
        room_id = request.form.get('room_id')
        if room_id:
            booking_data['room_id'] = room_id
            session['booking_data'] = booking_data
        else:
            flash('Room information is missing. Please start the booking process again.', 'error')
            return redirect(url_for('booking'))
    
    room = get_room_by_id(booking_data['room_id'])
    
    # Calculate duration for payment page
    start_hour = int(booking_data['time_start'].split(':')[0])
    end_hour = int(booking_data['time_end'].split(':')[0])
    duration = end_hour - start_hour
    
    # Show payment page
    return render_template(
        'payment.html',
        room=room,
        booking_date=booking_data['date'],
        time_start=booking_data['time_start'],
        time_end=booking_data['time_end'],
        duration=duration
    )

@app.route('/process_payment', methods=['POST'])
@login_required
def process_payment():
    """Process payment and create booking"""
    # Check if booking data exists in session
    if 'booking_data' not in session:
        flash('Booking information not found. Please try again.', 'error')
        return redirect(url_for('booking'))
      # Get payment details from form
    # TODO: in real app would validate and process payment here
    card_holder = request.form['card_holder']
    card_number = request.form['card_number']
    expiry_date = request.form['expiry_date']
    cvv = request.form['cvv']
    
    # Get booking data from session
    booking_data = session.pop('booking_data')  # Remove from session since we're processing it
    
    # Double-check that room is still available
    if not check_room_availability(booking_data['room_id'], booking_data['date'], 
                                  booking_data['time_start'], booking_data['time_end']):
        flash('Sorry, this room was just booked by someone else. Please select another time.', 'error')
        return redirect(url_for('booking'))
    
    # Create the booking in the database
    booking_id = create_booking(
        user_id=session['user_id'],
        room_id=booking_data['room_id'],
        date=booking_data['date'],
        time_start=booking_data['time_start'],
        time_end=booking_data['time_end'],
        admin_id=None,  # This is a user booking, not admin booking
        notes=None
    )
    
    if not booking_id:
        flash('Failed to create booking. Please try again.', 'error')
        return redirect(url_for('booking'))
    
    # Generate confirmation code
    confirmation_code = f"MEET-{booking_id}-{datetime.now().strftime('%y%m%d')}"
    
    # Get room details for success page
    room = get_room_by_id(booking_data['room_id'])
    
    # Show booking success page
    return render_template(
        'booking_success.html',
        room=room,
        booking_date=booking_data['date'],
        time_start=booking_data['time_start'],
        time_end=booking_data['time_end'],
        confirmation_code=confirmation_code
    )

@app.route('/cancel_booking/<int:booking_id>')
@login_required
def cancel_booking(booking_id):
    """Cancel a booking"""
    connection = get_database_connection()
    cursor = connection.cursor()
    
    # Get booking details
    cursor.execute("SELECT * FROM bookings WHERE id = ?", (booking_id,))
    booking = cursor.fetchone()
    
    if not booking:
        connection.close()
        flash('Booking not found', 'error')
        return redirect(url_for('dashboard'))
    
    # Check permissions - users can only cancel their own bookings
    if booking['user_id'] != session['user_id'] and session.get('role') != 'admin':
        connection.close()
        flash('You do not have permission to cancel this booking', 'error')
        return redirect(url_for('dashboard'))
    
    # Delete the booking
    try:
        cursor.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
        connection.commit()
        flash('Booking cancelled successfully', 'success')
    except Exception as error:
        connection.rollback()
        flash(f'Failed to cancel booking: {error}', 'error')
    finally:
        connection.close()
    
    return redirect(url_for('dashboard'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile page"""    # Get current user information
    user = get_user_by_id(session['user_id'])
    
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('logout'))
    
    if request.method == 'GET':
        # Show profile form with current user data
        return render_template('profile.html', user=user)
    
    # Process profile update (POST request)
    
    # Get updated information from form
    new_email = request.form['email'].strip()
    firstname = request.form.get('firstname', '').strip()
    lastname = request.form.get('lastname', '').strip()
    dob = request.form.get('dob', '').strip()
    address = request.form.get('address', '').strip()
    new_password = request.form.get('password', '').strip()
      # Check if new email is already used by another user
    if new_email != user['email']:
        existing_user = get_user_by_email(new_email)
        if existing_user:
            flash('Email already in use by another user', 'error')
            return redirect(url_for('my_account'))
    
    # Update user information in database
    connection = get_database_connection()
    cursor = connection.cursor()
    
    try:
        # Prepare update query
        if new_password:
            # User wants to change password
            password_hash = generate_password_hash(new_password)
            cursor.execute('''
                UPDATE users 
                SET email = ?, firstname = ?, lastname = ?, dob = ?, address = ?, password = ?
                WHERE id = ?
            ''', (new_email, firstname, lastname, dob, address, password_hash, user['id']))
        else:            # Keep existing password
            cursor.execute('''
                UPDATE users 
                SET email = ?, firstname = ?, lastname = ?, dob = ?, address = ?
                WHERE id = ?
            ''', (new_email, firstname, lastname, dob, address, user['id']))
        
        connection.commit()
        
        # Update session with new user data if update was successful
        updated_user = get_user_by_id(user['id'])
        if updated_user:
            session['username'] = updated_user['username']  # Keep username in session for compatibility
            
        flash('Profile updated successfully', 'success')
        
    except Exception as error:
        connection.rollback()
        flash(f'Failed to update profile: {error}', 'error')
    finally:
        connection.close()
    
    return redirect(url_for('my_account'))

@app.route('/history')
@login_required
def history():
    """User booking history page"""
    user_id = session['user_id']
    
    # Get all bookings for this user
    user_bookings = get_user_bookings(user_id)
    
    # Get current date and time for comparison
    now = datetime.now()
    current_date = now.date()
    current_time = now.time()
    
    # Add cancellation eligibility and completion status to each booking
    for booking in user_bookings:
        booking_date = date.fromisoformat(booking['date'])
        booking_start_time = time.fromisoformat(booking['time_start'] + ':00' if len(booking['time_start']) == 5 else booking['time_start'])
        
        if booking_date > current_date:
            booking['can_cancel'] = True
            booking['status'] = 'Confirmed'
        elif booking_date == current_date:
            booking['can_cancel'] = current_time < booking_start_time
            booking['status'] = 'Complete' if current_time >= booking_start_time else 'Confirmed'
        else:
            booking['can_cancel'] = False
            booking['status'] = 'Complete'

    return render_template('history.html', bookings=user_bookings)

# ============================================================================
# ROUTES - ADMIN FUNCTIONS
# ============================================================================

@app.route('/admin')
@login_required
@admin_required
def admin():
    """Admin dashboard"""
    connection = get_database_connection()
    cursor = connection.cursor()
    
    # Get all users
    cursor.execute("SELECT * FROM users ORDER BY username")
    users = [dict(row) for row in cursor.fetchall()]
    
    # Get all rooms
    cursor.execute("SELECT * FROM rooms ORDER BY name")
    rooms = [dict(row) for row in cursor.fetchall()]
      # Get current date and time for comparison
    now = datetime.now()
    current_date = now.date()
    current_time = now.time()
    
    # Get today's date for filtering
    from datetime import date
    today = date.today().strftime('%Y-%m-%d')
    
    # Get today's bookings with user and room information
    cursor.execute('''
        SELECT 
            b.id,
            b.date,
            b.time_start,
            b.time_end,
            b.notes,
            u.username,
            r.name as room_name,
            admin.username as admin_name
        FROM bookings b
        JOIN users u ON b.user_id = u.id
        JOIN rooms r ON b.room_id = r.id
        LEFT JOIN users admin ON b.booking_admin_id = admin.id
        WHERE b.date = ?
        ORDER BY b.time_start
    ''', (today,))
    
    today_bookings = []
    for row in cursor.fetchall():
        booking = dict(row)
        # Determine who made the booking
        if booking['admin_name']:
            booking['booked_by'] = f"Admin: {booking['admin_name']}"
        else:
            booking['booked_by'] = "Self"
        
        # Add time-based logic for today's bookings
        booking_date = date.fromisoformat(booking['date'])
        booking_start_time = time.fromisoformat(booking['time_start'] + ':00' if len(booking['time_start']) == 5 else booking['time_start'])
        
        if booking_date == current_date:
            booking['can_cancel'] = current_time < booking_start_time
            booking['status'] = 'Complete' if current_time >= booking_start_time else None
        else:
            booking['can_cancel'] = True
            booking['status'] = None
            
        today_bookings.append(booking)
    
    # Get all bookings with user and room information
    cursor.execute('''
        SELECT 
            b.id,
            b.date,
            b.time_start,
            b.time_end,
            b.notes,
            u.username,
            r.name as room_name,
            admin.username as admin_name
        FROM bookings b
        JOIN users u ON b.user_id = u.id
        JOIN rooms r ON b.room_id = r.id        LEFT JOIN users admin ON b.booking_admin_id = admin.id
        ORDER BY b.date, b.time_start
    ''')
    
    all_bookings = []
    for row in cursor.fetchall():
        booking = dict(row)
        # Determine who made the booking
        if booking['admin_name']:
            booking['booked_by'] = "Admin"
        else:
            booking['booked_by'] = "Self"
        
        # Add time-based logic for all bookings
        booking_date = date.fromisoformat(booking['date'])
        booking_start_time = time.fromisoformat(booking['time_start'] + ':00' if len(booking['time_start']) == 5 else booking['time_start'])
        
        if booking_date > current_date:
            booking['can_cancel'] = True
            booking['status'] = None
        elif booking_date == current_date:
            booking['can_cancel'] = current_time < booking_start_time
            booking['status'] = 'Complete' if current_time >= booking_start_time else None
        else:
            booking['can_cancel'] = False
            booking['status'] = 'Complete'
            
        all_bookings.append(booking)
    
    connection.close()
    
    return render_template('admin.html', users=users, rooms=rooms, bookings=all_bookings, today_bookings=today_bookings, today_date=today)

@app.route('/admin/add_room', methods=['POST'])
@login_required
@admin_required
def add_room():
    """Add new room"""
    # Get room details from form
    name = request.form['name'].strip()
    location = request.form['location'].strip()
    capacity = request.form['capacity']
    room_type = request.form['room_type'].strip()
    
    # Validate input
    if not name or not location or not room_type:
        flash('Room name, location, and room type are required', 'error')
        return redirect(url_for('admin'))
    
    # Validate room type
    valid_room_types = ['Circle Table', 'Long Table', 'Square Table']
    if room_type not in valid_room_types:
        flash('Invalid room type selected', 'error')
        return redirect(url_for('admin'))
    
    try:
        capacity = int(capacity)
        if capacity <= 0:
            flash('Room capacity must be a positive number', 'error')
            return redirect(url_for('admin'))
    except ValueError:
        flash('Room capacity must be a valid number', 'error')
        return redirect(url_for('admin'))
    
    # Add room to database
    connection = get_database_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO rooms (name, location, capacity, room_type)
            VALUES (?, ?, ?, ?)
        ''', (name, location, capacity, room_type))
        
        connection.commit()
        flash('Room added successfully', 'success')
        
    except Exception as error:
        connection.rollback()
        flash(f'Failed to add room: {error}', 'error')
    finally:
        connection.close()
    
    return redirect(url_for('admin'))

@app.route('/admin/edit_user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def edit_user(user_id):
    """Edit user information"""
    # Get updated user information from form
    email = request.form['email'].strip()
    firstname = request.form.get('firstname', '').strip()
    lastname = request.form.get('lastname', '').strip()
    dob = request.form.get('dob', '').strip()
    address = request.form.get('address', '').strip()
    role = request.form['role']
    
    # Validate input
    if not email:
        flash('Email is required', 'error')
        return redirect(url_for('admin'))
    
    if role not in ['user', 'admin']:
        flash('Invalid role selected', 'error')
        return redirect(url_for('admin'))
    
    # Update user in database
    connection = get_database_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute('''
            UPDATE users 
            SET email = ?, firstname = ?, lastname = ?, dob = ?, address = ?, role = ?
            WHERE id = ?
        ''', (email, firstname, lastname, dob, address, role, user_id))
        
        connection.commit()
        
        # If the updated user is the current admin, update their session
        if user_id == session['user_id']:
            updated_user = get_user_by_id(user_id)
            if updated_user:
                session['username'] = updated_user['username']
                session['role'] = updated_user['role']
        
        flash('User updated successfully', 'success')
        
    except Exception as error:
        connection.rollback()
        flash(f'Failed to update user: {error}', 'error')
    finally:
        connection.close()
    
    return redirect(url_for('admin'))

@app.route('/admin/book', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_book():
    """Admin booking page - Step 1: Select client, room type, and time"""
    if request.method == 'GET':
        # Show admin booking form with room type selection (like client booking)
        room_types = get_all_room_types()
        
        # Get all regular users (non-admin) for the client dropdown
        connection = get_database_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE role = 'user' ORDER BY username")
        clients = [dict(row) for row in cursor.fetchall()]
        connection.close()
        
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        return render_template('admin_book.html', 
                             room_types=room_types, 
                             clients=clients, 
                             current_date=current_date)
    
    # Process admin booking form (POST request)
    
    # Get booking details from form
    client_id = request.form.get('client_id')
    room_type = request.form.get('room_type')
    date = request.form.get('date')
    time_start = request.form.get('time_start')
    time_end = request.form.get('time_end')
    booking_notes = request.form.get('booking_notes', '').strip()
    is_recurring = request.form.get('is_recurring') == '1'
    recurrence_type = request.form.get('recurrence_type', 'weekly')
    recurrence_count = request.form.get('recurrence_count', '4')
    
    # Validate all required fields
    if not all([client_id, room_type, date, time_start, time_end]):
        flash('Please fill in all required fields.', 'error')
        return redirect(url_for('admin_book'))
    
    # Validate booking duration
    try:
        start_hour = int(time_start.split(':')[0])
        end_hour = int(time_end.split(':')[0])
        duration = end_hour - start_hour
        
        if duration < 1 or duration > 8:
            flash(f'Booking duration must be between 1 and 8 hours (you selected {duration} hours)', 'error')
            return redirect(url_for('admin_book'))
    except (ValueError, IndexError):
        flash('Invalid time format. Please try again.', 'error')
        return redirect(url_for('admin_book'))
    
    # Store booking details in session and redirect to room selection
    session['admin_booking_data'] = {
        'client_id': client_id,
        'room_type': room_type,
        'date': date,
        'time_start': time_start,
        'time_end': time_end,
        'duration': duration,
        'booking_notes': booking_notes,
        'is_admin_booking': True,
        'is_recurring': is_recurring,
        'recurrence_type': recurrence_type,
        'recurrence_count': recurrence_count
    }
    
    return redirect(url_for('admin_select_room'))

@app.route('/admin/select_room', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_select_room():
    """Admin room selection page - Step 2: Choose specific room"""
    if 'admin_booking_data' not in session:
        flash('Please start the booking process from the beginning.', 'error')
        return redirect(url_for('admin_book'))
    
    booking_data = session['admin_booking_data']
    
    if request.method == 'GET':
        # Show available rooms of selected type
        available_rooms = get_available_rooms_by_type(
            booking_data['room_type'],
            booking_data['date'],
            booking_data['time_start'],
            booking_data['time_end']
        )
        
        if not available_rooms:
            flash(f'No {booking_data["room_type"]} rooms are available for the selected date and time. Please choose a different time.', 'error')
            return redirect(url_for('admin_book'))
        
        # Get client details for display
        client = get_user_by_id(booking_data['client_id'])
        booking_data['client_name'] = f"{client['firstname']} {client['lastname']}"
        
        return render_template('admin_select_room.html', 
                             rooms=available_rooms, 
                             booking_data=booking_data)    # Process room selection (POST request)
    room_id = request.form.get('room_id')
    
    if not room_id:
        flash('Please select a room.', 'error')
        return redirect(url_for('admin_select_room'))
    
    # Convert room_id to integer
    try:
        room_id = int(room_id)
    except (ValueError, TypeError):
        flash('Invalid room selection.', 'error')
        return redirect(url_for('admin_select_room'))
    
    # Double-check room availability
    if not check_room_availability(room_id, booking_data['date'], 
                                 booking_data['time_start'], booking_data['time_end']):
        flash('This room is no longer available. Please select a different room.', 'error')
        return redirect(url_for('admin_select_room'))    # Update booking data with selected room
    session['admin_booking_data']['room_id'] = room_id
    
    # Get room and client details for confirmation page
    room = get_room_by_id(room_id)
    client = get_user_by_id(booking_data['client_id'])
    
    # Show admin booking confirmation page
    return render_template(
        'admin_booking_confirm.html',
        room=room,
        client=client,
        booking_date=booking_data['date'],
        time_start=booking_data['time_start'],
        time_end=booking_data['time_end'],
        duration=booking_data['duration'],
        booking_notes=booking_data.get('booking_notes', ''),
        is_recurring=booking_data.get('is_recurring', False),
        recurrence_type=booking_data.get('recurrence_type', 'weekly'),
        recurrence_count=booking_data.get('recurrence_count', 4)
    )

@app.route('/admin/confirm_booking', methods=['POST'])
@login_required
@admin_required
def admin_confirm_booking():
    """Process admin booking confirmation"""
    # Get user's choice (confirm or cancel)
    action = request.form.get('action')
    
    if action == 'cancel':
        # Admin cancelled the booking
        session.pop('admin_booking_data', None)
        flash('Booking cancelled', 'info')
        return redirect(url_for('admin_book'))
      # Get booking data from form (since confirmation template sends data via form)
    room_id = request.form.get('room_id')
    date = request.form.get('date')
    time_start = request.form.get('time_start')
    time_end = request.form.get('time_end')
    client_id = request.form.get('client_id')
    booking_notes = request.form.get('booking_notes', '')
    is_recurring = request.form.get('is_recurring') == '1'
    recurrence_type = request.form.get('recurrence_type', 'weekly')
    recurrence_count = int(request.form.get('recurrence_count', 4))
    
    # Validate required fields
    if not all([room_id, date, time_start, time_end, client_id]):
        flash('Missing required booking information. Please try again.', 'error')
        return redirect(url_for('admin_book'))
    
    # Convert room_id and client_id to integers
    try:
        room_id = int(room_id)
        client_id = int(client_id)
    except (ValueError, TypeError):
        flash('Invalid booking information. Please try again.', 'error')
        return redirect(url_for('admin_book'))
    
    # Double-check room availability
    if not check_room_availability(room_id, date, time_start, time_end):
        flash('Sorry, this room was just booked by someone else. Please select another time.', 'error')
        return redirect(url_for('admin_book'))
    
    # Create the initial booking
    booking_id = create_booking(
        user_id=client_id,  # Booking is for the client
        room_id=room_id,
        date=date,
        time_start=time_start,
        time_end=time_end,
        admin_id=session['user_id'],  # Track which admin created this booking
        notes=booking_notes
    )
    
    if not booking_id:
        flash('Failed to create booking. Please try again.', 'error')
        return redirect(url_for('admin_book'))
    
    created_bookings = [booking_id]
    all_bookings_created = True
    
    # Create recurring bookings if requested
    if is_recurring and recurrence_count > 1:
        booking_date = datetime.strptime(date, '%Y-%m-%d')
        
        # Calculate date intervals based on recurrence type
        for i in range(1, recurrence_count):
            if recurrence_type == 'weekly':
                next_date = booking_date + timedelta(weeks=i)
            elif recurrence_type == 'biweekly':
                next_date = booking_date + timedelta(weeks=i*2)
            elif recurrence_type == 'monthly':
                # Handle monthly recurrence by adding months
                month = booking_date.month + i
                year = booking_date.year + (month - 1) // 12
                month = ((month - 1) % 12) + 1
                
                # Handle day overflow (e.g., Jan 31 -> Feb 28)
                try:
                    next_date = booking_date.replace(year=year, month=month)
                except ValueError:
                    # Day doesn't exist in target month, use last day of month
                    last_day = calendar.monthrange(year, month)[1]
                    next_date = booking_date.replace(year=year, month=month, day=last_day)
            
            formatted_date = next_date.strftime('%Y-%m-%d')
            
            # Check if room is available for this recurring date
            if check_room_availability(room_id, formatted_date, time_start, time_end):
                # Create recurring booking
                recurring_notes = f"{booking_notes} (Recurring {i+1}/{recurrence_count})"
                recurring_id = create_booking(
                    user_id=client_id,
                    room_id=room_id,
                    date=formatted_date,
                    time_start=time_start,
                    time_end=time_end,
                    admin_id=session['user_id'],
                    notes=recurring_notes
                )
                
                if recurring_id:
                    created_bookings.append(recurring_id)
                else:
                    all_bookings_created = False
            else:
                all_bookings_created = False
    
    # Generate confirmation code
    confirmation_code = f"MEET-{booking_id}-{datetime.now().strftime('%y%m%d')}"
    
    # Get room and client details for success page
    room = get_room_by_id(room_id)
    client = get_user_by_id(client_id)
    
    # Show admin booking success page
    return render_template(
        'admin_booking_success.html',
        room=room,
        client=client,
        booking_date=date,
        time_start=time_start,
        time_end=time_end,
        confirmation_code=confirmation_code,
        booking_notes=booking_notes,
        is_recurring=is_recurring,
        recurrence_type=recurrence_type,
        recurrence_count=recurrence_count,        all_bookings_created=all_bookings_created,
        created_bookings_count=len(created_bookings)
    )

@app.route('/admin/add_user', methods=['POST'])
@login_required
@admin_required
def add_user():
    """Add new user"""
    # Get user details from form
    email = request.form['email'].strip()
    firstname = request.form['firstname'].strip()
    lastname = request.form['lastname'].strip()
    password = request.form['password']
    dob = request.form.get('dob', '').strip()
    address = request.form.get('address', '').strip()
    role = request.form['role']
    
    # Generate username from email (part before @)
    username = email.split('@')[0]
    
    # Validate input
    if not email or not firstname or not lastname or not password:
        flash('Email, first name, last name, and password are required', 'error')
        return redirect(url_for('admin'))
    
    # Check if email already exists
    if get_user_by_email(email):
        flash('Email already exists. Please use a different email.', 'error')
        return redirect(url_for('admin'))
    
    # Check if username already exists (in case the auto-generated one conflicts)
    if get_user_by_username(username):
        # If username conflicts, append a number
        counter = 1
        original_username = username
        while get_user_by_username(f"{original_username}{counter}"):
            counter += 1
        username = f"{original_username}{counter}"
    
    # Validate role
    if role not in ['user', 'admin']:
        flash('Invalid role selected', 'error')
        return redirect(url_for('admin'))
    
    # Add user to database
    connection = get_database_connection()
    cursor = connection.cursor()
    
    try:
        password_hash = generate_password_hash(password)
        cursor.execute('''
            INSERT INTO users (username, email, password, firstname, lastname, dob, address, role)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (username, email, password_hash, firstname, lastname, dob, address, role))
        
        connection.commit()
        flash('User added successfully', 'success')
        
    except Exception as error:
        connection.rollback()
        flash(f'Failed to add user: {error}', 'error')
    finally:
        connection.close()
    
    return redirect(url_for('admin'))

@app.route('/admin/delete_room/<int:room_id>', methods=['POST'])
@login_required
@admin_required
def delete_room(room_id):
    """Delete room"""
    connection = get_database_connection()
    cursor = connection.cursor()
    
    try:
        # Check if room exists
        cursor.execute('SELECT name FROM rooms WHERE id = ?', (room_id,))
        room = cursor.fetchone()
        
        if not room:
            flash('Room not found', 'error')
            return redirect(url_for('admin'))
        
        room_name = room['name']
        
        # Check if room has active bookings
        cursor.execute('''
            SELECT COUNT(*) as booking_count 
            FROM bookings 
            WHERE room_id = ? AND date >= DATE('now')
        ''', (room_id,))
        
        active_bookings = cursor.fetchone()['booking_count']
        
        if active_bookings > 0:
            flash(f'Cannot delete room "{room_name}". It has {active_bookings} active booking(s).', 'error')
            return redirect(url_for('admin'))
        
        # Delete the room
        cursor.execute('DELETE FROM rooms WHERE id = ?', (room_id,))
        connection.commit()
        
        flash(f'Room "{room_name}" deleted successfully', 'success')
        
    except Exception as error:
        connection.rollback()
        flash(f'Failed to delete room: {error}', 'error')
    finally:
        connection.close()
    
    return redirect(url_for('admin'))

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def page_not_found(error):
    """404 error page"""
    return render_template('error404.html'), 404

# ============================================================================
# UTILITY ROUTES
# ============================================================================

@app.route('/my_account', methods=['GET', 'POST'])
@login_required
def my_account():
    """Combined user account page with Dashboard, Profile, and History tabs"""
    connection = get_database_connection()
    cursor = connection.cursor()
    
    # Get current user's ID from session
    user_id = session['user_id']
    
    # Get current user information for profile tab
    user = get_user_by_id(user_id)
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('logout'))
      # Handle profile update (POST request)
    if request.method == 'POST':
        # Get updated information from form
        new_email = request.form['email'].strip()
        firstname = request.form.get('firstname', '').strip()
        lastname = request.form.get('lastname', '').strip()
        dob = request.form.get('dob', '').strip()
        address = request.form.get('address', '').strip()
        new_password = request.form.get('password', '').strip()
          # Check if new email is already used by another user
        if new_email != user['email']:
            existing_user = get_user_by_email(new_email)
            if existing_user:
                flash('Email already in use by another user', 'error')
                return redirect(url_for('my_account'))
        
        # Update user information in database
        try:
            # Prepare update query based on whether password is being changed
            if new_password:
                # User wants to change password
                password_hash = generate_password_hash(new_password)
                cursor.execute('''
                    UPDATE users 
                    SET email = ?, firstname = ?, lastname = ?, dob = ?, address = ?, password = ?
                    WHERE id = ?
                ''', (new_email, firstname, lastname, dob, address, password_hash, user_id))
            else:
                # Keep existing password
                cursor.execute('''
                    UPDATE users 
                    SET email = ?, firstname = ?, lastname = ?, dob = ?, address = ?
                    WHERE id = ?
                ''', (new_email, firstname, lastname, dob, address, user_id))
            connection.commit()
            
            # Update session with new user data
            updated_user = get_user_by_id(user_id)
            if updated_user:
                session['username'] = updated_user['username']  # Keep username in session for compatibility
                
            flash('Profile updated successfully', 'success')
        except Exception as e:
            flash('Error updating profile', 'error')
        
        return redirect(url_for('my_account'))
    
    # GET request - prepare data for all tabs
    
    # Get current date and time for comparison
    now = datetime.now()
    current_date = now.date()
    current_time = now.time()
    
    # Dashboard data
    from datetime import date, timedelta
    today = date.today()
    today_str = today.strftime('%Y-%m-%d')
    today_date = today.strftime('%B %d, %Y')
    
    # Calculate date range for upcoming bookings (next 7 days excluding today)
    tomorrow = today + timedelta(days=1)
    next_week = today + timedelta(days=7)
    tomorrow_str = tomorrow.strftime('%Y-%m-%d')
    next_week_str = next_week.strftime('%Y-%m-%d')
    
    # Get user's today's bookings for dashboard tab
    cursor.execute('''
        SELECT 
            b.id,
            b.date,
            b.time_start,
            b.time_end,
            b.notes,
            r.name as room_name,
            r.location as room_location
        FROM bookings b
        JOIN rooms r ON b.room_id = r.id
        WHERE b.user_id = ? AND b.date = ?
        ORDER BY b.time_start
    ''', (user_id, today_str))
    
    user_today_bookings = []
    for row in cursor.fetchall():
        booking = dict(row)
        
        # Add time-based logic for today's bookings
        booking_date = date.fromisoformat(booking['date'])
        booking_start_time = time.fromisoformat(booking['time_start'] + ':00' if len(booking['time_start']) == 5 else booking['time_start'])
        
        if booking_date == current_date:
            booking['can_cancel'] = current_time < booking_start_time
            booking['status'] = 'Complete' if current_time >= booking_start_time else None
        else:
            booking['can_cancel'] = True
            booking['status'] = None
            
        user_today_bookings.append(booking)
    
    # Get user's upcoming bookings for dashboard tab (next 7 days)
    cursor.execute('''
        SELECT 
            b.id,
            b.date,
            b.time_start,
            b.time_end,
            b.notes,
            r.name as room_name,
            r.location as room_location
        FROM bookings b
        JOIN rooms r ON b.room_id = r.id
        WHERE b.user_id = ? AND b.date >= ? AND b.date <= ?
        ORDER BY b.date, b.time_start
        LIMIT 10
    ''', (user_id, tomorrow_str, next_week_str))
    
    user_upcoming_bookings = []
    for row in cursor.fetchall():
        booking = dict(row)
        
        # Format the date for display
        booking_date = date.fromisoformat(booking['date'])
        booking['formatted_date'] = booking_date.strftime('%a, %b %d')
        
        # Add time-based logic for upcoming bookings (all future bookings can be cancelled)
        booking['can_cancel'] = True
        booking['status'] = None
        
        user_upcoming_bookings.append(booking)
    
    # History data - get all bookings for this user
    user_bookings = get_user_bookings(user_id)
    
    # Add cancellation eligibility and completion status to each booking for history tab
    for booking in user_bookings:
        booking_date = date.fromisoformat(booking['date'])
        booking_start_time = time.fromisoformat(booking['time_start'] + ':00' if len(booking['time_start']) == 5 else booking['time_start'])
        
        if booking_date > current_date:
            booking['can_cancel'] = True
            booking['status'] = 'Confirmed'
        elif booking_date == current_date:
            booking['can_cancel'] = current_time < booking_start_time
            booking['status'] = 'Complete' if current_time >= booking_start_time else 'Confirmed'
        else:
            booking['can_cancel'] = False
            booking['status'] = 'Complete'
    
    connection.close()
    
    return render_template('my_account.html', 
                         user=user,
                         today_date=today_date,
                         user_today_bookings=user_today_bookings,
                         user_upcoming_bookings=user_upcoming_bookings,
                         bookings=user_bookings)

# ============================================================================
# APPLICATION STARTUP
# ============================================================================

if __name__ == '__main__':
    print("Initializing MeetMate application...")
    initialize_database()
    
    print("MeetMate - Meeting Room Booking System")
    print("Default login credentials:")
    print("   Admin: admin@meetmate.com / admin123")
    print("   User:  user@meetmate.com / user123")
    print("Starting web server at http://127.0.0.1:5000")
    print("Press Ctrl+C to stop the server")
    
    app.run(debug=True, host='127.0.0.1', port=5000)
