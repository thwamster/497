import json

import geopandas as gpd
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. Load and filter data for 2013-2023
df = pd.read_csv(base_path + '5 - Data/Master-CA-Opioid.2010-2024.csv')
df_filtered = df[(df['year'] >= 2013) & (df['year'] <= 2023) & (df['zip_code'].notna())].copy()
df_filtered['zip_code'] = df_filtered['zip_code'].astype(int).astype(str).str.zfill(5)
df_filtered['death_age_adjusted_rate'] = pd.to_numeric(df_filtered['death_age_adjusted_rate'], errors='coerce')
df_filtered = df_filtered.sort_values('year')

# Calculate the logarithmic rate
df_filtered['log_death_rate'] = np.log10(df_filtered['death_age_adjusted_rate'] + 1)

# RAM Optimization: Keep only the essential columns required for the map to reduce memory overhead
df_filtered = df_filtered[['year', 'zip_code', 'death_age_adjusted_rate', 'log_death_rate']]

# Fix color scale bounds globally across all years for a consistent temporal trend
min_val = df_filtered['log_death_rate'].min()
max_val = df_filtered['log_death_rate'].max()

# 2. Load the GeoJSON
geojson_url = "https://raw.githubusercontent.com/OpenDataDE/State-zip-code-GeoJSON/master/ca_california_zip_codes_geo.min.json"
gdf = gpd.read_file(geojson_url)

# RAM Optimization & High Precision: Use 0.001 tolerance instead of 0.005.
# 0.001 degrees represents ~100 meters, making edges look sharp up close while discarding
# hundreds of thousands of redundant coordinates that crash the system's memory.
gdf['geometry'] = gdf['geometry'].simplify(tolerance=0.001, preserve_topology=True)
ca_zcta_geojson = json.loads(gdf.to_json())

# 3. Generate the main animated choropleth map
fig = px.choropleth(
    df_filtered,
    geojson=ca_zcta_geojson,
    locations='zip_code',
    featureidkey="properties.ZCTA5CE10",
    color='log_death_rate',
    color_continuous_scale="Reds",
    range_color=[min_val, max_val],
    animation_frame='year',
    hover_name='zip_code',
    hover_data={
        'log_death_rate': False,
        'death_age_adjusted_rate': True,
        'zip_code': False,
        'year': False
    },
    title="California Age-Adjusted Opioid Death Rate by ZIP Code (2013-2023)",
    labels={'death_age_adjusted_rate': 'Death Rate', 'log_death_rate': 'Log(Rate + 1)'}
)

# 4. Create a baseline trace containing ALL California ZIP codes to fill missing/empty regions
base_trace = go.Choropleth(
    geojson=ca_zcta_geojson,
    locations=gdf['ZCTA5CE10'],
    z=[0] * len(gdf),
    colorscale=[[0, '#bcbcbc'], [1, '#bcbcbc']],
    showscale=False,
    featureidkey="properties.ZCTA5CE10",
    hoverinfo='skip'
)

# Append background trace to the figure
fig.add_trace(base_trace)

# Move the background trace to index 0 so it stays underneath the data trace
fig.data = (fig.data[1], fig.data[0])

# Direct the animation frames to update trace index 1 (the data trace), leaving index 0 static
for frame in fig.frames:
    frame.traces = [1]

# 5. Apply styling: Add thin, light gray borders to all elements and frames
fig.update_traces(marker_line_width=0.4, marker_line_color='lightgray')

for frame in fig.frames:
    for trace in frame.data:
        trace.marker.line.width = 0.4
        trace.marker.line.color = 'lightgray'

fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0})

fig.write_html(base_path + "6 - Colab/out/Master-CA-Opioid-Chloropleth.html")
