import sqlite3
import os

# Connect to database
db_path = os.path.join('instance', 'meetmate.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=== CURRENT DATABASE STATUS ===")

# Check current room types
cursor.execute('SELECT DISTINCT room_type FROM rooms ORDER BY room_type')
room_types = [row[0] for row in cursor.fetchall()]
print(f"Current room types: {room_types}")

# Check all rooms
cursor.execute('SELECT name, room_type, capacity, location FROM rooms ORDER BY room_type, name')
print("\nAll rooms:")
for row in cursor.fetchall():
    print(f"  {row[1]}: {row[0]} (Capacity: {row[2]}, Location: {row[3]})")

# Count rooms by type
cursor.execute('SELECT room_type, COUNT(*) FROM rooms GROUP BY room_type ORDER BY room_type')
print("\nRoom count by type:")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]} rooms")

conn.close()
