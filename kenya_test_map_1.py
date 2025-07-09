import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json

# Load data
data = pd.read_csv('./kenya_courts_locations/Kenya_Court_Count.csv')
df_superior = pd.read_csv('./kenya_courts_locations/superior_courts.csv')
df_high = pd.read_csv('./kenya_courts_locations/high_courts.csv')
df_subordinate = pd.read_csv('./kenya_courts_locations/subordinate_courts.csv')
df_empLab = pd.read_csv('./kenya_courts_locations/EmpLab_courts.csv')
df_elc = pd.read_csv('./kenya_courts_locations/EnvtLand_courts.csv')

data.columns = data.columns.str.strip()
data['County'] = data['County'].str.strip().str.upper()

with open('kenya.geojson') as f:
    kenya_geojson = json.load(f)

# Create choropleth figure
fig = px.choropleth(
    data_frame=data,
    geojson=kenya_geojson,
    featureidkey="properties.COUNTY_NAM",
    locations='County',
    color='Total Courts',
    color_continuous_scale='Greens', # tested Viridis
    title='Number of Courts per County in Kenya',
)

# Add scatter layer
fig.add_trace(go.Scattergeo(
    lon=df_superior['Longitude'],
    lat=df_superior['Latitude'],
    text=df_superior['Court Name'],
    mode='markers',
    marker=dict(size=10, color='red'),
    name='Superior Courts'
))

fig.add_trace(go.Scattergeo(
    lon=df_high['Longitude'],
    lat=df_high['Latitude'],
    text=df_high['Court Name'],
    mode='markers',
    marker=dict(size=10, color='red', symbol='square'),
    name='High Courts'
))

fig.add_trace(go.Scattergeo(
    lon=df_subordinate['Longitude'],
    lat=df_subordinate['Latitude'],
    text=df_subordinate['Court Name'],
    mode='markers',
    marker=dict(size=7, color='blue', symbol = 'diamond'),
    name='Law Courts'
))

fig.add_trace(go.Scattergeo(
    lon=df_empLab['Longitude'],
    lat=df_empLab['Latitude'],
    text=df_empLab['Court Name'],
    mode='markers',
    marker=dict(size=8, color='orange', symbol = 'x'),
    name='Employement and Land Courts'
))

fig.add_trace(go.Scattergeo(
    lon=df_elc['Longitude'],
    lat=df_elc['Latitude'],
    text=df_elc['Court Name'],
    mode='markers',
    marker=dict(size=8, color='green', symbol = 'triangle-up', line=dict(width=0.5, color='darkslategray')),
    name='Environment and Land Courts'
))


fig.update_geos(
    visible=False,
    showcountries=False,
    showsubunits=True,
    lataxis_range=[-5, 5],   
    lonaxis_range=[33, 42]
)

fig.update_layout(
    legend=dict(
        title="Court Types",
        orientation="h",# horizontal layout
        yanchor="bottom",
        y=0.01,
        xanchor="left",
        x=0.01
    ),
    margin={"r":0, "t":50, "l":0, "b":20}
)

fig.show()
