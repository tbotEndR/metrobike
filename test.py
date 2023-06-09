import osmnx as ox
import folium
import geopandas as gpd
import requests
import webbrowser

<<<<<<< HEAD
#G = ox.graph_from_bbox(34.1879, 33.8983, -118.1576, -118.5287, network_type='bike')
#ox.save_graphml(G, "LA.graphml")
G = ox.load_graphml("LA.graphml")
fig, ax = ox.plot_graph(G, figsize=(10, 10), node_size=0, edge_color='y', edge_linewidth=0.2)
print(G)

url = "https://bikeshare.metro.net/stations/json/"
r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
#GeoJSON import using requests because the geopandas.read_file(url) doesn't allow for
##specifying a request header, which results in a 403 denied response

data = r.json()
fulldf = gpd.GeoDataFrame.from_features(data)
workdf = fulldf[["addressStreet", "addressZipCode", "bikesAvailable", "docksAvailable", "latitude", "longitude"]]
workdf['distToUser'] = 'Null'

#m = folium.Map(location=[workdf.latitude.mean(), workdf.longitude.mean()], zoom_start=14, control_scale=True)

#I know iterating over pandas data frames is bad practide but I'm tired and just need this to work right now
for i, row in workdf.iterrows():
    stationNode = (row['latitude'], row['longitude'])
    ox.get_near
=======
class Map:
    def __init__(self, center, zoom_start):
        self.center = center
        self.zoom_start = zoom_start
    
    def showMap(self):
        my_map = folium.Map(location = self.center, zoom_start = self.zoom_start)
        my_map.save("map.html")
        webbrowser.open("map.html")

def getUserBikes():
    userLoc = input("What is your current location? (Default central LA)\n") or "Mid-City, Los Angeles"
    kBikeStations = int(input("How many bikestations are you seaching for? (Default 1)\n") or 1)

def getNetworkGrid():
    try:
        G = ox.load_graphml("LA.graphml")
    except FileNotFoundError:
        G = ox.graph_from_bbox(34.1879, 33.8983, -118.1576, -118.5287, network_type='bike')
        ox.save_graphml(G, "LA.graphml")

def getStationData():
    url = "https://bikeshare.metro.net/stations/json/"
    r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    #GeoJSON import using requests because the geopandas.read_file(url) doesn't allow for
    ##specifying a request header, which results in a 403 denied response
    data = r.json()
    fulldf = gpd.GeoDataFrame.from_features(data)
    return fulldf[["addressStreet", "addressZipCode", "bikesAvailable", "docksAvailable", "latitude", "longitude"]]


stationDf = getStationData()
print(stationDf)

m = folium.Map(location=[stationDf.latitude.mean(), stationDf.longitude.mean()], zoom_start=14, control_scale=True)
m.save("bigMap.html")
webbrowser.open("bigMap.html")
>>>>>>> addUserInput
