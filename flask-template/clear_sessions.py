"""
Session clear utility for MeetMate Flask application
Use this script to clear all browser sessions and cache issues
"""

import os
import shutil
from pathlib import Path

def clear_flask_sessions():
    """Clear Flask session data by changing the secret key"""
    print("🧹 Clearing Flask sessions...")
    
    app_file = Path(__file__).parent / 'app.py'
    
    if app_file.exists():
        # Read the current app.py
        content = app_file.read_text()
        
        # Find and update the secret key
        import time
        new_key = f"meetmate_secret_key_{int(time.time())}"
        
        if "app.config['SECRET_KEY']" in content:
            # Replace the secret key
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if "app.config['SECRET_KEY']" in line:
                    lines[i] = f"app.config['SECRET_KEY'] = '{new_key}'"
                    break
            
            # Write back to file
            app_file.write_text('\n'.join(lines))
            print(f"✅ Updated SECRET_KEY to: {new_key}")
        else:
            print("❌ Could not find SECRET_KEY in app.py")
    else:
        print("❌ app.py not found")

def clear_pycache():
    """Clear Python cache files"""
    print("🧹 Clearing Python cache...")
    
    pycache_dir = Path(__file__).parent / '__pycache__'
    if pycache_dir.exists():
        shutil.rmtree(pycache_dir)
        print("✅ Cleared __pycache__ directory")
    else:
        print("ℹ️ No __pycache__ directory found")

def main():
    """Main function to clear all session-related issues"""
    print("=" * 50)
    print("🎯 MeetMate Session Clear Utility")
    print("=" * 50)
    
    clear_flask_sessions()
    clear_pycache()
    
    print("\n📋 Manual steps to complete:")
    print("1. Close your browser completely")
    print("2. Clear browser cache and cookies for localhost:5000")
    print("3. Or use Incognito/Private browsing mode")
    print("4. Restart your Flask application")
    
    print("\n✅ Session clearing complete!")
    print("🚀 You can now run: python app.py")

if __name__ == '__main__':
    main()
