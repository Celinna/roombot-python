
import time
import numpy as np
import random

from utils import *
from password import *

client_id = f'python-mqtt-{random.randint(0, 1000)}'


def publish(client, topic, msg):
    '''
    mqtt publisher
    '''
    time.sleep(1)
    
    result = client.publish(topic, msg, qos=2)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Sent `{msg}` to topic `{topic}`")
    else:
        print(f"Failed to send message to topic {topic}")

if __name__ == '__main__':
    print(broker)
    client = connect_mqtt(client_id, username, password, broker, port)
    client.loop_start()
    
    publish(client, '/pub', "PYTHON hello!")
    client.loop_stop() 
    # client.loop_forever()