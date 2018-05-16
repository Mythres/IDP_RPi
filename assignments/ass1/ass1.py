import sys

class Ass1:
    def __init__(self):
        self.name = "ass1"
        self.conn = None
        self.is_stopped = False

    def run(self, conn):
        self.conn = conn
        self.conn.send("Started")
        while True:
            self.handleMessages()
            
    def handleMessages(self):
        if self.conn.poll():
            received = self.conn.recv()
            if received == "Stop":
                self.is_stopped = True
                self.conn.send("Stopped")
            elif received == "Unload":
                self.unload()
                self.conn.send("Unloaded")
                sys.exit()

        while self.is_stopped:
            received = self.conn.recv()
            if received == "Run":
                self.is_stopped = False
                self.conn.send("Started")
            elif received == "Unload":
                self.unload()
                self.conn.send("Unloaded")
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
    ass1.run(conn)