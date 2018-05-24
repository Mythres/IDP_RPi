import importlib
import sys
from multiprocessing import Process, Pipe

def start(conn):
    try:
        controller = Controller(conn)
        controller.run()
    except KeyboardInterrupt:
        controller.unload(False)
        sys.exit(1)

class Controller:
    def __init__(self, conn):
        self.interface_conn = conn
        self.assignment_conn = None
        self.assignment_proc = None
        self.assignment = None
        self.started = False

    def run(self):
        while True:
            if self.interface_conn.poll():
                received = self.interface_conn.recv().split(" ")
                if received[0] == "exit":
                    if self.started:
                        self.stop()
                    if self.assignment is not None:
                        self.unload(True)
                    self.interface_conn.send("exit")
                    return

                if received[0] == "load":
                    self.load(received[1])
                elif received[0] == "unload":
                    self.unload(True)
                elif received[0] == "start":
                    self.start()
                elif received[0] == "stop":
                    self.stop()
                elif received[0] == "send":
                    self.send("".join(received[1:]))

            if self.started and self.assignment_conn.poll():
                received = self.assignment_conn.recv()
                self.interface_conn.send(received)

    def load(self, assignment):
        if self.assignment is not None:
            self.interface_conn.send("An assignment has already been loaded.")
            return

        self.assignment = importlib.import_module("assignments." + assignment + "." + assignment)
        self.assignment.load()
        self.interface_conn.send(assignment + " loaded.")

    def unload(self, wait):
        if self.assignment is None:
            self.interface_conn.send("No assignment has been loaded.")
            return
        else:
            if self.assignment_conn is None:
                self.assignment.unload()
            else:
                self.assignment_conn.send("Unload")
                while self.assignment_conn.recv() != "Unloaded" and wait:
                    continue
            
            assignment = self.assignment 
            self.assignment = None
            self.assignment_conn = None
            self.assignment_proc = None
            self.interface_conn.send("Unloaded " + assignment.name() + ".")
            return

    def start(self):
        if self.assignment is None:
            self.interface_conn.send("Please load an assignment first.")
        elif self.started:
            self.interface_conn.send("The assignment has already started.")
            return
        elif self.assignment_conn is not None:
            self.assignment_conn.send("Run")
            while self.assignment_conn.recv() != "Started":
                continue
            self.started = True
            self.interface_conn.send(self.assignment.name() + " started.")
        else:
            parent_conn, child_conn = Pipe()
            self.assignment_conn = parent_conn
            self.assignment_proc = Process(target=self.assignment.start, args=(child_conn,))
            self.assignment_proc.start()
            while self.assignment_conn.recv() != "Started":
                continue
            self.started = True
            self.interface_conn.send(self.assignment.name() + " started.")

    def stop(self):
        if self.started:
            self.assignment_conn.send("Stop")
            self.started = False
            self.interface_conn.send(self.assignment.name() + " stopped.")
            while self.assignment_conn.recv() != "Stopped":
                continue
            return
        else:
            self.interface_conn.send("No assignment is currently running.")

    def send(self, msg):
        if self.started:
            self.assignment_conn.send(msg)
            while self.assignment_conn.recv() != "Received":
                continue
            self.interface_conn.send("Message sent.")
        else:
            self.interface_conn.send("No assignment is currently running.")
