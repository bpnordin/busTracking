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
df = db.getTrip(df)

selectVehicles = df["vehicle_id"].unique().tolist()
selectVehicleWidget = Select(
    title="Select a vehicle id", options=selectVehicles, value=selectVehicles[0]
)

selectDirection = df["destination"].unique().tolist()
selectDirectionWidget = Select(
    title="Select a destination", options=selectDirection, value=selectDirection[0]
)

mask = (df["destination"] == selectDirectionWidget.value) & (
    df["vehicle_id"] == selectVehicleWidget.value
)
df_default = df[mask]

selectTrip = df_default['tripID'].unique().tolist()
selectTripWidget = Select(title="select a tripID", options=selectTrip, value="1")

def update_id(attr, old, new):
    tripMask = (df["destination"] == selectDirectionWidget.value) & (
        df["vehicle_id"] == selectVehicleWidget.value
    )
    selectTripWidget.update(options=df[tripMask]['tripID'].unique().tolist())
    print(selectVehicleWidget.value)
    print(df[df['vehicle_id'] == selectVehicleWidget.value])
    mask = (df["destination"] == selectDirectionWidget.value) & (
        df["vehicle_id"] == selectVehicleWidget.value
    ) & (df['tripID'] == selectTripWidget.value)
    source.data = df.loc[mask].sort_values("timestamp")
    source_inside.data = df.loc[mask & df["inside"]].sort_values("timestamp")


def update_destination(att, old, new):
    tripMask = (df["destination"] == selectDirectionWidget.value) & (
        df["vehicle_id"] == selectVehicleWidget.value
    )
    selectTripWidget.update(options=df[tripMask]['tripID'].unique().tolist())
    mask = (df["destination"] == selectDirectionWidget.value) & (
        df["vehicle_id"] == selectVehicleWidget.value
    ) & (df['tripID'] == selectTripWidget.value)
    source.data = df.loc[mask].sort_values("timestamp")
    source_inside.data = df.loc[mask & df["inside"]].sort_values("timestamp")

def update_trip(att,old,new):
    mask = (df["destination"] == selectDirectionWidget.value) & (
        df["vehicle_id"] == selectVehicleWidget.value
    ) & (df['tripID'] == selectTripWidget.value)
    source.data = df.loc[mask].sort_values("timestamp")
    source_inside.data = df.loc[mask & df["inside"]].sort_values("timestamp")


mask = (df["destination"] == selectDirectionWidget.value) & (
    df["vehicle_id"] == selectVehicleWidget.value
) & (df['tripID'] == selectTripWidget.value)

df_default = df[mask]
source = ColumnDataSource(df_default)
source_inside = ColumnDataSource(df_default[df_default["inside"]])
selectVehicleWidget.on_change("value", update_id)
selectDirectionWidget.on_change("value", update_destination)
selectTripWidget.on_change("value",update_trip)


stop_coords = (40.769267, -111.882791)
x, y = stop_coords

stopData = ColumnDataSource({"x": [y], "y": [x], "sizes": [0.005]})
glyph = Circle(
    x="x", y="y", radius="sizes", line_color="red", line_width=3, fill_alpha=0
)

p = figure(match_aspect=True)
p.line("longitude", "latitude", source=source, color="blue")
p.scatter("longitude", "latitude", source=source_inside, color="red")
p.add_glyph(stopData, glyph)
layout = column(p, selectVehicleWidget, selectDirectionWidget,selectTripWidget)
curdoc().add_root(layout)
show(layout)
