import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit, minimize
import sqlite3
from geopy import distance
from sklearn.preprocessing import normalize
import os


"""
I can easily get when the bus is around 0 distance from the stop

I believe the points around that 0 should be a parabola U 🙆
"""


def get_data(vehicle_id, conn):
    database = "busData.db"
    conn = sqlite3.connect(database)
    cursor = conn.cursor()

    cursor.execute(
        "select latitude, longitude, timestamp from locations where vehicle_id is ?",
        (vehicle_id,),
    )

    locationList = cursor.fetchall()
    df = pd.DataFrame(locationList, columns=["latitude", "longitude", "timestamp"])
    stop_coords = ("40.769267", "-111.882791")  # my stop near me, just for testing
    df["distance"] = df.apply(
        lambda row: distance.geodesic(
            stop_coords, (row["latitude"], row["longitude"])
        ).miles,
        axis=1,
    )

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["timeSeconds"] = (df["timestamp"] - pd.Timestamp("1970-01-01")) // pd.Timedelta(
        "1s"
    )  # to seconds since epoch
    df["derivative"] = df["distance"].diff() / df["timeSeconds"].diff()

    return df


def filter_data(df, distance_threshold=0.5):
    """
    filter to just the points around when the distance is small
    """
    mask_distance = df["distance"] < distance_threshold
    changePoints = np.where((mask_distance - mask_distance.shift()).fillna(0) != 0)[0]
    return changePoints


def fit_func(x, a, b, c, d, e):
    return a * pow(x, 2) + b * x + c + d * pow(x, 3) + e * x**4


def loss_function(params, t, y, penalty_weight=100):
    """
    I want the function to be 0 when the distance to the stop is 0, that is most important to the fit
    I am not sure what to do with the fit besides getting the function, but it is fun and easy to do so
    might as well do it
    """
    a, b, c, d, e = params

    residual = y - fit_func(t, a, b, c, d, e)
    least_squares = np.sum(residual**2)

    min = y.idxmin()
    value_at_min = fit_func(t.loc[min], a, b, c, d, e)
    penalty = penalty_weight * value_at_min**2

    total_loss = least_squares + penalty

    return total_loss


if __name__ == "__main__":

    database = "newBusTracking.db"
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    vehicle_id = "13005"
    df = get_data(vehicle_id, conn)
    changePoints = filter_data(df)

    for i in range(0, len(changePoints), 2):
        start_index = changePoints[i]
        end_index = changePoints[i + 1]
        df_plot = df.iloc[start_index:end_index]
        #        df_plot = df_plot.drop_duplicates(subset='distance')

        min = df_plot["distance"].min()
        df_plot["timeSeconds"] = (
            df_plot["timestamp"] - pd.Timestamp("1970-01-01")
        ) // pd.Timedelta("1s")
        df_plot["timeSeconds"] = (
            df_plot["timeSeconds"] - df_plot["timeSeconds"].min()
        ) / (df_plot["timeSeconds"].max() - df_plot["timeSeconds"].min())

        res = minimize(
            loss_function,
            [1, 1, 1, 1, 1],
            args=(df_plot["timeSeconds"], df_plot["distance"]),
        )
        a_opt, b_opt, c_opt, d_opt, e_opt = res.x
        y_opt = fit_func(df_plot["timeSeconds"], a_opt, b_opt, c_opt, d_opt, e_opt)

        plt.figure(figsize=(30, 10))
        #    plt.ylim(-.03, .03)
        plt.scatter(df_plot["timestamp"], df_plot["distance"], label="Data")
        #        plt.plot(df_plot['timestamp'], y_fit, label='Fit', color='red')
        plt.plot(df_plot["timestamp"], y_opt, label="Opt", color="green")
        plt.xlabel("normalized_time")
        plt.ylabel("distance")
        plt.legend()
        plt.savefig("temp.png")
        os.system("kitty icat temp.png")
        plt.close()
