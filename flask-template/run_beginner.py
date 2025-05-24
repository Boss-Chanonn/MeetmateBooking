#!/usr/bin/env python3
"""
Simple startup script for the beginner-friendly MeetMate application
This script starts the refactored version that uses sqlite3 instead of SQLAlchemy
"""

import os
import sys

def main():
    """Start the beginner-friendly MeetMate application"""
    print("=" * 60)
    print("🎯 MeetMate - Beginner-Friendly Version")
    print("=" * 60)
    print("📚 This version uses Python's built-in sqlite3 module")
    print("🔍 Database operations are clearly visible in the code")
    print("💡 Perfect for learning Flask and database concepts!")
    print("=" * 60)
    
    # Change to the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    try:
        # Import and run the beginner-friendly app
        print("Starting the application...")
        import app_beginner
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you have Flask installed: pip install flask werkzeug")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
