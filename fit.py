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

    vehicle_id = '24005'
    cursor.execute('select latitude, longitude, timestamp from locations where vehicle_id is ?',(vehicle_id,))

    locationList = cursor.fetchall()
    df = pd.DataFrame(locationList, columns=['latitude', 'longitude', 'timestamp'])
    stop_coords =('40.769267', '-111.882791') #my stop near me, just for testing
    df['distance'] = df.apply(lambda row: distance.geodesic(stop_coords,(row['latitude'],row['longitude'])).miles,axis=1)

    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['timeSeconds'] = (df['timestamp'] - pd.Timestamp("1970-01-01")) // pd.Timedelta("1s")#to seconds since epoch
    df['derivative'] = df['distance'].diff() / df['timeSeconds'].diff()

    return df


def filter_data(df, distance_threshold = 1, minutes_threshold = "10 minutes"):
    """
    filter to just the points around when the distance is small
    but I don't care about distsance, I care about time I just realized
    distance ~ 0 +- some amount of minutes
    """
    start_time = '2024-09-27 06:00:00'
    end_time = '2024-09-27 08:00:00'

    mask_time = (df['timestamp'] > start_time) & (df['timestamp'] < end_time)
    mask_distance = df['distance'] < distance_threshold
    #get points around this +- minutes_threshold
    #but this isn't a gurantee, it also needs to be within a certain distance
    mask_velocity = (df['derivative'] > 0) & (df['derivative'].shift(1) < 0)
    df_poi = df[mask_velocity & mask_distance]['timestamp']
    print(df[mask_velocity & mask_distance])


    for poi in df_poi:
        print(poi)
        window_start = poi - pd.to_timedelta(minutes_threshold)
        window_end = poi + pd.to_timedelta(minutes_threshold)
#        mask_time = (df['timestamp'] > window_start) & (df['timestamp'] < window_end)
        break




    mask = mask_time
#    mask = mask_distance
    df_predict = df.loc[mask]
    df_predict = df_predict.drop_duplicates(subset=['distance'])
    #normalize for fitting
    #TODO I should change this over to a pipeline so undoing the normalization is easy
#    df_predict['timeSeconds'] = (df_predict['timeSeconds'] - df_predict['timeSeconds'].min()) / (df_predict['timeSeconds'].max() - df_predict['timeSeconds'].min())
#    df_predict['distance'] = (df_predict['distance'] - df_predict['distance'].min()) / (df_predict['distance'].max() - df_predict['distance'].min())
#    df_predict['derivative'] = (df_predict['derivative'] - df_predict['derivative'].min()) / (df_predict['derivative'].max() - df_predict['derivative'].min())


    return df_predict

def fit_func(x, a, b,c,d,e):
    return a*pow(x,2) + b*x + c + d*pow(x,3)+e*x**4

def loss_function(params, t, y,penalty_weight = 100):
    """
    I want the function to be 0 when the distance to the stop is 0, that is most important to the fit
    I am not sure what to do with the fit besides getting the function, but it is fun and easy to do so 
    might as well do it
    """
    a,b,c,d,e = params
    
    residual = y - fit_func(t,a,b,c,d,e)
    least_squares = np.sum(residual**2)

    min = y.idxmin()
    value_at_min = fit_func(t.loc[min], a, b, c,d,e)
    penalty = penalty_weight*value_at_min**2 

    total_loss = least_squares + penalty
    
    return total_loss

if __name__ == '__main__':

    database = "newBusTracking.db"
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    vehicle_id = '24005'
    df = get_data(vehicle_id, conn)
#    df = filter_data(df)
    """
    min = df['distance'].min()
    res = minimize(loss_function, [1,1,1,1,1],args=(df['timeSeconds'],df['distance']))

    a_opt,b_opt,c_opt,d_opt,e_opt = res.x


    popt, pcov = curve_fit(fit_func, df['timeSeconds'], df['distance'])


    a_fit, b_fit,c_fit, d_fit,e_fit= popt
    y_fit = fit_func(df['timeSeconds'], a_fit, b_fit,c_fit,d_fit,e_fit)
    y_opt = fit_func(df['timeSeconds'], a_opt, b_opt, c_opt, d_opt,e_opt)
    """
    df['derivative'].apply(lambda d: 1 if d > 0 else -1 if d < 0 else 0)

    plt.figure(figsize=(30, 10))
#    plt.ylim(-.03, .03)
    plt.scatter(df['timestamp'], df['distance'], label='Data')
    plt.scatter(df['timestamp'], df['derivative'], label='Data')
#    plt.plot(df['timeSeconds'], y_fit, label='Fit', color='red')
#    plt.plot(df['timeSeconds'], y_opt, label='Opt', color='green')
    plt.xlabel('normalized_time')
    plt.ylabel('distance')
    plt.legend()
    plt.savefig("temp.png")
    os.system('kitty icat temp.png')
    plt.close()
