import folium
import pandas as pd
import os
from folium.plugins import MarkerCluster

# Folder containing CSV files
csv_folder = 'data'

# Initialize a Folium map centered on Australia with CartoDB positron tiles
aus_map = folium.Map(location=[-25.2744, 133.7751], zoom_start=4, tiles="CartoDB positron",
                     attr="&copy; <a href='https://carto.com/attributions'>CARTO</a>")

# Add state borders using GeoJSON
# You can replace this URL with a path to a local GeoJSON file if needed
geojson_url = "data/state_borders.geojson"
folium.GeoJson(
    geojson_url,
    name="State Borders",
    style_function=lambda x: {
        'fillColor': 'transparent',
        'color': 'black',
        'weight': 2
    }
).add_to(aus_map)

# List of colors for markers; add more colors if needed
colors = ["blue", "green", "purple", "orange", "darkred", "cadetblue", "darkgreen", "darkpurple", "lightblue"]

# Loop through each CSV file in the folder
for idx, filename in enumerate(os.listdir(csv_folder)):
    if filename.endswith('.csv'):
        # Load the CSV file
        file_path = os.path.join(csv_folder, filename)
        df = pd.read_csv(file_path)
        
        # Check if required columns exist
        if {'Longitude', 'Latitude', 'Postcode', 'Locality', 'State'}.issubset(df.columns):
            # Assign a color for the current file and remove ".csv" extension from the name
            color = colors[idx % len(colors)]  # Cycle through colors if more files than colors
            clean_filename = filename.replace('.csv', '')

            # Create a MarkerCluster with color consistency for each CSV file
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
                <table style="width: 220px; border: 1px solid black; border-collapse: collapse;">
                    <tr><th colspan="2" style="background-color: #f2f2f2;">{clean_filename}</th></tr>
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
                
                # Add a CircleMarker to the file's MarkerCluster for each location
                folium.CircleMarker(
                    location=[latitude, longitude],
                    radius=8,  # Scalable size
                    color=color,
                    fill=True,
                    fill_color=color,
                    fill_opacity=0.7,
                    popup=folium.Popup(popup_html, max_width=250),
                    tooltip=f"{locality}, {state}"  # Shows locality and state on hover
                ).add_to(file_cluster)

# Add layer control to toggle clusters and state borders
folium.LayerControl().add_to(aus_map)

# Save the map as an HTML file
aus_map.save("australian_cities_map.html")
