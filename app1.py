# testing.. https://github.com/randyzwitch/streamlit-folium/blob/master/examples/interactive_app.py
import pandas as pd
import geopandas as gpd
import streamlit as st
import folium
from streamlit_folium import st_folium
import h3

# title
st.title('H3 hexes')
st.caption('From DB to map')

# load data.. replace by db conn
df = pd.read_csv('pkstest.csv', usecols=['h3_07','muutos','geometry'])
df.rename(columns={'h3_07':'hex_id'}, inplace=True)

# function for h3
def get_h3_from_ui(map_data):
    # get bbox from UI..
    p1 = (map_data["bounds"]['_southWest']['lat'], map_data["bounds"]['_southWest']['lng'])
    p2 = (map_data["bounds"]['_northEast']['lat'], map_data["bounds"]['_southWest']['lng'])
    p3 = (map_data["bounds"]['_northEast']['lat'], map_data["bounds"]['_northEast']['lng'])
    p4 = (map_data["bounds"]['_southWest']['lat'], map_data["bounds"]['_northEast']['lng'])
    # create hexes on it..
    geoJson = {'type': 'Polygon',
               'coordinates': [[[p1[0], p1[1]],
                                [p2[0], p2[1]],
                                [p3[0], p3[1]],
                                [p4[0], p4[1]]]]}
    hex_list = list(h3.polyfill(geoJson, 7))
    empty_hexes = pd.DataFrame(hex_list, columns=['hex_id'])
    df_hex = pd.merge(empty_hexes, df, on='hex_id')
    gdf_hex = gpd.GeoDataFrame(df_hex, geometry=gpd.GeoSeries.from_wkt(df_hex['geometry'], crs=4326))
    return gdf_hex

# THE MAP
m = folium.Map(location=[60.2, 24.9], tiles='cartodbpositron', zoom_start=10, control_scale=True)
map_data = st_folium(m, key="choro", width=900, height=700)
gdf_hex = get_h3_from_ui(map_data)
# choropleth test
choro = folium.Choropleth(geo_data=gdf_hex.to_json(),
                          name='muutos',
                          data=gdf_hex,
                          columns=['hex_id', 'muutos'],
                          key_on='feature.properties.hex_id',
                          fill_color='YlOrRd',
                          fill_opacity=0.6,
                          line_opacity=0.9,
                          legend_name="Population change"
                          ).add_to(m)

# geojson test
style_function = lambda x: {'fillColor': '#ffffff',
                            'color':'#000000',
                            'fillOpacity': 0.1,
                            'weight': 0.1}
highlight_function = lambda x: {'fillColor': '#000000',
                                'color':'#000000',
                                'fillOpacity': 0.50,
                                'weight': 0.1}
H3s = folium.features.GeoJson(
    gdf_hex,
    style_function=style_function,
    control=False,
    highlight_function=highlight_function,
    tooltip=folium.features.GeoJsonTooltip(
        fields=['hex_id', 'muutos'],
        style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
    )
)
m.add_child(H3s)
map_data = st_folium(m, key="choro", width=900, height=700)
