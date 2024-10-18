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
for vID,listDF in vehicleInfoDict.items():
    uniqueDirections[vID] = []
    for df in listDF:
        uniqueDirections[vID].extend(df['destination'].unique())
        cds = ColumnDataSource(data=df)

    print(set(uniqueDirections[vID]))


print(cds.data)
# create a new plot with a title and axis labels
p = figure(title="Bus distance at time", x_axis_label="time stamp", y_axis_label="distance",x_axis_type="datetime")

# add a line renderer with legend and line thickness
p.line('timestamp', 'distance',source=cds)

# show the results
show(p)
