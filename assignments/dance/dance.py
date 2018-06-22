import sys
import time
import utils.communication as comm
import drivers.Motor.motor as motor
import serial
from neopixel import *

# TODO: Define how many leds for the dance
LED_COUNT = {}
LED_PIN = 18
LED_FREQ_HZ = 800000
LED_DMA = 10
LED_BRIGHTNESS = 50
LED_INVERT = False
LED_CHANNEL = 0


def update_led(strip):
    #TODO Make led code for dance
    {}


class Dance:
    def __init__(self):
        self.name = "dance"
        self.conn = None
        self.is_stopped = False
        self.left_joy_xpos = 512
        self.right_joy_xpos = 512
        self.serial = serial.Serial("/dev/ttyACM0")

        # Initiate neopixel led strip
        self.strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
        self.strip.begin()

    def run(self, conn):
        self.conn = conn
        comm.send_msg(self.conn, comm.MsgTypes.REPLY, "Started")

        while True:
            self.handleMessages()

            # TODO: Code dance and give values to serial.write for motor

            # TODO: Arm controls

            motor_values = str(int(round(left_speed))) + "," + str(left_polarity) + "," + str(int(round(right_speed))) + "," + str(right_polarity)

            comm.send_msg(self.conn, comm.MsgTypes.STATUS, motor_values)

            # Write to serial
            self.serial.write(bytes(motor_values + ";", "utf-8"))

            time.sleep(0.1)

    def handleMessages(self):
        if self.conn.poll():
            received = comm.recv_msg(self.conn)
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


dance = None


def name():
    return dance.name


def load():
    global dance
    dance = Dance()


def unload():
    {}


def start(conn):
    try:
        dance.run(conn)
    except KeyboardInterrupt:
        dance.unload()
        sys.exit(1)
