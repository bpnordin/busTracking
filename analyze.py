import sqlite3
import pandas as pd
from geopy import distance
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
import os

pd.options.mode.copy_on_write = True

database = "busData.db"

"""
.schema
CREATE TABLE vehicles (
        vehicle_id TEXT PRIMARY KEY,
        route_num TEXT,
        route_name TEXT,
        destination TEXT,
        schedule_status INTEGER
    );
CREATE TABLE locations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vehicle_id TEXT,
        latitude REAL,
        longitude REAL,
        timestamp TEXT,
        FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id)
    );
"""

"""
1. pick a bus
2. pick a bus stop
3. compute distance over time
4. graph
"""

"""
stop_lat = None
stop_lon = None
stopList = get.getStops("1")
for stop in stopList:
    if stop["stop_code"] == stop_id:
        stop_lat = stop["stop_lat"]
        stop_lon = stop["stop_lon"]
"""


def graph(df):

    plt.figure(figsize=(30, 10))
    plt.scatter(df["timestamp"], df["distance"], marker="o", linestyle="-", color="r")

    plt.xlabel("Time")
    plt.ylabel("Distance (km)")
    plt.title("Distance vs Time")

    plt.grid(True)
    plt.savefig("temp.png")
    os.system("kitty icat temp.png")
    plt.close()


def cleanDistance(df):
    filtered_df = df[
        (df["latitude"] != df["latitude"].shift(1))
        | (df["longitude"] != df["longitude"].shift(1))
        | (df["distance"] != df["distance"].shift(1))
    ]

    # Handle potential edge cases where the first or last row might not have a previous or next row
    if len(filtered_df) == 0:
        return df  # If no changes found, return the original DataFrame
    if filtered_df.index[0] != 0:
        filtered_df = pd.concat([df.iloc[:1], filtered_df])
    if filtered_df.index[-1] != df.index[-1]:
        filtered_df = pd.concat([filtered_df, df.iloc[-1:]])

    return filtered_df


conn = sqlite3.connect("newBusTracking.db")
cursor = conn.cursor()
vehicleSQL = "select vehicle_id from vehicles"
cursor.execute(vehicleSQL)
vehicle_id_list = cursor.fetchall()

for vehicle_id in vehicle_id_list:
    print(vehicle_id)
    stop_id = "102122"
    stop_coords = ("40.769267", "-111.882791")
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.execute(
        "select latitude, longitude, timestamp from locations where vehicle_id is ?",
        vehicle_id,
    )
    locationList = cursor.fetchall()

    df = pd.DataFrame(locationList, columns=["latitude", "longitude", "timestamp"])
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["distance"] = df.apply(
        lambda row: distance.geodesic(
            stop_coords, (row["latitude"], row["longitude"])
        ).miles,
        axis=1,
    )

    conn.close()

    df = df.sort_values(by="timestamp").reset_index(drop=True)
    start_time = "2024-09-24 06:00:00"
    end_time = "2024-09-24 07:30:00"

    """
    df_filtered = df.loc[df['distance'] < .3]
    df_filtered = df_filtered.loc[df['timestamp'] < end_time]
    df_filtered = df_filtered.loc[df['timestamp'] > start_time]
    df_filtered = cleanDistance(df_filtered)
    """
    #    graph(df_filtered)
    print(df["timestamp"].min())
    graph(df)
