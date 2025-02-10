from os import name
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from folium import IFrame
from folium import plugins
import matplotlib.colors as mcolors



# Load dataset
postcode_data = pd.read_csv("data/postcode_updated.csv")

# Prepare a color dictionary for categories
category_colors = {
    "Cities and major regional centres": mcolors.to_hex("purple"),
    "Regional centres and other regional areas": mcolors.to_hex("lightcoral"), 
    "Category3": mcolors.to_hex("gray"), 
}

# Prepare a color dictionary for states
state_colors = {
    "New South Wales": "#add8e6",
    "Victoria": "#98fb98",  
    "Queensland": "#ffcccb",
    "Western Australia": "#ffe4e1",
    "South Australia": "#fffacd",
    "Tasmania": "#ffb6c1",
    "Northern Territory": "#d3d3d3",
    "Australian Capital Territory": "#e0ffff",
}

# Initialize map centered on Australia
map_center = [-25.2744, 133.7751]  # Rough center of Australia
m = folium.Map(location=map_center, zoom_start=4, control_scale=True, tiles=None, max_zoom=4)

# These coordinates are adjusted to include a small buffer around the mainland and Tasmania
australia_bounds = [
    [-47.0, 107.8],  # Southwest corner with buffer
    [-6.6, 162]   # Northeast corner with buffer
]
# Set maxBounds with the buffer to limit the map view to Australia with some extra space
m.fit_bounds(australia_bounds)  # This ensures the map initially fits within these bounds
m.options['maxBounds'] = australia_bounds  # This limits zooming outside these bounds

# Print status
print(f"Bounds set to {australia_bounds}")

# Add basemaps
basemaps = {}

# Add CartoDB positron basemap
basemaps['Light Map'] = folium.TileLayer(
    tiles='https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
    attr='© OpenStreetMap contributors & CARTO',
    name="Light Map",
    subdomains='abcd'
).add_to(m)

# Add CartoDB Dark Matter basemap
basemaps['Dark Map'] = folium.TileLayer(
    tiles='https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
    attr='© OpenStreetMap contributors & CARTO',
    name='Dark Map',
    subdomains='abcd'
).add_to(m)

# Add Hybrid Imagery basemap
basemaps['Satellite Hybrid Imagery'] = folium.TileLayer(
    tiles="https://{s}.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
    attr="© Google",
    name="Hybrid Imagery",
    subdomains=["mt0", "mt1", "mt2", "mt3"]
).add_to(m)

# Create a dictionary to store MarkerClusters for each state
state_marker_clusters = {}

# Helper function to format postcode to four digits
def format_postcode(postcode):
    return f"{postcode:04d}"


# Iterate over each state to plot postcodes
for state in postcode_data['state'].unique():
    # Filter data for the current state
    state_data = postcode_data[postcode_data['state'] == state]
    
    
    # Initialize a MarkerCluster for the state
    marker_cluster = MarkerCluster(
        name=state,
        options={"showCoverageOnHover": False, 
                 "removeOutsideVisibleBounds": True, 
                 "spiderfyOnMaxZoom": True,
                 "maxClusterRadius": 160,  # Adjust the cluster size
                }
    ).add_to(m)
    
    # Iterate over postcodes in the current state
    for _, row in state_data.iterrows():
        category = row['category']

        pin_color = category_colors.get(category, "gray")  # Default to gray if category color is not defined
        
        # Filter out points with lat=0, long=0, or far from Australia
        if row['latitude'] == 0 or row['longitude'] == 0 or not (-44 < row['latitude'] < -10) or not (110 < row['longitude'] < 160):
            continue

        # Create a clean filename for the pop-up title
        clean_filename = row['place_name']  # You can customize this further if needed
        
        # Google Maps directions link
        directions_link = f"https://www.google.com/maps/dir/?api=1&destination={row['latitude']},{row['longitude']}&travelmode=driving"

        # Format postcode to ensure it's four digits
        formatted_postcode = format_postcode(int(row['postcode']))  # Assuming postcode is stored as a number or string
        
        # Create an HTML table for the popup with directions link
        popup_html = f"""
        <style>
            table {{
                width: 100%;
                border: 1px solid black; 
                border-collapse: collapse;
                font-family: Arial, sans-serif;
                font-size: 11px;  /* Reduced font size */
                overflow: hidden;
            }}
            th {{
                background-color: #f2f2f2;
                text-align: left;
                padding: 5px;
                font-size: 13px;  /* Slightly larger for headers */
            }}
            td {{
                padding: 8px;
                border: 1px solid black;
            }}
            tr:nth-child(even) {{
                background-color: #e6ffff;
            }}
            .category {{
                font-size: 10px;  /* Set the font size for Category to 10px */
            }}
        </style>
        <table>
            <tr><th colspan="2">{clean_filename} </th></tr>
            <tr><td><b>Postcode</b></td><td>{formatted_postcode}</td></tr>
            <tr><td><b>LGA</b></td><td>{row['lga_name']}</td></tr>
            <tr><td><b>State</b></td><td>{state}</td></tr>
            <tr class="category"><td><b>Category</b></td><td>{category}</td></tr>
            <tr><td colspan="2" style="text-align:center; padding-top: 5px;">
                <a href="{directions_link}" target="_blank" style="color: #337ab7; text-decoration: none;">
                    Get directions (Google Maps)
                </a>
            </td></tr>
            <tr><td colspan="2" style="text-align:center; padding-top: 5px;">
                <a href="http://hkrgis.notion.site" target="_blank" style="color: #7FA9D6; text-decoration: none; font-style: italic;">
                    More about this map
                </a>
            </td></tr>
        </table>
        """

        iframe = IFrame(popup_html, width=250, height=230)  # Adjust height as needed
        
        # Add the marker to the cluster
        tmpMarker = folium.Marker(
            location=(row['latitude'], row['longitude']),
            popup=folium.Popup(iframe, max_width=250)
        ).add_to(marker_cluster)

        plugins.BeautifyIcon(
            icon='leaf', 
            border_color=pin_color, 
        ).add_to(tmpMarker)

    # Add the cluster to the LayerControl
    state_marker_clusters[state] = marker_cluster


