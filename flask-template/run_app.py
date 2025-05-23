#!/usr/bin/env python3
"""
Robust startup script for MeetMate Flask application
This script handles common startup issues and provides better error reporting
"""

import os
import sys
import traceback
from pathlib import Path

def check_requirements():
    """Check if all required packages are installed"""
    required_packages = [
        'flask',
        'flask_sqlalchemy', 
        'werkzeug'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("💡 Install them with: pip install flask flask-sqlalchemy werkzeug")
        return False
    
    print("✅ All required packages are installed")
    return True

def check_database():
    """Check if database exists and is accessible"""
    db_path = Path(__file__).parent / 'instance' / 'meetmate.db'
    
    if not db_path.exists():
        print(f"❌ Database not found at: {db_path}")
        print("💡 Run: .\\reset_db.ps1 to create the database")
        return False
    
    print(f"✅ Database found at: {db_path}")
    return True

def start_app():
    """Start the Flask application with error handling"""
    try:
        print("🚀 Starting MeetMate application...")
        
        # Import the Flask app
        from app import app, db
        
        # Test database connection
        with app.app_context():
            try:
                # Use text() for modern SQLAlchemy compatibility
                from sqlalchemy import text
                result = db.session.execute(text('SELECT 1')).fetchone()
                print("✅ Database connection successful")
            except Exception as e:
                print(f"❌ Database connection failed: {e}")
                return False
        
        print("✅ Application initialized successfully")
        print("🌐 Starting web server...")
        print("📱 Open your browser to: http://127.0.0.1:5000")
        print("🛑 Press Ctrl+C to stop the server")
        print("-" * 50)
        
        # Start the Flask app
        app.run(host='127.0.0.1', port=5000, debug=True)
        
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
        return True
    except Exception as e:
        print(f"❌ Application error: {e}")
        print("\n📋 Full error details:")
        traceback.print_exc()
        return False

def main():
    """Main startup function"""
    print("=" * 50)
    print("🎯 MeetMate Flask Application Startup")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check database
    if not check_database():
        sys.exit(1)
    
    # Start the application
    if not start_app():
        sys.exit(1)

if __name__ == '__main__':
    main()
