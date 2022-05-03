# testing.. https://github.com/randyzwitch/streamlit-folium/blob/master/examples/interactive_app.py
#%%
import pandas as pd
import geopandas as gpd
import streamlit as st
import folium
from streamlit_folium import st_folium
import h3
import json
from io import StringIO

# title
st.title('H3 hexes')
st.caption('Testing with streamlit-folium..')

# load data.. replace with db conn
@st.cache()
def data_load():
    df = pd.read_csv('pkstest.csv', usecols=['h3_07','muutos','geometry'])
    df.rename(columns={'h3_07':'hex_id'}, inplace=True)
    return df

# map object def
def map_object(center_lat=60.2,center_lng=24.9,zoom=10):
    m = folium.Map(location=[center_lat, center_lng], tiles='cartodbpositron', zoom_start=zoom, control_scale=True)
    return m

def set_session_bounds(map_data):
    print(map_data["bounds"])
    if ~isinstance(map_data['bounds'],list): # checking if the map is rendered
        bounds = list(map_data["bounds"].values())
        bounds = [bounds[0]['lng'], bounds[0]['lat'], bounds[1]['lng'], bounds[1]['lat']]
        center_lat = (bounds[1] + bounds[3]) / 2
        center_lng = (bounds[0] + bounds[2]) / 2
        zoom = map_data['zoom']
        geoJson = json.dumps({
            'type': 'Polygon',
            'coordinates': [[
                [bounds[0], bounds[1]],
                [bounds[0], bounds[3]],
                [bounds[2], bounds[3]],
                [bounds[2], bounds[1]]
                ]]
            })
        # store map values as numbers

        st.session_state["bounding_geom"] = geoJson
        st.session_state["c_lat"] = center_lat
        st.session_state["c_lng"] = center_lng
        st.session_state["zoom"] = zoom

m = map_object()
map_data = st_folium(m, width=900, height=700)
#%%
if "start" not in st.session_state:
    # initializing the state variables:
    st.session_state["start"] = True
    st.session_state["bounding_geom"] = ''
    st.session_state["c_lat"] = 0
    st.session_state["c_lng"] = 0
    st.session_state["zoom"] = 0
    set_session_bounds(map_data)
else:
    # creating map based on values

    m = map_object(
        st.session_state.c_lat,
        st.session_state.c_lng,
        st.session_state.zoom)
    hex_list = list(
        h3.polyfill(
            json.loads(st.session_state["bounding_geom"]), 
            7
        ))
    empty_hexes = pd.DataFrame(hex_list, columns=['hex_id'])
    data = data_load()
    # ATTENTION! Here the two dataframes are not merging, and the result is an empty dataframe for df_hexes
    # this is causing the error and it should be fixed to show the data and resolve the error.
    # the issue might be in the hex id creation of the module h3
    df_hex = data[
        data['hex_id'].isin(empty_hexes['hex_id'])
        ]

    gdf_hex = gpd.GeoDataFrame(df_hex, geometry=gpd.GeoSeries.from_wkt(df_hex['geometry'], crs=4326))
    
    m = map_object(
        st.session_state["c_lat"],
        st.session_state["c_lng"],
        st.session_state["zoom"])
    # # add choropleth
    print(empty_hexes['hex_id'].to_list())
    choro = folium.Choropleth(
        geo_data=gdf_hex.to_json(),
        name='muutos',
        data=gdf_hex,
        columns=['hex_id', 'muutos'],
        key_on='feature.properties.hex_id',
        fill_color='YlOrRd',
        fill_opacity=0.6,
        line_opacity=0.9,
        legend_name="Population change"
        ).add_to(m)
    map_data = st_folium(m, key="whatever", width=900, height=700)
    set_session_bounds(map_data)



# %%
