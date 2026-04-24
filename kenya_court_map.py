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

LEGEND_COLORS = {
    "Supreme Court": "#5f4b8b",
    "Court of Appeal": "#5f9ea0",
    "High Courts": "#00008b",
    "Law Courts (Magistrate Courts)": "#3388ff",
    "Employment & Labour Courts": "#90ee90",
    "Environment & Land Courts": "#006400",
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
m = folium.Map(location=[0.5, 37.5], zoom_start=6, tiles='CartoDB positron', control_scale=True)

# Add choropleth layer
choropleth = folium.Choropleth(
    geo_data=kenya_geojson,
    data=data,
    columns=['County', 'Total Courts'],
    key_on=f'feature.properties.{geojson_property_key}',
    fill_color='Greens',
    fill_opacity=0.45,
    line_opacity=0.25,
    legend_name='Number of Courts per County',
    highlight=True
).add_to(m)

folium.GeoJsonTooltip(fields=[geojson_property_key], aliases=['County:']).add_to(choropleth.geojson)

# Function to clean coordinate columns and add court markers
def add_court_markers(df, color, label):
    group = folium.FeatureGroup(name=label, show=True)
    cluster = MarkerCluster(
        icon_create_function=icon_create_function,
        disableClusteringAtZoom=10,
        spiderfyOnMaxZoom=True,
        showCoverageOnHover=False,
        maxClusterRadius=50
    ).add_to(group)

    df = df.copy()
    df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
    df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
    df = df.dropna(subset=['Latitude', 'Longitude'])

    for _, row in df.iterrows():
        popup_content = (
            f"<b>{row['Court Name']}</b><br>"
            f"Type: {label}<br>"
            f"Lat/Lon: {row['Latitude']:.5f}, {row['Longitude']:.5f}"
        )

        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=9,
            color="#243D21",
            weight=1,
            fill=True,
            fill_opacity=0.12
        ).add_to(cluster)

        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=folium.Popup(popup_content, max_width=280),
            tooltip=f"{row['Court Name']} ({label})",
            icon=folium.Icon(color=color, icon=ICON_MAP.get(label, "gavel"), prefix='fa')
        ).add_to(cluster)

    group.add_to(m)

# Define icon creation function for MarkerCluster (can add ChildCount to style)
icon_create_function = '''
function(cluster) {
    var childCount = cluster.getChildCount();
    var size = Math.min(56, Math.max(34, 28 + Math.log(childCount + 1) * 10));
    return new L.DivIcon({
        html: '<div style="width:' + size + 'px; height:' + size + 'px; line-height:' + size + 'px;">' + childCount + '</div>',
        className: 'marker-cluster marker-cluster-custom',
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
.marker-cluster-custom {
    box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.95);
}
</style>
""")
m.get_root().html.add_child(layer_style)

legend_html = f"""
<div style="
    position: fixed;
    bottom: 30px;
    left: 10px;
    z-index: 9999;
    background: white;
    border: 1px solid #cfcfcf;
    border-radius: 8px;
    padding: 10px 12px;
    font-size: 13px;
    color: #243D21;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
">
    <div style="font-weight: 700; margin-bottom: 6px;">Court Types</div>
    <div><span style="display:inline-block;width:10px;height:10px;background:{LEGEND_COLORS['Supreme Court']};margin-right:6px;"></span>Supreme Court</div>
    <div><span style="display:inline-block;width:10px;height:10px;background:{LEGEND_COLORS['Court of Appeal']};margin-right:6px;"></span>Court of Appeal</div>
    <div><span style="display:inline-block;width:10px;height:10px;background:{LEGEND_COLORS['High Courts']};margin-right:6px;"></span>High Courts</div>
    <div><span style="display:inline-block;width:10px;height:10px;background:{LEGEND_COLORS['Law Courts (Magistrate Courts)']};margin-right:6px;"></span>Law Courts (Magistrate)</div>
    <div><span style="display:inline-block;width:10px;height:10px;background:{LEGEND_COLORS['Employment & Labour Courts']};margin-right:6px;"></span>Employment and Labour</div>
    <div><span style="display:inline-block;width:10px;height:10px;background:{LEGEND_COLORS['Environment & Land Courts']};margin-right:6px;"></span>Environment and Land</div>
</div>
"""
m.get_root().html.add_child(Element(legend_html))

# Add layer control
folium.LayerControl(collapsed=False, position='bottomright').add_to(m)

# Save the map
m.save('index.html')
print("Map saved successfully!")