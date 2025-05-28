#!/usr/bin/env python3
"""
MeetMate application runner
"""

import os
import sys

def main():
    """Start the MeetMate application"""
    print("Starting MeetMate...")
    
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    try:
        import app_beginner
    except ImportError as e:
        print(f"Error: {e}")
        print("Make sure Flask is installed: pip install flask werkzeug")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nStopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
