from operator import length_hint
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


def get_inside_points(series):
    b1 = series < radius
    b2 = series.shift() < radius
    if b1.iloc[0]:
        b2.iloc[0] = True
    else:
        b2.iloc[0] = False

    border = b1 ^ b2
    df_border = border.reset_index(drop=False)
    df_border.columns = ["index","inside"]
    start = series.iloc[0] < radius
    end = series.loc[series.index[-1]] < radius
    if start:
        #make the start a change point
        border.iloc[0] = True
    if end:
        #make the end a change point
        border.loc[border.index[-1]] = True

    #time to turn the series into a flat dataframe
    df = series.reset_index(drop=False)
    df.columns = ['index', 'distance']
    changePoints = df[border.reset_index(drop=True)]
    print(df_border)

    assert len(changePoints) % 2 == 0
    for i in range(0,len(changePoints),2):
        #i is where it is inside
        #i+1 is where it is just outside
        #any index between those two things should be inside no include i+1
        start = changePoints.iloc[i].name
        stop = changePoints.iloc[i+1].name
        print(start)
        print(stop)
        df_border.loc[start:stop-1,'inside'] = True
        df_border.loc[stop,'inside'] = False

    df_border = df_border.set_index('index')
    return df_border['inside']


df["inside"] = df.groupby(["vehicle_id", "destination"])["distance"].transform(get_inside_points)
print(df)

group = df.groupby(["vehicle_id", "destination"])[
    ["distance", "inside", "latitude", "longitude","timestamp"]
]

vehicle_id = "24002"
direction_tuple = ("University Hospital", "Poplar Grove (Orange St)")
_, vehicle_direction= direction_tuple
circle = Circle((x, y), radius=radius, color="red", fill=False)

mask = (df['destination'] == vehicle_direction) & (df['vehicle_id'] == vehicle_id)
mask_inside = mask & df['inside']
plt.plot(
    df.loc[mask]["longitude"],
    df.loc[mask]["latitude"],
)
plt.scatter(
    df.loc[mask_inside]["longitude"], df.loc[mask_inside]["latitude"], color="red"
)
plt.gca().add_patch(circle)
plt.show()
