from bokeh.plotting import figure, show
from database import BusData


"""

1. get list of vehicles
2. get direction they are going ("two unique options")
3. filter out for bus stop distance
    (need to also implement getting bus stop coords)
4. 
"""

dbFile = "newBusTracking.db"
db = BusData(dbFile)

vehicle_id = "13005"
vehicle_df = db.getVehiclesFromRoute("1")

for vehicle_id in vehicle_df['vehicle_id']:
    location_df = db.getVehicleLocationData(vehicle_id)
    location_df = db.calculateDistance(location_df)
    changePoints = db.filterDataForDistance(location_df)
    print(changePoints)

# prepare some data
x = [1, 2, 3, 4, 5]
y = [6, 7, 2, 4, 5]

# create a new plot with a title and axis labels
p = figure(title="Simple line example", x_axis_label="x", y_axis_label="y")

# add a line renderer with legend and line thickness
p.line(x, y, legend_label="Temp.", line_width=2)

# show the results
show(p)
