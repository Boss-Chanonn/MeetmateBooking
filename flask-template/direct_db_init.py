"""
Direct database initialization
Creates the database directly with SQLite to bypass potential SQLAlchemy constraints
"""
import os
import sqlite3
from werkzeug.security import generate_password_hash

# Define the paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INSTANCE_DIR = os.path.join(SCRIPT_DIR, 'instance')
DB_PATH = os.path.join(INSTANCE_DIR, 'meetmate.db')

def main():
    """Initialize the database directly"""
    # Create instance directory if it doesn't exist
    if not os.path.exists(INSTANCE_DIR):
        print(f"Creating instance directory: {INSTANCE_DIR}")
        os.makedirs(INSTANCE_DIR, exist_ok=True)
        
    # Remove existing database if it exists
    if os.path.exists(DB_PATH):
        print(f"Removing existing database: {DB_PATH}")
        try:
            os.remove(DB_PATH)
        except Exception as e:
            print(f"Error removing database: {e}")
            return False
    
    # Create new database
    print(f"Creating new database: {DB_PATH}")
    try:
        # Connect to the database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Create tables
        print("Creating tables...")
        
        # Users table
        cursor.execute('''
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
        )
        ''')
        
        # Rooms table
        cursor.execute('''
        CREATE TABLE rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            location TEXT NOT NULL,
            capacity INTEGER NOT NULL
        )
        ''')
        
        # Bookings table
        cursor.execute('''
        CREATE TABLE bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            room_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            time_start TEXT NOT NULL,
            time_end TEXT NOT NULL,
            booking_admin_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (room_id) REFERENCES rooms (id),
            FOREIGN KEY (booking_admin_id) REFERENCES users (id)
        )
        ''')
        
        # Insert admin user
        print("Adding admin user...")
        admin_password = generate_password_hash('admin123')
        cursor.execute('''
        INSERT INTO users (username, email, password, firstname, lastname, role)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', ('admin', 'admin@meetmate.com', admin_password, 'Admin', 'User', 'admin'))
        
        # Insert test user
        print("Adding test user...")
        user_password = generate_password_hash('password')
        cursor.execute('''
        INSERT INTO users (username, email, password, firstname, lastname, dob, address, role)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('testuser', 'test@example.com', user_password, 'Test', 'User', '1990-01-01', '123 Test Street', 'user'))
        
        # Insert sample rooms
        print("Adding sample rooms...")
        rooms = [
            ('Conference Room A', '1st Floor', 10),
            ('Meeting Room B', '2nd Floor', 6),
            ('Board Room', '3rd Floor', 20)
        ]
        cursor.executemany('INSERT INTO rooms (name, location, capacity) VALUES (?, ?, ?)', rooms)
        
        # Commit changes and close connection
        conn.commit()
        
        # Verify data
        print("\nVerifying data...")
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"Users: {user_count}")
        
        cursor.execute("SELECT COUNT(*) FROM rooms")
        room_count = cursor.fetchone()[0]
        print(f"Rooms: {room_count}")
        
        conn.close()
        
        print("\nDatabase initialized successfully!")
        print(f"Database path: {os.path.abspath(DB_PATH)}")
        return True
        
    except Exception as e:
        print(f"Error creating database: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
