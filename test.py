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

class stationObj(locationObj):
    def __init__(self, name, latitude, longitude, bikes, docks, userDist=None):
        self.name = name
        self.coordinates = (latitude, longitude)
        self.bikes = bikes
        self.docks = docks
        self.userDist = userDist

class userObj(locationObj):
    def __init__(self, name, latitude, longitude, k, queryType):
        self.name = name
        self.coordinates = (latitude, longitude)
        self.k = k
        self.queryType = queryType

class routeObj():
    def __init__(self, source, destination):
        self.source = source
        self.destination = destination
        self.startStation = source.nearestStation("bikes")[0]
        self.endStation = destination.nearestStation("docks")[0]

def do_geocode(address, attempt = 1, max_attempts = 5):
    try:
        return geocode(address)
    except exc.GeocoderTimedOut:
        if attempt <= max_attempts:
            return do_geocode(address, attempt=attempt+1)
        raise

def getUserInput():
    userAddress= input("What is your current location?\n") or "Mid-City, Los Angeles"
    numOfStations = int(input("How many stations do you want to display? (Default 1)\n") or 1)
    queryType = input("Are you searching for available bikes, docks or do you need route planning? (-b, -d or -r)\n").lower() or "-b"
    userLocation = do_geocode(userAddress)
    if userLocation == None:
        exit("Location not found.")
    else:
        if queryType == "-b":
            user = userObj("You are here", userLocation.latitude, userLocation.longitude, numOfStations, "bikes")
        elif queryType== "-d":
            user = userObj("You are here", userLocation.latitude, userLocation.longitude, numOfStations, "docks")
        else:
            exit("Couldn't parse bikes or stations.")
        return user

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
    elif stationType == "bikes":
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


geolocator = Nominatim(user_agent="metrobike_application")
geocode = lambda query: geolocator.geocode("%s, Los Angeles County CA" % query)
workingdf = getStationData()

user = getUserInput()
stationDf = getStationData()
relevantStations = nearestStation(user.coordinates, user.k, user.queryType)

m = folium.Map(location=[stationDf.latitude.mean(), stationDf.longitude.mean()], zoom_start=12, control_scale=True)
stationCluster = MarkerCluster(name="nearest stations",).add_to(m)
for i in range(len(relevantStations)):
    folium.Marker(location=relevantStations[i].coordinates, popup=relevantStations[i].name, icon=folium.Icon(color="blue")).add_to(stationCluster)
folium.Marker(location=user.coordinates, popup=user.name, icon=folium.Icon(color="green")).add_to(m)
m.save("bigMap.html")
webbrowser.open("bigMap.html")
