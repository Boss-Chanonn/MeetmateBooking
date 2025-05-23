import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import calendar
from functools import wraps

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'meetmate_secret_key_v2_2025'

# Ensure instance directory exists
instance_dir = os.path.join(app.root_path, 'instance')
os.makedirs(instance_dir, exist_ok=True)
db_path = os.path.join(instance_dir, 'meetmate.db') 
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Add custom Jinja filter to support {% now %} 
@app.template_filter('now')
def _jinja2_filter_now(format_string, timezone=None):
    return datetime.now().strftime(format_string)

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    firstname = db.Column(db.String(100), nullable=True)
    lastname = db.Column(db.String(100), nullable=True)
    dob = db.Column(db.String(10), nullable=True)  # Date of birth in YYYY-MM-DD format
    address = db.Column(db.String(200), nullable=True)
    role = db.Column(db.String(20), default='user')
    # User's bookings (as the booking owner)
    bookings = db.relationship('Booking', foreign_keys='Booking.user_id', backref='user', lazy=True)
    # Bookings made by this user as admin on behalf of others
    admin_bookings = db.relationship('Booking', foreign_keys='Booking.booking_admin_id', backref='admin', lazy=True)

class Room(db.Model):
    __tablename__ = 'rooms'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    bookings = db.relationship('Booking', backref='room', lazy=True)

