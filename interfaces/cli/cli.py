import interfaces.constants as constants
import sys
import utils.utils as utils


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
                if len(command_split) > 1:
                    if command_split[1] in self.assignment_mods.keys():
                        self.send(command)
                    else:
                        print("Invalid assignment.\n")
                elif command == "help":
                    utils.print_list(self.commands, "\nAvailable commands:")
                    utils.print_dict_keys(self.assignment_mods, "\nAvailable assignments:")
                    print()
                elif command == "quit" or command == "exit":
                    self.send("exit")
                    sys.exit()
                elif command == "read":
                    while self.conn.poll():
                        print(self.conn.recv())
                else:
                    self.send(command)
            else:
                print("Invalid command\n")

    def send(self, command):
        self.conn.send(command)
        print(self.conn.recv() + "\n")


def start(assignment_mods, conn):
    cli = Cli(assignment_mods, conn)
    cli.run()
