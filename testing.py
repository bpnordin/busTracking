from database import BusData
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import numpy as np

dbFile = "data/newBusTracking.db"
db = BusData(dbFile)
routeNum = "1"

radius = 0.005
stop_coords = (40.769267, -111.882791)
y, x = stop_coords

df = db.getRouteLocationData(routeNum)
df = db.calculateDistance(df)
df.sort_values("timestamp", inplace=True)
# filter so we don't get as many points
# df = df.loc[df["distance"] < radius + .001].copy()
# df = df.loc[df["distance"].diff() != 0].copy()

