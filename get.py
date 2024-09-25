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
    try:
        vehicleList = r.json()
    except requests.exceptions.JSONDecodeError:
        print(r.text)
        raise Exception("could not decode json, printed text and not throwing error")


    #print(vehicleList[0].keys()) #location{latitude, longitude}
    return vehicleList

