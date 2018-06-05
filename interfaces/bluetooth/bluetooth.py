import bluetooth
import interfaces.constants as constants
import interfaces.bluetooth.utils.utils as utils
import monitoring.monitoring as monitoring
import utils.communication as comm
import sys

from time import sleep

class Bluetooth:
    def __init__(self, assignment_mods, conn):
        self.assignment_mods = assignment_mods
        self.conn = conn
        self.socket = None
        self.commands = constants.commands

    def run(self):
        mac_addr = constants.bl_mac_address

        print("Connecting...")
        try:
            self.socket = utils.get_socket(mac_addr)
        except bluetooth.btcommon.BluetoothError:
            print("Unable to connect, exiting.")
            self.send("exit")
            sys.exit()

        print("Connection established.\n")

        #self.bl_send("Hello Everyone!")

        print('Listening..')
        while True:
            try:
                commands = self.bl_recv()
                for command in commands:
                    print(command)
                    command_split = command.split(" ")
                    command_params = command_split[0] + "/" + str(len(command_split))

                    if command_params in self.commands:
                        if len(command_split) > 1 and command_split[0] == "load":
                            if command_split[1] in self.assignment_mods.keys():
                                self.send(command)
                            else:
                                print("Received invalid assignment.\n")
                        if len(command_split) > 1 and command_split[0] == "monitoring":
                            if command_split[1] in monitoring.commands:
                                self.send(command)
                            else:
                                print("Received invalid monitoring command.\n")
                        elif command == "quit" or command == "exit":
                            self.send("exit")
                            sys.exit()
                        elif command == "read":
                            while self.conn.poll():
                                self.bl_send(comm.recv_msg(self.conn, strip_header=False))
                        else:
                            self.send(command)
                    elif len(command_split) > 1 and command_split[0] == "send":
                        self.send(command)
                    else:
                        print("Received invalid command.\n")

                    self.bl_send("2|Received")

            except IOError:
                pass

    def send(self, command):
        comm.send_msg(self.conn, comm.MsgTypes.COMMAND, command)

    def bl_send(self, data):
        utils.send_data(self.socket, data)

    def bl_recv(self):
        return utils.recv_data(self.socket)


def start(assignment_mods, conn):
    bl = Bluetooth(assignment_mods, conn)
    bl.run()
