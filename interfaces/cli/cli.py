import interfaces.cli.utils.utils as utils
import interfaces.constants as constants
import monitoring.monitoring as monitoring
import utils.communication as comm
import sys


class Cli:
    def __init__(self, assignment_mods, conn):
        self.assignment_mods = assignment_mods
        self.conn = conn
        self.commands = constants.commands
    
    def run(self):
        print("Welcome!")
        utils.print_dict_keys(self.assignment_mods, "Available assignments:")
        print()
        while True:
            command = input("=> ")
            command_split = command.split(" ")
            command_params = command_split[0] + "/" + str(len(command_split))

            if command_params in self.commands:
                if len(command_split) > 1 and command_split[0] == "load":
                    if command_split[1] in self.assignment_mods.keys():
                        self.send(command)
                    else:
                        print("Received invalid assignment.\n")
                elif len(command_split) > 1 and command_split[0] == "monitoring":
                    if command_split[1] in monitoring.commands:
                        self.send(command)
                    else:
                        print("Received invalid monitoring command.\n")

                elif command == "quit" or command == "exit":
                    self.send("exit")
                    sys.exit()
                elif command == "read":
                    while self.conn.poll():
                        print(comm.recv_msg(self.conn, strip_header=False))
                elif command == "help":
                    utils.print_dict_keys(self.assignment_mods, "Available assignments:")
                    print()
                    utils.print_list(self.commands, "Available commands:")
                else:
                    self.send(command)
            elif len(command_split) > 1 and command_split[0] == "send":
                self.send(command)
            else:
                print("Received invalid command.\n")

    def send(self, command):
        comm.send_msg(self.conn, comm.MsgTypes.COMMAND, command)
        print(comm.recv_msg(self.conn, comm.MsgTypes.REPLY) + "\n")


def start(assignment_mods, conn):
    cli = Cli(assignment_mods, conn)
    cli.run()
