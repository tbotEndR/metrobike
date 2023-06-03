import geopandas as gpd
import requests

url = "https://bikeshare.metro.net/stations/json/"
r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
"""Have to import using requests because the geopandas.read_file(url) doesn't allow for
specifying a request header, which results in a 403 denied response"""

data = r.json()
gdf = gpd.GeoDataFrame.from_features(data)
print(gdf)    