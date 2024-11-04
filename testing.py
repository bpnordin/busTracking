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


def change(series):
    b1 = series < radius
    b2 = series.shift() < radius
    if b1.iloc[0]:
        b2.iloc[0] = True
    else:
        b2.iloc[0] = False

    return b1 ^ b2


df["border"] = df.groupby(["vehicle_id", "destination"])["distance"].transform(change)

group = df.groupby(["vehicle_id", "destination"])[
    ["distance", "border", "latitude", "longitude"]
]

vehicle_id = "24006"
direction_tuple = ("University Hospital", "Poplar Grove (Orange St)")
vehicle_direction,_ = direction_tuple
changePoints = None
for groupTuple, series in group:
    id, destination = groupTuple
    print(f"{id} : {destination}")
    series.reset_index(inplace=True)
    changePoints = series.loc[series["border"]]
    print(changePoints)
    print(series.loc[0:20])
    if len(changePoints) % 2 != 0:
        #either starts or ends inside the circle
        if series.loc[0,'distance'] < radius:
            print("starts inside")
            series.loc[0,'border'] = True
            changePoints = series.loc[series["border"]]
        if series.loc[series.index[-1],'distance'] < radius:
            print("ends inside")
            series.loc[series.index[-1],'border'] = True
            changePoints = series.loc[series["border"]]
        pass
    assert len(changePoints) % 2 == 0
    for i in range(0,len(changePoints),2):
        #i is where it is inside
        #i+1 is where it is just outside
        #any index between those two things should be inside no include i+1
        start = changePoints.iloc[i].name
        stop = changePoints.iloc[i+1].name
        series.loc[start:stop-1,'border'] = True
        series.loc[stop,'border'] = False
        print(series.loc[start:stop])

    changePoints = series.loc[series["border"]]['index']

circle = Circle((x, y), radius=radius, color="red", fill=False)

plt.plot(
    df.loc[df["vehicle_id"] == vehicle_id]["longitude"],
    df.loc[df["vehicle_id"] == vehicle_id]["latitude"],
)
plt.scatter(
    df.loc[changePoints]["longitude"], df.loc[changePoints]["latitude"], color="red"
)
plt.gca().add_patch(circle)
plt.show()
