import pandas as pd
import folium
from folium.plugins import HeatMap

compass_card_history_path = 'Data/CompassCardHistoryBig.csv'
translink_transit_stops_path = 'Data/TranslinkTransitStops.csv'

compass_card_history = pd.read_csv(compass_card_history_path)
translink_transit_stops = pd.read_csv(translink_transit_stops_path)

def extract_location(transaction):
    if pd.isna(transaction):
        return None
    if "Bus Stop" in transaction:
        return transaction.split("Bus Stop ")[1]
    elif "Stn" in transaction:
        return transaction.split(" at ")[1].replace(" Stn", "")
    return None

compass_card_history['location'] = compass_card_history['Transaction'].apply(extract_location)

bus_stops = compass_card_history[compass_card_history['location'].str.isdigit().fillna(False)].copy()
train_stations = compass_card_history[~compass_card_history['location'].str.isdigit().fillna(False)].copy()

bus_stops['location'] = bus_stops['location'].astype(str)
translink_transit_stops['stop_code'] = translink_transit_stops['stop_code'].fillna(0).astype(int).astype(str)

bus_stops = bus_stops.merge(
    translink_transit_stops,
    left_on='location',
    right_on='stop_code',
    how='inner'
)

train_stations = train_stations.merge(
    translink_transit_stops[translink_transit_stops['stop_code'] == "99999"],
    left_on='location',
    right_on='stop_name',
    how='inner'
)

visited_locations = pd.concat([
    bus_stops[['stop_lat', 'stop_lon']],
    train_stations[['stop_lat', 'stop_lon']]
])

m = folium.Map(location=[visited_locations['stop_lat'].mean(), visited_locations['stop_lon'].mean()], zoom_start=12)

# for _, row in visited_locations.iterrows():
#     folium.CircleMarker(
#         location=[row['stop_lat'], row['stop_lon']],
#         radius=5,
#         color='blue',
#         fill=True,
#         fill_color='blue',
#         fill_opacity=0.6
#     ).add_to(m)

heat_data = visited_locations[['stop_lat', 'stop_lon']].values.tolist()

HeatMap(heat_data, radius=11, blur=10).add_to(m)

m.save('Data/visited_locations_heatmap.html')
print("Heatmap saved as 'visited_locations_heatmap.html'.")
