# Created by Yi Zhou (Celinna) Ju
# April 28, 2023
# Util funcs
from paho.mqtt import client as mqtt_client
import time
import numpy as np


def connect_mqtt(client_id, username, password, broker, port):
    '''
    Connect to mqtt broker with specified client
    '''
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def publish(client, topic, msg):
    '''
    mqtt publisher
    '''
    time.sleep(1)
    
    result = client.publish(topic, msg, qos=2)
    status = result[0]

    # if status == 0:
    #     print(f"Send `{msg}` to topic `{topic}`")
    # else:
    #     print(f"Failed to send message to topic {topic}")


def subscribe(client: mqtt_client, topic):
    def on_message(client, userdata, msg):
        payload = msg.payload.decode()
        if payload:
            print(f"Received `{msg.payload.decode()}` from `{topic}` topic")

    client.subscribe(topic)
    client.on_message = on_message