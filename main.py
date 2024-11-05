from bokeh.plotting import figure, show, curdoc
from database import BusData
from bokeh.models import ColumnDataSource, RangeTool, Select, Circle, Plot
from bokeh.layouts import column
import numpy as np


"""

1. get list of vehicles
2. get destination they are going ("two unique options")
3. filter out for bus stop distance
    (need to also implement getting bus stop coords)
4. 

instead of calculating distance, just use lat lon in x y and calc the distance of that
"""

dbFile = "data/newBusTracking.db"
db = BusData(dbFile)
routeNum = "1"

df = db.getRouteLocationData(routeNum)
df = db.calculateDistance(df)
df = db.getInsidePoints(df)
print(df[df['inside']])

selectVehicles = df["vehicle_id"].unique().tolist()
selectVehicleWidget = Select(title="Select a vehicle id", options=selectVehicles)

selectDirection = df["destination"].unique().tolist()
selectDirectionWidget = Select(title="Select a destination", options=selectDirection)


def update_id(attr, old, new):
    mask = (df["destination"] == selectDirectionWidget.value) & (df["vehicle_id"] == selectVehicleWidget.value)
    source.data = df.loc[mask].sort_values("timestamp")
    source_inside.data = df.loc[mask & df['inside']].sort_values("timestamp")


def update_destination(att, old, new):
    mask = (df["destination"] == selectDirectionWidget.value) & (df["vehicle_id"] == selectVehicleWidget.value)
    source.data = df.loc[mask].sort_values("timestamp")
    source_inside.data = df.loc[mask & df['inside']].sort_values("timestamp")


df_vehicle = df.loc[df["vehicle_id"] == "13004"].sort_values("timestamp")
print(df_vehicle)
source = ColumnDataSource(df_vehicle)
source_inside = ColumnDataSource(df_vehicle[df_vehicle['inside']])
selectVehicleWidget.on_change("value", update_id)
selectDirectionWidget.on_change("value", update_destination)


stop_coords = (40.769267, -111.882791)
x, y = stop_coords

stopData = ColumnDataSource({"x": [y], "y": [x], "sizes": [0.005]})
glyph = Circle(
    x="x", y="y", radius="sizes", line_color="red", line_width=3, fill_alpha=0
)

p = figure(match_aspect=True)
p.scatter("longitude", "latitude", source=source,color="blue")
p.scatter("longitude", "latitude", source=source_inside,color="red")
p.add_glyph(stopData, glyph)
layout = column(p, selectVehicleWidget, selectDirectionWidget)
curdoc().add_root(layout)
show(layout)
