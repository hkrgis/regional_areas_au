import folium
import pandas as pd
import os
from folium.plugins import MarkerCluster

# Folder containing CSV files
csv_folder = 'data/'

# Initialize a Folium map centered on Australia with a light theme
aus_map = folium.Map(location=[-25.2744, 133.7751], zoom_start=4, tiles="CartoDB positron",
                     attr="&copy; <a href='https://carto.com/attributions'>CARTO</a>")

# Add state borders using GeoJSON and fill states with different colors
geojson_url = "data/states.geojson"
# Define colors for each state
state_colors = {
    "New South Wales": "lightblue",
    "Victoria": "lightgreen",
    "Queensland": "lightsalmon",
    "Western Australia": "lightcoral",
    "South Australia": "lightpink",
    "Tasmania": "lightgrey",
    "Australian Capital Territory": "lightcyan",
    "Northern Territory": "lightgoldenrodyellow"
}

# Function to style each state based on its name
def style_function(feature):
    state_name = feature['properties']['STATE_NAME']
    return {
        'fillColor': state_colors.get(state_name, 'lightgray'),  # Default to lightgray if state not found
        'color': 'black',           # Border color
        'weight': 2,
        'fillOpacity': 0.25          # Opacity level
    }

# Add GeoJSON layer for states with the defined style
folium.GeoJson(
    geojson_url,
    name="State Borders",
    style_function=style_function
).add_to(aus_map)

# List of colors for markers; add more colors if needed
marker_colors = ["blue", "green", "purple", "orange", "darkred", "cadetblue", "darkgreen", "darkpurple", "lightblue"]

# Loop through each CSV file in the folder
for idx, filename in enumerate(os.listdir(csv_folder)):
    if filename.endswith('.csv'):
        # Load the CSV file
        file_path = os.path.join(csv_folder, filename)
        df = pd.read_csv(file_path)
        
        # Check if required columns exist
        if {'Longitude', 'Latitude', 'Postcode', 'Locality', 'State'}.issubset(df.columns):
            # Assign a color for the current file and remove ".csv" extension from the name
            marker_color = marker_colors[idx % len(marker_colors)]  # Color remains constant for each CSV file
            clean_filename = filename.replace('.csv', '')

            # Create a MarkerCluster
            file_cluster = MarkerCluster(name=clean_filename).add_to(aus_map)

            # Loop through each row in the CSV
            for _, row in df.iterrows():
                # Extract required data
                longitude = row['Longitude']
                latitude = row['Latitude']
                postcode = row['Postcode']
                locality = row['Locality']
                state = row['State']
                
                # Generate "Get directions" link with user location as starting point
                directions_link = f"https://www.google.com/maps/dir/?api=1&origin=My+Location&destination={latitude},{longitude}&travelmode=driving"
                
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
                    <tr><td><b>Locality</b></td><td>{locality}</td></tr>
                    <tr><td><b>Postcode</b></td><td>{postcode}</td></tr>
                    <tr><td><b>State</b></td><td>{state}</td></tr>
                    <tr><td colspan="2" style="text-align:center; padding-top: 5px;">
                        <a href="{directions_link}" target="_blank" style="color: #337ab7; text-decoration: none;">
                            Get directions (Drive)
                        </a>
                    </td></tr>
                </table>
                """
                
                # Create a custom icon with a circle and "i"
                icon_html = f"""
                <div style="background-color: {marker_color}; border-radius: 50%; width: 30px; height: 30px; text-align: center; line-height: 30px; color: white; font-weight: bold; font-size: 18px;">
                    i
                </div>
                """
                
                # Add a Marker with a custom DivIcon
                folium.Marker(
                    location=[latitude, longitude],
                    icon=folium.DivIcon(html=icon_html),  # Custom DivIcon with "i"
                    popup=folium.Popup(popup_html, max_width=250),
                    tooltip=f"{locality}, {state}"  # Shows locality and state on hover
                ).add_to(file_cluster)

# Add layer control to toggle clusters and state borders
folium.LayerControl().add_to(aus_map)

# Save the map as an HTML file
aus_map.save("index.html")
