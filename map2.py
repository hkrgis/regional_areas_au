from os import name
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from folium import IFrame



# Load datasets
postcode_data = pd.read_csv("data/australian_postcodes.csv")
regional_data = pd.read_csv("data/regional_postcodes.csv")

# Create a list to store markers and their search data
marker_list = []

# Prepare a color dictionary for categories
category_colors = {
    "Cities and Major Regional Centres":            "darkgreen",      # Blue
    "Regional Centres and Other Regional Areas":    "lightred",      # Green
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

# Add CartoDB positron basemap with a proper name
folium.TileLayer(
    tiles='https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
    attr='© OpenStreetMap contributors & CARTO',
    name="Light Map",
    subdomains='abcd'
).add_to(m)

# Create a dictionary to store MarkerClusters for each state
state_marker_clusters = {}

# Iterate over each state and its categories to plot the corresponding postcodes
for state in regional_data['state'].unique():
    # Filter data for the current state
    state_data = regional_data[regional_data['state'] == state]
    
    # Initialize a MarkerCluster for the state
    marker_cluster = MarkerCluster(
        name=state, 
        options={"showCoverageOnHover": False,
        "removeOutsideVisibleBounds": True,
        "spiderfyOnMaxZoom": True}).add_to(m)
    
    # Iterate over regions in the current state
    for _, region_row in state_data.iterrows():
        category = region_row['category']
        start_postcode = region_row['start_postcode']
        end_postcode = region_row['end_postcode']
        pin_color = category_colors.get(category, "#808080")  # Default to gray if category color is not defined
        
        # Filter the relevant postcodes within the given range
        relevant_postcodes = postcode_data[
            (postcode_data['postcode'] >= start_postcode) & 
            (postcode_data['postcode'] <= end_postcode)
        ]
        
        # Add each postcode as a marker on the map
        for _, row in relevant_postcodes.iterrows():
            # Filter out points with lat=0, long=0, or far from Australia
            if row['latitude'] == 0 or row['longitude'] == 0 or not (-44 < row['latitude'] < -10) or not (110 < row['longitude'] < 160):
                continue

    

            # Create a clean filename for the pop-up title
            clean_filename = row['locality']  # You can customize this further if needed
            
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
                <tr><td><b>Locality</b></td><td>{row['locality']}</td></tr>
                <tr><td><b>Postcode</b></td><td>{row['postcode']}</td></tr>
                <tr><td><b>LGA Region</b></td><td>{row['lgaregion']}</td></tr>
                <tr><td><b>State</b></td><td>{state}</td></tr>
                <tr class="category"><td><b>Category</b></td><td>{category}</td></tr>
                <tr><td colspan="2" style="text-align:center; padding-top: 5px;">
                    <a href="{directions_link}" target="_blank" style="color: #337ab7; text-decoration: none;">
                        Get directions (Google Maps)
                    </a>
                </td></tr>
            </table>
            """

            iframe = IFrame(popup_html, width=250, height=260)  # Adjust height as needed
            
            # folium.CircleMarker(
            #     location=(row['latitude'], row['longitude']),
            #     radius=6,  # Size of the pin
            #     color=pin_color,
            #     fill=True,
            #     fill_color=pin_color,
            #     fill_opacity=0.5,
            #     popup=folium.Popup(iframe, max_width=255)
            # ).add_to(marker_cluster)

            folium.Marker(
                location=(row['latitude'], row['longitude']),
                icon=folium.Icon(color=pin_color, icon='map-marker', prefix="glyphicon"),  # Custom symbol/icon
                popup=folium.Popup(iframe, max_width=255)
            ).add_to(marker_cluster)

            
    
    # Store the marker cluster for the state
    state_marker_clusters[state] = marker_cluster

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


# Add a layer control to toggle between the base map and the state marker clusters
folium.LayerControl(position="topright").add_to(m)

# Save the map as an HTML file
m.save("index.html")
print("Map saved as 'index.html'.")

# Add a "?" button with collapsible iframe at the bottom right
help_button_html = """
    <style>
        /* Help button style */
        #help-btn {
            position: fixed;
            bottom: 25px;
            right: 25px;
            width: 40px;
            height: 40px;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 50%;
            font-size: 20px;
            cursor: pointer;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            z-index: 9999; /* Ensure it's on top */
        }
        #help-btn:hover {
            background-color: #0056b3;
        }

        /* iFrame container style */
        #help-iframe-container {
            display: none;
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 60%;
            height: 70%;
            border: 1px solid #ccc;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            border-radius: 10px;
            overflow: hidden;
            background-color: white;
            z-index: 10000; /* Ensure it's above the button */
        }

        /* Close button style */
        #close-btn {
            position: absolute;
            top: 10px;
            right: 10px;
            width: 30px;
            height: 30px;
            background-color: #ff5c5c;
            color: white;
            border: none;
            border-radius: 50%;
            font-size: 20px;
            cursor: pointer;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        #close-btn:hover {
            background-color: #d43f3f;
        }

        /* iFrame style */
        #help-iframe-container iframe {
            width: 100%;
            height: 100%;
            border: none;
            padding-top: 40px; /* To leave space for the close button */
            box-sizing: border-box;
        }

        @media (max-width: 480px) {
            /* Further adjust the help button size and position for very small screens */
            #help-btn {
                width: 30px;
                height: 30px;
                font-size: 16px;
                bottom: 20px;  /* Adjust bottom position */
                right: 10px;  /* Adjust right position */
            }

            /* Further adjust the iframe container size for very small screens */
            #help-iframe-container {
                width: 90%;
                height: 70%;
            }

            /* Further adjust the iframe padding for very small screens */
            #help-iframe-container iframe {
                padding-top: 30px;
            }
        }
        
    </style>

    <div id="help-iframe-container">
        <button id="close-btn">&times;</button>
        <iframe id="help-iframe" src=""></iframe>
    </div>
    <button id="help-btn">?</button>

    <script>
        // Toggle the iframe container and load welcome.html when the help button is clicked
        document.getElementById("help-btn").addEventListener("click", function () {
            var iframeContainer = document.getElementById("help-iframe-container");
            var iframe = document.getElementById("help-iframe");
            
            // Check if the iframe is currently hidden or shown
            if (iframeContainer.style.display === "none" || iframeContainer.style.display === "") {
                // Dynamically set the iframe source to welcome.html when opening
                iframe.src = "templates/welcome.html";

                // Show the iframe container
                iframeContainer.style.display = "block";
            } else {
                // Hide the iframe container
                iframeContainer.style.display = "none";
            }
        });

        // Hide the iframe container when the close button is clicked
        document.getElementById("close-btn").addEventListener("click", function () {
            var iframeContainer = document.getElementById("help-iframe-container");
            iframeContainer.style.display = "none";
        });
    </script>
"""

# Append the help button and iframe container to the map HTML
with open("index.html", "a") as f:
    f.write(help_button_html)

print("Map updated with '?' help button!")

print('Added Welcome Page!')