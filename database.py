import sqlite3
from geopy import distance
import pandas as pd
from datetime import datetime
import numpy as np
import math


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
        df = pd.DataFrame(
            locationList, columns=["latitude", "longitude", "timestamp", "destination"]
        )
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df.sort_values("timestamp", inplace=True)
        return df

    def getRouteLocationData(self, routeNum):
        self.cursor.execute(
            "SELECT latitude, longitude, timestamp,destination,vehicles.vehicle_id FROM locations INNER JOIN vehicles ON locations.vehicle_id = vehicles.vehicle_id WHERE vehicles.route_num = ?",
            (routeNum,),
        )

        locationList = self.cursor.fetchall()
        df = pd.DataFrame(
            locationList,
            columns=["latitude", "longitude", "timestamp", "destination", "vehicle_id"],
        )
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df.sort_values("timestamp", inplace=True)
        return df

    def calculateDistance(self, df, stop_coords=("40.769267", "-111.882791")):
        """
        calculate distaance between two lat, long just like it is a point in 2d space
        return RMS
        """

        def calc(row):
            x, y = stop_coords
            x = float(x)
            y = float(y)
            p1 = [x, y]
            p2 = [row["latitude"], row["longitude"]]
            return math.dist(p1, p2)

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

    def getInsidePoints(self, df, distance_threshold=0.005):
        """
        filter to just the points around when the distance is small
        """

        def get_inside_points(series):
            b1 = series < distance_threshold
            b2 = series.shift() < distance_threshold
            if b1.iloc[0]:
                b2.iloc[0] = True
            else:
                b2.iloc[0] = False

            border = b1 ^ b2
            df_border = border.reset_index(drop=False)
            df_border.columns = ["index", "inside"]
            start = series.iloc[0] < distance_threshold
            end = series.loc[series.index[-1]] < distance_threshold
            if start:
                # make the start a change point
                border.iloc[0] = True
            if end:
                # make the end a change point
                border.loc[border.index[-1]] = True

            # time to turn the series into a flat dataframe
            df_fromSeries = series.reset_index(drop=False)
            df_fromSeries.columns = ["index", "distance"]
            changePoints = df_fromSeries[border.reset_index(drop=True)]

            assert len(changePoints) % 2 == 0
            for i in range(0, len(changePoints), 2):
                # i is where it is inside
                # i+1 is where it is just outside
                # any index between those two things should be inside no include i+1
                start = changePoints.iloc[i].name
                stop = changePoints.iloc[i + 1].name
                df_border.loc[start : stop - 1, "inside"] = True
                df_border.loc[stop, "inside"] = False

            df_border = df_border.set_index("index")
            return df_border["inside"]

        df["inside"] = df.groupby(["vehicle_id", "destination"])["distance"].transform(
            get_inside_points
        )
        return df

    def getTrip(self, df):
        def getTrip(series):
            dataframe = series.reset_index()
            dataframe.columns = ["index", "timestamp"]

            # should be no 0 values after we are done with this
            dataframe["tripID"] = "0"
            time_diff = dataframe["timestamp"].diff().dt.total_seconds() / 300
            time_diff = time_diff.fillna(0)
            mask = time_diff > 1

            changePoints = dataframe[mask]
            if len(changePoints) == 0:
                dataframe = dataframe.set_index("index")
                dataframe["tripID"] = "1"
                return dataframe["tripID"]

            startIndex = 0
            tripID = 1
            for endIndex, _ in changePoints.iterrows():
                dataframe.loc[startIndex:endIndex, "tripID"] = str(tripID)
                tripID += 1
                startIndex = endIndex

            # have to go to the end
            dataframe.loc[startIndex:, "tripID"] = str(tripID)

            dataframe = dataframe.set_index("index")
            assert len(dataframe[dataframe["tripID"] == "0"]) == 0
            return dataframe["tripID"]

        """
        df['time_diff'] = df['timestamp'].diff().dt.total_seconds() / 60
        gap_indices = df[df['time_diff'] > 1].index
        split_dfs = []
        start_idx = 0
        for end_idx in gap_indices:
            #iloc is not inclusive, and end_idx is the place where the timestsamp is > 60
            split_dfs.append(df.iloc[start_idx:end_idx].copy())
            start_idx = end_idx 

        split_dfs.append(df.iloc[start_idx:].copy())
        """

        df["tripID"] = df.groupby(["vehicle_id", "destination"])["timestamp"].transform(
            getTrip
        )
        return df
