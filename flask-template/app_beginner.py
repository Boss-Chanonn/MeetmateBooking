# -*- coding: utf-8 -*-
"""
MeetMate - Meeting Room Booking Application (Beginner-Friendly Version)
===========================================================================

This is a student-friendly version of the MeetMate Flask application that uses 
Python's built-in sqlite3 module instead of SQLAlchemy ORM. This approach makes 
it easier to understand how the database works and how SQL queries are executed.

Key Features:
- User registration and login
- Room booking system
- Admin management features
- Clear database operations using raw SQL

Author: Student Project
Date: 2025
"""

# ==============================================================================
# IMPORTS - All the tools we need for our web application
# ==============================================================================

import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import calendar
from functools import wraps

# ==============================================================================
# APPLICATION SETUP - Initialize Flask and configure basic settings
# ==============================================================================

# Create our Flask web application
app = Flask(__name__)

# Secret key used to encrypt session data (cookies)
# In production, this should be a random, secure string
app.config['SECRET_KEY'] = 'meetmate_secret_key_v2_2025'

# ==============================================================================
# DATABASE SETUP - Configure SQLite database connection
# ==============================================================================

def get_database_path():
    """
    Get the path where our SQLite database file will be stored.
    Creates the 'instance' directory if it doesn't exist.
    """
    # Get the directory where our app.py file is located
    app_directory = app.root_path
    
    # Create 'instance' subdirectory for our database
    instance_directory = os.path.join(app_directory, 'instance')
    os.makedirs(instance_directory, exist_ok=True)
    
    # Full path to our database file
    database_path = os.path.join(instance_directory, 'meetmate.db')
    
    return database_path

def get_database_connection():
    """
    Create and return a connection to our SQLite database.
    This function handles opening the database file and configuring it properly.
    """
    # Get the path to our database file
    db_path = get_database_path()
    
    # Connect to the SQLite database
    # If the file doesn't exist, SQLite will create it
    connection = sqlite3.connect(db_path)
    
    # Configure the connection to return rows as dictionaries
    # This makes it easier to work with query results
    connection.row_factory = sqlite3.Row
    
    return connection

