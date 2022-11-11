import yaml
import os
import sys
dir_path = os.getcwd()
sys.path.append(dir_path)

import pydeck as pdk
import streamlit as st


def get_config(config_filepath: str) -> dict:
    with open(config_filepath) as f:
        config = yaml.safe_load(f)
    return config


def get_pdk(st_empty, df, center_lat, center_lon):
    st_empty.pydeck_chart(pdk.Deck(
        map_style='road',
        initial_view_state=pdk.ViewState(
            latitude=center_lat,
            longitude=center_lon,
            zoom=11,
            pitch=50,
        ),
        layers=[
        #     pdk.Layer(
        #        'HexagonLayer',
        #        data=df,
        #        get_position='[lon, lat]',
        #        radius=200,
        #        elevation_scale=4,
        #        elevation_range=[0, 1000],
        #        pickable=True,
        #        extruded=True,
        #     ),
            pdk.Layer(
                'ScatterplotLayer',
                data=df,
                get_position='[lon, lat]',
                get_color='[200, 30, 0, 160]',
                get_radius=200,
            ),
            pdk.Layer(
                'ScatterplotLayer',
                data=df,
                get_position='[lon_pred, lat_pred]',
                get_color='[0, 30, 200, 160]',
                get_radius=200,
            ),
        ],
    ))