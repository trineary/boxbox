
import os
import sys
dir_path = os.getcwd()
sys.path.append(dir_path)

import json
import datetime
from time import sleep
import numpy as np
import pandas as pd
import streamlit as st
import asyncio

from scripts.mqtt import get_mqtt_client
from scripts.helpers import get_config, get_pdk

boxbox_dict = None


def st_print(text):
    st.text(text)


def on_message(client, userdata, msg):
    # print message, useful for checking if it was successful
    global boxbox_dict
    boxbox_dict = str(msg.payload.decode('ascii'))


# print which topic was subscribed to
def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    # st_print("MQTT subscribed successful: " + str(mid) + " " + str(granted_qos))
    # st_print(f"MQTT subscribe successful: {userdata}")
    # st_print(f"User data: {userdata}")
    pass


def on_connect(client, userdata, flags, rc, properties=None):
    # st_print(f"CONNACK received with code {type(rc)}, {str(rc)}")
    if str(rc) == "Success":
        # st_print("MQTT connected to broker")
        client.connected_flag = True  # set flag
    else:
        st_print(f"Bad connection to MQTT broker, returned code={rc}")


def on_publish(client, userdata, mid):
    st_print("mid: " + str(mid))


async def mqtt_periodic():
    map_zoom = 13
    map_pitch = 25

    global boxbox_dict
    global auto_center
    global show_predicted
    global max_crumbs

    cnt_cols = st.empty()
    col1, col2, col3 = cnt_cols.columns(3)
    col1.metric("VMR Cnt", "0")
    col2.metric("MFAM Cnt", "0")
    col3.metric("VN3xx Cnt", "0")

    data_cols = st.empty()
    col1, col2, col3 = data_cols.columns(3)
    col1.metric("Sat Cnt", "0")
    col2.metric("Air Temp", "0")
    col3.metric("Uptime", "0")

    gps_cols = st.empty()
    col1, col2 = gps_cols.columns(2)
    col1.metric("GPS Lat", "0")
    col2.metric("GPS lon", "0")

    pred_cols = st.empty()
    col1, col2 = pred_cols.columns(2)
    col1.metric("Pred Lat", "0")
    col2.metric("Pred Lon", "0")

    strt_map = st.empty()
    start_time = datetime.datetime.now()
    test = st.empty()
    dict_str = st.empty()
    lat_lons = None

    while True:
        if "mqtt_client" in st.session_state:
            st.session_state.mqtt_client.loop(1.0)
            test.text(f"UI uptime: {int((datetime.datetime.now() - start_time).seconds)} secs")
            if boxbox_dict is not None:
                boxbox_dict = boxbox_dict.replace("'", '"')
                # dict_str.text(f"boxbox_dict: {boxbox_dict}")
                box_data = json.loads(boxbox_dict)

                # Update data in columns
                col1, col2, col3 = cnt_cols.columns(3)
                col1.metric("VMR Cnt", box_data["VMR_PUB_Cnt"])
                col2.metric("MFAM Cnt", box_data["VN3xx_PUB_Cnt"])
                col3.metric("VN3xx Cnt", box_data["MFAM_PUB_Cnt"])

                col1, col2, col3 = data_cols.columns(3)
                col1.metric("Sat Cnt", box_data["num_sats"])
                col2.metric("Air Temp", box_data["air_temp"])
                col3.metric("Uptime", box_data["up_time"])

                # Plot lat/lon
                gps_lat, gps_lon, pred_lat, pred_lon = float(box_data['gps_lat']), float(box_data['gps_lon']), float(box_data['pred_lat']), float(box_data['pred_lon'])

                col1, col2 = gps_cols.columns(2)
                col1.metric("GPS Lat", gps_lat)
                col2.metric("GPS Lon", gps_lon)

                col1, col2 = pred_cols.columns(2)
                col1.metric("Pred Lat", pred_lat)
                col2.metric("Pred Lon", pred_lon)

                if lat_lons is None:
                    lat_lons = np.array([[gps_lat, gps_lon, pred_lat, pred_lon]])
                else:
                    lat_lons = np.append(lat_lons, [[gps_lat, gps_lon, pred_lat, pred_lon]], axis=0)

                if len(lat_lons) > max_crumbs:
                    lat_lons = lat_lons[-max_crumbs:]

                df = pd.DataFrame(lat_lons, columns=['gps_lat', 'gps_lon', 'pred_lat', 'pred_lon'])

                get_pdk(strt_map, df, center_lat=gps_lat, center_lon=gps_lon, zoom=map_zoom, pitch=map_pitch,
                        map_style='road', show_predicted=show_predicted)

                boxbox_dict = None
        else:
            test.text(f"Uptime  else: {int((datetime.datetime.now() - start_time).seconds)} secs")
            sleep(1.0)


VIEWER_WIDTH = 600

title = st.title("BoxBox Status")

config = get_config("./config/config.yml")

# Let user select which box to listen to
box_select = st.selectbox('BoxBox Selection:', config['topics'])

# Allow some options
# auto_center = st.checkbox("Auto-center GPS Lat/Lon")
show_predicted = st.checkbox("Show predicted Lat/Lon")

MQTT_UN = st.secrets["MQTT_UN"]
MQTT_PW = st.secrets["MQTT_PW"]
MQTT_CONN_STR = st.secrets["MQTT_CONN_STR"]

re_init_mqtt = False

max_crumbs = 120

if 'mqtt_client' not in st.session_state:
    re_init_mqtt = True

if "box_select" not in st.session_state:
    re_init_mqtt = True

if "box_select" in st.session_state:
    if box_select not in st.session_state.box_select:
        re_init_mqtt = True

if re_init_mqtt is True and box_select is not None:
    if "mqtt_client" in st.session_state:
        st.session_state.mqtt_client.loop_stop(force=True)
        # st.write("Stopping mqtt before restarting")

    # Reinitialize mqtt if it hasn't been initialized or if it has changed
    st.session_state.mqtt_client = get_mqtt_client(MQTT_UN, MQTT_PW, MQTT_CONN_STR, on_connect, on_message=on_message)
    st.session_state.mqtt_client.on_subscribe = on_subscribe
    st.session_state.mqtt_client.on_message = on_message
    st.session_state.mqtt_client.subscribe(box_select, qos=1)

    sleep(0.5)

asyncio.run(mqtt_periodic())
st_print("post asyncio")

