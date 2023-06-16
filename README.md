# metrobike
Applied Data Science Project using live GeoJSON data from the LA Metro Bike service.
The program retrieves the current LA Metro Bike Station data and uses it to
  - display the k nearest stations with available bikes
  - display the k nearest stations with available docks
  - plan a route and include a suitable bike and dock along the way
  
The points are drawn onto a map which is then opened in a browser.

This was my first ever project using Python as well as the first time that I used Git.

# DEPENENCIES
This project uses Folium, Geopy as well as Geopandas. Please make sure to install these packages according to the instructions on their respective websites.
You will also need a valid Rapid-API Key to insert in the directions() function in ext_requests.py:

> headers = {"X-RapidAPI-Key": "INSERT YOUR KEY HERE","X-RapidAPI-Host": "route-and-directions.p.rapidapi.com" }

### FOLIUM:
https://python-visualization.github.io/folium/installing.html

### GEOPY:
https://geopy.readthedocs.io/en/stable/#installation

### GEOPANDAS:
https://geopandas.org/en/stable/getting_started.html
