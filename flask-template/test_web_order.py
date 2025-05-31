#!/usr/bin/env python3
"""
Test script to verify the complete booking flow with new room type ordering
"""

import requests
from bs4 import BeautifulSoup

def test_booking_page_order():
    """Test that the booking page shows room types in the correct order"""
    print("Testing booking page room type order...")
    
    base_url = "http://127.0.0.1:5000"
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    try:
        # First, get the login page to see if server is running
        login_response = session.get(f"{base_url}/login")
        if login_response.status_code != 200:
            print(f"❌ ERROR: Cannot connect to server (status: {login_response.status_code})")
            return False
        
        # Login with user credentials
        login_data = {
            'email': 'user@meetmate.com',
            'password': 'user123'
        }
        
        login_response = session.post(f"{base_url}/login", data=login_data)
        if login_response.status_code != 200:
            print(f"❌ ERROR: Login failed (status: {login_response.status_code})")
            return False
        
        # Navigate to booking page
        booking_response = session.get(f"{base_url}/booking")
        if booking_response.status_code != 200:
            print(f"❌ ERROR: Cannot access booking page (status: {booking_response.status_code})")
            return False
        
        # Parse the HTML to extract room type order
        soup = BeautifulSoup(booking_response.text, 'html.parser')
        
        # Find all room type radio buttons
        room_type_inputs = soup.find_all('input', {'name': 'room_type', 'type': 'radio'})
        
        if not room_type_inputs:
            print("❌ ERROR: No room type inputs found on booking page")
            return False
        
        # Extract room types in the order they appear
        room_types_on_page = []
        for input_elem in room_type_inputs:
            room_type = input_elem.get('value')
            if room_type:
                room_types_on_page.append(room_type)
        
        print(f"Room types found on page: {room_types_on_page}")
        
        # Expected order: Square Table, Circle Table, Long Table
        expected_order = ['Square Table', 'Circle Table', 'Long Table']
        
        if room_types_on_page == expected_order:
            print("✅ SUCCESS: Room types on booking page are in the correct order!")
            print(f"   Order: {' → '.join(room_types_on_page)}")
            return True
        else:
            print("❌ FAILURE: Room types on booking page are not in the expected order!")
            print(f"   Expected: {' → '.join(expected_order)}")
            print(f"   Actual:   {' → '.join(room_types_on_page)}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to Flask server. Make sure it's running on http://127.0.0.1:5000")
        return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    test_booking_page_order()
