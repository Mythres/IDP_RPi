import sys
import assignments.ass1.ax12.ax12 as ax12
import utils.communication as comm
import serial
from time import sleep

class Ass1:
    def __init__(self):
        self.name = "ass1"
        self.conn = None
        self.is_stopped = False
        self.servos = ax12.Ax12()
        self.moving = False
        self.serial = serial.Serial("/dev/ttyUSB0")

    def run(self, conn):
        self.conn = conn
        comm.send_msg(self.conn, comm.MsgTypes.REPLY, "Started")

        while True:
            self.handleMessages()
            if self.moving:
                try:
                    self.servos.move(1, 100)
                    self.servos.move(2, 100)

                    sleep(2)

                    self.servos.move(1, 1000)
                    self.servos.move(2, 1000)
                    sleep(2)

                except self.servos.timeoutError:
                    comm.send_msg(self.conn, comm.MsgTypes.ERROR, "Servo not found.")

    def handleMessages(self):
        if self.conn.poll():
            received = comm.recv_msg(self.conn)
            received_split = received.split(" ")
            if received_split[0] == "controller":
                controller_values = ",".join(received_split[1:]) + ";"
                self.serial.write(bytes(controller_values, "utf-8"))
                comm.send_msg(self.conn, comm.MsgTypes.REPLY, "Received")

            if received == "Stop":
                self.is_stopped = True
                comm.send_msg(self.conn, comm.MsgTypes.REPLY, "Stopped")
            elif received == "Unload":
                self.unload()
                comm.send_msg(self.conn, comm.MsgTypes.REPLY, "Unloaded")
                sys.exit()
            elif received == "turn":
                comm.send_msg(self.conn, comm.MsgTypes.REPLY, "Received")
                self.moving = True;

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
        i = 1

ass1 = None

def name():
    return ass1.name

def load():
    global ass1
    ass1 = Ass1()

def unload():
    i = 0

def start(conn):
    try:
        ass1.run(conn)
    except KeyboardInterrupt:
        ass1.unload()
        sys.exit(1)
