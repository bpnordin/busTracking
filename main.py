import requests
import time
from geopy import distance


def main():
         
    route = "1"
    stopsURL = "https://webapi.rideuta.com/api/Stops/" + route
    #routesURL = "https://webapi.rideuta.com/api/Routes/" + route #this is for the shape of the route, don't need
    vehicleLocURL = "https://webapi.rideuta.com/api/VehicleLocation/" + route
    requestTime = 1

    r = requests.get(stopsURL)
    stopList = r.json()
    time.sleep(requestTime)


    r = requests.get(vehicleLocURL)
    vehicleList = r.json()
    time.sleep(requestTime)

    print(stopList[0].keys()) #stop_lat stop_lon
    print(vehicleList[0].keys()) #location{latitude, longitude}

    lat1 = float(stopList[0]['stop_lat'])
    lon1 = float(stopList[0]['stop_lon'])
    coords_1 = (lat1, lon1)

    lat2 = float(vehicleList[0]['location']['latitude'])
    lon2 = float(vehicleList[0]['location']['longitude'])
    coords_2 = (lat2, lon2)
    
    print(distance.geodesic(coords_1, coords_2).miles)



if __name__ == '__main__':
    main()
