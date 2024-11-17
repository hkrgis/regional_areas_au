import pandas as pd
import folium
from folium.plugins import MarkerCluster
from folium import IFrame

# Load datasets
postcode_data = pd.read_csv("data/australian_postcodes.csv")
regional_data = pd.read_csv("data/regional_postcodes.csv")

# Prepare a color dictionary for categories
category_colors = {
    "Category1": "#3498db",      # Blue
    "Category2": "#2ecc71",      # Green
    "Category3": "#e74c3c",      # Red
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

# Initialize map centered on Australia with a lighter tile
map_center = [-25.2744, 133.7751]  # Rough center of Australia
m = folium.Map(location=map_center, zoom_start=5, tiles='CartoDB positron')

# Add marker clustering for aggregation
marker_cluster = MarkerCluster().add_to(m)

# Iterate over each state and its categories to plot the corresponding postcodes
for state in regional_data['state'].unique():
    state_data = regional_data[regional_data['state'] == state]
    
    for _, region_row in state_data.iterrows():
        category = region_row['category']
        start_postcode = region_row['start_postcode']
        end_postcode = region_row['end_postcode']
        color = category_colors.get(category, "#808080")  # Default to gray if category color is not defined
        
        # Filter the relevant postcodes within the given range
        relevant_postcodes = postcode_data[
            (postcode_data['postcode'] >= start_postcode) & 
            (postcode_data['postcode'] <= end_postcode)
        ]
        
        # Add each postcode as a marker on the map, considering the conditions
        for _, row in relevant_postcodes.iterrows():
            # Filter out points with lat=0, long=0, or far from Australia
            if row['latitude'] == 0 or row['longitude'] == 0 or not (-44 < row['latitude'] < -10) or not (110 < row['longitude'] < 160):
                continue

            # Create a clean filename for the pop-up title
            clean_filename = row['locality']  # You can customize this further if needed
            
            # Google Maps directions link
            directions_link = f"https://www.google.com/maps/dir/?api=1&destination={row['latitude']},{row['longitude']}&travelmode=driving"
            
            # Create an HTML table for the popup with directions link
            popup_html = f"""
            <style>
                table {{
                    width: 220px; 
                    border: 1px solid black; 
                    border-collapse: collapse;
                    font-family: Arial, sans-serif;
                }}
                th {{
                    background-color: #f2f2f2;
                    text-align: left;
                    padding: 8px;
                }}
                td {{
                    padding: 8px;
                    border: 1px solid black;
                }}
                tr:nth-child(even) {{
                    background-color: #f9f9f9;
                }}
            </style>
            <table>
                <tr><th colspan="2">{clean_filename}</th></tr>
                <tr><td><b>Locality</b></td><td>{row['locality']}</td></tr>
                <tr><td><b>Postcode</b></td><td>{row['postcode']}</td></tr>
                <tr><td><b>State</b></td><td>{state}</td></tr>
                <tr><td colspan="2" style="text-align:center; padding-top: 5px;">
                    <a href="{directions_link}" target="_blank" style="color: #337ab7; text-decoration: none;">
                        Get directions (Drive)
                    </a>
                </td></tr>
            </table>
            """
            
            iframe = IFrame(popup_html, width=240, height=180)  # Adjust height as needed
            
            folium.CircleMarker(
                location=(row['latitude'], row['longitude']),
                radius=7,  # Size of the pin
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.7,
                popup=folium.Popup(iframe, max_width=240)
            ).add_to(marker_cluster)

# Add state polygons with fill colors and meaningful names
state_geojson = 'data/states.geojson'

# Load GeoJSON for states with meaningful naming
folium.GeoJson(
    state_geojson,
    name='State Borders',  # Giving a meaningful name to the GeoJson layer
    style_function=lambda feature: {
        'fillColor': state_colors.get(feature['properties']['STATE_NAME'], '#ffffff'),
        'color': 'black',
        'weight': 1,
        'fillOpacity': 0.5
    }
).add_to(m)

# Add a layer control to toggle between the base map and satellite imagery
folium.LayerControl().add_to(m)

# Save the map as an HTML file
m.save("index.html")
