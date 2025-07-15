import pandas as pd
import folium
import json
from folium.plugins import MarkerCluster
from folium import Element

# Constants for file paths
COURT_DATA_PATH = './kenya_courts_locations/'
GEOJSON_FILE = 'kenya.geojson'

# Court datasets and their properties
COURT_DATASETS = [
    {"file": "supreme_court.csv", "color": "darkpurple", "label": "Supreme Court"},
    {"file": "court_of_appeal_courts.csv", "color": "cadetblue", "label": "Court of Appeal"},
    {"file": "high_courts.csv", "color": "darkblue", "label": "High Courts"},
    {"file": "law_courts.csv", "color": "blue", "label": "Law Courts (Magistrate Courts)"},
    {"file": "EmpLab_courts.csv", "color": "lightgreen", "label": "Employment & Labour Courts"},
    {"file": "EnvtLand_courts.csv", "color": "darkgreen", "label": "Environment & Land Courts"},
]

ICON_MAP = {
    "Supreme Court": "balance-scale",
    "Court of Appeal": "exchange",
    "High Courts": "landmark",
    "Law Courts (Magistrate Courts)": "gavel",
    "Employment & Labour Courts": "briefcase",
    "Environment & Land Courts": "leaf"
}

# Load Kenya map + counties
try:
    data = pd.read_csv(f'{COURT_DATA_PATH}Kenya_Court_Count.csv')
    data.columns = data.columns.str.strip()
    data['County'] = data['County'].str.strip().str.upper()
except FileNotFoundError:
    print("Error: Kenya_Court_Count.csv file not found.")
    exit()

# Load GeoJSON
try:
    with open(GEOJSON_FILE) as f:
        kenya_geojson = json.load(f)
except FileNotFoundError:
    print("Error: GeoJSON file not found.")
    exit()

# Normalize GeoJSON to match CSV
geojson_property_key = 'COUNTY_NAM'
for feature in kenya_geojson['features']:
    if geojson_property_key in feature['properties']:
        feature['properties'][geojson_property_key] = str(feature['properties'][geojson_property_key]).upper()

# Create map
m = folium.Map(location=[0.5, 37.5], zoom_start=6, tiles='CartoDB positron')

# Add choropleth layer
choropleth = folium.Choropleth(
    geo_data=kenya_geojson,
    data=data,
    columns=['County', 'Total Courts'],
    key_on=f'feature.properties.{geojson_property_key}',
    fill_color='Greens',
    fill_opacity=0.7,
    line_opacity=0.3,
    legend_name='Number of Courts per County',
    highlight=True
).add_to(m)

folium.GeoJsonTooltip(fields=[geojson_property_key], aliases=['County:']).add_to(choropleth.geojson)

# Function to clean coordinate columns and add court markers
def add_court_markers(df, color, label):
    group = folium.FeatureGroup(name=label, show=True)
    cluster = MarkerCluster(icon_create_function=icon_create_function).add_to(group)

    df = df.copy()
    df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
    df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
    df = df.dropna(subset=['Latitude', 'Longitude'])

    for _, row in df.iterrows():
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=f"<b>{row['Court Name']}</b>",
            icon=folium.Icon(color=color, icon=ICON_MAP.get(label, "gavel"), prefix='fa')
        ).add_to(cluster)

    group.add_to(m)

# Define icon creation function for MarkerCluster (can add ChildCount to style)
icon_create_function = '''
function(cluster) {
    var childCount = cluster.getChildCount();
    var size = Math.min(60, Math.max(30, childCount * 2)); // Dynamically calculate size based on childCount
    return new L.DivIcon({
        html: '<div style="width:' + size + 'px; height:' + size + 'px; line-height:' + size + 'px;">'  + '</div>',
        className: 'marker-cluster',
        iconSize: new L.Point(size, size)
    });
}
'''

# Load court datasets and add markers
for court in COURT_DATASETS:
    try:
        df = pd.read_csv(f"{COURT_DATA_PATH}{court['file']}")
        add_court_markers(df, court['color'], court['label'])
    except FileNotFoundError:
        print(f"Error: {court['file']} file not found.")

# Add custom layer control styles
layer_style = Element("""
<style>
.leaflet-control-layers {
    font-family: 'Arial', sans-serif;
    background-color: white;
    border: 1px solid #ccc;
    border-radius: 6px;
    padding: 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    font-size: 14px;
}
.leaflet-control-layers-overlays label,
.leaflet-control-layers-base label {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 4px 0;
    cursor: pointer;
    color: #243D21;
    font-weight: 500;
}
.leaflet-control-layers input[type="checkbox"] {
    accent-color: #243D21;
    margin-right: 6px;
}
.leaflet-control-layers-overlays label::after {
    content: '';
    display: inline-block;
    width: 12px;
    height: 12px;
    border-radius: 2px;
    margin-left: 8px;
}

.leaflet-control-layers-overlays label:nth-of-type(2)::after { background: #5f4b8b; }
.leaflet-control-layers-overlays label:nth-of-type(3)::after { background: #5f9ea0; }
.leaflet-control-layers-overlays label:nth-of-type(4)::after { background: #00008b; }
.leaflet-control-layers-overlays label:nth-of-type(5)::after { background: #3388ff; }
.leaflet-control-layers-overlays label:nth-of-type(6)::after { background: #90ee90; }
.leaflet-control-layers-overlays label:nth-of-type(7)::after { background: #006400; }
                      
/* Cluster circle styling */
.marker-cluster {
    background-color: rgba(0, 123, 255, 0.6); /* Blue background */
    border: 2px solid #007bff; /* Border color */
    border-radius: 50%; /* Make it circular */
    color: white; /* Text color */
    font-weight: bold; /* Bold text */
    text-align: center; /* Center text */
    display: flex;
    align-items: center;
    justify-content: center;
}
</style>
""")
m.get_root().html.add_child(layer_style)

# Add layer control
folium.LayerControl(collapsed=False, position='bottomright').add_to(m)

# Save the map
m.save('index.html')
print("Map saved successfully!")