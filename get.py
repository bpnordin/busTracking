import requests

def getStops(route):

    stopsURL = "https://webapi.rideuta.com/api/Stops/" + route

    r = requests.get(stopsURL)
    stopList = r.json()

    print(stopList[0].keys()) #stop_lat stop_lon
    return stopList

def getVehicle(route):

    vehicleLocURL = "https://webapi.rideuta.com/api/VehicleLocation/" + route

    r = requests.get(vehicleLocURL)
    vehicleList = r.json()

    #print(vehicleList[0].keys()) #location{latitude, longitude}
    return vehicleList

