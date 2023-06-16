import folium
from folium.plugins import MarkerCluster
import webbrowser
from sys import exit
import ext_requests as er
import mapping_tools as mt

global workingdf

class locationObj:
    def __init__(self, name, latitude, longitude):
        self.name = name
        self.coordinates = (latitude, longitude)
    
    def latitude(self):
        return self.coordinates[0]
    def longitude(self):
        return self.coordinates[1]

class stationObj(locationObj):
    def __init__(self, name, latitude, longitude, bikes, docks, userDist=None):
        self.name = name
        self.coordinates = (latitude, longitude)
        self.bikes = bikes
        self.docks = docks
        self.userDist = userDist

class routeObj():
    def __init__(self, source, destination):
        self.source = source
        self.destination = destination
        self.sourceStation = nearestStation(source.coordinates, 1, stationType="bikes")[0]
        self.destinationStation = nearestStation(destination.coordinates, 1, stationType="docks")[0]

def getUserLocation(arg = "station"):
    userLocation = None
    if arg == "station":
        while userLocation is None:
            userAddress= input("What is your current location? (Default: Mid-City, LA)\n") or "Mid-City, Los Angeles"
            userLocation = er.do_geocode(userAddress)
            if userLocation == None:
                print("Location not found. Try again.\n")

    elif arg == "source":
        while userLocation is None:
            userAddress= input("What is your starting point?\n")
            userLocation = er.do_geocode(userAddress)
            if userLocation == None:
                print("Location not found. Try again.\n")
    
    elif arg == "destination":
        while userLocation is None:
            userAddress= input("What is your destination?\n")
            userLocation = er.do_geocode(userAddress)
            if userLocation == None:
                print("Location not found. Try again.\n")

    print(userLocation)
    print("Is this the correct location? (y/n)")
    correct = input() or 'y'
    if correct == 'n':
        getUserLocation(arg)
    return userLocation
    
def nearestStation(location, k = 1, stationType = "bikes"):
    tmpdf = workingdf.copy(deep=True)
    tmpdf.userDist = [mt.calcDist((stationLat, stationLon), location)
                for stationLat, stationLon in tmpdf[["latitude", "longitude"]].values]
    if stationType == "bikes":
        tmpdf = tmpdf.drop(tmpdf[tmpdf["bikesAvailable"] == 0].index)
    elif stationType == "docks":
        tmpdf = tmpdf.drop(tmpdf[tmpdf["docksAvailable"] == 0].index)
    tmpdf = tmpdf.sort_values("userDist", ascending=True)
    tmpdf = tmpdf.reset_index(drop=True)
    stationArray = []
    for i in range(k):
        row = tmpdf.iloc[i]
        newStation = stationObj(row.addressStreet, row.latitude, row.longitude, row.bikesAvailable, row.docksAvailable, row.userDist)
        stationArray.append(newStation)
    return stationArray

def nearestX(arg, map):
    userLoc = getUserLocation()
    if arg == "bikes":
        k = int(input("How many bike stations do you want to display? (Default: 1)\n")) or 1
    elif arg == "docks":
        k = int(input("How many docks do you want to display? (Default: 1)\n")) or 1

    user = locationObj(userLoc.address, userLoc.latitude, userLoc.longitude)
    relevantStations = nearestStation(user.coordinates, k, arg)
    stationCluster = MarkerCluster(name="nearest stations",).add_to(map)
    for i in range(len(relevantStations)):
        mt.toMarker(relevantStations[i], arg, stationCluster)
    mt.toMarker(user, "start", map)
    map.save("bigMap.html")

def routePlanning(map):
    source = getUserLocation("source")
    srcObj = locationObj(source.address, source.latitude, source.longitude)
    destination = getUserLocation("destination")
    destObj = locationObj(destination.address, destination.latitude, destination.longitude)
    route = routeObj(srcObj, destObj)
    bikeStation = route.sourceStation
    dockStation = route.destinationStation

    startToBike = er.directions(srcObj.latitude(), srcObj.longitude(), bikeStation.latitude(), bikeStation.longitude(), mode="walk")
    bikeToDock = er.directions(bikeStation.latitude(), bikeStation.longitude(), dockStation.latitude(), dockStation.longitude())
    dockToDest = er.directions(dockStation.latitude(), dockStation.longitude(), destObj.latitude(), destObj.longitude(), mode="walk")
    mt.plotRoute(startToBike, map)
    mt.plotRoute(bikeToDock, map)
    mt.plotRoute(dockToDest, map)

    mt.toMarker(route.sourceStation, "bikes", map)
    mt.toMarker(route.destinationStation, "docks", map)
    mt.toMarker(route.source, "start", map)
    mt.toMarker(route.destination, "destination", map)
    map.save("bigMap.html")
    

"""Setup code, grab newest GeoJSON Data and turn it into a geopandas df with only the relevant information"""
print("Loading in current data . . . \n")
workingdf = er.getStationData()
m = folium.Map(location=[workingdf.latitude.mean(), workingdf.longitude.mean()], zoom_start=12, control_scale=True)
minimap = folium.plugins.MiniMap()
m.add_child(minimap)

"""Menu"""
queryType = input("Are you searching for available bikes (-b), docks (-d) or do you need route planning (-r)?\n").lower() or "-b"
if queryType == "-b":
    nearestX("bikes", m) 
elif queryType== "-d":
    nearestX("docks", m)
elif queryType == "-r":
    routePlanning(m)
else:
    exit("Couldn't parse your input, please try again.")

webbrowser.open("bigMap.html")
exit("\nThank you for using our services.\n")