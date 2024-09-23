import sqlite3
from datetime import datetime
import get
import time


def tableCreation(conn):
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS vehicles (
        vehicle_id TEXT PRIMARY KEY,
        route_num TEXT,
        route_name TEXT,
        destination TEXT,
        schedule_status INTEGER
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
    conn.commit()

def inputData(conn,data):

    cursor = conn.cursor()

    def vehicle_exists(vehicle_id):
        cursor.execute('SELECT 1 FROM vehicles WHERE vehicle_id = ?', (vehicle_id,))
        return cursor.fetchone() is not None

    for vehicle in data:
        if not vehicle_exists(vehicle['vehicleId']):
            cursor.execute('''
                INSERT INTO vehicles (vehicle_id, route_num, route_name, destination, schedule_status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (vehicle['vehicleId'], vehicle['routeNum'], vehicle['routeName'], vehicle['destination'], vehicle['scheduleStatus'], ))
        
        cursor.execute('''
            INSERT INTO locations (vehicle_id, latitude, longitude, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (vehicle['vehicleId'], vehicle['location']['latitude'], vehicle['location']['longitude'], datetime.now().isoformat()))

    conn.commit()

if __name__ == '__main__':
    conn = sqlite3.connect('busData.db')
    tableCreation(conn)
    try:
        while True:
            data = get.getVehicle("1")
            inputData(conn,data)
            time.sleep(6)
    except KeyboardInterrupt:
            print("\nProgram interrupted! Exiting...")
    finally:
        conn.close()
        print("Database connection closed.")
