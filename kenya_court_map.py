import plotly.express as px
import pandas as pd
import json

# Load your data
data = pd.read_csv('Kenya_Court_Count.csv')
data['County'] = data['County'].str.strip().str.upper()

with open('kenya.geojson') as f:
    kenya_geojson = json.load(f)

# Plot Mapbox choropleth
fig = px.choropleth_mapbox(
    data_frame=data,
    geojson=kenya_geojson,
    featureidkey="properties.COUNTY_NAM",
    locations="County",
    color="Total Courts",
    mapbox_style="open-street-map",  # options: "carto-darkmatter", "open-street-map", etc. positron
    zoom=5.5,
    center={"lat": 0.5, "lon": 37.5},
    color_continuous_scale="Greens",
    opacity=0.6,
    title="Total Courts per County in Kenya"
)

fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
fig.show()
