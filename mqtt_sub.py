# python3.6

import random
import time
import datetime
from password import *
from utils import *

# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 1000)}'

global start


if __name__ == '__main__':
    client = connect_mqtt(client_id, username, password, broker, port)

    start = time.time()
    subscribe(client, "pubs/")

    client.loop_forever()