from os import name
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from folium import IFrame
from folium import plugins


# Load dataset
postcode_data = pd.read_csv("data/geocoded_postcodes.csv")

# Create a list to store markers and their search data
marker_list = []

# Prepare a color dictionary for categories
category_colors = {
    "Cities and Major Regional Centres": "darkgreen",  # Blue
    "Regional Centres and Other Regional Areas": "lightred",  # Green
    "Category3": "#e74c3c",  # Red
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
m = folium.Map(location=map_center, zoom_start=4, control_scale=True, tiles=None)


# Add Hybrid Imagery basemap
folium.TileLayer(
    tiles="https://{s}.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
    attr="© Google",
    name="Satellite Hybrid Imagery",
    subdomains=["mt0", "mt1", "mt2", "mt3"]
).add_to(m)

# Add CartoDB Dark Matter basemap
folium.TileLayer(
    tiles='https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
    attr='© OpenStreetMap contributors & CARTO',
    name='Dark Map',
    subdomains='abcd'
).add_to(m)

# Add CartoDB positron basemap
folium.TileLayer(
    tiles='https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
    attr='© OpenStreetMap contributors & CARTO',
    name="Light Map",
    subdomains='abcd'
).add_to(m)


# Create a dictionary to store MarkerClusters for each state
state_marker_clusters = {}

# Iterate over each state to plot postcodes
for state in postcode_data['state'].unique():
    # Filter data for the current state
    state_data = postcode_data[postcode_data['state'] == state]
    
    # Initialize a MarkerCluster for the state
    marker_cluster = MarkerCluster(
        name=state,
        options={"showCoverageOnHover": False, "removeOutsideVisibleBounds": True, "spiderfyOnMaxZoom": True}
    ).add_to(m)
    
    # Iterate over postcodes in the current state
    for _, row in state_data.iterrows():
        category = row['category']
        pin_color = category_colors.get(category, "#808080")  # Default to gray if category color is not defined
        
        # Filter out points with lat=0, long=0, or far from Australia
        if row['latitude'] == 0 or row['longitude'] == 0 or not (-44 < row['latitude'] < -10) or not (110 < row['longitude'] < 160):
            continue

        # Create a clean filename for the pop-up title
        clean_filename = row['place_name']  # You can customize this further if needed
        
        # Add marker data to search list for search functionality
        marker_list.append({
            'lat': row['latitude'],
            'lon': row['longitude'],
            'popup': clean_filename,  # Locality Name (or any other data you prefer)
            'postcode': row['postcode']  # Postcode for search functionality
        })
        
        # Google Maps directions link
        directions_link = f"https://www.google.com/maps/dir/?api=1&destination={row['latitude']},{row['longitude']}&travelmode=driving"
        
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
            <tr><td><b>Locality</b></td><td>{row['place_name']}</td></tr>
            <tr><td><b>Postcode</b></td><td>{row['postcode']}</td></tr>
            <tr><td><b>State</b></td><td>{state}</td></tr>
            <tr class="category"><td><b>Category</b></td><td>{category}</td></tr>
            <tr><td colspan="2" style="text-align:center; padding-top: 5px;">
                <a href="{directions_link}" target="_blank" style="color: #337ab7; text-decoration: none;">
                    Get directions (Google Maps)
                </a>
            </td></tr>
        </table>
        """

        iframe = IFrame(popup_html, width=250, height=200)  # Adjust height as needed
        
        # Add the marker to the cluster
        folium.Marker(
            location=(row['latitude'], row['longitude']),
            icon=folium.Icon(color=pin_color, icon='map-marker', prefix="glyphicon"),
            popup=folium.Popup(iframe, max_width=255)
        ).add_to(marker_cluster)

    # Add the cluster to the LayerControl
    state_marker_clusters[state] = marker_cluster


# Create a FeatureGroup for state polygons
state_polygons_group = folium.FeatureGroup(name='State Borders').add_to(m)

# Add state polygons with fill colors and meaningful names (optional, can be replaced by another GeoJSON)
state_geojson = 'data/states.geojson'
folium.GeoJson(
    state_geojson,
    name='State Borders', 
    style_function=lambda feature: {
        'fillColor': state_colors.get(feature['properties']['STATE_NAME'], '#ffffff'),
        'color': 'black',
        'weight': 1,
        'fillOpacity': 0.5
    }
).add_to(state_polygons_group)




# Add a LayerControl to toggle state postcodes
folium.LayerControl(position="topright").add_to(m)

# Save the map as an HTML file
m.save("index.html")
print("Map saved as 'index.html'.")
