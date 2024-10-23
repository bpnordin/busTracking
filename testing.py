from database import BusData


dbFile = "newBusTracking.db"
db = BusData(dbFile)
routeNum = "1"

radius = .005

df = db.getRouteLocationData(routeNum)
df = db.calculateDistance(df)
df.sort_values('timestamp',inplace=True)

df['offsetDistance'] = df.groupby(['vehicle_id','destination'])['distance'].transform(lambda x: (x < radius) & (x.shift().fillna(x) < radius))

#this will = -1 on the False when going from True > False
# or = 1 from False > True
df['offsetDistance_diff'] = df.groupby(['vehicle_id', 'destination'])['offsetDistance'].diff()
#df['offsetDistance'] = df.groupby(['vehicle_id','destination'])['distance'].shift()
#a = df.groupby(['vehicle_id','destination'])[['distance','offsetDistance']].apply(lambda x: (x['distance'] < radius) & (x['offsetDistance'] < radius))
vehicle_id = '24005'
endIndex = 55
print(df.loc[(df['offsetDistance_diff'] == -1) | df['offsetDistance_diff'] == 1].head(endIndex))
