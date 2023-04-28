# python3.6

import random
import time
import datetime

from paho.mqtt import client as mqtt_client

# broker = 'biorobsrvext1.epfl.ch'
broker = "128.178.148.27"
port = 1883
topic = "r15/stream/motor"
# generate client ID with pub prefix randomly
# client_id = f'python-mqtt-{random.randint(0, 1000)}'
client_id = 'python-mqtt-1'
username = 'roombots'
password = 'thn7YwgSt85ocxYY'
pos = []
UNIT = 13
global start

def connect_mqtt() -> mqtt_client:
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


def subscribe(client: mqtt_client):
    
    def on_message(client, userdata, msg):
        global start
        current = time.time()
        # diff.total_seconds()*1000
        print(f"{(current-start) * 1000}: Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        start = time.time()

    client.subscribe(topic, qos=0)
    client.on_message = on_message


def pos_subscriber(client: mqtt_client, topic):
    def on_message(client, userdata, msg):
        print(f"Motor positions: {msg.payload.decode()}")
        global pos 
        temp = msg.payload.decode().split(",")

        if check_outliers(temp):
            pos = [int(n) for n in temp]
              
    client.subscribe(topic)
    client.on_message = on_message


def check_outliers(msg):
    ''' Checks for outliers in return message from rXX/stream/ctrl
    Params
    ------
    msg (list): positions of motors

    Return
    ------
    (bool): whether the msg contains info for all 3 motors 
    '''
    for val in msg:
        if not val:
            return False
        for char in val:
            if char.isalpha():
                return False

    return True

def publish(client, topic, msg):
    '''
    mqtt publisher
    '''
    time.sleep(1)
    
    result = client.publish(topic, msg, qos=2)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Send `{msg}` to topic `{topic}`")
    else:
        print(f"Failed to send message to topic {topic}")

def run():
    client = connect_mqtt()
    publish(client, f'r{UNIT}/stream/ctrl', "start_motor_pos")
    # subscribe(client)
    pos_subscriber(client, f'r{UNIT}/stream/motor')

    client.loop_forever()


if __name__ == '__main__':
    # run()
    client = connect_mqtt()

    start = time.time()
    subscribe(client)

    client.loop_forever()