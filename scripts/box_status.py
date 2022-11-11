import os
import sys
dir_path = os.getcwd()
sys.path.append(dir_path)

import datetime
from time import sleep
import numpy as np
import streamlit as st
# import yaml
import asyncio

from scripts.mqtt import get_mqtt_client
from scripts.helpers import get_config



def st_print(text):
    st.text(text)


# print message, useful for checking if it was successful
def on_message(client, userdata, msg):
    st_print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))


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


async def mqtt_periodic(test):
    # col1, col2, col3 = st.columns(3)
    # col1.metric("Uptime", "0")
    # col2.metric("Wind", "9 mph", "-8%")
    # col3.metric("Humidity", "86%", "4%")
    start_time = datetime.datetime.now()
    while True:
        if "mqtt_client" in st.session_state:
            st.session_state.mqtt_client.loop(1.0)
            test.text(f"Uptime: {int((datetime.datetime.now() - start_time).seconds)} secs")
        else:
            test.text(f"Uptime: {int((datetime.datetime.now() - start_time).seconds)} secs")
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


test = st.empty()
test.text("Test text")
asyncio.run(mqtt_periodic(test))
st_print("post asyncio")

