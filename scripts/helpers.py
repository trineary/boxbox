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


def get_pdk(st_empty, df, center_lat, center_lon, zoom=11, pitch=50, map_style='road', show_predicted=False):
    if show_predicted is True:
        st_empty.pydeck_chart(pdk.Deck(
            map_style=map_style,
            initial_view_state=pdk.ViewState(
                latitude=center_lat,
                longitude=center_lon,
                zoom=zoom,
                pitch=pitch,
            ),
            layers=[
                pdk.Layer(
                    'ScatterplotLayer',
                    data=df,
                    get_position='[gps_lon, gps_lat]',
                    get_color='[200, 30, 0, 160]',
                    get_radius=100,
                ),
                pdk.Layer(
                    'ScatterplotLayer',
                    data=df,
                    get_position='[pred_lon, pred_lat]',
                    get_color='[0, 30, 200, 160]',
                    get_radius=100,
                ),
            ],
        ))
    else:
        st_empty.pydeck_chart(pdk.Deck(
            map_style=map_style,
            initial_view_state=pdk.ViewState(
                latitude=center_lat,
                longitude=center_lon,
                zoom=zoom,
                pitch=pitch,
            ),
            layers=[
                pdk.Layer(
                    'ScatterplotLayer',
                    data=df,
                    get_position='[gps_lon, gps_lat]',
                    get_color='[200, 30, 0, 160]',
                    get_radius=100,
                ),
            ],
        ))
