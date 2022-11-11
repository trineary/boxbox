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
# import yaml
import asyncio

from scripts.mqtt import get_mqtt_client
from scripts.helpers import get_config

boxbox_dict = None

def st_print(text):
    st.text(text)


# print message, useful for checking if it was successful
def on_message(client, userdata, msg):
    global boxbox_dict
    # st_print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    boxbox_dict = str(msg.payload.decode('ascii'))


# print which topic was subscribed to
def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    st_print("-"*100)
    st_print("Subscribed: " + str(mid) + " " + str(granted_qos))
    st_print(f"User data: {userdata}")
    st_print("-" * 100)


def on_connect(client, userdata, flags, rc, properties=None):
    st_print(f"CONNACK received with code {type(rc)}, {str(rc)}")
    if str(rc) == "Success":
        st_print("connected to MQTT broker")
        client.connected_flag = True  # set flag
    else:
        st_print(f"Bad connection to MQTT broker, returned code={rc}")


def on_publish(client, userdata, mid):
    st_print("mid: " + str(mid))


async def mqtt_periodic():  # test, cols, strt_map, anom_map):
    global boxbox_dict
    empty_cols = st.empty()
    col1, col2, col3, col4, col5 = empty_cols.columns(5)
    col1.metric("VMR Cnt", "0")
    col2.metric("MFAM Cnt", "0")
    col3.metric("VN3xx Cnt", "0")
    col4.metric("Sat Cnt", "0")
    col5.metric("Uptime", "0")

    strt_map = st.empty()
    start_time = datetime.datetime.now()
    test = st.empty()
    dict_str = st.empty()
    lat_lons = None

    while True:
        if "mqtt_client" in st.session_state:
            st.session_state.mqtt_client.loop(1.0)
            test.text(f"Uptime loop: {int((datetime.datetime.now() - start_time).seconds)} secs")
            if boxbox_dict is not None:
                boxbox_dict = boxbox_dict.replace("'", '"')
                dict_str.text(f"boxbox_dict: {boxbox_dict}")
                st.text(f"box tye: {type(boxbox_dict)}")
                box_data = json.loads(boxbox_dict)

                # Update data in columns
                col1, col2, col3, col4, col5 = empty_cols.columns(5)
                col1.metric("VMR Cnt", box_data["VMR_PUB_Cnt"])
                col2.metric("MFAM Cnt", box_data["VN3xx_PUB_Cnt"])
                col3.metric("VN3xx Cnt", box_data["MFAM_PUB_Cnt"])
                col4.metric("Sat Cnt", box_data["num_sats"])
                col5.metric("Uptime", box_data["up_time"])

                # Plot lat/lon
                lat, lon = float(box_data['lat']), float(box_data['long'])
                if lat_lons is None:
                    lat_lons = np.array([[lat, lon]])
                    lat_lons = np.append(lat_lons, [[lat, lon]], axis=0)
                    lat_lons = np.append(lat_lons, [[lat, lon]], axis=0)
                else:
                    lat_lons = np.append(lat_lons, [[lat, lon]], axis=0)

                st.write(f'np: {lat_lons.shape}')
                df = pd.DataFrame(lat_lons, columns=['lat', 'lon'])
                st.write(f'df: {df.shape}')
                strt_map.map(df)

                boxbox_dict = None
        else:
            test.text(f"Uptime  else: {int((datetime.datetime.now() - start_time).seconds)} secs")
            sleep(1.0)


VIEWER_WIDTH = 600

title = st.title("BoxBox Status")

config = get_config("./config/config.yml")

# Let user select which box to listen to
box_select = st.selectbox('BoxBox Selection:', config['topics'])
st.write('Selection: ', box_select)

# viewer = st.image(get_random_numpy(), width=VIEWER_WIDTH)

MQTT_UN = st.secrets["MQTT_UN"]
MQTT_PW = st.secrets["MQTT_PW"]
MQTT_CONN_STR = st.secrets["MQTT_CONN_STR"]

st_print("mqtt_client in session state: " + str('mqtt_client' in st.session_state))

re_init_mqtt = False

if 'mqtt_client' not in st.session_state:
    re_init_mqtt = True

if "box_select" not in st.session_state:
    re_init_mqtt = True

if "box_select" in st.session_state:
    if box_select not in st.session_state.box_select:
        re_init_mqtt = True

if re_init_mqtt is True and box_select is not None:
    st_print("Initializing mqtt client.")
    if "mqtt_client" in st.session_state:
        st.session_state.mqtt_client.loop_stop(force=True)
        st.write("Stopping mqtt before restarting")

    st.session_state.mqtt_client = get_mqtt_client(MQTT_UN, MQTT_PW, MQTT_CONN_STR, on_connect, on_message=on_message)
    st.session_state.mqtt_client.on_subscribe = on_subscribe
    st.session_state.mqtt_client.on_message = on_message
    st.session_state.mqtt_client.subscribe("boxbox/ground", qos=1)

    st.write("Finished initializing mqtt client")
    sleep(4.0)

st_print("pre asyncio")


# test = st.empty()
# cols = st.empty()
# strt_map = st.empty()
# anom_map = st.empty()
# test.text("Test text")
asyncio.run(mqtt_periodic())  # test, cols, strt_map, anom_map))
st_print("post asyncio")

