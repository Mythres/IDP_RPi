import sys
import time
import utils.communication as comm
import drivers.Motor.motor as motor


class Motor:
    def __init__(self):
        self.name = "motor"
        self.conn = None
        self.is_stopped = False
        self.left_joy_xpos = None
        self.right_joy_xpos = None

    def run(self, conn):
        self.conn = conn
        comm.send_msg(self.conn, comm.MsgTypes.REPLY, "Started")
        motor_driver = motor.Motor()

        while True:
            self.handleMessages()

            motor_values = ""
            motor_driver.update(self.left_joy_xpos, self.right_joy_xpos)

            # Update motor
            left_speed, left_polarity, right_speed, right_polarity = motor.update(self.left_joy_xpos, self.right_joy_xpos)

            motor_values.append(left_speed + "," + left_polarity + "," + right_speed + "," + right_polarity + ";")

            # Write to serial
            self.serial.write(bytes(motor_values, "utf-8"))

    def handleMessages(self):
        if self.conn.poll():
            received = comm.recv_msg(self.conn)
            received_split = received.split(" ")
            if received_split[0] == "controller":
                controller_values = ",".join(received_split[1:]) + ";"
                print(received_split)

                # Grab positions
                self.left_joy_xpos = int(controller_values[0].split(":")[1])
                self.right_joy_xpos = int(controller_values[1].split(":")[1])

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


motor = None


def name():
    return motor.name


def load():
    global motor
    motor = Motor()


def unload():
    {}


def start(conn):
    try:
        motor.run(conn)
    except KeyboardInterrupt:
        motor.unload()
        sys.exit(1)
