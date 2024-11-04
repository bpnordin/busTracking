from database import BusData
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

dbFile = "data/newBusTracking.db"
db = BusData(dbFile)
routeNum = "1"

radius = 0.005
stop_coords=(40.769267, -111.882791)
y,x = stop_coords

df = db.getRouteLocationData(routeNum)
df = db.calculateDistance(df)
df.sort_values("timestamp", inplace=True)
#filter so we don't get as many points
#df = df.loc[df["distance"] < radius + .001].copy()
#df = df.loc[df["distance"].diff() != 0].copy()


def change(series):
    b1 = series < radius
    b2 = series.shift() < radius
    if b1.iloc[0] == True:
        b2.iloc[0] = True
    else:
        b2.iloc[0] = False

    return b1 ^ b2


df["border"] = df.groupby(["vehicle_id", "destination"])["distance"].transform(change)

group = df.groupby(["vehicle_id", "destination"])[
    ["distance", "border", "latitude", "longitude"]
]

vehicle_id = "24006"
changePoints = None
for groupTuple, series in group:
    id, destination = groupTuple
    if (id == vehicle_id) & (destination == "University Hospital"):
        print(f"{id} : {destination}")
        changePoints = series.loc[series["border"] == True].index

print(df.loc[changePoints])

circle = Circle((x,y),radius=radius,color='red',fill=False)

plt.plot(df.loc[df['vehicle_id'] == vehicle_id]['longitude'],df.loc[df['vehicle_id'] == vehicle_id]['latitude'])
plt.scatter(df.loc[changePoints]['longitude'],df.loc[changePoints]['latitude'],color='red')
plt.gca().add_patch(circle)
plt.show()
