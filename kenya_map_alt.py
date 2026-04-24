import pandas as pd
import folium
import json
from folium.plugins import MarkerCluster
from folium import Element
import branca.colormap as cm

# Constants for file paths
COURT_DATA_PATH = './kenya_courts_locations/'
GEOJSON_FILE = 'kenya.geojson'

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

# Load data
try:
    data = pd.read_csv(f'{COURT_DATA_PATH}Kenya_Court_Count.csv')
    data.columns = data.columns.str.strip()
    data['County'] = data['County'].str.strip().str.upper()
except FileNotFoundError:
    print("Error: Kenya_Court_Count.csv file not found.")
    exit()

try:
    with open(GEOJSON_FILE) as f:
        kenya_geojson = json.load(f)
except FileNotFoundError:
    print("Error: GeoJSON file not found.")
    exit()

# Normalize GeoJSON
geojson_property_key = 'COUNTY_NAM'
for feature in kenya_geojson['features']:
    if geojson_property_key in feature['properties']:
        val = feature['properties'][geojson_property_key]
        feature['properties'][geojson_property_key] = str(val).upper() if val else "UNKNOWN"

# Custom color map (shades of F9EC90)
max_val = data['Total Courts'].max()
min_val = data['Total Courts'].min()
yellow_colormap = cm.linear.YlOrBr_09.scale(min_val, max_val)
yellow_colormap.colors = ['#FFFDE5', '#F9EC90', '#F6D13E']  # custom soft yellows

# Create base map
m = folium.Map(
    location=[0.5, 37.5],
    zoom_start=6,
    tiles=None,  # Remove default tiles
    control_scale=False
)

# Add dark green Africa background using a rectangle
folium.Rectangle(
    bounds=[[-35, -20], [38, 55]], 
    color='#40703A',
    fill=True,
    fill_opacity=1,
    weight=0
).add_to(m)

choropleth = folium.Choropleth(
    geo_data=kenya_geojson,
    name='Court Distribution',
    data=data,
    columns=['County', 'Total Courts'],
    key_on=f'feature.properties.{geojson_property_key}',
    fill_color='YlOrBr', 
    fill_opacity=0.9,
    line_opacity=0.1,
    highlight=True,
    legend_name='Number of Courts per County'
).add_to(m)

folium.GeoJsonTooltip(fields=[geojson_property_key], aliases=['County:']).add_to(choropleth.geojson)

# MarkerCluster function
icon_create_function = '''
function(cluster) {
    var count = cluster.getChildCount();
    var size = Math.min(60, Math.max(30, count * 2));
    return new L.DivIcon({
        html: '<div style="background:#243D21;color:white;width:' + size + 'px;height:' + size + 'px;line-height:' + size + 'px;border-radius:50%;text-align:center;font-weight:bold;">' + count + '</div>',
        className: 'marker-cluster',
        iconSize: new L.Point(size, size)
    });
}
'''

# Add court markers
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

for court in COURT_DATASETS:
    try:
        df = pd.read_csv(f"{COURT_DATA_PATH}{court['file']}")
        add_court_markers(df, court['color'], court['label'])
    except FileNotFoundError:
        print(f"Error: {court['file']} file not found.")

# Custom style for layers
layer_style = Element("""
<style>
.leaflet-control-layers {
    font-family: 'Arial', sans-serif;
    background-color: white;
    border-radius: 6px;
    padding: 10px;
    font-size: 14px;
}
.leaflet-control-layers-overlays label,
.leaflet-control-layers-base label {
    color: #243D21;
    font-weight: 500;
}
</style>
""")
m.get_root().html.add_child(layer_style)

# Add layer control
folium.LayerControl(collapsed=False, position='bottomright').add_to(m)

# Save
m.save("indexALT.html")
print("Map saved with yellow choropleth and green Africa background!")
