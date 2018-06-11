import sys
from time import sleep

import drivers.ax12.ax12 as ax12
import utils.communication as comm

commands = ["start", "stop", "unload"]

class Monitoring:
    def __init__(self, conn):
        self.conn = conn
        self.is_stopped = True
        self.servos = ax12.Ax12()

    def run(self):
        while True:
            self.handleMessages()
            sending = ""
            for id in range(1,3):
                try:
                    temp = str(10)  # str(self.servos.readTemperature(id))
                    pos = str(20) # str(self.servos.readPosition(id))
                    #print("Position: " + pos + ", Temperature: " + temp)
                    sending += str(id) + ":" + temp + ","
                    sending += str(id) + ":" + pos
                    sending += "-"
                except self.servos.timeoutError:
                    comm.send_msg(self.conn, comm.MsgTypes.ERROR, "Servo not found.")

            comm.send_msg(self.conn, comm.MsgTypes.STATUS, sending[:-1])

            sleep(0.7)

    def handleMessages(self):
        if self.conn.poll():
            received = comm.recv_msg(self.conn)
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
        i = 1

monitoring = None

def start(conn):
    try:
        monitoring = Monitoring(conn)
        monitoring.run()
    except KeyboardInterrupt:
        monitoring.unload()
        sys.exit(1)
