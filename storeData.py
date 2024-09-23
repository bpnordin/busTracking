import requests
import sqlite3
from datetime import datetime
import get

# API URL
url = 'https://webapi.rideuta.com/api/vehiclelocation/1'

# Database connection
conn = sqlite3.connect('busData.db')
cursor = conn.cursor()

# Create tables if they do not exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS vehicles (
    vehicle_id TEXT PRIMARY KEY,
    route_num TEXT,
    route_name TEXT,
    destination TEXT,
    schedule_status INTEGER,
    bearing REAL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id TEXT,
    latitude REAL,
    longitude REAL,
    timestamp TEXT,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id)
)
''')

# Fetch the data from the API
data = get.getVehicle("1")

# Function to check if a vehicle exists
def vehicle_exists(vehicle_id):
    cursor.execute('SELECT 1 FROM vehicles WHERE vehicle_id = ?', (vehicle_id,))
    return cursor.fetchone() is not None

# Insert or update vehicle and location data
for vehicle in data:
    # Check if the vehicle already exists in the vehicles table
    if not vehicle_exists(vehicle['vehicleId']):
        # Insert vehicle data into the vehicles table (only if it doesn't exist)
        cursor.execute('''
            INSERT INTO vehicles (vehicle_id, route_num, route_name, destination, schedule_status, bearing)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (vehicle['vehicleId'], vehicle['routeNum'], vehicle['routeName'], vehicle['destination'], vehicle['scheduleStatus'], vehicle['bearing']))
    
    # Insert location data into the locations table with the current timestamp
    cursor.execute('''
        INSERT INTO locations (vehicle_id, latitude, longitude, timestamp)
        VALUES (?, ?, ?, ?)
    ''', (vehicle['vehicleId'], vehicle['location']['latitude'], vehicle['location']['longitude'], datetime.now().isoformat()))

# Commit and close connection
conn.commit()
conn.close()

print("Vehicle and location data have been processed successfully.")

