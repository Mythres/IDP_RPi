import importlib
from multiprocessing import Process, Pipe

def start(conn):
    controller = Controller(conn)
    controller.run()

class Controller:
    def __init__(self, conn):
        self.interface_conn = conn
        self.assignment_conn = None
        self.assignment_proc = None
        self.assignment = None
        self.started = False

    def run(self):
        while True:
            received = self.interface_conn.recv().split(" ")
            if received[0] == "exit":
                if self.started:
                    self.stop()
                if self.assignment != None:
                    self.unload()
                self.interface_conn.send("exit")
                return
            
            if received[0] == "load":
                self.load(received[1])
            elif received[0] == "unload":
                self.unload()
            elif received[0] == "start":
                self.start()
            elif received[0] == "stop":
                self.stop()

    def load(self, assignment):
        self.assignment = importlib.import_module("assignments." + assignment + "." + assignment)
        self.assignment.load()
        self.interface_conn.send(assignment + " loaded.")

    def unload(self):
        if self.assignment == None:
            self.interface_conn.send("No assignment has been loaded.")
            return
        else:
            if self.assignment_conn == None:
                self.assignment.unload()
            else:
                self.assignment_conn.send("Unload")
                while self.assignment_conn.recv() != "Unloaded":
                    continue
            
            assignment = self.assignment 
            self.assignment = None
            self.assignment_conn = None
            self.assignment_proc = None
            self.interface_conn.send("Unloaded " + assignment.name() + ".")
            return


    def start(self):
        if self.assignment == None:
            self.interface_conn.send("Please load an assignment first.")
        elif self.assignment_conn != None:
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