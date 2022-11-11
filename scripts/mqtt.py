
"""
Code to initialize MQTT client.
"""

from paho.mqtt import client as mqtt
import paho.mqtt.client as paho


def on_disconnect(client, userdata,rc=0):
    client.loop_stop()


def get_mqtt_client(mqtt_un, mqtt_pw, mqtt_conn_str, on_connect=None, on_subscribe=None, on_message=None, on_publish=None):
    """Return the MQTT client object."""
    _mqtt_client = mqtt.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
    _mqtt_client.connected_flag = False  # set flag

    # setting callbacks, use separate functions like above for better visibility
    _mqtt_client.on_subscribe = on_subscribe
    _mqtt_client.on_message = on_message
    _mqtt_client.on_publish = on_publish
    _mqtt_client.on_connect = on_connect
    _mqtt_client.on_disconnect = on_disconnect

    # enable TLS for secure connection
    _mqtt_client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS)
    # set username and password
    _mqtt_client.username_pw_set(mqtt_un, mqtt_pw)
    # connect to HiveMQ Cloud on port 8883 (default for MQTT)
    _mqtt_client.connect(mqtt_conn_str, 8883)

    return _mqtt_client


def test_mqtt_sub():
    from time import sleep
    import os
    import sys
    dir_path = os.getcwd()
    sys.path.append(dir_path)

    import streamlit as st
    from paho.mqtt import client as mqtt

    from scripts.helpers import get_config

    CONFIG_FILE_PATH = os.getenv("MQTT_BOXBOX_CONFIG", "../config/config.yml")
    CONFIG = get_config(CONFIG_FILE_PATH)

    MQTT_BROKER = CONFIG["mqtt"]["broker"]
    MQTT_PORT = CONFIG["mqtt"]["port"]
    MQTT_QOS = CONFIG["mqtt"]["QOS"]
    MQTT_UN = CONFIG["mqtt"]["un"]
    MQTT_PW = CONFIG["mqtt"]["pw"]
    MQTT_CONN_STR = CONFIG["mqtt"]["connect_str"]

    MQTT_TOPIC = CONFIG["boxbox"]["mqtt_topic"]

    VIEWER_WIDTH = 600

    def st_print(text):
        print(text)

    # print which topic was subscribed to
    def on_subscribe(client, userdata, mid, granted_qos, properties=None):
        st_print("-" * 100)
        st_print("Subscribed: " + str(mid) + " " + str(granted_qos))
        st_print("User data: ")
        st_print("-" * 100)

    # Initialize MQTT connection
    st_print("st.session_state")
    # tf = 'mqtt_client' not in st.session_state
    # st_print(str(tf))

    # if 'mqtt_client' not in st.session_state:
    st_print("Initializing mqtt client.")
    mqtt_client = get_mqtt_client()
    # mqtt_client.on_subscribe = on_subscribe
    mqtt_client.subscribe("boxbox/ground", qos=1)
    mqtt_client.loop_start()

    sleep(5.0)

    mqtt_client.loop_stop()

    st_print("test print")
    pass


# if __name__ == "__main__":
#     test_mqtt_sub()
