import pandas as pd
import folium
from folium.plugins import HeatMap
from branca.element import MacroElement, Template

# Load data
df = pd.read_csv("/Users/dennissiegert/Downloads/Chicago 2023 Crime Data.csv", low_memory=False)

# Clean coordinates
df = df.dropna(subset=['Latitude', 'Longitude'])
df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
df = df.dropna(subset=['Latitude', 'Longitude'])

# Define bounds
min_lat, max_lat = df['Latitude'].min(), df['Latitude'].max()
min_lon, max_lon = df['Longitude'].min(), df['Longitude'].max()
bounds = [[min_lat, min_lon], [max_lat, max_lon]]

# Create base map
m = folium.Map(
    location=[df['Latitude'].mean(), df['Longitude'].mean()],
    zoom_start=12,
    min_zoom=11,
    max_zoom=13
)

# Lock view
class MaxBounds(MacroElement):
    def __init__(self, bounds):
        super().__init__()
        self._template = Template(u"""
            {% macro script(this, kwargs) %}
                {{this._parent.get_name()}}.setMaxBounds([[{{ this.bounds[0][0] }}, {{ this.bounds[0][1] }}], [{{ this.bounds[1][0] }}, {{ this.bounds[1][1] }}]]);
            {% endmacro %}
        """)
        self.bounds = bounds

m.get_root().add_child(MaxBounds(bounds))
m.fit_bounds(bounds)

# Add heatmaps by crime type
top_crimes = df['Primary Type'].value_counts().nlargest(5).index

for crime in top_crimes:
    crime_df = df[df['Primary Type'] == crime]
    heat_data = crime_df[['Latitude', 'Longitude']].dropna().values.tolist()

    if not heat_data:
        continue

    heat_layer = folium.FeatureGroup(name=crime)
    HeatMap(heat_data, radius=10, blur=12).add_to(heat_layer)
    heat_layer.add_to(m)

# Add area highlight (example polygon for South Side)
folium.Polygon(
    locations=[
        [41.74, -87.65],
        [41.74, -87.58],
        [41.70, -87.58],
        [41.70, -87.65]
    ],
    color="red",
    fill=True,
    fill_opacity=0.2,
    popup="South Side (Example Area)"
).add_to(m)

# Add legend (HTML + CSS)
legend_html = """
<div style="
    position: fixed;
    bottom: 30px;
    left: 30px;
    z-index: 9999;
    background-color: white;
    padding: 10px;
    border:2px solid grey;
    border-radius: 5px;
    box-shadow: 2px 2px 6px rgba(0,0,0,0.3);
">
    <b>Crime Heatmap Legend</b><br>
    <i style="background: red; opacity: 0.6; width: 18px; height: 10px; float: left; margin-right: 5px;"></i> Higher Crime Concentration<br>
    <i style="background: yellow; opacity: 0.6; width: 18px; height: 10px; float: left; margin-right: 5px;"></i> Moderate Concentration<br>
    <i style="background: green; opacity: 0.6; width: 18px; height: 10px; float: left; margin-right: 5px;"></i> Lower Concentration<br>
    <br><b>Red Box</b>: Example Area Highlight
</div>
"""

m.get_root().html.add_child(folium.Element(legend_html))

# Layer control
folium.LayerControl(collapsed=False).add_to(m)

# Save map
m.save("chicago_crime_heatmap_legend_area.html")
print("✅ Map created: chicago_crime_heatmap_legend_area.html")