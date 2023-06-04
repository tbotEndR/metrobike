import osmnx as ox
import folium
import geopandas as gpd
import requests

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