def initialize_database():
    """
    Create all the tables we need for our application.
    This function is called when the app starts to ensure our database schema exists.
    """
    # Connect to the database
    connection = get_database_connection()
    cursor = connection.cursor()
    
    try:
        # Create USERS table - stores information about registered users
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
        
        # Create ROOMS table - stores information about meeting rooms
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rooms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                location TEXT NOT NULL,
                capacity INTEGER NOT NULL
            )
        ''')
        
        # Create BOOKINGS table - stores room reservations
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
        
        # Save all changes to the database
        connection.commit()
        
        # Check if we need to create default data (admin user and sample rooms)
        create_default_data_if_needed(cursor, connection)
        
        print("✅ Database initialized successfully!")
        
    except Exception as error:
        print(f"❌ Error initializing database: {error}")
        connection.rollback()  # Undo any changes if there was an error
    finally:
        connection.close()  # Always close the database connection

def create_default_data_if_needed(cursor, connection):
    """
    Create default admin user and sample rooms if the database is empty.
    This helps new users get started with the application.
    """
    # Check if any users exist
    cursor.execute("SELECT COUNT(*) as count FROM users")
    user_count = cursor.fetchone()['count']
    
    if user_count == 0:
        print("Creating default admin user...")
        
        # Create default admin user
        admin_password_hash = generate_password_hash('admin123')
        cursor.execute('''
            INSERT INTO users (username, email, password, firstname, lastname, role)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ('admin', 'admin@meetmate.com', admin_password_hash, 'Admin', 'User', 'admin'))
        
        # Create sample regular user
        user_password_hash = generate_password_hash('user123')
        cursor.execute('''
            INSERT INTO users (username, email, password, firstname, lastname, role)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ('testuser', 'user@meetmate.com', user_password_hash, 'Test', 'User', 'user'))
        
        print("✅ Default users created: admin/admin123 and testuser/user123")
    
    # Check if any rooms exist
    cursor.execute("SELECT COUNT(*) as count FROM rooms")
    room_count = cursor.fetchone()['count']
    
    if room_count == 0:
        print("Creating sample meeting rooms...")
        
        # Create sample meeting rooms
        sample_rooms = [
            ('Conference Room A', 'Floor 1, Building A', 10),
            ('Conference Room B', 'Floor 2, Building A', 8),
            ('Board Room', 'Floor 3, Building A', 15),
            ('Small Meeting Room', 'Floor 1, Building B', 4),
            ('Video Conference Room', 'Floor 2, Building B', 6)
        ]
        
        for room_name, location, capacity in sample_rooms:
            cursor.execute('''
                INSERT INTO rooms (name, location, capacity)
                VALUES (?, ?, ?)
            ''', (room_name, location, capacity))
        
        print("✅ Sample meeting rooms created!")
    
    # Save all changes
    connection.commit()

# ==============================================================================
# HELPER FUNCTIONS - Reusable functions for common database operations
# ==============================================================================

def get_user_by_id(user_id):
    """
    Find a user in the database by their ID number.
    Returns the user data as a dictionary, or None if not found.
    """
    connection = get_database_connection()
    cursor = connection.cursor()
    
    # Execute SQL query to find user by ID
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()  # Get the first (and only) result
    
    connection.close()
    
    # Convert sqlite3.Row to regular dictionary if user exists
    if user:
        return dict(user)
    return None

def get_user_by_username(username):
    """
    Find a user in the database by their username.
    Returns the user data as a dictionary, or None if not found.
    """
    connection = get_database_connection()
    cursor = connection.cursor()
    
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    
    connection.close()
    
    if user:
        return dict(user)
    return None

def get_user_by_email(email):
    """
    Find a user in the database by their email address.
    Returns the user data as a dictionary, or None if not found.
    """
    connection = get_database_connection()
    cursor = connection.cursor()
    
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    
    connection.close()
    
    if user:
        return dict(user)
    return None

def get_all_rooms():
    """
    Get all meeting rooms from the database.
    Returns a list of room dictionaries.
    """
    connection = get_database_connection()
    cursor = connection.cursor()
    
    cursor.execute("SELECT * FROM rooms ORDER BY name")
    rooms = cursor.fetchall()
    
    connection.close()
    
    # Convert each sqlite3.Row to a regular dictionary
    return [dict(room) for room in rooms]

def get_room_by_id(room_id):
    """
    Find a specific room by its ID number.
    Returns the room data as a dictionary, or None if not found.
    """
    connection = get_database_connection()
    cursor = connection.cursor()
    
    cursor.execute("SELECT * FROM rooms WHERE id = ?", (room_id,))
    room = cursor.fetchone()
    
    connection.close()
    
    if room:
        return dict(room)
    return None

def get_user_bookings(user_id):
    """
    Get all bookings for a specific user.
    Returns a list of booking dictionaries with room information included.
    """
    connection = get_database_connection()
    cursor = connection.cursor()
    
    # Join bookings with rooms to get room details
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
    """
    Check if a room is available for booking at a specific date and time.
    
    Parameters:
    - room_id: ID of the room to check
    - date: Date in YYYY-MM-DD format
    - time_start: Start time in HH:MM format
    - time_end: End time in HH:MM format
    - exclude_booking_id: Optional booking ID to exclude from the check (for editing existing bookings)
    
    Returns:
    - True if room is available, False if already booked
    """
    connection = get_database_connection()
    cursor = connection.cursor()
    
    # Build the SQL query
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
    
    # If we're checking for editing an existing booking, exclude it from the check
    if exclude_booking_id:
        query += " AND id != ?"
        params.append(exclude_booking_id)
    
    cursor.execute(query, params)
    result = cursor.fetchone()
    connection.close()
    
    # Room is available if there are no conflicting bookings
    return result['count'] == 0

def create_booking(user_id, room_id, date, time_start, time_end, admin_id=None, notes=None):
    """
    Create a new booking in the database.
    
    Parameters:
    - user_id: ID of the user making the booking
    - room_id: ID of the room being booked
    - date: Date in YYYY-MM-DD format
    - time_start: Start time in HH:MM format
    - time_end: End time in HH:MM format
    - admin_id: Optional ID of admin making booking on behalf of user
    - notes: Optional notes about the booking
    
    Returns:
    - ID of the newly created booking, or None if creation failed
    """
    connection = get_database_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO bookings (user_id, room_id, date, time_start, time_end, booking_admin_id, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, room_id, date, time_start, time_end, admin_id, notes))
        
        # Get the ID of the newly created booking
        booking_id = cursor.lastrowid
        
        connection.commit()
        connection.close()
        
        return booking_id
        
    except Exception as error:
        print(f"Error creating booking: {error}")
        connection.rollback()
        connection.close()
        return None

# ==============================================================================
# AUTHENTICATION DECORATORS - Functions to protect routes that require login
# ==============================================================================

def login_required(f):
    """
    Decorator to ensure user is logged in before accessing a route.
    If not logged in, redirects to login page.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is logged in (user_id exists in session)
        if 'user_id' not in session:
            flash('Please login to access this page', 'error')
            return redirect(url_for('login'))
        
        # Verify that the user still exists in the database
        user = get_user_by_id(session['user_id'])
        if not user:
            # User was deleted from database, clear session
            session.clear()
            flash('Your account is no longer valid. Please login again.', 'warning')
            return redirect(url_for('login'))
        
        # User is valid, continue to the requested page
        return f(*args, **kwargs)
    
    return decorated_function

def admin_required(f):
    """
    Decorator to ensure user is an admin before accessing a route.
    Must be used together with @login_required.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is logged in and has admin role
        if 'user_id' not in session or session.get('role') != 'admin':
            flash('Admin access required for this page', 'error')
            return redirect(url_for('dashboard'))
        
        # Verify that the admin user still exists and is still an admin
        user = get_user_by_id(session['user_id'])
        if not user or user['role'] != 'admin':
            session.clear()
            flash('Admin session expired. Please login again.', 'warning')
            return redirect(url_for('login'))
        
        # User is a valid admin, continue to the requested page
        return f(*args, **kwargs)
    
    return decorated_function

# ==============================================================================
# MAIN ROUTES - The web pages that users can visit
# ==============================================================================

@app.route('/')
def index():
    """
    Home page - the first page users see when they visit our website.
    If user is already logged in, redirect them to their dashboard.
    """
    # Check if user is already logged in
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    # Show the home page for visitors who aren't logged in
    return render_template('home.html')

@app.route('/about')
def about():
    """
    About page - information about the MeetMate application.
    This page is accessible to everyone (no login required).
    """
    return render_template('about.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    User registration page.
    GET: Show the registration form
    POST: Process the registration form and create new user account
    """
    if request.method == 'GET':
        # Show the registration form
        return render_template('register.html')
    
    # Process the registration form (POST request)
    
    # Get form data from the user
    email = request.form['email'].strip()
    password = request.form['password']
    confirm_password = request.form['confirm_password']
    firstname = request.form.get('firstname', '').strip()
    lastname = request.form.get('lastname', '').strip()
    dob = request.form.get('dob', '').strip()
    address = request.form.get('address', '').strip()
    
    # Validate that required fields are not empty
    if not email or not password or not confirm_password:
        flash('Email, password, and confirm password are required', 'error')
        return redirect(url_for('register'))
    
    # Check if passwords match
    if password != confirm_password:
        flash('Passwords do not match', 'error')
        return redirect(url_for('register'))
    
    # Check if email is already registered
    existing_email = get_user_by_email(email)
    if existing_email:
        flash('Email already registered. Please use a different email.', 'error')
        return redirect(url_for('register'))
    
    # Create username from email (use part before @ symbol)
    username = email.split('@')[0]
    
    # Check if this auto-generated username already exists, if so, add a number
    base_username = username
    counter = 1
    while get_user_by_username(username):
        username = f"{base_username}{counter}"
        counter += 1
    
    # Create new user account
    connection = get_database_connection()
    cursor = connection.cursor()
    
    try:
        # Hash the password for security (never store plain text passwords!)
        password_hash = generate_password_hash(password)
        
        # Insert new user into database
        cursor.execute('''
            INSERT INTO users (username, email, password, firstname, lastname, dob, address, role)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (username, email, password_hash, firstname, lastname, dob, address, 'user'))
        
        # Save changes to database
        connection.commit()
        
        flash('Registration successful! You can now login with your email address.', 'success')
        return redirect(url_for('login'))
        
    except Exception as error:
        # Something went wrong, undo any changes
        connection.rollback()
        flash(f'Registration failed: {error}', 'error')
        return redirect(url_for('register'))
        
    finally:
        # Always close the database connection
        connection.close()

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login page.
    GET: Show the login form
    POST: Process login credentials and start user session
    """
    # If user is already logged in, redirect to dashboard
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'GET':
        # Show the login form
        return render_template('login.html')
    
    # Process login form (POST request)
    
    # Get login credentials from form
    email = request.form['email'].strip()
    password = request.form['password']
    
    # Find user by email only
    user = get_user_by_email(email)
    
    # Check if user exists and password is correct
    if not user or not check_password_hash(user['password'], password):
        flash('Invalid email or password', 'error')
        return redirect(url_for('login'))
    
    # Login successful! Create user session
    session.clear()  # Clear any existing session data
    session['user_id'] = user['id']
    session['username'] = user['username']
    session['role'] = user['role']
    
    flash(f'Welcome back, {user["username"]}!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    """
    Log out the current user by clearing their session.
    """
    # Clear all session data
    session.clear()
    
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """
    User dashboard - shows the user's current bookings.
    Only accessible to logged-in users.
    """
    # Get current user's ID from session
    user_id = session['user_id']
    
    # Get all bookings for this user
    user_bookings = get_user_bookings(user_id)
    
    # Show the dashboard with user's bookings
    return render_template('dashboard.html', bookings=user_bookings)

@app.route('/booking', methods=['GET', 'POST'])
@login_required
def booking():
    """
    Room booking page for regular users.
    GET: Show booking form with available rooms
    POST: Process booking request and redirect to confirmation
    """
    # If user is admin, redirect to admin booking page
    if session.get('role') == 'admin':
        return redirect(url_for('admin_book'))
    
    if request.method == 'GET':
        # Show booking form
        rooms = get_all_rooms()
        current_time = datetime.now()
        return render_template('booking.html', rooms=rooms, now=current_time)
    
    # Process booking form (POST request)
    
    # Get booking details from form
    room_id = request.form['room_id']
    date = request.form['date']
    time_start = request.form['time_start']
    time_end = request.form['time_end']
    
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
    
    # Check if room is available at requested time
    if not check_room_availability(room_id, date, time_start, time_end):
        flash('This room is already booked during the selected time. Please choose a different time.', 'error')
        return redirect(url_for('booking'))
    
    # Room is available! Store booking details in session for confirmation page
    session['booking_data'] = {
        'room_id': room_id,
        'date': date,
        'time_start': time_start,
        'time_end': time_end
    }
    
    # Get room details for confirmation page
    room = get_room_by_id(room_id)
    
    # Show booking confirmation page
    return render_template(
        'booking_confirm.html',
        room=room,
        booking_date=date,
        time_start=time_start,
        time_end=time_end,
        duration=duration
    )

@app.route('/confirm_booking', methods=['POST'])
@login_required
def confirm_booking():
    """
    Process booking confirmation from user.
    User can either confirm the booking (go to payment) or cancel it.
    """
    # Check if booking data exists in session
    if 'booking_data' not in session:
        flash('Booking information not found. Please try again.', 'error')
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
    """
    Process payment and create the final booking.
    In a real application, this would integrate with a payment gateway.
    For this demo, we just simulate successful payment.
    """
    # Check if booking data exists in session
    if 'booking_data' not in session:
        flash('Booking information not found. Please try again.', 'error')
        return redirect(url_for('booking'))
    
    # Get payment details from form
    # In a real app, you would validate and process payment here
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
    """
    Cancel an existing booking.
    Users can only cancel their own bookings, admins can cancel any booking.
    """
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
    """
    User profile page where users can view and edit their account information.
    """
    # Get current user information
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
            return redirect(url_for('profile'))
    
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
        else:
            # Keep existing password
            cursor.execute('''
                UPDATE users 
                SET email = ?, firstname = ?, lastname = ?, dob = ?, address = ?
                WHERE id = ?
            ''', (new_email, firstname, lastname, dob, address, user['id']))
        
        connection.commit()
        flash('Profile updated successfully', 'success')
        
    except Exception as error:
        connection.rollback()
        flash(f'Failed to update profile: {error}', 'error')
    finally:
        connection.close()
    
    return redirect(url_for('profile'))

# ==============================================================================
# ADMIN ROUTES - Special pages only accessible to admin users
# ==============================================================================

@app.route('/admin')
@login_required
@admin_required
def admin():
    """
    Admin dashboard showing all users, rooms, and bookings.
    Only accessible to admin users.
    """
    connection = get_database_connection()
    cursor = connection.cursor()
    
    # Get all users
    cursor.execute("SELECT * FROM users ORDER BY username")
    users = [dict(row) for row in cursor.fetchall()]
    
    # Get all rooms
    cursor.execute("SELECT * FROM rooms ORDER BY name")
    rooms = [dict(row) for row in cursor.fetchall()]
    
    # Get all bookings with user and room information
    cursor.execute('''
        SELECT 
            b.id,
            b.date,
            b.time_start,
            b.time_end,
            b.notes,
            u.username as user_name,
            r.name as room_name,
            admin.username as admin_name
        FROM bookings b
        JOIN users u ON b.user_id = u.id
        JOIN rooms r ON b.room_id = r.id
        LEFT JOIN users admin ON b.booking_admin_id = admin.id
        ORDER BY b.date, b.time_start
    ''')
    
    bookings = []
    for row in cursor.fetchall():
        booking = dict(row)
        # Determine who made the booking
        if booking['admin_name']:
            booking['booked_by'] = f"Admin: {booking['admin_name']}"
        else:
            booking['booked_by'] = "Self"
        bookings.append(booking)
    
    connection.close()
    
    return render_template('admin.html', users=users, rooms=rooms, bookings=bookings)

@app.route('/admin/add_room', methods=['POST'])
@login_required
@admin_required
def add_room():
    """
    Add a new meeting room to the system.
    Only accessible to admin users.
    """
    # Get room details from form
    name = request.form['name'].strip()
    location = request.form['location'].strip()
    capacity = request.form['capacity']
    
    # Validate input
    if not name or not location:
        flash('Room name and location are required', 'error')
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
            INSERT INTO rooms (name, location, capacity)
            VALUES (?, ?, ?)
        ''', (name, location, capacity))
        
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
    """
    Edit user information (admin only).
    Allows admins to change user details and roles.
    """
    # Get updated user information from form
    username = request.form['username'].strip()
    email = request.form['email'].strip()
    role = request.form['role']
    
    # Validate input
    if not username or not email:
        flash('Username and email are required', 'error')
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
            SET username = ?, email = ?, role = ?
            WHERE id = ?
        ''', (username, email, role, user_id))
        
        connection.commit()
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
    """
    Admin booking page - allows admins to make bookings on behalf of users.
    Includes support for recurring bookings.
    """
    if request.method == 'GET':
        # Show admin booking form
        rooms = get_all_rooms()
        
        # Get all regular users (non-admin) for the client dropdown
        connection = get_database_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE role = 'user' ORDER BY username")
        clients = [dict(row) for row in cursor.fetchall()]
        connection.close()
        
        current_time = datetime.now()
        
        return render_template('admin_book.html', rooms=rooms, clients=clients, now=current_time)
    
    # Process admin booking form (POST request)
    
    # Get booking details from form
    room_id = request.form['room_id']
    date = request.form['date']
    time_start = request.form['time_start']
    time_end = request.form['time_end']
    client_id = request.form['client_id']
    booking_notes = request.form.get('booking_notes', '').strip()
    is_recurring = request.form.get('is_recurring') == '1'
    recurrence_type = request.form.get('recurrence_type', 'weekly')
    recurrence_count = request.form.get('recurrence_count', '4')
    
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
    
    # Check if room is available at requested time
    if not check_room_availability(room_id, date, time_start, time_end):
        flash('This room is already booked during the selected time. Please choose a different time.', 'error')
        return redirect(url_for('admin_book'))
    
    # Store booking details in session for confirmation
    session['booking_data'] = {
        'room_id': room_id,
        'date': date,
        'time_start': time_start,
        'time_end': time_end,
        'client_id': client_id,
        'booking_notes': booking_notes,
        'is_admin_booking': True,
        'is_recurring': is_recurring,
        'recurrence_type': recurrence_type,
        'recurrence_count': recurrence_count
    }
    
    # Get room and client details for confirmation page
    room = get_room_by_id(room_id)
    client = get_user_by_id(client_id)
    
    # Show admin booking confirmation page
    return render_template(
        'admin_booking_confirm.html',
        room=room,
        client=client,
        booking_date=date,
        time_start=time_start,
        time_end=time_end,
        duration=duration,
        booking_notes=booking_notes,
        is_recurring=is_recurring,
        recurrence_type=recurrence_type,
        recurrence_count=recurrence_count
    )

@app.route('/admin/confirm_booking', methods=['POST'])
@login_required
@admin_required
def admin_confirm_booking():
    """
    Process admin booking confirmation.
    Creates the booking(s) in the database, including recurring bookings if specified.
    """
    # Get user's choice (confirm or cancel)
    action = request.form.get('action')
    
    if action == 'cancel':
        # Admin cancelled the booking
        session.pop('booking_data', None)
        flash('Booking cancelled', 'info')
        return redirect(url_for('admin_book'))
    
    # Get booking data from session
    if 'booking_data' not in session:
        flash('Booking information not found. Please try again.', 'error')
        return redirect(url_for('admin_book'))
    
    booking_data = session.pop('booking_data')  # Remove from session since we're processing it
    
    # Extract booking details
    room_id = booking_data['room_id']
    date = booking_data['date']
    time_start = booking_data['time_start']
    time_end = booking_data['time_end']
    client_id = booking_data['client_id']
    booking_notes = booking_data.get('booking_notes', '')
    is_recurring = booking_data.get('is_recurring', False)
    recurrence_type = booking_data.get('recurrence_type', 'weekly')
    recurrence_count = int(booking_data.get('recurrence_count', 4))
    
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
        recurrence_count=recurrence_count,
        all_bookings_created=all_bookings_created,
        created_bookings_count=len(created_bookings)
    )

# ==============================================================================
# ERROR HANDLERS - Custom pages for common errors
# ==============================================================================

@app.errorhandler(404)
def page_not_found(error):
    """
    Custom 404 (Page Not Found) error page.
    """
    return render_template('error404.html'), 404

# ==============================================================================
# APPLICATION STARTUP - Initialize database and run the app
# ==============================================================================

if __name__ == '__main__':
    # Initialize the database when the application starts
    print("Initializing MeetMate application...")
    initialize_database()
    
    print("=" * 60)
    print("🎯 MeetMate - Meeting Room Booking System")
    print("=" * 60)
    print("📚 This is the beginner-friendly version using sqlite3")
    print("🔑 Default login credentials (EMAIL ONLY):")
    print("   Admin: admin@meetmate.com / admin123")
    print("   User:  user@meetmate.com / user123")
    print("🌐 Starting web server...")
    print("📱 Open your browser to: http://127.0.0.1:5000")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 60)
    
    # Start the Flask web server
    app.run(debug=True, host='127.0.0.1', port=5000)
