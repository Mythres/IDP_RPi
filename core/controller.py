import importlib
import sys
import time
from multiprocessing import Process, Pipe

import utils.communication as comm

def start(monitoring_conn, interface_conn):
    try:
        controller = Controller(monitoring_conn, interface_conn)
        controller.run()
    except KeyboardInterrupt:
        controller.unload(False)
        sys.exit(1)

class Controller:
    def __init__(self, monitoring_conn, interface_conn):
        self.interface_conn = interface_conn
        self.monitoring_conn = monitoring_conn
        self.assignment_conn = None
        self.assignment_proc = None
        self.assignment = None
        self.started = False
        self.monitoring_started = False

    def run(self):
        while True:
            if self.interface_conn.poll():
                received = comm.recv_msg(self.interface_conn).split(" ")
                if received[0] == "exit":
                    self.exit()
                if received[0] == "load":
                    self.load(received[1])
                elif received[0] == "unload":
                    self.unload(True)
                elif received[0] == "start":
                    self.start()
                elif received[0] == "stop":
                    self.stop()
                elif received[0] == "send":
                    self.send(" ".join(received[1:]))
                elif received[0] == "monitoring":
                    self.monitoring(received[1])

            if self.started and self.assignment_conn.poll():
                received = comm.recv_msg(self.assignment_conn)
                comm.send_msg(self.interface_conn, comm.MsgTypes.STATUS, received)

            if self.monitoring_started and self.monitoring_conn.poll():
                received = comm.recv_msg(self.monitoring_conn)
                comm.send_msg(self.interface_conn, comm.MsgTypes.STATUS, received)

    def load(self, assignment):
        if self.assignment is not None:
            comm.send_msg(self.interface_conn, comm.MsgTypes.REPLY, "An assignment has already been loaded.")
            return

        self.assignment = importlib.import_module("assignments." + assignment + "." + assignment)
        self.assignment.load()
        comm.send_msg(self.interface_conn, comm.MsgTypes.REPLY, assignment + " loaded.")

    def unload(self, wait):
        if self.assignment is None:
            comm.send_msg(self.interface_conn, comm.MsgTypes.REPLY, "No assignment has been loaded.")
            return
        else:
            if self.assignment_conn is None:
                self.assignment.unload()
            else:
                comm.send_msg(self.assignment_conn, comm.MsgTypes.COMMAND, "Unload")
                while wait and comm.recv_msg(self.assignment_conn, comm.MsgTypes.REPLY) != "Unloaded":
                    continue
            
            assignment = self.assignment 
            self.assignment = None
            self.assignment_conn = None
            self.assignment_proc = None
            comm.send_msg(self.interface_conn, comm.MsgTypes.REPLY, "Unloaded " + assignment.name() + ".")
            return

    def start(self):
        if self.assignment is None:
            comm.send_msg(self.interface_conn, comm.MsgTypes.REPLY, "Please load an assignment first.")
        elif self.started:
            comm.send_msg(self.interface_conn, comm.MsgTypes.REPLY, "The assignment has already started.")
            return
        elif self.assignment_conn is not None:
            comm.send_msg(self.assignment_conn, comm.MsgTypes.COMMAND, "Start")
            while comm.recv_msg(self.assignment_conn, comm.MsgTypes.REPLY) != "Started":
                continue
            self.started = True
            comm.send_msg(self.interface_conn, comm.MsgTypes.REPLY, self.assignment.name() + " started.")
        else:
            parent_conn, child_conn = Pipe()
            self.assignment_conn = parent_conn
            self.assignment_proc = Process(target=self.assignment.start, args=(child_conn,))
            self.assignment_proc.start()
            while comm.recv_msg(self.assignment_conn, comm.MsgTypes.REPLY) != "Started":
                continue
            self.started = True
            comm.send_msg(self.interface_conn, comm.MsgTypes.REPLY, self.assignment.name() + " started.")

    def stop(self):
        if self.started:
            comm.send_msg(self.assignment_conn, comm.MsgTypes.COMMAND, "Stop")
            self.started = False
            while comm.recv_msg(self.assignment_conn, comm.MsgTypes.REPLY) != "Stopped":
                continue
            comm.send_msg(self.interface_conn, comm.MsgTypes.REPLY, self.assignment.name() + " stopped.")
            return
        else:
            comm.send_msg(self.interface_conn, comm.MsgTypes.REPLY, "No assignment is currently running.")

    def send(self, msg):
        if self.started:
            comm.send_msg(self.assignment_conn, comm.MsgTypes.COMMAND, msg)
            while comm.recv_msg(self.assignment_conn, comm.MsgTypes.REPLY) != "Received":
                continue
            comm.send_msg(self.interface_conn, comm.MsgTypes.REPLY, "Message sent.")
        else:
            comm.send_msg(self.interface_conn, comm.MsgTypes.REPLY, "No assignment is currently running.")

    def exit(self):
        if self.started:
            self.stop()
        if self.monitoring_conn is not None:
            self.monitoring("unload")
        if self.assignment is not None:
            self.unload(True)
        comm.send_msg(self.interface_conn, comm.MsgTypes.REPLY, "exit")
        sys.exit()

    def monitoring(self, msg):
        if self.monitoring_conn is None:
            comm.send_msg(self.interface_conn, comm.MsgTypes.REPLY, "Monitoring has been unloaded, please restart the application.")
        else:
            if msg == "start":
                if not self.monitoring_started:
                    comm.send_msg(self.monitoring_conn, comm.MsgTypes.COMMAND, "Start")
                    comm.send_msg(self.interface_conn, comm.MsgTypes.REPLY, comm.recv_msg(self.monitoring_conn, comm.MsgTypes.REPLY))
                    self.monitoring_started = True
                else:
                    comm.send_msg(self.interface_conn, comm.MsgTypes.REPLY, "Monitoring is already running.")
            elif msg == "stop":
                if self.monitoring_started:
                    comm.send_msg(self.monitoring_conn, comm.MsgTypes.COMMAND, "Stop")
                    comm.send_msg(self.interface_conn, comm.MsgTypes.REPLY, comm.recv_msg(self.monitoring_conn, comm.MsgTypes.REPLY))
                    self.monitoring_started = False
                else:
                    comm.send_msg(self.interface_conn, comm.MsgTypes.REPLY, "Monitoring has already been stopped.")
            elif msg == "unload":
                comm.send_msg(self.monitoring_conn, comm.MsgTypes.COMMAND, "Unload")
                comm.send_msg(self.interface_conn, comm.MsgTypes.REPLY, comm.recv_msg(self.monitoring_conn, comm.MsgTypes.REPLY))
                self.monitoring_started = False

