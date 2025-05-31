#!/usr/bin/env python3
"""
Test script to verify room type ordering
"""

import os
import sys
import sqlite3

# Add the current directory to Python path so we can import from app.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import get_all_room_types

def test_room_type_order():
    """Test that room types are returned in the correct order"""
    print("Testing room type ordering...")
    
    # Get room types from our modified function
    room_types = get_all_room_types()
    
    print(f"Current room type order: {room_types}")
    
    # Expected order: Square Table, Circle Table, Long Table
    expected_order = ['Square Table', 'Circle Table', 'Long Table']
    
    if room_types == expected_order:
        print("✅ SUCCESS: Room types are in the correct order!")
        print(f"   Order: {' → '.join(room_types)}")
        return True
    else:
        print("❌ FAILURE: Room types are not in the expected order!")
        print(f"   Expected: {' → '.join(expected_order)}")
        print(f"   Actual:   {' → '.join(room_types)}")
        return False

if __name__ == "__main__":
    test_room_type_order()
