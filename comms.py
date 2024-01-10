
import time
import numpy as np
import pandas as pd
import random
from paho.mqtt import client as mqtt_client
import os

import asyncio_mqtt as aiomqtt
import paho.mqtt as mqtt
import asyncio

from utils import *
from roombot import Roombot
from password import *

# USER DEFINED
save = True
verbose = False
continuous = False
timeout = 1 #second
trials = 55000
qos = 0
err_tresh = 10
save_path = "./data/test_bat"


# MQTT CONSTANTS
broker = "128.178.148.27"
port = 1883

# global vars
data = {
        # "13": [], 
        # "15": [],
        # "16": [],
        "19": []
        }

modules = data.keys()

global start_time
global count
global check
check = set()
global position 
position = 0

async def listen(module):
    global start_time
    global count

    state = 0
    topic = f"r{module}/resp/motor/M0"
    async with aiomqtt.Client(broker) as client:
        payload = "pa" + str(position)
        await client.publish(f"r{module}/com/motor/M0", payload=payload, qos=qos)
        start_time = time.time() * 1000

        async with client.messages() as messages:
            await client.subscribe(topic, qos=qos)
            async for message in messages:
                if message.topic.matches(topic):
                    interval = time.time() * 1000 - start_time
                    pyld = message.payload.decode()
                    # print(topic, pyld)
                    
                    if (pyld == "*"):
                        state = 1
                    else:
                        state = 2 # indicates error msg
                    # print(f"[r{module}] {pyld}")
                    # data[module].append()
                    # data[module].append([count, interval, state, pyld])

                    return interval, state, pyld



async def main():
    global start_time
    global count
    global check
    global position

    error = 0
    loop = asyncio.get_event_loop()

    async with aiomqtt.Client(broker) as client:
        # initiate robots
        robots = []
        for module in modules:
            robots.append(Roombot(int(module), client, timeout))

        # trials
        
        print("[INFO] starting trials")
        for i in range(trials):
            if i%500 == 0:
                print(f"Iter {i}")
            # listeners = [loop.create_task(listen(id)) for id in modules]
            listeners = []
            for m in modules:
                t = loop.create_task(listen(m))
                t.name = m
                listeners.append(t)

            count = i 
            # start_time = round(time.time() * 1000)
            # for module in modules:
                
            
            done, pending = await asyncio.wait(listeners, timeout=timeout)
            position += 1
            if position > 3600:
                position = 0
            
            # checks if a unit has been unresponsive for several continuous pings
            for task in done:
                interval, state, pyld = task.result()
                data[task.name].append([count, interval, state, pyld])
            
            for task in pending:
                if verbose:
                    print(count, task.name)
                data[task.name].append([count, timeout*1000, 0, ""])

            for task in listeners:
                task.cancel()

            if len(pending) > 0:
                error += 1
            else:
                error = 0
        
            if error > err_tresh:
                print("[ERROR] one or more modules is unresponsive!")
                break

            

    header = ["trial", "interval (ms)", "state", "payload"]
    for m in modules:
        print(f"[INFO] Module {m}")
        df = pd.DataFrame(data[m], columns=header)

        # save data
        if save:
            timestr = time.strftime("%Y%m%d-%H%M%S")
            print(f"[INFO] saving module {m} data...")
            filepath = os.path.join(save_path, f"r{m}_qos{qos}_{timestr}.csv")
            if continuous:
                df.to_csv(filepath, index=True, mode='a', header=False) 
            else:
                df.to_csv(filepath, index=True)
        
        print(df)

   
            

    # # end tasks
    # listener
              

if __name__ == '__main__':
    asyncio.run(main())