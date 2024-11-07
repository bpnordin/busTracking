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
df = db.getTrip(df)
