import bluetooth
import interfaces.constants as constants
import interfaces.bluetooth.utils.utils as utils
import sys


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

        self.bl_send("Hello!")

        print('Listening..')
        while True:
            try:
                command = self.bl_recv()
                command_split = command.split(" ")
                command_params = command_split[0] + "/" + str(len(command_split))

                if command_params in self.commands:
                    if len(command_split) > 1:
                        if command_split[1] in self.assignment_mods.keys():
                            self.send(command)
                        else:
                            print("Received invalid assignment.\n")
                    elif command == "quit" or command == "exit":
                        self.send("exit")
                        sys.exit()
                    else:
                        self.send(command)
                else:
                    print("Received invalid command\n")

            except IOError:
                pass

    def send(self, command):
        self.conn.send(command)
        print(self.conn.recv() + "\n")

    def bl_send(self, data):
        utils.send_data(self.socket, data)

    def bl_recv(self):
        return utils.recv_data(self.socket)


def start(assignment_mods, conn):
    bl = Bluetooth(assignment_mods, conn)
    bl.run()
