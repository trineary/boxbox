import os
import sys
dir_path = os.getcwd()
sys.path.append(dir_path)

import time
from time import sleep

import numpy as np
import streamlit as st
# import yaml
from paho.mqtt import client as mqtt
import paho.mqtt.client as paho

from scripts.mqtt import get_mqtt_client
from scripts.helpers import get_config


CONFIG_FILE_PATH = os.getenv("MQTT_BOXBOX_CONFIG", "./config/config.yml")
CONFIG = get_config(CONFIG_FILE_PATH)

MQTT_BROKER = CONFIG["mqtt"]["broker"]
MQTT_PORT = CONFIG["mqtt"]["port"]
MQTT_QOS = CONFIG["mqtt"]["QOS"]
MQTT_UN = CONFIG["mqtt"]["un"]
MQTT_PW = CONFIG["mqtt"]["pw"]
MQTT_CONN_STR = CONFIG["mqtt"]["connect_str"]

MQTT_TOPIC = CONFIG["boxbox"]["mqtt_topic"]

VIEWER_WIDTH = 600

title = st.title(MQTT_TOPIC)


def st_print(text):
    st.text(text)


# print which topic was subscribed to
def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    st_print("-"*100)
    st_print("Subscribed: " + str(mid) + " " + str(granted_qos))
    st_print("User data: ")
    st_print("-" * 100)


# Initialize MQTT connection
st_print(st.session_state)
tf = 'mqtt_client' not in st.session_state
st_print(str(tf))

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

#
# def get_mqtt_client():
#     """Return the MQTT client object."""
#     _mqtt_client = mqtt.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
#     _mqtt_client.connected_flag = False  # set flag
#     _mqtt_client.on_connect = on_connect
#     # _mqtt_client.on_subscribe = on_subscribe
#
#     # TODO: Move pw/un/connect info out of code
#     # enable TLS for secure connection
#     _mqtt_client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS)
#     # set username and password
#     _mqtt_client.username_pw_set("saqboxbox", "B0xB0x112233")
#     # connect to HiveMQ Cloud on port 8883 (default for MQTT)
#     _mqtt_client.connect("1b340fc437084fd7bd0e181716709ad2.s2.eu.hivemq.cloud", 8883)
#
#     # setting callbacks, use separate functions like above for better visibility
#     _mqtt_client.on_subscribe = on_subscribe
#     _mqtt_client.on_message = on_message
#     # _mqtt_client.on_publish = _on_subscribe
#     return _mqtt_client

# # if 'mqtt_client' not in st.session_state:
# st_print("Initializing mqtt client.")
# st.session_state.mqtt_client = get_mqtt_client()
# # st.session_state.mqtt_client.on_subscribe = on_subscribe
# st.session_state.mqtt_client.subscribe("boxbox/ground", qos=1)
# st.session_state.mqtt_client.loop_forever()

st_print("test print")

# viewer = st.image(get_random_numpy(), width=VIEWER_WIDTH)

def main():
    # client = get_mqtt_client()
    # client.on_message = on_message
    # client.connect(MQTT_BROKER, port=MQTT_PORT)
    # client.subscribe(MQTT_TOPIC)
    # time.sleep(4)  # Wait for connection setup to complete
    # client.loop_forever()

    # if 'mqtt_client' not in st.session_state:
    st_print("Initializing mqtt client.")
    mqtt_client = get_mqtt_client(on_connect)
    mqtt_client.on_subscribe = on_subscribe
    mqtt_client.on_message = on_message
    mqtt_client.subscribe("boxbox/ground", qos=1)
    sleep(4.0)
    mqtt_client.loop_forever()


if __name__ == "__main__":
    main()
