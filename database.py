import sqlite3
from geopy import distance
import pandas as pd
from datetime import datetime
import numpy as np


class BusData:

    def __init__(self, dbFileName):
        self.dbFileName = dbFileName
        self.connection = sqlite3.connect(self.dbFileName)
        self.cursor = self.connection.cursor()

    def __del__(self):
        self.connection.close()

    def tableCreation(self):
        """
        create the tables that are used for bus data if they don't exist
        """

        self.cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS vehicles (
            vehicle_id TEXT PRIMARY KEY,
            route_num TEXT,
            route_name TEXT,
            schedule_status INTEGER
        )
        """
        )

        self.cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id TEXT,
            latitude REAL,
            longitude REAL,
            timestamp TEXT,
            destination TEXT,
            FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id)
        )
        """
        )
        self.connection.commit()

    def inputData(self, data):
        """
        input the data that we get from the UTA website into the database
        """

        def vehicle_exists(vehicle_id, route_num):
            """
            helper function to check if the vehicle has already been added to the vehicle table
            """
            self.cursor.execute(
                "SELECT 1 FROM vehicles WHERE vehicle_id = ? AND route_num = ?",
                (vehicle_id, route_num),
            )
            return self.cursor.fetchone() is not None

        for vehicle in data:
            if not vehicle_exists(vehicle["vehicleId"], vehicle["routeNum"]):
                self.cursor.execute(
                    """
                    INSERT INTO vehicles (vehicle_id, route_num, route_name, schedule_status)
                    VALUES (?, ?, ?, ?)
                """,
                    (
                        vehicle["vehicleId"],
                        vehicle["routeNum"],
                        vehicle["routeName"],
                        vehicle["scheduleStatus"],
                    ),
                )

            self.cursor.execute(
                """
                INSERT INTO locations (vehicle_id, latitude, longitude, timestamp, destination)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    vehicle["vehicleId"],
                    vehicle["location"]["latitude"],
                    vehicle["location"]["longitude"],
                    datetime.now().isoformat(),
                    vehicle["destination"],
                ),
            )

        self.connection.commit()

    def getVehiclesFromRoute(self, routeNum):
        """
        get a list of all the vehicles based upon the route number
        """

        sqlString = f"select * from vehicles where route_num is {routeNum}"
        self.cursor.execute(sqlString)
        vehicleList = self.cursor.fetchall()
        df = pd.DataFrame(
            vehicleList,
            columns=["vehicle_id", "route_num", "route_name", "schedule_status"],
        )

        return df

    def getVehicleLocationData(self, vehicle_id):
        """
        Get all the data given a vehicle_id from the database and return a pandas dataframe
        """

        self.cursor.execute(
            "select latitude, longitude, timestamp,destination from locations where vehicle_id is ?",
            (vehicle_id,),
        )

        locationList = self.cursor.fetchall()
        df = pd.DataFrame(locationList, columns=["latitude", "longitude", "timestamp","destination"])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df


    def getRouteLocationData(self,routeNum):
        self.cursor.execute(
            "SELECT latitude, longitude, timestamp,destination,vehicles.vehicle_id FROM locations INNER JOIN vehicles ON locations.vehicle_id = vehicles.vehicle_id WHERE vehicles.route_num = ?",
            (routeNum,),
        )

        locationList = self.cursor.fetchall()
        df = pd.DataFrame(locationList, columns=["latitude", "longitude", "timestamp","destination","vehicle_id"])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df

    def calculateDistance(self,df,stop_coords=("40.769267", "-111.882791")):
        """
        calculate distaance between two lat, long just like it is a point in 2d space
        return RMS
        """
        def calc(row):
            x,y = stop_coords
            x = float(x)
            y = float(y)
            a = abs(x-row['latitude'])**2
            b = abs(y-row['longitude'])**2
            return a+b
        df_copy = df.copy()
        df_copy["distance"] = df_copy.apply(
            calc,
            axis=1,
        )
        return df_copy

    def calculateGeoDistance(self, df, stop_coords=("40.769267", "-111.882791")):
        """
        using the location data in a pandas data frame df, calc the distance using geopy to a point
        add that as a column and return the modified database
        """
        df_copy = df.copy()
        df_copy["distance"] = df_copy.apply(
            lambda row: distance.geodesic(
                stop_coords, (row["latitude"], row["longitude"])
            ).miles,
            axis=1,
        )
        return df_copy

    def getChangePoints(self,df, distance_threshold=0.5):
        """
        filter to just the points around when the distance is small
        """
        mask_distance = df["distance"] < distance_threshold
        changePoints = np.where((mask_distance - mask_distance.shift()).infer_objects().fillna(0) != 0)[0]
        print(changePoints)
        print(len(changePoints))
        print(mask_distance[0])
        if mask_distance[0] == True:
            #subtracting to find out where it goes True-False does not take into account that it can start true -> false
            changePoints = np.insert(changePoints,0,0)
        return changePoints

    def filterDataForDistance(self,df,distance_threshold=0.5):
        """
        filter to just the points around when the distance is small
        and return a list of seperate dataframes for each group of points
        """
        changePoints = self.getChangePoints(df,distance_threshold=distance_threshold)
        listOfDF = []
        for i in range(0, len(changePoints), 2):
            start_index = changePoints[i]
            end_index = changePoints[i + 1]
            listOfDF.append(df.iloc[start_index:end_index-1])

        return listOfDF

