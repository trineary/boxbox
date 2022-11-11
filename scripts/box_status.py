import os
import sys
dir_path = os.getcwd()
sys.path.append(dir_path)

from time import sleep
import numpy as np
import streamlit as st
# import yaml

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


VIEWER_WIDTH = 600

title = st.title("BoxBox Status")

config = get_config("./config/config.yml")
st_print(str(config['topics']))

# Initialize MQTT connection
st_print(st.session_state)
tf = 'mqtt_client' not in st.session_state
st_print(str(tf))

# Let user select which box to listen to
box_select = st.selectbox('BoxBox Selection:', config['topics'])
st.write('Selection: ', box_select)


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

MQTT_UN = st.secrets["MQTT_UN"]
MQTT_PW = st.secrets["MQTT_PW"]
MQTT_CONN_STR = st.secrets["MQTT_CONN_STR"]


def main():
    # To restart client, 'Stop' the streamlit from running and refresh the page

    # if 'mqtt_client' not in st.session_state:
    st_print("Initializing mqtt client.")
    # (mqtt_un, mqtt_pw, mqtt_conn_str, on_connect=None,
    mqtt_client = get_mqtt_client(MQTT_UN, MQTT_PW, MQTT_CONN_STR, on_connect, on_message=on_message)
    mqtt_client.on_subscribe = on_subscribe
    mqtt_client.on_message = on_message
    mqtt_client.subscribe("boxbox/ground", qos=1)
    sleep(4.0)
    mqtt_client.loop_forever()


if __name__ == "__main__":
    main()
