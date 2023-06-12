import folium
from folium.plugins import MarkerCluster
import geopandas as gpd
import requests
import webbrowser
from geopy.geocoders import Nominatim
from geopy import exc
from geopy import distance
from geopy import units
from sys import exit

geolocator = Nominatim(user_agent="metrobike_application")
geocode = lambda query: geolocator.geocode("%s, Los Angeles County CA" % query)

class locStationObj:
    def __init__(self, geolocation, kStations, bod):
        self.location = geolocation
        self.kStations = kStations
        self.coords = (self.location.latitude, self.location.longitude)
        self.bod = bod

def do_geocode(address, attempt = 1, max_attempts = 5):
    try:
        return geocode(address)
    except exc.GeocoderTimedOut:
        if attempt <= max_attempts:
            return do_geocode(address, attempt=attempt+1)
        raise

def getUlocKstat():
    userInput= input("What is your current location? (Default central LA)\n") or "Mid-City, Los Angeles"
    kBikeStations = int(input("How many stations do you want to display? (Default 1)\n") or 1)
    bOrD = input("Are you searching for available bikes or docks? (Default bikes)\n").lower() or "bikes"
    userLoc = do_geocode(userInput)
    if userLoc != None:
        if bOrD == 'bikes':
            userLoc = locStationObj(userLoc, kBikeStations, "bikesAvailable")
        elif bOrD == 'docks':
            userLoc = locStationObj(userLoc, kBikeStations, "docksAvailable")
        else:
            exit("Couldn't parse bikes or stations.")
        return userLoc
    else:
        exit("Location not found.")

def calcDist(stationLoc, userLoc):
    try:
        return int(distance.distance((stationLoc[0], stationLoc[1]),(userLoc[0], userLoc[1])).meters)
    except:
        return 0

def getStationData():
    url = "https://bikeshare.metro.net/stations/json/"
    r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    #GeoJSON import using requests because the geopandas.read_file(url) doesn't allow for
    ##specifying a request header, which results in a 403 denied response
    data = r.json()
    fulldf = gpd.GeoDataFrame.from_features(data)
    workdf = fulldf[["addressStreet", "addressZipCode", "bikesAvailable", "docksAvailable", "latitude", "longitude"]]
    workdf = workdf.assign(userDist='NV')
    #print(workdf.to_string())
    return workdf

def formatDf(workdf, userLocStationObj):
    workdf.userDist = [calcDist((stationLat, stationLon), userLocStationObj.coords)
                       for stationLat, stationLon in workdf[["latitude", "longitude"]].values]
    workdf = workdf.drop(workdf[workdf[userLocStationObj.bod] == 0].index)
    workdf = workdf.sort_values("userDist", ascending=True)
    workdf = workdf.reset_index(drop=True)
    workdf = workdf.loc[0:userLocStationObj.kStations-1]
    return workdf

userLoc = getUlocKstat()
stationDf = getStationData()
relevantStations = formatDf(stationDf, userLoc)
print(relevantStations)

m = folium.Map(location=[stationDf.latitude.mean(), stationDf.longitude.mean()], zoom_start=12, control_scale=True)
nodes = relevantStations[["latitude", "longitude"]]
MarkerCluster(nodes).add_to(m)
folium.Marker(location=[userLoc.coords[0], userLoc.coords[1]], popup="You are here", icon=folium.Icon(color="green")).add_to(m)
m.save("bigMap.html")
webbrowser.open("bigMap.html")
