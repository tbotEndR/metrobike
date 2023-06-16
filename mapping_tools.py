import folium
from geopy import distance

def calcDist(stationLoc, userLoc):
    try:
        return int(distance.distance((stationLoc[0], stationLoc[1]),(userLoc[0], userLoc[1])).meters)
    except:
        return 0
    
def plotRoute(routeResponse, map):
    mls = routeResponse.json()['features'][0]['geometry']['coordinates']
    points = [(i[1], i[0]) for i in mls[0]]
    folium.PolyLine(points, weight=5, opacity=1).add_to(map)

def toMarker(location, type, map):
    match type:
        case "bikes":
            html = """{0}<br><br>Available bikes: {1}""".format(location.name, location.bikes)
            iconType = "bicycle"
            color = "darkblue"
        case "docks":
            html = """{0}<br><br>Available docks: {1}""".format(location.name, location.docks)
            iconType = "charging-station"
            color = "lightred"
        case "start":
            html = """Your location:<br>{0}<br>""".format(location.name)
            iconType = "user-circle"
            color = "green"
        case "destination":
            html = """Your destination:<br>{0}<br>""".format(location.name)
            iconType = "map-pin"
            color = "green"

    iframe = folium.IFrame(html, figsize=(3,2))
    popup = folium.Popup(iframe, max_width=200)
    folium.Marker(location=location.coordinates, popup=popup, icon=folium.Icon(color=color, prefix='fa', icon=iconType)).add_to(map)