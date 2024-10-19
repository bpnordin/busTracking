from bokeh.plotting import figure, show, curdoc
from database import BusData
from bokeh.models import ColumnDataSource, RangeTool, Select, Circle,Plot
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

dbFile = "newBusTracking.db"
db = BusData(dbFile)
routeNum = "1"

df = db.getRouteLocationData(routeNum)
df = db.calculateDistance(df)
selectVehicles = df['vehicle_id'].unique().tolist()
selectVehicleWidget = Select(title="Select a vehicle id",options=selectVehicles)

selectDirection = df['destination'].unique().tolist()
selectDirectionWidget = Select(title="Select a destination",options=selectDirection)

def update_id(attr,old,new):
    source.data = df.loc[(df['destination'] == selectDirectionWidget.value) & (df['vehicle_id'] == selectVehicleWidget.value)].sort_values('timestamp')

def update_destination(att,old,new):
    source.data = df.loc[(df['destination'] == selectDirectionWidget.value) & (df['vehicle_id'] == selectVehicleWidget.value)].sort_values('timestamp')


df_vehicle = df.loc[df['vehicle_id'] == "13004"].sort_values('timestamp')
source = ColumnDataSource(df_vehicle)
selectVehicleWidget.on_change('value', update_id)
selectDirectionWidget.on_change('value',update_destination)


stop_coords = (40.769267, -111.882791)
x,y = stop_coords

stopData = ColumnDataSource({"x":[y],"y":[x],"sizes":[.005]})
glyph = Circle(x="x", y="y", radius="sizes", line_color="red", line_width=3,fill_alpha=0)

p = figure()
p.line("longitude","latitude",source=source)
p.add_glyph(stopData,glyph)
layout = column(p, selectVehicleWidget,selectDirectionWidget)
curdoc().add_root(layout)
show(layout)

