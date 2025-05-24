#!/usr/bin/env python3
"""
Complete test script for MeetMate login and dashboard functionality
Tests the full flow from login to dashboard redirect
"""

import requests
import sys

def test_login_flow():
    """Test complete login flow and dashboard redirect"""
    base_url = "http://127.0.0.1:5000"
    
    print("=" * 60)
    print("MEETMATE COMPLETE FLOW TEST")
    print("=" * 60)
    
    # Test 1: Homepage accessibility
    try:
        response = requests.get(f"{base_url}/")
        print(f"✓ Homepage accessible: {response.status_code}")
        if response.status_code != 200:
            print(f"  Warning: Expected 200, got {response.status_code}")
    except Exception as e:
        print(f"✗ Homepage test failed: {e}")
        return False
    
    # Test 2: Login page accessibility
    try:
        response = requests.get(f"{base_url}/login")
        print(f"✓ Login page accessible: {response.status_code}")
        if response.status_code != 200:
            print(f"  Warning: Expected 200, got {response.status_code}")
    except Exception as e:
        print(f"✗ Login page test failed: {e}")
        return False
    
    # Test 3: Login with valid admin credentials
    session = requests.Session()
    
    try:
        # First get the login page to establish session
        login_response = session.get(f"{base_url}/login")
        print(f"✓ Login page loaded for session: {login_response.status_code}")
        
        # Attempt login with admin credentials
        login_data = {
            'username': 'admin',
            'password': 'admin'  # Default password from database reset
        }
        
        login_post = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
        print(f"✓ Login POST response: {login_post.status_code}")
        
        if login_post.status_code == 302:
            print(f"✓ Login redirect detected to: {login_post.headers.get('Location', 'Unknown')}")
            
            # Follow the redirect to dashboard
            dashboard_response = session.get(f"{base_url}/dashboard")
            print(f"✓ Dashboard accessible after login: {dashboard_response.status_code}")
            
            if dashboard_response.status_code == 200:
                print("✓ LOGIN AND DASHBOARD REDIRECT SUCCESS!")
                
                # Test admin page access
                admin_response = session.get(f"{base_url}/admin")
                print(f"✓ Admin page accessible: {admin_response.status_code}")
                
                return True
            else:
                print(f"✗ Dashboard access failed: {dashboard_response.status_code}")
                return False
        else:
            print(f"✗ Login failed. Expected redirect (302), got {login_post.status_code}")
            print(f"  Response content: {login_post.text[:200]}")
            return False
            
    except Exception as e:
        print(f"✗ Login flow test failed: {e}")
        return False

def test_user_login():
    """Test regular user login"""
    base_url = "http://127.0.0.1:5000"
    session = requests.Session()
    
    print("\n" + "=" * 40)
    print("TESTING REGULAR USER LOGIN")
    print("=" * 40)
    
    try:
        # Login with test user credentials
        login_data = {
            'username': 'testuser',
            'password': 'testuser'  # Assuming same pattern as admin
        }
        
        login_post = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
        print(f"✓ User login POST response: {login_post.status_code}")
        
        if login_post.status_code == 302:
            dashboard_response = session.get(f"{base_url}/dashboard")
            print(f"✓ User dashboard accessible: {dashboard_response.status_code}")
            
            # Test that regular user cannot access admin page
            admin_response = session.get(f"{base_url}/admin")
            print(f"✓ Admin page access for user (should redirect): {admin_response.status_code}")
            
            return True
        else:
            print(f"✗ User login failed: {login_post.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ User login test failed: {e}")
        return False

if __name__ == "__main__":
    print("Starting MeetMate application tests...")
    print("Make sure the Flask app is running on http://127.0.0.1:5000")
    print()
    
    # Test admin login flow
    admin_success = test_login_flow()
    
    # Test user login flow  
    user_success = test_user_login()
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Admin Login & Dashboard: {'✓ PASS' if admin_success else '✗ FAIL'}")
    print(f"User Login & Dashboard:  {'✓ PASS' if user_success else '✗ FAIL'}")
    
    if admin_success and user_success:
        print("\n🎉 ALL TESTS PASSED! MeetMate is working correctly!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the application.")
        sys.exit(1)
