import pandas as pd
import folium
import json
from folium.plugins import MarkerCluster

# Load kenya map + counties
data = pd.read_csv('./kenya_courts_locations/Kenya_Court_Count.csv')
data.columns = data.columns.str.strip()
data['County'] = data['County'].str.strip().str.upper()

# Load court location datasets
df_supreme = pd.read_csv('./kenya_courts_locations/supreme_court.csv')
df_coa = pd.read_csv('./kenya_courts_locations/court_of_appeal_courts.csv')
df_high = pd.read_csv('./kenya_courts_locations/high_courts.csv')
df_subordinate = pd.read_csv('./kenya_courts_locations/law_courts.csv')
df_empLab = pd.read_csv('./kenya_courts_locations/EmpLab_courts.csv')
df_elc = pd.read_csv('./kenya_courts_locations/EnvtLand_courts.csv')

# Load geojson
with open('kenya.geojson') as f:
    kenya_geojson = json.load(f)
# Check geojson file
print("Available property keys in the first feature:")
print(kenya_geojson['features'][0]['properties'].keys())
geojson_property_key = 'COUNTY_NAM'  

# Normalize GeoJSON to match CSV
for feature in kenya_geojson['features']:
    if geojson_property_key in feature['properties']:
        feature['properties'][geojson_property_key] = str(feature['properties'][geojson_property_key]).upper()

# Create map
m = folium.Map(location=[0.5, 37.5], zoom_start=6, tiles='CartoDB positron')

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
    #Keeping this incase we revert back to clusters
    icon_create_function = '''
    function(cluster) {
        var childCount = cluster.getChildCount();
        var c = ' marker-cluster-';
        if (childCount < 2) {
            c += 'small';
        } else if (childCount < 20) {
            c += 'medium';
        } else {
            c += 'large';
        }
        return new L.DivIcon({
            html: '<div></div>', // The key change: an empty div
            className: 'marker-cluster' + c,
            iconSize: new L.Point(40, 40)
        });
    }
    '''
    # cluster = MarkerCluster().add_to(group) 
    cluster = MarkerCluster(icon_create_function=icon_create_function).add_to(group)
    

    df = df.copy()
    df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
    df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
    df = df.dropna(subset=['Latitude', 'Longitude'])

    for _, row in df.iterrows():
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=f"<b>{row['Court Name']}</b>", 
            icon=folium.Icon(color=color, icon='gavel', prefix='fa')
        ).add_to(cluster) # if we can want we can add to cluster instead of group

    group.add_to(m)


# Add layers for each court type
add_court_markers(df_supreme, 'purple', 'Supreme Court - Purple')
add_court_markers(df_coa, 'pink', 'Court of Appeal - Pink')
add_court_markers(df_high, 'red', 'High Courts- Red')
add_court_markers(df_subordinate, 'blue', 'Law Courts (Magistrate Courts) - Blue')
add_court_markers(df_empLab, 'orange', 'Employment & Labour Courts - Orange')
add_court_markers(df_elc, 'green', 'Environment & Land Courts- Green')

# # Add toggle
folium.LayerControl(collapsed=False).add_to(m)

# Save the map
m.save('kenya_court_map.html')
print("Map saved successfully!")