# Create a FeatureGroup for state polygons
state_polygons_group = folium.FeatureGroup(name='State Borders').add_to(m)

# Add state polygons with fill colors and meaningful names (optional, can be replaced by another GeoJSON)
state_geojson = 'data/states2.geojson'
folium.GeoJson(
    state_geojson,
    name='State Borders', 
    style_function=lambda feature: {
        'fillColor': state_colors.get(feature['properties']['STATE_NAME'], '#ffffff'),
        'color': 'black',
        'weight': 1,
        'fillOpacity': 0.4
    }
).add_to(state_polygons_group)

# Custom Layer Control with groups for multi-select
basemaps_layer_control = plugins.GroupedLayerControl(
    groups={
        'Basemaps': list(basemaps.values()), 
    
    },
    exclusive_groups=['Basemaps'],
    collapsed=True  # Optional: start with the control expanded
)
basemaps_layer_control.add_to(m)

# Custom Layer Control with groups for multi-select
postcodes_layer_control = plugins.GroupedLayerControl(
    groups={
        'State Postcodes': list(state_marker_clusters.values()),
        'State Borders': [state_polygons_group],
    },
    exclusive_groups=[],
    collapsed=True  # Optional: start with the control expanded
)
postcodes_layer_control.add_to(m)


# Save the map as an HTML file
m.save("index.html")
print("Map saved as 'index.html'.")



"""
- change zoom based on browser and mobile devices
- Layer control width and text 
- Marker size

"""

# Manually edit the generated HTML file to add responsive meta tags and CSS
with open("index.html", "r") as file:
    content = file.read()

# Add meta tags and CSS for responsiveness with adjustments for Marker Pins
responsive_content = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        html, body {
            width: 100%;
            height: 100%;
            margin: 0;
            padding: 0;
        }
        #map {
            width: 100%;
            height: 100vh; 
        }

        @media (max-width: 600px) {
            #map {
                height: 80vh; 
            }
            .folium-popup {
                max-width: 150px;
                font-size: 10px; /* Smaller text for better fit on mobile */ 
            }
            .leaflet-container {
                zoom: 0.75; 
            }
            .leaflet-control-layers {
                max-width: 180px; 
                font-size: 10px; 
                max-height: 70vh; /* Limit height to viewport size */
                overflow-y: auto; 
            }
        }
        @media (min-width: 601px) and (max-width: 1024px) {
            .leaflet-container {
                zoom: 1.0; 
            }
            .leaflet-control-layers {
                max-width: 200px; 
                font-size: 10px; 
                max-height: 80vh; /* Limit height to viewport size */
                overflow-y: auto; 
            }
        
        }
        @media (min-width: 1025px) {
            .leaflet-control-layers {
                max-width: 300px; 
                font-size: 12px; 
                max-height: 90vh; /* Limit height to viewport size */
                overflow-y: auto; 
            }
        }
    </style>
</head>
<body>
""" + content + """
</body>
</html>
"""

with open("index.html", "w") as file:
    file.write(responsive_content)

print("Map saved again as 'index.html'.")