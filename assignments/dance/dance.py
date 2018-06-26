import sys
import time
import utils.communication as comm
import drivers.Motor.motor as motor
import serial
from drivers.Motor import MotorDirections
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
    # TODO Make led code for dance
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
        self.strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS,
                                       LED_CHANNEL)
        self.strip.begin()
        self.motor = motor.Motor(100, 25)

    def run(self, conn):
        self.conn = conn
        comm.send_msg(self.conn, comm.MsgTypes.REPLY, "Started")

        # Monitor time at start of dance
        start_time = time.time()

        # Starting led values
        g = 0
        r = 255
        b = 0

        while True:
            self.handleMessages()

            current_time = time.time()

            if current_time - start_time < 5:
                print("backward")
                ls, lp, rs, rp = self.motor.move_backward(250, True)
            elif current_time - start_time < 10:
                print("forward")
                ls, lp, rs, rp = self.motor.move_forward(100, True)
            elif current_time - start_time < 15:
                print("forward right")
                ls, lp, rs, rp = self.motor.rotate_around_axis(100, MotorDirections.RIGHT,
                                                               autoTransform=True)
            elif current_time - start_time < 20:
                print("forward left")
                ls, lp, rs, rp = self.motor.rotate_around_axis(100, MotorDirections.LEFT,
                                                               autoTransform=True)
            else:
                self.motor.update(0, 0)
                if current_time - start_time < 25:
                    break
                else:
                    continue

            vals = self.motor.get_motor_values_string(ls, lp, rs, rp)
            # if vals is not motor_values:
            # print(vals)
            motor_values = vals

            comm.send_msg(self.conn, comm.MsgTypes.STATUS, motor_values)
            # Updates the motor values to Arduino
            self.serial.write(bytes(motor_values + ";", "utf-8"))
            update_led(self.strip, g, r, b)

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
