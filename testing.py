from pandas.core.frame import treat_as_nested
from database import BusData
import matplotlib.pyplot as plt
import numpy as np


dbFile = "newBusTracking.db"
db = BusData(dbFile)
routeNum = "1"

radius = .005
second_radius = .006
vehicle_id = '13003'

df = db.getRouteLocationData(routeNum)
df = db.calculateDistance(df)
df.sort_values('timestamp',inplace=True)
one_vehicle = df.loc[df['vehicle_id'] == vehicle_id].copy()
df = df.loc[df['distance'] < second_radius].copy()
df = df.loc[df['distance'].diff() != 0].copy()
def change(series):
    b1 = series < radius
    b2 = series.shift() < radius
    if b1.iloc[0] == True:
        b2.iloc[0] = True
    else:
        b2.iloc[0] = False
        
    return b1 ^ b2


df['border'] = df.groupby(['vehicle_id','destination'])['distance'].transform(change)

group = df.groupby(['vehicle_id','destination'])[['distance','border','latitude','longitude']]

changePoints = None
for groupTuple,series in group:
    id, destination = groupTuple
    if id == '24006' & destination == 'University Hospital':
        print(f'{id} : {destination}')
        changePoints = series.loc[series['border'] == True].index

print(df.loc[changePoints])
