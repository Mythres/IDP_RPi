import sys
import time
import utils.communication as comm
import drivers.Motor.motor as motor
import serial
from neopixel import *

LED_COUNT = 20
LED_PIN = 18
LED_FREQ_HZ = 800000
LED_DMA = 10
LED_BRIGHTNESS = 50
LED_INVERT = False
LED_CHANNEL = 0


def update_led(strip):
    #TODO Make led code for enter the arena
    {}


class Arena:
    def __init__(self):
        self.name = "arena"
        self.conn = None
        self.is_stopped = False
        self.left_joy_xpos = 512
        self.right_joy_xpos = 512
        self.left_joy_ypos = 512
        self.right_joy_ypos = 512
        self.serial = serial.Serial("/dev/ttyACM0")
        self.motor_driver = motor.Motor(150, 40)

        # Initiate neopixel led strip
        self.strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
        self.strip.begin()

    def run(self, conn):
        self.conn = conn
        comm.send_msg(self.conn, comm.MsgTypes.REPLY, "Started")

        while True:
            self.handleMessages()

    def handleMessages(self):
        if self.conn.poll():
            received = comm.recv_msg(self.conn)
            received_split = received.split(" ")
            if received_split[0] == "controller":
                controller_values = received_split[1].split("-")

                # Grab positions
                self.right_joy_ypos = int(controller_values[0].split(":")[1].split(",")[0])
                self.left_joy_ypos = int(controller_values[1].split(":")[1].split(",")[0])
                self.right_joy_xpos = int(controller_values[0].split(":")[1].split(",")[1])
                self.left_joy_xpos = int(controller_values[1].split(":")[1].split(",")[1])

                # Update motor
                left_speed, left_polarity, right_speed, right_polarity = self.motor_driver.update(self.left_joy_ypos, self.right_joy_ypos)

                motor_values = str(int(round(left_speed))) + "," + str(left_polarity) + "," + str(int(round(right_speed))) + "," + str(right_polarity)

                comm.send_msg(self.conn, comm.MsgTypes.STATUS, motor_values)

                # Write to serial
                self.serial.write(bytes(motor_values + ";", "utf-8"))

                comm.send_msg(self.conn, comm.MsgTypes.REPLY, "Received")
            if received == "Stop":
                self.is_stopped = True
                comm.send_msg(self.conn, comm.MsgTypes.REPLY, "Stopped")
            elif received == "Unload":
                self.unload()
                comm.send_msg(self.conn, comm.MsgTypes.REPLY, "Unloaded")
                sys.exit()

        while self.is_stopped:
            received = comm.recv_msg(self.conn)
            if received == "Start":
                self.is_stopped = False
                comm.send_msg(self.conn, comm.MsgTypes.REPLY, "Started")
            elif received == "Unload":
                self.unload()
                comm.send_msg(self.conn, comm.MsgTypes.REPLY, "Unloaded")
                sys.exit()

    def unload(self):
        {}


arena = None


def name():
    return arena.name


def load():
    global arena
    arena = Arena()


def unload():
    {}


def start(conn):
    try:
        arena.run(conn)
    except KeyboardInterrupt:
        arena.unload()
        sys.exit(1)
