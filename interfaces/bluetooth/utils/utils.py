import bluetooth

def get_socket(mac_address):
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    sock.connect((mac_address, 1))
    return sock

def send_data(socket, data):
    socket.send(bytes(str(len(data)), "utf-8") + b"|" + bytes(data, "utf-8") + b';')
    print("Sent: " + str(len(data)) + "|" + data + ";")

def check_data(data):
    commands = data.split(";")
    for command in commands:
        if command.find("|") == -1 and len(command) > 0:
            return False
        command_split = command.split("|")
        if len(command) > 0 and int(command_split[0]) != len(command_split[1]):
            return False

    return True

def recv_data(socket):
    data = ""
    commands = []

    while "|" not in data:
        data += socket.recv(1024).decode("utf-8", errors="ignore")

    while not check_data(data):
        data += socket.recv(1024).decode("utf-8", errors="ignore")

    for command in data.split(";"):
        if len(command) != 0:
            command_split = command.split("|")
            commands.append(command_split[1])

    return commands
