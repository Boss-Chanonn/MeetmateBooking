"""
Utility script to check and update the database schema
This is intended to be run directly to check if the database schema
needs to be updated without running the full application
"""
import os
import sqlite3
from app import app, db, User, Room, Booking

def check_and_update_schema():
    """Check if the database schema is up to date and update if needed"""
    with app.app_context():
        print("Checking database schema...")
        
        # Ensure instance directory exists
        instance_path = os.path.join(app.root_path, 'instance')
        os.makedirs(instance_path, exist_ok=True)
        
        # Check database path
        db_path = os.path.join(instance_path, 'meetmate.db')
        print(f"Database path: {db_path}")
        
        if os.path.exists(db_path):
            print("Database file exists, checking schema...")
            
            try:
                # Connect to the database and check tables
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                  # Check if booking_admin_id column exists
                cursor.execute("PRAGMA table_info(bookings)")
                columns = cursor.fetchall()
                column_names = [col[1] for col in columns]
                
                if 'booking_admin_id' not in column_names:
                    print("Schema update needed: Adding booking_admin_id column")
                    
                    # Add the column
                    try:
                        cursor.execute("ALTER TABLE bookings ADD COLUMN booking_admin_id INTEGER REFERENCES users(id)")
                        conn.commit()
                        print("Added booking_admin_id column successfully")
                    except Exception as e:
                        print(f"Error adding column: {e}")
                        print("Will try full schema migration")
                        conn.close()
                        return False
                
                # Check if notes column exists in bookings table
                if 'notes' not in column_names:
                    print("Schema update needed: Adding notes column")
                    
                    # Add the column
                    try:
                        cursor.execute("ALTER TABLE bookings ADD COLUMN notes TEXT")
                        conn.commit()
                        print("Added notes column successfully")
                    except Exception as e:
                        print(f"Error adding notes column: {e}")
                        print("Will try full schema migration")
                        conn.close()
                        return False
                    
                # Check other tables
                cursor.execute("PRAGMA table_info(users)")
                user_columns = [col[1] for col in cursor.fetchall()]
                
                required_user_columns = ['firstname', 'lastname', 'dob', 'address', 'role']
                for col in required_user_columns:
                    if col not in user_columns:
                        print(f"Missing user column: {col}")
                        print("Schema update needed")
                        conn.close()
                        return False
                
                # Schema is good
                conn.close()
                print("Schema is up to date!")
                return True
                
            except Exception as e:
                print(f"Error checking schema: {e}")
                return False
        else:
            # Database doesn't exist, create it from scratch
            print("Database file doesn't exist, creating fresh database...")
            try:
                db.create_all()
                print("Created database schema")
                return True
            except Exception as e:
                print(f"Error creating database: {e}")
                return False

if __name__ == "__main__":
    if check_and_update_schema():
        print("Schema check complete - database is ready to use!")
        exit(0)
    else:
        print("Schema issues detected - please run reset_db.ps1 to fix")
        exit(1)
