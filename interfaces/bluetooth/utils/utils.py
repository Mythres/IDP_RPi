import bluetooth

def get_socket(mac_address):
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    sock.connect((mac_address, 1))
    return sock

def send_data(socket, data):
    data_split = data.split("|")
    socket.send(bytes(data_split[0], "utf-8") + b',' + bytes(str(len(data_split[1])), "utf-8") + b"|" + bytes(data_split[1], "utf-8") + b';')
    print("Sent: " + data_split[0] + "," + str(len(data_split[1])) + "|" + data_split[1] + ";")

def check_data(data):
    commands = data.split(";")
    for command in commands:
        if command.find("|") == -1 and len(command) > 0:
            return False
        command_split = command.split("|")
        header_split = command_split[0].split(",")
        if len(command) > 0 and int(header_split[1]) != len(command_split[1]):
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
