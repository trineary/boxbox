
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
import streamlit.components.v1 as components
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
    col1, col2, col3, col4, col5 = cnt_cols.columns(5)
    col1.metric("VMR Cnt", "0")
    col2.metric("MFAM Cnt", "0")
    col3.metric("VN3xx Cnt", "0")
    col4.metric("RAM %", "0")
    col5.metric("CPU %", "0")

    data_cols = st.empty()
    col1, col2, col3, col4 = data_cols.columns(4)
    col1.metric("Sat Cnt", "0")
    col2.metric("Air Temp", "0")
    col3.metric("Uptime", "0")
    col4.metric("File Cnt", "-1")

    gps_cols = st.empty()
    col1, col2 = gps_cols.columns(2)
    col1.metric("GPS Lat", "0")
    col2.metric("GPS lon", "0")

    pred_cols = st.empty()
    col1, col2 = pred_cols.columns(2)
    col1.metric("Pred Lat", "0")
    col2.metric("Pred Lon", "0")

    mag_cols = st.empty()
    mfam1, mfam2, utc, lat, lon = mag_cols.columns(5)
    mfam1.metric("MFAM1", -1)
    mfam2.metric("MFAM2", -1)
    utc.metric("UTC", -1)
    lat.metric("LAT", -1)
    lon.metric("LON", -1)

    vmr_cols = st.empty()
    vmr1, vmr3, vmr5, vmr7 = vmr_cols.columns(4)
    vmr1.metric("VMR1", -1)
    vmr3.metric("VMR3", -1)
    vmr5.metric("VMR5", -1)
    vmr7.metric("VMR7", -1)

    strt_map = st.empty()
    start_time = datetime.datetime.now()
    test = st.empty()
    dict_str = st.empty()
    lat_lons = None

    flt_aware = st.empty()
    # "https://www.planeflighttracker.com/2013/12/flight-number-search.html"
    # components.iframe("https://www.planeflighttracker.com/2013/12/flight-number-search.html", width=675, height=410)
    components.iframe("http://embed.flightaware.com/commercial/integrated/web/delay_map.rvt", width=675, height=410)

    while True:
        if "mqtt_client" in st.session_state:
            st.session_state.mqtt_client.loop(1.0)
            test.text(f"UI uptime: {int((datetime.datetime.now() - start_time).seconds)} secs")
            if boxbox_dict is not None:
                boxbox_dict = boxbox_dict.replace("'", '"')
                # dict_str.text(f"boxbox_dict: {boxbox_dict}")
                box_data = json.loads(boxbox_dict)

                # Update data in columns
                col1, col2, col3, col4, col5 = cnt_cols.columns(5)
                if "VMR_PUB_Cnt" in box_data: col1.metric("VMR Cnt/sec", box_data["VMR_PUB_Cnt"])
                else: col1.metric("VMR Cnt", -1)
                if "MFAM_PUB_Cnt" in box_data: col2.metric("MFAM Cnt/sec", box_data["MFAM_PUB_Cnt"])
                else: col2.metric("MFAM Cnt", -1)
                if "VN3xx_PUB_Cnt" in box_data: col3.metric("VN3xx Cnt/sec", box_data["VN3xx_PUB_Cnt"])
                else: col3.metric("VN3xx Cnt", -1)
                if "ram_load" in box_data: col4.metric("RAM %", box_data["ram_load"])
                else: col4.metric("RAM %", -1)
                if "cpu_load" in box_data: col5.metric("CPU %", box_data["cpu_load"])
                else: col5.metric("CPU %", -1)

                col1, col2, col3, col4 = data_cols.columns(4)
                if "num_sats" in box_data: col1.metric("Sat Cnt", box_data["num_sats"])
                else: col1.metric("Sat Cnt", -1)
                if "air_temp" in box_data: col2.metric("Air Temp", box_data["air_temp"])
                else: col2.metric("Air Temp", -1)
                if "up_time" in box_data: col3.metric("Uptime", box_data["up_time"])
                else: col3.metric("Uptime", -1)
                if "file_cnt" in box_data: col4.metric("File Cnt", box_data["file_cnt"])
                else: col4.metric("File Cnt", -1)

                # Plot lat/lon
                gps_lat, gps_lon, pred_lat, pred_lon = -1, -1, -1, -1
                if 'gps_lat' in box_data and 'gps_lon' in box_data and 'pred_lat' in box_data and 'pred_lon' in box_data:
                    gps_lat, gps_lon, pred_lat, pred_lon = float(box_data['gps_lat']), float(box_data['gps_lon']), float(box_data['pred_lat']), float(box_data['pred_lon'])

                col1, col2 = gps_cols.columns(2)
                col1.metric("GPS Lat", gps_lat)
                col2.metric("GPS Lon", gps_lon)

                col1, col2 = pred_cols.columns(2)
                col1.metric("Pred Lat", pred_lat)
                col2.metric("Pred Lon", pred_lon)

                # mfam1, mfam2, vmr1, vmr3, vmr5, vmr7 = sensor_cols.columns(6)
                mfam1, mfam2, utc, lat, lon = mag_cols.columns(5)
                if "mag1" in box_data: mfam1.metric("MFAM1", int(box_data["mag1"]))
                else: mfam1.metric("MFAM1", -1)
                if "mag2" in box_data: mfam2.metric("MFAM2", int(box_data["mag2"]))
                else: mfam2.metric("MFAM2", -1)
                if "gps_str" in box_data:
                    gps_list = box_data["gps_str"].split(",")
                    data_str = f"UTC: {gps_list[1]}, \nLAT:{gps_list[3]}{gps_list[4]}, Lon:{gps_list[5]}{gps_list[6]}"
                    utc.metric("UTC", f"{gps_list[1]}")
                    lat.metric("LAT", f"{gps_list[3]}{gps_list[4]}")
                    lon.metric("LON", f"{gps_list[5]}{gps_list[6]}")
                else:
                    utc.metric("UTC", -1)
                    lat.metric("LAT", -1)
                    lon.metric("LON", -1)

                vmr1, vmr3, vmr5, vmr7 = vmr_cols.columns(4)
                if "vmr1" in box_data: vmr1.metric("VMR1", int(box_data["vmr1"]))
                else: vmr1.metric("VMR1", -1)
                if "vmr3" in box_data: vmr3.metric("VMR3", int(box_data["vmr3"]))
                else: vmr3.metric("VMR3", -1)
                if "vmr5" in box_data: vmr5.metric("VMR5", int(box_data["vmr5"]))
                else: vmr5.metric("VMR5", -1)
                if "vmr7" in box_data: vmr7.metric("VMR7", int(box_data["vmr7"]))
                else: vmr7.metric("VMR7", -1)

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

