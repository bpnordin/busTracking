from bokeh.plotting import figure, show
from database import BusData
from bokeh.models import ColumnDataSource, RangeTool
from bokeh.layouts import column


"""

1. get list of vehicles
2. get direction they are going ("two unique options")
3. filter out for bus stop distance
    (need to also implement getting bus stop coords)
4. 
"""

dbFile = "busData.db"
db = BusData(dbFile)

vehicle_df = db.getVehiclesFromRoute("1")
#list of lists of dataframes
vehicleInfoDict = {}

for vehicle_id in vehicle_df['vehicle_id']:
    print(vehicle_id)
    location_df = db.getVehicleLocationData(vehicle_id)
    location_df = db.calculateDistance(location_df)
    df = db.filterDataForDistance(location_df)
    vehicleInfoDict[vehicle_id] = df
    break

uniqueDirections = {}
cds = ColumnDataSource(data={})
l = []
d = []
for vID,listDF in vehicleInfoDict.items():
    uniqueDirections[vID] = []
    for df in listDF:
        uniqueDirections[vID].extend(df['destination'].unique())
        cds = ColumnDataSource(data=df)
    l = listDF

    print(list(set(uniqueDirections[vID])))
    d = list(set(uniqueDirections[vID]))

directionLabel = [f"Direction {i}" for i in d]
print(directionLabel)
labels = [f"DataFrame {i}: {df.timestamp.dt.time.min()} - {df.timestamp.dt.time.max()}" for i, df in enumerate(l)]
print(labels)
# create a new plot with a title and axis labels
p = figure(title="Bus distance at time", x_axis_label="time stamp", y_axis_label="distance",x_axis_type="datetime")

# add a line renderer with legend and line thickness
p.scatter('timestamp', 'distance',source=cds)
select = figure(title="Drag the middle and edges of the selection box to change the range above",
                height=130, width=800, y_range=p.y_range,
                x_axis_type="datetime", y_axis_type=None,
                tools="", toolbar_location=None, background_fill_color="#efefef")

range_tool = RangeTool(x_range=p.x_range, start_gesture="pan")
range_tool.overlay.fill_color = "navy"
range_tool.overlay.fill_alpha = 0.2

select.line('timestamp', 'distance', source=cds)
select.ygrid.grid_line_color = None
select.add_tools(range_tool)

show(column(p, select))

# show the results
