import pandas as pd
import folium

# Load the transit history data
compass_card_history = pd.read_csv('Data/CompassCardHistory.csv')
translink_transit_stops = pd.read_csv('Data/TranslinkTransitStops.csv')

# Extract locations from Compass Card History
def extract_location(transaction):
    if "Bus Stop" in transaction:
        return transaction.split("Bus Stop ")[1]
    elif "Stn" in transaction:
        return transaction.split(" at ")[1].replace(" Stn", "")
    return None

compass_card_history['location'] = compass_card_history['Transaction'].apply(extract_location)

# Separate bus stops and train stations
bus_stops = compass_card_history[compass_card_history['location'].str.isdigit()]
train_stations = compass_card_history[~compass_card_history['location'].str.isdigit()]

# Ensure data types match for merging
compass_card_history['location'] = compass_card_history['location'].astype(str)
translink_transit_stops['stop_code'] = translink_transit_stops['stop_code'].fillna(0).astype(int).astype(str)

# Match bus stops by stop_code
bus_stops = bus_stops.merge(
    translink_transit_stops,
    left_on='location',
    right_on='stop_code',
    how='inner'
)

# Match train stations by stop_name
train_stations = train_stations.merge(
    translink_transit_stops[translink_transit_stops['stop_code'] == 99999],
    left_on='location',
    right_on='stop_name',
    how='inner'
)

# Combine data
visited_locations = pd.concat([
    bus_stops[['stop_lat', 'stop_lon']],
    train_stations[['stop_lat', 'stop_lon']]
])

# Create a heatmap
m = folium.Map(location=[visited_locations['stop_lat'].mean(), visited_locations['stop_lon'].mean()], zoom_start=12)

for _, row in visited_locations.iterrows():
    folium.CircleMarker(
        location=[row['stop_lat'], row['stop_lon']],
        radius=5,
        color='blue',
        fill=True,
        fill_color='blue',
        fill_opacity=0.6
    ).add_to(m)

# Save the heatmap to an HTML file
m.save('Data/visited_locations_heatmap.html')

print("Heatmap saved as 'visited_locations_heatmap.html'.")