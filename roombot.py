# Roombot class
from utils import *
import time
import numpy as np
import threading

from paho.mqtt import client as mqtt_client

class Roombot:
    def __init__(self, id, client, timeout):
        self.id = id
        self.motors = ["M0", "M1", "M2"]
        self.pos = []
        self.client = client
        self.start_time = np.zeros((3))
        self.end_time = np.zeros((3))
        self.received = np.zeros((3), dtype=int) # bool values
        self.timeout = timeout #s
        self.payloads = [""] * 3
        self.data = []
        self.state = 0
        self.interval = self.timeout

    def set_acm(self, value):
        publish(self.client, f'r{self.id}/com/acm/X0', "p" + str(value[0]))
        publish(self.client, f'r{self.id}/com/acm/X1', "p" + str(value[1]))


    def check_outliers(self, msg):
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
    

    def stream_position(self, topic):
        def on_message(client, userdata, msg):
            # print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
            temp = msg.payload.decode().split(",")

            if self.check_outliers(temp):
                self.pos = [int(n) for n in temp]
                
        self.client.subscribe(topic)
        self.client.on_message = on_message


    def subscribe_pos_M0(self):
        def on_message(client, userdata, msg):
            # print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
            self.received[0] = 1
            self.payloads[0] = msg.payload.decode()
            
            self.check_ping(0)

        self.client.subscribe(f"r{self.id}/resp/motor/M0")
        self.client.on_message = on_message


    def subscribe_pos_M1(self):
        def on_message(client, userdata, msg):
            print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

        self.client.subscribe(f"r{self.id}/resp/motor/M1")
        self.client.on_message = on_message


    def check_pos(self, value, margin=3):
        ''' Check if target positions reached
        Params
        ------
        goal (list): target positions of motors
        '''
        if len(self.pos) != 3:
            print("ERROR reading current position!")
        else:
            thresh_upper = [x + margin for x in value] # goal should have 3 motors
            thresh_lower = [x - margin for x in value]
        
            for i in range(len(value)):
                while (self.pos[i] <= thresh_lower[i]) or (self.pos[i] >= thresh_upper[i]):
                    print("Waiting for M{} to reach position {} from {}".format(i, value[i], self.pos[i]))
                    publish(self.client, f'r{self.id}/com/motor/M{i}', "pa" + str(value[i]))
                    time.sleep(1)    


    def ping(self, motor):
        self.start_time = round(time.time() * 1000)
        publish(self.client, f'r{self.id}/com/motor/M{motor}', "pa" + str(0))
        timer = threading.Timer(self.timeout, self.callback())

    
    def callback(self):
        # print(self.id, self.interval, self.state, self.payloads[0])
        self.data.append([self.interval, self.state, self.payloads[0]])
        self.interval = self.timeout
        self.state = 0
        self.payloads = [""] * 3


    def check_ping(self, motor):
        self.interval = round(time.time() * 1000) - self.start_time
        if (self.payloads[motor] == "*"):
            self.state = 1
        else:
            self.state = 2 # indicates error msg

        



    def reset_pos(self):
        ''' 
        Reset id to 0 position
        '''
        value = [0, 0, 0]

        publish(self.client, f'r{self.id}/com/motor/M0', "pa" + str(value[0]))
        publish(self.client, f'r{self.id}/com/motor/M1', "pa" + str(value[1]))
        publish(self.client, f'r{self.id}/com/motor/M2', "pa" + str(value[2]))
        
        self.check_pos(value)


    def set_pos(self, value):
        ''' Set all motors to target position
        Params
        ------
        goal (list): target motor positions
        '''
        for i in range(len(self.motors)):
            self.start_time[i] = round(time.time() * 1000) # current milli time
            publish(self.client, f'r{self.id}/com/motor/{self.motors[i]}', "pa" + str(value[i]))

        # self.check_pos(value) # Loops to check if position for each motor reached


    def set_gains(self, gains):
        # Change gains
        # gains = [100, 7, 250]

        for motor in self.motors:
            publish(self.client, f'r{self.id}/com/motor/{motor}', "enf0")
        #     get_pos_filter(client, motor)
            time.sleep(2)
        
            # change pid values
            publish(self.client, f'r{self.id}/com/motor/{motor}', f"pakp{gains[0]}")
            publish(self.client, f'r{self.id}/com/motor/{motor}', f"paki{gains[1]}")
            publish(self.client, f'r{self.id}/com/motor/{motor}', f"pakd{gains[2]}")
            
            self.get_gains(motor)
            time.sleep(1)


    def get_gains(self, motor):
        # query pid values
        topic = f"r{self.id}/com/any"

        subscribe(self.client, f"r{self.id}/resp/any")

        publish(self.client, topic, f"?{motor}-{self.id}pakp")
        publish(self.client, topic, f"?{motor}-{self.id}paki")
        publish(self.client, topic, f"?{motor}-{self.id}pakd")


    def get_pos_filter(self, motor):
        # query pid values
        topic = f"r{self.id}/com/any"
        subscribe(self.client, f"r{self.id}/resp/any")
        publish(self.client, topic, f"?{motor}-{self.id}enf")


    def stream_pos(self):
        publish(self.client, f'r{self.id}/stream/ctrl', "start_motor_pos")
        self.stream_position(f'r{self.id}/stream/motor')
        time.sleep(1)


    def set_leds(self, msg):
        publish(self.client, f'r{self.id}/com/led/L0', msg)
        publish(self.client, f'r{self.id}/com/led/L1', msg)
