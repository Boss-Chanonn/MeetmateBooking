#!/usr/bin/env python3
"""
Simple login test for MeetMate
"""

def test_database_users():
    """Test that we can query users from the database"""
    import sys
    import os
    sys.path.append(os.getcwd())
    
    try:
        from app import app, User, db
        
        with app.app_context():
            # Check if we can query users
            users = User.query.all()
            print(f"Found {len(users)} users in database:")
            
            for user in users:
                print(f"  - {user.username} ({user.email}) - Role: {user.role} - Admin: {user.is_admin}")
                
            # Check if we can find admin user
            admin = User.query.filter_by(username='admin').first()
            if admin:
                print(f"\n✓ Admin user found: {admin.username}")
                print(f"  Email: {admin.email}")
                print(f"  Role: {admin.role}")
                print(f"  Is Admin: {admin.is_admin}")
                return True
            else:
                print("\n✗ Admin user not found")
                return False
                
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False

def test_password_verification():
    """Test password verification"""
    import sys
    import os
    sys.path.append(os.getcwd())
    
    try:
        from app import app, User, db
        from werkzeug.security import check_password_hash
        
        with app.app_context():
            admin = User.query.filter_by(username='admin').first()
            if admin:
                # Test different possible passwords
                possible_passwords = ['admin', 'password', 'meetmate', 'admin123', '123456']
                
                print("\nTesting password verification:")
                for pwd in possible_passwords:
                    if check_password_hash(admin.password, pwd):
                        print(f"✓ Correct password found: '{pwd}'")
                        return pwd
                    else:
                        print(f"✗ '{pwd}' is not the correct password")
                
                print("\n❌ Could not find correct password")
                print(f"Stored hash: {admin.password[:50]}...")
                return None
            else:
                print("Admin user not found")
                return None
                
    except Exception as e:
        print(f"Password test failed: {e}")
        return None

if __name__ == "__main__":
    print("=" * 50)
    print("MEETMATE DATABASE & PASSWORD TEST")
    print("=" * 50)
    
    # Test database connectivity and users
    db_success = test_database_users()
    
    if db_success:
        # Test password verification
        admin_password = test_password_verification()
        
        if admin_password:
            print(f"\n🎉 SUCCESS!")
            print(f"You can login with:")
            print(f"  Username: admin")
            print(f"  Password: {admin_password}")
        else:
            print(f"\n❌ Password verification failed")
            print("You may need to reset the admin password")
    else:
        print(f"\n❌ Database test failed")