class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    date = db.Column(db.String(10), nullable=False)
    time_start = db.Column(db.String(5), nullable=False)
    time_end = db.Column(db.String(5), nullable=False)
    booking_admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # This will be set if an admin booked on behalf of a user
    notes = db.Column(db.Text, nullable=True)  # Optional notes for the booking

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'error')
            return redirect(url_for('login'))
        
        # Validate that the user still exists in database
        try:
            user = User.query.get(session['user_id'])
            if not user:
                session.clear()
                flash('Your session has expired. Please login again.', 'warning')
                return redirect(url_for('login'))
        except Exception:
            session.clear()
            flash('Session error. Please login again.', 'error')
            return redirect(url_for('login'))
            
        return f(*args, **kwargs)
    return decorated_function

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash('Admin access required', 'error')
            return redirect(url_for('dashboard'))
        
        # Validate that the admin user still exists in database
        try:
            user = User.query.get(session['user_id'])
            if not user or user.role != 'admin':
                session.clear()
                flash('Admin session expired. Please login again.', 'warning')
                return redirect(url_for('login'))
        except Exception:
            session.clear()
            flash('Session error. Please login again.', 'error')
            return redirect(url_for('login'))
            
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        firstname = request.form.get('firstname', '')
        lastname = request.form.get('lastname', '')
        dob = request.form.get('dob', '')
        address = request.form.get('address', '')
        
        # Check if user or email already exists
        user_exists = User.query.filter_by(username=username).first()
        email_exists = User.query.filter_by(email=email).first()
        
        if user_exists:
            flash('Username already exists', 'error')
            return redirect(url_for('register'))
        
        if email_exists:
            flash('Email already registered', 'error')
            return redirect(url_for('register'))
        
        # Create new user
        new_user = User(
            username=username,
            email=email,
            password=generate_password_hash(password),
            firstname=firstname,
            lastname=lastname,
            dob=dob,
            address=address
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if input is email or username
        if '@' in username:
            user = User.query.filter_by(email=username).first()
        else:
            user = User.query.filter_by(username=username).first()
        
        if not user or not check_password_hash(user.password, password):
            flash('Invalid email/username or password', 'error')
            return redirect(url_for('login'))
        
        session['user_id'] = user.id
        session['username'] = user.username
        session['role'] = user.role
        
        flash(f'Welcome back, {user.username}!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session.get('user_id')
    user_bookings = Booking.query.filter_by(user_id=user_id).all()
    
    # Format bookings with room information
    bookings = []
    for booking in user_bookings:
        room = Room.query.get(booking.room_id)
        if room:  # Make sure the room exists
            bookings.append({
                'id': booking.id,
                'room_name': room.name,
                'room_location': room.location,
                'date': booking.date,
                'time_start': booking.time_start,
                'time_end': booking.time_end,
                'notes': booking.notes
            })
    
    return render_template('dashboard.html', bookings=bookings)

@app.route('/booking', methods=['GET', 'POST'])
@login_required
def booking():
    # Check if user is admin - if so, redirect to admin booking
    if session.get('role') == 'admin':
        return redirect(url_for('admin_book'))
        
    rooms = Room.query.all()
    now = datetime.now()
    
    if request.method == 'POST':
        room_id = request.form['room_id']
        date = request.form['date']
        time_start = request.form['time_start']
        time_end = request.form['time_end']
        
        # Check if the room is already booked at this time
        existing_booking = Booking.query.filter_by(
            room_id=room_id,
            date=date
        ).filter(
            (Booking.time_start <= time_end) &
            (Booking.time_end >= time_start)
        ).first()
        
        if existing_booking:
            flash('This room is already booked during the selected time', 'error')
            return redirect(url_for('booking'))
        
        # Get room details for confirmation page
        room = Room.query.get(room_id)
        
        # Calculate booking duration in hours
        start_hour = int(time_start.split(':')[0])
        end_hour = int(time_end.split(':')[0])
        duration = end_hour - start_hour
        
        # Validate booking duration (1-8 hours)
        if duration < 1 or duration > 8:
            flash(f'Booking duration must be between 1 and 8 hours (got {duration} hours)', 'error')
            return redirect(url_for('booking'))
        
        # Store booking details in session for confirmation
        session['booking_data'] = {
            'room_id': room_id,
            'date': date,
            'time_start': time_start,
            'time_end': time_end
        }
        
        return render_template(
            'booking_confirm.html',
            room=room,
            booking_date=date,
            time_start=time_start,
            time_end=time_end,
            duration=duration
        )
    
    return render_template('booking.html', rooms=rooms, now=now)


@app.route('/confirm_booking', methods=['POST'])
@login_required
def confirm_booking():
    # Check if the booking data exists in session
    if 'booking_data' not in session:
        flash('Booking information not found. Please try again.', 'error')
        return redirect(url_for('booking'))
    
    # Get action (confirm or cancel)
    action = request.form.get('action')
    
    if action == 'cancel':
        # Clear booking data from session
        session.pop('booking_data', None)
        flash('Booking cancelled', 'info')
        return redirect(url_for('booking'))
    
    # Get booking data from session
    booking_data = session['booking_data']  # Don't pop it yet, we need it for the payment page
    room_id = booking_data['room_id']
    date = booking_data['date']
    time_start = booking_data['time_start']
    time_end = booking_data['time_end']
    
    # Check again if the room is still available
    existing_booking = Booking.query.filter_by(
        room_id=room_id,
        date=date
    ).filter(
        (Booking.time_start <= time_end) &
        (Booking.time_end >= time_start)
    ).first()
    
    if existing_booking:
        # Clear booking data from session
        session.pop('booking_data', None)
        flash('Sorry, this room was just booked by someone else. Please select another time.', 'error')
        return redirect(url_for('booking'))
    
    # Proceed to payment page
    room = Room.query.get(room_id)
    
    # Calculate booking duration in hours
    start_hour = int(time_start.split(':')[0])
    end_hour = int(time_end.split(':')[0])
    duration = end_hour - start_hour
    
    return render_template(
        'payment.html',
        room=room,
        booking_date=date,
        time_start=time_start,
        time_end=time_end,
        duration=duration
    )

@app.route('/cancel_booking/<int:booking_id>')
@login_required
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    
    # Ensure the booking belongs to this user or user is admin
    if booking.user_id != session['user_id'] and session.get('role') != 'admin':
        flash('You do not have permission to cancel this booking', 'error')
        return redirect(url_for('dashboard'))
    
    db.session.delete(booking)
    db.session.commit()
    
    flash('Booking cancelled successfully', 'success')
    return redirect(url_for('dashboard'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        email = request.form['email']
        
        # Check if email is already in use by another user
        email_exists = User.query.filter(User.email == email, User.id != user.id).first()
        if email_exists:
            flash('Email already in use', 'error')
            return redirect(url_for('profile'))
        
        user.email = email
        user.firstname = request.form.get('firstname', '')
        user.lastname = request.form.get('lastname', '')
        user.dob = request.form.get('dob', '')
        user.address = request.form.get('address', '')
        
        # Update password if provided
        if request.form['password']:
            user.password = generate_password_hash(request.form['password'])
        
        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('profile'))
    
    return render_template('profile.html', user=user)

@app.route('/admin')
@login_required
@admin_required
def admin():
    users = User.query.all()
    rooms = Room.query.all()
    bookings = Booking.query.all()
    
    # Format bookings with user and room information
    formatted_bookings = []
    for booking in bookings:
        user = User.query.get(booking.user_id)
        room = Room.query.get(booking.room_id)
        
        # Get admin info if booking was made by an admin
        booked_by = "Self"
        if booking.booking_admin_id:
            admin = User.query.get(booking.booking_admin_id)
            booked_by = f"Admin: {admin.username}"
        
        formatted_bookings.append({
            'id': booking.id,
            'username': user.username,
            'room_name': room.name,
            'date': booking.date,
            'time_start': booking.time_start,
            'time_end': booking.time_end,
            'booked_by': booked_by,
            'notes': booking.notes
        })
    
    return render_template('admin.html', users=users, rooms=rooms, bookings=formatted_bookings)

@app.route('/admin/add_room', methods=['POST'])
@login_required
@admin_required
def add_room():
    name = request.form['name']
    location = request.form['location']
    capacity = request.form['capacity']
    
    new_room = Room(name=name, location=location, capacity=capacity)
    db.session.add(new_room)
    db.session.commit()
    
    flash('Room added successfully', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/edit_user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    
    user.username = request.form['username']
    user.email = request.form['email']
    user.role = request.form['role']
    
    db.session.commit()
    flash('User updated successfully', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/book', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_book():
    rooms = Room.query.all()
    clients = User.query.filter_by(role='user').all()
    now = datetime.now()
    
    if request.method == 'POST':
        room_id = request.form['room_id']
        date = request.form['date']
        time_start = request.form['time_start']
        time_end = request.form['time_end']
        client_id = request.form['client_id']
        booking_notes = request.form.get('booking_notes', '')
        is_recurring = request.form.get('is_recurring') == '1'
        recurrence_type = request.form.get('recurrence_type', 'weekly')
        recurrence_count = request.form.get('recurrence_count', '4')
        
        # Check if the room is already booked at this time
        existing_booking = Booking.query.filter_by(
            room_id=room_id,
            date=date
        ).filter(
            (Booking.time_start <= time_end) &
            (Booking.time_end >= time_start)
        ).first()
        
        if existing_booking:
            flash('This room is already booked during the selected time', 'error')
            return redirect(url_for('admin_book'))
        
        # Get room and client details for confirmation page
        room = Room.query.get(room_id)
        client = User.query.get(client_id)
        
        # Calculate booking duration in hours
        start_hour = int(time_start.split(':')[0])
        end_hour = int(time_end.split(':')[0])
        duration = end_hour - start_hour
        
        # Validate booking duration (1-8 hours)
        if duration < 1 or duration > 8:
            flash(f'Booking duration must be between 1 and 8 hours (got {duration} hours)', 'error')
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
    
    return render_template('admin_book.html', rooms=rooms, clients=clients, now=now)

@app.route('/process_payment', methods=['POST'])
@login_required
def process_payment():
    # Check if the booking data exists in session
    if 'booking_data' not in session:
        flash('Booking information not found. Please try again.', 'error')
        return redirect(url_for('booking'))
    
    # Get payment details (in a real app you would process the payment here)
    card_holder = request.form['card_holder']
    card_number = request.form['card_number']
    expiry_date = request.form['expiry_date']
    cvv = request.form['cvv']
    
    # For demo purposes, we're just showing a successful payment
    # In a real app, you would integrate with a payment gateway here
    
    # Get booking data from session
    booking_data = session.pop('booking_data')  # Now we can pop it
    room_id = booking_data['room_id']
    date = booking_data['date']
    time_start = booking_data['time_start']
    time_end = booking_data['time_end']
    
    # Check one last time if the room is still available
    existing_booking = Booking.query.filter_by(
        room_id=room_id,
        date=date
    ).filter(
        (Booking.time_start <= time_end) &
        (Booking.time_end >= time_start)
    ).first()
    
    if existing_booking:
        flash('Sorry, this room was just booked by someone else. Please select another time.', 'error')
        return redirect(url_for('booking'))
    
    # Create new booking
    new_booking = Booking(
        user_id=session['user_id'],
        room_id=room_id,
        date=date,
        time_start=time_start,
        time_end=time_end,
        booking_admin_id=None  # Regular user booking, not made by admin
    )
    
    db.session.add(new_booking)
    db.session.commit()
    
    # Generate a confirmation code
    confirmation_code = f"MEET-{new_booking.id}-{datetime.now().strftime('%y%m%d')}"
    
    # Get room details for success page
    room = Room.query.get(room_id)
    
    # Show success page
    return render_template(
        'booking_success.html',
        room=room,
        booking_date=date,
        time_start=time_start,
        time_end=time_end,
        confirmation_code=confirmation_code
    )

@app.route('/admin/confirm_booking', methods=['POST'])
@login_required
@admin_required
def admin_confirm_booking():
    # Get action (confirm or cancel)
    action = request.form.get('action')
    
    if action == 'cancel':
        # Clear booking data from session if it exists
        if 'booking_data' in session:
            session.pop('booking_data', None)
        flash('Booking cancelled', 'info')
        return redirect(url_for('admin_book'))
    
    # Get booking data from session if available, otherwise from form
    if 'booking_data' in session:
        booking_data = session['booking_data']
    else:
        # Get booking data from form
        form_room_id = request.form.get('room_id')
        form_date = request.form.get('date')
        form_time_start = request.form.get('time_start')
        form_time_end = request.form.get('time_end')
        form_client_id = request.form.get('client_id')
        form_booking_notes = request.form.get('booking_notes', '')
        form_is_recurring = request.form.get('is_recurring') == '1'
        form_recurrence_type = request.form.get('recurrence_type', 'weekly')
        form_recurrence_count = request.form.get('recurrence_count', '4')
        
        # Validate that all required fields are present and valid
        if not form_room_id or not form_date or not form_time_start or not form_time_end or not form_client_id:
            flash('Booking information incomplete. Please try again.', 'error')
            return redirect(url_for('admin_book'))
            
        booking_data = {
            'room_id': form_room_id,
            'date': form_date,
            'time_start': form_time_start,
            'time_end': form_time_end,
            'client_id': form_client_id,
            'booking_notes': form_booking_notes,
            'is_admin_booking': True,
            'is_recurring': form_is_recurring,
            'recurrence_type': form_recurrence_type,
            'recurrence_count': form_recurrence_count
        }
    
    room_id = booking_data['room_id']
    date = booking_data['date']
    time_start = booking_data['time_start']
    time_end = booking_data['time_end']
    client_id = booking_data['client_id']
    booking_notes = booking_data.get('booking_notes', '')
    is_recurring = booking_data.get('is_recurring', False)
    recurrence_type = booking_data.get('recurrence_type', 'weekly')
    recurrence_count = int(booking_data.get('recurrence_count', 4))
    
    # Validate booking duration
    try:
        start_hour = int(time_start.split(':')[0])
        end_hour = int(time_end.split(':')[0])
        duration = end_hour - start_hour
        
        if duration < 1 or duration > 8:
            flash(f'Booking duration must be between 1 and 8 hours (got {duration} hours)', 'error')
            return redirect(url_for('admin_book'))
    except (ValueError, IndexError):
        flash('Invalid time format. Please try again.', 'error')
        return redirect(url_for('admin_book'))
    
    # Check again if the room is still available
    existing_booking = Booking.query.filter_by(
        room_id=room_id,
        date=date
    ).filter(
        (Booking.time_start <= time_end) &
        (Booking.time_end >= time_start)
    ).first()
    
    if existing_booking:
        # Clear booking data from session
        if 'booking_data' in session:
            session.pop('booking_data', None)
        flash('Sorry, this room was just booked by someone else. Please select another time.', 'error')
        return redirect(url_for('admin_book'))
    
    try:
        all_bookings_created = True
        created_bookings = []
        booking_date = datetime.strptime(date, '%Y-%m-%d')
        
        # Create the initial booking
        new_booking = Booking(
            user_id=client_id,  # Using the client's ID, not the admin's
            room_id=room_id,
            date=date,
            time_start=time_start,
            time_end=time_end,
            booking_admin_id=session['user_id'],  # Track which admin created this booking
            notes=booking_notes
        )
        
        db.session.add(new_booking)
        db.session.commit()
        created_bookings.append(new_booking)
        
        # For recurring bookings, create additional bookings
        if is_recurring:
            # Calculate date intervals based on recurrence type
            if recurrence_type == 'weekly':
                days_interval = 7
            elif recurrence_type == 'biweekly':
                days_interval = 14
            elif recurrence_type == 'monthly':
                days_interval = 30  # Approximate, will be adjusted below
            
            # Create recurring bookings
            for i in range(1, recurrence_count):
                if recurrence_type == 'monthly':
                    # For monthly, increment the month correctly
                    next_date = booking_date.replace(month=booking_date.month + i if booking_date.month + i <= 12 else (booking_date.month + i) % 12,
                                                  year=booking_date.year + ((booking_date.month + i - 1) // 12))
                    # Adjust for months with fewer days
                    last_day_of_month = calendar.monthrange(next_date.year, next_date.month)[1]
                    if next_date.day > last_day_of_month:
                        next_date = next_date.replace(day=last_day_of_month)
                else:
                    # For weekly/biweekly, just add days
                    next_date = booking_date + timedelta(days=days_interval * i)
                
                formatted_date = next_date.strftime('%Y-%m-%d')
                
                # Check if the room is available for this recurring date
                recurring_existing = Booking.query.filter_by(
                    room_id=room_id,
                    date=formatted_date
                ).filter(
                    (Booking.time_start <= time_end) &
                    (Booking.time_end >= time_start)
                ).first()
                
                if not recurring_existing:
                    # Create the recurring booking
                    recurring_booking = Booking(
                        user_id=client_id,
                        room_id=room_id,
                        date=formatted_date,
                        time_start=time_start,
                        time_end=time_end,
                        booking_admin_id=session['user_id'],
                        notes=f"{booking_notes} (Recurring {i+1}/{recurrence_count})"
                    )
                    
                    db.session.add(recurring_booking)
                    db.session.commit()
                    created_bookings.append(recurring_booking)
                else:
                    all_bookings_created = False
        
        # Clear booking data from session
        if 'booking_data' in session:
            session.pop('booking_data', None)
        
        # Generate a confirmation code
        confirmation_code = f"MEET-{new_booking.id}-{datetime.now().strftime('%y%m%d')}"
        
        # Get room and client details for success page
        room = Room.query.get(room_id)
        client = User.query.get(client_id)
        
        # Instead of redirecting to admin, show a success page
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
            all_bookings_created=all_bookings_created
        )
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred while creating the booking: {str(e)}', 'error')
        return redirect(url_for('admin_book'))

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error404.html'), 404

if __name__ == '__main__':
    # Start the application
    app.run(debug=True)
