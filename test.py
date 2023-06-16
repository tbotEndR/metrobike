import folium
from folium.plugins import MarkerCluster
import geopandas as gpd
import requests
import webbrowser
from geopy.geocoders import Nominatim
from geopy import exc
from geopy import distance
from sys import exit

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

class userObj(locationObj):
    def __init__(self, name, latitude, longitude, k=1, queryType=None):
        self.name = name
        self.coordinates = (latitude, longitude)
        self.k = k
        self.queryType = queryType

class routeObj():
    def __init__(self, source, destination):
        self.source = source
        self.destination = destination
        self.sourceStation = nearestStation(source.coordinates, 1, stationType="bikes")[0]
        self.destinationStation = nearestStation(destination.coordinates, 1, stationType="docks")[0]

def do_geocode(address, attempt = 1, max_attempts = 5):
    try:
        return geocode(address)
    
    except exc.GeocoderTimedOut:
        if attempt <= max_attempts:
            return do_geocode(address, attempt=attempt+1)
        exit("Geocoding service requests timed out. Please try again.\n")

    except TimeoutError:
        if attempt <= max_attempts:
            return do_geocode(address, attempt=attempt+1)
        exit("Geocoding service requests timed out. Please try again.\n")


def getUserLocation(arg = "station"):
    userLocation = None
    if arg == "station":
        while userLocation is None:
            userAddress= input("What is your current location? (Default: Mid-City, LA)\n") or "Mid-City, Los Angeles"
            userLocation = do_geocode(userAddress)
            if userLocation == None:
                print("Location not found. Try again.\n")

    elif arg == "source":
        while userLocation is None:
            userAddress= input("What is your starting point?\n")
            userLocation = do_geocode(userAddress)
            if userLocation == None:
                print("Location not found. Try again.\n")
    
    elif arg == "destination":
        while userLocation is None:
            userAddress= input("What is your destination?\n")
            userLocation = do_geocode(userAddress)
            if userLocation == None:
                print("Location not found. Try again.\n")

    print(userLocation)
    print("Is this the correct location? (y/n)")
    correct = input() or 'y'
    if correct == 'n':
        getUserLocation(arg)
    return userLocation

def calcDist(stationLoc, userLoc):
    try:
        return int(distance.distance((stationLoc[0], stationLoc[1]),(userLoc[0], userLoc[1])).meters)
    except:
        return 0
    
def nearestStation(location, k = 1, stationType = "bikes"):
    tmpdf = workingdf.copy(deep=True)
    tmpdf.userDist = [calcDist((stationLat, stationLon), location)
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

def getStationData():
    url = "https://bikeshare.metro.net/stations/json/"
    r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    #GeoJSON import using requests because the geopandas.read_file(url) doesn't allow for
    ##specifying a request header, which results in a 403 denied response
    data = r.json()
    fulldf = gpd.GeoDataFrame.from_features(data)
    smalldf = fulldf[["addressStreet", "addressZipCode", "bikesAvailable", "docksAvailable", "latitude", "longitude"]]
    smalldf = smalldf.assign(userDist='NV')
    return smalldf

def toMarker(station, type):
    if type == "bikes":
        html = """{0}<br><br>Available bikes: {1}""".format(station.name, station.bikes)
        iconType = "bicycle"
        color = "darkblue"
    elif type == "docks":
        html = """{0}<br><br>Available docks: {1}""".format(station.name, station.docks)
        iconType = "charging-station"
        color = "lightred"
    iframe = folium.IFrame(html, figsize=(3,2))
    popup = folium.Popup(iframe, max_width=200)
    mapMarker = folium.Marker(location=station.coordinates, popup=popup, icon=folium.Icon(color=color, prefix='fa', icon=iconType))
    return mapMarker

def nearestX(arg, map):
    userLoc = getUserLocation()
    if arg == "bikes":
        k = int(input("How many bike stations do you want to display? (Default: 1)\n")) or 1
    elif arg == "docks":
        k = int(input("How many docks do you want to display? (Default: 1)\n")) or 1

    user = userObj(name = "You are here", latitude= userLoc.latitude, longitude= userLoc.longitude, k = k, queryType = arg)
    relevantStations = nearestStation(user.coordinates, user.k, user.queryType)
    stationCluster = MarkerCluster(name="nearest stations",).add_to(map)
    for i in range(len(relevantStations)):
        toMarker(relevantStations[i], user.queryType).add_to(stationCluster)
    folium.Marker(location=user.coordinates, popup="You are here", icon=folium.Icon(color="green", prefix='fa', icon="circle-user")).add_to(map)
    map.save("bigMap.html")

def directions(startLat, startLon, destLat, destLon, mode="bicycle"):
    url = "https://route-and-directions.p.rapidapi.com/v1/routing"
    querystring = {"waypoints":f"{str(startLat)},{str(startLon)}|{str(destLat)},{str(destLon)}", "mode":mode}
    #querystring = {"waypoints":"34.06339,-118.23616|33.99537,-118.4648","mode":"walk"}
    headers = {
	"X-RapidAPI-Key": "f5a6ad24fdmsh40bd4fffc865494p135019jsndaa4d4c1bd9b",
	"X-RapidAPI-Host": "route-and-directions.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)
    return response

def plotRoute(routeResponse, map):
    mls = routeResponse.json()['features'][0]['geometry']['coordinates']
    points = [(i[1], i[0]) for i in mls[0]]
    folium.PolyLine(points, weight=5, opacity=1).add_to(map)


def routePlanning(map):
    source = getUserLocation("source")
    srcObj = locationObj(source.address, source.latitude, source.longitude)
    destination = getUserLocation("destination")
    destObj = locationObj(destination.address, destination.latitude, destination.longitude)
    route = routeObj(srcObj, destObj)
    bikeStation = route.sourceStation
    dockStation = route.destinationStation
    print(bikeStation.latitude(), bikeStation.longitude(), dockStation.latitude(), dockStation.longitude())

    startToBike = directions(srcObj.latitude(), srcObj.longitude(), bikeStation.latitude(), bikeStation.longitude(), mode="walk")
    bikeToDock = directions(bikeStation.latitude(), bikeStation.longitude(), dockStation.latitude(), dockStation.longitude())
    dockToDest = directions(dockStation.latitude(), dockStation.longitude(), destObj.latitude(), destObj.longitude(), mode="walk")

    print(startToBike)

    plotRoute(startToBike, map)
    plotRoute(bikeToDock, map)
    plotRoute(dockToDest, map)

    toMarker(route.sourceStation, "bikes").add_to(map)
    toMarker(route.destinationStation, "docks").add_to(map)
    folium.Marker(location=route.source.coordinates, popup="Start", icon=folium.Icon(color="green", prefix='fa', icon="circle-user")).add_to(map)
    folium.Marker(location=route.destination.coordinates, popup="Destination", icon=folium.Icon(color="green", prefix='fa', icon="map-pin")).add_to(map)
    map.save("bigMap.html")
    
    

"""Setup code, grab newest GeoJSON Data and turn it into a geopandas df with only the relevant information"""
geolocator = Nominatim(user_agent="metrobike_application")
geocode = lambda query: geolocator.geocode("%s, Los Angeles County CA" % query)
workingdf = getStationData()
m = folium.Map(location=[workingdf.latitude.mean(), workingdf.longitude.mean()], zoom_start=12, control_scale=True)
minimap = folium.plugins.MiniMap()
m.add_child(minimap)
print("<<Loading in current data>>\n")

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