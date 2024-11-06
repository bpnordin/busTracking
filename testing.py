from database import BusData
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import numpy as np
from scipy.interpolate import CubicSpline, splrep


dbFile = "data/newBusTracking.db"
db = BusData(dbFile)
routeNum = "1"

radius = 0.005
stop_coords = (40.769267, -111.882791)
y, x = stop_coords

df = db.getRouteLocationData(routeNum)
df = db.calculateDistance(df)
df = db.getInsidePoints(df)

id = "24002"
destination = "University Hospital"
mask = (df['destination'] == destination) & (df['vehicle_id'] == id)
df = df[mask].reset_index(drop=True)

# Calculate time differences between consecutive timestamps
df['time_diff'] = df['timestamp'].diff().dt.total_seconds() / 60
# Identify indices where time difference exceeds 1 minute
gap_indices = df[df['time_diff'] > 1].index
# Split the DataFrame based on gap indices
split_dfs = []
start_idx = 0
for end_idx in gap_indices:
    #iloc is not inclusive, and end_idx is the place where the timestsamp is > 60
    print(end_idx)
    split_dfs.append(df.iloc[start_idx:end_idx].copy())
    start_idx = end_idx 

# Append the last part of the DataFrame
split_dfs.append(df.iloc[start_idx:].copy())
circle = Circle((x,y),radius=radius,color="red",fill=False)
plt.gca().add_patch(circle)
# Now, split_dfs is a list of DataFrames, each representing a continuous segment of data.
for trip in split_dfs:

    x = trip['longitude']
    y = trip['latitude']
    plt.plot(x,y)
    plt.scatter(trip[trip['inside']]['longitude'],trip[trip['inside']]['latitude'],color="red")

plt.show()
