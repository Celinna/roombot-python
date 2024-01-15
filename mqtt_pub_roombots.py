
import time
import numpy as np
import random
from paho.mqtt import client as mqtt_client

from utils import *
from roombot import Roombot
from password import *

# USER DEFINED
id = 16

# broker = "128.178.148.27"

# MQTT CONSTANTS
client_id = f'python-mqtt-{random.randint(0, 1000)}'
port = 1883


def lift_box(robot):
    '''
    For lifting box
    '''
    robot.reset_pos() 

    # Set ACM to grip table
    # publish(client, f'r{id}/com/acm/X1', "p50")

    # Grab box
    robot.set_pos([0, 0, 1200])
    robot.set_acm([50, 0])

    # Lift box
    robot.set_pos([-1200, 0, 1200])
    robot.set_pos([-1200, 0, 0])
    robot.reset_pos() 
    robot.set_acm([0, 0])



def circle_walk(robot, num_steps=1):
    # Reset
    robot.set_acm([0, 0])
    time.sleep(2)
    robot.reset_pos()
    time.sleep(2)

    # Initial position
    robot.set_acm([50, 0])
    time.sleep(2)
    robot.set_pos([0, 1800, -1200])

    # Lower 
    robot.set_pos([1200, 1800, -1200])

    # Walk
    for i in range(num_steps):
        circle_walk_step(robot)


def circle_walk_step(robot):
    # Change ACMs
    robot.set_acm([0, 50])
    time.sleep(2)

    # Go upright 
    robot.set_pos([1200, 1800, 0])

    # Lower 
    circle_walk_lower(robot, motorID=2)

    # Change ACMs
    robot.set_acm([50, 0])

    # Go upright
    robot.set_pos([0, 1800, 1200])

    # Lower
    circle_walk_lower(robot, motorID=0)


def circle_walk_lower(robot, motorID):
    if motorID == 2:
        publish(robot.client, f'r{id}/com/motor/M0', "pa" + str(-1200))
        time.sleep(2.5)
        publish(robot.client, f'r{id}/com/motor/M2', "pa" + str(1200))
        robot.check_pos([-1200, 1800, 1200]) # Loops to check if position for each motor reached
    else:
        publish(robot.client, f'r{id}/com/motor/M2', "pa" + str(-1200))
        time.sleep(2.5)
        publish(robot.client, f'r{id}/com/motor/M0', "pa" + str(1200))
        robot.check_pos([1200, 1800, -1200]) # Loops to check if position for each motor reached

def test(robot):
    publish(robot.client, f'r{id}/com/motor/M0', "pa" + str(100))
    time.sleep(1)
    publish(robot.client, f'r{id}/com/motor/M0', "pa" + str(200))
    time.sleep(1)
    publish(robot.client, f'r{id}/com/motor/M0', "pa" + str(300))
    time.sleep(1)
    robot.set_pos([0, 0, 0])


if __name__ == '__main__':
    client = connect_mqtt(client_id, username, password, broker, port)
    client.loop_start()
    
    robot = Roombot(id, client)

    robot.subscribe_pos(f"r{id}/resp/motor/M0")

    # Indicate id on
    robot.set_leds("cg")
    
    # Stream motor locations
    # robot.stream_pos()

    # Main function
    # circle_walk(robot, num_steps=1)
    test(robot)

    # Indicate actions done
    robot.set_leds("cw")

    client.loop_stop() 