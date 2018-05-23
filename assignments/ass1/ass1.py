import sys
import assignments.ass1.ax12.ax12 as ax12
from time import sleep

class Ass1:
    def __init__(self):
        self.name = "ass1"
        self.conn = None
        self.is_stopped = False
        self.servos = ax12.Ax12()

    def run(self, conn):
        self.conn = conn
        self.conn.send("Started")
        while True:
            self.handleMessages()
            sending = ""
            for id in range(1,3):
              temp = str(self.servos.readTemperature(id))
              pos = str(self.servos.readPosition(id))
              print("Position: " + pos + ", Temperature: " + temp)
              sending += str(id) + ":" + temp + ","
              sending += str(id) + ":" + pos
              sending += "-"
            self.conn.send(sending[:-1])
            sleep(1)

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
            elif received == "turn":
                while True:
                    self.servos.move(1, 100)
                    self.servos.move(2, 100)

                    sleep(2)
                    
                    self.servos.move(1, 1000)
                    self.servos.move(2, 1000)
                    sleep(2)
                

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
