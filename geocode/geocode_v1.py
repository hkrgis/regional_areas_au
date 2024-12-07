from numpy import place
import requests
import pandas as pd
import time

# Mapbox API key
MAPBOX_API_KEY = "pk.eyJ1IjoiaGsyMzUiLCJhIjoiY200ZHFzNnZrMDJyODJtcHp3NWt6ZWFsMSJ9.EfNBdnT-gxO5fZBxRyHWSw"

# Input and output CSV file paths
INPUT_CSV = "immi_regional_areas.csv"  # Replace with your CSV file containing postcodes, state, and category
OUTPUT_CSV = "geocoded_postcodes.csv"

# Function to geocode a postcode
def geocode_postcode(postcode):
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{postcode}.json"
    params = {
        "access_token": MAPBOX_API_KEY,
        "country": "AU",  # Restrict to Australia
        "limit": 10,      # Maximum results per query
        "fuzzyMatch": "true",  # Enable fuzzy matching
        "autocomplete": "true",  # Enable autocomplete
    }

    retries = 10  # Number of retries in case of rate limiting
    for attempt in range(retries):
        response = requests.get(url, params=params)
        
        # If rate limit exceeded, wait and retry
        if response.status_code == 429:
            print(f"Rate limit exceeded for postcode {postcode}. Retrying in {2 ** attempt} seconds...")
            time.sleep(4 ** attempt)  # Exponential backoff for retries
            continue
        elif response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()  # Raise error for other status codes

    raise Exception(f"Failed to geocode postcode {postcode} after {retries} attempts.")

# Function to extract locality or place data, matching the input postcode
def extract_context_data(data, postcode):
    results = []
    for feature in data.get("features", []):
        coordinates = feature["geometry"]["coordinates"]
        place_name = None
        is_postcode_matched = False

        # Check if "postcode" in context matches input
        for context in feature.get("context", []):
            if "postcode" in context.get("id", "") and context.get("text") == str(postcode):
                is_postcode_matched = True

        # If postcode matches, extract "locality" or "place"
        if is_postcode_matched:
            for context in feature.get("context", []):
                if "locality" in context.get("id", ""):
                    place_name = context.get("text")
                    break
            if not place_name:
                for context in feature.get("context", []):
                    if "place" in context.get("id", ""):
                        place_name = context.get("text")
                        break

        # Add the result if a name is found and the postcode matches
        if place_name:
            results.append({
                "postcode": postcode,
                "latitude": coordinates[1],
                "longitude": coordinates[0],
                "place_name": place_name,
            })
            print(f"{place_name} of {postcode}")
    return results

# Function to make multiple variations of a query
def generate_exhaustive_queries(postcode):
    return [postcode, f"{postcode}, Australia"]  # Add more variations if needed

# Read the input CSV
df = pd.read_csv(INPUT_CSV)

# Create a DataFrame to store the results
output_data = []

# Process each row in the CSV
for index, row in df.iterrows():
    start_postcode = row.get("start_postcode")  # Replace with actual column name for start_postcode
    end_postcode = row.get("end_postcode")      # Replace with actual column name for end_postcode
    state = row.get("state")                     # Add state
    category = row.get("category")               # Add category

    # Ensure that start_postcode and end_postcode are valid integers
    if start_postcode is not None and end_postcode is not None:
        try:
            start_postcode = int(start_postcode)
            end_postcode = int(end_postcode)

            # Generate the range of postcodes from start to end
            for postcode in range(start_postcode, end_postcode + 1):
                try:
                    # Query variations for each postcode
                    queries = generate_exhaustive_queries(postcode)
                    for query in queries:
                        geocode_data = geocode_postcode(query)
                        geocode_results = extract_context_data(geocode_data, postcode)
                        for result in geocode_results:
                            result["state"] = state  # Add state to the result
                            result["category"] = category  # Add category to the result
                            result["start_postcode"] = start_postcode  # Add start_postcode
                            result["end_postcode"] = end_postcode  # Add end_postcode
                            output_data.append(result)  # Append result to output list
                except Exception as e:
                    print(f"Error processing postcode {postcode}: {e}")
        except ValueError:
            print(f"Invalid postcode range for start_postcode: {start_postcode} or end_postcode: {end_postcode}. Skipping row.")
    else:
        print(f"Missing start_postcode or end_postcode for row {index}. Skipping row.")

# Create a DataFrame and deduplicate by "place_name"
output_df = pd.DataFrame(output_data).drop_duplicates(subset=["place_name"])

# Save results to a new CSV
output_df.to_csv(OUTPUT_CSV, index=False)

print(f"Geocoding completed. Results saved to {OUTPUT_CSV}.")
