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


def update_led(strip, g, r, b):
    #TODO Make led code for dance
    strip.setPixelColor(i, Color(g, r, b))


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

        # Monitor time at start of dance
        start_time = time.time()

        # Segment booleans
        segment_one_done = False
        segment_two_done = False
        segment_three_done = False

        # Move booleans
        move_one_done = False
        move_two_done = False
        move_three_done = False

        # Starting move (Drive in a circle
        motor_values = str(1) + str(100) + str(1) + str(255)

        # Starting led values
        g = 0
        r = 255
        b = 0

        while True:
            self.handleMessages()

            current_time = time.time()

            # Actual motor update to Arduino
            self.serial.write(bytes(motor_values + ":", "utf-8"))

            # Led update
            update_led(strip, g, r, b)

            # Switch to spinning after 10 seconds
            if current_time - start_time > 10 and move_one_done is False:
                motor_values = str(1) + str(255) + str(0) + str(255)
                move_one_done = True
                print("Segment one done")
                continue

            if current_time - start_time > 20 and move_two_done is False:
                # TODO something else
                move_two_done = True
                print("Segment two done")
                continue

            # TODO: Arm controls

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
