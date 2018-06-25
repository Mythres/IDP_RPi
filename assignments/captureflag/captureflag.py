import sys
import time
import utils.communication as comm
import drivers.Motor.motor as motor
import serial


class Captureflag:
    def __init__(self):
        self.name = "captureflag"
        self.conn = None
        self.is_stopped = False
        self.left_joy_xpos = 512
        self.right_joy_xpos = 512
        self.left_joy_ypos = 512
        self.right_joy_ypos = 512
        self.serial = serial.Serial("/dev/ttyACM0")

    def run(self, conn):
        self.conn = conn
        comm.send_msg(self.conn, comm.MsgTypes.REPLY, "Started")
        motor_driver = motor.Motor()

        while True:
            self.handleMessages()

            # TODO: Arm controls

            # Update motor
            left_speed, left_polarity, right_speed, right_polarity = motor_driver.update(self.left_joy_xpos, self.right_joy_xpos)

            motor_values = str(int(round(left_speed))) + "," + str(left_polarity) + "," + str(int(round(right_speed))) + "," + str(right_polarity)

            comm.send_msg(self.conn, comm.MsgTypes.STATUS, motor_values)

            # Write to serial
            self.serial.write(bytes(motor_values + ";", "utf-8"))

            time.sleep(0.1)

    def handleMessages(self):
        if self.conn.poll():
            received = comm.recv_msg(self.conn)
            received_split = received.split(" ")
            if received_split[0] == "controller":
                controller_values = received_split[1].split(",")
                print(received_split)

                print(controller_values)

                # Grab positions
                self.left_joy_ypos = int(controller_values[0].split(":")[1].split(",")[0])
                self.right_joy_ypos = int(controller_values[1].split(":")[1].split(",")[0])
                self.left_joy_xpos = int(controller_values[0].split(":")[1].split(",")[1])
                self.right_joy_xpos = int(controller_values[1].split(":")[1].split(",")[1])

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


captureflag = None


def name():
    return captureflag.name


def load():
    global captureflag
    captureflag = Captureflag()


def unload():
    {}


def start(conn):
    try:
        captureflag.run(conn)
    except KeyboardInterrupt:
        captureflag.unload()
        sys.exit(1)
