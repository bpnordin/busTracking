from bokeh.plotting import figure, show
from database import BusData
from bokeh.models import ColumnDataSource, RangeTool, Select
from bokeh.layouts import column
from bokeh.io import curdoc



"""

1. get list of vehicles
2. get direction they are going ("two unique options")
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
select_widget = Select(title="Select a vehicle id",options=selectVehicles)

def update_id(attr,old,new):
    source.data = df.loc[df['vehicle_id'] == select_widget.value].sort_values('timestamp').to_dict()


df_vehicle = df.loc[df['vehicle_id'] == "13004"].sort_values('timestamp')
source = ColumnDataSource(df_vehicle)
select_widget.on_change('value', update_id)


p = figure()
p.line("longitude","latitude",source=source)
layout = column(p, select_widget)
curdoc().add(p)
curdoc().add(select_widget)
