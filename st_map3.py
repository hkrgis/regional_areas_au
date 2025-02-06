import pandas as pd
import geopandas as gpd
import folium
import streamlit as st
import random

# Load the CSV file
df = pd.read_csv('data/postcode_updated.csv')

# Load the GeoJSON file
states = gpd.read_file('data/states2.geojson')


m = folium.Map(location=[df['latitude'].mean(), df['longitude'].mean()], zoom_start=6)
for index, row in df.iterrows():
    popup_text = f"Place: {row['place_name']}<br>State: {row['state']}<br>LGA: {row['lga_name']}<br>Category: {row['category']}"
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        popup=folium.Popup(popup_text, max_width=300),
        tooltip=row['postcode']
    ).add_to(m)

# Function to generate a random color with 50% transparency
def random_color():
    r = lambda: random.randint(0,255)
    return f'rgba({r()}, {r()}, {r()}, 0.5)'

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

# Color each state
folium.GeoJson(
    states,
    name='State Borders', 
    style_function=lambda feature: {
        'fillColor': state_colors.get(feature['properties']['STATE_NAME'], '#ffffff'),
        'color': 'black',
        'weight': 1,
        'fillOpacity': 0.5
    }
).add_to(m)

def main():
    st.title("Postcode Map with State Colors")
    
    # Convert folium map to HTML
    map_html = m.get_root().render()
    
    # Display the map in Streamlit
    st.components.v1.html(map_html, width=800, height=600)

if __name__ == "__main__":
    main()