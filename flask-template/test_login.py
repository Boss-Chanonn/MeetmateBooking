"""
Login test script to verify the login functionality works properly
"""

import requests
import time

def test_login_functionality():
    """Test the login flow"""
    base_url = "http://127.0.0.1:5000"
    
    print("🧪 Testing MeetMate Login Functionality")
    print("=" * 50)
    
    # Test 1: Access login page
    try:
        response = requests.get(f"{base_url}/login")
        if response.status_code == 200:
            print("✅ Login page accessible")
        else:
            print(f"❌ Login page error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Failed to access login page: {e}")
        return False
    
    # Test 2: Test login with admin credentials
    try:
        session = requests.Session()
        
        # Get login page to establish session
        login_page = session.get(f"{base_url}/login")
        
        # Submit login form
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        
        response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
        
        if response.status_code == 302:  # Redirect indicates successful login
            redirect_location = response.headers.get('Location', '')
            if 'dashboard' in redirect_location or response.headers.get('Location', '').endswith('/dashboard'):
                print("✅ Login redirect working properly")
                
                # Follow the redirect to dashboard
                dashboard_response = session.get(f"{base_url}/dashboard")
                if dashboard_response.status_code == 200:
                    print("✅ Dashboard accessible after login")
                else:
                    print(f"❌ Dashboard access failed: {dashboard_response.status_code}")
            else:
                print(f"❌ Unexpected redirect location: {redirect_location}")
        else:
            print(f"❌ Login failed with status: {response.status_code}")
            print(f"Response content: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ Login test failed: {e}")
        return False
    
    print("✅ All login functionality tests passed!")
    return True

if __name__ == "__main__":
    print("Make sure your Flask app is running on http://127.0.0.1:5000")
    print("Waiting 3 seconds...")
    time.sleep(3)
    
    success = test_login_functionality()
    if success:
        print("\n🎉 Login functionality is working correctly!")
    else:
        print("\n❌ Login functionality needs attention!")
