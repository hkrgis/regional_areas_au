import folium
import pandas as pd
import os
import random

# Folder containing CSV files
csv_folder = 'data/'

# List of colors for markers; add more colors if needed
colors = ["blue", "green", "purple", "orange", "darkred", "cadetblue", "darkgreen", "darkpurple", "lightblue"]

# Initialize a Folium map centered on Australia
aus_map = folium.Map(location=[-25.2744, 133.7751], zoom_start=4, tiles="CartoDB positron",
                     attr="&copy; <a href='https://carto.com/attributions'>CARTO</a>")

# Loop through each CSV file in the folder
for idx, filename in enumerate(os.listdir(csv_folder)):
    if filename.endswith('.csv'):
        # Load the CSV file
        file_path = os.path.join(csv_folder, filename)
        df = pd.read_csv(file_path)
        
        # Check if required columns exist
        if {'Longitude', 'Latitude', 'Postcode', 'Locality', 'State'}.issubset(df.columns):
            # Assign a color for the current file
            color = colors[idx % len(colors)]  # Cycle through colors if more files than colors
            
            # Loop through each row in the CSV
            for _, row in df.iterrows():
                # Extract required data
                longitude = row['Longitude']
                latitude = row['Latitude']
                postcode = row['Postcode']
                locality = row['Locality']
                state = row['State']
                
                # Generate "Get directions" link
                directions_link = f"https://www.google.com/maps/dir/?api=1&destination={latitude},{longitude}"
                
                # Create an HTML table for the popup with directions link
                popup_html = f"""
                <table style="width: 220px; border: 1px solid black; border-collapse: collapse;">
                    <tr><th colspan="2" style="background-color: #f2f2f2;">{filename}</th></tr>
                    <tr><td><b>Locality</b></td><td>{locality}</td></tr>
                    <tr><td><b>Postcode</b></td><td>{postcode}</td></tr>
                    <tr><td><b>State</b></td><td>{state}</td></tr>
                    <tr><td colspan="2" style="text-align:center; padding-top: 5px;">
                        <a href="{directions_link}" target="_blank" style="color: #337ab7; text-decoration: none;">
                            Get directions
                        </a>
                    </td></tr>
                </table>
                """
                
                # Add a CircleMarker with customized color and size
                folium.CircleMarker(
                    location=[latitude, longitude],
                    radius=8,  # Scalable size
                    color=color,
                    fill=True,
                    fill_color=color,
                    fill_opacity=0.7,
                    popup=folium.Popup(popup_html, max_width=250),
                    tooltip=f"{locality}, {state}"  # Shows locality and state on hover
                ).add_to(aus_map)

# Save the map as an HTML file
aus_map.save("australian_cities_map.html")
