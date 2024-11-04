import folium
import pandas as pd
import os

# Folder containing CSV files
csv_folder = 'data/'

# Initialize a Folium map centered on Australia
aus_map = folium.Map(location=[-25.2744, 133.7751], zoom_start=4, tiles="CartoDB positron",
                     attr="&copy; <a href='https://carto.com/attributions'>CARTO</a>")

# Loop through each CSV file in the folder
for filename in os.listdir(csv_folder):
    if filename.endswith('.csv'):
        # Load the CSV file
        file_path = os.path.join(csv_folder, filename)
        df = pd.read_csv(file_path)
        
        # Check if required columns exist
        if {'Longitude', 'Latitude', 'Postcode', 'Locality', 'State'}.issubset(df.columns):
            # Loop through each row in the CSV
            for _, row in df.iterrows():
                # Extract required data
                longitude = row['Longitude']
                latitude = row['Latitude']
                postcode = row['Postcode']
                locality = row['Locality']
                state = row['State']
                
                # Create an HTML table for the popup
                popup_html = f"""
                <table style="width: 200px; border: 1px solid black; border-collapse: collapse;">
                    <tr><th colspan="2" style="background-color: #f2f2f2;">{filename}</th></tr>
                    <tr><td><b>Locality</b></td><td>{locality}</td></tr>
                    <tr><td><b>Postcode</b></td><td>{postcode}</td></tr>
                    <tr><td><b>State</b></td><td>{state}</td></tr>
                </table>
                """
                
                # Add a marker for each location
                folium.Marker(
                    location=[latitude, longitude],
                    popup=folium.Popup(popup_html, max_width=250),
                    tooltip=f"{locality}, {state}"  # Shows locality and state on hover
                ).add_to(aus_map)

# Save the map as an HTML file
aus_map.save("australian_cities_map.html")
