import geopandas as gpd
import requests
from geopy import exc
from geopy.geocoders import Nominatim
from sys import exit

geolocator = Nominatim(user_agent="metrobike_application")
geocode = lambda query: geolocator.geocode("%s, Los Angeles County CA" % query)

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

def directions(startLat, startLon, destLat, destLon, mode="bicycle"):
    url = "https://route-and-directions.p.rapidapi.com/v1/routing"
    querystring = {"waypoints":f"{str(startLat)},{str(startLon)}|{str(destLat)},{str(destLon)}", "mode":mode}
    headers = {
	"X-RapidAPI-Key": "f5a6ad24fdmsh40bd4fffc865494p135019jsndaa4d4c1bd9b",
	"X-RapidAPI-Host": "route-and-directions.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)
    return response