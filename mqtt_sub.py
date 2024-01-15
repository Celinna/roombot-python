# python3.6

import random
import time
import datetime
from password import *
from utils import *

from paho.mqtt import client as mqtt_client


# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 1000)}'

global start


if __name__ == '__main__':
    client = connect_mqtt(client_id, username, password, broker, port)

    start = time.time()
    subscribe(client, "/pub")

    client.loop_forever()