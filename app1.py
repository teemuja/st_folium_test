# testing.. https://github.com/randyzwitch/streamlit-folium/blob/master/examples/interactive_app.py
import pandas as pd
import geopandas as gpd
import streamlit as st
import folium
from streamlit_folium import st_folium
import h3

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

# THE MAP
if "p1_lat" not in st.session_state:
    # initial empty map
    m = map_object()
    map_data = st_folium(m, width=900, height=700)
    p1 = (map_data["bounds"]['_southWest']['lat'], map_data["bounds"]['_southWest']['lng'])
    p2 = (map_data["bounds"]['_northEast']['lat'], map_data["bounds"]['_southWest']['lng'])
    p3 = (map_data["bounds"]['_northEast']['lat'], map_data["bounds"]['_northEast']['lng'])
    p4 = (map_data["bounds"]['_southWest']['lat'], map_data["bounds"]['_northEast']['lng'])
    center_lat = p2[0] - (p2[0] - p1[0]) / 2
    center_lng = p3[1] - (p3[1] - p2[1]) / 2
    zoom = map_data['zoom']
    # store map values as numbers
    st.session_state.p1_lat = map_data["bounds"]['_southWest']['lat']
    st.session_state.p1_lng = map_data["bounds"]['_southWest']['lng']
    st.session_state.p2_lat = map_data["bounds"]['_northEast']['lat']
    st.session_state.p2_lng = map_data["bounds"]['_southWest']['lng']
    st.session_state.p3_lat = map_data["bounds"]['_northEast']['lat']
    st.session_state.p3_lng = map_data["bounds"]['_northEast']['lng']
    st.session_state.p4_lat = map_data["bounds"]['_southWest']['lat']
    st.session_state.p4_lng = map_data["bounds"]['_northEast']['lng']
    st.session_state.c_lat = center_lat
    st.session_state.c_lng = center_lng
    st.session_state.zoom = zoom
else:
    # get new bounds from session_state
    p1 = (st.session_state.p1_lat, st.session_state.p1_lng)
    p2 = (st.session_state.p2_lat, st.session_state.p2_lng)
    p3 = (st.session_state.p3_lat, st.session_state.p3_lng)
    p4 = (st.session_state.p4_lat, st.session_state.p4_lng)
    # create hexes on it..
    geoJson = {'type': 'Polygon',
               'coordinates': [[[p1[0], p1[1]],
                                [p2[0], p2[1]],
                                [p3[0], p3[1]],
                                [p4[0], p4[1]]]]}
    hex_list = list(h3.polyfill(geoJson, 7))
    empty_hexes = pd.DataFrame(hex_list, columns=['hex_id'])
    data = data_load()
    df_hex = pd.merge(empty_hexes, data, on='hex_id')
    gdf_hex = gpd.GeoDataFrame(df_hex, geometry=gpd.GeoSeries.from_wkt(df_hex['geometry'], crs=4326))
    # new map with new values from session_state
    center_lat = st.session_state.c_lat
    center_lng = st.session_state.c_lng
    zoom = st.session_state.zoom
    m = map_object(center_lat,center_lng,zoom)
    # add choropleth
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
    map_data = st_folium(m, key="whatever", width=900, height=700)
    # update new map values
    p1 = (map_data["bounds"]['_southWest']['lat'], map_data["bounds"]['_southWest']['lng'])
    p2 = (map_data["bounds"]['_northEast']['lat'], map_data["bounds"]['_southWest']['lng'])
    p3 = (map_data["bounds"]['_northEast']['lat'], map_data["bounds"]['_northEast']['lng'])
    p4 = (map_data["bounds"]['_southWest']['lat'], map_data["bounds"]['_northEast']['lng'])
    center_lat = p2[0] - (p2[0]-p1[0])/2
    center_lng = p3[1] - (p3[1]-p2[1])/2
    zoom = map_data['zoom']
    # replace session_states for the new rerun
    st.session_state.p1_lat = map_data["bounds"]['_southWest']['lat']
    st.session_state.p1_lng = map_data["bounds"]['_southWest']['lng']
    st.session_state.p2_lat = map_data["bounds"]['_northEast']['lat']
    st.session_state.p2_lng = map_data["bounds"]['_southWest']['lng']
    st.session_state.p3_lat = map_data["bounds"]['_northEast']['lat']
    st.session_state.p3_lng = map_data["bounds"]['_northEast']['lng']
    st.session_state.p4_lat = map_data["bounds"]['_southWest']['lat']
    st.session_state.p4_lng = map_data["bounds"]['_northEast']['lng']
    st.session_state.c_lat = center_lat
    st.session_state.c_lng = center_lng
    st.session_state.zoom = zoom


